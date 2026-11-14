"""Validation harness: the baseline every future swarm configuration is compared to.

For each cipher family and ciphertext length, held-out synthetic cases are
generated (answers hidden from the executor), the executor searches a key space
that contains the true key among decoys, and we measure:

  recall  = fraction of cases where some attempt that passes the *final*
            check (Bonferroni over every attempt on the case's target, so
            independent of search order) reproduces the true plaintext
            (>= 90% similarity); recall_in_run uses the in-run triage verdict;
  FPR     = passing attempts whose plaintext is wrong (< 50% agreement),
            divided by all wrong attempts;
  partial = passing attempts with 50-90% agreement (near-solutions, reported
            separately, not counted as false positives).

A separate null check measures the oracle's false-positive rate on fresh null
samples at the configured (unadjusted) alpha.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from pathlib import Path
import numpy as np

from lpswarm.alphabet import Alphabet, get_alphabet
from lpswarm.ciphers import VARIANTS, get_family
from lpswarm.executor import (EnumeratedKeys, Executor, ExplicitKeys, Target, TextKeys,
                              final_check)
from lpswarm.ledger import Ledger
from lpswarm.oracle import FullOracle, OracleConfig, null_fpr_check, wilson
from lpswarm.textgen.synth import SynthCase, case_breaks, encoded_words, heldout_cases

DEFAULT_FAMILIES = ("caesar", "vigenere", "autokey", "running_key", "substitution", "columnar")
DEFAULT_LENGTHS = (20, 40, 60, 100, 200)


@dataclass
class ValidationConfig:
    families: tuple[str, ...] = DEFAULT_FAMILIES
    lengths: tuple[int, ...] = DEFAULT_LENGTHS
    cases_per_cell: int = 5
    decoys: int = 500                # wrong word-derived keys per case (word-keyed families)
    columnar_max_width: int = 6
    running_key_offsets: int = 2000  # offsets searched (true offset is inside)
    difficulty: str = "medium"
    alphabet: str = "latin26"
    language: str = "english"
    seed: int = 0
    null_check_samples: int = 2000
    word_breaks: bool = False        # give targets the plaintext's word breaks (as LP pages show)
    out_dir: str = "reports"
    ledger_path: str | None = None   # default: <out_dir>/validation.sqlite (recreated)

    def __post_init__(self) -> None:
        self.families = tuple(self.families)
        self.lengths = tuple(int(x) for x in self.lengths)
        for f in self.families:
            get_family(f)
        if not self.families or not self.lengths:
            raise ValueError("ValidationConfig: need at least one family and one length")
        if min(self.lengths) < 1 or self.cases_per_cell < 1 or self.decoys < 0:
            raise ValueError("ValidationConfig: lengths and cases_per_cell must be >= 1, decoys >= 0")
        if self.difficulty not in ("easy", "medium", "hard"):
            raise ValueError(f"ValidationConfig: unknown difficulty {self.difficulty!r}")
        if self.columnar_max_width < 2 or self.running_key_offsets < 1:
            raise ValueError("ValidationConfig: columnar_max_width >= 2, running_key_offsets >= 1")
        if self.null_check_samples < 1:
            raise ValueError("ValidationConfig: null_check_samples >= 1")


def _agreement(cand: np.ndarray, truth: np.ndarray) -> float:
    """Similarity of a candidate to the true plaintext in [0, 1].

    Max of positional agreement and difflib's matching-blocks ratio. The ratio
    credits decryptions that are the true text shifted or re-ordered in runs
    (e.g. rotated or partly-correct columnar keys), which are near-solutions,
    not noise."""
    import difflib
    cand, truth = np.asarray(cand), np.asarray(truth)
    if not len(cand):
        return 0.0
    pos = float((cand == truth[: len(cand)]).mean()) if len(cand) <= len(truth) else 0.0
    t = "".join(chr(0x100 + int(x)) for x in truth)
    c = "".join(chr(0x100 + int(x)) for x in cand)
    ratio = difflib.SequenceMatcher(None, c, t, autojunk=False).ratio()
    return max(pos, ratio)


def _key_space(case: SynthCase, alphabet: Alphabet, vc: ValidationConfig,
               rng: np.random.Generator):
    """Key source + param limits for a case. Contains the true key."""
    fam = get_family(case.family)
    n = alphabet.size
    L = case.length
    if case.family == "caesar":
        return EnumeratedKeys(), {}
    if case.family == "columnar":
        return EnumeratedKeys(max_width=vc.columnar_max_width), {}
    if case.family == "running_key":
        span = min(vc.running_key_offsets, len(case.key) - L)
        true_off = case.params["offset"]
        lo = max(0, min(true_off - int(rng.integers(0, span + 1)), len(case.key) - L - span))
        return TextKeys([("synthetic-key-text", case.key)], name="synthetic"), {
            "offset_lo": lo, "offset_hi": lo + span, "variants": ("vigenere",)}
    # word-keyed families: decoys from the training word list + the true key at a random slot
    words = [w for w in encoded_words(alphabet, vc.language) if 3 <= len(w) <= 12]
    idx = rng.choice(len(words), size=min(vc.decoys, len(words)), replace=False)
    keys = []
    true_hash = fam.key_hash(case.key)
    for i in idx:
        k = fam.key_from_word(words[int(i)], n)
        if k is not None and fam.key_hash(k) != true_hash:
            keys.append(k)
    pos = int(rng.integers(0, len(keys) + 1))
    keys.insert(pos, case.key)
    limits = {"variants": VARIANTS} if case.family in ("vigenere", "autokey") else {}
    return ExplicitKeys(keys, derivation="validation-decoys"), limits


def run_validation(vc: ValidationConfig | None = None, oc: OracleConfig | None = None,
                   progress: bool = True) -> dict:
    vc = vc or ValidationConfig()
    oc = oc or OracleConfig()
    out = Path(vc.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ledger_path = Path(vc.ledger_path) if vc.ledger_path else out / "validation.sqlite"
    for suffix in ("", "-wal", "-shm", "-journal"):
        p = Path(str(ledger_path) + suffix)
        if p.exists():
            try:
                p.unlink()
            except PermissionError:
                raise PermissionError(f"cannot replace {p}: is it open in another program "
                                      "(e.g. a DB browser)? Close it and retry.") from None
    alphabet = get_alphabet(vc.alphabet)
    t0 = time.monotonic()
    oracle = FullOracle(alphabet, oc)
    ledger = Ledger(ledger_path)
    ex = Executor(ledger, oracle, stop_file=None, keep_hits=100_000)
    rng = np.random.default_rng([vc.seed, 0xBA5E])
    cases = heldout_cases(vc.families, vc.lengths, vc.cases_per_cell, vc.difficulty, vc.language,
                          alphabet, vc.seed)
    per_case = []
    for ci, case in enumerate(cases):
        keys, limits = _key_space(case, alphabet, vc, rng)
        hyp = ledger.add_hypothesis(case.family, f"validation case {case.case_id}", "baseline",
                                    "validation")
        tgt = Target(alphabet, case.ciphertext, f"val:{case.family}:{case.length}:{case.case_id}",
                     is_synthetic=True,
                     breaks=case_breaks(case, alphabet) if vc.word_breaks else None)
        s = ex.run(tgt, hyp, case.family, keys, limits)
        final_ok = {r["attempt_id"] for r in final_check(ledger, oracle, s.target_id)
                    if r["passed_final"]}
        if s.passes and len(s.hits) >= ex.keep_hits:
            raise RuntimeError("hit list truncated; raise keep_hits")
        correct = partial = wrong = 0
        inrun_correct = 0
        for h in s.hits:
            if h.verdict != "pass":
                continue
            ag = _agreement(h.plaintext_arr, case.plaintext)
            if ag >= 0.9:
                inrun_correct += 1
            if h.attempt_id not in final_ok:
                continue
            if ag >= 0.9:
                correct += 1
            elif ag >= 0.5:
                partial += 1
            else:
                wrong += 1
        wrong_attempts = max(1, s.new_attempts - correct - partial)
        per_case.append({
            "case_id": case.case_id, "family": case.family, "length": case.length,
            "attempts": s.new_attempts, "screened_out": s.screened_out,
            "passes": s.passes, "near_misses": s.near_misses,
            "final_passes": len(final_ok),
            "correct_passes": correct, "partial_passes": partial, "false_passes": wrong,
            "wrong_attempts": wrong_attempts, "recovered": int(correct > 0),
            "recovered_in_run": int(inrun_correct > 0), "unreachable": s.unreachable,
            "elapsed_s": round(s.elapsed_s, 3),
        })
        if progress:
            print(f"[{ci + 1}/{len(cases)}] {case.family:<12} L={case.length:<4} "
                  f"attempts={s.new_attempts:<5} pass={s.passes:<3} recovered={int(correct > 0)} "
                  f"false={wrong}", flush=True)
    ledger.commit()

    # aggregate per family x length
    table = []
    for fam in vc.families:
        for L in vc.lengths:
            rows = [r for r in per_case if r["family"] == fam and r["length"] == L]
            if not rows:
                continue
            nrec = sum(r["recovered"] for r in rows)
            nrec_run = sum(r["recovered_in_run"] for r in rows)
            fp = sum(r["false_passes"] for r in rows)
            wa = sum(r["wrong_attempts"] for r in rows)
            rlo, rhi = wilson(nrec, len(rows))
            table.append({
                "family": fam, "length": L, "cases": len(rows), "recovered": nrec,
                "recall": nrec / len(rows), "recall_ci_lo": rlo, "recall_ci_hi": rhi,
                "recall_in_run": nrec_run / len(rows),
                "attempts": sum(r["attempts"] for r in rows),
                "false_passes": fp, "wrong_attempts": wa, "fpr": fp / wa,
                "cases_with_false_pass": sum(1 for r in rows if r["false_passes"]),
                "partial_passes": sum(r["partial_passes"] for r in rows),
            })

    if progress:
        print("null false-positive check ...", flush=True)
    bmap = None
    if vc.word_breaks:   # null check with a real break pattern of each length
        bmap = {}
        for case in cases:
            bmap.setdefault(case.length, case_breaks(case, alphabet))
    nulls = null_fpr_check(oracle, vc.lengths, samples=vc.null_check_samples, seed=vc.seed + 777,
                           breaks_by_length=bmap)
    elapsed = time.monotonic() - t0
    result = {"validation_config": asdict(vc), "oracle_config": asdict(oc), "table": table,
              "cases": per_case, "null_check": nulls, "elapsed_s": elapsed,
              "ledger_counts": ledger.counts(), "ledger_path": str(ledger_path),
              "alphabet": alphabet.name, "alphabet_size": alphabet.size}
    ledger.close()
    from lpswarm.validation.report import write_reports
    write_reports(result, out)
    return result

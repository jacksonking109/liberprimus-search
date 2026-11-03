"""Model tier test (Phase 3): do model-driven generators beat the baselines?

Arms, each on the same held-out synthetic cases, each with its own ledger:
  - baseline:        Phase 1 brute force (word lists + enumerable key spaces)
  - random_program:  random specs from the cipher-program language (control)
  - <model name>:    an LLM generator from the models config, optionally with a
                     ranker model (weighting role)

Cases are cipher *programs* sampled from a hidden distribution (skip rules,
number-sequence streams, reverse maps, transpositions ...) applied to held-out
text, so no model can have memorised the answers. A case counts as recovered
when an attempt that passes the final check (Bonferroni over every attempt the
arm made on that case) decrypts to >= 90% of the true plaintext.

Comparisons are at the arms' own budgets: the report gives attempts, model calls,
tokens and USD next to recall, so "beats" can be judged per unit of cost.
"""
from __future__ import annotations

import csv
import json
import statistics
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence

import numpy as np

from lpswarm.alphabet import get_alphabet
from lpswarm.ciphers import get_family
from lpswarm.executor import Target
from lpswarm.ledger import Ledger
from lpswarm.oracle import FullOracle, OracleConfig, wilson
from lpswarm.textgen.synth import heldout_cases
from lpswarm.validation.harness import _agreement

BUILTIN_ARMS = ("baseline", "random_program")


def _builtin(arm: str) -> bool:
    """baseline, random_program, or random_program:N (N random proposals per case)."""
    return arm in BUILTIN_ARMS or (arm.startswith("random_program:") and arm.split(":", 1)[1].isdigit())


@dataclass
class TierConfig:
    arms: tuple[str, ...] = BUILTIN_ARMS
    case_families: tuple[str, ...] = ("program",)
    lengths: tuple[int, ...] = (80, 160)
    cases_per_length: int = 5
    difficulty: str = "medium"
    rounds: int = 5
    per_round: int = 8
    max_attempts: int | None = 20_000     # per case per swarm arm
    ranker: str | None = None             # model name with the weighting role
    models_config: str | None = None
    max_usd: float | None = None          # global cap per model arm (on top of per-model caps)
    baseline_words: int = 2000
    alphabet: str = "latin26"
    language: str = "english"
    seed: int = 0
    out_dir: str = "reports/tiertest"
    # Model calls are logged here, never deleted, so max_usd caps hold across tier-test runs.
    spend_ledger: str = "reports/model_spend.sqlite"

    def __post_init__(self) -> None:
        self.arms = tuple(self.arms)
        self.case_families = tuple(self.case_families)
        self.lengths = tuple(int(x) for x in self.lengths)
        if not self.arms:
            raise ValueError("TierConfig: at least one arm")
        for f in self.case_families:
            get_family(f)
        if self.cases_per_length < 1 or not self.lengths:
            raise ValueError("TierConfig: need cases and lengths")
        model_arms = [a for a in self.arms if not _builtin(a)]
        if (model_arms or self.ranker) and not self.models_config:
            raise ValueError(f"arms {model_arms or [self.ranker]} need --models (a models TOML)")


def _decrypt_attempt(led: Ledger, attempt_id: int, ct: np.ndarray, n: int) -> np.ndarray | None:
    d = led.attempt_detail(attempt_id)
    if not d or d["value_json"] is None:
        return None
    fam = get_family(d["cipher_family"])
    key = json.loads(d["value_json"])
    if isinstance(key, list):
        key = tuple(key)
    return fam.decrypt(ct, key, n, **json.loads(d["params_json"]))


def _cost(led: Ledger | None, label: str) -> dict:
    if led is None:
        return {"model_calls": 0, "tokens_in": 0, "tokens_out": 0, "usd": 0.0}
    prefix = label + "#"  # exact prefix match (LIKE would treat '_' and '%' as wildcards)
    row = led.conn.execute("SELECT COUNT(*), COALESCE(SUM(tokens_in),0), COALESCE(SUM(tokens_out),0),"
                           " COALESCE(SUM(usd),0) FROM budget_event WHERE substr(task_id, 1, ?) = ?",
                           (len(prefix), prefix)).fetchone()
    return {"model_calls": int(row[0]), "tokens_in": int(row[1]), "tokens_out": int(row[2]),
            "usd": float(row[3])}


def _fresh_ledger(path: Path) -> Ledger:
    for suffix in ("", "-wal", "-shm", "-journal"):
        p = Path(str(path) + suffix)
        if p.exists():
            p.unlink()
    return Ledger(path)


def run_tiertest(tc: TierConfig, oc: OracleConfig | None = None, progress: bool = True) -> dict:
    from lpswarm.baseline import BaselineConfig, run_baseline
    from lpswarm.router import Router
    from lpswarm.swarm import LLMGenerator, ModelRanker, RandomProgramGenerator, SwarmConfig, run_swarm
    from lpswarm.textgen import corpus

    out = Path(tc.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    alphabet = get_alphabet(tc.alphabet)
    n = alphabet.size
    oracle = FullOracle(alphabet, oc or OracleConfig())
    cases = heldout_cases(tc.case_families, tc.lengths, tc.cases_per_length, tc.difficulty,
                          tc.language, alphabet, tc.seed)
    words = corpus.wordlist(tc.language, min_len=1, limit=tc.baseline_words)
    t0 = time.monotonic()
    run_id = time.strftime("%Y%m%dT%H%M%S")
    rows = []
    needs_models = any(not _builtin(a) for a in tc.arms) or tc.ranker
    spend = Ledger(tc.spend_ledger) if needs_models else None
    for arm in tc.arms:
        led = _fresh_ledger(out / f"{arm.replace(':', '_')}.sqlite")
        router = None
        if not _builtin(arm):
            router = Router.from_toml(tc.models_config, ledger=spend, global_max_usd=tc.max_usd)
            if not _builtin(arm):
                router.spec(arm)  # raises on unknown model names
        ranker = ModelRanker(router, tc.ranker) if tc.ranker and router else None
        for ci, case in enumerate(cases):
            label = f"tier:{run_id}:{arm}:{case.family}:{case.length}:{case.case_id}"
            tgt = Target(alphabet, case.ciphertext, label, is_synthetic=True)
            ts = time.monotonic()
            stopped = None
            if arm == "baseline":
                fams = ("caesar", "vigenere", "autokey", "substitution", "columnar")
                res = run_baseline(tgt, led, oracle, words,
                                   BaselineConfig(families=fams, stop_file=None), progress=False)
                tid, final = res.target_id, res.final
            else:
                rounds, per_round = tc.rounds, tc.per_round
                if arm.startswith("random_program"):
                    gens = [RandomProgramGenerator(seed=tc.seed * 1000 + ci, difficulty="hard")]
                    if ":" in arm:  # attempt-matched control: N proposals in rounds of 100
                        total = int(arm.split(":", 1)[1])
                        per_round = min(100, max(1, total))
                        rounds = max(1, -(-total // per_round))
                else:
                    gens = [LLMGenerator(router, arm)]
                sr = run_swarm(tgt, led, oracle, gens,
                               SwarmConfig(rounds=rounds, per_round=per_round,
                                           max_attempts=tc.max_attempts, stop_file=None),
                               ranker=ranker if not _builtin(arm) else None, progress=False)
                tid, final, stopped = sr.target_id, sr.final, sr.stopped
            correct, partial, wrong, unverified = [], 0, 0, 0
            for f in final:
                if not f["passed_final"]:
                    continue
                pt = _decrypt_attempt(led, f["attempt_id"], case.ciphertext, n)
                if pt is None:
                    unverified += 1
                    continue
                ag = _agreement(pt, case.plaintext)
                if ag >= 0.9:
                    correct.append(f["attempt_id"])
                elif ag >= 0.5:
                    partial += 1
                else:
                    wrong += 1
            first = None
            if correct:
                first = int(led.conn.execute("SELECT COUNT(*) FROM attempt WHERE target_id=? AND id<=?",
                                             (tid, min(correct))).fetchone()[0])
            row = {"arm": arm, "case_id": case.case_id, "family": case.family, "length": case.length,
                   "recovered": int(bool(correct)), "attempts": led.attempt_count(tid),
                   "attempts_to_solve": first, "false_passes": wrong, "partial_passes": partial,
                   "unverified_passes": unverified, "stopped": stopped,
                   "elapsed_s": round(time.monotonic() - ts, 2),
                   **_cost(spend, label)}
            rows.append(row)
            if progress:
                print(f"[{arm}] {ci + 1}/{len(cases)} L={case.length} recovered={row['recovered']} "
                      f"attempts={row['attempts']} calls={row['model_calls']} usd={row['usd']:.4f}"
                      + (f" stopped={stopped}" if stopped else ""), flush=True)
        led.close()
    if spend is not None:
        spend.close()

    summary = []
    for arm in tc.arms:
        for L in (*tc.lengths, None):
            rs = [r for r in rows if r["arm"] == arm and (L is None or r["length"] == L)]
            if not rs:
                continue
            k = sum(r["recovered"] for r in rs)
            lo, hi = wilson(k, len(rs))
            solved = [r["attempts_to_solve"] for r in rs if r["attempts_to_solve"]]
            summary.append({
                "arm": arm, "length": "all" if L is None else L, "cases": len(rs), "recovered": k,
                "recall": k / len(rs), "recall_ci_lo": lo, "recall_ci_hi": hi,
                "median_attempts_to_solve": statistics.median(solved) if solved else None,
                "attempts": sum(r["attempts"] for r in rs),
                "false_passes": sum(r["false_passes"] for r in rs),
                "model_calls": sum(r["model_calls"] for r in rs),
                "tokens_in": sum(r["tokens_in"] for r in rs),
                "tokens_out": sum(r["tokens_out"] for r in rs),
                "usd": round(sum(r["usd"] for r in rs), 4),
            })
    result = {"config": asdict(tc), "oracle_config": asdict(oracle.cfg), "rows": rows,
              "summary": summary, "elapsed_s": time.monotonic() - t0}
    _write(result, out)
    return result


def _write(result: dict, out: Path) -> None:
    for name, data in (("tiertest_cases.csv", result["rows"]), ("tiertest.csv", result["summary"])):
        with (out / name).open("w", encoding="utf-8", newline="") as f:
            if data:
                w = csv.DictWriter(f, fieldnames=list(data[0]))
                w.writeheader()
                w.writerows(data)
    (out / "tiertest.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    tc = result["config"]
    lines = [
        "# Model tier test",
        "",
        f"Held-out synthetic {', '.join(tc['case_families'])} ciphers, difficulty "
        f"`{tc['difficulty']}`, {tc['cases_per_length']} cases per length, seed {tc['seed']}. "
        f"Swarm arms: {tc['rounds']} rounds x {tc['per_round']} proposals, at most "
        f"{tc['max_attempts']} attempts per case. Runtime {result['elapsed_s']:.0f}s.",
        "",
        "Recovered = an attempt surviving the final check (Bonferroni over all of the arm's "
        "attempts on that case) decrypts to >= 90% of the plaintext. Each arm has its own ledger.",
        "",
        f"Model spend is logged in `{tc['spend_ledger']}` (kept across runs, so per-model "
        "`max_usd` caps are cumulative).",
        "",
        "| arm | length | cases | recall | 95% CI | median attempts to solve | attempts | false passes | model calls | tokens in/out | USD |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for s in result["summary"]:
        med = "-" if s["median_attempts_to_solve"] is None else f"{s['median_attempts_to_solve']:.0f}"
        lines.append(f"| {s['arm']} | {s['length']} | {s['cases']} | {s['recall']:.2f} | "
                     f"[{s['recall_ci_lo']:.2f}, {s['recall_ci_hi']:.2f}] | {med} | {s['attempts']} | "
                     f"{s['false_passes']} | {s['model_calls']} | {s['tokens_in']}/{s['tokens_out']} | "
                     f"{s['usd']:.4f} |")
    lines += ["", "Per-case rows: `tiertest_cases.csv`. Ledgers: one `<arm>.sqlite` per arm.", ""]
    (out / "tiertest.md").write_text("\n".join(lines), encoding="utf-8")

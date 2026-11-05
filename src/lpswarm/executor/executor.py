"""Executor: enumerate (params x key candidates) for a hypothesis, decrypt, score,
record everything in the ledger. Already-recorded attempts are skipped, never
retried.

Budgets: max_attempts (new attempts per run), timeout_s (wall clock), and a
kill switch (a STOP file and/or a threading.Event). All checks are plain code
and work the same on Windows and POSIX.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from lpswarm import EXECUTOR_VERSION
from lpswarm.alphabet import Alphabet
from lpswarm.ciphers import get_family
from lpswarm.executor.keysources import KeySource
from lpswarm.ledger import Ledger, dedupe_hash
from lpswarm.oracle import FullOracle, ScoreReport

PREVIEW_CHARS = 80
MAX_KEY_JSON = 4096   # keys longer than this (e.g. running-key texts) keep only hash + preview


@dataclass
class Target:
    alphabet: Alphabet
    ciphertext: np.ndarray
    label: str
    page_range: str | None = None
    is_synthetic: bool = False
    breaks: tuple[int, ...] | None = None   # word-start indices (plaintext positions), optional


@dataclass
class Hit:
    family: str
    params: dict
    key_hash: str
    key_label: str
    verdict: str
    combined: float
    threshold: float
    plaintext: str
    plaintext_arr: np.ndarray
    attempt_id: int = 0


@dataclass
class RunSummary:
    target_id: str
    family: str
    hypothesis_id: int
    new_attempts: int = 0
    skipped: int = 0
    screened_out: int = 0
    passes: int = 0
    near_misses: int = 0
    prior_passes: int = 0            # skipped attempts that had already passed
    lean: int = 0                    # failed attempts counted but not stored (lean sweeps)
    equivalent: int = 0              # skipped: same decryption as an earlier, different key
    unreachable: int = 0             # attempts whose threshold exceeded the best possible score
    stopped: str | None = None       # reason if a budget or kill switch stopped the run
    hits: list[Hit] = field(default_factory=list)
    elapsed_s: float = 0.0


class Executor:
    def __init__(self, ledger: Ledger, oracle: FullOracle, *, max_attempts: int | None = None,
                 timeout_s: float | None = None, stop_file: str | Path | None = "STOP",
                 stop_event: threading.Event | None = None, commit_every: int = 2000,
                 keep_hits: int = 20):
        self.ledger = ledger
        self.oracle = oracle
        self.max_attempts = max_attempts
        self.timeout_s = timeout_s
        self.stop_file = Path(stop_file) if stop_file else None
        self.stop_event = stop_event
        self.commit_every = commit_every
        self.keep_hits = keep_hits

    def _should_stop(self, t0: float, new: int) -> str | None:
        if self.max_attempts is not None and new >= self.max_attempts:
            return "max_attempts"
        if self.timeout_s is not None and time.monotonic() - t0 > self.timeout_s:
            return "timeout"
        if self.stop_event is not None and self.stop_event.is_set():
            return "stop_event"
        if self.stop_file is not None and self.stop_file.exists():
            return "stop_file"
        return None

    def run(self, target: Target, hypothesis_id: int, family_name: str, keys: KeySource,
            param_limits: dict[str, Any] | None = None, lean_id: str | None = None) -> RunSummary:
        """Run every key of `keys` on the target. With `lean_id` (a hash of the proposal) the
        run is a *lean sweep*, for expansions too large to store row by row: attempts that fail
        are only counted (they still count towards the Bonferroni total), passes and near misses
        are stored in full, and a finished sweep of the same proposal is skipped whole."""
        fam = get_family(family_name)
        alpha = target.alphabet
        n = alpha.size
        ct = np.asarray(target.ciphertext, dtype=np.int16).reshape(-1)
        L = len(ct)
        if L < self.oracle.min_length:
            raise ValueError(f"ciphertext has {L} symbols; the oracle needs at least "
                             f"{self.oracle.min_length}")
        if ct.min() < 0 or ct.max() >= n:
            raise ValueError(f"ciphertext values must be in 0..{n - 1} for alphabet {alpha.name}")
        if alpha.size != self.oracle.alphabet.size or alpha.name != self.oracle.alphabet.name:
            raise ValueError("target alphabet differs from the oracle's alphabet")
        lim = param_limits or {}
        breaks = self.oracle.normalise_breaks(L, target.breaks)
        self.oracle.calibrate(L, breaks)  # fail early (e.g. length too long) before touching the ledger
        tid = self.ledger.add_target(alpha, ct, target.label, target.page_range, target.is_synthetic,
                                     breaks=target.breaks)
        self.ledger.set_hypothesis_status(hypothesis_id, "running")
        self.ledger.commit()
        summary = RunSummary(tid, family_name, hypothesis_id)
        if lean_id is not None:
            done = self.ledger.sweep_done(tid, lean_id)
            if done is not None:
                summary.skipped += done
                summary.stopped = None
                self.ledger.set_hypothesis_status(hypothesis_id, "ruled_out")
                self.ledger.commit()
                return summary
        count = self.ledger.attempt_count(tid)
        seen_outputs = self.ledger.output_hashes(tid)
        lean_screened, lean_best = 0, None
        t0 = time.monotonic()
        since_commit = 0
        exhausted = True
        try:
            for kc in keys.candidates(fam, n, L):
                khash = fam.key_hash(kc.key)
                kid = None
                for params in fam.param_grid(L, kc.key, **lim):
                    stop = self._should_stop(t0, summary.new_attempts)
                    if stop:
                        summary.stopped = stop
                        exhausted = False
                        raise _Stop
                    dh = dedupe_hash(tid, family_name, params, khash)
                    prior = self.ledger.prior_verdict(dh)
                    if prior is not None:
                        summary.skipped += 1
                        if prior == "pass":
                            summary.prior_passes += 1
                        continue
                    ts = time.perf_counter()
                    variant = fam.null_variant(kc.key) if hasattr(fam, "null_variant") else None
                    if variant:   # search-optimised decryption: needs the LM, own nulls
                        pt = fam.decrypt(ct, kc.key, n, lm=self.oracle.bigram_table(), **params)
                    else:
                        pt = fam.decrypt(ct, kc.key, n, **params)
                    # A different key (or family) that decrypts to exactly the same text is
                    # the same test: skip it, and do not count it as a new attempt.
                    oh = hashlib.sha256((variant or "").encode() + b"|"
                                        + np.asarray(pt, dtype=np.int16).tobytes()).hexdigest()[:32]
                    prior = self.ledger.prior_output(tid, oh) if oh in seen_outputs else None
                    if prior is not None:
                        summary.skipped += 1
                        summary.equivalent += 1
                        if prior == "pass":
                            summary.prior_passes += 1
                        continue
                    rep = self.oracle.score(pt, attempt_count=count + 1, breaks=breaks,
                                            variant=variant)
                    if lean_id is not None and rep.verdict == "fail":
                        # Counted, not stored: one aggregate row per sweep is written at the end.
                        seen_outputs.add(oh)
                        count += 1
                        summary.new_attempts += 1
                        summary.lean += 1
                        if rep.stage == "screen":
                            summary.screened_out += 1
                            lean_screened += 1
                        elif rep.threshold is not None and rep.combined is not None:
                            m = float(rep.combined - rep.threshold)
                            lean_best = m if lean_best is None else max(lean_best, m)
                        if rep.unreachable:
                            summary.unreachable += 1
                        continue
                    if kid is None:
                        preview = kc.label or fam.key_preview(kc.key)
                        kj = json.dumps(fam.key_json(kc.key), sort_keys=True, separators=(",", ":"))
                        kid = self.ledger.key_candidate_id(khash, kc.derivation, preview,
                                                           kc.corpus_item_id, kc.edition_id,
                                                           kj if len(kj) <= MAX_KEY_JSON else None)
                    ms = (time.perf_counter() - ts) * 1000.0
                    aid = self.ledger.record_attempt(
                        hypothesis_id=hypothesis_id, key_candidate_id=kid, target_id=tid,
                        cipher_family=family_name, params=params, dedupe=dh,
                        executor_version=EXECUTOR_VERSION, runtime_ms=ms,
                        page_range=target.page_range, output_hash=oh)
                    if aid is None:  # recorded concurrently by someone else; treat as skipped
                        summary.skipped += 1
                        continue
                    seen_outputs.add(oh)
                    count += 1
                    preview_pt = alpha.decode(pt[:PREVIEW_CHARS]) if rep.stage == "full" else None
                    self.ledger.record_result(aid, rep, preview_pt)
                    self._tally(summary, rep, fam.name, params, khash, kc.label, alpha, pt, aid)
                    since_commit += 1
                    if since_commit >= self.commit_every:
                        self.ledger.commit()
                        since_commit = 0
        except _Stop:
            pass
        except BaseException:
            # Roll back the uncommitted batch: an interrupt between the attempt and result
            # inserts must not leave an attempt without a result (it would be skipped
            # forever). At most commit_every attempts are lost and get redone next run.
            # Do not leave the hypothesis looking 'running' forever.
            self.ledger.rollback()
            self.ledger.set_hypothesis_status(hypothesis_id, "open")
            self.ledger.commit()
            raise
        if lean_id is not None:
            self.ledger.record_sweep(tid, hypothesis_id, family_name, lean_id, summary.lean,
                                     lean_screened, lean_best, complete=exhausted)
        self.ledger.commit()
        tried = summary.new_attempts + summary.skipped
        if summary.passes or summary.prior_passes or self.ledger.hypothesis_has_pass(hypothesis_id):
            status = "lead"
        elif exhausted and tried > 0:
            status = "ruled_out"
        else:
            status = "open"   # stopped early, or the key source produced nothing to try
        if tried == 0 and exhausted:
            summary.stopped = "empty_search_space"
        self.ledger.set_hypothesis_status(hypothesis_id, status)
        self.ledger.commit()
        summary.elapsed_s = time.monotonic() - t0
        return summary

    def _tally(self, s: RunSummary, rep: ScoreReport, family: str, params: dict, khash: str,
               label: str, alpha: Alphabet, pt: np.ndarray, attempt_id: int = 0) -> None:
        s.new_attempts += 1
        if rep.unreachable:
            s.unreachable += 1
        if rep.stage == "screen":
            s.screened_out += 1
            return
        if rep.verdict == "pass":
            s.passes += 1
        elif rep.verdict == "near_miss":
            s.near_misses += 1
        else:
            return
        s.hits.append(Hit(family, dict(params), khash, label, rep.verdict, float(rep.combined),
                          float(rep.threshold), alpha.decode(pt[:PREVIEW_CHARS]), pt.copy(),
                          attempt_id))
        s.hits.sort(key=lambda h: h.combined - h.threshold, reverse=True)
        del s.hits[self.keep_hits:]


class _Stop(Exception):
    pass


def final_check(ledger: Ledger, oracle: FullOracle, target_id: str) -> list[dict]:
    """Order-independent end-of-search decision for one target.

    Re-scores every in-run pass / near miss against alpha / N_total, where N_total
    is the number of attempts recorded on the target now (Bonferroni over the
    whole search, whatever order it ran in). Thresholds only rise with N, so this
    candidate set contains everything that can pass. Results go to final_check.
    """
    info = ledger.target_info(target_id)
    if info is None:
        raise ValueError(f"unknown target {target_id}")
    total = ledger.attempt_count(target_id)
    breaks = json.loads(info["word_breaks"]) if info.get("word_breaks") else None
    rows = []
    thresholds: dict = {}
    for c in ledger.candidates_for_final(target_id):
        variant = c.get("null_variant")
        if variant not in thresholds:   # each attempt is judged against its own nulls
            thresholds[variant] = oracle.final_threshold(int(info["length"]), total, breaks, variant)
        a, thr = thresholds[variant]
        ok = c["combined"] is not None and c["combined"] >= thr
        ledger.record_final_check(c["attempt_id"], total, a, thr, ok)
        rows.append({**c, "attempt_count_final": total, "alpha_eff_final": a,
                     "threshold_final": thr, "passed_final": ok})
    ledger.commit()
    return rows

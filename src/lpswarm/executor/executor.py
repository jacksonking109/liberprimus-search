"""Executor: enumerate (params x key candidates) for a hypothesis, decrypt, score,
record everything in the ledger. Already-recorded attempts are skipped, never
retried.

Budgets: max_attempts (new attempts per run), timeout_s (wall clock), and a
kill switch (a STOP file and/or a threading.Event). All checks are plain code
and work the same on Windows and POSIX.
"""
from __future__ import annotations

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


@dataclass
class Target:
    alphabet: Alphabet
    ciphertext: np.ndarray
    label: str
    page_range: str | None = None
    is_synthetic: bool = False


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
            param_limits: dict[str, Any] | None = None) -> RunSummary:
        fam = get_family(family_name)
        alpha = target.alphabet
        n = alpha.size
        ct = np.asarray(target.ciphertext, dtype=np.int16)
        L = len(ct)
        lim = param_limits or {}
        tid = self.ledger.add_target(alpha, ct, target.label, target.page_range, target.is_synthetic)
        self.ledger.set_hypothesis_status(hypothesis_id, "running")
        summary = RunSummary(tid, family_name, hypothesis_id)
        count = self.ledger.attempt_count(tid)
        self.oracle.calibrate(L)
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
                    if self.ledger.has_attempt(dh):
                        summary.skipped += 1
                        continue
                    if kid is None:
                        preview = kc.label or fam.key_preview(kc.key)
                        kid = self.ledger.key_candidate_id(khash, kc.derivation, preview,
                                                           kc.corpus_item_id, kc.edition_id)
                    ts = time.perf_counter()
                    pt = fam.decrypt(ct, kc.key, n, **params)
                    rep = self.oracle.score(pt, attempt_count=count + 1)
                    ms = (time.perf_counter() - ts) * 1000.0
                    aid = self.ledger.record_attempt(
                        hypothesis_id=hypothesis_id, key_candidate_id=kid, target_id=tid,
                        cipher_family=family_name, params=params, dedupe=dh,
                        executor_version=EXECUTOR_VERSION, runtime_ms=ms,
                        page_range=target.page_range)
                    if aid is None:  # raced with an identical attempt; treat as skipped
                        summary.skipped += 1
                        continue
                    count += 1
                    preview_pt = alpha.decode(pt[:PREVIEW_CHARS]) if rep.stage == "full" else None
                    self.ledger.record_result(aid, rep, preview_pt)
                    self._tally(summary, rep, fam.name, params, khash, kc.label, alpha, pt)
                    since_commit += 1
                    if since_commit >= self.commit_every:
                        self.ledger.commit()
                        since_commit = 0
        except _Stop:
            pass
        finally:
            self.ledger.commit()
        if summary.passes or self.ledger.hypothesis_has_pass(hypothesis_id):
            status = "lead"
        elif exhausted:
            status = "ruled_out"
        else:
            status = "open"
        self.ledger.set_hypothesis_status(hypothesis_id, status)
        self.ledger.commit()
        summary.elapsed_s = time.monotonic() - t0
        return summary

    def _tally(self, s: RunSummary, rep: ScoreReport, family: str, params: dict, khash: str,
               label: str, alpha: Alphabet, pt: np.ndarray) -> None:
        s.new_attempts += 1
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
                          float(rep.threshold), alpha.decode(pt[:PREVIEW_CHARS]), pt.copy()))
        s.hits.sort(key=lambda h: h.combined - h.threshold, reverse=True)
        del s.hits[self.keep_hits:]


class _Stop(Exception):
    pass

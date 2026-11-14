"""Brute-force baseline: no models, every cipher family, key candidates drawn
from a word list (plus each family's small enumerable space). Everything goes
into the ledger with proposer_model='baseline'.

This is the bar Phase 3 model-driven generators have to beat.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

import numpy as np

from lpswarm.alphabet import Alphabet
from lpswarm.ciphers import VARIANTS
from lpswarm.executor import (ChainKeys, EnumeratedKeys, Executor, KeySource, RunSummary, Target,
                              TextKeys, WordlistKeys, final_check)
from lpswarm.ledger import Ledger
from lpswarm.oracle import FullOracle

ALL_FAMILIES = ("caesar", "vigenere", "autokey", "substitution", "columnar", "running_key")


@dataclass
class BaselineConfig:
    families: tuple[str, ...] = ALL_FAMILIES
    wordlist_name: str = "corpus-top"
    vigenere_enum_len: int = 2            # also enumerate all keys up to this length
    columnar_max_width: int = 7
    running_key_offset_step: int = 1
    running_key_max_offsets: int = 20000  # per key text
    max_attempts_per_family: int | None = None
    timeout_s: float | None = None        # per family
    stop_file: str | None = "STOP"

    def __post_init__(self) -> None:
        from lpswarm.ciphers import get_family
        self.families = tuple(self.families)
        for f in self.families:
            get_family(f)
        if self.vigenere_enum_len < 0 or self.columnar_max_width < 2:
            raise ValueError("BaselineConfig: vigenere_enum_len >= 0 and columnar_max_width >= 2")
        if self.running_key_offset_step < 1 or self.running_key_max_offsets < 1:
            raise ValueError("BaselineConfig: running-key step and max offsets must be >= 1")


@dataclass
class BaselineResult:
    target_id: str
    summaries: list[RunSummary] = field(default_factory=list)
    final: list[dict] = field(default_factory=list)   # end-of-search Bonferroni check


def _family_plan(family: str, words: WordlistKeys, cfg: BaselineConfig,
                 key_texts: Sequence[tuple[str, np.ndarray]],
                 length: int) -> tuple[KeySource, dict, str] | None:
    if family == "caesar":
        return EnumeratedKeys(), {}, "all shifts"
    if family in ("vigenere", "autokey"):
        src = ChainKeys(words, EnumeratedKeys(max_key_len=cfg.vigenere_enum_len)) \
            if cfg.vigenere_enum_len else words
        return src, {"variants": VARIANTS}, (f"{cfg.wordlist_name} words + all keys up to length "
                                             f"{cfg.vigenere_enum_len}; variants {','.join(VARIANTS)}")
    if family == "substitution":
        return words, {}, f"keyword-mixed alphabets from {cfg.wordlist_name}"
    if family == "columnar":
        return (ChainKeys(EnumeratedKeys(max_width=cfg.columnar_max_width), words), {},
                f"all orders up to width {cfg.columnar_max_width} + word-derived orders")
    if family == "running_key":
        if not key_texts:
            return None
        usable = [len(t) - length for _, t in key_texts if len(t) >= length]
        if not usable:
            return None
        hi = min((cfg.running_key_max_offsets - 1) * cfg.running_key_offset_step, max(usable))
        return (TextKeys(list(key_texts), name="user-texts"),
                {"offset_hi": hi, "offset_step": cfg.running_key_offset_step,
                 "variants": VARIANTS},
                f"running key from {len(key_texts)} text(s), offsets 0..{hi} step "
                f"{cfg.running_key_offset_step}")
    raise ValueError(family)


def run_baseline(target: Target, ledger: Ledger, oracle: FullOracle, words: Sequence[str],
                 cfg: BaselineConfig | None = None,
                 key_texts: Sequence[tuple[str, np.ndarray]] = (),
                 progress: bool = True) -> BaselineResult:
    cfg = cfg or BaselineConfig()
    alpha: Alphabet = target.alphabet
    wl = WordlistKeys(words, alpha, name=cfg.wordlist_name, min_len=1)
    ex = Executor(ledger, oracle, max_attempts=cfg.max_attempts_per_family,
                  timeout_s=cfg.timeout_s, stop_file=cfg.stop_file)
    res = BaselineResult(ledger.add_target(alpha, target.ciphertext, target.label,
                                           target.page_range, target.is_synthetic,
                                           breaks=target.breaks))
    L = len(target.ciphertext)
    for fam in cfg.families:
        plan = _family_plan(fam, wl, cfg, key_texts, L)
        if plan is None:
            if progress:
                print(f"{fam:<13} skipped (no key texts at least as long as the ciphertext)")
            continue
        src, limits, desc = plan
        hyp = ledger.find_or_add_hypothesis(fam, f"brute force: {desc}", "baseline", "baseline")
        s = ex.run(target, hyp, fam, src, limits)
        res.summaries.append(s)
        if progress:
            print(f"{fam:<13} new={s.new_attempts:<8} skipped={s.skipped:<8} "
                  f"screened_out={s.screened_out:<8} pass={s.passes:<4} near={s.near_misses:<5} "
                  f"{s.elapsed_s:6.1f}s" + (f"  stopped: {s.stopped}" if s.stopped else ""),
                  flush=True)
            if s.unreachable:
                print(f"{'':<13} warning: {s.unreachable} attempts had a threshold above the best "
                      "possible score (ciphertext too short for this many attempts)")
        # max_attempts and timeout are per family; only the kill switch stops the whole run.
        if s.stopped in ("stop_file", "stop_event"):
            break
    res.final = final_check(ledger, oracle, res.target_id)
    return res


def load_key_texts(paths: Sequence[str | Path], alphabet: Alphabet) -> list[tuple[str, np.ndarray]]:
    out = []
    for p in paths:
        p = Path(p)
        files = sorted(p.glob("*.txt")) if p.is_dir() else [p]
        if not files:
            raise FileNotFoundError(f"no key texts found at {p}")
        from lpswarm.textio import read_text
        for f in files:
            arr = alphabet.encode(read_text(f, errors="replace"))
            if len(arr):
                out.append((f.name, arr))
    return out

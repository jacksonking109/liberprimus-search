"""Deterministic text signals over integer arrays.

All signals are numeric. None of them is a yes/no judgement; decisions are
made only in oracle.py against calibrated null distributions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view


def index_of_coincidence(arr: np.ndarray, n: int) -> float:
    """Normalised IC: n * sum f(f-1) / (L(L-1)). ~1.0 for uniform random text."""
    L = len(arr)
    if L < 2:
        return 0.0
    f = np.bincount(arr.astype(np.int64), minlength=n).astype(np.float64)
    return float(n * (f * (f - 1)).sum() / (L * (L - 1)))


@dataclass
class NgramModel:
    """Character n-gram model with add-k smoothing.

    `logprob` is a flat table of log P(c | previous order-1 symbols), indexed
    by the n-gram's base-n integer value.
    """
    n_symbols: int
    order: int
    logprob: np.ndarray
    name: str = ""

    @classmethod
    def train(cls, arr: np.ndarray, n_symbols: int, order: int, k: float = 0.5,
              name: str = "") -> "NgramModel":
        if order < 1:
            raise ValueError("order must be >= 1")
        size = n_symbols ** order
        if size > 50_000_000:
            raise ValueError("n-gram table too large; lower the order")
        idx = cls._indices(arr, n_symbols, order)
        counts = np.bincount(idx, minlength=size).astype(np.float64).reshape(-1, n_symbols)
        ctx = counts.sum(axis=1, keepdims=True)
        logp = np.log(counts + k) - np.log(ctx + k * n_symbols)
        return cls(n_symbols, order, logp.reshape(-1), name)

    @staticmethod
    def _indices(arr: np.ndarray, n: int, order: int) -> np.ndarray:
        a = np.asarray(arr, dtype=np.int64)
        if len(a) < order:
            return np.zeros(0, dtype=np.int64)
        if order == 1:
            return a
        win = sliding_window_view(a, order)
        weights = n ** np.arange(order - 1, -1, -1, dtype=np.int64)
        return win @ weights

    def score(self, arr: np.ndarray) -> float:
        """Mean log-probability per scored symbol (higher = more language-like)."""
        idx = self._indices(arr, self.n_symbols, self.order)
        if idx.size == 0:
            return float("nan")
        return float(self.logprob[idx].mean())


class Dictionary:
    """Word set for dictionary coverage, stored as alphabet keystrings."""

    def __init__(self, words: Iterable[np.ndarray], min_len: int = 3, max_len: int = 12):
        self.min_len, self.max_len = min_len, max_len
        self.words = {"".join(chr(0x100 + int(x)) for x in w) for w in words
                      if min_len <= len(w) <= max_len}

    def coverage(self, arr: np.ndarray) -> float:
        """Max fraction of symbols covered by non-overlapping dictionary words.

        Works on unspaced text (dynamic programming over segmentations), so it
        does not need word breaks in the ciphertext.
        """
        L = len(arr)
        if L == 0:
            return 0.0
        s = "".join(chr(0x100 + int(x)) for x in arr)
        words = self.words
        lo, hi = self.min_len, self.max_len
        best = [0] * (L + 1)
        for i in range(L):
            b = best[i]
            if best[i + 1] < b:
                best[i + 1] = b
            for l in range(lo, min(hi, L - i) + 1):
                if s[i:i + l] in words:
                    v = b + l
                    if best[i + l] < v:
                        best[i + l] = v
        return best[L] / L


#: Pluggable language-model log-likelihood: decoded text -> log-likelihood per symbol.
#: Must return a number, never a verdict. Phase 1 ships no implementation.
LMScorer = Callable[[str], float]

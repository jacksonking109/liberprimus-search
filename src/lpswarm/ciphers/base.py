"""Cipher family interface.

All families work on integer arrays over an alphabet of size `n` and never
look at symbol spellings, so they are alphabet-agnostic.

A *key* is family-specific (int, tuple of ints, or an array for running keys).
*Params* are the non-key settings a family enumerates (e.g. Vigenere variant,
running-key offset). An attempt is (family, params, key).
"""
from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Iterator, Sequence

import numpy as np

from lpswarm.alphabet import DTYPE

DIFFICULTIES = ("easy", "medium", "hard")


class CipherFamily(ABC):
    name: ClassVar[str]
    #: True if `enumerate_keys` can walk the key space without a key source.
    enumerable: ClassVar[bool] = False
    #: True if the family can turn a dictionary word into a key.
    word_keys: ClassVar[bool] = True

    @abstractmethod
    def encrypt(self, pt: np.ndarray, key: Any, n: int, **params: Any) -> np.ndarray: ...

    @abstractmethod
    def decrypt(self, ct: np.ndarray, key: Any, n: int, **params: Any) -> np.ndarray: ...

    def param_grid(self, length: int, key: Any = None, **limits: Any) -> list[dict]:
        """Non-key parameters to try for a ciphertext of `length` (default: one empty set)."""
        return [{}]

    @abstractmethod
    def random_key(self, rng: np.random.Generator, n: int, difficulty: str = "medium",
                   words: Sequence[np.ndarray] | None = None, length: int | None = None) -> Any: ...

    def random_params(self, rng: np.random.Generator, length: int, key: Any = None) -> dict:
        grid = self.param_grid(length, key)
        return dict(grid[int(rng.integers(len(grid)))])

    def key_from_word(self, word: np.ndarray, n: int) -> Any | None:
        return None

    def enumerate_keys(self, n: int, length: int, **limits: Any) -> Iterator[Any]:
        raise NotImplementedError(f"{self.name} key space is not enumerable")

    def enumeration_size(self, n: int, length: int, **limits: Any) -> int | None:
        return None

    # ----------------------------------------------------------- key encoding
    def key_json(self, key: Any) -> Any:
        """JSON-serialisable canonical form of a key."""
        if isinstance(key, np.ndarray):
            return [int(x) for x in key]
        if isinstance(key, (tuple, list)):
            return [int(x) for x in key]
        return int(key)

    def key_hash(self, key: Any) -> str:
        """Family-scoped: the same integers mean different keys in different families."""
        payload = json.dumps([self.name, self.key_json(key)], separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()

    def key_preview(self, key: Any, max_len: int = 64) -> str:
        s = json.dumps(self.key_json(key), separators=(",", ":"))
        return s if len(s) <= max_len else s[: max_len - 3] + "..."


def as_arr(x: Any) -> np.ndarray:
    return np.asarray(x, dtype=DTYPE)


def random_symbols(rng: np.random.Generator, n: int, length: int) -> tuple[int, ...]:
    return tuple(int(v) for v in rng.integers(0, n, size=length))


def pick_word(rng: np.random.Generator, words: Sequence[np.ndarray], lo: int, hi: int) -> np.ndarray | None:
    cand = [w for w in words if lo <= len(w) <= hi]
    if not cand:
        return None
    return cand[int(rng.integers(len(cand)))]

"""Seeded synthetic plaintext/ciphertext pairs with known answers.

`generate_case` / `generate_cases` produce the *train* split from training
text. The *heldout* split comes from separate text and a separate seed stream
and is only reachable through `heldout_cases`, which refuses callers outside
the validation harness and the test suite.
"""
from __future__ import annotations

import hashlib
import inspect
import json
import zlib
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Sequence

import numpy as np

from lpswarm.alphabet import Alphabet
from lpswarm.ciphers import get_family
from lpswarm.textgen import corpus

RUNNING_KEY_WINDOW = 2000  # running-key offsets are drawn from [0, window]
_HELDOUT_SEED_SALT = 0x5EED_4E1D


@dataclass
class SynthCase:
    case_id: str
    family: str
    language: str
    length: int
    difficulty: str
    split: str
    plaintext: np.ndarray
    ciphertext: np.ndarray
    key: Any
    params: dict
    extra: dict = field(default_factory=dict)


@lru_cache(maxsize=32)
def encoded_text(alphabet: Alphabet, language: str, split: str) -> np.ndarray:
    if split == "train":
        text = corpus.training_text(language)
    elif split == "heldout":
        text = corpus._heldout_text(language)
    else:
        raise ValueError(split)
    return alphabet.encode(text)


@lru_cache(maxsize=32)
def encoded_words(alphabet: Alphabet, language: str, min_len: int = 3,
                  limit: int = 5000) -> tuple[np.ndarray, ...]:
    out = []
    for w in corpus.wordlist(language, min_len=min_len, limit=limit):
        a = alphabet.encode(w)
        if len(a) >= min_len:
            out.append(a)
    return tuple(out)


def _window(rng: np.random.Generator, arr: np.ndarray, length: int) -> np.ndarray:
    if len(arr) < length:
        raise ValueError("corpus too short for requested length")
    start = int(rng.integers(0, len(arr) - length + 1))
    return arr[start:start + length].copy()


def _case_id(**kw: Any) -> str:
    return hashlib.sha256(json.dumps(kw, sort_keys=True, default=str).encode()).hexdigest()[:16]


def _make(family: str, length: int, difficulty: str, language: str, alphabet: Alphabet,
          seed: int, split: str, index: int) -> SynthCase:
    fam = get_family(family)
    salt = _HELDOUT_SEED_SALT if split == "heldout" else 0
    rng = np.random.default_rng([seed, salt, index, length, zlib.crc32(family.encode()),
                                 ("easy", "medium", "hard").index(difficulty)])
    text = encoded_text(alphabet, language, split)
    pt = _window(rng, text, length)
    words = encoded_words(alphabet, language)
    extra: dict = {}
    if family == "running_key":
        key = _window(rng, text, length + RUNNING_KEY_WINDOW)
        params = fam.random_params(rng, length, key)
        extra["key_text_len"] = len(key)
    elif family == "program":
        # Resample until the program decrypts unambiguously (a skip symbol produced by
        # encryption elsewhere would make the answer unrecoverable by design).
        for attempt in range(100):
            key = fam.random_key(rng, alphabet.size, difficulty, words=words, length=length)
            if attempt == 99:
                key["skip"] = []
            from lpswarm.programs.spec import roundtrips
            if roundtrips(pt, key, alphabet.size):
                break
        params = {}
    else:
        key = fam.random_key(rng, alphabet.size, difficulty, words=words, length=length)
        params = fam.random_params(rng, length, key)
    ct = fam.encrypt(pt, key, alphabet.size, **params)
    cid = _case_id(family=family, length=length, difficulty=difficulty, language=language,
                   alphabet=alphabet.name, seed=seed, split=split, index=index)
    return SynthCase(cid, family, language, length, difficulty, split, pt, ct, key, params, extra)


def generate_case(family: str, length: int, difficulty: str = "medium", language: str = "english",
                  alphabet: Alphabet | None = None, seed: int = 0, index: int = 0) -> SynthCase:
    """One reproducible training-split case."""
    return _make(family, length, difficulty, language, alphabet or Alphabet.latin26(), seed,
                 "train", index)


def generate_cases(families: Sequence[str], lengths: Sequence[int], n_per: int,
                   difficulty: str = "medium", language: str = "english",
                   alphabet: Alphabet | None = None, seed: int = 0) -> list[SynthCase]:
    alphabet = alphabet or Alphabet.latin26()
    return [_make(f, L, difficulty, language, alphabet, seed, "train", i)
            for f in families for L in lengths for i in range(n_per)]


_ALLOWED_HELDOUT_CALLERS = ("lpswarm.validation", "test_", "tests.", "conftest")


def _require_validation_caller() -> None:
    """Only the direct caller of heldout_cases is checked. This is a guard
    against accidental use (e.g. a generator tuning itself on held-out data),
    not a security boundary."""
    frame = inspect.currentframe()
    caller = frame.f_back.f_back if frame and frame.f_back else None
    mod = caller.f_globals.get("__name__", "") if caller else ""
    if not mod.startswith(_ALLOWED_HELDOUT_CALLERS):
        raise PermissionError(f"held-out synthetic data is reserved for lpswarm.validation "
                              f"(called from {mod!r})")


def heldout_cases(families: Sequence[str], lengths: Sequence[int], n_per: int,
                  difficulty: str = "medium", language: str = "english",
                  alphabet: Alphabet | None = None, seed: int = 0) -> list[SynthCase]:
    _require_validation_caller()
    alphabet = alphabet or Alphabet.latin26()
    return [_make(f, L, difficulty, language, alphabet, seed, "heldout", i)
            for f in families for L in lengths for i in range(n_per)]

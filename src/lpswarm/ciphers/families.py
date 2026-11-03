"""Concrete cipher families: shift, periodic polyalphabetic, autokey, running key,
simple substitution, columnar transposition."""
from __future__ import annotations

import itertools
from typing import Any, Iterator, Sequence

import numpy as np

from lpswarm.alphabet import DTYPE
from lpswarm.ciphers.base import CipherFamily, as_arr, pick_word, random_symbols

# Polyalphabetic variants, as functions of plaintext p, key k, modulus n.
#   vigenere:          c = p + k
#   beaufort:          c = k - p   (self-inverse)
#   variant_beaufort:  c = p - k
VARIANTS = ("vigenere", "beaufort", "variant_beaufort")


def _enc(p: np.ndarray, k: np.ndarray, n: int, variant: str) -> np.ndarray:
    p32, k32 = p.astype(np.int32), k.astype(np.int32)
    if variant == "vigenere":
        c = p32 + k32
    elif variant == "beaufort":
        c = k32 - p32
    elif variant == "variant_beaufort":
        c = p32 - k32
    else:
        raise ValueError(f"unknown variant {variant}")
    return np.mod(c, n).astype(DTYPE)


def _dec(c: np.ndarray, k: np.ndarray, n: int, variant: str) -> np.ndarray:
    c32, k32 = c.astype(np.int32), k.astype(np.int32)
    if variant == "vigenere":
        p = c32 - k32
    elif variant == "beaufort":
        p = k32 - c32
    elif variant == "variant_beaufort":
        p = c32 + k32
    else:
        raise ValueError(f"unknown variant {variant}")
    return np.mod(p, n).astype(DTYPE)


# ----------------------------------------------------------------- Caesar
class Caesar(CipherFamily):
    name = "caesar"
    enumerable = True
    word_keys = False

    def encrypt(self, pt, key, n, **params):
        return np.mod(pt.astype(np.int32) + int(key), n).astype(DTYPE)

    def decrypt(self, ct, key, n, **params):
        return np.mod(ct.astype(np.int32) - int(key), n).astype(DTYPE)

    def random_key(self, rng, n, difficulty="medium", words=None, length=None):
        return int(rng.integers(1, n))

    def enumerate_keys(self, n, length, **limits):
        return iter(range(n))

    def enumeration_size(self, n, length, **limits):
        return n


# -------------------------------------------------------- periodic Vigenere
_KEYLEN = {"easy": (3, 5), "medium": (6, 9), "hard": (5, 12)}


class Vigenere(CipherFamily):
    """Repeating-key polyalphabetic cipher with Vigenere / Beaufort / variant-Beaufort sign."""
    name = "vigenere"
    enumerable = True

    def _stream(self, key, length):
        k = as_arr(key)
        return np.resize(k, length)

    def encrypt(self, pt, key, n, variant="vigenere", **params):
        return _enc(pt, self._stream(key, len(pt)), n, variant)

    def decrypt(self, ct, key, n, variant="vigenere", **params):
        return _dec(ct, self._stream(key, len(ct)), n, variant)

    def param_grid(self, length, key=None, **limits):
        variants = limits.get("variants") or VARIANTS
        return [{"variant": v} for v in variants]

    def random_key(self, rng, n, difficulty="medium", words=None, length=None):
        lo, hi = _KEYLEN[difficulty]
        if words is not None and difficulty != "hard":
            w = pick_word(rng, words, lo, hi)
            if w is not None:
                return tuple(int(x) for x in w)
        return random_symbols(rng, n, int(rng.integers(lo, hi + 1)))

    def key_from_word(self, word, n):
        return tuple(int(x) for x in word) if len(word) else None

    def enumerate_keys(self, n, length, max_key_len=2, **limits):
        for L in range(1, max_key_len + 1):
            yield from itertools.product(range(n), repeat=L)

    def enumeration_size(self, n, length, max_key_len=2, **limits):
        return sum(n ** L for L in range(1, max_key_len + 1))


# ------------------------------------------------------------------ Autokey
class Autokey(Vigenere):
    """Autokey: keystream = primer followed by the plaintext itself."""
    name = "autokey"

    def encrypt(self, pt, key, n, variant="vigenere", **params):
        primer = as_arr(key)
        stream = np.concatenate([primer, pt])[: len(pt)]
        return _enc(pt, stream, n, variant)

    def decrypt(self, ct, key, n, variant="vigenere", **params):
        primer = as_arr(key)
        m = len(primer)
        out = np.empty(len(ct), dtype=DTYPE)
        prev = primer
        # Process in blocks of the primer length: block j uses plaintext block j-1.
        for start in range(0, len(ct), m):
            blk = ct[start:start + m]
            p = _dec(blk, prev[: len(blk)], n, variant)
            out[start:start + len(blk)] = p
            prev = p
        return out


# -------------------------------------------------------------- Running key
class RunningKey(CipherFamily):
    """Running key: keystream is a long text (array) starting at `offset`.

    The key is the key text as an int array; `offset` is a param. Key texts
    come from a key source (e.g. corpus items), never from enumeration.
    """
    name = "running_key"
    word_keys = False

    def _stream(self, key, length, offset):
        k = as_arr(key)
        if offset + length > len(k):
            raise ValueError("running key text too short for offset+length")
        return k[offset:offset + length]

    def encrypt(self, pt, key, n, variant="vigenere", offset=0, **params):
        return _enc(pt, self._stream(key, len(pt), offset), n, variant)

    def decrypt(self, ct, key, n, variant="vigenere", offset=0, **params):
        return _dec(ct, self._stream(key, len(ct), offset), n, variant)

    def param_grid(self, length, key=None, **limits):
        variants = limits.get("variants") or ("vigenere",)
        if key is None:
            return [{"variant": v, "offset": 0} for v in variants]
        max_off = len(key) - length
        lo = int(limits.get("offset_lo", 0))
        hi = min(max_off, int(limits.get("offset_hi", max_off)))
        step = int(limits.get("offset_step", 1))
        return [{"variant": v, "offset": o} for v in variants for o in range(lo, hi + 1, step)]

    def random_key(self, rng, n, difficulty="medium", words=None, length=None):
        raise NotImplementedError("running-key keys are drawn from key texts; see textgen.synth")

    def random_params(self, rng, length, key=None):
        max_off = len(key) - length
        return {"variant": "vigenere", "offset": int(rng.integers(0, max_off + 1))}


# ------------------------------------------------------------- substitution
class Substitution(CipherFamily):
    """Simple monoalphabetic substitution. Key is a permutation: c = key[p].

    Words give keyword-mixed alphabets (keyword letters first, deduplicated,
    then the remaining symbols in order). Random permutations are only
    reachable through a key source that supplies them.
    """
    name = "substitution"

    def encrypt(self, pt, key, n, **params):
        perm = as_arr(key)
        return perm[pt]

    def decrypt(self, ct, key, n, **params):
        perm = as_arr(key)
        inv = np.empty(n, dtype=DTYPE)
        inv[perm] = np.arange(n, dtype=DTYPE)
        return inv[ct]

    @staticmethod
    def keyword_perm(word: Sequence[int], n: int) -> tuple[int, ...]:
        seen: list[int] = []
        for x in word:
            if int(x) not in seen:
                seen.append(int(x))
        rest = [i for i in range(n) if i not in seen]
        return tuple(seen + rest)

    def random_key(self, rng, n, difficulty="medium", words=None, length=None):
        if difficulty != "hard" and words is not None:
            lo, hi = (4, 7) if difficulty == "easy" else (7, 12)
            w = pick_word(rng, words, lo, hi)
            if w is not None:
                return self.keyword_perm(w, n)
        return tuple(int(x) for x in rng.permutation(n))

    def key_from_word(self, word, n):
        return self.keyword_perm(word, n) if len(word) else None


# --------------------------------------------------------------- columnar
_WIDTH = {"easy": (3, 4), "medium": (5, 6), "hard": (7, 9)}


class Columnar(CipherFamily):
    """Columnar transposition (irregular last row allowed).

    Key is a column order: key[i] is the rank of column i; columns are read
    top to bottom in increasing rank.
    """
    name = "columnar"
    enumerable = True

    @staticmethod
    def _perm(key, length):
        order = np.asarray(key)
        w = len(order)
        read_cols = np.argsort(order, kind="stable")
        idx = [np.arange(c, length, w) for c in read_cols]
        return np.concatenate(idx) if idx else np.arange(0)

    def encrypt(self, pt, key, n, **params):
        return pt[self._perm(key, len(pt))]

    def decrypt(self, ct, key, n, **params):
        perm = self._perm(key, len(ct))
        out = np.empty_like(ct)
        out[perm] = ct
        return out

    def random_key(self, rng, n, difficulty="medium", words=None, length=None):
        lo, hi = _WIDTH[difficulty]
        if length is not None:
            hi = max(2, min(hi, length // 2))
            lo = min(lo, hi)
        w = int(rng.integers(lo, hi + 1))
        return tuple(int(x) for x in rng.permutation(w))

    def key_from_word(self, word, n):
        if len(word) < 2:
            return None
        ranks = np.empty(len(word), dtype=int)
        ranks[np.argsort(np.asarray(word), kind="stable")] = np.arange(len(word))
        return tuple(int(x) for x in ranks)

    def enumerate_keys(self, n, length, max_width=6, min_width=2, **limits):
        for w in range(min_width, min(max_width, length) + 1):
            yield from itertools.permutations(range(w))

    def enumeration_size(self, n, length, max_width=6, min_width=2, **limits):
        import math
        return sum(math.factorial(w) for w in range(min_width, min(max_width, length) + 1))

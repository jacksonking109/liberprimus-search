"""Standard integer sequences available to cipher-program keystreams.

Generic number theory and constants only; nothing here encodes a claim about any
particular puzzle.

Keystreams only need terms mod N, so `window(name, offset, count, n)` computes
exactly that without building huge integers (Fibonacci uses its Pisano period,
primes come from one cached sieve). Each sequence has a maximum index
(MAX_INDEX); asking beyond it raises ValueError, which compile/decrypt report as
an invalid proposal.

The plain functions (primes(count), ...) return the first `count` exact terms and
are kept for tests and inspection.
"""
from __future__ import annotations

import math
import sys
from functools import lru_cache
from typing import Callable

import numpy as np

MAX_INDEX = {
    "primes": 1_100_000, "prime_totients": 1_100_000, "naturals": 10_000_000,
    "fibonacci": 10_000_000, "squares": 10_000_000, "triangular": 10_000_000,
    "pi_digits": 30_000, "e_digits": 30_000,
}

# ------------------------------------------------------------------ primes
_PRIMES = np.zeros(0, dtype=np.int64)


def _primes_count(count: int) -> np.ndarray:
    """First `count` primes, from a sieve that only ever grows."""
    global _PRIMES
    if count > len(_PRIMES):
        c = max(count, 1000)
        limit = int(c * (math.log(c) + math.log(math.log(c)) + 3))
        while True:
            sieve = np.ones(limit + 1, dtype=bool)
            sieve[:2] = False
            for i in range(2, int(limit ** 0.5) + 1):
                if sieve[i]:
                    sieve[i * i::i] = False
            p = np.flatnonzero(sieve).astype(np.int64)
            if len(p) >= count:
                _PRIMES = p
                break
            limit *= 2
    return _PRIMES[:count]


# ---------------------------------------------------------------- pi and e
def _digits_of(value: int, count: int) -> tuple[int, ...]:
    # Python >= 3.11 limits int->str conversion to 4300 digits by default.
    old = sys.get_int_max_str_digits() if hasattr(sys, "get_int_max_str_digits") else None
    try:
        if old is not None:
            sys.set_int_max_str_digits(0)
        s = str(value)[:count]
    finally:
        if old is not None:
            sys.set_int_max_str_digits(old)
    return tuple(int(ch) for ch in s)


@lru_cache(maxsize=2)
def _pi_digits(count: int) -> tuple[int, ...]:
    """Decimal digits of pi (3, 1, 4, 1, 5, ...) via Machin's formula with integers."""
    scale = 10 ** (count + 10)

    def arctan_inv(x: int) -> int:
        total = term = scale // x
        x2, k, sign = x * x, 1, 1
        while term:
            term //= x2
            k += 2
            sign = -sign
            total += sign * (term // k)
        return total
    return _digits_of(4 * (4 * arctan_inv(5) - arctan_inv(239)), count)


@lru_cache(maxsize=2)
def _e_digits(count: int) -> tuple[int, ...]:
    """Decimal digits of e (2, 7, 1, 8, 2, ...)."""
    scale = 10 ** (count + 10)
    total, term, k = 0, scale, 0
    while term:
        total += term
        k += 1
        term //= k
    return _digits_of(total, count)


def _digit_window(fn, offset: int, count: int) -> np.ndarray:
    # Compute in steps of 5000 digits so repeated calls share a cache entry.
    need = offset + count
    size = -(-need // 5000) * 5000
    return np.asarray(fn(size)[offset:need], dtype=np.int64)


# ------------------------------------------------------------------ fibonacci
@lru_cache(maxsize=64)
def _pisano(n: int) -> np.ndarray:
    """One period of Fibonacci (1, 1, 2, 3, ...) mod n."""
    if n == 1:
        return np.zeros(1, dtype=np.int64)
    out = [1 % n, 1 % n]
    while True:
        out.append((out[-1] + out[-2]) % n)
        if out[-2] == 1 % n and out[-1] == 1 % n and len(out) > 3:
            return np.asarray(out[:-2], dtype=np.int64)
        if len(out) > 6 * n + 10:  # Pisano period <= 6n
            raise RuntimeError("Pisano period not found")


# --------------------------------------------------------------------- window
def window(name: str, offset: int, count: int, n: int) -> np.ndarray:
    """Terms offset .. offset+count-1 of sequence `name`, reduced mod n (int64)."""
    if name not in MAX_INDEX:
        raise ValueError(f"unknown sequence {name!r}")
    offset, count, n = int(offset), int(count), int(n)
    if offset < 0 or count < 0 or n < 1:
        raise ValueError("offset and count must be >= 0, n >= 1")
    if offset + count > MAX_INDEX[name]:
        raise ValueError(f"{name} supports indices below {MAX_INDEX[name]}; "
                         f"offset {offset} + length {count} is too far")
    idx = np.arange(offset, offset + count, dtype=np.int64)
    if name == "naturals":
        return idx % n
    if name == "squares":
        r = idx % n
        return (r * r) % n
    if name == "triangular":
        return (idx * (idx + 1) // 2) % n
    if name == "fibonacci":
        per = _pisano(n)
        return per[idx % len(per)]
    if name in ("primes", "prime_totients"):
        p = _primes_count(offset + count)[offset:]
        return ((p - 1) if name == "prime_totients" else p) % n
    if name == "pi_digits":
        return _digit_window(_pi_digits, offset, count) % n
    return _digit_window(_e_digits, offset, count) % n


# ------------------------------------------------- exact terms (for inspection)
def primes(count: int) -> list[int]:
    """2, 3, 5, 7, 11, ..."""
    return [int(x) for x in _primes_count(int(count))]


def prime_totients(count: int) -> list[int]:
    """phi(p) = p - 1 for the primes: 1, 2, 4, 6, 10, ..."""
    return [p - 1 for p in primes(count)]


def naturals(count: int) -> list[int]:
    """0, 1, 2, 3, ..."""
    return list(range(int(count)))


def fibonacci(count: int) -> list[int]:
    """1, 1, 2, 3, 5, ..."""
    out, a, b = [], 1, 1
    for _ in range(int(count)):
        out.append(a)
        a, b = b, a + b
    return out


def squares(count: int) -> list[int]:
    return [i * i for i in range(int(count))]


def triangular(count: int) -> list[int]:
    return [i * (i + 1) // 2 for i in range(int(count))]


def pi_digits(count: int) -> list[int]:
    return list(_pi_digits(int(count)))


def e_digits(count: int) -> list[int]:
    return list(_e_digits(int(count)))


SEQUENCES: dict[str, Callable[[int], list[int]]] = {
    "primes": primes, "prime_totients": prime_totients, "naturals": naturals,
    "fibonacci": fibonacci, "squares": squares, "triangular": triangular,
    "pi_digits": pi_digits, "e_digits": e_digits,
}

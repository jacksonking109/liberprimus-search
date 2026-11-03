"""Standard integer sequences available to cipher-program keystreams.

Generic number theory and constants only; nothing here encodes a claim about any
particular puzzle. Each function returns the first `count` terms as Python ints.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Callable

_MAX_TERMS = 1_100_000


def _check(count: int) -> int:
    count = int(count)
    if not 0 <= count <= _MAX_TERMS:
        raise ValueError(f"sequence length must be in [0, {_MAX_TERMS}]")
    return count


@lru_cache(maxsize=8)
def _primes_upto_count(count: int) -> tuple[int, ...]:
    if count == 0:
        return ()
    import math
    limit = max(16, int(count * (math.log(count + 2) + math.log(math.log(count + 3)) + 3)))
    while True:
        sieve = bytearray([1]) * (limit + 1)
        sieve[0:2] = b"\x00\x00"
        for i in range(2, int(limit ** 0.5) + 1):
            if sieve[i]:
                sieve[i * i::i] = bytearray(len(range(i * i, limit + 1, i)))
        primes = [i for i in range(limit + 1) if sieve[i]]
        if len(primes) >= count:
            return tuple(primes[:count])
        limit *= 2


def primes(count: int) -> list[int]:
    """2, 3, 5, 7, 11, ..."""
    return list(_primes_upto_count(_check(count)))


def prime_totients(count: int) -> list[int]:
    """phi(p) = p - 1 for the primes: 1, 2, 4, 6, 10, ..."""
    return [p - 1 for p in primes(count)]


def naturals(count: int) -> list[int]:
    """0, 1, 2, 3, ..."""
    return list(range(_check(count)))


def fibonacci(count: int) -> list[int]:
    """1, 1, 2, 3, 5, ..."""
    out, a, b = [], 1, 1
    for _ in range(_check(count)):
        out.append(a)
        a, b = b, a + b
    return out


def squares(count: int) -> list[int]:
    return [i * i for i in range(_check(count))]


def triangular(count: int) -> list[int]:
    return [i * (i + 1) // 2 for i in range(_check(count))]


@lru_cache(maxsize=4)
def _pi_digits(count: int) -> tuple[int, ...]:
    """Decimal digits of pi (3, 1, 4, 1, 5, ...) via Machin's formula with integers."""
    guard = 10
    scale = 10 ** (count + guard)

    def arctan_inv(x: int) -> int:
        total = term = scale // x
        x2, k, sign = x * x, 1, 1
        while term:
            term //= x2
            k += 2
            sign = -sign
            total += sign * (term // k)
        return total
    pi = 4 * (4 * arctan_inv(5) - arctan_inv(239))
    s = str(pi)[:count]
    return tuple(int(ch) for ch in s)


@lru_cache(maxsize=4)
def _e_digits(count: int) -> tuple[int, ...]:
    """Decimal digits of e (2, 7, 1, 8, 2, ...)."""
    guard = 10
    scale = 10 ** (count + guard)
    total, term, k = 0, scale, 0
    while term:
        total += term
        k += 1
        term //= k
    return tuple(int(ch) for ch in str(total)[:count])


def pi_digits(count: int) -> list[int]:
    count = _check(count)
    if count > 20000:
        raise ValueError("pi_digits limited to 20000 terms")
    return list(_pi_digits(count))


def e_digits(count: int) -> list[int]:
    count = _check(count)
    if count > 20000:
        raise ValueError("e_digits limited to 20000 terms")
    return list(_e_digits(count))


SEQUENCES: dict[str, Callable[[int], list[int]]] = {
    "primes": primes,
    "prime_totients": prime_totients,
    "naturals": naturals,
    "fibonacci": fibonacci,
    "squares": squares,
    "triangular": triangular,
    "pi_digits": pi_digits,
    "e_digits": e_digits,
}

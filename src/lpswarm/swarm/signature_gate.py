"""Signature gate: a proposed cipher program must be able to produce what the unsolved text looks like.

A program is a DECRYPTION. Run in the other direction (`programs.spec.encrypt`) on English plaintext it shows what ciphertext the
construction makes. The unsolved LP2 text has a measured signature (docs/avenues_explored.md, `research_signature`): adjacent equal runes
about 0.19 of chance (lag 1), lags 2-8 at chance, flat unigram and first-difference IC. A program whose ciphertext misses that cannot be
the cipher, so it is refused before it costs oracle budget, with the numbers fed back to the proposer.

This is a conservative filter, not a judge: it blocks only a clear miss (wide bands, every expanded member of the proposal failing) and lets
through anything it cannot evaluate (no inverse, too many ciphers, an error). It is specific to the LP2 sections 10-25 and is off by default
(`--signature-gate`); never turn it on for solved pages or synthetic targets, whose ciphers do not share the signature.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

N = 29
MAX_MEMBERS = 64             # proposals expanding to more ciphers than this are not gated
WINDOWS = 4
WINDOW_LEN = 3000


@dataclass(frozen=True)
class Signature:
    """Real signature with deliberately wide bands (the screen's own bands are tighter: lag 1 in 0.15-0.24)."""
    lag1: tuple = (0.08, 0.40)
    flat: tuple = (0.70, 1.30)          # every lag 2-8
    ic_max: float = 1.25                # unigram and first-difference IC x 29 (real text 1.00 and 1.03; language 1.6-2.0)
    real_lag1: float = 0.19


SIGNATURE = Signature()


@lru_cache(maxsize=2)
def _windows(alpha):
    from lpswarm.research_signature import english_windows
    return tuple((pt, br) for pt, br in english_windows(alpha, WINDOWS, WINDOW_LEN))


def member_profile(spec: dict, alpha) -> dict:
    from lpswarm.programs.spec import encrypt
    from lpswarm.research_signature import profile
    units = {str(i): np.asarray(encrypt(pt, spec, N, breaks=list(br) or None), dtype=np.int64) for i, (pt, br) in enumerate(_windows(alpha))}
    return profile(units)


def judge(pr: dict, sig: Signature = SIGNATURE) -> tuple[bool, str]:
    """(passes, why not) for one profile."""
    r = pr["ratio"]
    why = []
    if not sig.lag1[0] <= r[0] <= sig.lag1[1]:
        why.append(f"adjacent equal runes at {r[0]:.2f} of chance (real text {sig.real_lag1:.2f})")
    if not all(sig.flat[0] <= x <= sig.flat[1] for x in r[1:]):
        why.append(f"lags 2-8 between {r[1:].min():.2f} and {r[1:].max():.2f} (real text 0.98-1.08)")
    if pr["uni_ic"] > sig.ic_max:
        why.append(f"letter frequencies not flat (IC x 29 = {pr['uni_ic']:.2f}, real text 1.00)")
    if pr["diff_ic"] > sig.ic_max:
        why.append(f"neighbour differences not flat (IC x 29 = {pr['diff_ic']:.2f}, real text 1.03)")
    return (not why, "; ".join(why))


def gate_spec(spec: dict, alpha, sig: Signature = SIGNATURE, profile_fn=None) -> tuple[bool, str]:
    """(blocked, reason). Blocks only if every expanded member is evaluable and fails."""
    from lpswarm.programs.spec import expand_iter, expansion_size
    try:
        if expansion_size(spec) > MAX_MEMBERS:
            return False, ""
        members = []
        for m in expand_iter(spec, None):
            members.append(m)
            if len(members) > MAX_MEMBERS:
                return False, ""
        best = None
        for m in members:
            pr = (profile_fn or member_profile)(m, alpha)
            ok, why = judge(pr, sig)
            if ok:
                return False, ""
            if best is None or abs(np.log(max(pr["ratio"][0], 1e-3) / sig.real_lag1)) < best[0]:
                best = (abs(np.log(max(pr["ratio"][0], 1e-3) / sig.real_lag1)), why)
        if best is None:
            return False, ""
        n = len(members)
        return True, ("signature gate: this program cannot produce the unsolved text's signature"
                      + (f" (closest of {n} ciphers: {best[1]})" if n > 1 else f" ({best[1]})"))
    except Exception:                                                      # no inverse, bad spec, anything: do not block
        return False, ""

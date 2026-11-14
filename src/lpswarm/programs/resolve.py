"""Resolve skip-symbol ambiguity with dynamic programming.

With a `skip` rule, a ciphertext occurrence of a skip symbol may be a literal
(plaintext = that symbol, key stream does not advance) or an ordinary encrypted
symbol that happens to equal it. `skip_mode = "all"` treats every occurrence as
literal. `skip_mode = "resolve"` chooses per occurrence: a Viterbi search over
the number of literals so far (which fixes the key position) picks the choices
that maximise a bigram language model's log-likelihood.

Choosing the most English-looking path inflates scores for *wrong* keys too,
so the oracle calibrates such attempts against nulls decrypted with the same
search (FullOracle null variant "skipdp:<symbols>"). Supported for constant,
repeat and sequence streams (autokey makes the key depend on the path).
"""
from __future__ import annotations

import numpy as np

from lpswarm.programs import spec as S

NEG = -1e18


def resolve_decrypt(ct: np.ndarray, spec: dict, n: int, bigram: np.ndarray) -> np.ndarray:
    """Decrypt with per-occurrence literal/encrypted choices for skip symbols.

    `bigram` is an (n, n) table of log P(next | previous)."""
    if spec["stream"]["kind"] == "autokey":
        raise S.SpecError("skip_mode 'resolve' does not support autokey streams")
    c = np.asarray(ct, dtype=np.int64).copy()
    if spec.get("transpose"):
        perm = S._transpose_perm(spec["transpose"], len(c))
        tmp = np.empty_like(c)
        tmp[perm] = c
        c = tmp
    if spec.get("reverse_text"):
        c = c[::-1].copy()
    L = len(c)
    if L == 0:
        return c.astype(np.int16)
    skip = np.asarray(spec["skip"], dtype=np.int64)
    is_skip = np.isin(c, skip)
    S_ = int(is_skip.sum()) + 1                     # possible literal counts 0..s
    k = S._stream_values(spec["stream"], L, n).astype(np.int64)   # k[t], t = key position
    m = (n - 1) - c if spec["map"] == "reverse" else c
    how = spec["combine"]
    d = np.arange(S_)
    score = np.full((S_, 2), NEG)
    sym = np.zeros((S_, 2), dtype=np.int64)
    back = np.zeros((L, S_, 2), dtype=np.int8)      # previous position's literal flag
    for i in range(L):
        t = i - d                                   # key position if i is encrypted
        valid = t >= 0
        kt = k[np.clip(t, 0, L - 1)]
        if how == "sub":
            p_enc = (m[i] - kt) % n
        elif how == "add":
            p_enc = (m[i] + kt) % n
        else:
            p_enc = (kt - m[i]) % n
        new = np.full((S_, 2), NEG)
        nsym = np.zeros((S_, 2), dtype=np.int64)
        nsym[:, 0] = p_enc
        nsym[:, 1] = c[i]
        if i == 0:
            new[0, 0] = 0.0
            if is_skip[i] and S_ > 1:
                new[1, 1] = 0.0
        else:
            for lp in (0, 1):
                prev, ps = score[:, lp], sym[:, lp]
                cand = np.where(valid, prev + bigram[ps, p_enc], NEG)
                better = cand > new[:, 0]
                new[better, 0] = cand[better]
                back[i, better, 0] = lp
                if is_skip[i]:
                    cand2 = prev[:-1] + bigram[ps[:-1], c[i]]
                    tgt = new[1:, 1]
                    better2 = cand2 > tgt
                    tgt[better2] = cand2[better2]
                    new[1:, 1] = tgt
                    b2 = back[i, 1:, 1]
                    b2[better2] = lp
                    back[i, 1:, 1] = b2
        score, sym = new, nsym
    dd, ll = (int(x) for x in np.unravel_index(int(np.argmax(score)), score.shape))
    out = np.empty(L, dtype=np.int64)
    for i in range(L - 1, -1, -1):
        if ll == 1:
            out[i] = c[i]
        else:
            kt = k[i - dd]
            out[i] = ((m[i] - kt) if how == "sub" else (m[i] + kt) if how == "add" else (kt - m[i])) % n
        prev_l = int(back[i, dd, ll])
        if ll == 1:
            dd -= 1
        ll = prev_l
    return out.astype(np.int16)

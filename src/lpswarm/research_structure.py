"""Structure diagnostics: ways to look at the ciphertext that do not guess a key.

No oracle, no models, no decryption scoring: counts and fixed statistics on the ciphertext
against a fixed-frequency shuffle null, plus a power table on synthetic ciphertexts (English
plaintext put through known mechanisms) so a negative can be read next to what the same
diagnostic can and cannot see.

    python -m lpswarm.research_structure diffs  --out reports/diag
    python -m lpswarm.research_structure scans  --out reports/diag
    python -m lpswarm.research_structure repeats --out reports/diag
    python -m lpswarm.research_structure power  --out reports/diag
    python -m lpswarm.research_structure all    --out reports/diag

diffs   differences d = c[i]-c[i-1] and sums s = c[i]+c[i-1] (mod 29), the 29x29 transition table,
        whether the sections share one statistical process
scans   mutual information between c[i] and c[i-k] (k = 1..64) and the index of coincidence of
        c[i] + r*c[i-k] (r = 1..28, k = 1..16)
repeats where the adjacent equal runes fall (separator, rune, position in the section)
power   what each of those can see (synthetic data only)

Everything is deterministic (fixed seeds), bounded (a wall-clock cap; partial results are marked)
and EXPLORATORY: the units were chosen after looking at the data, p-values calibrate a maximum over
the inspected units, and nothing here confirms anything.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

from lpswarm.research_diagnostics import FREQ_SECTIONS, _word_ids
from lpswarm.research_packets import ALPHABET, load_sections

N = 29
REPS = 199
POWER_REPS = 99
SEED = 20261105
CAP_SECONDS = 300
UNSOLVED = (10, 12, 13, 14, 16, 17, 18, 20, 22, 24, 25)
REFERENCE = FREQ_SECTIONS              # directly readable sections, for comparison only
MAX_MI_LAG = 64
MAX_TR_LAG = 16
LABEL = "EXPLORATORY: units chosen after inspecting the data; a p-value here is not confirmation"
ALPHA = 0.05

# gather index for the transform scan: C_t(r) = sum_a J[a, (t - r*a) % N]
_A = np.arange(N)[None, None, :]
_GI = (np.arange(N)[None, :, None] - np.arange(1, N)[:, None, None] * _A) % N     # (28, 29, 29)
_NEAR_ZERO = (1, 2, N - 2, N - 1)


def _joint(x: np.ndarray, k: int) -> np.ndarray:
    """counts[a, b] of pairs (x[i-k] = a, x[i] = b)."""
    return np.bincount(x[:-k] * N + x[k:], minlength=N * N).reshape(N, N)


def mutual_information(J: np.ndarray) -> float:
    m = J.sum()
    if m == 0:
        return 0.0
    P = J / m
    pa, pb = P.sum(1, keepdims=True), P.sum(0, keepdims=True)
    nz = P > 0
    return float((P[nz] * np.log(P[nz] / (pa @ pb)[nz])).sum())


def transform_ic(J: np.ndarray) -> np.ndarray:
    """index of coincidence (x 29) of (c[i] + r*c[i-k]) mod 29 for r = 1..28, from the joint table."""
    m = float(J.sum())
    C = J[_A, _GI].sum(axis=2).astype(float)                    # (28, 29)
    return N * (C ** 2).sum(axis=1) / (m * m)


def _z(obs, null):
    """z of the observed value and of every shuffle, with mean and sd taken over the shuffles AND
    the observed sample (an exact Monte Carlo test: all r+1 samples are exchangeable under the
    null, so a p-value computed from these z's is not biased by fitting the mean to the shuffles
    only). `null` has the shuffle index on the last axis. Returns z_obs, z_null, mean, sd."""
    allv = np.concatenate([obs[..., None], null], axis=-1)
    mean = allv.mean(axis=-1)
    sd = np.maximum(allv.std(axis=-1, ddof=1), 1e-12)
    return (obs - mean) / sd, (null - mean[..., None]) / sd[..., None], mean, sd


def _p_max(z_obs_max: float, z_null_max: np.ndarray) -> float:
    return (1 + int((z_null_max >= z_obs_max).sum())) / (len(z_null_max) + 1)


def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return _jsonable(o.tolist())
    return o


def _descriptive(secs: dict, ids) -> list[dict]:
    rows = []
    for i in ids:
        x = secs[i]["ct"]
        n = len(x)
        f = np.bincount(x, minlength=N) / n
        wid = _word_ids(n, secs[i]["breaks"])
        eq = x[1:] == x[:-1]
        same = wid[1:] == wid[:-1]
        rows.append({"section": i, "label": secs[i]["label"], "runes": n,
                     "ic29": float(N * (f * f).sum()), "ic29_if_uniform": 1 + (N - 1) / n,
                     "adjacent_equal": int(eq.sum()), "adjacent_expected": float((n - 1) * (f * f).sum()),
                     "equal_within_word": int((eq & same).sum()),
                     "equal_across_boundary": int((eq & ~same).sum())})
    return rows


# ------------------------------------------------------------------------------- diffs
def _dsh(x: np.ndarray) -> np.ndarray:
    """58 counts: the 29 values of d = c[i]-c[i-1], then the 29 values of s = c[i]+c[i-1]."""
    return np.concatenate([np.bincount((x[1:] - x[:-1]) % N, minlength=N),
                           np.bincount((x[1:] + x[:-1]) % N, minlength=N)])


def _bigram(x: np.ndarray) -> np.ndarray:
    return np.bincount(x[:-1] * N + x[1:], minlength=N * N).reshape(N, N)


def _homog(counts: np.ndarray) -> tuple[float, np.ndarray]:
    """chi-square of homogeneity rows (sections) x 29 against the pooled row; per-row contributions."""
    pooled = counts.sum(0) / counts.sum()
    exp = counts.sum(1, keepdims=True) * pooled[None, :]
    contrib = ((counts - exp) ** 2 / np.maximum(exp, 1e-9)).sum(1)
    return float(contrib.sum()), contrib


def diffs(secs: dict, ids, reps: int = REPS, seed: int = SEED, cap_s: float = CAP_SECONDS,
          reference_ids=()) -> dict:
    t0 = time.monotonic()
    ids = list(ids)
    X = {i: secs[i]["ct"] for i in ids}
    WID = {i: _word_ids(len(X[i]), secs[i]["breaks"]) for i in ids}
    lens = [len(X[i]) for i in ids]

    def stat_set(xs: dict):
        dsh = sum(_dsh(xs[i]) for i in ids)
        trans = sum(_bigram(xs[i]) for i in ids)
        within = across = 0
        for i in ids:
            eq = xs[i][1:] == xs[i][:-1]
            same = WID[i][1:] == WID[i][:-1]
            within += int((eq & same).sum())
            across += int((eq & ~same).sum())
        return dsh, trans, within, across

    obs_dsh, obs_trans, obs_w, obs_a = stat_set(X)
    obs_freq = np.array([np.bincount(X[i], minlength=N) for i in ids])
    obs_dh = np.array([_dsh(X[i])[:N] for i in ids])
    rngs = {i: np.random.default_rng(seed + i) for i in ids}
    rng_cross = np.random.default_rng(seed + 100003)
    pool = np.concatenate([X[i] for i in ids])
    cuts = np.cumsum(lens)[:-1]
    n_dsh, n_trans, n_w, n_a, n_hf, n_hd, n_cf, n_cd = [], [], [], [], [], [], [], []
    complete = True
    for _ in range(reps):
        if time.monotonic() - t0 >= cap_s:
            complete = False
            break
        sh = {i: rngs[i].permutation(X[i]) for i in ids}
        d, t, w, a = stat_set(sh)
        n_dsh.append(d)
        n_trans.append(t)
        n_w.append(w)
        n_a.append(a)
        parts = np.split(rng_cross.permutation(pool), cuts)
        hf, cf = _homog(np.array([np.bincount(p, minlength=N) for p in parts]))
        hd, cd = _homog(np.array([_dsh(p)[:N] for p in parts]))
        n_hf.append(hf)
        n_hd.append(hd)
        n_cf.append(cf)
        n_cd.append(cd)
    r = len(n_dsh)
    out: dict = {"kind": "diffs", "label": LABEL, "sections": ids, "shuffles": r, "complete": complete,
                 "seed": seed, "bigrams": int(obs_trans.sum()),
                 "descriptive": _descriptive(secs, list(ids) + [i for i in reference_ids if i in secs])}
    if r < 20:
        out["error"] = "too few shuffles completed (time cap)"
        out["seconds"] = round(time.monotonic() - t0, 2)
        return out
    A = np.array(n_dsh, dtype=float)                                  # (r, 58)
    z_bins, zn_bins, _m, _s = _z(obs_dsh.astype(float), A.T)
    z_null_bins = zn_bins.T                                           # (r, 58)
    mean_b = A.mean(axis=0)                                           # shuffle mean, for display
    max_obs = float(np.abs(z_bins).max())
    p_bins = _p_max(max_obs, np.abs(z_null_bins).max(axis=1))
    # Given the observed number of repeats (d = 0): the missing repeats must show up somewhere, so
    # each shuffle's non-zero bins are rescaled to the observed non-zero total before comparing.
    total = float(obs_dsh[:N].sum())
    scale = (total - obs_dsh[0]) / np.maximum(total - A[:, 0], 1.0)
    B = A[:, 1:N] * scale[:, None]                                   # (r, 28)
    obs_nz = obs_dsh[1:N].astype(float)
    z_cond, zc_null, b_mean, _bs = _z(obs_nz, B.T)
    z_cond_null = zc_null.T
    chi_obs = float(((obs_nz - b_mean) ** 2 / np.maximum(b_mean, 1e-9)).sum())
    chi_null = ((B - b_mean) ** 2 / np.maximum(b_mean, 1e-9)).sum(axis=1)
    near_idx = [d - 1 for d in _NEAR_ZERO]
    near_obs = float(z_cond[near_idx].sum())
    near_null = z_cond_null[:, near_idx].sum(axis=1)
    max_cond = float(np.abs(z_cond).max())
    out["differences"] = {
        "table": [{"d": d, "observed": int(obs_dsh[d]), "shuffle_mean": float(mean_b[d]),
                   "z": float(z_bins[d]),
                   "z_given_repeats": None if d == 0 else float(z_cond[d - 1])} for d in range(N)],
        "sum_table": [{"s": d, "observed": int(obs_dsh[N + d]), "shuffle_mean": float(mean_b[N + d]),
                       "z": float(z_bins[N + d])} for d in range(N)],
        "max_abs_z_over_58_bins": max_obs, "p_max_abs_z": p_bins,
        "max_abs_z_non_zero_d_given_repeats": max_cond,
        "p_max_abs_z_non_zero_d_given_repeats": _p_max(max_cond, np.abs(z_cond_null).max(axis=1)),
        "chi2_d_excluding_zero": chi_obs, "p_chi2_d_excluding_zero": _p_max(chi_obs, chi_null),
        "near_zero_enrichment_z": near_obs, "p_near_zero_enrichment": _p_max(near_obs, near_null),
        "p_formula": "(1 + shuffles with statistic >= observed) / (shuffles + 1); max |z| is "
                     "calibrated over all 58 bins; the non-zero-d statistics hold the number of "
                     "repeats fixed (shuffled counts rescaled to the observed non-zero total)"}
    wn, an = np.array(n_w, float), np.array(n_a, float)
    out["repeats_by_stratum"] = {
        "within_word": {"observed": obs_w, "shuffle_mean": float(wn.mean()), "z": float((obs_w - wn.mean()) / max(wn.std(ddof=1), 1e-9))},
        "across_boundary": {"observed": obs_a, "shuffle_mean": float(an.mean()), "z": float((obs_a - an.mean()) / max(an.std(ddof=1), 1e-9))}}
    T = np.array(n_trans, dtype=float)
    E = np.maximum(np.concatenate([obs_trans[None].astype(float), T]).mean(axis=0), 0.5)
    chi2 = lambda M: float(((M - E) ** 2 / E).sum())               # noqa: E731
    chi_t_obs, chi_t_null = chi2(obs_trans), np.array([chi2(m) for m in T])
    diag = np.eye(N, dtype=bool)
    tot_b = float(obs_trans.sum())
    tr_scale = (tot_b - np.trace(obs_trans)) / np.maximum(tot_b - np.trace(T, axis1=1, axis2=2), 1.0)
    Toff = T * tr_scale[:, None, None]                              # repeats held at the observed count
    Eoff = np.maximum(np.concatenate([obs_trans[None].astype(float), Toff]).mean(axis=0), 0.5)
    nd = lambda M: float((((M - Eoff) ** 2 / Eoff)[~diag]).sum())  # noqa: E731
    chi_nd_obs, chi_nd_null = nd(obs_trans), np.array([nd(m) for m in Toff])
    low_obs = int((obs_trans <= 1).sum())
    low_null = np.array([(m <= 1).sum() for m in T], float)
    out["transitions"] = {
        "chi2_vs_independence": chi_t_obs, "p_chi2": _p_max(chi_t_obs, chi_t_null),
        "diagonal_share_of_chi2": float((((obs_trans - E) ** 2 / E)[diag]).sum() / max(chi_t_obs, 1e-9)),
        "cells_le_1_off_diagonal": int(((obs_trans <= 1) & ~diag).sum()),
        "low_cells": [[int(a), int(b), int(obs_trans[a, b])] for a, b in zip(*np.where(obs_trans <= 1))][:12],
        "chi2_excluding_diagonal": chi_nd_obs, "p_chi2_excluding_diagonal": _p_max(chi_nd_obs, chi_nd_null),
        "cells_with_count_le_1": low_obs, "cells_le_1_shuffle_mean": float(low_null.mean()),
        "p_cells_le_1": _p_max(low_obs, low_null),
        "diagonal_observed": int(np.trace(obs_trans)), "diagonal_shuffle_mean": float(np.trace(E)),
        "note": "expected counts are the shuffle mean per cell; the null chi-square uses the same "
                "expectation, so it is slightly conservative"}
    if len(ids) >= 2:
        hf_obs, cf_obs = _homog(obs_freq.astype(float))
        hd_obs, cd_obs = _homog(obs_dh.astype(float))
        CF, CD = np.array(n_cf), np.array(n_cd)
        zf = (cf_obs - CF.mean(0)) / np.maximum(CF.std(0, ddof=1), 1e-9)
        zd = (cd_obs - CD.mean(0)) / np.maximum(CD.std(0, ddof=1), 1e-9)
        out["homogeneity"] = {
            "frequencies": {"chi2": hf_obs, "shuffle_mean": float(np.mean(n_hf)),
                            "p": _p_max(hf_obs, np.array(n_hf))},
            "difference_histograms": {"chi2": hd_obs, "shuffle_mean": float(np.mean(n_hd)),
                                      "p": _p_max(hd_obs, np.array(n_hd))},
            "per_section_z": [{"section": i, "frequency_z": float(zf[k]), "difference_z": float(zd[k])}
                              for k, i in enumerate(ids)],
            "null": "symbols permuted across all sections, section lengths fixed"}
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


# ------------------------------------------------------------------------------- scans
def scans(secs: dict, ids, reps: int = REPS, seed: int = SEED, cap_s: float = CAP_SECONDS,
          max_mi_lag: int = MAX_MI_LAG, max_tr_lag: int = MAX_TR_LAG,
          exclude_equal: bool = False) -> dict:
    """exclude_equal drops pairs with c[i] == c[i-k] from every joint table (observed and shuffled),
    so the known shortage of adjacent repeats cannot drive the result: what is left is dependence
    beyond the repeat deficit."""
    t0 = time.monotonic()
    ids = list(ids)
    use = [i for i in ids if len(secs[i]["ct"]) > max_mi_lag + 20]
    skipped = [i for i in ids if i not in use]
    S = len(use)
    pooled = S >= 2

    def compute(xs: dict):
        mi = np.zeros((S + 1, max_mi_lag))
        tr = np.zeros((S + 1, max_tr_lag, N - 1))
        Jsum = [np.zeros((N, N)) for _ in range(max_mi_lag)]
        for si, i in enumerate(use):
            for k in range(1, max_mi_lag + 1):
                J = _joint(xs[i], k)
                if exclude_equal:
                    J[np.arange(N), np.arange(N)] = 0
                Jsum[k - 1] += J
                mi[si, k - 1] = mutual_information(J)
                if k <= max_tr_lag:
                    tr[si, k - 1] = transform_ic(J)
        if pooled:
            for k in range(1, max_mi_lag + 1):
                mi[S, k - 1] = mutual_information(Jsum[k - 1])
                if k <= max_tr_lag:
                    tr[S, k - 1] = transform_ic(Jsum[k - 1])
        return mi, tr

    X = {i: secs[i]["ct"] for i in use}
    obs_mi, obs_tr = compute(X)
    rngs = {i: np.random.default_rng(seed + 7 + i) for i in use}
    null_mi, null_tr = [], []
    complete = True
    for _ in range(reps):
        if time.monotonic() - t0 >= cap_s:
            complete = False
            break
        mi, tr = compute({i: rngs[i].permutation(X[i]) for i in use})
        null_mi.append(mi)
        null_tr.append(tr)
    r = len(null_mi)
    out: dict = {"kind": "scans", "label": LABEL, "sections": use, "skipped_too_short": skipped,
                 "shuffles": r, "complete": complete, "seed": seed,
                 "exclude_equal_pairs": exclude_equal, "mi_lags": max_mi_lag, "transform_lags": max_tr_lag,
                 "transforms_per_lag": N - 1}
    if r < 20 or S == 0:
        out["error"] = "too few shuffles completed (time cap)" if S else "no section long enough"
        out["seconds"] = round(time.monotonic() - t0, 2)
        return out
    NM = np.moveaxis(np.array(null_mi), 0, -1)                   # (S+1, lags, r)
    NT = np.moveaxis(np.array(null_tr), 0, -1)                   # (S+1, lags, 28, r)
    zm, zm_null, _mm, _sm = _z(obs_mi, NM)
    zt, zt_null, _mt, _st = _z(obs_tr, NT)

    def family(z, zn, rows, axes_names):
        """max z over `rows` units; p against the same max in every shuffle."""
        zo = z[rows]
        zno = zn[rows]
        flat_o = zo.max()
        flat_n = zno.reshape(-1, zno.shape[-1]).max(axis=0) if zno.ndim > 1 else zno
        return float(flat_o), _p_max(float(flat_o), flat_n)

    def tops(z, rows, label_of, m, k=8):
        idx = np.argsort(-z[rows].reshape(-1))[:k]
        shape = z[rows].shape
        res = []
        for f in idx:
            pos = np.unravel_index(f, shape)
            res.append({**label_of(rows, pos), "z": float(z[rows][pos]), "observed": float(m[rows][pos])})
        return res

    sec_rows = slice(0, S)
    max_mi, p_mi = family(zm, zm_null, sec_rows, "section x lag")
    max_tr, p_tr = family(zt, zt_null, sec_rows, "section x lag x r")

    def lab_mi(rows, pos):
        return {"section": use[pos[0]], "lag": pos[1] + 1}

    def lab_tr(rows, pos):
        return {"section": use[pos[0]], "lag": pos[1] + 1, "r": pos[2] + 1}

    out["dependence_per_section"] = {
        "units": S * max_mi_lag, "max_z": max_mi, "p_max_over_units": p_mi,
        "top": tops(zm, sec_rows, lab_mi, mi_corr(obs_mi, X, use, max_mi_lag))}
    out["transform_per_section"] = {
        "units": S * max_tr_lag * (N - 1), "max_z": max_tr, "p_max_over_units": p_tr,
        "top": tops(zt, sec_rows, lab_tr, obs_tr)}
    if pooled:
        pm, pp = family(zm, zm_null, S, "lag")
        tm, tp = family(zt, zt_null, S, "lag x r")
        out["dependence_pooled"] = {"units": max_mi_lag, "max_z": pm, "p_max_over_units": pp,
                                    "top": [{"lag": int(k) + 1, "z": float(zm[S, k]),
                                             "mutual_information_nats": float(obs_mi[S, k])}
                                            for k in np.argsort(-zm[S])[:8]]}
        pt = zt[S]
        out["transform_pooled"] = {"units": max_tr_lag * (N - 1), "max_z": tm, "p_max_over_units": tp,
                                   "top": [{"lag": int(f // (N - 1)) + 1, "r": int(f % (N - 1)) + 1,
                                            "z": float(pt.reshape(-1)[f]),
                                            "ic29": float(obs_tr[S].reshape(-1)[f])}
                                           for f in np.argsort(-pt.reshape(-1))[:8]]}
    out["note"] = ("mutual information is the plug-in estimate (nats); z is against the shuffle null; "
                   "transforms use r = b/a, which covers every a*c[i-k] + b*c[i] up to relabelling")
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


def mi_corr(obs_mi: np.ndarray, X: dict, use: list, lags: int) -> np.ndarray:
    """Plug-in MI minus its expected bias (N-1)^2 / (2 m), for reporting effect sizes."""
    out = obs_mi.copy()
    for si, i in enumerate(use):
        for k in range(1, lags + 1):
            out[si, k - 1] -= (N - 1) ** 2 / (2 * max(len(X[i]) - k, 1))
    return out


# ------------------------------------------------------------------------------- power
MECHANISMS = ("plaintext (no cipher)", "iid noise", "neighbour feedback (add)", "chain / plaintext autokey",
              "progressive key (arithmetic)", "prime stream", "Hill 2x2 blocks", "periodic key, length 37")
POWER_LENGTHS = (334, 534, 1022, 1434)


def _mechanism_ct(name: str, pt: np.ndarray, alpha, rng) -> np.ndarray:
    from lpswarm.programs import compile_spec, encrypt
    const0 = {"kind": "constant", "value": 0}
    spec = None
    if name == "plaintext (no cipher)":
        return pt.copy()
    if name == "iid noise":
        return rng.integers(0, N, size=len(pt))
    if name == "neighbour feedback (add)":
        spec = {"stream": const0, "combine": "sub", "mix": {"kind": "neighbor", "op": "add", "lag": 1,
                                                          "dir": "prev", "reset": "none", "at": "before"}}
    elif name == "chain / plaintext autokey":
        spec = {"stream": const0, "combine": "sub", "mix": {"kind": "chain", "op": "sub", "lag": 1,
                                                          "dir": "prev", "reset": "none", "at": "before"}}
    elif name == "progressive key (arithmetic)":
        spec = {"stream": {"kind": "sequence", "name": "naturals", "scale": 5, "offset": 3, "add": 0},
                "combine": "sub"}
    elif name == "prime stream":
        spec = {"stream": {"kind": "sequence", "name": "primes", "scale": 1, "offset": 0, "add": 0},
                "combine": "sub"}
    elif name == "Hill 2x2 blocks":
        spec = {"stream": const0, "combine": "sub", "mix": {"kind": "hill", "size": 2, "matrix": [3, 2, 1, 1],
                                                          "at": "before"}}
    elif name == "periodic key, length 37":
        spec = {"stream": {"kind": "repeat", "key": [int(v) for v in rng.integers(0, N, size=37)]},
                "combine": "sub"}
    else:
        raise ValueError(name)
    return np.asarray(encrypt(pt, compile_spec(spec, alpha), N), dtype=np.int64)


def power(reps: int = POWER_REPS, seed: int = SEED, cap_s: float = CAP_SECONDS,
          lengths=POWER_LENGTHS, mechanisms=MECHANISMS) -> dict:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.textgen.synth import encoded_text
    t0 = time.monotonic()
    alpha = get_alphabet(ALPHABET)
    text = encoded_text(alpha, "english", "train")
    rows = []
    complete = True
    for mi_, name in enumerate(mechanisms):
        for li, L in enumerate(lengths):
            if time.monotonic() - t0 >= cap_s:
                complete = False
                break
            rng = np.random.default_rng(seed + 1000 * mi_ + L)
            start = int(rng.integers(0, len(text) - L))
            ct = _mechanism_ct(name, text[start:start + L].astype(np.int64), alpha, rng)
            secs = {0: {"ct": ct, "breaks": [], "label": f"{name} L={L}", "runes": L}}
            left = max(cap_s - (time.monotonic() - t0), 1)
            d = diffs(secs, [0], reps=reps, seed=seed + mi_, cap_s=left / 2)
            s = scans(secs, [0], reps=reps, seed=seed + mi_, cap_s=left / 3)
            s2 = scans(secs, [0], reps=reps, seed=seed + mi_, cap_s=left / 3, exclude_equal=True)
            if "error" in d or "error" in s or "error" in s2:
                complete = False
                continue
            p = {"differences: any bin": d["differences"]["p_max_abs_z"],
                 "differences: non-zero d": d["differences"]["p_chi2_d_excluding_zero"],
                 "differences: near-zero d": d["differences"]["p_near_zero_enrichment"],
                 "transitions": d["transitions"]["p_chi2"],
                 "dependence (MI)": s["dependence_per_section"]["p_max_over_units"],
                 "transform scan": s["transform_per_section"]["p_max_over_units"],
                 "dependence, repeats excluded": s2["dependence_per_section"]["p_max_over_units"],
                 "transform, repeats excluded": s2["transform_per_section"]["p_max_over_units"]}
            rows.append({"mechanism": name, "length": L, "p": p,
                         "detected_by": [k for k, v in p.items() if v < ALPHA]})
    return {"kind": "power", "label": "SYNTHETIC: English plaintext (training split) through known "
            "mechanisms; says what each diagnostic can see, not what the real sections are",
            "shuffles": reps, "alpha": ALPHA, "complete": complete, "seed": seed, "rows": rows,
            "tests": ["differences: any bin", "differences: non-zero d", "differences: near-zero d",
                      "transitions", "dependence (MI)", "transform scan", "dependence, repeats excluded",
                      "transform, repeats excluded"],
            "seconds": round(time.monotonic() - t0, 2)}


# ---------------------------------------------------------------------------- repeats
REFERENCE_ALL = (3, 5, 7, 9, 27, 4, 8)      # readable / shift pages and the two Vigenere pages
POSITION_PERMUTATIONS = 10000
RARE_GAP = 20


def _gap_kind(gap: str) -> str:
    k = []
    if "\u2022" in gap:
        k.append("word dot")
    if "\n" in gap:
        k.append("newline")
    if " " in gap:
        k.append("space")
    if '"' in gap:
        k.append("quote")
    if any(c not in "\u2022\n \"" for c in gap):
        k.append("other")
    return " + ".join(k) if k else "none (inside a word)"


def repeat_profile(texts: dict, alpha, seed: int = SEED, permutations: int = POSITION_PERMUTATIONS) -> dict:
    """Where the adjacent equal runes (c[i] == c[i-1]) fall in the raw text: by what separates the
    two runes (nothing, a word dot, a line end, a quote ...), by rune, by position in the section.

    `texts` maps a section id to its raw rune text (separators, line ends and quotes included).
    Expected counts use each section's own symbol frequencies (pairs x sum of f^2). The position test
    is ONE summary statistic, the mean relative position of the repeats, against permutations that keep
    each section's repeat count (permutations = 0 skips it)."""
    by_gap: dict = {}
    rune_obs, rune_exp = np.zeros(N), np.zeros(N)
    deciles = np.zeros(10, dtype=int)
    rel_all, rel_rep, per_section = [], [], []
    for i, raw in texts.items():
        syms, gaps, gap = [], [], ""
        for ch in raw:
            a = alpha.encode(ch, glyphs_only=True)
            if len(a) == 1:
                gaps.append(_gap_kind(gap) if syms else "start")
                syms.append(int(a[0]))
                gap = ""
            else:
                gap += ch
        x = np.asarray(syms, dtype=np.int64)
        n = len(x)
        if n < 2:
            continue
        f = np.bincount(x, minlength=N) / n
        p_eq = float((f * f).sum())
        rep = x[1:] == x[:-1]
        for a in range(1, n):
            slot = by_gap.setdefault(gaps[a], [0, 0, 0.0])
            slot[0] += 1
            slot[1] += int(rep[a - 1])
            slot[2] += p_eq
        rune_obs += np.bincount(x[1:][rep], minlength=N)
        rune_exp += (n - 1) * f * f
        rel = np.arange(1, n) / n
        rel_all.append(rel)
        rel_rep.append(rel[rep])
        deciles += np.bincount(np.minimum((rel[rep] * 10).astype(int), 9), minlength=10)
        per_section.append({"section": i, "runes": n, "repeats": int(rep.sum()),
                            "expected": float((n - 1) * p_eq),
                            "mean_relative_position": float(rel[rep].mean()) if rep.any() else None})
    pairs = sum(v[0] for v in by_gap.values())
    reps_n = sum(v[1] for v in by_gap.values())
    exp_n = sum(v[2] for v in by_gap.values())
    rare = [0, 0, 0.0]
    rows = []
    for k, (pr, eq, ex) in sorted(by_gap.items(), key=lambda kv: -kv[1][0]):
        if pr < RARE_GAP:
            rare = [rare[0] + pr, rare[1] + eq, rare[2] + ex]
        else:
            rows.append({"gap": k, "pairs": pr, "equal": eq, "expected": ex, "ratio": eq / ex if ex else None})
    if rare[0]:
        rows.append({"gap": "other (fewer than %d pairs each)" % RARE_GAP, "pairs": rare[0], "equal": rare[1],
                     "expected": rare[2], "ratio": rare[1] / rare[2] if rare[2] else None})
    out = {"kind": "repeats", "label": LABEL, "sections": list(texts), "pairs": pairs, "repeats": reps_n,
           "expected": exp_n, "rate": reps_n / pairs if pairs else None,
           "ratio_to_expected": reps_n / exp_n if exp_n else None,
           "by_gap": rows,
           "by_rune": [{"rune": r, "equal": int(rune_obs[r]), "expected": float(rune_exp[r])} for r in range(N)],
           "deciles": deciles.tolist(), "per_section": per_section}
    if permutations and rel_rep and reps_n:
        rng = np.random.default_rng(seed + 424242)
        counts = [len(r) for r in rel_rep]
        obs = float(np.concatenate(rel_rep).mean())
        null = np.empty(permutations)
        for j in range(permutations):
            null[j] = np.concatenate([rng.choice(rel_all[k], size=c, replace=False)
                                      for k, c in enumerate(counts) if c]).mean()
        out["position"] = {
            "mean_relative_position": obs, "uniform": 0.5,
            "p_two_sided": (1 + int((np.abs(null - 0.5) >= abs(obs - 0.5)).sum())) / (permutations + 1),
            "permutations": permutations,
            "first_half": int((np.concatenate(rel_rep) < 0.5).sum()),
            "second_half": int((np.concatenate(rel_rep) >= 0.5).sum()),
            "note": "one summary statistic, chosen after looking at deciles of the same data: a weak lead "
                    "at most, not a confirmed trend"}
    return out


def repeats(ids, reference_ids=REFERENCE_ALL, manifest: str = None, seed: int = SEED,
            permutations: int = POSITION_PERMUTATIONS) -> dict:
    """repeat_profile on the unsolved sections plus plain totals for the reference sections."""
    import json as _json
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import MANIFEST
    from lpswarm.textio import read_text
    manifest = manifest or MANIFEST
    alpha = get_alphabet(ALPHABET)
    mpath = Path(manifest)
    man = _json.loads(read_text(mpath))
    files = {sec["index"]: (mpath.parent / sec["file"]) for sec in man["sections"]}
    texts = {i: read_text(files[i]) for i in ids}
    main_ = repeat_profile(texts, alpha, seed, permutations)
    ref = {}
    for i in reference_ids:
        if i in files:
            r = repeat_profile({i: read_text(files[i])}, alpha, seed, 0)
            ref[str(i)] = {"runes": r["pairs"] + 1, "repeats": r["repeats"], "rate": r["rate"],
                           "ratio_to_expected": r["ratio_to_expected"]}
    main_["reference_sections"] = ref
    main_["random_rate"] = 1 / N
    return main_


# ------------------------------------------------------------------------------ output
def _fmt(p) -> str:
    return "n/a" if p is None else f"{p:.3f}"


def to_markdown(rep: dict) -> str:
    L = ["# Structure diagnostics", "", f"**{LABEL}.** No models, no oracle, no decryption scoring.", ""]
    d = rep.get("diffs")
    if d:
        L += ["## Differences, bigrams, homogeneity", "",
              f"Sections {d['sections']}; {d['shuffles']} shuffles"
              + ("" if d["complete"] else " (**PARTIAL: time cap**)") + f"; {d.get('bigrams', 0)} bigrams.", ""]
        if "error" in d:
            L += [d["error"], ""]
        else:
            L += ["| section | runes | IC x29 | if uniform | adjacent equal | expected | within word | across boundary |",
                  "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
            for r in d["descriptive"]:
                L.append(f"| {r['section']} | {r['runes']} | {r['ic29']:.2f} | {r['ic29_if_uniform']:.2f} | "
                         f"{r['adjacent_equal']} | {r['adjacent_expected']:.0f} | {r['equal_within_word']} | "
                         f"{r['equal_across_boundary']} |")
            L += ["", "Rows after the unsolved set are readable sections, for comparison only.", ""]
            df = d["differences"]
            L += [f"Differences d = c[i] - c[i-1] (pooled): max |z| over 58 bins {df['max_abs_z_over_58_bins']:.2f}, "
                  f"p {_fmt(df['p_max_abs_z'])}; given the observed number of repeats: max |z| over the 28 non-zero d "
                  f"{df['max_abs_z_non_zero_d_given_repeats']:.2f} (p {_fmt(df['p_max_abs_z_non_zero_d_given_repeats'])}), "
                  f"chi-square of the non-zero d p {_fmt(df['p_chi2_d_excluding_zero'])}, "
                  f"enrichment of d = +-1, +-2 p {_fmt(df['p_near_zero_enrichment'])}.", "",
                  "| d | observed | shuffle mean | z | z given the repeat count |", "| ---: | ---: | ---: | ---: | ---: |"]
            for r in df["table"]:
                zc = "" if r["z_given_repeats"] is None else f"{r['z_given_repeats']:+.1f}"
                L.append(f"| {r['d']} | {r['observed']} | {r['shuffle_mean']:.1f} | {r['z']:+.1f} | {zc} |")
            st = d["repeats_by_stratum"]
            tr = d["transitions"]
            L += ["", f"Repeats (d = 0): within word {st['within_word']['observed']} (shuffle mean "
                  f"{st['within_word']['shuffle_mean']:.0f}, z {st['within_word']['z']:+.1f}); across a word boundary "
                  f"{st['across_boundary']['observed']} (shuffle mean {st['across_boundary']['shuffle_mean']:.0f}, "
                  f"z {st['across_boundary']['z']:+.1f}).", "",
                  f"Transition table 29x29: chi-square vs independence p {_fmt(tr['p_chi2'])}; diagonal share of "
                  f"chi-square {tr['diagonal_share_of_chi2']:.2f}; chi-square without the diagonal p "
                  f"{_fmt(tr['p_chi2_excluding_diagonal'])}; cells with count <= 1: {tr['cells_with_count_le_1']} "
                  f"({tr['cells_le_1_off_diagonal']} off the diagonal; shuffle mean {tr['cells_le_1_shuffle_mean']:.2f}, "
                  f"p {_fmt(tr['p_cells_le_1'])}); diagonal "
                  f"{tr['diagonal_observed']} vs {tr['diagonal_shuffle_mean']:.0f} expected.", ""]
            h = d.get("homogeneity")
            if h:
                L += [f"Homogeneity across sections: frequencies p {_fmt(h['frequencies']['p'])}, difference "
                      f"histograms p {_fmt(h['difference_histograms']['p'])}. Per-section z (frequency / difference): "
                      + ", ".join(f"{r['section']}: {r['frequency_z']:+.1f}/{r['difference_z']:+.1f}"
                                  for r in h["per_section_z"]) + ".", ""]
    for skey, stitle in (("scans", "Dependence and transform scans"),
                         ("scans_no_repeats", "Dependence and transform scans, equal pairs excluded "
                                              "(what is left once the repeat shortage is removed)")):
      s = rep.get(skey)
      if s:
        L += [f"## {stitle}", "",
              f"Sections {s['sections']}; {s['shuffles']} shuffles"
              + ("" if s["complete"] else " (**PARTIAL: time cap**)") + ".", ""]
        if "error" in s:
            L += [s["error"], ""]
        else:
            for key, title in (("dependence_per_section", "Mutual information, per section x lag (1-64)"),
                               ("dependence_pooled", "Mutual information, sections pooled, per lag"),
                               ("transform_per_section", "Transform IC, per section x lag x r"),
                               ("transform_pooled", "Transform IC, sections pooled")):
                if key in s:
                    u = s[key]
                    L += [f"**{title}**: {u['units']} units, max z {u['max_z']:.2f}, "
                          f"p (max over units) {_fmt(u['p_max_over_units'])}. Top units:", "",
                          "```", *[json.dumps(_jsonable(t), sort_keys=True) for t in u["top"][:5]], "```", ""]
            L += [s["note"], ""]
    rp = rep.get("repeats")
    if rp:
        L += ["## Where the adjacent repeats fall", "",
              f"Sections {rp['sections']}: {rp['repeats']} adjacent equal runes in {rp['pairs']} pairs "
              f"({100 * rp['rate']:.2f}%; uniform random text would give {100 * rp['random_rate']:.1f}%; "
              f"{rp['expected']:.0f} expected from each section's own frequencies, ratio "
              f"{rp['ratio_to_expected']:.2f}).", "",
              "| what separates the two runes | pairs | equal | expected | ratio |",
              "| --- | ---: | ---: | ---: | ---: |"]
        for r in rp["by_gap"]:
            L.append(f"| {r['gap']} | {r['pairs']} | {r['equal']} | {r['expected']:.1f} | "
                     f"{'n/a' if r['ratio'] is None else format(r['ratio'], '.2f')} |")
        L += ["", "By rune (equal / expected): " + ", ".join(f"{r['rune']}: {r['equal']}/{r['expected']:.0f}"
                                                        for r in rp["by_rune"]) + ".", "",
              "By decile of the section: " + str(rp["deciles"]) + ".", ""]
        pos = rp.get("position")
        if pos:
            L += [f"Mean relative position of the repeats {pos['mean_relative_position']:.3f} (uniform 0.5), "
                  f"permutation p {_fmt(pos['p_two_sided'])} ({pos['permutations']} permutations); first half "
                  f"{pos['first_half']}, second half {pos['second_half']}. {pos['note']}.", ""]
        ref = rp.get("reference_sections")
        if ref:
            L += ["Absolute rates in other sections of the manifest (their ciphers are as the source notes "
                  "claim; used only to put the rate in context):", "",
                  "| section | runes | repeats | rate |", "| ---: | ---: | ---: | ---: |"]
            for k, v in ref.items():
                L.append(f"| {k} | {v['runes']} | {v['repeats']} | {100 * v['rate']:.2f}% |")
            L.append("")
    pw = rep.get("power")
    if pw:
        L += ["## What each diagnostic can see (synthetic)", "", f"{pw['label']}. {pw['shuffles']} shuffles per case, "
              f"alpha {pw['alpha']}; no multiplicity correction across the eight columns.", "",
              "| mechanism | length | " + " | ".join(pw["tests"]) + " |",
              "| --- | ---: | " + " | ".join("---:" for _ in pw["tests"]) + " |"]
        for r in pw["rows"]:
            L.append(f"| {r['mechanism']} | {r['length']} | "
                     + " | ".join(("**" + _fmt(r['p'][t]) + "**") if r["p"][t] < pw["alpha"] else _fmt(r["p"][t])
                                  for t in pw["tests"]) + " |")
        L += ["", "Bold = detected at this level. A real section that shows nothing is only evidence against "
              "mechanisms the row above detects at its length." + ("" if pw["complete"] else " **PARTIAL.**"), ""]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_structure", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["diffs", "scans", "repeats", "power", "all"])
    ap.add_argument("--sections", help="comma-separated manifest ids (default: unsolved sections of 300+ runes)")
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cap", type=float, default=CAP_SECONDS, help="wall-clock seconds per command")
    ap.add_argument("--out", default="reports/diag")
    args = ap.parse_args(argv)
    ids = [int(v) for v in args.sections.split(",")] if args.sections else list(UNSOLVED)
    rep: dict = {"label": LABEL, "seed": args.seed}
    if args.command in ("diffs", "scans", "all"):
        secs = load_sections(indexes=sorted(set(ids) | set(REFERENCE)))
        if args.command in ("diffs", "all"):
            rep["diffs"] = diffs(secs, ids, args.reps, args.seed, args.cap, reference_ids=REFERENCE)
        if args.command in ("scans", "all"):
            rep["scans"] = scans(secs, ids, args.reps, args.seed, args.cap)
            rep["scans_no_repeats"] = scans(secs, ids, args.reps, args.seed, args.cap, exclude_equal=True)
    if args.command in ("repeats", "all"):
        rep["repeats"] = repeats(ids, seed=args.seed)
    if args.command in ("power", "all"):
        rep["power"] = power(min(args.reps, POWER_REPS), args.seed, args.cap)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "diagnostics_structure.json").write_text(json.dumps(_jsonable(rep), indent=1, sort_keys=True) + "\n",
                                                    encoding="utf-8")
    md = to_markdown(rep)
    (out / "diagnostics_structure.md").write_text(md + "\n", encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())

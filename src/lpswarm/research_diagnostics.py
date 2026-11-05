"""Exploratory numeric diagnostics for the research packets. No oracle, no models, no decryption
scoring: only counts and fixed statistics on ciphertext, with shuffled / relabelled nulls.

    python -m lpswarm.research_diagnostics preflight --sections 13,24,25 --out reports/diag
    python -m lpswarm.research_diagnostics keycancel --out reports/diag

Everything is deterministic (fixed seeds), bounded (199 repetitions, a wall-clock cap) and
labelled exploratory: the p-values calibrate a maximum over the inspected units, were chosen after
looking at the data, and are not confirmation.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

from lpswarm.research_packets import load_sections

N = 29
REPS = 199
LAGS = tuple(range(1, 9))
STRATA = ("within_word", "across_boundary", "all")
PAIRS = ((10, 12), (17, 18), (24, 25))
OFFSETS = (-2, -1, 0, 1, 2)
FREQ_SECTIONS = (3, 7, 9, 27)
CAP_SECONDS = 300


def _word_ids(length: int, breaks: list[int]) -> np.ndarray:
    wid = np.zeros(length, dtype=np.int64)
    for b in sorted({int(b) for b in breaks if 0 < int(b) < length}):
        wid[b:] += 1
    return wid


def lag_counts(x: np.ndarray, wid: np.ndarray) -> dict[tuple[int, str], tuple[int, int]]:
    """(equal count, pair count) for each (lag, stratum)."""
    out = {}
    for d in LAGS:
        if len(x) <= d:
            continue
        eq = x[d:] == x[:-d]
        same = wid[d:] == wid[:-d]
        out[(d, "within_word")] = (int((eq & same).sum()), int(same.sum()))
        out[(d, "across_boundary")] = (int((eq & ~same).sum()), int((~same).sum()))
        out[(d, "all")] = (int(eq.sum()), int(len(eq)))
    return out


def preflight(section_ids: list[int], reps: int = REPS, seed: int = 20261105,
              cap_s: float = CAP_SECONDS) -> dict:
    t0 = time.monotonic()
    secs = load_sections(indexes=section_ids)
    obs: dict[tuple, tuple[int, int]] = {}
    shuf: dict[tuple, list[int]] = {}
    done = 0
    for si in section_ids:
        s = secs[si]
        x = s["ct"]
        wid = _word_ids(len(x), s["breaks"])
        for (d, st), v in lag_counts(x, wid).items():
            obs[(si, d, st)] = v
            shuf[(si, d, st)] = []
        rng = np.random.default_rng(seed + si)
        for _ in range(reps):
            if time.monotonic() - t0 > cap_s:
                break
            for (d, st), (c, _n) in lag_counts(rng.permutation(x), wid).items():
                shuf[(si, d, st)].append(c)
        done = min(len(v) for v in shuf.values()) if shuf else 0
    units = sorted(obs)
    complete = all(len(shuf[u]) == reps for u in units)
    r = min(len(shuf[u]) for u in units)
    arrs = {u: np.asarray(shuf[u][:r], dtype=float) for u in units}
    mean = {u: arrs[u].mean() for u in units}
    sd = {u: max(arrs[u].std(ddof=1), 1e-9) for u in units}
    z_obs = {u: (mean[u] - obs[u][0]) / sd[u] for u in units}          # positive = fewer repeats
    max_obs = max(z_obs.values())
    max_null = np.array([max((mean[u] - arrs[u][j]) / sd[u] for u in units) for j in range(r)])
    p = (1 + int((max_null >= max_obs).sum())) / (r + 1)
    rows = [{"target": u[0], "lag": u[1], "stratum": u[2], "equal": obs[u][0], "pairs": obs[u][1],
             "rate": obs[u][0] / obs[u][1] if obs[u][1] else None,
             "shuffle_mean_rate": mean[u] / obs[u][1] if obs[u][1] else None,
             "standardised_deficit": z_obs[u]} for u in units]
    return {"kind": "preflight", "label": "EXPLORATORY: selected after inspecting the data",
            "sections": {str(i): {"label": secs[i]["label"], "runes": secs[i]["runes"],
                                  "words": len(set(_word_ids(secs[i]["runes"], secs[i]["breaks"])))}
                         for i in section_ids},
            "shuffles_per_target": r, "complete": complete, "seed": seed,
            "units": len(units), "max_standardised_deficit": max_obs,
            "p_max_over_all_units": p,
            "p_formula": "(1 + shuffled maxima >= observed maximum) / (shuffles + 1), the maximum "
                         "taken over every lag x stratum x target unit",
            "rows": rows, "seconds": round(time.monotonic() - t0, 2)}


# ---------------------------------------------------------------- key cancellation
def freq_table(section_ids=FREQ_SECTIONS) -> tuple[np.ndarray, np.ndarray]:
    """f (with +1 pseudocounts) from the public directly readable sections, and H[d] =
    sum_x f(x) f(x - d). Frozen before any comparison."""
    secs = load_sections(indexes=list(section_ids))
    counts = np.ones(N)
    for s in secs.values():
        counts += np.bincount(s["ct"], minlength=N)
    f = counts / counts.sum()
    H = np.array([sum(f[x] * f[(x - d) % N] for x in range(N)) for d in range(N)])
    return f, H


def half_stat(A: np.ndarray, B: np.ndarray, delta: int, H: np.ndarray) -> float:
    """min over the two halves of mean log(29 * H[D]) for D_i = A_i - B_(i+delta)."""
    hi = min(len(A), len(B)) - 3
    idx = np.arange(2, hi + 1)
    D = (A[idx] - B[idx + delta]) % N
    sc = np.log(N * H[D])
    n = len(sc)
    return float(min(sc[: n // 2].mean(), sc[n // 2:].mean()))


def _all_stats(A: np.ndarray, B: np.ndarray, H: np.ndarray) -> list[float]:
    return [half_stat(A, B, d, H) for d in OFFSETS]


def keycancel(pairs=PAIRS, reps: int = REPS, seed: int = 20261105, cap_s: float = CAP_SECONDS) -> dict:
    t0 = time.monotonic()
    f, H = freq_table()
    need = sorted({i for p in pairs for i in p})
    secs = load_sections(indexes=need)
    observed = {}
    for a, b in pairs:
        for d, st in zip(OFFSETS, _all_stats(secs[a]["ct"], secs[b]["ct"], H)):
            observed[(a, b, d)] = st
    keys = sorted(observed)
    max_obs = max(observed.values())
    rng = np.random.default_rng(seed)
    nulls, evals = [], len(keys)
    for _ in range(reps):
        if time.monotonic() - t0 > cap_s:
            break
        best = -1e9
        for a, b in pairs:
            perm = rng.permutation(N)                     # relabel the 29 runes of the second member
            relabelled = perm[secs[b]["ct"]]
            for st in _all_stats(secs[a]["ct"], relabelled, H):
                best = max(best, st)
                evals += 1
        nulls.append(best)
    r = len(nulls)
    p = (1 + sum(1 for m in nulls if m >= max_obs)) / (r + 1)
    # development controls: shared key vs independent key, over development text
    dev = _dev_controls(secs=None, H=H, seed=seed)
    return {"kind": "keycancel",
            "label": "EXPLORATORY screening statistic; not a plaintext score and not a probability "
                     "model of English",
            "pairs": [list(p_) for p_ in pairs], "offsets": list(OFFSETS),
            "frequency_sections": list(FREQ_SECTIONS), "null_repetitions": r, "complete": r == reps,
            "statistic_evaluations": evals, "seed": seed,
            "observed": [{"pair": [a, b], "offset": d, "statistic": observed[(a, b, d)]}
                         for a, b, d in keys],
            "max_observed": max_obs, "p_max_over_15": p,
            "p_formula": "(1 + null maxima >= observed maximum) / (repetitions + 1); each null "
                         "repetition relabels the 29 runes of the second member of each pair",
            "development_controls": dev, "seconds": round(time.monotonic() - t0, 2)}


def _dev_controls(secs, H, seed: int) -> dict:
    """Six development pairs over cleartext: three sharing an additive key, three independent.
    Shows the statistic's power on this exact construction; it cannot calibrate the real data."""
    dev = load_sections(indexes=[7])[7]["ct"]
    rng = np.random.default_rng(seed + 1)
    out = []
    for k in range(6):
        P = dev[k * 40: k * 40 + 300]
        Q = dev[(k * 40 + 310) % (len(dev) - 300): (k * 40 + 310) % (len(dev) - 300) + 300]
        K = rng.integers(0, N, 300)
        K2 = rng.integers(0, N, 300)
        shared = k < 3
        A = (P + K) % N
        B = (Q + (K if shared else K2)) % N
        stats = _all_stats(A, B, H)
        out.append({"pair": k, "shared_key": shared,
                    "statistics_by_offset": dict(zip(map(str, OFFSETS), stats)),
                    "statistic_at_offset_0": stats[OFFSETS.index(0)]})
    return {"pairs": out, "comparisons": len(out) * len(OFFSETS)}


# ------------------------------------------------------------------------ output
def to_markdown(rep: dict) -> str:
    L = [f"# Diagnostics: {rep['kind']}", "", f"**{rep['label']}**", ""]
    if rep["kind"] == "preflight":
        L += [f"{rep['units']} units (lags 1-8 x within / across / all x targets), "
              f"{rep['shuffles_per_target']} shuffles per target "
              f"({'complete' if rep['complete'] else 'INCOMPLETE: time cap reached'}). "
              f"Largest standardised deficit {rep['max_standardised_deficit']:.2f}; "
              f"exploratory maximum-calibrated p = {rep['p_max_over_all_units']:.4f} "
              f"({rep['p_formula']}).", "",
              "| target | lag | stratum | equal / pairs | rate | shuffle mean rate | standardised deficit |",
              "| ---: | ---: | --- | ---: | ---: | ---: | ---: |"]
        for r in rep["rows"]:
            if r["lag"] <= 2 or r["stratum"] == "all":
                L.append(f"| {r['target']} | {r['lag']} | {r['stratum']} | {r['equal']} / {r['pairs']} | "
                         f"{r['rate']:.4f} | {r['shuffle_mean_rate']:.4f} | {r['standardised_deficit']:.2f} |")
        L += ["", "(Only lags 1-2 and the 'all' stratum are listed here; all rows are in the JSON.)"]
    else:
        L += [f"{len(rep['observed'])} observed pair/offset comparisons; {rep['null_repetitions']} "
              f"null repetitions ({'complete' if rep['complete'] else 'INCOMPLETE: time cap reached'}); "
              f"{rep['statistic_evaluations']} statistic evaluations. Maximum observed "
              f"{rep['max_observed']:.4f}; exploratory p = {rep['p_max_over_15']:.4f} "
              f"({rep['p_formula']}).", "",
              "| pair | offset | statistic |", "| --- | ---: | ---: |"]
        for o in rep["observed"]:
            L.append(f"| {o['pair'][0]}-{o['pair'][1]} | {o['offset']} | {o['statistic']:.4f} |")
        L += ["", "Development controls (shared key vs independent key, offset 0):", "",
              "| pair | shared key | statistic |", "| ---: | --- | ---: |"]
        for d in rep["development_controls"]["pairs"]:
            L.append(f"| {d['pair']} | {'yes' if d['shared_key'] else 'no'} | {d['statistic_at_offset_0']:.4f} |")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_diagnostics")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("preflight")
    p.add_argument("--sections", default="13,24,25")
    p.add_argument("--shuffles", type=int, default=REPS)
    k = sub.add_parser("keycancel")
    k.add_argument("--shuffles", type=int, default=REPS)
    for q in (p, k):
        q.add_argument("--out", default="reports/diagnostics")
        q.add_argument("--cap-seconds", type=float, default=CAP_SECONDS)
    args = ap.parse_args(argv)
    if args.cmd == "preflight":
        rep = preflight([int(s) for s in args.sections.split(",")], reps=args.shuffles,
                        cap_s=args.cap_seconds)
    else:
        rep = keycancel(reps=args.shuffles, cap_s=args.cap_seconds)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"diagnostics_{rep['kind']}.json").write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n",
                                                         encoding="utf-8")
    (out / f"diagnostics_{rep['kind']}.md").write_text(to_markdown(rep), encoding="utf-8")
    print(f"wrote {out}/diagnostics_{rep['kind']}.json and .md "
          f"({'complete' if rep['complete'] else 'INCOMPLETE'}, {rep['seconds']} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

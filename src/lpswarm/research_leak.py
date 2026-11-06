"""Leak anatomy: where do the adjacent equal runes (the 86 'doubles') sit?

    python -m lpswarm.research_leak --table data/lp_derived/lp2_runes.csv --out reports/diag

The adjacent-equal shortage is the one real anomaly of the unsolved text (see docs/avenues_explored.md). A rule that forbids repeats has
exceptions, and where the exceptions fall may point at the mechanism. Tests are pre-specified (docs/plan_repeat_shortage.md), in five
families, each with a family p-value that is the maximum over its statistics:

  layout    pair kind, gap type, position in word (from start and end), word length, position in line, colour, line of page, drop cap
  phase     index mod m for m = 2..200, with the global, per-page and per-section index
  spacing   minimum gap, number of close pairs, dispersion and maximum gap between consecutive doubles
  context   the step before and after a double, the rune before and after, the rune itself
  alphabet  odd/even rune index, lower/upper half, vowel/consonant

Null: the same number of doubles at positions drawn uniformly without replacement from the valid adjacent pairs. Statistics are
standardised against that null; a family p is the share of null replicates whose maximum standardised statistic reaches the observed
maximum. Everything is exploratory and deterministic (fixed seed).

Decision rule (fixed in the plan): any family with p < 0.01 means the leak is structured (look for a cipher with exceptions, and the
structure says where); no family below 0.05 means the leak looks like random thinning.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from lpswarm.lp_table import load_table

N = 29
SEED = 20261106
REPS = 2000
MAX_M = 200
VOWELS = ("A", "AE", "E", "I", "IO", "O", "OE", "U", "Y", "EA", "EO")
LABEL = "EXPLORATORY: tests fixed in advance, but the 86 doubles are one sample; a p-value here is not confirmation"
ALPHA_FAMILY = 0.05
STRUCTURED = 0.01


# -------------------------------------------------------------------------------------------- features
def prepare(t: dict) -> dict:
    """Per-pair arrays for the adjacent pairs (i, i+1), i = 0..n-2."""
    c = np.asarray(t["rune"], dtype=np.int64)
    n = len(c)
    page, line, idx = np.asarray(t["page"]), np.asarray(t["line"]), np.asarray(t["idx_in_line"])
    same_page = page[:-1] == page[1:]
    same_line = same_page & (line[:-1] == line[1:])
    # words from the image's dots (a word may run over a line end; a page end is always a boundary)
    boundary = (np.asarray(t["sep"]) != "none") | np.r_[page[:-1] != page[1:], True]
    word_id = np.cumsum(np.r_[0, boundary[:-1]])
    first = np.r_[True, word_id[1:] != word_id[:-1]]
    start_of = np.maximum.accumulate(np.where(first, np.arange(n), 0))
    pos = np.arange(n) - start_of
    wlen = np.bincount(word_id)[word_id]
    inside = (word_id[:-1] == word_id[1:])
    # line length and page-line extent for the 'position in line' and 'line of page' features
    key = page * 1000 + line
    uniq, inv = np.unique(key, return_inverse=True)
    line_len = np.bincount(inv)[inv]
    max_line = {}
    for p, l in zip(page, line):
        max_line[p] = max(max_line.get(p, 0), l)
    last_line = np.array([line[i] == max_line[page[i]] for i in range(n)])
    # per-page running index
    page_start = np.maximum.accumulate(np.where(np.r_[True, page[1:] != page[:-1]], np.arange(n), 0))
    idx_page = np.arange(n) - page_start
    return {"c": c, "n": n, "V": n - 1, "equal": c[:-1] == c[1:], "same_page": same_page, "same_line": same_line, "inside": inside,
            "pos": pos, "wlen": wlen, "line_len": line_len, "idx": idx, "line": line, "last_line": last_line, "page": page,
            "red": np.asarray(t["red"]), "drop": np.asarray(t["drop_cap"]), "sep": np.asarray(t["sep"]), "token": np.asarray(t["token"]),
            "g": np.arange(n), "idx_page": idx_page, "sec_idx": np.asarray(t["section_idx"]), "section": np.asarray(t["section"])}


def layout_features(d: dict) -> dict:
    """name -> (category per pair, applicable mask, number of categories)."""
    V, same_line, inside = d["V"], d["same_line"], d["inside"]
    pos, wlen, idx, ll = d["pos"], d["wlen"], d["idx"], d["line_len"]
    kind = np.where(same_line, 0, np.where(d["same_page"], 1, 2))
    gap = np.where(d["sep"][:-1] == "word", 1, np.where(d["sep"][:-1] == "colon", 2, 0))
    feats = {
        "pair kind (within line / over a line end / over a page end)": (kind, np.ones(V, bool), 3),
        "gap after the first rune (none / word dot / colon)": (gap, same_line, 3),
        "position in word, from the start": (np.minimum(pos[:-1], 5), inside, 6),
        "position in word, from the end": (np.minimum(wlen[:-1] - 1 - pos[1:], 5), inside, 6),
        "word length": (np.clip(wlen[:-1], 2, 8) - 2, inside, 7),
        "position in line (tenths)": (np.minimum((10 * idx[:-1]) // np.maximum(ll[:-1] - 1, 1), 9), same_line, 10),
        "colour (both red / not)": ((d["red"][:-1] & d["red"][1:]).astype(int), np.ones(V, bool), 2),
        "line of the page (first / last / other)": (np.where(d["line"][:-1] == 1, 0, np.where(d["last_line"][:-1], 1, 2)), np.ones(V, bool), 3),
        "involves a drop cap": ((d["drop"][:-1] | d["drop"][1:]).astype(int), np.ones(V, bool), 2)}
    return feats


def context_features(d: dict) -> dict:
    c, V = d["c"], d["V"]
    ok = np.zeros(V, bool)
    ok[1:V - 1] = True                                                    # needs the rune before and the rune after
    prev_step, next_step = np.zeros(V, np.int64), np.zeros(V, np.int64)
    prev_step[1:] = (c[1:V] - c[:V - 1]) % N
    next_step[:V - 1] = (c[2:] - c[1:V]) % N
    before, after = np.zeros(V, np.int64), np.zeros(V, np.int64)
    before[1:] = c[:V - 1]
    after[:V - 1] = c[2:]
    return {"step before the pair": (prev_step, ok, N), "step after the pair": (next_step, ok, N),
            "rune before the pair": (before, ok, N), "rune after the pair": (after, ok, N), "the repeated rune": (c[:-1], np.ones(V, bool), N)}


def alphabet_features(d: dict) -> dict:
    c, V = d["c"][:-1], d["V"]
    vowel = np.isin(d["token"][:-1], VOWELS).astype(int)
    return {"rune index odd / even": (c % 2, np.ones(V, bool), 2), "rune index lower / upper half": ((c >= 15).astype(int), np.ones(V, bool), 2),
            "vowel / consonant": (vowel, np.ones(V, bool), 2)}


# -------------------------------------------------------------------------------------------------- null
def sample_positions(V: int, D: int, reps: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.stack([rng.choice(V, size=D, replace=False) for _ in range(reps)])


def _counts(cat: np.ndarray, appl: np.ndarray, S: np.ndarray, k: int) -> np.ndarray:
    """Doubles per category for each row of position samples S (only applicable positions count)."""
    R = S.shape[0]
    c = np.where(appl[S], cat[S], k)                                      # category k = not applicable, dropped below
    flat = c + (np.arange(R)[:, None] * (k + 1))
    return np.bincount(flat.ravel(), minlength=R * (k + 1)).reshape(R, k + 1)[:, :k]


def chi_square(counts: np.ndarray, prop: np.ndarray) -> np.ndarray:
    n = counts.sum(axis=1, keepdims=True)
    exp = n * prop[None, :]
    use = exp > 0
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(use, (counts - exp) ** 2 / np.where(use, exp, 1), 0.0)
    return terms.sum(axis=1)


def family(feats: dict, obs_pos: np.ndarray, S: np.ndarray) -> dict:
    """Chi-square of each feature against the proportions of all valid pairs; z against the null; family p = maximum."""
    rows, zs_null, zs_obs = [], [], []
    for name, (cat, appl, k) in feats.items():
        prop = np.bincount(np.where(appl, cat, k), minlength=k + 1)[:k].astype(float)
        prop = prop / prop.sum()
        null = chi_square(_counts(cat, appl, S, k), prop)
        obs_counts = _counts(cat, appl, obs_pos[None, :], k)
        obs = float(chi_square(obs_counts, prop)[0])
        mu, sd = float(null.mean()), float(max(null.std(ddof=1), 1e-9))
        zs_null.append((null - mu) / sd)
        zs_obs.append((obs - mu) / sd)
        rows.append({"statistic": name, "observed": obs, "null_mean": mu, "z": (obs - mu) / sd, "p": (1 + int((null >= obs).sum())) / (len(null) + 1),
                     "doubles_counted": int(obs_counts.sum()), "counts": obs_counts[0].tolist(), "expected": (obs_counts.sum() * prop).round(2).tolist()})
    zn = np.max(np.stack(zs_null), axis=0)
    p = (1 + int((zn >= max(zs_obs)).sum())) / (len(zn) + 1)
    return {"statistics": rows, "p_family": p, "max_z": float(max(zs_obs))}


def phase_family(d: dict, obs_pos: np.ndarray, S: np.ndarray, max_m: int = MAX_M) -> dict:
    V = d["V"]
    R = S.shape[0]
    idxs = {"global": d["g"][:-1], "per page": d["idx_page"][:-1], "per section": np.where(d["sec_idx"][:-1] >= 0, d["sec_idx"][:-1], d["g"][:-1])}
    rows, zn_all, zo_all = [], [], []
    for name, ix in idxs.items():
        best = None
        for m in range(2, max_m + 1):
            res = ix % m
            prop = np.bincount(res, minlength=m).astype(float)
            prop /= prop.sum()
            flat = res[S] + np.arange(R)[:, None] * m
            null = chi_square(np.bincount(flat.ravel(), minlength=R * m).reshape(R, m), prop)
            obs = float(chi_square(np.bincount(res[obs_pos], minlength=m)[None, :], prop)[0])
            mu, sd = float(null.mean()), float(max(null.std(ddof=1), 1e-9))
            zn_all.append((null - mu) / sd)
            zo_all.append((obs - mu) / sd)
            if best is None or zo_all[-1] > best["z"]:
                best = {"statistic": f"{name} index, m = {m}", "m": m, "observed": obs, "null_mean": mu, "z": zo_all[-1],
                        "p": (1 + int((null >= obs).sum())) / (R + 1)}
        rows.append(best)
    zn = np.max(np.stack(zn_all), axis=0)
    return {"statistics": rows, "p_family": (1 + int((zn >= max(zo_all)).sum())) / (len(zn) + 1), "max_z": float(max(zo_all)),
            "tests": len(zo_all)}


def spacing_stats(P: np.ndarray, close: int = 20) -> dict:
    P = np.sort(P, axis=1)
    g = np.diff(P, axis=1)
    return {"minimum gap": g.min(axis=1).astype(float), f"pairs of doubles closer than {close}": (g < close).sum(axis=1).astype(float),
            "dispersion of gaps (sd / mean)": g.std(axis=1) / g.mean(axis=1), "maximum gap": g.max(axis=1).astype(float)}


def spacing_family(obs_pos: np.ndarray, S: np.ndarray) -> dict:
    if len(obs_pos) < 3:                                                   # gaps need at least three doubles
        return {"statistics": [], "p_family": 1.0, "max_z": 0.0}
    obs = spacing_stats(obs_pos[None, :])
    null = spacing_stats(S)
    rows, zn_all, zo_all = [], [], []
    for name in obs:
        mu, sd = float(null[name].mean()), float(max(null[name].std(ddof=1), 1e-9))
        zn_all.append(np.abs(null[name] - mu) / sd)
        zo_all.append(abs(obs[name][0] - mu) / sd)
        lo = (1 + int((null[name] <= obs[name][0]).sum())) / (len(S) + 1)
        hi = (1 + int((null[name] >= obs[name][0]).sum())) / (len(S) + 1)
        rows.append({"statistic": name, "observed": float(obs[name][0]), "null_mean": mu, "z": float((obs[name][0] - mu) / sd), "p": min(1.0, 2 * min(lo, hi))})
    zn = np.max(np.stack(zn_all), axis=0)
    return {"statistics": rows, "p_family": (1 + int((zn >= max(zo_all)).sum())) / (len(zn) + 1), "max_z": float(max(zo_all))}


# ------------------------------------------------------------------------------------------------ report
def analyse_positions(d: dict, obs_pos: np.ndarray, reps: int = REPS, seed: int = SEED, max_m: int = MAX_M) -> dict:
    S = sample_positions(d["V"], len(obs_pos), reps, seed)
    fams = {"layout": family(layout_features(d), obs_pos, S), "phase": phase_family(d, obs_pos, S, max_m),
            "spacing": spacing_family(obs_pos, S), "context": family(context_features(d), obs_pos, S),
            "alphabet": family(alphabet_features(d), obs_pos, S)}
    pmin = min(f["p_family"] for f in fams.values())
    verdict = ("structured" if pmin < STRUCTURED else "looks like random thinning" if pmin >= ALPHA_FAMILY else "borderline (a family between 0.01 and 0.05)")
    return {"runes": d["n"], "pairs": d["V"], "doubles": int(len(obs_pos)), "reps": reps, "seed": seed, "families": fams,
            "p_smallest_family": pmin, "p_smallest_family_bonferroni": min(1.0, pmin * len(fams)), "verdict": verdict}


def analyse(t: dict, reps: int = REPS, seed: int = SEED, max_m: int = MAX_M) -> dict:
    d = prepare(t)
    return analyse_positions(d, np.nonzero(d["equal"])[0], reps, seed, max_m)


def planted_weights(d: dict, kind: str) -> np.ndarray:
    """Weights over the valid pairs for a planted effect (a known structure the tests should see)."""
    V = d["V"]
    w = np.ones(V)
    g = d["g"][:-1]
    if kind == "phase (20% of doubles on one residue mod 17)":
        w = np.where(g % 17 == 3, (0.2 / (1 / 17)) / ((1 - 0.2) / (1 - 1 / 17)), 1.0)
    elif kind == "gap (half the doubles across a word dot)":
        frac = np.mean(d["sep"][:-1] == "word")
        w = np.where(d["sep"][:-1] == "word", (0.5 / frac) / ((0.5) / (1 - frac)), 1.0)
    elif kind == "clusters (half the doubles within 30 of ten centres)":
        rng = np.random.default_rng(3)
        centres = rng.choice(V, 10, replace=False)
        near = np.zeros(V, bool)
        for c in centres:
            near[max(c - 30, 0):c + 30] = True
        frac = near.mean()
        w = np.where(near, (0.5 / frac) / (0.5 / (1 - frac)), 1.0)
    elif kind == "context (80% after a small step)":
        step = np.zeros(V, np.int64)
        step[1:] = (d["c"][1:V] - d["c"][:V - 1]) % N
        small = (step >= 1) & (step <= 3)
        frac = small.mean()
        w = np.where(small, (0.8 / frac) / (0.2 / (1 - frac)), 1.0)
    elif kind == "alphabet (80% on vowel runes)":
        vow = np.isin(d["token"][:-1], VOWELS)
        frac = vow.mean()
        w = np.where(vow, (0.8 / frac) / (0.2 / (1 - frac)), 1.0)
    return w / w.sum()


def calibration_and_power(t: dict, sims: int = 40, reps: int = 400, seed: int = SEED) -> dict:
    """How often each family reaches p < 0.05 when the doubles are placed at random (should be about 5%), and when a known structure is
    planted (the power of this analysis at 86 doubles)."""
    d = prepare(t)
    D = int(d["equal"].sum())
    rng = np.random.default_rng(seed + 7)
    names = ["layout", "phase", "spacing", "context", "alphabet"]
    out = {"sims": sims, "reps": reps, "doubles": D, "null": {n: 0 for n in names}, "planted": {}}
    for k in range(sims):
        pos = rng.choice(d["V"], size=D, replace=False)
        r = analyse_positions(d, pos, reps, seed + 100 + k)
        for n in names:
            out["null"][n] += r["families"][n]["p_family"] < 0.05
    kinds = {"phase (20% of doubles on one residue mod 17)": "phase", "gap (half the doubles across a word dot)": "layout",
             "clusters (half the doubles within 30 of ten centres)": "spacing", "context (80% after a small step)": "context",
             "alphabet (80% on vowel runes)": "alphabet"}
    for kind, fam in kinds.items():
        w = planted_weights(d, kind)
        hit = 0
        for k in range(sims):
            pos = rng.choice(d["V"], size=D, replace=False, p=w)
            hit += analyse_positions(d, pos, reps, seed + 500 + k)["families"][fam]["p_family"] < 0.01
        out["planted"][kind] = {"family": fam, "detected_p_below_0.01": hit / sims}
    out["null"] = {n: v / sims for n, v in out["null"].items()}
    return out


def _p(x: float) -> str:
    return "<0.001" if x < 0.001 else f"{x:.3f}"


def markdown(rep: dict) -> str:
    L = ["# Leak anatomy: where the adjacent equal runes sit", "", f"**{LABEL}.**", "",
         f"{rep['doubles']} doubles in {rep['pairs']} adjacent pairs ({rep['runes']} runes); null: the same number of doubles at positions drawn "
         f"uniformly from the valid pairs ({rep['reps']} replicates, seed {rep['seed']}). A family p is the maximum standardised statistic "
         "against the same null. Rule fixed in advance: any family p < 0.01 = structured leak; none below 0.05 = looks like random thinning.", "",
         f"**Verdict: {rep['verdict']}.** Smallest family p {_p(rep['p_smallest_family'])} (Bonferroni over 5 families {_p(rep['p_smallest_family_bonferroni'])}).", "",
         "| family | statistics | family p | largest z |", "| --- | ---: | ---: | ---: |"]
    for name, f in rep["families"].items():
        L.append(f"| {name} | {f.get('tests', len(f['statistics']))} | {_p(f['p_family'])} | {f['max_z']:.2f} |")
    for name, f in rep["families"].items():
        L += ["", f"## {name}", ""]
        if name == "phase":
            L += ["Best modulus for each index (the maximum over m = 2..200 sets the family p):", ""]
        L += ["| statistic | observed | null mean | z | p (single) |", "| --- | ---: | ---: | ---: | ---: |"]
        for r in sorted(f["statistics"], key=lambda r: -r["z"])[:12]:
            L.append(f"| {r['statistic']} | {r['observed']:.2f} | {r['null_mean']:.2f} | {r['z']:+.2f} | {_p(r['p'])} |")
    cal = rep.get("calibration")
    if cal:
        L += ["", "## What this analysis could have seen", "",
              f"{cal['sims']} simulations with {cal['doubles']} doubles each. Under a random placement a family should reach p < 0.05 about 5% of the time: "
              + ", ".join(f"{n} {100 * v:.0f}%" for n, v in cal["null"].items()) + ".", "",
              "Planted structures, share of simulations with the matching family p < 0.01:", "", "| planted structure | family | detected |", "| --- | --- | ---: |"]
        for kind, v in cal["planted"].items():
            L.append(f"| {kind} | {v['family']} | {100 * v['detected_p_below_0.01']:.0f}% |")
    lay = {r["statistic"]: r for r in rep["families"]["layout"]["statistics"]}
    for key in ("pair kind (within line / over a line end / over a page end)", "gap after the first rune (none / word dot / colon)"):
        if key in lay:
            r = lay[key]
            L += ["", f"{key}: doubles {r['counts']} against expected {r['expected']}."]
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_leak", description=__doc__.split("\n")[0])
    ap.add_argument("--table", default="data/lp_derived/lp2_runes.csv")
    ap.add_argument("--out", default="reports/diag")
    ap.add_argument("--reps", type=int, default=REPS)
    ap.add_argument("--sims", type=int, default=40, help="calibration / power simulations (0 to skip)")
    args = ap.parse_args(argv)
    t = load_table(args.table)
    rep = analyse(t, args.reps)
    if args.sims:
        rep["calibration"] = calibration_and_power(t, args.sims)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "leak_anatomy.json").write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = markdown(rep)
    (out / "leak_anatomy.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

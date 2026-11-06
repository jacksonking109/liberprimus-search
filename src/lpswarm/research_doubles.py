"""The repeat shortage in detail: per rune, per page, per lag, and the transcription against the page images.

    python -m lpswarm.research_doubles perrune --out reports/diag
    python -m lpswarm.research_doubles align   --out reports/diag
    python -m lpswarm.research_doubles all     --out reports/diag

No oracle, no models, no key hypotheses. Fixed seeds, exploratory.

perrune  is the deficit of adjacent identical runes the same for every rune, page and lag? Expected counts are exact
         under a permutation of each page's (section's) known runes among its known positions, the same null the
         shuffles use; the uniformity test conditions on the observed total (multinomial, Monte Carlo p). A power line
         says what the test could have seen.
align    the transcription of manifest sections 10-25 aligned with the glyph sequence read from pages 17-72: matches,
         substitutions, extra glyphs on either side, and every double present in only one source.

Image reading takes about 3 minutes; `--cache FILE` keeps the rune sequences (no images) as JSON for re-runs.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np

N = 29
SEED = 20261105
REPS = 1999
LAGS = 8
HET_REPS = 20000
POWER_SIMS = 2000
PAGES = [f"{n:02d}" for n in range(17, 73)]
SECTIONS = tuple(range(10, 26))
ALIGN_GATE = 0.95
LABEL = "EXPLORATORY: units chosen after inspecting the data; a p-value here is not confirmation"


# ------------------------------------------------------------------------------------------------ units
def image_units(read: dict) -> dict:
    """Rune sequence (-1 = unknown or unresolved glyph) and line number per glyph for pages 17-72, reading order."""
    lab, out = read["lab"], {}
    for pg in PAGES:
        r = read["reads"].get(pg)
        if r is None:
            continue
        gl = sorted(r["glyphs"], key=lambda g: (g["line"], g["x0"]))
        out[pg] = {"runes": [int(lab.get(g["shape"], -1)) if g["shape"] >= 0 and not g.get("unresolved") else -1
                             for g in gl],
                   "lines": [int(g["line"]) for g in gl]}
    return out


def text_units(secs: dict, ids) -> dict:
    return {str(i): np.asarray(secs[i]["ct"], dtype=np.int64) for i in ids if i in secs}


def _prep(seq, lags: int = LAGS):
    seq = np.asarray(seq, dtype=np.int64)
    known = seq >= 0
    kn = np.nonzero(known)[0]
    valid = {k: (np.nonzero(known[:-k] & known[k:])[0] if len(seq) > k else np.zeros(0, dtype=np.int64))
             for k in range(1, lags + 1)}
    return seq, kn, valid


# ---------------------------------------------------------------------------------------------- counts
def expected(units: dict, lags: int = LAGS) -> dict:
    """Exact expectations when a unit's known runes are permuted among its known positions."""
    e_r, e_k, e_f2 = np.zeros(N), np.zeros(lags), 0.0
    e_u, pairs_u = {}, {}
    for name, seq in units.items():
        seq, kn, valid = _prep(seq, lags)
        m = len(kn)
        pairs_u[name] = int(len(valid[1]))
        if m < 2:
            e_u[name] = 0.0
            continue
        n = np.bincount(seq[kn], minlength=N).astype(float)
        per = n * (n - 1) / (m * (m - 1))
        e_r += len(valid[1]) * per
        e_u[name] = float(len(valid[1]) * per.sum())
        for k in range(1, lags + 1):
            e_k[k - 1] += len(valid[k]) * per.sum()
        e_f2 += len(valid[1]) * float(((n / m) ** 2).sum())
    return {"rune": e_r, "lag": e_k, "f2": e_f2, "unit": e_u, "pairs": pairs_u}


def observed(units: dict, lags: int = LAGS) -> dict:
    d_r, d_k, d_u = np.zeros(N, int), np.zeros(lags, int), {}
    pairs_k = np.zeros(lags, int)
    for name, seq in units.items():
        seq, kn, valid = _prep(seq, lags)
        for k in range(1, lags + 1):
            a = seq[valid[k]]
            eq = a == seq[valid[k] + k]
            d_k[k - 1] += int(eq.sum())
            pairs_k[k - 1] += len(valid[k])
            if k == 1:
                c = np.bincount(a[eq], minlength=N)
                d_r += c
                d_u[name] = int(eq.sum())
    return {"rune": d_r, "lag": d_k, "unit": d_u, "lag_pairs": pairs_k}


def null_counts(units: dict, reps: int = REPS, seed: int = SEED, lags: int = LAGS):
    """Shuffle null: per-rune doubles and per-lag equal-pair counts, one row per replicate."""
    rng = np.random.default_rng(seed)
    by_rune, by_lag = np.zeros((reps, N), int), np.zeros((reps, lags), int)
    for seq in units.values():
        seq, kn, valid = _prep(seq, lags)
        if len(kn) < 2:
            continue
        vals = seq[kn]
        for r in range(reps):
            sh = seq.copy()
            sh[kn] = rng.permutation(vals)
            for k in range(1, lags + 1):
                a = sh[valid[k]]
                eq = a == sh[valid[k] + k]
                by_lag[r, k - 1] += int(eq.sum())
                if k == 1:
                    by_rune[r] += np.bincount(a[eq], minlength=N)
    return by_rune, by_lag


def holm(p) -> np.ndarray:
    p = np.asarray(p, float)
    m = len(p)
    adj, run = np.empty(m), 0.0
    for rank, i in enumerate(np.argsort(p)):
        run = max(run, (m - rank) * p[i])
        adj[i] = min(1.0, run)
    return adj


def heterogeneity(d, e, reps: int = HET_REPS, seed: int = SEED) -> dict:
    """Is d proportional to e? Conditional on the total, uniform suppression gives d ~ Multinomial(D, e / sum e)."""
    d, e = np.asarray(d, float), np.asarray(e, float)
    keep = e > 0
    D = int(round(d[keep].sum()))
    p = e[keep] / e[keep].sum()
    mu = D * p
    stat = float(((d[keep] - mu) ** 2 / mu).sum())
    draws = np.random.default_rng(seed).multinomial(D, p, size=reps)
    null = ((draws - mu) ** 2 / mu).sum(axis=1)
    resid = np.full(len(d), np.nan)
    resid[keep] = (d[keep] - mu) / np.sqrt(mu)
    lo = (1 + (draws <= d[keep]).sum(axis=0)) / (reps + 1)
    hi = (1 + (draws >= d[keep]).sum(axis=0)) / (reps + 1)
    p_cell = np.full(len(d), np.nan)
    p_cell[keep] = holm(np.minimum(1.0, 2 * np.minimum(lo, hi)))
    return {"stat": stat, "p": (1 + int((null >= stat).sum())) / (reps + 1), "total": D,
            "null_95": float(np.quantile(null, 0.95)), "resid": resid, "p_cell_holm": p_cell, "cells": int(keep.sum())}


def power_line(e, total: int, null_95: float, sims: int = POWER_SIMS, seed: int = SEED) -> dict:
    """How often the uniformity test (p < 0.05) fires when the same number of doubles is distributed unevenly."""
    e = np.asarray(e, float)
    keep = e > 0
    rng = np.random.default_rng(seed + 1)
    mu = total * e[keep] / e[keep].sum()
    order = [i for i in np.argsort(-e) if keep[i]]
    mid = order[len(order) // 2]

    def fire(weights):
        w = np.where(keep, weights, 0.0)
        draws = rng.multinomial(total, w / w.sum(), size=sims)[:, keep]
        return float((((draws - mu) ** 2 / mu).sum(axis=1) > null_95).mean())

    w1 = e.copy(); w1[order[:5]] = 0
    w2 = np.zeros_like(e); w2[order[:5]] = e[order[:5]]
    w3 = e.copy(); w3[mid] *= 4
    return {"top5_runes_never_double": fire(w1), "only_top5_runes_double": fire(w2), "one_mid_rune_4x": fire(w3)}


# ------------------------------------------------------------------------------------------ per-rune report
def perrune_report(units: dict, tokens: list[str], reps: int = REPS, seed: int = SEED, lags: int = LAGS) -> dict:
    exp, obs = expected(units, lags), observed(units, lags)
    by_rune, by_lag = null_counts(units, reps, seed, lags)
    D = int(obs["rune"].sum())
    rows = []
    p2 = []
    for r in range(N):
        lo = (1 + int((by_rune[:, r] <= obs["rune"][r]).sum())) / (reps + 1)
        hi = (1 + int((by_rune[:, r] >= obs["rune"][r]).sum())) / (reps + 1)
        p2.append(min(1.0, 2 * min(lo, hi)))
        rows.append({"rune": r, "token": tokens[r], "doubles": int(obs["rune"][r]), "expected": float(exp["rune"][r]),
                     "ratio": float(obs["rune"][r] / exp["rune"][r]) if exp["rune"][r] > 0 else None,
                     "p_deficit": lo, "p_excess": hi})
    het_r = heterogeneity(obs["rune"], exp["rune"], seed=seed)
    for row, a, z, q in zip(rows, holm(p2), het_r["resid"], het_r["p_cell_holm"]):
        row["p_holm_vs_chance"] = float(a)
        row["resid_vs_pooled"] = None if np.isnan(z) else float(z)
        row["p_holm_vs_pooled"] = None if np.isnan(q) else float(q)
    names = list(units)
    d_u = np.array([obs["unit"][n] for n in names])
    e_u = np.array([exp["unit"][n] for n in names])
    het_u = heterogeneity(d_u, e_u, seed=seed)
    unit_rows = [{"unit": n, "doubles": int(d), "expected": float(e), "resid": (None if np.isnan(z) else float(z)),
                  "pairs": exp["pairs"][n]} for n, d, e, z in zip(names, d_u, e_u, het_u["resid"])]
    lag_rows = []
    for k in range(lags):
        nk = by_lag[:, k]
        sd = float(nk.std(ddof=1))
        lag_rows.append({"lag": k + 1, "pairs": int(obs["lag_pairs"][k]), "equal": int(obs["lag"][k]),
                         "rate": float(obs["lag"][k] / max(obs["lag_pairs"][k], 1)),
                         "expected": float(exp["lag"][k]), "ratio": float(obs["lag"][k] / exp["lag"][k]),
                         "z": float((obs["lag"][k] - nk.mean()) / max(sd, 1e-9)),
                         "p_deficit": (1 + int((nk <= obs["lag"][k]).sum())) / (reps + 1)})
    pw = power_line(exp["rune"], D, het_r["null_95"], seed=seed)
    pairs = int(sum(exp["pairs"].values()))
    return {"units": len(units), "pairs": pairs, "doubles": D, "rate": D / pairs if pairs else None,
            "expected_permutation": float(exp["rune"].sum()), "expected_frequency_squared": float(exp["f2"]),
            "ratio_permutation": D / float(exp["rune"].sum()), "ratio_frequency_squared": D / float(exp["f2"]),
            "reps": reps, "runes": rows, "heterogeneity_runes": {k: v for k, v in het_r.items() if k not in ("resid", "p_cell_holm")},
            "heterogeneity_units": {k: v for k, v in het_u.items() if k not in ("resid", "p_cell_holm")}, "unit_rows": unit_rows,
            "lags": lag_rows, "power": pw}


# --------------------------------------------------------------------------------------------- alignment
def align_sequences(a, b) -> dict:
    """Align image glyphs `a` with text runes `b`. Status per element: 0 equal, 1 substituted, 2 extra on this side."""
    a, b = list(map(int, a)), list(map(int, b))
    a2b = np.full(len(a), -1, dtype=np.int64)
    b2a = np.full(len(b), -1, dtype=np.int64)
    sa, sb = np.zeros(len(a), dtype=np.int8), np.zeros(len(b), dtype=np.int8)
    a_pos = np.zeros(len(a), dtype=np.int64)          # text position an image-only glyph sits at
    subs = Counter()
    for tag, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            a2b[i1:i2] = np.arange(j1, j2)
            b2a[j1:j2] = np.arange(i1, i2)
            a_pos[i1:i2] = np.arange(j1, j2)
            continue
        m = min(i2 - i1, j2 - j1)
        for t in range(m):
            a2b[i1 + t], b2a[j1 + t] = j1 + t, i1 + t
            sa[i1 + t] = sb[j1 + t] = 1
            subs[(a[i1 + t], b[j1 + t])] += 1
        a_pos[i1:i2] = np.minimum(np.arange(j1, j1 + (i2 - i1)), max(len(b) - 1, 0))
        sa[i1 + m:i2] = 2
        sb[j1 + m:j2] = 2
    return {"a2b": a2b, "b2a": b2a, "sa": sa, "sb": sb, "a_pos": a_pos, "subs": subs, "a": a, "b": b}


def _doubles(x) -> np.ndarray:
    x = np.asarray(x)
    return np.nonzero((x[:-1] >= 0) & (x[:-1] == x[1:]))[0]


def reconcile(al: dict) -> dict:
    """Doubles present in both sources, in the image only, in the text only, with the reason when they differ."""
    a, b, a2b, b2a = np.asarray(al["a"]), np.asarray(al["b"]), al["a2b"], al["b2a"]
    both, image_only, text_only = [], [], []
    for i in _doubles(a):
        j, j2 = a2b[i], a2b[i + 1]
        if j >= 0 and j2 == j + 1:
            (both if b[j] >= 0 and b[j] == b[j2] else image_only).append((int(i), int(j), "text has different runes"))
        else:
            image_only.append((int(i), int(j) if j >= 0 else None, "a glyph has no counterpart in the text"))
    for j in _doubles(b):
        i, i2 = b2a[j], b2a[j + 1]
        if i >= 0 and i2 == i + 1:
            if not (a[i] >= 0 and a[i] == a[i2]):
                text_only.append((int(j), int(i), "image has different glyphs"))
        else:
            text_only.append((int(j), int(i) if i >= 0 else None, "a rune has no counterpart in the image"))
    return {"both": both, "image_only": image_only, "text_only": text_only}


def _context(seq, i: int, tokens, width: int = 6) -> str:
    lo, hi = max(0, i - width), min(len(seq), i + 2 + width)
    parts = [(tokens[v] if v >= 0 else "?") for v in seq[lo:hi]]
    k = i - lo
    parts[k] = "[" + parts[k]
    parts[k + 1] = parts[k + 1] + "]"
    return " ".join(parts)


def align_report(units: dict, secs: dict, tokens: list[str], ids=SECTIONS) -> dict:
    pages = list(units)
    img = [r for p in pages for r in units[p]["runes"]]
    img_page = [p for p in pages for _ in units[p]["runes"]]
    img_line = [ln for p in pages for ln in units[p]["lines"]]
    ids = [i for i in ids if i in secs]
    text = [int(v) for i in ids for v in secs[i]["ct"]]
    bounds = np.cumsum([0] + [len(secs[i]["ct"]) for i in ids])
    al = align_sequences(img, text)
    sa, sb = al["sa"], al["sb"]
    matched = float((sa == 0).mean()) if len(sa) else 0.0
    rep = {"image_glyphs": len(img), "text_runes": len(text), "matched": int((sa == 0).sum()),
           "matched_fraction_of_image": matched, "matched_fraction_of_text": float((sb == 0).mean()),
           "substituted": int((sa == 1).sum()), "image_only": int((sa == 2).sum()), "text_only": int((sb == 2).sum()),
           "unknown_image_glyphs": int(sum(1 for v in img if v < 0)), "gate": ALIGN_GATE, "gate_passed": matched >= ALIGN_GATE,
           "confusions": [{"image": (tokens[a] if a >= 0 else "?"), "text": tokens[b], "count": c}
                          for (a, b), c in al["subs"].most_common(12)]}
    extra = np.nonzero(sa == 2)[0]                                   # image-only glyphs, placed by text position
    extra_sec = np.searchsorted(bounds, al["a_pos"][extra], side="right") - 1
    sec_rows = []
    for k, i in enumerate(ids):
        lo, hi = int(bounds[k]), int(bounds[k + 1])
        sec_rows.append({"section": i, "text_runes": hi - lo, "text_matched": int((sb[lo:hi] == 0).sum()),
                         "text_substituted": int((sb[lo:hi] == 1).sum()), "text_only": int((sb[lo:hi] == 2).sum()),
                         "image_only": int((extra_sec == k).sum())})
    page_err = Counter()
    page_n = Counter(img_page)
    for x, s in enumerate(sa):
        if s:
            page_err[img_page[x]] += 1
    rep["sections"] = sec_rows
    rep["worst_pages"] = [{"page": p, "glyphs": page_n[p], "mismatched": c, "rate": c / page_n[p]}
                          for p, c in page_err.most_common(8)]
    if not rep["gate_passed"]:
        rep["doubles"] = None
        return rep
    rc = reconcile(al)
    rows = []
    for kind in ("image_only", "text_only"):
        for item in rc[kind]:
            if kind == "image_only":
                i = item[0]
                rows.append({"kind": kind, "page": img_page[i], "line": img_line[i] + 1, "reason": item[2],
                             "image": _context(img, i, tokens),
                             "text": _context(text, item[1], tokens) if item[1] is not None else None})
            else:
                j = item[0]
                i = item[1]
                rows.append({"kind": kind, "page": img_page[i] if i is not None else None,
                             "line": img_line[i] + 1 if i is not None else None, "reason": item[2],
                             "image": _context(img, i, tokens) if i is not None else None,
                             "text": _context(text, j, tokens)})
    rep["doubles"] = {"both": len(rc["both"]), "image_only": len(rc["image_only"]), "text_only": len(rc["text_only"]),
                      "image_total": len(_doubles(img)), "text_total": len(_doubles(text)), "differences": rows}
    return rep


# --------------------------------------------------------------------------------------------- rendering
def _p(p) -> str:
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def perrune_markdown(rep: dict, name: str) -> list[str]:
    het, hu, pw = rep["heterogeneity_runes"], rep["heterogeneity_units"], rep["power"]
    L = [f"## {name}", "",
         f"{rep['doubles']} doubles in {rep['pairs']} pairs ({100 * rep['rate']:.2f}%) over {rep['units']} units. Expected under the "
         f"shuffle: {rep['expected_permutation']:.0f} (ratio {rep['ratio_permutation']:.2f}); with the simpler frequency-squared "
         f"expectation {rep['expected_frequency_squared']:.0f} (ratio {rep['ratio_frequency_squared']:.2f}).", "",
         f"**Uniform across runes?** chi-square {het['stat']:.1f} on {het['cells'] - 1} df, Monte Carlo p = {_p(het['p'])} "
         f"(null 95% point {het['null_95']:.1f}). **Uniform across units?** chi-square {hu['stat']:.1f} on {hu['cells'] - 1} df, "
         f"p = {_p(hu['p'])}.", "",
         f"Power at {het['total']} doubles (share of simulations with p < 0.05): five most frequent runes never double "
         f"{pw['top5_runes_never_double']:.2f}; only the five most frequent runes double {pw['only_top5_runes_double']:.2f}; "
         f"one mid-frequency rune at 4x {pw['one_mid_rune_4x']:.2f}.", "",
         "Per rune: `p deficit` is against the shuffle (is this rune short of chance?); `resid` and `Holm p` compare the rune "
         "with the pooled rate (is this rune different from the others?).", "",
         "| rune | doubles | expected | ratio | p deficit | resid vs pooled | Holm p vs pooled |",
         "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in sorted(rep["runes"], key=lambda r: -r["expected"]):
        res = "" if r["resid_vs_pooled"] is None else f"{r['resid_vs_pooled']:+.1f}"
        q = "" if r["p_holm_vs_pooled"] is None else _p(r["p_holm_vs_pooled"])
        L.append(f"| {r['token']} | {r['doubles']} | {r['expected']:.1f} | "
                 f"{'' if r['ratio'] is None else format(r['ratio'], '.2f')} | {_p(r['p_deficit'])} | {res} | {q} |")
    L += ["", "Equal runes at distance k (pairs with both runes known; shuffle null):", "",
          "| lag | pairs | equal | rate | expected | ratio | z | p deficit |", "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rep["lags"]:
        L.append(f"| {r['lag']} | {r['pairs']} | {r['equal']} | {100 * r['rate']:.2f}% | {r['expected']:.0f} | {r['ratio']:.2f} | "
                 f"{r['z']:.1f} | {_p(r['p_deficit'])} |")
    worst = sorted([u for u in rep["unit_rows"] if u["resid"] is not None], key=lambda u: -abs(u["resid"]))[:6]
    L += ["", "Units furthest from uniform (standardised residual): " +
          ", ".join(f"{u['unit']} ({u['doubles']} vs {u['expected'] * rep['doubles'] / rep['expected_permutation']:.1f}, z {u['resid']:+.1f})"
                    for u in worst), ""]
    return L


def align_markdown(rep: dict) -> list[str]:
    L = ["# Transcription against the page images", "", f"**{LABEL}.** Manifest sections 10-25 against the glyph sequence of pages "
         "17-72, aligned with a longest-matching-block alignment; substitutions are paired positionally inside a replaced block.", "",
         f"Image glyphs {rep['image_glyphs']}, text runes {rep['text_runes']}. Matched {rep['matched']} "
         f"({100 * rep['matched_fraction_of_image']:.2f}% of the image glyphs, {100 * rep['matched_fraction_of_text']:.2f}% of the text), "
         f"substituted {rep['substituted']}, image-only {rep['image_only']}, text-only {rep['text_only']}; "
         f"{rep['unknown_image_glyphs']} image glyphs have no known shape. Gate: {100 * rep['gate']:.0f}% of image glyphs must "
         f"align: {'passed' if rep['gate_passed'] else 'NOT passed, so the doubles comparison is not reported'}.", "",
         "| section | text runes | matched | substituted | text-only | image-only (at this section) |",
         "| ---: | ---: | ---: | ---: | ---: | ---: |"]
    for s in rep["sections"]:
        L.append(f"| {s['section']} | {s['text_runes']} | {s['text_matched']} | {s['text_substituted']} | {s['text_only']} | {s['image_only']} |")
    L += ["", "Most common substitutions (image / text): " + (", ".join(
        f"{c['image']}/{c['text']} x{c['count']}" for c in rep["confusions"]) or "none"), "",
          "Image pages with the most mismatches: " + (", ".join(
              f"{w['page']} ({w['mismatched']}/{w['glyphs']})" for w in rep["worst_pages"]) or "none"), ""]
    d = rep.get("doubles")
    if d:
        L += ["## Doubles in both sources", "",
              f"Image {d['image_total']}, text {d['text_total']}; in both {d['both']}, image only {d['image_only']}, "
              f"text only {d['text_only']}.", ""]
        if d["differences"]:
            L += ["| in | page | line | reason | image context | text context |", "| --- | --- | ---: | --- | --- | --- |"]
            for r in d["differences"]:
                L.append(f"| {r['kind'].replace('_', ' ')} | {r['page'] or ''} | {r['line'] or ''} | {r['reason']} | "
                         f"{r['image'] or ''} | {r['text'] or ''} |")
            L.append("")
    return L


# ------------------------------------------------------------------------------------------------- CLI
def _jsonable(o):
    if isinstance(o, dict):
        return {str(k): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return o


def load_image_units(img_dir: str, cache: str | None) -> dict:
    if cache and Path(cache).exists():
        return json.loads(Path(cache).read_text(encoding="utf-8"))
    from lpswarm.pageimages import read_all
    units = image_units(read_all(img_dir, keep=True))
    if cache:
        Path(cache).parent.mkdir(parents=True, exist_ok=True)
        Path(cache).write_text(json.dumps(units), encoding="utf-8")
    return units


def main(argv: list[str] | None = None) -> int:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET, load_sections
    from lpswarm.research_structure import UNSOLVED
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_doubles", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["perrune", "align", "all"])
    ap.add_argument("--out", default="reports/diag")
    ap.add_argument("--dir", default="data/lp_images")
    ap.add_argument("--cache", default=None, help="JSON file for the image rune sequences (no images)")
    ap.add_argument("--reps", type=int, default=REPS)
    args = ap.parse_args(argv)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    tokens = list(get_alphabet(ALPHABET).tokens)
    units = load_image_units(args.dir, args.cache)
    secs = load_sections(indexes=list(SECTIONS))
    if args.command in ("perrune", "all"):
        img = {p: np.asarray(u["runes"]) for p, u in units.items()}
        reps = {"image, pages 17-72": perrune_report(img, tokens, args.reps),
                "text, sections 10-25": perrune_report(text_units(secs, SECTIONS), tokens, args.reps),
                "text, the 300+ rune sections (the 84-double count)": perrune_report(
                    text_units(secs, [i for i in UNSOLVED if i in secs]), tokens, args.reps)}
        (out / "perrune.json").write_text(json.dumps(_jsonable(reps), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        L = ["# Per-rune, per-unit and per-lag breakdown of the repeat shortage", "",
             f"**{LABEL}.** Image and text are the same pages, so they are a consistency check, not two independent samples. "
             "Expected counts are exact under a permutation of each unit's known runes among its known positions.", ""]
        for name, rep in reps.items():
            L += perrune_markdown(rep, name)
        (out / "perrune.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("\n".join(L))
    if args.command in ("align", "all"):
        rep = align_report(units, secs, tokens)
        (out / "alignment.json").write_text(json.dumps(_jsonable(rep), indent=1, sort_keys=True) + "\n", encoding="utf-8")
        text = "\n".join(align_markdown(rep)) + "\n"
        (out / "alignment.md").write_text(text, encoding="utf-8")
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

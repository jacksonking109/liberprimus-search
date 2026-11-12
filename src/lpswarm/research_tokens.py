"""The two-character token tables on images 66-68 (community pages 49-51): transcription and plain statistics.

    python -m lpswarm.research_tokens read      # images -> data/lp_derived/tokens_66_68.csv (needs data/lp_images)
    python -m lpswarm.research_tokens analyse   # statistics from the CSV (no images needed)

The tokens are set in one computer typeface, so the same character renders as identical pixels. `read` cuts each token row into
connected components, groups components of identical shape and size (60 groups) and maps each group to a character through the
hand-checked table SHAPE_LABELS (the labels came from looking at one example of each group, with cap-height 'I' told from
ascender-height 'l' by size and 'Q' from 'O' by pixel difference). A token is two characters; the first is always a digit 0-4, the
second a digit or letter. Value = 62 * first + position of the second in 0-9A-Za-z (0 to 263).

`analyse`: uniformity of the values over 0..263, repeat counts, equal-pair counts at lags 1-128, residues mod m, and the 'pointer'
reading (token value as an index into a page's runes) scored by IC against random values. Exploratory; no models.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np

A62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
M = 264                                       # values 0..263 (first char 0-4; first char 4 only up to 'F')
# token rows (y ranges, found from the horizontal ink profile inside x 640-1760) on each page
ROWS = {
    66: [(1244, 1342), (1427, 1520), (1606, 1699), (1787, 1856), (1960, 2035), (2139, 2220), (2318, 2416), (2497, 2595), (2681, 2758), (2855, 2936)],
    67: [(627, 721), (809, 880), (985, 1078), (1165, 1238), (1344, 1438), (1519, 1616), (1704, 1796), (1877, 1954), (2060, 2133), (2239, 2333),
         (2414, 2512), (2597, 2669), (2772, 2847)],
    68: [(629, 704), (803, 901), (987, 1056), (1165, 1237), (1340, 1438), (1523, 1617), (1698, 1775), (1881, 1974), (2062, 2154)],
}
# Characters of the 60 shape groups, in order of group size then first appearance (as clustered by `shape_groups` below).
SHAPE_LABELS = ("2 0 1 3 4 O D p 9 L s W r t v M E C l 6 g n I K G k q 8 a X x U 5 S o w u N 7 H P d J V e Z c A B T b F m Y R i h j 0J j").split()
Q_DIFF = 0.02                                 # an 'O'-shaped group member this far from the 'O' template is a 'Q'


def token_value(tok: str) -> int:
    return int(tok[0]) * 62 + A62.index(tok[1])


def components(page: int, imgdir: str = "data/lp_images"):
    from PIL import Image
    from scipy import ndimage as ndi
    a = np.array(Image.open(Path(imgdir) / f"{page:02d}.jpg").convert("L")) < 128
    out = []
    for ri, (y0, y1) in enumerate(ROWS[page]):
        band = a[y0 - 5:y1 + 5, 560:1840]
        lab, _ = ndi.label(band)
        comps = sorted((o[1].start, o[1].stop, o[0].start, o[0].stop, i + 1) for i, o in enumerate(ndi.find_objects(lab)))
        merged: list = []
        for c in comps:
            if merged and c[0] < merged[-1][1] - 1:
                m = merged[-1]
                merged[-1] = [m[0], max(m[1], c[1]), min(m[2], c[2]), max(m[3], c[3]), m[4] + [c[4]]]
            else:
                merged.append([c[0], c[1], c[2], c[3], [c[4]]])
        for ci, m in enumerate([m for m in merged if m[0] > 2 and m[1] < 1278]):      # drop band-edge slivers
            img = np.isin(lab[:, m[0]:m[1]], m[4])[m[2]:m[3]].astype(np.uint8)
            out.append({"page": page, "row": ri, "col": ci, "w": m[1] - m[0], "h": m[3] - m[2], "bot": m[3] + y0 - 5, "img": img})
    return out


def shape_groups(chars: list[dict]) -> list[list[dict]]:
    from PIL import Image
    feat = lambda c: np.array(Image.fromarray(c["img"] * 255).resize((24, 24), Image.BILINEAR), float) / 255
    rows = defaultdict(list)
    for c in chars:
        c["f"] = feat(c)
        rows[(c["page"], c["row"])].append(c)
    for v in rows.values():
        base = np.median([c["bot"] for c in v])
        for c in v:
            c["rb"] = c["bot"] - base
    groups: list[list[dict]] = []
    for c in chars:
        for g in groups:
            r = g[0]
            if abs(c["w"] - r["w"]) <= 4 and abs(c["h"] - r["h"]) <= 4 and abs(c["rb"] - r["rb"]) <= 5 and np.abs(c["f"] - r["f"]).mean() < 0.06:
                g.append(c)
                break
        else:
            groups.append([c])
    return sorted(groups, key=lambda g: -len(g))


def read(imgdir: str = "data/lp_images", out: str = "data/lp_derived/tokens_66_68.csv") -> list[str]:
    chars = [c for p in ROWS for c in components(p, imgdir)]
    groups = shape_groups(chars)
    if len(groups) != len(SHAPE_LABELS):
        raise SystemExit(f"{len(groups)} shape groups, expected {len(SHAPE_LABELS)}: labels no longer apply, relabel by eye")
    from PIL import Image
    big = lambda c: np.array(Image.fromarray(c["img"] * 255).resize((48, 48), Image.BILINEAR), float) / 255
    label: dict = {}
    for g, ch in zip(groups, SHAPE_LABELS):
        ref = big(g[0])
        for c in g:
            label[(c["page"], c["row"], c["col"])] = "Q" if ch == "O" and np.abs(big(c) - ref).mean() > Q_DIFF else ch
    rows = defaultdict(list)
    for k, v in sorted(label.items()):
        rows[(k[0], k[1])].append(v)
    toks, lines = [], [["index", "page", "row", "col", "token"]]
    for (p, r), v in sorted(rows.items()):
        s = "".join(v)
        assert len(s) == 16 and all(s[i] in "01234" for i in range(0, 16, 2)), (p, r, s)
        for c in range(8):
            lines.append([len(toks), p, r, c, s[2 * c:2 * c + 2]])
            toks.append(s[2 * c:2 * c + 2])
    with open(out, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(lines)
    return toks


def load(path: str = "data/lp_derived/tokens_66_68.csv") -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [r["token"] for r in csv.DictReader(f)]


def ic29(x) -> float:
    c = np.bincount(np.asarray(x), minlength=29)
    n = len(x)
    return float(29 * (c * (c - 1)).sum() / (n * (n - 1)))


def analyse(toks: list[str], table: str = "data/lp_derived/lp2_runes.csv", sims: int = 500, seed: int = 20261112) -> dict:
    v = np.array([token_value(t) for t in toks])
    n = len(v)
    rng = np.random.default_rng(seed)
    res = {"tokens": n, "min": int(v.min()), "max": int(v.max()), "distinct": int(len(set(toks))),
           "distinct_expected": float(M * (1 - (1 - 1 / M) ** n)), "first_char": {d: sum(t[0] == d for t in toks) for d in "01234"}}
    res["missing_second_chars"] = [c for c in A62 if c not in {t[1] for t in toks}]
    mx = lambda w: max(int((w[k:] == w[:-k]).sum()) for k in range(1, 129))
    obs = mx(v)
    null = np.array([mx(rng.integers(0, M, n)) for _ in range(sims)])
    res["equal_pairs_max_lag1_128"] = {"obs": obs, "null_mean": float(null.mean()), "p": float((1 + (null >= obs).sum()) / (sims + 1))}
    res["equal_pairs_lag1"] = int((v[1:] == v[:-1]).sum())
    try:
        rows = list(csv.DictReader(open(table, encoding="utf-8")))
    except OSError:
        return res
    byp = defaultdict(list)
    for r in sorted(rows, key=lambda r: int(r["global"])):
        byp[int(r["page"])].append(int(r["rune"]))

    def best_ic(w):
        best = (0.0, None)
        for p, rn in byp.items():
            rn = np.array(rn)
            for base in (0, 1):
                for rev in (False, True):
                    idx = w - base
                    ok = (idx >= 0) & (idx < len(rn))
                    if ok.mean() < 0.6:
                        continue
                    s = ic29((rn[::-1] if rev else rn)[idx[ok]])
                    if s > best[0]:
                        best = (s, (p, base, rev))
        return best
    obs_ic, where = best_ic(v)
    nulls = np.array([best_ic(rng.integers(0, M, n))[0] for _ in range(min(sims, 100))])
    res["pointer_reading"] = {"best_ic_x29": obs_ic, "page_base_reversed": where, "null_best_mean": float(nulls.mean()), "null_best_max": float(nulls.max()),
                              "p": float((1 + (nulls >= obs_ic).sum()) / (len(nulls) + 1))}
    return res


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_tokens", description=__doc__.split("\n")[0])
    ap.add_argument("mode", choices=["read", "analyse"])
    args = ap.parse_args(argv)
    if args.mode == "read":
        print(len(read()), "tokens written")
    else:
        import json
        print(json.dumps(analyse(load()), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Audit of the page-image reader: is the image-to-rune translation reliable?

    python -m lpswarm.reader_audit --out reports/diag [--pickle FILE]

No oracle, no models. Checks, each aimed at one way the reader could be wrong:

margins     for every glyph on every page: the stroke distance to the shape it was given (d1) and to the nearest shape of a
            DIFFERENT rune (d2). A reliable reading has d1 small and d2 large (the page type is drawn in one typeface: same rune
            <= 3 px, different runes >= 15 px). Flags glyphs with a large d1 or a small gap d2 - d1.
solved      agreement with the manifest on solved pages that were NOT used to label the shapes (labels come from pages 14-16 only,
            so agreement on those is circular and is shown separately).
scale       the reader is tuned to the page glyph size. Pages are rescaled and re-read: does a wrong size ever give a WRONG rune,
            or only unknown / missing glyphs? (the short-image failure mode).
strip       a small image read at many scales against a known answer (optional).
separators  the word dots and colon pairs read from the images against the word breaks of the scream314 text.
disputed    for every position where the image and the text differ, the distance from that glyph to the shape of each reading.
"""
from __future__ import annotations

import argparse
import json
import pickle
import tempfile
from collections import Counter
from pathlib import Path

import numpy as np

from lpswarm.pageimages import THRESH, bin_aligned, crop_mask, dilated, load_masks, read_page, stroke_dist
from lpswarm.research_doubles import align_sequences

UNSOLVED = [f"{n:02d}" for n in range(17, 73)]
LABEL_PAGES = ("14", "15", "16")                       # the shapes were labelled from these pages (sections 8 and 9)
# solved sections that map onto page files, and the pages that carry them
SOLVED_GROUPS = (("01", ["01"], [1]), ("05", ["05"], [3]), ("03-04", ["03", "04"], [4]), ("06-09", ["06", "07", "08", "09"], [5, 6]),
                 ("10-13", ["10", "11", "12", "13"], [7]), ("73", ["73"], [26]), ("74", ["74"], [27]))
FLAT_GAP = 15                                         # documented: different runes are at least this far apart
SAME_MAX = 3                                          # documented: the same rune is at most this far from its shape
SCALES = (0.8, 0.85, 0.9, 0.95, 1.05, 1.1, 1.15, 1.2)
SCALE_PAGES = ("17", "33", "58")


# ---------------------------------------------------------------------------------------------- margins
def flag_margins(d1: np.ndarray, d2: np.ndarray, same_max: int = SAME_MAX, flat_gap: int = FLAT_GAP) -> dict:
    d1, d2 = np.asarray(d1), np.asarray(d2)
    gap = d2 - d1
    return {"glyphs": int(len(d1)), "d1_max": int(d1.max()) if len(d1) else 0, "d1_median": float(np.median(d1)) if len(d1) else 0.0,
            "d2_min": int(d2.min()) if len(d2) else 0, "d2_median": float(np.median(d2)) if len(d2) else 0.0,
            "d1_above_same_max": int((d1 > same_max).sum()), "d2_below_flat_gap": int((d2 < flat_gap).sum()),
            "gap_below_threshold": int((gap < THRESH).sum()), "gap_min": int(gap.min()) if len(gap) else 0}


def glyph_distances(read: dict, img_dir, ext: str = ".jpg") -> list[dict]:
    """(page, line, index, rune, d1, d2, nearest other rune) for every glyph with a known shape."""
    frozen, lab = read["frozen"], read["lab"]
    rows = []
    for pg in sorted(read["reads"]):
        glyphs = sorted(read["reads"][pg]["glyphs"], key=lambda g: (g["line"], g["x0"]))
        black, red = load_masks(Path(img_dir) / f"{pg}{ext}")
        per_line = Counter()
        for g in glyphs:
            k = g["shape"]
            idx = per_line[g["line"]]
            per_line[g["line"]] += 1
            if k < 0 or g.get("unresolved") or g.get("drop_cap"):
                continue
            b = bin_aligned(crop_mask(black, red, g))
            db = dilated(b)
            w = g["x1"] - g["x0"]
            d1, d2, other = None, 10 ** 9, None
            for j, (rep, dil) in enumerate(zip(frozen.reps, frozen.dil)):
                if abs(frozen.width[j] - w) > 6:
                    continue
                d = stroke_dist(b, rep, db, dil)
                if j == k:
                    d1 = d
                elif lab.get(j) != lab.get(k) and d < d2:
                    d2, other = d, lab.get(j)
            if d1 is None:
                d1 = stroke_dist(b, frozen.reps[k], db, frozen.dil[k])
            rows.append({"page": pg, "line": g["line"] + 1, "index": idx, "rune": lab.get(k), "d1": d1, "d2": d2, "other": other})
    return rows


# ------------------------------------------------------------------------------------------ agreement
def diff_counts(test, base) -> dict:
    """How a re-read differs from a base reading, by an exact edit-distance alignment (substitution, insertion and deletion each
    cost 1). wrong = a rune read as a different rune, unknown = read as no known shape (-1), structural = glyphs added or lost."""
    a, b = np.asarray(test, dtype=np.int64), np.asarray(base, dtype=np.int64)
    n, m = len(a), len(b)
    D = np.zeros((n + 1, m + 1), dtype=np.int32)
    D[:, 0] = np.arange(n + 1)
    D[0, :] = np.arange(m + 1)
    for i in range(1, n + 1):
        sub = D[i - 1, :-1] + (a[i - 1] != b)
        row = np.minimum(sub, D[i - 1, 1:] + 1)                  # substitution or "glyph only in test"
        for j in range(1, m + 1):                                 # "rune only in base" depends on the same row
            v = D[i, j - 1] + 1
            D[i, j] = row[j - 1] if row[j - 1] <= v else v
    out = {"matched": 0, "wrong": 0, "unknown": 0, "structural": 0}
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and D[i, j] == D[i - 1, j - 1] + (a[i - 1] != b[j - 1]):
            if a[i - 1] == b[j - 1]:
                out["matched"] += 1
            else:
                out["unknown" if a[i - 1] < 0 else "wrong"] += 1
            i, j = i - 1, j - 1
        elif i > 0 and D[i, j] == D[i - 1, j] + 1:
            out["structural"] += 1
            i -= 1
        else:
            out["structural"] += 1
            j -= 1
    return out


def page_runes(read: dict, pg: str) -> list[int]:
    lab = read["lab"]
    gl = sorted(read["reads"][pg]["glyphs"], key=lambda g: (g["line"], g["x0"]))
    return [int(lab.get(g["shape"], -1)) if g["shape"] >= 0 and not g.get("unresolved") else -1 for g in gl]


def solved_agreement(read: dict, secs: dict) -> list[dict]:
    rows = []
    groups = list(SOLVED_GROUPS) + [("14-16 (labelling pages: circular)", list(LABEL_PAGES), [8, 9])]
    for name, pages, sections in groups:
        img = [r for p in pages if p in read["reads"] for r in page_runes(read, p)]
        text = [int(v) for i in sections if i in secs for v in secs[i]["ct"]]
        if not img or not text:
            continue
        al = align_sequences(img, text)
        owner = [p for p in pages if p in read["reads"] for _ in page_runes(read, p)]
        only = Counter(owner[i] for i in np.nonzero(al["sa"] == 2)[0])
        rows.append({"image_only_by_page": {p: c for p, c in only.items() if c >= 5}, "group": name, "image_glyphs": len(img), "text_runes": len(text), "matched": int((al["sa"] == 0).sum()),
                     "substituted": int((al["sa"] == 1).sum()), "image_only": int((al["sa"] == 2).sum()),
                     "text_only": int((al["sb"] == 2).sum()), "unknown_image_glyphs": int(sum(1 for v in img if v < 0)),
                     "agreement_text": float((al["sb"] == 0).mean())})
    return rows


# ------------------------------------------------------------------------------------------------ scale
def scale_robustness(read: dict, img_dir, pages=SCALE_PAGES, scales=SCALES) -> list[dict]:
    from PIL import Image
    frozen = read["frozen"]
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for pg in pages:
            base = page_runes(read, pg)
            im = Image.open(Path(img_dir) / f"{pg}.jpg").convert("RGB")
            for s in scales:
                big = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
                path = Path(tmp) / f"{pg}_{s}.png"
                big.save(path)
                try:
                    r = read_page(path, frozen, learn=False)
                except Exception as exc:                          # a failed read is a result, not an error
                    rows.append({"page": pg, "scale": s, "error": f"{type(exc).__name__}: {exc}"[:90]})
                    continue
                lab = read["lab"]
                gl = sorted(r["glyphs"], key=lambda g: (g["line"], g["x0"]))
                test = [int(lab.get(g["shape"], -1)) if g["shape"] >= 0 and not g.get("unresolved") else -1 for g in gl]
                rows.append({"page": pg, "scale": s, "glyphs": len(test), "base_glyphs": len(base), **diff_counts(test, base)})
    return rows


def read_strip(path, read: dict, scale: float, tokens: list[str]) -> list[str]:
    """Read a small image of one line of runes at a given scale (the reader's glyph-size window is about 100-130 px)."""
    from PIL import Image
    from scipy import ndimage as ndi
    im = Image.open(path).convert("L")
    big = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
    mask = np.asarray(big) < 128
    labeled, _ = ndi.label(mask, structure=np.ones((3, 3)))
    boxes = sorted((s[1].start, s[1].stop, s[0].start, s[0].stop) for s in ndi.find_objects(labeled))
    merged = []
    for b in boxes:
        if merged and b[0] < merged[-1][1] - 1:
            m = merged[-1]
            merged[-1] = (m[0], max(m[1], b[1]), min(m[2], b[2]), max(m[3], b[3]))
        else:
            merged.append(b)
    frozen, lab = read["frozen"], read["lab"]
    out = []
    for x0, x1, y0, y1 in merged:
        if y1 - y0 < 30:
            continue
        d, k = frozen.match(bin_aligned(mask[y0:y1, x0:x1]), x1 - x0)
        out.append(tokens[lab[k]] if d <= THRESH and k in lab else "?")
    return out


def strip_scales(path, read: dict, truth: list[str], tokens: list[str], scales=None) -> list[dict]:
    rows = []
    for s in (scales or [round(1.4 + 0.1 * i, 2) for i in range(14)]):
        got = read_strip(path, read, s, tokens)
        # digits are not runes: compare only the rune positions of the truth (digits appear as '?')
        same_len = len(got) == len(truth)
        rows.append({"scale": s, "pieces": len(got), "unknown": got.count("?") - truth.count("?"),
                     "wrong": sum(1 for a, b in zip(got, truth) if a != "?" and b != "?" and a != b) if same_len else None,
                     "exact": got == truth, "reading": " ".join(got)})
    return rows


# ------------------------------------------------------------------------------------------ separators
def separator_confusion(pairs: list[tuple[bool, str]]) -> dict:
    """pairs: (text has a word break here, image separator kind) for consecutive glyphs on the same line."""
    c = Counter((t, sep) for t, sep in pairs)
    word_like = ("word", "colon")
    both = sum(v for (t, s), v in c.items() if t and s in word_like)
    only_text = sum(v for (t, s), v in c.items() if t and s not in word_like)
    only_image = sum(v for (t, s), v in c.items() if not t and s in word_like)
    neither = sum(v for (t, s), v in c.items() if not t and s not in word_like)
    n = both + only_text + only_image + neither
    return {"pairs": n, "both_break": both, "text_only": only_text, "image_only": only_image, "neither": neither,
            "agreement": (both + neither) / n if n else None, "by_kind": {f"{'break' if t else 'no break'} / {s}": v for (t, s), v in c.items()}}


def separators(read: dict, secs: dict, ids) -> dict:
    img_pages = [p for p in UNSOLVED if p in read["reads"]]
    glyphs = []
    for p in img_pages:
        glyphs += [(p, g) for g in sorted(read["reads"][p]["glyphs"], key=lambda g: (g["line"], g["x0"]))]
    lab = read["lab"]
    img = [int(lab.get(g["shape"], -1)) if g["shape"] >= 0 and not g.get("unresolved") else -1 for _p, g in glyphs]
    ids = [i for i in ids if i in secs]
    text = [int(v) for i in ids for v in secs[i]["ct"]]
    starts = set()
    off = 0
    for i in ids:
        starts |= {off + int(b) for b in secs[i]["breaks"]}
        off += len(secs[i]["ct"])
    al = align_sequences(img, text)
    pairs = []
    for a in range(len(glyphs) - 1):
        ga, gb = glyphs[a][1], glyphs[a + 1][1]
        j, j2 = al["a2b"][a], al["a2b"][a + 1]
        if ga["line"] != gb["line"] or glyphs[a][0] != glyphs[a + 1][0] or j < 0 or j2 != j + 1 or al["sa"][a] or al["sa"][a + 1]:
            continue
        pairs.append(((j + 1) in starts, ga.get("sep", "none")))
    return separator_confusion(pairs)


# --------------------------------------------------------------------------------------------- disputed
def disputed(read: dict, secs: dict, img_dir, ids, tokens: list[str]) -> list[dict]:
    pages = [p for p in UNSOLVED if p in read["reads"]]
    glyphs = []
    for p in pages:
        glyphs += [(p, g) for g in sorted(read["reads"][p]["glyphs"], key=lambda g: (g["line"], g["x0"]))]
    lab, frozen = read["lab"], read["frozen"]
    img = [int(lab.get(g["shape"], -1)) if g["shape"] >= 0 and not g.get("unresolved") else -1 for _p, g in glyphs]
    ids = [i for i in ids if i in secs]
    text = [int(v) for i in ids for v in secs[i]["ct"]]
    al = align_sequences(img, text)
    out = []
    for a in np.nonzero(al["sa"] == 1)[0]:
        p, g = glyphs[a]
        black, red = load_masks(Path(img_dir) / f"{p}.jpg")
        b = bin_aligned(crop_mask(black, red, g))
        want = text[al["a2b"][a]]
        w = g["x1"] - g["x0"]
        dist = {}
        for j in range(len(frozen.reps)):
            if abs(frozen.width[j] - w) <= 6 and lab.get(j) is not None:
                d = stroke_dist(b, frozen.reps[j], None, frozen.dil[j])
                r = lab[j]
                dist[r] = min(dist.get(r, 10 ** 9), d)
        out.append({"page": p, "line": g["line"] + 1, "image_rune": tokens[img[a]], "text_rune": tokens[want],
                    "distance_to_image_reading": dist.get(img[a]), "distance_to_text_reading": dist.get(want),
                    "nearest_three": [(tokens[r], d) for r, d in sorted(dist.items(), key=lambda kv: kv[1])[:3]]})
    return out


# ---------------------------------------------------------------------------------------------- report
def audit(read: dict, secs: dict, img_dir, tokens: list[str], strip_path=None, truth=None) -> dict:
    rows = glyph_distances(read, img_dir)
    d1 = np.array([r["d1"] for r in rows]), np.array([r["d2"] for r in rows])
    unsolved_rows = [r for r in rows if r["page"] in UNSOLVED]
    rep = {"margins_all": flag_margins(*d1),
           "margins_unsolved": flag_margins(np.array([r["d1"] for r in unsolved_rows]), np.array([r["d2"] for r in unsolved_rows])),
           "weakest": sorted(({**r, "gap": r["d2"] - r["d1"], "rune": tokens[r["rune"]], "other": tokens[r["other"]] if r["other"] is not None else None}
                              for r in rows), key=lambda r: r["gap"])[:25],
           "solved": solved_agreement(read, secs), "scale": scale_robustness(read, img_dir),
           "separators": separators(read, secs, range(10, 26)), "disputed": disputed(read, secs, img_dir, range(10, 26), tokens)}
    if strip_path and truth and Path(strip_path).exists():
        rep["strip"] = strip_scales(strip_path, read, truth, tokens)
    return rep


def markdown(rep: dict) -> str:
    m, mu = rep["margins_all"], rep["margins_unsolved"]
    L = ["# Image reader audit", "", "**EXPLORATORY audit; no oracle, no models.** Documented separation of the typeface: same rune <= "
         f"{SAME_MAX} px from its shape, different runes >= {FLAT_GAP} px apart.", "",
         "## 1. Match margins (every glyph with a known shape)", "",
         "| set | glyphs | d1 median / max | d2 median / min | d1 > 3 | d2 < 15 | gap (d2 - d1) < 8 | smallest gap |", "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |"]
    for name, x in (("all pages", m), ("unsolved pages 17-72", mu)):
        L.append(f"| {name} | {x['glyphs']} | {x['d1_median']:.0f} / {x['d1_max']} | {x['d2_median']:.0f} / {x['d2_min']} | "
                 f"{x['d1_above_same_max']} | {x['d2_below_flat_gap']} | {x['gap_below_threshold']} | {x['gap_min']} |")
    L += ["", "Weakest margins (smallest gap between the given shape and the nearest other rune):", "",
          "| page | line | index | read as | nearest other | d1 | d2 | gap |", "| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |"]
    for r in rep["weakest"][:12]:
        L.append(f"| {r['page']} | {r['line']} | {r['index']} | {r['rune']} | {r['other']} | {r['d1']} | {r['d2']} | {r['gap']} |")
    L += ["", "## 2. Agreement with the manifest on solved pages", "",
          "The shapes were labelled from pages 14-16, so those rows are circular; the others are independent.", "",
          "| pages | image glyphs | text runes | matched | substituted | image only | text only | unknown glyphs | agreement (of text) |",
          "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rep["solved"]:
        L.append(f"| {r['group']} | {r['image_glyphs']} | {r['text_runes']} | {r['matched']} | {r['substituted']} | {r['image_only']} | "
                 f"{r['text_only']} | {r['unknown_image_glyphs']} | {100 * r['agreement_text']:.2f}% |")
    notes = [f"{r['group']}: {', '.join(f'page {p} {c}' for p, c in r['image_only_by_page'].items())} image glyphs with no text" for r in rep["solved"] if r["image_only_by_page"]]
    if notes:
        L += ["", "Image glyphs the manifest text does not have (5 or more on a page): " + "; ".join(notes) + "."]
    L += ["", "## 3. Wrong glyph size: wrong runes, or only unknown ones?", "",
          "Pages rescaled and re-read with the same shapes, against the normal reading of the same page. `wrong` = a rune read as a different "
          "rune; `unknown` = read as no known shape; `structural` = glyphs lost or added.", "",
          "| page | scale | glyphs | matched | wrong | unknown | structural |", "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for r in rep["scale"]:
        if "error" in r:
            L.append(f"| {r['page']} | {r['scale']} | error: {r['error']} | | | | |")
        else:
            L.append(f"| {r['page']} | {r['scale']} | {r['glyphs']} | {r['matched']} | {r['wrong']} | {r['unknown']} | {r['structural']} |")
    wrong = sum(r.get("wrong", 0) for r in rep["scale"])
    L += ["", f"Wrong runes across all rescaled reads: {wrong}.", ""]
    if "strip" in rep:
        L += ["## 4. The short image at many scales (known answer)", "", "| scale | pieces | unknown | wrong | exact |", "| ---: | ---: | ---: | ---: | --- |"]
        for r in rep["strip"]:
            L.append(f"| {r['scale']} | {r['pieces']} | {r['unknown']} | {r['wrong']} | {'yes' if r['exact'] else 'no'} |")
        L.append("")
    s = rep["separators"]
    L += ["## 5. Separators against the text's word breaks", "",
          f"Consecutive glyphs on one line, both aligned: {s['pairs']}. Both mark a break {s['both_break']}, text only {s['text_only']}, "
          f"image only {s['image_only']}, neither {s['neither']}; agreement {100 * s['agreement']:.2f}%.", ""]
    L += ["## 6. Positions where the image and the text differ", ""]
    if rep["disputed"]:
        L += ["| page | line | image reads | text has | distance to image reading | distance to text reading | nearest three |", "| --- | ---: | --- | --- | ---: | ---: | --- |"]
        for r in rep["disputed"]:
            L.append(f"| {r['page']} | {r['line']} | {r['image_rune']} | {r['text_rune']} | {r['distance_to_image_reading']} | "
                     f"{r['distance_to_text_reading']} | {', '.join(f'{a} {d}' for a, d in r['nearest_three'])} |")
    else:
        L.append("None.")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.pageimages import read_all
    from lpswarm.research_packets import ALPHABET, load_sections
    ap = argparse.ArgumentParser(prog="python -m lpswarm.reader_audit", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="reports/diag")
    ap.add_argument("--dir", default="data/lp_images")
    ap.add_argument("--pickle", default=None, help="cached read_all(keep=True) result (not committed)")
    ap.add_argument("--strip", default=None, help="optional small image of one line of runes")
    ap.add_argument("--strip-truth", default=None, help="the strip's runes as tokens, '?' for non-runes")
    args = ap.parse_args(argv)
    tokens = list(get_alphabet(ALPHABET).tokens)
    read = pickle.load(open(args.pickle, "rb")) if args.pickle and Path(args.pickle).exists() else read_all(args.dir, keep=True)
    secs = load_sections(indexes=sorted({i for _n, _p, s in SOLVED_GROUPS for i in s} | {8, 9} | set(range(10, 26))))
    rep = audit(read, secs, args.dir, tokens, args.strip, args.strip_truth.split() if args.strip_truth else None)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "reader_audit.json").write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    text = markdown(rep)
    (out / "reader_audit.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

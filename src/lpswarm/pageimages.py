"""Read the rune glyphs, colours and punctuation marks out of the Liber Primus page images.

The pages are drawn in one computer typeface, so the same rune is near pixel-identical wherever it appears
(stroke distance <= 3 px) and different runes are far apart (>= 15 px). That makes a transcription a matter of
cutting glyphs and grouping identical shapes, with no trained model. The images are never committed.

    python -m lpswarm.pageimages fetch                 # partial git clone of iBotPeaches/cicada_3301 -> data/lp_images
    python -m lpswarm.pageimages headings --out reports/diag

What it records that the text transcriptions lose: line breaks, which runes are red (headings and closing lines),
the large red drop cap, the dotted red square that ends a red passage, and the separator after each glyph (word dot
or colon-like pair).

Needs Pillow and scipy (optional extra `images`); the rest of the package needs only numpy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

import numpy as np

REPO_URL = "https://github.com/iBotPeaches/cicada_3301"
IMG_DIR = Path("data/lp_images")
SHA_FILE = Path("data/lp_images.sha256")
GLYPH_H = (100, 130)        # height of a text glyph in the 2400x3600 images
NARROW_MAX = 56             # widest single narrow glyph; wider boxes are a wide rune or two touching glyphs
THRESH = 8                  # stroke distance at which two glyphs are the same rune (same <= 3, different >= 15)
CANVAS = 132


def _need():
    try:
        from PIL import Image  # noqa: F401
        from scipy import ndimage  # noqa: F401
    except ImportError as exc:                           # pragma: no cover
        raise SystemExit("pageimages needs Pillow and scipy: pip install pillow scipy") from exc


# ------------------------------------------------------------------------------------------ fetch
def fetch(dest: str | Path = IMG_DIR, repo: str = REPO_URL, run=subprocess.run, sha_file: Path = SHA_FILE) -> int:
    """Partial clone of the repo and copy of liber_primus/NN.jpg into `dest`. Returns the number of images."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "repo"
        run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none", "--no-checkout", repo, str(clone)], check=True)
        run(["git", "-C", str(clone), "checkout", "HEAD", "--", "liber_primus"], check=True)
        files = sorted((clone / "liber_primus").glob("[0-9][0-9].jpg"))
        for f in files:
            shutil.copy2(f, dest / f.name)
    sums = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.glob("*.jpg"))}
    sha_file.parent.mkdir(parents=True, exist_ok=True)
    sha_file.write_text("".join(f"{h}  {n}\n" for n, h in sums.items()), encoding="utf-8")
    return len(sums)


# ------------------------------------------------------------------------------------ segmentation
def load_masks(path) -> tuple[np.ndarray, np.ndarray]:
    _need()
    from PIL import Image
    im = np.asarray(Image.open(path).convert("RGB")).astype(int)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    return (R < 110) & (G < 110) & (B < 110), (R > 140) & (G < 90) & (B < 90)


def components(black: np.ndarray, red: np.ndarray, margin: int = 120) -> list[dict]:
    from scipy import ndimage as ndi
    H, W = black.shape
    ink = (black | red)
    box = (margin, W - margin, margin, H - margin)
    lab, _n = ndi.label(ink[box[2]:box[3], box[0]:box[1]], structure=np.ones((3, 3)))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        m = lab[sl] == i
        a = int(m.sum())
        if a < 6:
            continue
        isred = bool(red[box[2]:box[3], box[0]:box[1]][sl][m].mean() > 0.5)
        out.append({"x": sl[1].start + box[0], "y": sl[0].start + box[2], "w": sl[1].stop - sl[1].start,
                    "h": sl[0].stop - sl[0].start, "area": a, "red": isred})
    return out


def find_lines(comps: list[dict]) -> list[dict]:
    """Text lines from the glyph-height components that line up; each line carries its y centre and x extent."""
    full = [c for c in comps if GLYPH_H[0] <= c["h"] <= GLYPH_H[1] and c["area"] >= 400 and c["w"] <= 125]
    if not full:
        return []
    ys = sorted(full, key=lambda c: c["y"] + c["h"] / 2)
    groups, cur = [], [ys[0]]
    for c in ys[1:]:
        if (c["y"] + c["h"] / 2) - (cur[-1]["y"] + cur[-1]["h"] / 2) > 60:
            groups.append(cur)
            cur = [c]
        else:
            cur.append(c)
    groups.append(cur)
    return [{"yc": float(np.mean([c["y"] + c["h"] / 2 for c in g])), "x0": min(c["x"] for c in g),
             "x1": max(c["x"] + c["w"] for c in g), "n": len(g)} for g in groups if len(g) >= 3]


def build_glyph_boxes(comps: list[dict], lines: list[dict]) -> dict:
    """Assign components to lines, merge the parts of one glyph, separate dots, hatch dots and drop caps."""
    drop = [c for c in comps if c["red"] and c["h"] > 200 and c["w"] < 300]
    inside = []
    for c in comps:
        if c in drop or c["h"] > 200:
            continue
        yc = c["y"] + c["h"] / 2
        j = int(np.argmin([abs(yc - l["yc"]) for l in lines])) if lines else None
        if j is None or abs(yc - lines[j]["yc"]) > 75 or c["x"] < lines[j]["x0"] - 40 or c["x"] > lines[j]["x1"] + 40:
            continue
        c["line"] = j
        inside.append(c)
    parts = [c for c in inside if c["h"] >= 30 or c["area"] >= 150]
    smalls = [c for c in inside if not (c["h"] >= 30 or c["area"] >= 150)]
    boxes = []
    for j in range(len(lines)):
        merged = []
        for c in sorted([p for p in parts if p["line"] == j], key=lambda p: p["x"]):
            if merged and c["x"] < merged[-1]["x1"] - 0.3 * min(c["w"], merged[-1]["x1"] - merged[-1]["x0"]):
                m = merged[-1]
                m["x1"] = max(m["x1"], c["x"] + c["w"])
                m["x0"] = min(m["x0"], c["x"])
                m["y0"] = min(m["y0"], c["y"])
                m["y1"] = max(m["y1"], c["y"] + c["h"])
                m["red"] = m["red"] or c["red"]
            else:
                merged.append({"x0": c["x"], "x1": c["x"] + c["w"], "y0": c["y"], "y1": c["y"] + c["h"],
                               "red": c["red"], "line": j})
        boxes += merged
    return {"boxes": boxes, "smalls": smalls, "drop": drop}


def crop_mask(black, red, b) -> np.ndarray:
    return (black | red)[b["y0"]:b["y1"], b["x0"]:b["x1"]]


def bin_aligned(mask: np.ndarray) -> np.ndarray:
    ys, xs = np.nonzero(mask)
    c = np.zeros((CANVAS, CANVAS), bool)
    if not len(ys):
        return c
    oy, ox = int(round(CANVAS / 2 - ys.mean())), int(round(CANVAS / 2 - xs.mean()))
    yy, xx = ys + oy, xs + ox
    ok = (yy >= 0) & (yy < CANVAS) & (xx >= 0) & (xx < CANVAS)
    c[yy[ok], xx[ok]] = True
    return c


_STRUCT = None


def dilated(a: np.ndarray, r: int = 3) -> np.ndarray:
    from scipy import ndimage as ndi
    return ndi.binary_dilation(a, np.ones((2 * r + 1, 2 * r + 1), bool))


def stroke_dist(a: np.ndarray, b: np.ndarray, da: np.ndarray | None = None, db: np.ndarray | None = None) -> int:
    """Pixels of one glyph further than 3 px from any pixel of the other (the larger of the two directions)."""
    da = dilated(a) if da is None else da
    db = dilated(b) if db is None else db
    return int(max((a & ~db).sum(), (b & ~da).sum()))


class Shapes:
    """Growing set of glyph shapes (clusters) with cached dilations."""

    def __init__(self, thr: int = THRESH):
        self.thr, self.reps, self.dil, self.width, self.count = thr, [], [], [], []
        self.pending: list[tuple[np.ndarray, int]] = []        # wide boxes that did not split (learning pass)

    def finish_learning(self, min_count: int = 3) -> int:
        """Cluster the pending wide boxes; clusters seen at least `min_count` times become wide runes."""
        groups: list[list[tuple[np.ndarray, int]]] = []
        for b, w in self.pending:
            for g in groups:
                if abs(g[0][1] - w) <= 6 and stroke_dist(b, g[0][0]) <= self.thr:
                    g.append((b, w))
                    break
            else:
                groups.append([(b, w)])
        added = 0
        for g in groups:
            if len(g) >= min_count:
                k = self.add(g[0][0], g[0][1])
                self.count[k] = len(g)
                added += 1
        self.pending = []
        return added

    def match(self, b: np.ndarray, width: int | None = None) -> tuple[int, int]:
        db = dilated(b)
        best = (10 ** 9, -1)
        for k, (r, dr) in enumerate(zip(self.reps, self.dil)):
            if width is not None and abs(self.width[k] - width) > 6:
                continue
            d = stroke_dist(b, r, db, dr)
            if d < best[0]:
                best = (d, k)
        return best

    def add(self, b: np.ndarray, width: int) -> int:
        self.reps.append(b)
        self.dil.append(dilated(b))
        self.width.append(width)
        self.count.append(0)
        return len(self.reps) - 1

    def classify(self, b: np.ndarray, width: int, create: bool = True) -> int:
        d, k = self.match(b, width)
        if d <= self.thr:
            self.count[k] += 1
            return k
        if not create:
            return -1
        k = self.add(b, width)
        self.count[k] += 1
        return k


def freeze(shapes: Shapes, keep) -> tuple[Shapes, dict[int, int]]:
    """A new Shapes holding only the shapes in `keep` (old id -> new id returned)."""
    out, remap = Shapes(shapes.thr), {}
    for k in sorted(keep):
        remap[k] = out.add(shapes.reps[k], shapes.width[k])
        out.count[remap[k]] = shapes.count[k]
    return out, remap


def split_touching(mask: np.ndarray, shapes: Shapes, depth: int = 0) -> list[tuple[int, int]] | None:
    """Split a box holding touching glyphs into column spans whose halves both match known shapes."""
    h, w = mask.shape
    col = mask.sum(axis=0)
    cands = sorted(range(8, w - 8), key=lambda c: col[max(c - 1, 0):c + 2].sum())[:12]
    best = None
    for c in cands:
        left, right = mask[:, :c], mask[:, c:]
        if not left.any() or not right.any():
            continue
        dl, kl = shapes.match(bin_aligned(left), c)
        dr, kr = shapes.match(bin_aligned(right), w - c)
        if dl <= THRESH and dr <= THRESH:
            if best is None or dl + dr < best[0]:
                best = (dl + dr, c)
    if best:
        return [(0, best[1]), (best[1], w)]
    if depth == 0:                                       # three touching glyphs: split off one known glyph first
        for c in cands:
            left = mask[:, :c]
            if left.any() and shapes.match(bin_aligned(left), c)[0] <= THRESH:
                rest = split_touching(mask[:, c:], shapes, 1)
                if rest:
                    return [(0, c)] + [(a + c, b + c) for a, b in rest]
    return None


def read_page(path, shapes: Shapes, learn: bool = True) -> dict:
    """Glyph sequence of one page in reading order with colours, separators, drop caps and terminators.
    learn=True grows the shape set (first pass); learn=False only recognises known shapes (shape -1 = unknown)."""
    black, red = load_masks(path)
    comps = components(black, red)
    lines = find_lines(comps)
    built = build_glyph_boxes(comps, lines)
    boxes = [b for b in built["boxes"] if GLYPH_H[0] <= b["y1"] - b["y0"] <= GLYPH_H[1] + 40]
    glyphs, unresolved = [], []
    narrow = [b for b in boxes if b["x1"] - b["x0"] <= NARROW_MAX]
    wide = [b for b in boxes if b["x1"] - b["x0"] > NARROW_MAX]
    for b in narrow:
        m = crop_mask(black, red, b)
        k = shapes.classify(bin_aligned(m), b["x1"] - b["x0"], create=learn)
        if k < 0 and not learn:                             # an unknown narrow box is usually two touching glyphs
            spans = split_touching(m, shapes)
            if spans:
                for a, c in spans:
                    sb = dict(b, x0=b["x0"] + a, x1=b["x0"] + c)
                    glyphs.append({**sb, "shape": shapes.classify(bin_aligned(crop_mask(black, red, sb)), c - a, create=False)})
                continue
        glyphs.append({**b, "shape": k})
    for b in wide:                                      # a wide rune (known shape) or two touching glyphs
        m = crop_mask(black, red, b)
        d, k = shapes.match(bin_aligned(m), b["x1"] - b["x0"])
        if d <= THRESH and (shapes.count[k] >= 3 or not learn):
            shapes.count[k] += 1
            glyphs.append({**b, "shape": k})
            continue
        spans = split_touching(m, shapes)
        if spans:
            for a, c in spans:
                sb = dict(b, x0=b["x0"] + a, x1=b["x0"] + c)
                glyphs.append({**sb, "shape": shapes.classify(bin_aligned(crop_mask(black, red, sb)), c - a, create=False)})
        else:
            unresolved.append(b)
            if learn:
                shapes.pending.append((bin_aligned(m), b["x1"] - b["x0"]))
            glyphs.append({**b, "shape": -1, "unresolved": True})
    glyphs.sort(key=lambda g: (g["line"], g["x0"]))
    # drop caps join the first line of their paragraph
    for dcap in built["drop"]:
        top = dcap["y"]
        j = int(np.argmin([abs((l["yc"] - 57) - top) for l in lines]))
        m = (black | red)[dcap["y"]:dcap["y"] + dcap["h"], dcap["x"]:dcap["x"] + dcap["w"]]
        from PIL import Image
        scale = 115 / m.shape[0]
        sm = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).resize(
            (max(int(round(m.shape[1] * scale)), 1), 115), Image.BILINEAR)) > 127
        k = shapes.classify(bin_aligned(sm), sm.shape[1], create=False)
        glyphs.append({"x0": dcap["x"], "x1": dcap["x"] + dcap["w"], "y0": dcap["y"], "y1": dcap["y"] + dcap["h"],
                       "red": True, "line": j, "shape": k, "drop_cap": True})
    glyphs.sort(key=lambda g: (g["line"], g["x0"]))
    # separators after each glyph: dots between glyphs, and dotted red squares (terminators)
    hatch = [c for c in built["smalls"] if c["red"] and c["h"] <= 14 and 30 <= c["area"] <= 120]
    hatches = defaultdict(list)
    for c in sorted(hatch, key=lambda c: c["x"]):
        groups = hatches[c["line"]]
        if groups and c["x"] - groups[-1][-1]["x"] < 40:
            groups[-1].append(c)
        else:
            groups.append([c])
    terminators = [(j, g[0]["x"]) for j, gs in hatches.items() for g in gs if len(g) >= 8]
    dots = [c for c in built["smalls"] if not (c["red"] and c["h"] <= 14 and 30 <= c["area"] <= 120)]
    for g in glyphs:
        g["sep"] = "none"
    by_line = defaultdict(list)
    for g in glyphs:
        by_line[g["line"]].append(g)
    for j, gs in by_line.items():
        gs.sort(key=lambda g: g["x0"])
        for a, b in zip(gs, gs[1:]):
            n = sum(1 for d in dots if d["line"] == j and a["x1"] - 2 <= d["x"] <= b["x0"] + 2)
            a["sep"] = "word" if n == 1 else ("colon" if n >= 2 else "none")
        for (tj, tx) in terminators:
            if tj != j:
                continue
            prev = [g for g in gs if g["x1"] <= tx + 12]
            if prev:
                prev[-1]["terminator"] = True
    return {"path": str(path), "lines": len(lines), "glyphs": glyphs, "unresolved": len(unresolved),
            "drop_caps": len(built["drop"]), "terminators": len(terminators)}


# --------------------------------------------------------------------------------- labelling and headings
def runs_of_red(glyphs: list[dict]) -> list[dict]:
    """Consecutive red glyphs in reading order, each with its terminator flag."""
    out, cur = [], []
    for i, g in enumerate(glyphs):
        if g["red"]:
            cur.append(i)
            if g.get("terminator"):
                out.append(cur)
                cur = []
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return [{"first": r[0], "last": r[-1], "length": len(r), "terminated": bool(glyphs[r[-1]].get("terminator"))}
            for r in out]


def infer_labels(pairs: list[tuple[list[int], list[int]]]) -> dict[int, int]:
    """shape id -> rune index, by majority over (shape sequence, rune sequence) pairs of equal length."""
    votes: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for shapes_seq, runes in pairs:
        if len(shapes_seq) != len(runes):
            continue
        for s, r in zip(shapes_seq, runes):
            if s >= 0:
                votes[s][int(r)] += 1
    return {s: max(v.items(), key=lambda kv: kv[1])[0] for s, v in votes.items()}


# ---------------------------------------------------------------------------------------- crib test
N = 29
# Titles that open passages on the solved pages (decoded from the red runs of the plain-substitution pages 05,
# 10-13, 16 and 74, and from the cipher pages' known plaintext). K and V are written C and U in the alphabet.
TITLES = ["AN INSTRUCTION", "SOME WISDOM", "KNOW THIS", "A WARNING", "AN END", "A KOAN", "PARABLE",
          "THE LOSS OF DIVINITY", "CONSUMPTION", "PRESERVATION", "ADHERENCE", "WELCOME"]
SEQUENCES = ("primes", "fibonacci", "naturals", "squares", "triangular", "pi_digits", "e_digits")
CRIB_OFFSETS = 20000


def implied_keys(c: np.ndarray, p: np.ndarray) -> dict[str, np.ndarray]:
    """Key vectors that would turn plaintext p into ciphertext c under the four sign/orientation conventions."""
    r = (N - 1 - c) % N
    return {"c-p": (c - p) % N, "p-c": (p - c) % N, "(28-c)-p": (r - p) % N, "p-(28-c)": (p - r) % N}


def sequence_matches(k: np.ndarray, offsets: int = CRIB_OFFSETS, sequences=SEQUENCES) -> list[tuple[str, int, int]]:
    """(sequence, scale, offset) such that k equals scale * sequence[offset:] up to a constant (first differences
    match). A window of L terms matches by chance with probability about 29^-(L-1) per candidate."""
    from lpswarm.programs.sequences import window
    dk = (k[1:] - k[:-1]) % N
    out = []
    for name in sequences:
        S = window(name, 0, offsets + len(k) + 2, N).astype(np.int64)
        dS = (S[1:] - S[:-1]) % N
        for a in range(1, N):
            adS = (a * dS) % N
            for o in np.nonzero(adS[:offsets] == dk[0])[0]:
                if np.array_equal(adS[o:o + len(dk)], dk):
                    out.append((name, a, int(o)))
    return out


def short_period(k: np.ndarray) -> list[int]:
    """Periods m <= L/2 with k[t] == k[t+m] throughout (1 = a constant key)."""
    return [m for m in range(1, len(k) // 2 + 1) if np.array_equal(k[m:], k[:-m])]


def crib_scan(headings: list[dict], alphabet, titles=TITLES, min_len: int = 6, seed: int = 1,
              null_per_test: int = 3, offsets: int = CRIB_OFFSETS) -> dict:
    """Try every title of the same length as each heading; report implied keys that are a sequence window or a short
    repeating key, and the same test on random plaintext as the false-match baseline."""
    plain = {t: np.array([int(v) for v in alphabet.encode(t.replace("K", "C").replace("V", "U"))], dtype=np.int64)
             for t in titles}
    rng = np.random.default_rng(seed)
    hits, tested, null_tests, null_hits = [], 0, 0, 0
    for h in headings:
        c = np.asarray(h["cipher"], dtype=np.int64)
        if len(c) < min_len:
            continue
        for title, p in plain.items():
            if len(p) != len(c):
                continue
            for conv, k in implied_keys(c, p).items():
                tested += 1
                seq, per = sequence_matches(k, offsets), short_period(k)
                if seq or per:
                    hits.append({"page": h["page"], "length": len(c), "title": title, "convention": conv,
                                 "sequence_matches": seq[:4], "repeat_periods": per})
                for _ in range(null_per_test):
                    q = rng.integers(0, N, size=len(c))
                    null_tests += 1
                    kk = implied_keys(c, q)[conv]
                    null_hits += bool(sequence_matches(kk, offsets) or short_period(kk))
    return {"tested": tested, "hits": hits, "null_tests": null_tests, "null_hits": null_hits}


# ------------------------------------------------------------------------------------------- headings
def read_all(img_dir, manifest: str = "data/lp/manifest.json") -> dict:
    """Learn the shapes on every page, label them from the two sections whose glyph count equals the manifest's
    (pages 14-15 = section 8, page 16 = section 9), freeze the labelled set and re-read every page."""
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET, load_sections
    pages = sorted(Path(img_dir).glob("[0-9][0-9].jpg"))
    if not pages:
        raise SystemExit(f"no page images in {img_dir}: run `python -m lpswarm.pageimages fetch` first")
    alpha = get_alphabet(ALPHABET)
    shapes = Shapes()
    for p in pages:
        read_page(p, shapes, learn=True)
    shapes.finish_learning()
    secs = load_sections(manifest=manifest, indexes=[8, 9])
    seeds = {"14": 8, "15": 8, "16": 9}
    by_page = {p.stem: read_page(p, shapes, learn=False) for p in pages if p.stem in seeds}
    seq8 = [g["shape"] for q in ("14", "15") for g in by_page[q]["glyphs"]]
    seq9 = [g["shape"] for g in by_page["16"]["glyphs"]]
    labels = infer_labels([(seq8, list(secs[8]["ct"])), (seq9, list(secs[9]["ct"]))])
    if len(set(labels.values())) != 29:
        raise SystemExit(f"labelling covers {len(set(labels.values()))} of 29 runes; the seed pages did not read cleanly")
    frozen, remap = freeze(shapes, labels.keys())
    lab = {remap[k]: v for k, v in labels.items()}
    pages_out = {}
    for p in pages:
        r = read_page(p, frozen, learn=False)
        gl = sorted(r["glyphs"], key=lambda g: (g["line"], g["x0"]))
        runs = []
        for run in runs_of_red(gl):
            cipher = [lab.get(gl[i]["shape"], -1) for i in range(run["first"], run["last"] + 1)]
            runs.append({**run, "cipher": cipher, "tokens": "".join(alpha.tokens[v] if v >= 0 else "?" for v in cipher),
                         "has_drop_cap": bool(gl[run["first"]].get("drop_cap"))})
        pages_out[p.stem] = {"glyphs": len(gl), "lines": r["lines"], "drop_caps": r["drop_caps"],
                             "terminators": r["terminators"], "unresolved": r["unresolved"], "red_runs": runs}
    seed_ok = {}
    for name, seq, sec in (("14-15", seq8, 8), ("16", seq9, 9)):
        ref = [int(v) for v in secs[sec]["ct"]]
        seed_ok[name] = sum(1 for a, b in zip(seq, ref) if labels.get(a) == b) / len(ref)
    return {"pages": pages_out, "labelled_shapes": len(labels), "seed_agreement": seed_ok, "shapes": len(frozen.reps)}


def headings_report(read: dict, alpha, out_dir) -> dict:
    solved_plain = ("05", "10", "11", "12", "13", "16", "74")
    validation = {p: [(r["tokens"], r["terminated"]) for r in read["pages"][p]["red_runs"]]
                  for p in solved_plain if p in read["pages"]}
    unsolved = []
    for pg, v in read["pages"].items():
        if 17 <= int(pg) <= 72:
            for r in v["red_runs"]:
                if 6 <= r["length"] <= 25 and all(x >= 0 for x in r["cipher"]):
                    unsolved.append({"page": int(pg), "cipher": r["cipher"], "tokens": r["tokens"], "terminated": r["terminated"]})
    controls = [{"page": int(pg), "cipher": r["cipher"], "tokens": r["tokens"]}
                for pg in ("73", "74") if pg in read["pages"] for r in read["pages"][pg]["red_runs"]
                if r["length"] >= 5 and all(x >= 0 for x in r["cipher"])]
    crib = crib_scan(unsolved, alpha)
    control = crib_scan(controls, alpha, min_len=5)
    rep = {"read": read, "validation_plain_pages": validation, "unsolved_headings": unsolved, "crib": crib,
           "crib_controls": control}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "headings.json").write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    lines = ["# Red headings read from the page images", "",
             "**EXPLORATORY.** Red runs are headings or closing lines; the dotted red square ends a red passage "
             f"(`|`). {read['labelled_shapes']} shapes labelled from pages 14-16 (agreement with the manifest: "
             + ", ".join(f"{k} {100 * v:.1f}%" for k, v in read["seed_agreement"].items()) + ").", "",
             "## Plain-substitution pages (readable as written)", ""]
    for p, runs in validation.items():
        lines.append(f"- page {p}: " + "; ".join(f"{t}{'|' if term else ''}" for t, term in runs))
    lines += ["", "## Red runs on the unsolved pages (ciphertext runes, as plain Gematria tokens)", "",
              "| page | length | terminated | ciphertext |", "| ---: | ---: | --- | --- |"]
    for u in unsolved:
        lines.append(f"| {u['page']} | {len(u['cipher'])} | {'yes' if u['terminated'] else 'no'} | {u['tokens']} |")
    lines += ["", "## Crib test", "",
              f"Each heading is tried against every title of the same length ({', '.join(TITLES)}). The implied key must be "
              f"a window of a sequence (7 families x 28 scales x offsets 0..{CRIB_OFFSETS}) or a short repeating key.", "",
              f"Unsolved headings: {crib['tested']} combinations tested, {len(crib['hits'])} hits. Random-plaintext baseline: "
              f"{crib['null_hits']} of {crib['null_tests']} false matches.", ""]
    for h in crib["hits"]:
        lines.append(f"- HIT page {h['page']} as '{h['title']}' [{h['convention']}]: {h['sequence_matches']} {h['repeat_periods']}")
    lines += ["", f"Known-page controls (pages 73 and 74): {len(control['hits'])} hits in {control['tested']} combinations:", ""]
    for h in control["hits"]:
        lines.append(f"- page {h['page']} as '{h['title']}' [{h['convention']}]: {h['sequence_matches']} {h['repeat_periods']}")
    (out / "headings.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lpswarm.pageimages", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["fetch", "headings"])
    ap.add_argument("--dir", default=str(IMG_DIR))
    ap.add_argument("--out", default="reports/diag")
    args = ap.parse_args(argv)
    if args.command == "fetch":
        n = fetch(args.dir)
        print(f"{n} images in {args.dir}; sha256 list in {SHA_FILE}")
        return 0
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET
    read = read_all(args.dir)
    rep = headings_report(read, get_alphabet(ALPHABET), args.out)
    print(Path(args.out, "headings.md").read_text(encoding="utf-8"))
    return 0 if rep else 1


if __name__ == "__main__":
    sys.exit(main())

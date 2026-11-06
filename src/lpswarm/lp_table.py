"""The unsolved pages as one small committed table (derived counts only; no images).

    python -m lpswarm.lp_table --out data/lp_derived/lp2_runes.csv [--pickle FILE]

One row per rune on pages 17-72 in reading order, from the image reading (`pageimages`), with the word separator the image shows after the
rune, whether the scream314 text has a word break there, the page, line and position, the colour, and the manifest section and position
the rune aligns to. Analyses that need page and line structure read this file, so they run without the page images.
"""
from __future__ import annotations

import argparse
import csv
import pickle
from pathlib import Path

import numpy as np

from lpswarm.research_doubles import align_sequences

COLUMNS = ("global", "page", "line", "idx_in_line", "rune", "token", "sep", "text_break", "red", "drop_cap", "terminator", "section",
           "section_idx")
PAGES = [f"{n:02d}" for n in range(17, 73)]
SECTIONS = tuple(range(10, 26))


def build_rows(read: dict, secs: dict, tokens: list[str], pages=PAGES, ids=SECTIONS) -> list[dict]:
    lab = read["lab"]
    glyphs = []
    for p in pages:
        if p not in read["reads"]:
            continue
        per_line: dict[int, int] = {}
        for g in sorted(read["reads"][p]["glyphs"], key=lambda g: (g["line"], g["x0"])):
            k = per_line.get(g["line"], 0)
            per_line[g["line"]] = k + 1
            rune = int(lab.get(g["shape"], -1)) if g["shape"] >= 0 and not g.get("unresolved") else -1
            glyphs.append((p, g, k, rune))
    ids = [i for i in ids if i in secs]
    text = [int(v) for i in ids for v in secs[i]["ct"]]
    bounds = np.cumsum([0] + [len(secs[i]["ct"]) for i in ids])
    starts = set()
    for n, i in enumerate(ids):
        starts |= {int(bounds[n]) + int(b) for b in secs[i]["breaks"]}
    al = align_sequences([r for _p, _g, _k, r in glyphs], text)
    rows = []
    for n, (p, g, k, rune) in enumerate(glyphs):
        if rune < 0:                                              # margin art and other non-runes
            continue
        j = int(al["a2b"][n])
        sec = ids[int(np.searchsorted(bounds, j, side="right")) - 1] if j >= 0 else None
        rows.append({"global": len(rows), "page": int(p), "line": g["line"] + 1, "idx_in_line": k, "rune": rune, "token": tokens[rune],
                     "sep": g.get("sep", "none"), "text_break": int(j >= 0 and (j + 1) in starts), "red": int(bool(g["red"])),
                     "drop_cap": int(bool(g.get("drop_cap"))), "terminator": int(bool(g.get("terminator"))),
                     "section": sec if sec is not None else "", "section_idx": j - int(bounds[ids.index(sec)]) if sec is not None else ""})
    return rows


def write_csv(rows: list[dict], path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def load_table(path) -> dict[str, np.ndarray]:
    """The table as numpy columns (ints, plus `sep` and `token` as strings)."""
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out: dict[str, np.ndarray] = {}
    for c in COLUMNS:
        vals = [r[c] for r in rows]
        if c in ("sep", "token"):
            out[c] = np.array(vals)
        else:
            out[c] = np.array([int(v) if v != "" else -1 for v in vals], dtype=np.int64)
    return out


def main(argv: list[str] | None = None) -> int:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.pageimages import read_all
    from lpswarm.research_packets import ALPHABET, load_sections
    ap = argparse.ArgumentParser(prog="python -m lpswarm.lp_table", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="data/lp_derived/lp2_runes.csv")
    ap.add_argument("--dir", default="data/lp_images")
    ap.add_argument("--pickle", default=None, help="cached read_all(keep=True) result")
    args = ap.parse_args(argv)
    tokens = list(get_alphabet(ALPHABET).tokens)
    read = pickle.load(open(args.pickle, "rb")) if args.pickle and Path(args.pickle).exists() else read_all(args.dir, keep=True)
    rows = build_rows(read, load_sections(indexes=list(SECTIONS)), tokens)
    write_csv(rows, args.out)
    print(f"{len(rows)} runes on {len({r['page'] for r in rows})} pages -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

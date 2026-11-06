"""Image reader audit: pure helpers and a synthetic page (no real images, no network)."""
import numpy as np
import pytest

pytest.importorskip("scipy")
pytest.importorskip("PIL")

from lpswarm import pageimages as P  # noqa: E402
from lpswarm import reader_audit as A  # noqa: E402
from test_pageimages import draw  # noqa: E402


def test_flag_margins_counts_the_documented_thresholds():
    d1 = np.array([0, 1, 2, 4, 3])
    d2 = np.array([40, 30, 14, 20, 9])
    f = A.flag_margins(d1, d2)
    assert f["d1_above_same_max"] == 1                    # only the 4
    assert f["d2_below_flat_gap"] == 2                    # 14 and 9
    assert f["gap_below_threshold"] == 1                  # gaps 40, 29, 12, 16, 6: only the 6 is under 8
    assert f["gap_min"] == 6 and f["d2_min"] == 9


def test_diff_counts_separates_wrong_unknown_and_structural():
    base = [3, 4, 5, 6, 7, 8, 9, 10]
    test = [3, 4, 9, 6, -1, 8, 10]                        # 5 read as 9 (wrong), 7 unknown, glyph 9 lost
    c = A.diff_counts(test, base)
    assert c == {"matched": 5, "wrong": 1, "unknown": 1, "structural": 1}      # 3, 4, 6, 8, 10 match
    assert c["matched"] + c["wrong"] + c["unknown"] <= len(test)
    assert A.diff_counts(base, base) == {"matched": 8, "wrong": 0, "unknown": 0, "structural": 0}


def test_separator_confusion_reports_both_directions():
    pairs = [(True, "word"), (True, "colon"), (False, "none"), (False, "none"), (True, "none"), (False, "word")]
    c = A.separator_confusion(pairs)
    assert (c["both_break"], c["neither"], c["text_only"], c["image_only"]) == (2, 2, 1, 1)
    assert c["agreement"] == pytest.approx(4 / 6)


def test_a_clean_synthetic_page_has_wide_margins_and_every_glyph_is_measured(tmp_path):
    rng = np.random.default_rng(5)
    lines = [[(int(rng.integers(0, 29)), False) for _ in range(14)] for _ in range(6)]
    path = tmp_path / "17.png"
    draw(lines, path)
    shapes = P.Shapes()
    P.read_page(path, shapes, learn=True)
    r = P.read_page(path, shapes, learn=False)
    gl = sorted(r["glyphs"], key=lambda g: (g["line"], g["x0"]))
    flat = [rn for l in lines for rn, _ in l]
    lab = {}
    for g, rn in zip(gl, flat):
        lab[g["shape"]] = rn
    read = {"frozen": shapes, "lab": lab, "reads": {"17": r}}
    rows = A.glyph_distances(read, tmp_path, ext=".png")
    assert len(rows) == len(flat)
    f = A.flag_margins(np.array([x["d1"] for x in rows]), np.array([x["d2"] for x in rows]))
    assert f["d1_max"] <= A.SAME_MAX and f["d2_min"] >= A.FLAT_GAP and f["gap_below_threshold"] == 0
    assert A.page_runes(read, "17") == flat


def test_a_wrong_glyph_size_gives_unknown_or_nothing_never_a_wrong_rune(tmp_path):
    from PIL import Image
    rng = np.random.default_rng(6)
    lines = [[(int(rng.integers(0, 29)), False) for _ in range(14)] for _ in range(6)]
    path = tmp_path / "17.png"
    draw(lines, path)
    shapes = P.Shapes()
    P.read_page(path, shapes, learn=True)
    base = P.read_page(path, shapes, learn=False)
    gl = sorted(base["glyphs"], key=lambda g: (g["line"], g["x0"]))
    lab = {g["shape"]: rn for g, rn in zip(gl, [rn for l in lines for rn, _ in l])}
    truth = [lab[g["shape"]] for g in gl]
    im = Image.open(path)
    for s in (0.7, 0.9, 0.95, 1.05, 1.15, 1.4):
        small = tmp_path / f"s{s}.png"
        im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS).save(small)
        r = P.read_page(small, shapes, learn=False)                 # must not raise, whatever the size
        got = [int(lab.get(g["shape"], -1)) if g["shape"] >= 0 else -1 for g in sorted(r["glyphs"], key=lambda g: (g["line"], g["x0"]))]
        assert A.diff_counts(got, truth)["wrong"] == 0, s

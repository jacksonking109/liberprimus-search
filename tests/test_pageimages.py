"""Page-image reader: synthetic pages drawn from planted rune bitmaps (no real images, no network)."""
import numpy as np
import pytest

pytest.importorskip("scipy")
PIL = pytest.importorskip("PIL")
from PIL import Image  # noqa: E402

from lpswarm import pageimages as P  # noqa: E402
from lpswarm.alphabet import get_alphabet  # noqa: E402
from lpswarm.research_packets import ALPHABET  # noqa: E402

N = 29
H = 114


def glyph(i: int) -> np.ndarray:
    """A distinct 114-high bitmap per rune index: a stem plus strokes chosen by the bits of i (9 px thick)."""
    w = 53 if i >= 16 else 34
    g = np.zeros((H, w), bool)
    g[:, :9] = True
    if i & 1:
        g[:9, :] = True
    if i & 2:
        g[52:61, :] = True
    if i & 4:
        g[H - 9:, :] = True
    if i & 8:
        for y in range(H):
            x = int(y * (w - 9) / H)
            g[y, x:x + 9] = True
    if (i >> 4) & 1 and (i & 1) == 0:
        for y in range(H):
            x = w - 9 - int(y * (w - 9) / H)
            g[y, x:x + 9] = True
    return g


def draw(runs, path, drop_cap=None, hatch_after=None, touch=None):
    """runs: list of lines; each line a list of (rune, is_red). Writes a 2400x3600 PNG."""
    img = np.full((3600, 2400, 3), 255, np.uint8)
    for j, line in enumerate(runs):
        yc = 700 + 217 * j
        x = 790 if (drop_cap is not None and j < 3) else 600
        for k, (r, red) in enumerate(line):
            g = glyph(r)
            y0 = yc - H // 2
            if touch is not None and (j, k) == touch:
                x -= 4                                          # overlap the previous glyph: they touch
            col = (190, 0, 0) if red else (0, 0, 0)
            img[y0:y0 + H, x:x + g.shape[1]][g] = col
            x += g.shape[1] + 20
            if k + 1 < len(line) and line[k + 1][1] == red and k % 4 == 3:
                img[yc - 5:yc + 5, x - 12:x - 2] = (0, 0, 0)       # a word dot
            if hatch_after == (j, k):
                for a in range(3):
                    for b in range(5):
                        img[yc - 25 + a * 18:yc - 15 + a * 18, x + b * 18:x + b * 18 + 10] = (190, 0, 0)
                x += 110
    if drop_cap is not None:
        g = np.kron(glyph(drop_cap), np.ones((5, 5), bool))[:, :170]
        img[672:672 + g.shape[0], 601:601 + g.shape[1]][g] = (190, 0, 0)
    Image.fromarray(img).save(path)


@pytest.fixture(scope="module")
def clean_page(tmp_path_factory):
    d = tmp_path_factory.mktemp("pages")
    rng = np.random.default_rng(3)
    lines = [[(int(rng.integers(0, 29)), False) for _ in range(14)] for _ in range(6)]
    lines[0] = [(r, True) for r, _ in lines[0][:6]] + lines[0][6:]
    path = d / "clean.png"
    draw(lines, path, hatch_after=(0, 5))
    return path, lines


def test_glyph_bitmaps_are_far_apart_so_identical_runes_group_exactly():
    b = [P.bin_aligned(glyph(i)) for i in range(29)]
    d = min(P.stroke_dist(b[i], b[j]) for i in range(29) for j in range(i + 1, 29))
    assert d >= 15


def test_reader_recovers_glyph_count_colours_and_the_dotted_terminator(clean_page):
    path, lines = clean_page
    shapes = P.Shapes()
    r = P.read_page(path, shapes, learn=True)
    gl = sorted(r["glyphs"], key=lambda g: (g["line"], g["x0"]))
    assert len(gl) == sum(len(l) for l in lines) and r["lines"] == 6
    runs = P.runs_of_red(gl)
    assert runs == [{"first": 0, "last": 5, "length": 6, "terminated": True}]       # a 6-rune heading, then the square
    assert sum(g["red"] for g in gl) == 6 and r["terminators"] == 1
    # the same rune always gets the same shape and different runes different shapes
    flat = [rn for l in lines for rn, _ in l]
    by = {}
    for g, rn in zip(gl, flat):
        by.setdefault(rn, set()).add(g["shape"])
    assert all(len(v) == 1 for v in by.values()) and len({next(iter(v)) for v in by.values()}) == len(by)


def test_a_touching_pair_is_split_once_both_shapes_are_known(tmp_path, clean_page):
    path, lines = clean_page
    shapes = P.Shapes()
    P.read_page(path, shapes, learn=True)                  # learn the shapes from a clean page
    known = {rn for l in lines for rn, _ in l}
    a, b = sorted(known)[:2]
    touching = [[(a, False), (b, False)] + [(sorted(known)[2], False)] * 3, [(b, False)] * 3 + [(a, False)] * 3,
                [(a, False)] * 4]
    p2 = tmp_path / "touch.png"
    draw(touching, p2, touch=(0, 1))
    r = P.read_page(p2, shapes, learn=False)
    gl = sorted(r["glyphs"], key=lambda g: (g["line"], g["x0"]))
    assert len(gl) == sum(len(l) for l in touching)
    assert all(g["shape"] >= 0 for g in gl) and r["unresolved"] == 0


def test_a_drop_cap_is_found_and_joins_the_first_line(tmp_path):
    lines = [[(i % 29, i < 3) for i in range(10)] for _ in range(5)]
    p = tmp_path / "drop.png"
    draw(lines, p, drop_cap=5, hatch_after=(0, 2))
    r = P.read_page(p, P.Shapes(), learn=True)
    assert r["drop_caps"] == 1
    gl = sorted(r["glyphs"], key=lambda g: (g["line"], g["x0"]))
    assert gl[0].get("drop_cap") and gl[0]["red"] and gl[0]["line"] == 0
    assert len(gl) == 51


def test_infer_labels_takes_the_majority_over_equal_length_pairs():
    pairs = [([7, 7, 9, 9, 9], [1, 1, 2, 2, 2]), ([7, 9], [1, 2]), ([5, 5], [3])]       # last pair is ignored
    assert P.infer_labels(pairs) == {7: 1, 9: 2}


def test_red_runs_with_and_without_terminators():
    gl = [{"red": r, "terminator": t} for r, t in [(True, False), (True, True), (False, False), (True, False), (True, False)]]
    runs = P.runs_of_red(gl)
    assert [(r["length"], r["terminated"]) for r in runs] == [(2, True), (2, False)]


def test_crib_scan_finds_a_planted_prime_stream_and_not_random_headings():
    from lpswarm.programs.sequences import window
    alpha = get_alphabet(ALPHABET)
    title = "THE LOSS OF DIVINITY"
    p = np.array([int(v) for v in alpha.encode(title.replace("V", "U"))], dtype=np.int64)
    key = window("primes", 0, 3000, N).astype(np.int64)[777:777 + len(p)]
    c = (p + 2 * key) % N                                 # prime stream, scale 2, offset 777
    found = P.crib_scan([{"page": 99, "cipher": c.tolist()}], alpha, offsets=2000, null_per_test=1)
    assert any(h["title"] == title and any(m[0] == "primes" and m[2] == 777 for m in h["sequence_matches"])
               for h in found["hits"])
    rng = np.random.default_rng(8)
    noise = [{"page": i, "cipher": rng.integers(0, N, size=16).tolist()} for i in range(6)]
    assert P.crib_scan(noise, alpha, offsets=2000, null_per_test=1)["hits"] == []
    assert P.short_period(np.array([4, 4, 4, 4, 4, 4])) == [1, 2, 3] and P.short_period(np.arange(8)) == []


def test_fetch_copies_images_and_records_hashes(tmp_path):
    def fake_run(cmd, check=True):
        if "clone" in cmd:
            d = tmp_path / "ignored"                       # the real clone dir is the last argument
            from pathlib import Path
            clone = Path(cmd[-1]) / "liber_primus"
            clone.mkdir(parents=True)
            for n in range(3):
                (clone / f"{n:02d}.jpg").write_bytes(bytes([n]) * 10)
            (clone / "notes.md").write_text("x")
    n = P.fetch(tmp_path / "imgs", run=fake_run, sha_file=tmp_path / "sums.txt")
    assert n == 3 and sorted(p.name for p in (tmp_path / "imgs").iterdir()) == ["00.jpg", "01.jpg", "02.jpg"]
    assert len((tmp_path / "sums.txt").read_text().splitlines()) == 3


# ------------------------------------------------------------------------------------ direct repeat count
def _rune(j, k):
    return (5 * j + 3 * k) % 29                         # neighbours differ by 3, and line ends never repeat


def _doubles_lines(substitute=None):
    """6 lines x 14 runes, no accidental repeats, with planted doubles:
    red heading double (line 0), plain double (line 1, gap 1-2), double after a word dot (line 2, gap 3-4),
    a double across a line end (line 3 -> line 4), and the two runes that are closest in shape side by side."""
    lines = [[(_rune(j, k), False) for k in range(14)] for j in range(6)]
    lines[0] = [(r, True) for r, _ in lines[0][:6]] + lines[0][6:]
    lines[0][2] = (lines[0][1][0], True)
    lines[1][2] = (lines[1][1][0], False)
    lines[2][4] = (lines[2][3][0], False)
    lines[4][0] = (lines[3][13][0], False)
    b = [P.bin_aligned(glyph(i)) for i in range(29)]
    a_, c_ = min(((i, j) for i in range(29) for j in range(i + 1, 29)), key=lambda t: P.stroke_dist(b[t[0]], b[t[1]]))
    lines[5][8:10] = [(a_, False), (c_, False)]         # different runes, adjacent, as alike as the alphabet allows
    if substitute:
        for (j, k), rn in substitute.items():
            lines[j][k] = (rn, lines[j][k][1])
    return lines


def _read_pairs(tmp_path, lines, learn_lines=None):
    shapes = P.Shapes()
    learn = tmp_path / "learn.png"
    draw(learn_lines or lines, learn, hatch_after=None)
    P.read_page(learn, shapes, learn=True)
    page = tmp_path / "page.png"
    draw(lines, page)
    r = P.read_page(page, shapes, learn=False)
    black, red = P.load_masks(page)
    return P.page_pairs(r, black, red), r


def test_doubles_are_counted_from_pixels_and_stratified(tmp_path):
    lines = _doubles_lines()
    pg, r = _read_pairs(tmp_path, lines)
    flat = [rn for l in lines for rn, _ in l]
    truth = sum(1 for a, b in zip(flat, flat[1:]) if a == b)
    assert truth == 4 and len(pg["rows"]) == len(flat) - 1 and pg["excluded"] == 0
    found = [x for x in pg["rows"] if x["double"]]
    assert len(found) == truth
    assert sorted((x["line"], x["kind"], x["sep"], x["red"]) for x in found) == sorted([
        (0, "within", "none", True), (1, "within", "none", False), (2, "within", "word", False),
        (3, "line_end", "none", False)])
    near = [x for x in pg["rows"] if x["line"] == 5 and x["i"] >= 5 * 14 + 8][:1]          # the closest pair of different runes
    assert near and not near[0]["double"] and near[0]["pix"] is not None and near[0]["pix"] > P.THRESH


def test_the_two_identity_tests_agree_on_every_pair(tmp_path):
    pg, _ = _read_pairs(tmp_path, _doubles_lines())
    assert not any(x["disagree"] for x in pg["rows"])
    for x in pg["rows"]:
        if x["pix"] is None:                                  # glyph widths differ by more than 6 px: not the same rune
            assert not x["double"] and not x["same_shape"]
        else:
            assert (x["pix"] <= P.THRESH) == x["double"] == x["same_shape"]
    assert sum(x["pix"] is not None for x in pg["rows"]) > 40


def test_pairs_touching_unknown_glyphs_are_excluded_and_counted(tmp_path):
    base = _doubles_lines()
    # learn the shapes on a page that never shows rune 9, then read a page where it appears twice mid-line
    learn_lines = [[(rn if rn != 9 else 10, red) for rn, red in l] for l in base]
    page_lines = [list(l) for l in learn_lines]
    page_lines[1][6], page_lines[3][9] = (9, False), (9, False)
    pg, r = _read_pairs(tmp_path, page_lines, learn_lines)
    n = sum(len(l) for l in page_lines)
    assert pg["excluded"] == 4 and len(pg["rows"]) == n - 1 - 4          # two neighbours of each unknown glyph
    assert sum(1 for g in pg["glyphs"] if g["shape"] < 0) == 2
    assert sum(x["double"] for x in pg["rows"]) >= 3                    # planted doubles elsewhere are still found
    assert 9 not in {rn for l in learn_lines for rn, _ in l}


def test_expected_count_and_shuffle_null_use_each_pages_own_shapes():
    shapes = [0, 0, 1, 1, 2, 2]
    rows = [{"i": i} for i in range(5)]
    assert P.expected_doubles(shapes, rows) == pytest.approx(5 / 3)                 # 5 pairs x (3 x (1/3)^2)
    assert P.expected_doubles([-1, -1], []) == 0.0
    null = P.shuffle_null([{"shapes": shapes, "rows": rows}], reps=199)
    assert null.max() <= 3 and 0.6 < null.mean() < 1.4                              # 5 pairs x 0.2 chance
    s = P.summarise([{"shapes": shapes, "rows": [{**r, "double": shapes[r["i"]] == shapes[r["i"] + 1], "disagree": False,
                                                    "kind": "within", "sep": "none", "red": False} for r in rows],
                      "excluded": 0}], reps=199)
    assert s["pairs"] == 5 and s["doubles"] == 3 and s["shuffle"]["z"] > 1.5 and s["ratio"] == pytest.approx(3 / (5 / 3))

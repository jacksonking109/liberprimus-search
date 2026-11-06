"""The committed rune table: built from a synthetic page, round-tripped through CSV (no real images)."""
import numpy as np
import pytest

pytest.importorskip("scipy")
pytest.importorskip("PIL")

from lpswarm import lp_table as T  # noqa: E402
from lpswarm import pageimages as P  # noqa: E402
from test_pageimages import draw  # noqa: E402


def _synthetic(tmp_path):
    rng = np.random.default_rng(9)
    lines = [[(int(rng.integers(0, 29)), False) for _ in range(14)] for _ in range(6)]
    lines[0] = [(r, True) for r, _ in lines[0][:6]] + lines[0][6:]
    path = tmp_path / "17.png"
    draw(lines, path)
    shapes = P.Shapes()
    P.read_page(path, shapes, learn=True)
    r = P.read_page(path, shapes, learn=False)
    flat = [rn for l in lines for rn, _ in l]
    gl = sorted(r["glyphs"], key=lambda g: (g["line"], g["x0"]))
    lab = {g["shape"]: rn for g, rn in zip(gl, flat)}
    return {"frozen": shapes, "lab": lab, "reads": {"17": r}}, flat


def test_rows_carry_page_line_position_separator_colour_and_section(tmp_path):
    read, flat = _synthetic(tmp_path)
    breaks = [4, 8, 12, 14, 20]                                   # word starts in the (synthetic) text
    secs = {10: {"ct": np.array(flat), "breaks": breaks}}
    tokens = [f"R{i}" for i in range(29)]
    rows = T.build_rows(read, secs, tokens, pages=["17"], ids=[10])
    assert [r["rune"] for r in rows] == flat and [r["global"] for r in rows] == list(range(len(flat)))
    assert {r["page"] for r in rows} == {17} and {r["section"] for r in rows} == {10}
    assert [r["section_idx"] for r in rows] == list(range(len(flat)))
    assert [r["line"] for r in rows][:15] == [1] * 14 + [2] and [r["idx_in_line"] for r in rows][:3] == [0, 1, 2]
    assert [r["text_break"] for r in rows].count(1) == len(breaks)
    assert all(rows[b - 1]["text_break"] == 1 for b in breaks)
    assert sum(r["red"] for r in rows) == 6 and rows[3]["sep"] == "word" and rows[4]["sep"] == "none"      # the helper draws a dot after glyph 3, 7, 11
    assert rows[0]["token"] == f"R{flat[0]}"


def test_csv_round_trip_keeps_every_column(tmp_path):
    read, flat = _synthetic(tmp_path)
    secs = {10: {"ct": np.array(flat), "breaks": [4, 8]}}
    rows = T.build_rows(read, secs, [f"R{i}" for i in range(29)], pages=["17"], ids=[10])
    T.write_csv(rows, tmp_path / "t.csv")
    t = T.load_table(tmp_path / "t.csv")
    assert set(t) == set(T.COLUMNS)
    assert t["rune"].tolist() == flat and t["sep"].tolist() == [r["sep"] for r in rows]
    assert t["section"].tolist() == [10] * len(flat) and t["text_break"].sum() == 2

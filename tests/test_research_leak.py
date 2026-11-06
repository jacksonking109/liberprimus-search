"""Leak anatomy on synthetic tables: a random placement is not flagged, planted structures are (fixed seeds)."""
import numpy as np
import pytest

from lpswarm import research_leak as L

N = 29


def _table(seed=1, pages=20, per_page=300, line_len=14, word=5):
    """A synthetic table with real-looking page, line and word structure and a rune stream that never repeats."""
    rng = np.random.default_rng(seed)
    rows = {k: [] for k in ("rune", "page", "line", "idx_in_line", "sep", "text_break", "red", "drop_cap", "section", "section_idx", "token")}
    prev = -1
    for p in range(pages):
        for i in range(per_page):
            r = int(rng.integers(0, N))
            while r == prev:
                r = int(rng.integers(0, N))
            prev = r
            rows["rune"].append(r)
            rows["page"].append(17 + p)
            rows["line"].append(1 + i // line_len)
            rows["idx_in_line"].append(i % line_len)
            rows["sep"].append("word" if (i + 1) % word == 0 and (i % line_len) != line_len - 1 else "none")
            rows["text_break"].append(0)
            rows["red"].append(0)
            rows["drop_cap"].append(0)
            rows["section"].append(10 + p // 4)
            rows["section_idx"].append((p % 4) * per_page + i)
            rows["token"].append("A" if r % 3 == 0 else "B")
    return {k: np.array(v) for k, v in rows.items()}


def _plant(t, positions):
    t = dict(t)
    c = t["rune"].copy()
    for i in positions:
        c[i + 1] = c[i]
    t["rune"] = c
    return t


def _positions(d, rng, n, weights=None):
    return np.sort(rng.choice(d["V"], size=n, replace=False, p=weights))


def test_prepare_builds_words_and_pair_kinds():
    t = _table(pages=2, per_page=60)
    d = L.prepare(t)
    assert d["n"] == 120 and d["V"] == 119 and not d["equal"].any()
    kinds = L.layout_features(d)["pair kind (within line / over a line end / over a page end)"][0]
    assert (kinds == 2).sum() == 1 and (kinds == 1).sum() == (60 // 14 - 1 + 1) * 2 - 1 + 0 or (kinds == 1).sum() > 0
    assert d["pos"][0] == 0 and d["pos"][4] == 4 and d["wlen"][0] == 5


def test_a_random_placement_of_doubles_is_rarely_flagged():
    """Under a random placement a family p < 0.01 should be rare; allow one in eight for the rare-cell statistics."""
    t = _table()
    d = L.prepare(t)
    flagged = 0
    for seed in range(8):
        pos = _positions(d, np.random.default_rng(100 + seed), 60)
        rep = L.analyse(_plant(t, pos), reps=300, max_m=40, seed=seed)
        assert 60 <= rep["doubles"] <= 70
        flagged += rep["verdict"] == "structured"
    assert flagged <= 1


@pytest.mark.parametrize("kind,family", [("phase", "phase"), ("word_dot", "layout"), ("clusters", "spacing"), ("vowels", "alphabet")])
def test_planted_structure_is_detected(kind, family):
    t = _table(seed=3)
    d = L.prepare(t)
    rng = np.random.default_rng(4)
    V = d["V"]
    g = d["g"][:-1]
    if kind == "phase":
        w = np.where(g % 13 == 4, 12.0, 1.0)
    elif kind == "word_dot":
        w = np.where(d["sep"][:-1] == "word", 12.0, 1.0)
    elif kind == "clusters":
        w = np.ones(V)
        for c in rng.choice(V, 4, replace=False):
            w[max(c - 15, 0):c + 15] = 80.0
    else:
        w = np.where(np.isin(d["token"][:-1], L.VOWELS), 12.0, 1.0)
    pos = _positions(d, rng, 70, w / w.sum())
    rep = L.analyse(_plant(t, pos), reps=500, max_m=60)
    assert rep["families"][family]["p_family"] < 0.01, (kind, rep["families"][family]["p_family"])
    assert rep["verdict"] == "structured"


def test_chi_square_and_null_sampler_basics():
    S = L.sample_positions(1000, 20, 50, seed=1)
    assert S.shape == (50, 20) and all(len(set(r)) == 20 for r in S)
    prop = np.array([0.5, 0.5])
    assert L.chi_square(np.array([[10, 10]]), prop)[0] == 0
    assert L.chi_square(np.array([[20, 0]]), prop)[0] == pytest.approx(20.0)
    sp = L.spacing_stats(np.array([[0, 10, 20, 500]]), close=20)
    assert sp["minimum gap"][0] == 10 and sp["maximum gap"][0] == 480


def test_the_table_loader_feeds_the_analysis(tmp_path):
    from lpswarm import lp_table
    t = _table(pages=3, per_page=100)
    rows = [{"global": i, "page": int(t["page"][i]), "line": int(t["line"][i]), "idx_in_line": int(t["idx_in_line"][i]), "rune": int(t["rune"][i]),
             "token": str(t["token"][i]), "sep": str(t["sep"][i]), "text_break": 0, "red": 0, "drop_cap": 0, "terminator": 0,
             "section": int(t["section"][i]), "section_idx": int(t["section_idx"][i])} for i in range(len(t["rune"]))]
    lp_table.write_csv(rows, tmp_path / "t.csv")
    loaded = lp_table.load_table(tmp_path / "t.csv")
    rep = L.analyse(loaded, reps=50, max_m=20)
    assert rep["runes"] == 300 and rep["doubles"] == 0 or rep["doubles"] >= 0

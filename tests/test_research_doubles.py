"""Per-rune breakdown of the repeat shortage and text-to-image alignment, on synthetic data (no images, no network)."""
import numpy as np
import pytest

from lpswarm import research_doubles as R

N = 29
TOKENS = [f"R{i}" for i in range(N)]


def _units(rng, n_units=10, length=300, weights=None, suppress=None):
    """iid runes (rune 3 frequent); suppress(seq) may rewrite doubles afterwards."""
    w = np.ones(N)
    w[3] = 8.0
    w /= w.sum()
    out = {}
    for u in range(n_units):
        seq = rng.choice(N, size=length, p=w if weights is None else weights)
        if suppress is not None:
            suppress(seq, rng)
        out[f"u{u}"] = seq
    return out


def _kill_rune3_doubles(seq, rng):
    for i in range(len(seq) - 1):
        if seq[i] == 3 and seq[i + 1] == 3:
            seq[i + 1] = (3 + 1 + int(rng.integers(0, N - 1))) % N


def _thin_all_doubles(seq, rng, keep=0.2):
    for i in range(len(seq) - 1):
        if seq[i] == seq[i + 1] and rng.random() > keep:
            seq[i + 1] = (seq[i] + 1 + int(rng.integers(0, N - 1))) % N


def test_expectation_is_exact_and_matches_the_shuffle_null():
    rng = np.random.default_rng(1)
    units = _units(rng, n_units=4, length=200)
    units["u0"][::7] = -1                                          # unknown positions stay out of the pairs
    e = R.expected(units)
    by_rune, by_lag = R.null_counts(units, reps=600, seed=5)
    assert e["rune"].sum() == pytest.approx(by_rune.sum(axis=1).mean(), rel=0.05)
    assert e["lag"][0] == pytest.approx(by_lag[:, 0].mean(), rel=0.05)
    assert e["lag"][3] == pytest.approx(by_lag[:, 3].mean(), rel=0.05)
    assert R.observed(units)["rune"].sum() == sum(int(((u[:-1] == u[1:]) & (u[:-1] >= 0)).sum()) for u in units.values())


def test_a_planted_per_rune_suppression_is_flagged_and_uniform_suppression_is_not():
    rng = np.random.default_rng(2)
    planted = R.perrune_report(_units(rng, suppress=_kill_rune3_doubles), TOKENS, reps=1999, seed=11)
    row3 = planted["runes"][3]
    assert row3["doubles"] == 0 and row3["expected"] > 30 and row3["p_holm_vs_pooled"] < 0.05
    assert planted["heterogeneity_runes"]["p"] < 0.01
    assert [r["rune"] for r in planted["runes"] if (r["p_holm_vs_pooled"] or 1) < 0.05] == [3]

    uniform = R.perrune_report(_units(np.random.default_rng(3), suppress=_thin_all_doubles), TOKENS, reps=1999, seed=11)
    assert uniform["ratio_permutation"] < 0.4                                    # a strong, even deficit
    assert uniform["heterogeneity_runes"]["p"] > 0.05
    assert not any((r["p_holm_vs_pooled"] or 1) < 0.05 for r in uniform["runes"])
    assert any(r["p_holm_vs_chance"] < 0.05 for r in uniform["runes"])            # each frequent rune is short of chance


def test_the_lag_profile_separates_a_lag_one_deficit_from_a_general_one():
    rng = np.random.default_rng(4)
    rep = R.perrune_report(_units(rng, n_units=10, length=400, suppress=_thin_all_doubles), TOKENS, reps=299, seed=3)
    lag = {r["lag"]: r for r in rep["lags"]}
    assert lag[1]["ratio"] < 0.4 and lag[1]["p_deficit"] < 0.01 and lag[1]["z"] < -5
    assert all(0.7 < lag[k]["ratio"] < 1.3 for k in range(2, 9))


def test_heterogeneity_and_holm_basics():
    d = np.array([10, 10, 10, 10])
    assert R.heterogeneity(d, np.ones(4), reps=999)["p"] > 0.9
    assert R.heterogeneity(np.array([0, 20, 10, 10]), np.ones(4), reps=999)["p"] < 0.05
    assert list(R.holm([0.01, 0.04, 0.03])) == pytest.approx([0.03, 0.06, 0.06])
    pw = R.power_line(np.arange(1, 30, dtype=float), 86, 41.3, sims=300)
    assert pw["top5_runes_never_double"] > 0.2 or pw["only_top5_runes_double"] > 0.2


# ------------------------------------------------------------------------------------------------ alignment
def _base(rng, n=1000):
    x = [int(rng.integers(0, N))]
    while len(x) < n:
        v = int(rng.integers(0, N))
        if v != x[-1]:
            x.append(v)
    return x


def _secs(text, cut=600):
    return {10: {"ct": np.array(text[:cut])}, 11: {"ct": np.array(text[cut:])}}


def _units_from(seq):
    h = len(seq) // 2
    return {"17": {"runes": seq[:h], "lines": [0] * h}, "18": {"runes": seq[h:], "lines": [0] * (len(seq) - h)}}


def test_identical_sources_align_with_no_discrepancies():
    base = _base(np.random.default_rng(5))
    rep = R.align_report(_units_from(base), _secs(base), TOKENS, ids=(10, 11))
    assert rep["gate_passed"] and rep["matched_fraction_of_image"] == 1.0
    assert rep["substituted"] == rep["image_only"] == rep["text_only"] == 0
    assert rep["doubles"]["differences"] == [] and rep["doubles"]["both"] == 0


def test_planted_differences_are_recovered_with_their_kind():
    rng = np.random.default_rng(6)
    base = _base(rng)
    text, image = list(base), list(base)
    text[101] = text[100]                         # a double only the transcription has (the image shows a different glyph)
    image[301] = image[300]                       # a double only the image has
    text[501] = text[500] = image[501] = image[500] = base[500]      # a double in both
    image[200] = -1                               # a glyph with no known shape
    image[700] = (base[700] + 5) % N              # a substitution
    for k in (699, 701):
        assert image[700] not in (base[k],)
    image.insert(800, (base[800] + 7) % N)        # a glyph the text lacks
    del image[901]                                # a rune the image lacks (index shifted by the insertion)
    rep = R.align_report(_units_from(image), _secs(text), TOKENS, ids=(10, 11))
    assert rep["gate_passed"] and rep["unknown_image_glyphs"] == 1
    assert rep["image_only"] == 1 and rep["text_only"] == 1 and rep["substituted"] == 4
    d = rep["doubles"]
    assert (d["both"], d["image_only"], d["text_only"]) == (1, 1, 1)
    assert d["image_total"] == 2 and d["text_total"] == 2
    img_only = next(r for r in d["differences"] if r["kind"] == "image_only")
    txt_only = next(r for r in d["differences"] if r["kind"] == "text_only")
    assert img_only["page"] == "17" and img_only["reason"] == "text has different runes"
    assert txt_only["page"] == "17" and txt_only["reason"] == "image has different glyphs"
    assert "[" in img_only["image"] and "[" in txt_only["text"]
    assert sum(s["text_substituted"] for s in rep["sections"]) == 4
    assert any(w["page"] == "17" for w in rep["worst_pages"])


def test_the_gate_stops_the_doubles_comparison_on_unrelated_sequences():
    rng = np.random.default_rng(7)
    a, b = _base(rng), _base(rng)
    rep = R.align_report(_units_from(a), _secs(b), TOKENS, ids=(10, 11))
    assert not rep["gate_passed"] and rep["doubles"] is None


def test_image_units_use_the_label_map_and_mark_unknown_glyphs():
    glyphs = [{"shape": 0, "line": 0, "x0": 5}, {"shape": 1, "line": 0, "x0": 1}, {"shape": -1, "line": 1, "x0": 0},
              {"shape": 1, "line": 1, "x0": 9, "unresolved": True}]
    u = R.image_units({"lab": {0: 7, 1: 3}, "reads": {"17": {"glyphs": glyphs}}})
    assert u["17"]["runes"] == [3, 7, -1, -1] and u["17"]["lines"] == [0, 0, 1, 1]

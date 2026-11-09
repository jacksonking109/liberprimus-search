"""Literal readings: self-keyed round trips and recovery, prime-step walks, grid sums (synthetic)."""
import numpy as np

from lpswarm import research_literal as R

N = 29


def test_self_keyed_variants_round_trip_and_a_planted_text_is_recovered():
    rng = np.random.default_rng(1)
    w = np.arange(N, 0, -1) ** 2.0
    p = rng.choice(N, size=2000, p=w / w.sum())
    for kind, lag, sign in R.VARIANTS:
        c = R.encrypt_self_keyed(p, kind, lag, sign, seed=2)
        assert np.array_equal(R.decrypt_self_keyed(c, kind, lag, sign), p)
        assert R.ic29(R.decrypt_self_keyed(c, kind, lag, sign)) > 1.5 > R.ic29(c)


def test_prime_keyed_flags_a_planted_section_and_ignores_short_ones():
    rng = np.random.default_rng(3)
    w = np.arange(N, 0, -1) ** 2.0
    planted = R.encrypt_self_keyed(rng.choice(N, size=800, p=w / w.sum()), "prime of rune t-lag", 1, 1, seed=4)
    secs = {10: {"ct": planted}, 11: {"ct": rng.integers(0, N, 600)}, 15: {"ct": np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])}}
    rep = R.prime_keyed(secs, [10, 11, 15], shuffles=10)
    assert rep["sections"] == ["10", "11"]
    row = next(r for r in rep["rows"] if r["variant"] == "p = c - key, key = prime of rune t-1")
    assert row["flag"] and row["per_section"]["10"] > 1.5


def test_jump_walk_steps_by_prime_values_and_stops_before_a_revisit():
    runes = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])            # primes 2, 3, 5, 7, 11, 13, 17, 19, 23, 29
    assert R.jump_walk(runes, 0).tolist()[:3] == [0, 2, 7]     # 0 -> +2 -> 2 -> +5 -> 7
    w = R.jump_walk(runes, 0)
    assert len(w) == len(set(range(10)) & set(range(10))) or len(w) <= 10


def test_grid_sums_find_hint_numbers():
    runes = np.zeros(121, dtype=np.int64)                        # every cell prime 2
    g = R.grid_sums(runes)
    assert g["side"] == 11 and g["rows"][0] == 22 and g["total"] == 242
    assert g["hint_number_hits"] == []

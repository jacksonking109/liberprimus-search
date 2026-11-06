"""Signature screen: which DSL mechanisms reproduce the repeat signature (synthetic data, no oracle)."""
from collections import Counter

import numpy as np
import pytest

from lpswarm import research_signature as S
from lpswarm.alphabet import get_alphabet
from lpswarm.programs.spec import compile_spec
from lpswarm.research_packets import ALPHABET, _spec

N = 29
ALPHA = get_alphabet(ALPHABET)
REF = {"ratio": 0.2, "ci": [0.157, 0.243]}


def _windows(rng, n=3, length=3000, skip=()):
    keep = [r for r in range(N) if r not in skip]
    return [(rng.choice(keep, size=length).astype(np.int64), ()) for _ in range(n)]


def test_poisson_interval_matches_known_values():
    lo, hi = S.poisson_ci(0)
    assert lo == 0.0 and hi == pytest.approx(3.689, abs=0.01)
    lo, hi = S.poisson_ci(86)
    assert lo == pytest.approx(68.8, abs=0.3) and hi == pytest.approx(106.2, abs=0.3)
    lo, hi = S.poisson_ci(10)
    assert lo == pytest.approx(4.795, abs=0.02) and hi == pytest.approx(18.39, abs=0.05)


def test_profile_reads_one_for_iid_and_zero_for_a_no_repeat_sequence():
    rng = np.random.default_rng(1)
    iid = S.profile({str(i): rng.integers(0, N, size=4000) for i in range(4)})
    assert 0.85 < iid["ratio"][0] < 1.15 and np.all(np.abs(iid["ratio"][1:] - 1) < 0.2)
    no_rep = np.cumsum(rng.integers(1, N, size=4000)) % N                  # neighbours always differ
    p = S.profile({"x": no_rep})
    assert p["equal"][0] == 0 and p["ratio"][0] == 0.0


def test_a_constant_shift_keeps_the_ratio_exactly_and_a_progressive_key_changes_it():
    rng = np.random.default_rng(2)
    runs = [(np.repeat(rng.integers(0, N, size=300), 10).astype(np.int64), ()) for _ in range(3)]   # plaintext full of repeats
    ident = compile_spec(_spec(0), ALPHA)
    shift = compile_spec(_spec(5), ALPHA)
    prog = compile_spec({"stream": {"kind": "sequence", "name": "naturals", "scale": 1, "offset": 0, "add": 0},
                         "combine": "sub"}, ALPHA)
    r0, r5, rp = (S.screen_spec(sp, runs) for sp in (ident, shift, prog))
    assert np.allclose(r0, r5, rtol=1e-9) and r0[0] > 10
    assert rp[0] < r0[0] / 10                                                  # a non-zero step removes the repeats


def test_neighbour_feedback_doubles_are_exactly_the_plaintext_rune_minus_b():
    """neighbor sub with shift b: c[i] == c[i-1] iff p[i] == -b. Without that rune in the plaintext there are no repeats."""
    mix = {"kind": "neighbor", "op": "sub", "lag": 1, "dir": "prev", "reset": "none", "at": "before"}
    b = 7
    spec = compile_spec(_spec(b, mix), ALPHA)
    missing = (-b) % N
    without = S.screen_spec(spec, _windows(np.random.default_rng(3), skip=(missing,)))
    withit = S.screen_spec(spec, _windows(np.random.default_rng(3)))
    assert without[0] == 0.0 and withit[0] > 0.5
    assert np.all(np.abs(without[1:] - 1) < 0.25)                              # the other lags stay near chance


def test_classify_applies_the_prespecified_band_and_the_loose_sensitivity():
    flat = np.array([0.2, 1.0, 1.0, 1.1, 0.9, 1.0, 1.0, 1.0])
    band = [0.24, 0.84]
    c = S.classify(flat, REF, plain_r1=0.7, loose_band=band, uni_ic=1.02, diff_ic=1.05)
    assert c["match"] and c["in_ci"] and c["flat"] and c["ic_ok"] and c["full"] and c["loose"]
    off = flat.copy(); off[0] = 0.4
    c = S.classify(off, REF, plain_r1=0.7, loose_band=band, uni_ic=1.02, diff_ic=1.05)
    assert not c["match"] and not c["full"] and c["loose"] and c["factor"] == pytest.approx(0.4 / 0.7)
    bumpy = flat.copy(); bumpy[2] = 1.4
    assert not S.classify(bumpy, REF)["match"] and not S.classify(bumpy, REF)["flat"]
    # lag conditions alone pass, but the first differences are language-like: a lag-only match, not a full one
    c = S.classify(flat, REF, plain_r1=0.7, loose_band=band, uni_ic=1.02, diff_ic=1.8)
    assert c["match"] and not c["ic_ok"] and not c["full"] and not c["loose"]


def test_the_ic_helpers_read_one_for_uniform_and_high_for_skewed_symbols():
    rng = np.random.default_rng(5)
    assert S._ic29([rng.integers(0, N, size=20000)]) == pytest.approx(1.0, abs=0.05)
    w = np.arange(N, 0, -1) ** 2.0
    skew = rng.choice(N, size=20000, p=w / w.sum())
    assert S._ic29([skew]) > 1.4


def test_neighbour_feedback_flattens_the_symbols_but_leaves_the_first_differences_skewed():
    """A running sum of skewed plaintext is near-uniform, but its first differences are the plaintext (shifted): this is
    why a neighbour-feedback cipher can match the lag statistics and still contradict the real, flat, first differences."""
    rng = np.random.default_rng(6)
    w = np.arange(N, 0, -1) ** 2.0
    windows = [(rng.choice(N, size=5000, p=w / w.sum()).astype(np.int64), ()) for _ in range(4)]
    mix = {"kind": "neighbor", "op": "sub", "lag": 1, "dir": "prev", "reset": "none", "at": "before"}
    plain = S.screen_full(compile_spec(_spec(0), ALPHA), windows)
    fed = S.screen_full(compile_spec(_spec(7, mix), ALPHA), windows)
    assert plain["uni_ic"] > 1.5 and fed["uni_ic"] < 1.15 and fed["diff_ic"] > 1.5


def test_a_spec_that_cannot_be_enciphered_is_counted_not_raised():
    S._init(_windows(np.random.default_rng(4), n=1, length=200))
    fam, label, ratio, err = S._work(("f", "broken", {"stream": {"kind": "nonsense"}, "combine": "sub"}))
    assert ratio is None and err and fam == "f"


def test_packet_families_are_enumerated_as_the_packets_expand_them():
    counts = Counter(f for f, _l, _s in S.packet_candidates(ALPHA, wordkey_limit=20))
    assert counts["exp1 feedback (neighbour/chain, 8 forms x b)"] == 8 * N + N
    assert counts["exp2b two-shear Hill blocks, all shifts"] == 32 * N + N
    assert counts["exp3 progressive keys"] == 6 * 28 * N + 1
    assert sum(1 for _ in S.sequence_candidates(ALPHA)) == len(S.EXTRA_SEQUENCES) * 2 * 28 * len(S.EXTRA_OFFSETS)
    assert [l for _f, l, _s in S.control_candidates(ALPHA)][0] == "identity"


def test_the_thinned_walk_has_the_signature_so_the_criteria_can_be_met():
    rng = np.random.default_rng(8)
    units = {str(i): S.thinned_walk(5000, rng) for i in range(6)}
    pr = S.profile(units)
    c = S.classify(pr["ratio"], {"ratio": 0.2, "ci": [0.15, 0.25]}, None, None, pr["uni_ic"], pr["diff_ic"])
    assert 0.15 <= pr["ratio"][0] <= 0.25 and np.all(np.abs(pr["ratio"][1:] - 1) < 0.15)
    assert pr["uni_ic"] < 1.1 and pr["diff_ic"] < 1.1 and c["full"]


def test_the_wider_mixer_sweep_enumerates_what_it_says_and_every_cipher_round_trips():
    from lpswarm.programs.spec import roundtrips
    cands = list(S.mixer_candidates(ALPHA, lags=(1, 2), hill_samples=3))
    counts = Counter(f for f, _l, _s in cands)
    assert counts[S.FEEDBACK_FAMILY] == 2 * 3 * 2 * 2 * 3 * 2 * 2 * N
    assert counts[S.HILL_FAMILY] == 3 * 3 and counts[S.PERM_FAMILY] == 2 + 6 + 24 + 120
    rng = np.random.default_rng(9)
    pt = rng.integers(0, N, size=240).astype(np.int64)
    breaks = list(range(0, 240, 5))
    for fam in (S.FEEDBACK_FAMILY, S.HILL_FAMILY, S.PERM_FAMILY):
        mine = [c for c in cands if c[0] == fam]
        for _f, _label, spec in mine[:: max(len(mine) // 40, 1)]:
            assert roundtrips(pt, spec, N, breaks=breaks), (fam, spec)


def test_english_windows_are_deterministic_and_disjoint():
    a = S.english_windows(ALPHA, 4, 500, seed=3)
    b = S.english_windows(ALPHA, 4, 500, seed=3)
    assert all(np.array_equal(x[0], y[0]) and x[1] == y[1] for x, y in zip(a, b))
    assert all(len(w) == 500 and max(br, default=0) < 500 for w, br in a)
    assert not np.array_equal(a[0][0], a[1][0])

"""Multiplicatively keyed running sums: the zero-step property, the IC sweep and its controls (synthetic)."""
import numpy as np
import pytest

from lpswarm import research_muldiff as M

N = 29


def test_inverse_table_and_ic_helper():
    assert all((a * M.INV[a]) % N == 1 for a in range(1, N)) and M.INV[0] == 0
    rng = np.random.default_rng(1)
    rows = rng.integers(0, N, size=(4, 3000))
    ic = M.ic29(rows, np.ones_like(rows, bool))
    assert np.all(np.abs(ic - 1.0) < 0.1)
    skew = np.zeros((1, 100), dtype=np.int64)
    assert M.ic29(skew, np.ones_like(skew, bool))[0] == pytest.approx(29.0)


def test_a_zero_step_happens_exactly_where_the_plaintext_is_the_zero_rune():
    rng = np.random.default_rng(2)
    plain = rng.integers(0, N, size=4000)
    key = rng.integers(1, N, size=4000)
    for zero in (28, 0, 9):
        c = M.encipher_muldiff(plain, key, zero)
        steps = (c[1:] - c[:-1]) % N
        assert np.array_equal(steps == 0, plain[1:] == zero)


def test_the_family_has_flat_steps_and_a_rare_zero_step_for_the_29th_rune():
    from lpswarm import research_signature as S
    rng = np.random.default_rng(3)
    w = np.arange(N, 0, -1) ** 2.0
    units = {str(i): M.encipher_muldiff(rng.choice(N, size=5000, p=w / w.sum()), rng.integers(1, N, size=5000), 28) for i in range(6)}
    pr = S.profile(units)
    assert pr["uni_ic"] < 1.1 and pr["diff_ic"] < 1.1                      # skewed plaintext, flat ciphertext and steps
    p28 = w[28] / w.sum()
    assert pr["ratio"][0] == pytest.approx(N * p28, abs=0.1) or pr["ratio"][0] < 0.5


def test_the_sweep_recovers_a_planted_position_keyed_multiplier_and_not_noise():
    seqs = M.sequences(900)
    rng = np.random.default_rng(4)
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET
    from lpswarm.textgen.synth import encoded_text
    text = encoded_text(get_alphabet(ALPHABET), "english", "train").astype(np.int64)
    key = np.where(seqs["primes"][40:40 + 500] == 0, 1, seqs["primes"][40:40 + 500])
    ct = M.encipher_muldiff(text[1000:1500], key, 28)
    r = M.run_section(ct, {"primes": seqs["primes"], "naturals": seqs["naturals"]}, offsets=100, window=480)
    assert r["sequence"] == "primes" and r["offset"] == 41 and r["best_ic"] > 1.5     # first difference j uses key[j + 1]
    noise = M.run_section(rng.integers(0, N, size=500), {"primes": seqs["primes"], "naturals": seqs["naturals"]}, offsets=100, window=480)
    assert noise["best_ic"] < 1.25

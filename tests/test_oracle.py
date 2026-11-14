import numpy as np
import pytest

from lpswarm.alphabet import Alphabet
from lpswarm.oracle import (FAIL, NEAR_MISS, PASS, CoarseOracle, FullOracle, OracleConfig,
                            null_fpr_check)
from lpswarm.oracle.signals import Dictionary, NgramModel, index_of_coincidence
from lpswarm.textgen.synth import generate_cases, heldout_cases


def test_ic_values():
    rng = np.random.default_rng(0)
    assert abs(index_of_coincidence(rng.integers(0, 26, 20000), 26) - 1.0) < 0.05
    assert index_of_coincidence(np.zeros(50, dtype=int), 26) == pytest.approx(26.0)


def test_ngram_prefers_language(latin):
    from lpswarm.textgen.corpus import training_text
    arr = latin.encode(training_text())
    m = NgramModel.train(arr, 26, 3)
    eng = latin.encode("THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG")
    rnd = np.random.default_rng(1).integers(0, 26, len(eng))
    assert m.score(eng) > m.score(rnd) + 1.0


def test_dictionary_coverage(latin):
    d = Dictionary([latin.encode(w) for w in ["THE", "CAT", "SAT", "MAT"]])
    assert d.coverage(latin.encode("THECATSAT")) == 1.0
    assert d.coverage(latin.encode("XXTHEXX")) == pytest.approx(3 / 7)


def test_known_plaintext_passes(oracle, latin):
    cases = heldout_cases(["caesar"], [40, 100, 200], 5, seed=3)
    for c in cases:
        rep = oracle.score(c.plaintext, attempt_count=1000)
        assert rep.verdict == PASS, (c.length, rep.combined, rep.threshold)
        assert rep.attempt_count == 1000 and rep.alpha_eff == pytest.approx(0.01 / 1000)


def test_ciphertext_fails(oracle):
    for c in generate_cases(["vigenere", "substitution"], [60, 200], 5, seed=4):
        assert oracle.score(c.ciphertext).verdict in (FAIL, NEAR_MISS)


def test_threshold_tightens_with_attempts(oracle):
    t = [oracle.threshold(60, n) for n in (1, 10, 1000, 10 ** 6)]
    assert t == sorted(t) and t[-1] > t[0]


def test_nulls_fail_at_roughly_configured_rate(oracle):
    res = null_fpr_check(oracle, [40, 120], samples=1500, seed=99)
    for s in res["summary"]:
        assert s["within_tolerance"], s
    for r in res["rows"]:
        assert r["not_anticonservative"], r


def test_coarse_api_hides_numbers(oracle, latin):
    co = CoarseOracle(oracle)
    c = heldout_cases(["caesar"], [80], 1, seed=5)[0]
    assert co.judge(c.plaintext) == PASS
    assert co.judge(c.ciphertext) in (FAIL, NEAR_MISS)
    public = [a for a in dir(co) if not a.startswith("_")]
    assert public == ["judge"]


def test_rune_like_alphabet_oracle():
    from lpswarm.textgen.corpus import training_text
    a = Alphabet.rune_like(29, corpus=training_text())
    o = FullOracle(a, OracleConfig(null_samples=300))
    c = heldout_cases(["vigenere"], [80], 2, alphabet=a, seed=6)
    for case in c:
        assert o.score(case.plaintext, 100).verdict == PASS
        assert o.score(case.ciphertext, 1).verdict != PASS


def test_lm_slot_is_numeric_and_recorded(latin):
    o = FullOracle(latin, OracleConfig(null_samples=200), lm_scorer=lambda s: -1.5)
    c = heldout_cases(["caesar"], [60], 1, seed=7)[0]
    assert o.score(c.plaintext).lm_loglik == -1.5


def test_heldout_guard():
    import lpswarm.textgen.synth as synth
    # Simulate a non-validation caller.
    g = {"__name__": "lpswarm.swarm.generator", "synth": synth}
    with pytest.raises(PermissionError):
        exec("def f():\n    return synth.heldout_cases(['caesar'], [30], 1)\nf()", g)


def test_word_boundaries_from_text():
    from lpswarm.alphabet import Alphabet, word_spans
    a = Alphabet.latin26()
    b = []
    arr = a.encode("the cat\nsat • on  mat", boundaries=b)
    assert b == [3, 6, 9, 11] and word_spans(len(arr), b)[-1] == (11, 14)


def test_word_breaks_change_target_identity_and_null_fpr(oracle):
    from lpswarm.ledger import target_id_for
    from lpswarm.oracle import null_fpr_check
    c = heldout_cases(["caesar"], [40], 1, seed=8)[0]
    from lpswarm.textgen.synth import case_breaks
    b = case_breaks(c, oracle.alphabet)
    assert target_id_for(oracle.alphabet, c.ciphertext) != target_id_for(oracle.alphabet, c.ciphertext, b)
    rep = oracle.score(c.plaintext, attempt_count=1000, breaks=b)
    assert rep.passed and rep.word_score is not None
    res = null_fpr_check(oracle, [40], samples=600, seed=5, breaks_by_length={40: b})
    assert all(r["not_anticonservative"] for r in res["rows"])

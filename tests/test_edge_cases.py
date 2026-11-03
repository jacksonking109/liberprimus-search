"""Regression tests for edge cases found in review."""
import json
import warnings

import numpy as np
import pytest

from lpswarm.alphabet import Alphabet, get_alphabet
from lpswarm.ciphers import get_family
from lpswarm.executor import EnumeratedKeys, Executor, ExplicitKeys, Target, final_check
from lpswarm.ledger import Ledger, canonical_json, dedupe_hash
from lpswarm.oracle import FullOracle, OracleConfig
from lpswarm.textgen.synth import heldout_cases


# ------------------------------------------------------------------ alphabet
def test_encode_does_not_drift_on_length_changing_case():
    a = Alphabet.latin26()
    assert a.decode(a.encode("ßABCDEFGH")) == "ABCDEFGH"
    assert a.decode(a.encode("ﬁ ﬂ ABCDEFGH")) == "ABCDEFGH"
    skipped = []
    a.encode("aßb", skipped=skipped)
    assert skipped == ["ß"]


def test_alphabet_conflicts_raise():
    with pytest.raises(ValueError, match="duplicate glyphs"):
        Alphabet.from_tokens("x", ["A", "B"], ["q", "q"])
    with pytest.raises(ValueError, match="non-empty"):
        Alphabet.from_tokens("x", ["A", ""])
    with pytest.raises(ValueError, match="also the token"):
        Alphabet.from_tokens("x", ["A", "B"], ["B", "C"])
    with pytest.raises(ValueError, match="maps to both"):
        Alphabet.from_tokens("x", ["A", "B"], aliases={"A": "B"})
    with pytest.raises(ValueError, match="not a token"):
        Alphabet.from_tokens("x", ["A", "B"], aliases={"Q": "Z"})


def test_exact_glyph_beats_case_folded_token():
    a = Alphabet.from_tokens("x", ["A", "B"], ["b", "a"])
    assert a.encode("b").tolist() == [0]   # glyph of symbol 0
    assert a.encode("B").tolist() == [1]   # token of symbol 1


def test_alphabet_json_with_bom_and_errors(tmp_path):
    p = tmp_path / "a.json"
    p.write_bytes(b"\xef\xbb\xbf" + json.dumps({"tokens": ["A", "B", "C"]}).encode())
    assert Alphabet.from_json(p).size == 3
    q = tmp_path / "b.json"
    q.write_text('{"glyphs": ["x"]}', encoding="utf-8")
    with pytest.raises(ValueError, match="tokens"):
        Alphabet.from_json(q)
    r = tmp_path / "c.json"
    r.write_bytes("{\"tokens\": [\"\xe9\"]}".encode("cp1252"))
    with pytest.raises(ValueError, match="not UTF-8"):
        Alphabet.from_json(r)
    u = tmp_path / "d.json"
    u.write_text(json.dumps({"tokens": ["A", "B"]}), encoding="utf-16")
    assert Alphabet.from_json(u).size == 2


def test_get_alphabet_specs(tmp_path):
    assert get_alphabet("rune_like30").size == 30
    assert Alphabet.rune_like(90, extra_tokens=[f"X{i}" for i in range(64)]).size == 90
    with pytest.raises(ValueError, match="unknown alphabet"):
        get_alphabet("rune_like_x.json")


# ------------------------------------------------------------------- ciphers
def test_cipher_key_validation():
    pt = np.arange(10, dtype=np.int16) % 26
    for fam in ("vigenere", "autokey"):
        with pytest.raises(ValueError):
            get_family(fam).encrypt(pt, (), 26)
        with pytest.raises(ValueError):
            get_family(fam).decrypt(pt, (), 26)
    sub = get_family("substitution")
    with pytest.raises(ValueError, match="permutation"):
        sub.decrypt(pt, tuple([0] * 26), 26)
    with pytest.raises(ValueError, match="permutation"):
        sub.encrypt(pt, tuple(range(10)), 26)
    with pytest.raises(ValueError, match="permutation"):
        get_family("columnar").encrypt(pt, (0, 0, 1), 26)
    assert get_family("caesar").random_key(np.random.default_rng(0), 1) == 0


def test_running_key_bounds():
    rk = get_family("running_key")
    key = np.arange(50, dtype=np.int16) % 26
    assert rk.param_grid(60, key) == []                     # key shorter than text
    grid = rk.param_grid(40, key, offset_lo=-5, offset_hi=999, offset_step=0)
    assert [g["offset"] for g in grid] == list(range(0, 11))
    with pytest.raises(ValueError):
        rk.decrypt(np.zeros(40, dtype=np.int16), key, 26, offset=-1)
    with pytest.raises(ValueError):
        rk.random_params(np.random.default_rng(0), 60, key)


def test_params_canonical_hash():
    assert canonical_json({"offset": 1, "variant": "v"}) == canonical_json(
        {"variant": "v", "offset": 1.0})
    assert dedupe_hash("t", "f", {"offset": np.int64(3)}, "k") == dedupe_hash("t", "f",
                                                                             {"offset": 3}, "k")


# -------------------------------------------------------------------- oracle
def test_oracle_config_validation():
    for bad in ({"alpha": 0}, {"alpha": 1.5}, {"null_samples": 0}, {"order": 0},
                {"multiple_comparisons": "bh"}, {"null_types": ("nope",)},
                {"wrong_key_families": ("nope",)}, {"languages": ()}):
        with pytest.raises(ValueError):
            OracleConfig(**bad)


def test_large_alphabet_lowers_order():
    tokens = [chr(0x41 + i) for i in range(26)] + [f"Q{i}" for i in range(74)]  # N = 100
    a = Alphabet.from_tokens("big", tokens)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        o = FullOracle(a, OracleConfig(null_samples=100))
    assert o.order == 3 and any("lowered" in str(x.message) for x in w)


def test_length_limits(oracle):
    with pytest.raises(ValueError, match="too short"):
        oracle.calibrate(3)
    with pytest.raises(ValueError, match="too long"):
        oracle.calibrate(10_000_000)


def test_unreachable_flag(oracle):
    c = heldout_cases(["caesar"], [20], 1, seed=1)[0]
    rep = oracle.score(c.plaintext, attempt_count=10 ** 9)
    assert rep.unreachable and not rep.passed


def test_spending_mode_sums_below_alpha(latin):
    o = FullOracle(latin, OracleConfig(null_samples=200, multiple_comparisons="spending"))
    total = sum(o.alpha_eff(i) for i in range(1, 100_000))
    assert total < o.cfg.alpha


def test_supplied_training_text_builds_its_own_dictionary(latin):
    from lpswarm.textgen.corpus import training_text
    o = FullOracle(latin, OracleConfig(null_samples=100, languages=("klingon",)),
                   training_texts={"klingon": training_text()[:300_000]})
    assert o.training_sources["klingon"] == ["<supplied text>"]
    assert len(o._models["klingon"][2].words) > 1000


# ------------------------------------------------------- executor and ledger
def _tgt(latin, case):
    return Target(latin, case.ciphertext, f"t:{case.case_id}", is_synthetic=True)


def test_prior_pass_under_another_hypothesis_is_a_lead(latin, oracle):
    led = Ledger()
    case = heldout_cases(["caesar"], [60], 1, seed=11)[0]
    ex = Executor(led, oracle, stop_file=None)
    a = led.add_hypothesis("caesar", "A", "human", "human")
    ex.run(_tgt(latin, case), a, "caesar", EnumeratedKeys())
    b = led.add_hypothesis("caesar", "B", "baseline", "baseline")
    s = ex.run(_tgt(latin, case), b, "caesar", ExplicitKeys([case.key]))
    assert s.new_attempts == 0 and s.prior_passes == 1
    st = led.conn.execute("SELECT status FROM hypothesis WHERE id=?", (b,)).fetchone()[0]
    assert st == "lead"


def test_empty_search_space_is_not_ruled_out(latin, oracle):
    led = Ledger()
    case = heldout_cases(["caesar"], [60], 1, seed=12)[0]
    h = led.add_hypothesis("running_key", "short text", "human", "human")
    from lpswarm.executor import TextKeys
    s = Executor(led, oracle, stop_file=None).run(
        _tgt(latin, case), h, "running_key", TextKeys([("short", np.zeros(10, dtype=np.int16))]))
    assert s.stopped == "empty_search_space"
    st = led.conn.execute("SELECT status FROM hypothesis WHERE id=?", (h,)).fetchone()[0]
    assert st == "open"


def test_exception_mid_run_leaves_no_orphans(latin, oracle):
    led = Ledger()
    case = heldout_cases(["caesar"], [60], 1, seed=13)[0]
    h = led.add_hypothesis("caesar", "boom", "human", "human")

    class Boom(ExplicitKeys):
        def candidates(self, family, n, length):
            yield from super().candidates(family, n, length)
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        Executor(led, oracle, stop_file=None, commit_every=2).run(
            _tgt(latin, case), h, "caesar", Boom([1, 2, 3]))
    orphans = led.conn.execute("SELECT COUNT(*) FROM attempt a LEFT JOIN result r"
                               " ON r.attempt_id=a.id WHERE r.attempt_id IS NULL").fetchone()[0]
    assert orphans == 0
    st = led.conn.execute("SELECT status FROM hypothesis WHERE id=?", (h,)).fetchone()[0]
    assert st == "open"
    # The committed part is kept and the rest is redone on the next run.
    s = Executor(led, oracle, stop_file=None).run(_tgt(latin, case), h, "caesar",
                                                  ExplicitKeys([1, 2, 3]))
    assert s.new_attempts + s.skipped == 3


def test_key_candidates_are_family_scoped(latin, oracle):
    led = Ledger()
    case = heldout_cases(["columnar"], [40], 1, seed=14)[0]
    ex = Executor(led, oracle, stop_file=None)
    h1 = led.add_hypothesis("columnar", "c", "human", "human")
    ex.run(_tgt(latin, case), h1, "columnar", ExplicitKeys([(0, 1, 2)], derivation="orders"))
    h2 = led.add_hypothesis("vigenere", "v", "human", "human")
    ex.run(_tgt(latin, case), h2, "vigenere", ExplicitKeys([(0, 1, 2)], derivation="wordlist:x"),
           {"variants": ("vigenere",)})
    rows = led.conn.execute("SELECT a.cipher_family, k.derivation FROM attempt a JOIN key_candidate"
                            " k ON k.id=a.key_candidate_id ORDER BY a.id").fetchall()
    assert [tuple(r) for r in rows] == [("columnar", "orders"), ("vigenere", "wordlist:x")]


def test_rollback_clears_key_cache(latin):
    led = Ledger()
    with pytest.raises(RuntimeError):
        with led.transaction():
            led.key_candidate_id("h", "d")
            raise RuntimeError
    kid = led.key_candidate_id("h", "d")
    assert led.conn.execute("SELECT COUNT(*) FROM key_candidate WHERE id=?", (kid,)).fetchone()[0] == 1


def test_final_check_is_order_independent(latin, oracle):
    led = Ledger()
    case = heldout_cases(["vigenere"], [40], 1, seed=15)[0]
    tgt = _tgt(latin, case)
    ex = Executor(led, oracle, stop_file=None)
    h = led.add_hypothesis("vigenere", "true key first, then many decoys", "human", "human")
    words = [tuple(int(x) for x in np.random.default_rng(i).integers(0, 26, 6)) for i in range(800)]
    ex.run(tgt, h, "vigenere", ExplicitKeys([case.key] + words),
           {"variants": (case.params["variant"],)})
    rows = final_check(led, oracle, led.targets()[0]["id"])
    total = led.attempt_count(led.targets()[0]["id"])
    assert total == 801
    assert all(r["attempt_count_final"] == total for r in rows)
    thr_first = led.conn.execute("SELECT threshold FROM result ORDER BY attempt_id LIMIT 1").fetchone()[0]
    assert rows and rows[0]["threshold_final"] >= thr_first
    assert led.leads(final_only=True)[0]["passed_final"] == 1


def test_baseline_timeout_is_per_family(tmp_path, latin, oracle):
    from lpswarm.baseline import BaselineConfig, run_baseline
    led = Ledger()
    case = heldout_cases(["caesar"], [60], 1, seed=16)[0]
    res = run_baseline(_tgt(latin, case), led, oracle, ["KEY", "WORD"],
                       BaselineConfig(families=("caesar", "vigenere"), timeout_s=0.0,
                                      stop_file=None), progress=False)
    assert [s.family for s in res.summaries] == ["caesar", "vigenere"]


def test_user_corpus_overlapping_heldout_is_refused(tmp_path, monkeypatch):
    from lpswarm.textgen import corpus
    d = tmp_path / "corpora" / "english"
    d.mkdir(parents=True)
    (d / "leak.txt").write_text(corpus._heldout_text()[10_000:20_000], encoding="utf-8")
    (d / "ok.txt").write_text("An entirely new sentence about owls and lanterns. " * 50,
                              encoding="utf-8")
    monkeypatch.setenv("LPSWARM_DATA", str(tmp_path))
    with pytest.warns(UserWarning, match="overlaps the held-out"):
        src = corpus.training_sources()
    assert any(s.endswith("ok.txt") for s in src) and not any(s.endswith("leak.txt") for s in src)

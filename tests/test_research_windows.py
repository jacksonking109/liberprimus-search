"""Local-window search for an out-of-step prime stream: planted streams are found and verified on text the
selection never saw, noise is not, and the result is deterministic."""
import numpy as np
import pytest

from lpswarm import research_windows as W
from lpswarm.alphabet import get_alphabet
from lpswarm.oracle import FullOracle, OracleConfig
from lpswarm.research_packets import ALPHABET


@pytest.fixture(scope="module")
def env():
    alpha = get_alphabet(ALPHABET)
    return alpha, FullOracle(alpha, OracleConfig(null_samples=300)).bigram_table()


def test_stretches_are_the_longest_f_free_runs():
    x = np.array([5] * 70 + [0] + [6] * 90 + [0, 0] + [7] * 65 + [0] + [8] * 10)
    assert W.stretches(x) == [(71, 90), (0, 70), (163, 65)] or W.stretches(x)[0] == (71, 90)
    assert [s[1] for s in W.stretches(x, count=2)] == [90, 70]
    assert W.stretches(np.array([1, 2, 3, 0, 4, 5]), min_len=60) == []


def test_planted_prime_minus_one_stream_is_found_and_verified_outside_the_stretch(env):
    alpha, bigram = env
    controls = dict(W.make_controls(alpha))
    for name in ("English, prime-minus-one stream, F-skip", "same, plus one extra skipped index at 200"):
        r = W.section_search(controls[name], bigram, alpha, offsets=1200, null_reps=1)
        assert r["flag"], name
        best = max((s["stage2"]["verified"][0] for s in r["stretches"] if s["stage2"]["verified"]),
                   key=lambda v: v["stage2_z"])
        assert best["scale"] == 1 and best["constant"] == 28 and abs(best["global_offset"] - 500) <= 2
        assert best["orientation"] == "plain" and best["stage2_z"] >= W.FLAG_Z


def test_noise_is_not_flagged(env):
    alpha, bigram = env
    flags = 0
    for sd in range(5):
        noise = np.random.default_rng(100 + sd).integers(0, 29, size=800)
        flags += W.section_search(noise, bigram, alpha, offsets=1000, nstretch=2, null_reps=1)["flag"]
    assert flags == 0


def test_verification_ignores_the_stretch_it_was_selected_on(env):
    alpha, bigram = env
    plain = np.arange(60) % 29
    part = W._outside_mean(plain, bigram, 10, 20)
    assert np.isfinite(part)
    assert part != W._outside_mean(plain, bigram, 40, 10)           # a different stretch excludes different pairs
    ident = plain.copy()
    ident[11:29] = 0                                               # runes inside the stretch change nothing outside it
    assert W._outside_mean(ident, bigram, 10, 20) == pytest.approx(part)


def test_deterministic(env):
    alpha, bigram = env
    ct = dict(W.make_controls(alpha))["uniform noise"]
    a = W.section_search(ct, bigram, alpha, offsets=600, nstretch=1, null_reps=1)
    b = W.section_search(ct, bigram, alpha, offsets=600, nstretch=1, null_reps=1)
    for r in (a, b):
        r.pop("seconds")
    assert a == b


def test_module_imports_no_model_or_network_code():
    import subprocess
    import sys
    code = ("import sys, lpswarm.research_windows;"
            "print([k for k in sys.modules if k.startswith(('lpswarm.router','requests','httpx','urllib3','openai'))])")
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True,
                         env={**__import__("os").environ, "PYTHONPATH": "src"}, check=True)
    assert out.stdout.strip() == "[]"

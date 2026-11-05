"""Structure diagnostics: planted effects are found, absent effects are not, results are
deterministic and bounded, and nothing touches a model."""
import json
import subprocess
import sys

import numpy as np
import pytest

from lpswarm import research_structure as R
from lpswarm.alphabet import get_alphabet
from lpswarm.research_packets import ALPHABET
from lpswarm.textgen.synth import encoded_text

REPS = 59


@pytest.fixture(scope="module")
def english():
    alpha = get_alphabet(ALPHABET)
    return alpha, encoded_text(alpha, "english", "train")


def _sec(ct, breaks=()):
    return {0: {"ct": np.asarray(ct, dtype=np.int64), "breaks": list(breaks), "label": "t", "runes": len(ct)}}


def _no_repeats(n, seed):
    """Uniform random symbols except that a symbol never equals the previous one."""
    rng = np.random.default_rng(seed)
    x = np.empty(n, dtype=np.int64)
    x[0] = rng.integers(0, 29)
    for i in range(1, n):
        x[i] = (x[i - 1] + 1 + rng.integers(0, 28)) % 29
    return x


def test_iid_noise_is_rarely_flagged_and_feedback_is_flagged(english):
    alpha, text = english
    flags = {"mi": 0, "tr": 0, "trans": 0}
    seeds = (11, 12, 13, 14, 15, 16)
    for sd in seeds:                                    # each test has a 5% false-positive rate
        noise = _sec(np.random.default_rng(sd).integers(0, 29, size=1000))
        s = R.scans(noise, [0], reps=REPS)
        flags["mi"] += s["dependence_per_section"]["p_max_over_units"] <= 0.05
        flags["tr"] += s["transform_per_section"]["p_max_over_units"] <= 0.05
        flags["trans"] += R.diffs(noise, [0], reps=REPS)["transitions"]["p_chi2"] <= 0.05
    assert all(v <= 2 for v in flags.values()), flags            # 2 of 6 would already be unlikely
    rng = np.random.default_rng(1)
    fb = _sec(R._mechanism_ct("neighbour feedback (add)", text[3000:4000].astype(np.int64), alpha, rng))
    s_fb = R.scans(fb, [0], reps=REPS)
    assert s_fb["dependence_per_section"]["p_max_over_units"] <= 0.05
    assert s_fb["transform_per_section"]["p_max_over_units"] <= 0.05
    assert R.diffs(fb, [0], reps=REPS)["transitions"]["p_chi2"] <= 0.05


def test_progressive_key_makes_the_difference_histogram_non_uniform(english):
    alpha, text = english
    rng = np.random.default_rng(2)
    prog = _sec(R._mechanism_ct("progressive key (arithmetic)", text[2000:3200].astype(np.int64), alpha, rng))
    d = R.diffs(prog, [0], reps=REPS)
    assert d["differences"]["p_max_abs_z"] <= 0.05          # the key adds a constant to every difference
    # and the planted shift is where it should be: the English difference histogram shifted by the step
    obs = np.array([r["observed"] for r in d["differences"]["table"]])
    assert int(np.argmax(obs)) != 0


def test_a_repeat_shortage_alone_is_seen_by_diffs_and_removed_by_excluding_equal_pairs():
    x = _no_repeats(4000, 3)
    sec = _sec(x)
    d = R.diffs(sec, [0], reps=REPS)
    assert d["differences"]["p_max_abs_z"] <= 0.05
    assert d["differences"]["table"][0]["observed"] == 0
    # given the repeat count, nothing else in the differences
    assert d["differences"]["p_max_abs_z_non_zero_d_given_repeats"] > 0.05
    assert d["differences"]["p_chi2_d_excluding_zero"] > 0.05
    assert d["transitions"]["p_chi2_excluding_diagonal"] > 0.05
    all_pairs = R.scans(sec, [0], reps=REPS)
    no_equal = R.scans(sec, [0], reps=REPS, exclude_equal=True)
    assert all_pairs["dependence_per_section"]["p_max_over_units"] <= 0.05
    assert all_pairs["transform_per_section"]["p_max_over_units"] <= 0.05
    assert no_equal["exclude_equal_pairs"] is True
    assert no_equal["dependence_per_section"]["p_max_over_units"] > 0.05
    assert no_equal["transform_per_section"]["p_max_over_units"] > 0.05


def test_a_repeat_shortage_only_across_word_boundaries_is_attributed_to_that_stratum():
    rng = np.random.default_rng(4)
    n, w = 9000, 6
    x = rng.integers(0, 29, size=n).astype(np.int64)
    breaks = list(range(w, n, w))
    for b in breaks:                                         # never repeat across a boundary
        if x[b] == x[b - 1]:
            x[b] = (x[b] + 1 + rng.integers(0, 28)) % 29
    d = R.diffs(_sec(x, breaks), [0], reps=REPS)
    st = d["repeats_by_stratum"]
    assert st["across_boundary"]["observed"] == 0 and st["across_boundary"]["z"] < -4
    assert abs(st["within_word"]["z"]) < 3


def test_homogeneity_flags_a_section_with_a_different_distribution():
    rng = np.random.default_rng(5)
    secs = {i: {"ct": rng.integers(0, 29, size=800).astype(np.int64), "breaks": [], "label": str(i),
                "runes": 800} for i in range(4)}
    same = R.diffs(secs, list(secs), reps=REPS)
    assert same["homogeneity"]["frequencies"]["p"] > 0.01
    secs[3] = {**secs[3], "ct": (rng.integers(0, 12, size=800)).astype(np.int64)}      # only 12 symbols
    odd = R.diffs(secs, list(secs), reps=REPS)
    assert odd["homogeneity"]["frequencies"]["p"] <= 0.05
    z = {r["section"]: r["frequency_z"] for r in odd["homogeneity"]["per_section_z"]}
    assert z[3] == max(z.values())


def test_output_is_deterministic_and_the_time_cap_returns_partial_results():
    rng = np.random.default_rng(6)
    sec = _sec(rng.integers(0, 29, size=500))
    a = json.dumps(R._jsonable(R.scans(sec, [0], reps=REPS)), sort_keys=True)
    b = json.dumps(R._jsonable(R.scans(sec, [0], reps=REPS)), sort_keys=True)
    a = a.replace(a[a.index('"seconds"'):a.index('"seconds"') + 20], "")
    b = b.replace(b[b.index('"seconds"'):b.index('"seconds"') + 20], "")
    assert a == b
    capped = R.scans(sec, [0], reps=REPS, cap_s=0)
    assert capped["complete"] is False and "error" in capped
    capped_d = R.diffs(sec, [0], reps=REPS, cap_s=0)
    assert capped_d["complete"] is False and "error" in capped_d


def test_mutual_information_and_transform_ic_basics():
    J = np.eye(29) * 10                                      # c[i] == c[i-k] always
    assert R.mutual_information(J) == pytest.approx(np.log(29))
    assert R.mutual_information(np.ones((29, 29))) == pytest.approx(0.0)
    ic = R.transform_ic(J)                                   # T = c + r*c = (1+r)c: nonuniform except r=28 (T = 0)
    assert ic[27] == pytest.approx(29.0)                     # r = 28: T == 0 for every pair
    assert ic[0] == pytest.approx(1.0)                       # r = 1: T = 2c, uniform over residues


def test_power_table_has_a_false_positive_row_and_detects_feedback():
    p = R.power(reps=REPS, lengths=(534,), mechanisms=("iid noise", "neighbour feedback (add)"))
    rows = {r["mechanism"]: r for r in p["rows"]}
    assert rows["neighbour feedback (add)"]["detected_by"]
    assert len(rows["iid noise"]["detected_by"]) <= 2        # eight tests at 0.05, no correction
    assert p["complete"] is True and "SYNTHETIC" in p["label"]


def test_the_module_does_not_import_any_model_or_network_code():
    code = ("import sys, lpswarm.research_structure as m;"
            "bad=[k for k in sys.modules if k.startswith(('lpswarm.router','requests','httpx','urllib3','openai'))];"
            "print(bad)")
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True,
                         env={**__import__("os").environ, "PYTHONPATH": "src"}, check=True)
    assert out.stdout.strip() == "[]"

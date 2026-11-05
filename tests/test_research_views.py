"""Assumption-audit views: planted effects are found, absent ones are not, runs are deterministic and
bounded, and nothing touches a model."""
import json
import subprocess
import sys
import zlib

import numpy as np
import pytest

from lpswarm import research_views as V

N = 29
VALUES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103,
          107, 109]
SMALL = dict(offsets=700, scales=range(1, 29), seqs=("primes", "fibonacci"), replicates=1, stretch_reps=12)


@pytest.fixture(scope="module")
def english():
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET
    from lpswarm.textgen.synth import encoded_text
    alpha = get_alphabet(ALPHABET)
    return alpha, np.asarray(encoded_text(alpha, "english", "train"), dtype=np.int64)


def test_ic_helpers_and_flag_floor():
    assert V.ic_of(np.zeros(100, dtype=np.int64)) == pytest.approx(29.0)
    x = np.tile(np.arange(29), 10)
    assert V.ic_of(x) == pytest.approx(29 * (29 * 10 * 9) / (290 * 289))     # exactly uniform: just below 1
    assert V.longest_f_free(np.array([1, 2, 0, 3, 4, 5, 0, 6])) == (3, 3)


def test_sweep_finds_a_planted_prime_stream_in_any_language_and_not_noise(english):
    from lpswarm.programs.sequences import window
    alpha, text = english
    S = window("primes", 0, 400 + 600, N)
    zipf = 1.0 / np.arange(1, N + 1)
    zipf /= zipf.sum()
    pt = np.random.default_rng(2).choice(N, size=600, p=zipf)            # a "language" that is not English
    ct = (pt + 2 * S[345:945]) % N
    found = V.agnostic_section(ct, **SMALL)
    top = found["top"][0]
    assert found["flag"] and top["sequence"] == "primes" and top["scale"] in (2, 27) and top["offset"] == 345 \
        or found["best_ic"] > 2.0 and found["flag"]
    noise = V.agnostic_section(np.random.default_rng(3).integers(0, N, size=600), **SMALL)
    assert not noise["flag"] and noise["best_ic"] < V.FLAG_IC


def test_the_f_free_stretch_recovers_an_ambiguous_f_skip_stream(english):
    from lpswarm.programs.sequences import window
    alpha, text = english
    S = window("fibonacci", 0, 91 + 700, N)
    pt, ct, j = text[60000:60600], [], 0
    for v in pt:                                                          # F literal iff plaintext F, as on the real pages
        if v == 0:
            ct.append(0)
        else:
            ct.append((int(v) + 3 * int(S[91 + j])) % N)
            j += 1
    r = V.agnostic_section(np.array(ct), **SMALL)
    assert r["best_ic"] < V.FLAG_IC                                       # a fixed F treatment loses the alignment
    assert r["stretch"] and r["stretch"]["flag"] and r["flag"]            # the F-free stretch does not


def test_bytes_views_find_a_compressed_payload_and_not_noise(english):
    alpha, text = english
    data = zlib.compress(bytes(int(v) + 65 for v in text[:3000]), 9)
    v, digs = int.from_bytes(data, "big"), []
    while v:
        v, r = divmod(v, N)
        digs.append(r)
    runes = np.array(digs[::-1], dtype=np.int64)
    r = V.bytes_section(runes, reps=39)
    assert any(h["kind"] == "valid zlib stream" for h in r["hits"]["base 29, digits most significant first"])
    flagged = 0
    for sd in range(40, 46):                                              # each noise section has a 5% false-positive rate
        noise = V.bytes_section(np.random.default_rng(sd).integers(0, N, size=700), reps=39)
        assert sum(len(h) for h in noise["hits"].values()) == 0           # decoders and magic numbers: never
        flagged += noise["p_max_over_stats"] <= 0.05
    assert flagged <= 2
    lang = V.bytes_section(text[30000:30600], reps=39)                    # real language compresses: sensitivity check
    assert lang["p_max_over_stats"] <= 0.05


def test_decompressors_and_magic_numbers_have_no_false_positives_on_random_bytes():
    rng = np.random.default_rng(5)
    hits = sum(len(V.structure_hits(bytes(rng.integers(0, 256, size=400, dtype=np.uint8)))) for _ in range(200))
    assert hits == 0
    assert V.structure_hits(b"\x00\x00" + zlib.compress(b"hello hello hello hello"))[0] == \
        {"offset": 2, "kind": "valid zlib stream"}
    assert V.structure_hits(b"..\x89PNG" + b"." * 40)[0]["kind"] == "magic number: PNG"


def test_number_theory_helpers():
    assert [n for n in range(2, 30) if V.is_prime(n)] == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert V.is_prime(2 ** 61 - 1) and not V.is_prime(2 ** 61 + 1)
    assert V.is_square(144) and not V.is_square(145) and V.is_fibonacci(144) and not V.is_fibonacci(145)
    assert V.base29_value(np.array([1, 0, 0])) == 841 and V.base29_value(np.array([1, 0, 0]), msb=False) == 1


def test_words_as_numbers_flag_prime_words_and_not_random_words():
    c = V.number_controls(VALUES, reps=59)
    assert c["words that are primes written in base 29"]["p_max_over_readings"] <= 0.05
    assert c["words that are primes written in base 29"]["top"][0]["reading"].startswith("W1")
    assert c["words from random runes"]["p_max_over_readings"] > 0.05


def test_parse_units_splits_words_and_lines():
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET
    alpha = get_alphabet(ALPHABET)
    g = alpha.glyphs
    raw = g[1] + g[2] + g[3] + "•" + g[4] + "\n" + g[5] + g[6] + "•" + g[7] + g[8] + g[9] + "\n"
    flat, words, lines = V.parse_units(raw, alpha)
    assert flat.tolist() == [1, 2, 3, 4, 5, 6, 7, 8, 9] and words == [3, 1, 2, 3] and lines == [4, 5]


def test_sequence_fits_flag_polynomials_and_recurrences_not_noise():
    c = V.sequence_controls()
    assert c["cubic polynomial in position"]["finite_differences"]["flag"]
    assert c["cubic polynomial in position"]["recurrence_order_3"]["flag"]
    assert c["second-order recurrence (3, 5)"]["recurrence_order_2"]["flag"]
    assert not any(c["uniform random runes"][k]["flag"]
                   for k in ("finite_differences", "recurrence_order_2", "recurrence_order_3"))


def test_leave_one_out_z_is_calibrated_on_noise():
    rng = np.random.default_rng(6)
    flags = 0
    for _ in range(200):
        null = rng.normal(size=(1, 99))
        obs = rng.normal(size=1)
        z, zn = V._z_loo(obs, null)
        flags += int(abs(z[0]) >= np.sort(np.abs(zn[0]))[-5])             # obs among the top 5 of 100: 5% expected
    assert flags <= 20                                                    # 10 expected, generous bound


def test_output_is_deterministic_and_markdown_renders(english):
    alpha, text = english
    x = text[20000:20600]
    a = V.agnostic_section(x, **SMALL)
    b = V.agnostic_section(x, **SMALL)
    for r in (a, b):
        r.pop("seconds")
    assert json.dumps(V._jsonable(a), sort_keys=True) == json.dumps(V._jsonable(b), sort_keys=True)
    rep = {"agnostic": {"offsets": 700, "replicates": 1, "complete": True, "sections": {"1": a}, "controls": []}}
    assert "Decrypt, then index of coincidence" in V.to_markdown(rep)


def test_module_imports_no_model_or_network_code():
    code = ("import sys, lpswarm.research_views as m;"
            "print([k for k in sys.modules if k.startswith(('lpswarm.router','requests','httpx','urllib3','openai'))])")
    out = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True,
                         env={**__import__("os").environ, "PYTHONPATH": "src"}, check=True)
    assert out.stdout.strip() == "[]"


def test_derive_option_runs_the_sweep_on_differences(tmp_path):
    rc = V.main(["agnostic", "--derive", "diff", "--no-packets", "--sections", "13", "--offsets", "60",
                 "--replicates", "1", "--out", str(tmp_path)])
    assert rc == 0
    md = (tmp_path / "diagnostics_views.md").read_text(encoding="utf-8")
    assert "first differences" in md and "| 13 |" in md
    data = json.loads((tmp_path / "diagnostics_views.json").read_text(encoding="utf-8"))
    assert data["derive"] == "diff" and data["agnostic"]["sections"]["13"]["window"] == 332

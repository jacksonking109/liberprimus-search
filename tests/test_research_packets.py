"""Research packets (fixed proposal lists) and exploratory diagnostics."""
import json
import shlex
from pathlib import Path

import numpy as np
import pytest

from lpswarm import research_diagnostics as D
from lpswarm import research_packets as P
from lpswarm.cli import main
from lpswarm.ledger import Ledger

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def sections():
    return P.load_sections(indexes=[13, 24, 25, 16])


def test_packets_compile_have_exact_counts_and_are_stable(tmp_path, sections):
    a, b = tmp_path / "a", tmp_path / "b"
    res = {n: P.render_packet(n, a, sections) for n in P.PACKETS}
    res2 = {n: P.render_packet(n, b, sections) for n in P.PACKETS}
    assert {n: r["per_target"] for n, r in res.items()} == {"exp1_feedback": 261, "exp2_two_shear": 33,
                                                           "exp2b_all_shifts": 957,
                                                           "exp3_progressive": 4873}
    assert res["exp3_progressive"]["total"] == 4 * 4873            # 3 sequences x 2 combines x 28 x 29 + control
    assert res["exp1_feedback"]["total"] == 696 + 87            # Astra's 696 candidates + 87 controls
    assert res["exp2_two_shear"]["total"] == 96 + 3
    assert res["exp2b_all_shifts"]["total"] == 2784 + 87
    for n in P.PACKETS:
        assert res[n]["sha256"] == res2[n]["sha256"]            # deterministic
        assert (a / n / "proposals.json").read_bytes() == (b / n / "proposals.json").read_bytes()
        replies = json.loads((a / n / "proposals.json").read_text(encoding="utf-8"))
        assert all(len(json.loads(r)["proposals"]) <= P.PACKETS[n]["per_round"] for r in replies)
        assert len(replies) <= P.PACKETS[n]["rounds"]
        text = (a / n / "packet.md").read_text(encoding="utf-8")
        assert "Nothing has been run" in text and "Stop rule (literal)" in text
        assert "novelty is unknown" in text and res[n]["sha256"] in text
    assert "NO: needs separate approval" in (a / "exp2b_all_shifts" / "packet.md").read_text(encoding="utf-8")


def test_shear_matrices_have_determinant_one_and_both_orders():
    mats = P.shear_matrices()
    assert len(mats) == 32
    for name, (a, b, c, d) in mats:
        assert (a * d - b * c) % 29 == 1, name
    assert dict(mats)["UL a=2 t=1"] == [3, 2, 1, 1]               # Astra's worked example
    assert dict(mats)["LU a=2 t=1"] == [1, 2, 1, 3]


def test_no_candidate_is_a_duplicate_decryption(tmp_path, sections):
    r = P.render_packet("exp1_feedback", tmp_path, sections)
    for t, d in r["distinct"].items():
        assert d["distinct_decryptions"] == d["candidates"], t


def test_odd_length_sections_are_refused_for_the_hill_packet(tmp_path, sections):
    fake = {**sections, 24: {**sections[24], "runes": 533}}
    with pytest.raises(ValueError, match="odd length"):
        P.render_packet("exp2_two_shear", tmp_path, fake)


def _run_packet(tmp_path, monkeypatch, sections, name, section, expected):
    monkeypatch.chdir(ROOT)
    out = tmp_path / "packets"
    r = P.render_packet(name, out, sections)
    conf = tmp_path / "conf.toml"
    conf.write_text("[swarm]\nstop_on_pass = false\n[oracle]\nnull_samples = 200\n", encoding="utf-8")
    argv = shlex.split(r["command"])[1:]
    argv[argv.index("--sections") + 1] = str(section)             # one target keeps the test short
    assert main(argv + ["--config", str(conf), "--quiet"]) == 0
    with Ledger(out / name / "run" / "ledger.sqlite") as led:
        tid = led.conn.execute("SELECT id FROM target").fetchone()[0]
        n = led.attempt_count(tid)
    assert n == expected                                          # exactly the packet's proposals ran
    return out / name / "run"


def test_exp2_packet_runs_through_the_real_swarm_with_the_scripted_proposer(tmp_path, monkeypatch, sections):
    run = _run_packet(tmp_path, monkeypatch, sections, "exp2_two_shear", 24, 33)
    assert main(["coverage", "--ledger", str(run / "ledger.sqlite"), "--out", str(tmp_path / "cov")]) == 0
    # the swarm recorded what it was evaluated with, and coverage shows the ACTUAL configuration
    cov = json.loads((tmp_path / "cov" / "coverage.json").read_text(encoding="utf-8"))
    group = cov["sections"][0]["evaluator_groups"][0]
    assert group["oracle_config"]["null_samples"] == 200 and len(group["oracle_config_hash"]) == 64
    meta = cov["inputs"]["ledgers"][0]["run_meta"][0]
    assert meta["command"] == "swarm" and meta["caps"]["max_attempts"] == 40 and meta["caps"]["rounds"] == 2
    assert meta["models"]["generators"] == ["packet-exp2_two_shear"]
    assert meta["alphabet_sha256"] != "unknown" and meta["corpus_sha256"] != "unknown"


def test_exp1_packet_runs_through_the_real_swarm_with_the_scripted_proposer(tmp_path, monkeypatch, sections):
    _run_packet(tmp_path, monkeypatch, sections, "exp1_feedback", 13, 261)


# ------------------------------------------------------------------ diagnostics
def _zipf_text(rng, n):
    w = 1.0 / np.arange(1, 30) ** 1.3
    return rng.choice(29, size=n, p=w / w.sum())


def _fake_sections(planted_shared: bool):
    rng = np.random.default_rng(5)
    dev = _zipf_text(rng, 700)
    secs = {i: dev[(i % 3) * 100: (i % 3) * 100 + 300] for i in (3, 7, 9, 27)}
    secs[7] = dev
    keyA, keyB = rng.integers(0, 29, 400), rng.integers(0, 29, 400)
    for a, b, shared in ((10, 12, planted_shared), (17, 18, False), (24, 25, False)):
        P_, Q_ = _zipf_text(rng, 400), _zipf_text(rng, 400)
        K = rng.integers(0, 29, 400)
        secs[a] = (P_ + K) % 29
        secs[b] = (Q_ + (K if shared else rng.integers(0, 29, 400))) % 29
    return {i: {"ct": np.asarray(v, dtype=np.int64), "breaks": [], "label": f"fake{i}",
                "runes": len(v), "sha256": None, "clean": True} for i, v in secs.items()}


def test_keycancel_detects_a_planted_shared_key_and_not_independent_keys(monkeypatch):
    for planted, expect_small in ((True, True), (False, False)):
        fake = _fake_sections(planted)
        monkeypatch.setattr(D, "load_sections", lambda manifest=None, alphabet_path=None, indexes=None, f=fake:
                            {i: f[i] for i in (indexes or f)})
        rep = D.keycancel(reps=40, cap_s=60)
        best = max(rep["observed"], key=lambda o: o["statistic"])
        if expect_small:
            assert best["pair"] == [10, 12] and best["offset"] == 0
            assert rep["p_max_over_15"] <= 0.05
        else:
            assert rep["p_max_over_15"] > 0.05
        assert rep["statistic_evaluations"] == 15 + 40 * 15 and rep["complete"]
        assert rep["label"].startswith("EXPLORATORY")
        rep2 = D.keycancel(reps=40, cap_s=60)                      # deterministic
        rep.pop("seconds"), rep2.pop("seconds")
        assert rep == rep2
    shared = [d["statistic_at_offset_0"] for d in rep["development_controls"]["pairs"] if d["shared_key"]]
    indep = [d["statistic_at_offset_0"] for d in rep["development_controls"]["pairs"] if not d["shared_key"]]
    assert min(shared) > max(indep)                                # the statistic has power on dev data


def test_preflight_flags_a_planted_repeat_deficit_and_not_a_random_text(monkeypatch):
    rng = np.random.default_rng(9)
    plain = rng.integers(0, 29, 600)
    deficit = plain.copy()
    for i in range(1, len(deficit)):                                # no adjacent repeats at all
        while deficit[i] == deficit[i - 1]:
            deficit[i] = rng.integers(0, 29)
    for name, text, small in (("deficit", deficit, True), ("random", plain, False)):
        fake = {7: {"ct": text.astype(np.int64), "breaks": list(range(8, 600, 8)), "label": name,
                    "runes": 600, "sha256": None, "clean": True}}
        monkeypatch.setattr(D, "load_sections", lambda manifest=None, alphabet_path=None, indexes=None, f=fake: f)
        rep = D.preflight([7], reps=99, cap_s=60)
        assert rep["units"] == 24 and rep["shuffles_per_target"] == 99 and rep["complete"]
        assert (rep["p_max_over_all_units"] <= 0.05) == small
        assert D.to_markdown(rep).startswith("# Diagnostics: preflight")


def test_progressive_packet_counts_and_covers_planted_arithmetic_and_triangular_keys(tmp_path, sections):
    from lpswarm.alphabet import get_alphabet
    from lpswarm.programs import compile_spec, decrypt, encrypt, expand
    from lpswarm.textgen.synth import encoded_text
    replies, table = P.exp3_replies()
    assert len(replies) == 7 and sum(t["proposals"] for t in table) == 6 * 28 + 1
    assert all(len(json.loads(r)["proposals"]) <= 28 for r in replies)
    alpha = get_alphabet(P.ALPHABET)
    packet = [c for r in replies for p in json.loads(r)["proposals"]
              for c in expand(compile_spec(p["spec"], alpha), None)]
    assert len(packet) == 4873
    pt = encoded_text(alpha, "english", "train")[:300]
    for seq, scale, off, combine in (("naturals", 7, 5, "sub"), ("naturals", 28, 0, "sub"),
                                     ("triangular", 3, 11, "beaufort"), ("squares", 2, 20, "sub")):
        planted = compile_spec({"stream": {"kind": "sequence", "name": seq, "scale": scale,
                                           "offset": off, "add": 0}, "combine": combine}, alpha)
        ct = encrypt(pt, planted, alpha.size)
        assert any(np.array_equal(decrypt(ct, c, alpha.size), pt) for c in packet), (seq, scale, off)
    # an arithmetic key k = d*t + b for any b is a naturals proposal with offset b/d mod 29
    for d, b in ((4, 17), (13, 0), (27, 28)):
        planted = compile_spec({"stream": {"kind": "constant", "value": 0}, "combine": "sub"}, alpha)
        k = (d * np.arange(300) + b) % 29
        ct = (pt + k) % 29                                          # p = c - k
        assert any(np.array_equal(decrypt(ct, c, alpha.size), pt) for c in packet), (d, b)


def test_exp3_labels_beaufort_as_a_sign_convention_not_a_theory(tmp_path, sections):
    r = P.render_packet("exp3_progressive", tmp_path, sections)
    text = (tmp_path / "exp3_progressive" / "packet.md").read_text(encoding="utf-8")
    assert "reversed-alphabet form" in text and "not a claim about how the unsolved sections" in text
    assert "naturals, beaufort" not in text                       # round labels use the algebra instead
    assert "p = k - c (reversed-alphabet form)" in text
    assert r["per_target"] == 4873                                # specs and counts are unchanged
    replies = json.loads((tmp_path / "exp3_progressive" / "proposals.json").read_text(encoding="utf-8"))
    combines = {p["spec"]["combine"] for rr in replies for p in json.loads(rr)["proposals"]}
    assert combines == {"sub", "beaufort"}                        # the DSL keyword itself is untouched

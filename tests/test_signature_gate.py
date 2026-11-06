"""Signature gate: refuses programs that cannot produce the unsolved text's signature; lets through what it cannot judge."""
import json
from argparse import Namespace
from pathlib import Path

import numpy as np
import pytest

from lpswarm.alphabet import get_alphabet
from lpswarm.cli import _with_facts, main
from lpswarm.programs.spec import compile_spec
from lpswarm.research_packets import ALPHABET
from lpswarm.swarm import signature_gate as G

ROOT = Path(__file__).resolve().parent.parent
ALPHA = get_alphabet(ALPHABET)


def _profile(r1, rest=1.0, uni=1.0, diff=1.0):
    return {"ratio": np.array([r1] + [rest] * 7), "uni_ic": uni, "diff_ic": diff}


def test_judge_applies_wide_bands_and_names_the_miss():
    assert G.judge(_profile(0.2))[0] and G.judge(_profile(0.1))[0] and G.judge(_profile(0.38))[0]
    ok, why = G.judge(_profile(0.95))
    assert not ok and "0.95" in why and "0.19" in why
    assert not G.judge(_profile(0.2, rest=1.6))[0] and not G.judge(_profile(0.2, uni=1.8))[0] and not G.judge(_profile(0.2, diff=1.5))[0]


def test_a_plain_program_is_blocked_and_a_matching_profile_is_not():
    spec = compile_spec({"stream": {"kind": "constant", "value": 3}, "combine": "sub"}, ALPHA)
    blocked, why = G.gate_spec(spec, ALPHA)
    assert blocked and why.startswith("signature gate")                 # English through a shift: lag 1 about 0.6, IC 1.8
    assert G.gate_spec(spec, ALPHA, profile_fn=lambda m, a: _profile(0.2)) == (False, "")


def test_what_cannot_be_judged_is_let_through():
    window = compile_spec({"stream": {"kind": "constant", "value": 0}, "combine": "sub", "mix": {"kind": "window", "size": 3, "at": "before"}}, ALPHA)
    assert G.gate_spec(window, ALPHA) == (False, "")                    # a window mix has no inverse
    wide = compile_spec({"stream": {"kind": "sequence", "name": "primes"}, "combine": "sub", "offset_range": [0, 200]}, ALPHA)
    assert G.gate_spec(wide, ALPHA) == (False, "")                      # more ciphers than the gate evaluates


def test_the_closest_member_is_reported_for_a_small_expansion():
    spec = compile_spec({"stream": {"kind": "sequence", "name": "naturals", "scale": 1, "offset": 0}, "combine": "sub", "offset_range": [0, 3]}, ALPHA)
    blocked, why = G.gate_spec(spec, ALPHA)
    assert blocked and "closest of" in why


def test_with_facts_prepends_the_file_text(tmp_path):
    f = tmp_path / "facts.md"
    f.write_text("fact one\n", encoding="utf-8")
    assert _with_facts(Namespace(facts_file=str(f)), "results").startswith("ESTABLISHED FACTS")
    assert _with_facts(Namespace(facts_file=str(f)), "results").endswith("results")
    assert _with_facts(Namespace(facts_file=None), "results") == "results"


def test_the_swarm_refuses_gated_programs_before_the_oracle(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    reply = json.dumps({"proposals": [{"spec": {"stream": {"kind": "constant", "value": 3}, "combine": "sub"}, "why": "plain shift"},
                                      {"spec": {"stream": {"kind": "constant", "value": 5}, "combine": "sub"}, "why": "another shift"}]})
    models = tmp_path / "m.toml"
    models.write_text('[models.g]\nprovider = "scripted"\nmodel = "x"\nroles = ["proposer"]\n' f"replies = [{json.dumps(reply)}]\n", encoding="utf-8")
    conf = tmp_path / "c.toml"
    conf.write_text("[swarm]\nstop_on_pass = false\n[oracle]\nnull_samples = 100\n", encoding="utf-8")
    rep = tmp_path / "rep"
    rc = main(["swarm", "--manifest", "data/lp/manifest.json", "--alphabet", "data/alphabet/gematria_primus.json", "--sections", "13", "--generators", "g",
               "--models", str(models), "--spend-ledger", str(tmp_path / "s.sqlite"), "--rounds", "1", "--per-round", "8",
               "--ledger", str(tmp_path / "l.sqlite"), "--report-dir", str(rep), "--config", str(conf), "--quiet",
               "--signature-gate", "--facts-file", "config/briefs/lp2_signature.md"])
    assert rc == 0
    g = json.loads((rep / "report.json").read_text(encoding="utf-8"))["targets"][0]["generators"]["g"]
    assert g["proposals"] == 2 and g["gated"] == 2 and g["attempts"] == 0 and g["invalid"] == 0
    assert any(k.startswith("signature gate") for k in g["invalid_reasons"])

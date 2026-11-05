"""Invalid proposals are counted by reason and kept in report.json / report.md."""
import json
from pathlib import Path

from lpswarm.cli import main
from lpswarm.swarm.loop import GeneratorStats, normalise_reason

ROOT = Path(__file__).resolve().parent.parent


def test_normalise_groups_numbers_quotes_and_lists():
    a = normalise_reason("unknown stream fields ['foo'] for kind constant")
    b = normalise_reason("unknown stream fields ['bar', 'baz'] for kind constant")
    assert a == b
    assert normalise_reason("proposal expands to 12000 ciphers; the limit is 5000") == \
        normalise_reason("proposal expands to 7000 ciphers; the limit is 5000")
    assert normalise_reason("") == "(empty)"


def test_reason_table_is_capped_and_counts_add_up():
    gs = GeneratorStats("m")
    for i in range(100):
        gs.note_invalid(f"weird problem number word{i}x{'y' * i} is bad")   # many distinct reasons
    assert len(gs.invalid_reasons) <= 41                                     # 40 keys + "(other reasons)"
    assert sum(c for c, _ in gs.invalid_reasons.values()) == 100


def test_swarm_records_why_proposals_were_invalid(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    good = {"spec": {"stream": {"kind": "constant", "value": 3}, "combine": "sub"}, "why": "ok"}
    bad_field1 = {"spec": {"stream": {"kind": "constant", "value": 1, "bogus": 2}}, "why": "x"}
    bad_field2 = {"spec": {"stream": {"kind": "constant", "value": 2, "other": 1}}, "why": "x"}
    bad_seq = {"spec": {"stream": {"kind": "sequence", "name": "nonesuch"}}, "why": "x"}
    bad_range = {"spec": {"stream": {"kind": "sequence", "name": "primes"}, "offset_range": [10, 5]}, "why": "x"}
    reply = json.dumps({"proposals": [good, bad_field1, bad_field2, bad_seq, bad_range]})
    models = tmp_path / "m.toml"
    models.write_text('[models.bad]\nprovider = "scripted"\nmodel = "x"\nroles = ["proposer"]\n'
                      f"replies = [{json.dumps(reply)}]\n", encoding="utf-8")
    conf = tmp_path / "c.toml"
    conf.write_text("[swarm]\nstop_on_pass = false\n[oracle]\nnull_samples = 100\n", encoding="utf-8")
    rep = tmp_path / "rep"
    rc = main(["swarm", "--manifest", "data/lp/manifest.json", "--alphabet",
               "data/alphabet/gematria_primus.json", "--sections", "13", "--generators", "bad",
               "--models", str(models), "--spend-ledger", str(tmp_path / "s.sqlite"), "--rounds", "1",
               "--per-round", "8", "--ledger", str(tmp_path / "l.sqlite"), "--report-dir", str(rep),
               "--config", str(conf), "--quiet"])
    assert rc == 0
    data = json.loads((rep / "report.json").read_text(encoding="utf-8"))
    g = data["targets"][0]["generators"]["bad"]
    assert g["proposals"] == 5 and g["invalid"] == 4
    reasons = g["invalid_reasons"]
    assert sum(c for c, _ in reasons.values()) == 4
    fields = [v for k, v in reasons.items() if k.startswith("unknown stream fields")]
    assert len(fields) == 1 and fields[0][0] == 2                           # grouped despite different names
    md = (rep / "report.md").read_text(encoding="utf-8")
    assert "Invalid proposals by reason (bad" in md and "unknown stream fields" in md

import json
import sqlite3

import pytest

from lpswarm.cli import main


def test_validate_quick_writes_reports(tmp_path, capsys):
    out = tmp_path / "rep"
    rc = main(["validate", "--quick", "--quiet", "--families", "caesar,vigenere,columnar",
               "--lengths", "40,100", "--out", str(out)])
    assert rc == 0
    for name in ("validation.md", "validation.csv", "null_fpr.csv", "validation.json",
                 "validation_cases.csv"):
        assert (out / name).exists(), name
    res = json.loads((out / "validation.json").read_text(encoding="utf-8"))
    rec = {(r["family"], r["length"]): r["recall"] for r in res["table"]}
    assert rec[("caesar", 100)] == 1.0 and rec[("vigenere", 100)] == 1.0
    md = (out / "validation.md").read_text(encoding="utf-8")
    assert "Null calibration overall: PASS" in md
    # Re-running recreates the validation ledger instead of appending to it.
    main(["validate", "--quick", "--quiet", "--families", "caesar", "--lengths", "40",
          "--out", str(out)])
    n = sqlite3.connect(out / "validation.sqlite").execute("SELECT COUNT(*) FROM hypothesis").fetchone()[0]
    assert n == 2


def test_baseline_demo_is_idempotent(tmp_path, capsys):
    db = tmp_path / "demo.sqlite"
    args = ["baseline", "--demo", "caesar:60", "--ledger", str(db), "--words", "300",
            "--families", "caesar,vigenere,columnar", "--columnar-max-width", "5", "--quiet"]
    assert main(args) == 0
    first = capsys.readouterr().out
    assert "pass" in first
    c = sqlite3.connect(db)
    n1 = c.execute("SELECT COUNT(*) FROM attempt").fetchone()[0]
    c.close()
    assert main(args) == 0
    c = sqlite3.connect(db)
    assert c.execute("SELECT COUNT(*) FROM attempt").fetchone()[0] == n1
    assert c.execute("SELECT COUNT(*) FROM result").fetchone()[0] == n1
    c.close()
    assert main(["ruled-out", "--ledger", str(db)]) == 0
    assert main(["leads", "--ledger", str(db), "--json"]) == 0


def test_baseline_ciphertext_file_and_alphabet_json(tmp_path, capsys):
    from lpswarm.alphabet import Alphabet
    from lpswarm.ciphers import get_family
    a = Alphabet.latin26()
    pt = a.encode("IT WAS THE BEST OF TIMES IT WAS THE WORST OF TIMES IT WAS THE AGE OF WISDOM")
    ct = get_family("caesar").encrypt(pt, 7, 26)
    f = tmp_path / "page.txt"
    f.write_text(a.decode(ct), encoding="utf-8")
    alpha = tmp_path / "alpha.json"
    alpha.write_text(json.dumps(a.to_json()), encoding="utf-8")
    db = tmp_path / "lp.sqlite"
    assert main(["baseline", "--ciphertext", str(f), "--alphabet", str(alpha), "--ledger", str(db),
                 "--families", "caesar", "--quiet"]) == 0
    out = capsys.readouterr().out
    assert "ITWASTHEBESTOFTIMES" in out


def test_cli_errors(tmp_path):
    with pytest.raises(SystemExit):
        main(["baseline", "--ledger", str(tmp_path / "x.sqlite")])
    with pytest.raises(SystemExit):
        main(["ruled-out", "--ledger", str(tmp_path / "missing.sqlite")])


def test_no_network_imports_in_package():
    import pathlib
    import re
    root = pathlib.Path(__file__).resolve().parent.parent / "src" / "lpswarm"
    pat = re.compile(r"^\s*(import|from)\s+(urllib|http|socket|requests|httpx|ssl)\b", re.M)
    offenders = [p.name for p in root.rglob("*.py") if pat.search(p.read_text(encoding="utf-8"))]
    assert offenders == []


def test_model_config_parses_without_env():
    import pathlib
    from lpswarm.router import NullRouter, Role, load_model_specs
    p = pathlib.Path(__file__).resolve().parent.parent / "config" / "models.example.toml"
    specs = {s.name: s for s in load_model_specs(p)}
    assert specs["deepseek"].api_key_env == "DEEPSEEK_API_KEY"
    assert Role.WEIGHTING in specs["granite-tiny"].roles
    with pytest.raises(NotImplementedError):
        NullRouter().propose(Role.PROPOSER, {})

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from lpswarm.cli import main
from lpswarm.doctor import FAIL, OK, WARN, run_checks


class _Tags(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        data = json.dumps({"models": [{"name": "qwen3:14b"}, {"name": "granite3.3:2b"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


@pytest.fixture()
def ollama_stub():
    srv = HTTPServer(("127.0.0.1", 0), _Tags)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def _cfg(tmp_path, endpoint, extra=""):
    p = tmp_path / "models.toml"
    p.write_text(f"""
[models.qwen]
provider = "ollama"
endpoint = "{endpoint}"
model = "qwen3:14b"
roles = ["proposer"]

[models.granite]
provider = "ollama"
endpoint = "{endpoint}"
model = "granite3.3:2b"
roles = ["weighting"]

[models.missing]
provider = "ollama"
endpoint = "{endpoint}"
model = "gemma3:12b"

[models.api]
provider = "openai_compatible"
endpoint = "https://example.invalid"
model = "x"
api_key_env = "LPSWARM_DOCTOR_TEST_KEY"
max_usd = 1.0
{extra}
""", encoding="utf-8")
    return str(p)


def _by_name(checks):
    return {c.name: c for c in checks}


def test_doctor_reports_models(tmp_path, ollama_stub, monkeypatch):
    monkeypatch.delenv("LPSWARM_DOCTOR_TEST_KEY", raising=False)
    checks = _by_name(run_checks(_cfg(tmp_path, ollama_stub)))
    assert checks["model qwen"].status == OK
    assert checks["model granite"].status == OK
    assert checks["model missing"].status == FAIL and "gemma3:12b" in checks["model missing"].detail
    assert checks["model api"].status == WARN and "not set" in checks["model api"].detail
    assert "ranker" not in checks  # granite has the weighting role


def test_doctor_never_prints_key_and_flags_zero_prices(tmp_path, ollama_stub, monkeypatch, capsys):
    monkeypatch.setenv("LPSWARM_DOCTOR_TEST_KEY", "sk-doctor-secret")
    checks = _by_name(run_checks(_cfg(tmp_path, ollama_stub)))
    assert checks["model api"].status == WARN and "prices are 0" in checks["model api"].detail
    rc = main(["doctor", "--models", _cfg(tmp_path, ollama_stub)])
    out = capsys.readouterr().out
    assert rc == 1 and "sk-doctor-secret" not in out   # FAIL from the missing gemma tag


def test_doctor_unreachable_ollama_is_reported_not_raised(tmp_path):
    checks = _by_name(run_checks(_cfg(tmp_path, "http://127.0.0.1:9")))
    assert checks["model qwen"].status == FAIL and "not reachable" in checks["model qwen"].detail


def test_doctor_bad_config(tmp_path):
    p = tmp_path / "bad.toml"
    p.write_text("[models.x]\nprovider = \"ollama\"\n", encoding="utf-8")
    checks = _by_name(run_checks(str(p)))
    assert checks["models config"].status == FAIL


def test_doctor_ping_scripted(tmp_path):
    p = tmp_path / "dry.toml"
    p.write_text('[models.dry]\nprovider = "scripted"\nmodel = "dry"\nroles = ["proposer"]\n'
                 'replies = ["{\\"ok\\": true}"]\n', encoding="utf-8")
    spend = tmp_path / "spend.sqlite"
    checks = _by_name(run_checks(str(p), ping=True, ledgers=[str(spend)]))
    assert checks["ping dry"].status == OK
    import sqlite3
    assert sqlite3.connect(spend).execute("SELECT COUNT(*) FROM budget_event").fetchone()[0] == 1

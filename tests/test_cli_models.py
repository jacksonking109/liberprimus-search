"""Claude Code / Codex subscription connectors, usage limits and pauses (with fake CLIs)."""
import json
import os
import sys
import time
from pathlib import Path

import pytest

from lpswarm.ledger import Ledger
from lpswarm.router import ModelSpec, RateLimited, Role, Router, ScriptedAdapter
from lpswarm.router.cli_adapters import CLILimitError, ClaudeCodeAdapter, CodexAdapter
from lpswarm.router.limits import looks_like_limit, parse_resume_at

FAKE = r'''
import json, os, sys, time
log = os.environ["FAKE_LOG"]
mode = os.environ.get("FAKE_MODE", "ok")
argv = sys.argv[1:]
stdin = sys.stdin.buffer.read().decode("utf-8")
rec = {"argv": argv, "cwd": os.getcwd(), "stdin": stdin,
       "has_anthropic_key": "ANTHROPIC_API_KEY" in os.environ,
       "has_openai_key": "OPENAI_API_KEY" in os.environ}
if "--system-prompt-file" in argv:
    rec["system"] = open(argv[argv.index("--system-prompt-file") + 1], encoding="utf-8").read()
with open(log, "a", encoding="utf-8") as f:
    f.write(json.dumps(rec) + "\n")
kind = os.environ["FAKE_KIND"]
if argv == ["--version"]:
    print(kind + " 9.9.9"); sys.exit(0)
if kind == "claude":
    if mode == "ok":
        print(json.dumps({"type": "result", "is_error": False, "result": "REPLY:" + stdin[:20],
                          "usage": {"input_tokens": 10, "cache_read_input_tokens": 5, "output_tokens": 7},
                          "total_cost_usd": 0.0123}))
    elif mode == "limit_ts":
        print(json.dumps({"type": "result", "is_error": True,
                          "result": "Claude AI usage limit reached|" + os.environ["FAKE_TS"]})); sys.exit(1)
    elif mode == "limit_text":
        print(json.dumps({"type": "result", "is_error": True,
                          "result": "You've hit your limit - resets 3pm"})); sys.exit(1)
    elif mode == "trailing":
        print(json.dumps({"type": "result", "is_error": False, "result": "OK-REPLY", "usage": {}}))
        print("Update available: run claude update")
    elif mode == "limit_not_error":
        print(json.dumps({"type": "result", "is_error": False,
                          "result": "Claude AI usage limit reached|" + os.environ["FAKE_TS"]}))
    elif mode == "other_error_429_stderr":
        sys.stderr.write("warning: upstream returned 429 once, retried\n")
        print(json.dumps({"type": "result", "is_error": True, "result": "Invalid model name"})); sys.exit(1)
    elif mode == "sleep":
        import subprocess
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        open(os.environ["FAKE_CHILD"], "w").write(str(child.pid))
        time.sleep(60)
    else:
        sys.stderr.write("boom"); sys.exit(2)
else:
    out = argv[argv.index("-o") + 1]
    if mode == "ok":
        print(json.dumps({"type": "thread.started", "session": {"model": os.environ.get("FAKE_MODEL", "")}}))
        print(json.dumps({"type": "turn.completed", "usage": {"input_tokens": 100, "output_tokens": 20}}))
        open(out, "w", encoding="utf-8").write("CODEX:" + stdin[-10:])
    elif mode == "limit":
        print(json.dumps({"type": "error", "message": "You've hit your usage limit. Try again in 2 hours."}))
        sys.exit(1)
    else:
        sys.exit(3)
'''


def _fake_exe(tmp_path: Path, name: str) -> str:
    script = tmp_path / f"fake_{name}.py"
    script.write_text(FAKE, encoding="utf-8")
    if os.name == "nt":
        exe = tmp_path / f"{name}.cmd"
        exe.write_text(f'@"{sys.executable}" "{script}" %*\n', encoding="utf-8")
    else:
        exe = tmp_path / name
        exe.write_text(f"#!{sys.executable}\n" + FAKE, encoding="utf-8")
        exe.chmod(0o755)
    return str(exe)


@pytest.fixture()
def fake(tmp_path, monkeypatch):
    log = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_LOG", str(log))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-should-be-removed")
    monkeypatch.setenv("OPENAI_API_KEY", "test-should-be-removed")

    def calls():
        return [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
    return {"claude": _fake_exe(tmp_path, "claude"), "codex": _fake_exe(tmp_path, "codex"),
            "calls": calls, "repo": os.getcwd()}


MSGS = [{"role": "system", "content": "SYSTEM RULES"}, {"role": "user", "content": "hello there"}]


def test_claude_code_adapter_isolated_and_plan_billed(fake, monkeypatch):
    monkeypatch.setenv("FAKE_KIND", "claude")
    c = ClaudeCodeAdapter("sonnet", exe=fake["claude"]).complete(MSGS)
    assert c.text == "REPLY:hello there" and (c.tokens_in, c.tokens_out) == (15, 7) and c.usd == 0.0
    rec = fake["calls"]()[-1]
    a = rec["argv"]
    assert a[:3] == ["-p", "--output-format", "json"]
    assert a[a.index("--tools") + 1] == "" and a[a.index("--max-turns") + 1] == "1"
    for flag in ("--no-session-persistence", "--strict-mcp-config", "--disable-slash-commands"):
        assert flag in a
    assert a[a.index("--permission-mode") + 1] == "dontAsk" and a[a.index("--model") + 1] == "sonnet"
    assert rec["system"] == "SYSTEM RULES" and rec["stdin"] == "hello there"
    assert not rec["has_anthropic_key"]                       # plan, never API billing
    assert Path(rec["cwd"]).resolve() != Path(fake["repo"]).resolve()
    assert not Path(rec["cwd"]).exists()                      # temp folder removed afterwards


def test_codex_adapter_read_only_and_plan_billed(fake, monkeypatch):
    monkeypatch.setenv("FAKE_KIND", "codex")
    c = CodexAdapter("", exe=fake["codex"]).complete(MSGS)
    assert c.text == "CODEX:ello there" and (c.tokens_in, c.tokens_out) == (100, 20)
    rec = fake["calls"]()[-1]
    a = rec["argv"]
    assert a[0] == "exec" and a[a.index("--sandbox") + 1] == "read-only" and a[-1] == "-"
    for flag in ("--ephemeral", "--skip-git-repo-check", "--json"):
        assert flag in a
    assert rec["stdin"].startswith("SYSTEM RULES") and not rec["has_openai_key"]
    assert not Path(rec["cwd"]).exists()


def test_limit_detection_and_router_pause(fake, monkeypatch):
    monkeypatch.setenv("FAKE_KIND", "claude")
    ts = int(time.time()) + 3600
    monkeypatch.setenv("FAKE_MODE", "limit_ts")
    monkeypatch.setenv("FAKE_TS", str(ts))
    with pytest.raises(CLILimitError) as ei:
        ClaudeCodeAdapter("", exe=fake["claude"]).complete(MSGS)
    assert ei.value.resume_at == ts and ei.value.parsed
    led = Ledger()
    spec = ModelSpec("cc", "claude_code", "", (Role.PROPOSER,), extra={"exe": fake["claude"]})
    r = Router([spec], ledger=led)
    with pytest.raises(RateLimited) as ei2:
        r.complete("cc", MSGS, role="proposer")
    assert ei2.value.resume_at == ts
    n = len(fake["calls"]())
    monkeypatch.setenv("FAKE_MODE", "ok")
    with pytest.raises(RateLimited):                          # paused: the CLI is not even called
        r.complete("cc", MSGS, role="proposer")
    assert len(fake["calls"]()) == n
    assert r.window_status("cc")["paused_until"] == ts


def test_codex_limit_try_again_in(fake, monkeypatch):
    monkeypatch.setenv("FAKE_KIND", "codex")
    monkeypatch.setenv("FAKE_MODE", "limit")
    t = time.time()
    with pytest.raises(CLILimitError) as ei:
        CodexAdapter("", exe=fake["codex"]).complete(MSGS)
    assert abs(ei.value.resume_at - (t + 7200)) < 60


def test_other_cli_errors_are_not_limits(fake, monkeypatch):
    from lpswarm.router import AdapterError
    monkeypatch.setenv("FAKE_KIND", "claude")
    monkeypatch.setenv("FAKE_MODE", "error")
    with pytest.raises(AdapterError) as ei:
        ClaudeCodeAdapter("", exe=fake["claude"]).complete(MSGS)
    assert not isinstance(ei.value, CLILimitError)


def test_missing_cli_is_clear_error():
    from lpswarm.router import AdapterError
    with pytest.raises(AdapterError, match="not found"):
        ClaudeCodeAdapter("", exe="definitely-not-installed-xyz").complete(MSGS)


def test_parse_resume_at():
    now = 1_800_000_000.0
    assert parse_resume_at("limit reached|1800003600", now) == (1800003600.0, True)
    assert parse_resume_at("Try again in 90 minutes", now) == (now + 5400, True)
    assert parse_resume_at("try again in 2h", now) == (now + 7200, True)
    at, ok = parse_resume_at("5-hour limit reached - resets 3pm", now)
    assert ok and now < at <= now + 86400
    assert parse_resume_at("limit reached", now, 600) == (now + 600, False)
    assert looks_like_limit("You've hit your usage limit") and not looks_like_limit("syntax error")


def test_window_cap_pauses_until_oldest_call_ages_out():
    led = Ledger()
    spec = ModelSpec("m", "scripted", "m", (Role.PROPOSER,),
                     extra={"max_calls_per_window": 2, "window_hours": 5})
    r = Router([spec], ledger=led, adapters={"m": ScriptedAdapter("m", ["x"])})
    r.complete("m", [], role="proposer")
    r.complete("m", [], role="proposer")
    with pytest.raises(RateLimited) as ei:
        r.complete("m", [], role="proposer")
    assert 5 * 3600 - 60 < ei.value.resume_at - time.time() <= 5 * 3600 + 10
    assert "local cap" in ei.value.reason
    with pytest.raises(ValueError, match="ledger"):
        Router([spec], adapters={"m": ScriptedAdapter("m", ["x"])})


class _LimitedOnce:
    """Adapter: first call hits a usage limit that resets in `secs`, then replies."""

    def __init__(self, secs, reply):
        self.secs, self.reply, self.calls = secs, reply, 0

    def complete(self, messages, temperature=0.7, max_tokens=2048):
        self.calls += 1
        if self.calls == 1:
            raise CLILimitError("usage limit", time.time() + self.secs, True)
        from lpswarm.router import Completion
        return Completion(self.reply, "m")


def test_swarm_waits_for_reset_and_does_not_lose_the_round(oracle):
    from lpswarm.alphabet import Alphabet
    from lpswarm.executor import Target
    from lpswarm.swarm import LLMGenerator, SwarmConfig, run_swarm
    from lpswarm.textgen.synth import generate_case
    a = Alphabet.latin26()
    case = generate_case("caesar", 60, seed=3)
    reply = json.dumps({"proposals": [{"spec": {"stream": {"kind": "constant", "value": 1}}}]})
    ad = _LimitedOnce(1.5, reply)
    led = Ledger()
    r = Router([ModelSpec("m", "scripted", "m", (Role.PROPOSER,))], ledger=led, adapters={"m": ad})
    t0 = time.monotonic()
    res = run_swarm(Target(a, case.ciphertext, "w", is_synthetic=True), led, oracle,
                    [LLMGenerator(r, "m")], SwarmConfig(rounds=2, per_round=1, stop_file=None,
                                                         stop_on_pass=False), progress=False)
    assert time.monotonic() - t0 >= 1.0
    assert ad.calls == 3 and res.stats["m"].proposals == 2 and res.rounds_run == 2
    r2 = Router([ModelSpec("m", "scripted", "m", (Role.PROPOSER,))], ledger=Ledger(),
                adapters={"m": _LimitedOnce(3600, reply)})
    res2 = run_swarm(Target(a, case.ciphertext, "w2", is_synthetic=True), r2.ledger, oracle,
                     [LLMGenerator(r2, "m")],
                     SwarmConfig(rounds=2, stop_file=None, wait_on_rate_limit=False), progress=False)
    assert res2.stopped == "rate_limited"


def test_doctor_reports_cli_models_and_window(fake, tmp_path, monkeypatch):
    from lpswarm.doctor import OK, run_checks
    cfg = tmp_path / "m.toml"
    cfg.write_text(f'[models.cc]\nprovider = "claude_code"\nmodel = "sonnet"\nexe = {json.dumps(fake["claude"])}\n'
                   f'roles = ["proposer"]\nmax_calls_per_window = 40\n'
                   f'[models.cx]\nprovider = "codex"\nmodel = ""\nexe = {json.dumps(fake["codex"])}\n',
                   encoding="utf-8")
    monkeypatch.setenv("FAKE_KIND", "claude")
    led_path = tmp_path / "spend.sqlite"
    with Ledger(led_path) as led:
        led.add_budget_event("claude_code", "cc", 1, 1, 0.0, "t#1")
    checks = {c.name: c for c in run_checks(str(cfg), ledgers=[str(led_path)])}
    assert checks["model cc"].status == OK and "9.9.9" in checks["model cc"].detail
    assert "removed for this model" in checks["model cc"].detail   # ANTHROPIC_API_KEY is set
    assert checks["usage cc"].detail.startswith("1 call(s) in the last 5h (cap 40)")
    assert len(fake["calls"]()) == 2                                 # only --version, no model calls


def test_review_regressions_claude_parsing(fake, monkeypatch):
    from lpswarm.router import AdapterError
    monkeypatch.setenv("FAKE_KIND", "claude")
    ad = ClaudeCodeAdapter("", exe=fake["claude"])
    monkeypatch.setenv("FAKE_MODE", "trailing")
    assert ad.complete(MSGS).text == "OK-REPLY"             # notice after the JSON is ignored
    monkeypatch.setenv("FAKE_MODE", "limit_not_error")
    monkeypatch.setenv("FAKE_TS", str(int(time.time()) + 600))
    with pytest.raises(CLILimitError):                       # limit text in a non-error result
        ad.complete(MSGS)
    monkeypatch.setenv("FAKE_MODE", "other_error_429_stderr")
    with pytest.raises(AdapterError) as ei:                  # 429 on stderr is not a limit
        ad.complete(MSGS)
    assert not isinstance(ei.value, CLILimitError)


def test_non_ascii_prompt_round_trips(fake, monkeypatch):
    monkeypatch.setenv("FAKE_KIND", "claude")
    runes = "\u16a0\u16a2\u16a6 \u2022 \u16a9"
    ClaudeCodeAdapter("", exe=fake["claude"]).complete([{"role": "user", "content": runes}])
    assert fake["calls"]()[-1]["stdin"] == runes


def test_stale_reset_time_falls_back_to_cooldown():
    now = time.time()
    at, parsed = parse_resume_at(f"usage limit reached|{int(now) - 100}", now)
    assert not parsed and at >= now + 60
    at, parsed = parse_resume_at("Try again in 1 hour 30 minutes", now)
    assert parsed and abs(at - now - 5400) < 1
    assert parse_resume_at("retry in 500ms", now)[0] - now < 1
    assert not parse_resume_at("presets 10 things", now)[1]


@pytest.mark.skipif(os.name == "nt", reason="process-group check uses POSIX signals")
def test_timeout_kills_the_whole_process_tree(fake, monkeypatch, tmp_path):
    from lpswarm.router import AdapterError
    monkeypatch.setenv("FAKE_KIND", "claude")
    monkeypatch.setenv("FAKE_MODE", "sleep")
    child_file = tmp_path / "child.pid"
    monkeypatch.setenv("FAKE_CHILD", str(child_file))
    t0 = time.monotonic()
    with pytest.raises(AdapterError, match="timed out"):
        ClaudeCodeAdapter("", exe=fake["claude"], timeout=2).complete(MSGS)
    assert time.monotonic() - t0 < 20
    pid = int(child_file.read_text())
    time.sleep(0.5)
    try:
        os.kill(pid, 0)
        alive = Path(f"/proc/{pid}/status").exists() and "zombie" not in Path(f"/proc/{pid}/status").read_text()
    except ProcessLookupError:
        alive = False
    assert not alive


def test_loop_never_spins_on_a_past_reset(oracle):
    """A limit that keeps reporting an already-past reset must not make the loop call
    the CLI in a tight loop: each pause is at least a minute, so we stop via timeout."""
    from lpswarm.alphabet import Alphabet
    from lpswarm.executor import Target
    from lpswarm.swarm import LLMGenerator, SwarmConfig, run_swarm
    from lpswarm.textgen.synth import generate_case

    class AlwaysLimited:
        calls = 0

        def complete(self, messages, temperature=0.7, max_tokens=2048):
            AlwaysLimited.calls += 1
            raise CLILimitError("usage limit", time.time() - 10, True)

    a = Alphabet.latin26()
    case = generate_case("caesar", 60, seed=4)
    led = Ledger()
    r = Router([ModelSpec("m", "scripted", "m", (Role.PROPOSER,))], ledger=led,
               adapters={"m": AlwaysLimited()})
    res = run_swarm(Target(a, case.ciphertext, "s", is_synthetic=True), led, oracle,
                    [LLMGenerator(r, "m")], SwarmConfig(rounds=2, stop_file=None, timeout_s=3),
                    progress=False)
    assert res.stopped == "timeout" and AlwaysLimited.calls <= 2


def test_codex_reports_the_model_it_ran(fake, monkeypatch, capsys):
    from lpswarm.router import ModelSpec, Role, Router
    from lpswarm.ledger import Ledger
    monkeypatch.setenv("FAKE_KIND", "codex")
    monkeypatch.setenv("FAKE_MODEL", "gpt-test-1")
    monkeypatch.setenv("LPSWARM_LOG_CALLS", "1")
    spec = ModelSpec("codex", "codex", "default", (Role.PROPOSER,), extra={"exe": fake["codex"]})
    c = Router([spec], ledger=Ledger()).complete("codex", MSGS, role="proposer")
    assert c.model == "gpt-test-1"
    assert "model gpt-test-1" in capsys.readouterr().out
    monkeypatch.setenv("FAKE_MODEL", "")
    Router([spec], ledger=Ledger()).complete("codex", MSGS, role="proposer")
    assert "model not reported" in capsys.readouterr().out

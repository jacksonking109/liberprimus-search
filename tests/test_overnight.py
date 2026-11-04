"""Unattended queue runner, supervisor menu, publishing, shared quota groups."""
import json
import subprocess
from pathlib import Path

import pytest

from lpswarm.ledger import Ledger
from lpswarm.overnight import (Overnight, OvernightConfig, apply_supervisor_reply, expand_jobs,
                               load_config, manifest_sections, publish_results)
from lpswarm.router import ModelSpec, RateLimited, Role, Router, ScriptedAdapter

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = str(ROOT / "data" / "lp" / "manifest.json")
ALPHA = str(ROOT / "data" / "alphabet" / "gematria_primus.json")


def _cfg(tmp_path, jobs, **kw):
    return OvernightConfig(models=str(tmp_path / "none.toml"), spend_ledger=str(tmp_path / "spend.sqlite"),
                           publish=False, manifest=MANIFEST, alphabet=ALPHA, jobs=jobs, **kw)


def test_config_and_expansion(tmp_path):
    p = tmp_path / "o.toml"
    p.write_text('[overnight]\npublish = false\n[[job]]\nid = "a"\nkind = "swarm"\n'
                 f'args = ["--manifest", {json.dumps(MANIFEST)}, "--sections", "unsolved"]\n',
                 encoding="utf-8")
    cfg = load_config(p)
    jobs = expand_jobs(cfg)
    unsolved = manifest_sections(MANIFEST, "unsolved")
    assert len(jobs) == len(unsolved) >= 15 and jobs[0]["id"].startswith("a/")
    assert "--sections" in jobs[0]["args"] and jobs[0]["args"][jobs[0]["args"].index("--sections") + 1].isdigit()
    bad = tmp_path / "b.toml"
    bad.write_text('[[job]]\nid = "x"\nkind = "rm"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(bad)
    example = load_config(ROOT / "config" / "overnight.example.toml")
    assert [j["id"] for j in example.jobs] == ["tier-claude", "sonnet", "codex", "local", "deepseek"]


TIER = {"id": "tier", "kind": "tiertest",
        "args": ["--arms", "random_program:5", "--lengths", "40", "--cases", "1", "--null-samples", "100"]}
SWARM = {"id": "sw", "kind": "swarm",
         "args": ["--manifest", MANIFEST, "--alphabet", ALPHA, "--sections", "9", "--generators",
                  "random_program", "--rounds", "1", "--per-round", "3", "--null-samples", "100"]}
BROKEN = {"id": "broken", "kind": "baseline", "args": ["--no-such-flag"]}


def test_runner_end_to_end_failure_isolation_and_summary(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    run = Overnight(_cfg(tmp_path, [BROKEN, TIER, SWARM]), tmp_path / "run",
                    stop_file=tmp_path / "STOP", poll_s=0.5, progress=False)
    st = run.run()
    status = {j["id"]: j["status"] for j in st["jobs"]}
    assert status == {"broken": "failed", "tier": "done", "sw/9": "done"}
    assert st["status"] == "finished"
    summary = (tmp_path / "run" / "SUMMARY.md").read_text(encoding="utf-8")
    assert "random_program:5: recall" in summary and "LP1:16.jpg" in summary
    assert "last log lines" in summary            # failed job shows its log tail
    assert (tmp_path / "run" / "sw_9" / "report.md").is_file()


def test_stop_file_then_resume(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    stop = tmp_path / "STOP"
    stop.write_text("", encoding="utf-8")
    run = Overnight(_cfg(tmp_path, [TIER]), tmp_path / "run", stop_file=stop, poll_s=0.5, progress=False)
    st = run.run()
    assert st["status"] == "stopped" and st["jobs"][0]["status"] == "pending"
    stop.unlink()
    st2 = Overnight(_cfg(tmp_path, [TIER]), tmp_path / "run", stop_file=stop, poll_s=0.5,
                    progress=False).run()
    assert st2["jobs"][0]["status"] == "done" and any("resumed" in e for e in st2["events"])


def test_preflight_refuses_unsafe_api_models(tmp_path, monkeypatch):
    models = tmp_path / "m.toml"
    models.write_text('[models.ds]\nprovider = "openai_compatible"\nendpoint = "https://x.invalid"\n'
                      'model = "m"\napi_key_env = "LPSWARM_T_KEY"\nroles = ["proposer"]\nmax_usd = 1.0\n',
                      encoding="utf-8")
    cfg = _cfg(tmp_path, [{"id": "j", "kind": "swarm", "args": ["--generators", "ds"]}])
    cfg.models = str(models)
    run = Overnight(cfg, tmp_path / "run", stop_file=tmp_path / "STOP", progress=False)
    assert "prices are 0" in run.preflight(run.state["jobs"][0])
    models.write_text(models.read_text(encoding="utf-8") + "price_in_per_mtok = 0.3\n", encoding="utf-8")
    monkeypatch.delenv("LPSWARM_T_KEY", raising=False)
    assert "not set" in run.preflight(run.state["jobs"][0])


def _sup_run(tmp_path, replies):
    led = Ledger(tmp_path / "spend.sqlite")
    specs = [ModelSpec("sup", "scripted", "sup", (Role.SUPERVISOR,)),
             ModelSpec("codex", "scripted", "codex", (Role.PROPOSER,))]
    router = Router(specs, ledger=led, adapters={"sup": ScriptedAdapter("sup", replies),
                                                 "codex": ScriptedAdapter("codex", ["{}"])})
    cfg = _cfg(tmp_path, [TIER, {**TIER, "id": "tier2"}], supervisor="sup", max_added_jobs=1)
    return Overnight(cfg, tmp_path / "run", router=router, stop_file=tmp_path / "STOP", progress=False)


def test_supervisor_menu_is_validated(tmp_path):
    run = _sup_run(tmp_path, ["x"])
    run.state["jobs"][0]["status"] = "failed"
    reply = json.dumps({"actions": [
        {"type": "note", "text": "all quiet"},
        {"type": "add_job", "sections": [9, 11], "generators": ["codex", "not-a-model"], "rounds": 99,
         "per_round": 99, "reason": "look closer"},
        {"type": "add_job", "sections": "unsolved", "generators": ["codex"]},     # over the cap
        {"type": "add_job", "sections": [9], "generators": ["gpt-unknown"]},
        {"type": "retry_job", "id": "tier"}, {"type": "retry_job", "id": "tier"},
        {"type": "skip_job", "id": "tier2"},
        {"type": "run_shell", "cmd": "rm -rf /"},
        "junk",
    ]})
    msgs = apply_supervisor_reply(run, "Sure!\n" + reply)
    jobs = {j["id"]: j for j in run.state["jobs"]}
    added = [j for j in run.state["jobs"] if j["added_by"] == "supervisor"]
    assert [j["id"] for j in added] == ["sup1/9", "sup1/11"]
    a = added[0]["args"]
    assert a[a.index("--rounds") + 1] == "8" and a[a.index("--per-round") + 1] == "8"
    assert a[a.index("--generators") + 1] == "codex"
    assert any("nightly limit" in m for m in msgs) and any("no configured proposer" in m for m in msgs)
    assert jobs["tier"]["status"] == "pending" and jobs["tier"]["retries"] == 1
    assert jobs["tier2"]["status"] == "skipped"
    assert any("unknown action" in m for m in msgs) and run.state["notes"][0].endswith("all quiet")
    assert apply_supervisor_reply(run, "no json") == ['reply had no {"actions": [...]} object; ignored']
    apply_supervisor_reply(run, json.dumps({"actions": [{"type": "stop", "reason": "done"}]}))
    assert run.should_stop().startswith("supervisor")


def test_supervisor_tick_uses_router_and_survives_failure(tmp_path):
    run = _sup_run(tmp_path, [json.dumps({"actions": [{"type": "note", "text": "tick ok"}]})])
    run.write_summary()
    run.maybe_tick(force=True)
    assert run.state["notes"] and "tick ok" in run.state["notes"][-1]

    class Down:
        def complete(self, messages, temperature=0.7, max_tokens=2048):
            from lpswarm.router.cli_adapters import CLILimitError
            import time
            raise CLILimitError("usage limit", time.time() + 600, True)
    run.router._models["sup"].adapter = Down()
    run.maybe_tick(force=True)          # within 10 minutes of the last check-in: throttled
    assert not any("supervisor unavailable" in e for e in run.state["events"])
    run.last_tick = 0.0
    run.maybe_tick(force=True)          # paused supervisor: logged, run continues
    assert any("supervisor unavailable" in e for e in run.state["events"])


def _git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def test_publish_results_to_branch(tmp_path):
    remote = tmp_path / "remote.git"
    repo = tmp_path / "repo"
    _git(["init", "-q", "--bare", str(remote)], tmp_path)
    _git(["init", "-q", str(repo)], tmp_path)
    for k, v in (("user.email", "t@example.invalid"), ("user.name", "t")):
        _git(["config", k, v], repo)
    (repo / "README.md").write_text("x", encoding="utf-8")
    _git(["add", "."], repo)
    _git(["commit", "-q", "-m", "init"], repo)
    _git(["remote", "add", "origin", str(remote)], repo)
    run_dir = repo / "reports" / "overnight" / "20260101-2200"
    (run_dir / "job").mkdir(parents=True)
    (run_dir / "SUMMARY.md").write_text("# s", encoding="utf-8")
    (run_dir / "job" / "report.md").write_text("# r", encoding="utf-8")
    (run_dir / "job" / "ledger.sqlite").write_bytes(b"secretish")
    (run_dir / "job" / "job.log").write_text("log", encoding="utf-8")
    assert "file(s)" in publish_results(run_dir, "results", repo=repo)
    assert publish_results(run_dir, "results", repo=repo) == "nothing new"
    files = subprocess.run(["git", "ls-tree", "-r", "--name-only", "results"], cwd=remote,
                           capture_output=True, text=True, check=True).stdout.split()
    assert sorted(files) == ["20260101-2200/SUMMARY.md", "20260101-2200/job/report.md"]


def test_quota_group_shared_between_models():
    led = Ledger()
    g = {"quota_group": "claude-plan", "max_calls_per_window": 2}
    specs = [ModelSpec("opus", "scripted", "o", (Role.PROPOSER,), extra=dict(g)),
             ModelSpec("sonnet", "scripted", "s", (Role.PROPOSER,), extra=dict(g)),
             ModelSpec("other", "scripted", "x", (Role.PROPOSER,))]
    r = Router(specs, ledger=led, adapters={n: ScriptedAdapter(n, ["ok"]) for n in ("opus", "sonnet", "other")})
    r.complete("opus", [], role="proposer")
    r.complete("sonnet", [], role="proposer")
    with pytest.raises(RateLimited):          # group cap reached by the two together
        r.complete("opus", [], role="proposer")
    with pytest.raises(RateLimited):          # and the pause applies to the whole group
        r.complete("sonnet", [], role="proposer")
    r.complete("other", [], role="proposer")  # other models are unaffected
    assert r.window_status("sonnet")["calls"] == 2


def test_blocked_jobs_do_not_trigger_publish_or_supervisor(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    models = tmp_path / "m.toml"
    models.write_text('[models.ds]\nprovider = "openai_compatible"\nendpoint = "https://x.invalid"\n'
                      'model = "m"\napi_key_env = "K"\nroles = ["proposer"]\nmax_usd = 1.0\n',
                      encoding="utf-8")
    jobs = [{"id": f"j{i}", "kind": "swarm", "args": ["--generators", "ds"]} for i in range(5)]
    run = _sup_run(tmp_path, [json.dumps({"actions": []})])
    run.cfg.models = str(models)
    run.state["jobs"] = [__import__("lpswarm.overnight", fromlist=["_job"])._job(j["id"], "swarm", j["args"], "config")
                         for j in jobs]
    calls = {"publish": 0}
    monkeypatch.setattr(run, "publish", lambda: calls.__setitem__("publish", calls["publish"] + 1))
    st = run.run()
    assert all(j["status"] == "blocked" for j in st["jobs"])
    assert calls["publish"] == 1                         # only the final publish
    assert run.state["ticks"] == 0                       # no supervisor calls for refused jobs


def test_retry_failed_resets_failed_and_blocked(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    run = Overnight(_cfg(tmp_path, [TIER]), tmp_path / "run", stop_file=tmp_path / "STOP", progress=False)
    run.state["jobs"][0]["status"] = "failed"
    run.save()
    again = Overnight(_cfg(tmp_path, [TIER]), tmp_path / "run", stop_file=tmp_path / "STOP",
                      progress=False, retry_failed=True)
    assert again.state["jobs"][0]["status"] == "pending"


def test_tiertest_recheck_handles_resolved_specs(tmp_path):
    from lpswarm.alphabet import Alphabet
    from lpswarm.executor import Executor, ExplicitKeys, Target
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.programs import compile_spec
    from lpswarm.textgen.synth import generate_case
    from lpswarm.validation.tiertest import _decrypt_attempt
    a = Alphabet.latin26()
    o = FullOracle(a, OracleConfig(null_samples=100, variant_null_samples=100))
    case = generate_case("caesar", 60, seed=3)
    led = Ledger()
    h = led.add_hypothesis("program", "x", "t", "proposer")
    spec = compile_spec({"stream": {"kind": "constant", "value": int(case.key)}, "skip": [25],
                         "skip_mode": "resolve"}, a)
    Executor(led, o, stop_file=None).run(Target(a, case.ciphertext, "r", is_synthetic=True), h,
                                         "program", ExplicitKeys([spec]))
    aid = led.conn.execute("SELECT id FROM attempt").fetchone()[0]
    assert _decrypt_attempt(led, aid, case.ciphertext, 26, o) is not None
    assert _decrypt_attempt(led, aid, case.ciphertext, 26, None) is None   # no crash without LM


def test_router_call_log_and_transcript(tmp_path, monkeypatch, capsys):
    tr = tmp_path / "t.jsonl"
    monkeypatch.setenv("LPSWARM_LOG_CALLS", "1")
    monkeypatch.setenv("LPSWARM_TRANSCRIPT", str(tr))
    r = Router([ModelSpec("codex", "scripted", "c", (Role.PROPOSER,))], ledger=Ledger(),
               adapters={"codex": ScriptedAdapter("codex", ["hello"], tokens=(12, 3))})
    r.complete("codex", [{"role": "user", "content": "q"}], role="proposer", task_id="x#r1")
    out = capsys.readouterr().out
    assert "[model] codex (proposer) ok" in out and "tokens in/out 12/3" in out
    rec = json.loads(tr.read_text(encoding="utf-8").splitlines()[0])
    assert rec["model"] == "codex" and rec["reply"] == "hello" and rec["messages"][0]["content"] == "q"


def test_log_tail_skips_warning_noise(tmp_path):
    from lpswarm.overnight import _log_tail
    p = tmp_path / "job.log"
    p.write_text("round 1 [codex] proposals=8\nC:\\x\\router.py:106: UserWarning: prices are 0\n"
                 "  return cls(load_model_specs(path), ledger=ledger, **kw)\n"
                 "  r = cls(load_model_specs(path), ledger=ledger, **kw)\n\n", encoding="utf-8")
    assert _log_tail(p, 3) == ["round 1 [codex] proposals=8"]


def test_jobs_run_verbose_with_model_call_lines(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    run = Overnight(_cfg(tmp_path, [SWARM]), tmp_path / "run", stop_file=tmp_path / "STOP",
                    poll_s=0.5, progress=False)
    assert "--quiet" not in run.job_command(run.state["jobs"][0])
    run.run()
    log = (tmp_path / "run" / "sw_9" / "job.log").read_text(encoding="utf-8")
    assert "round 1 [random_program]" in log

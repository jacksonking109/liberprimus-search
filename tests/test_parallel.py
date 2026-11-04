"""Live window caps, thread-safe router, parallel swarm rounds, parallel overnight jobs."""
import sys
import threading
import time
from pathlib import Path

from lpswarm.ledger import Ledger
from lpswarm.overnight import Overnight, OvernightConfig
from lpswarm.router import ModelSpec, RateLimited, Role, Router, ScriptedAdapter, backend_key

ROOT = Path(__file__).resolve().parent.parent


def _plan_router(led, cap):
    specs = [ModelSpec(n, "scripted", n, (Role.PROPOSER, Role.SUPERVISOR),
                       extra={"quota_group": "claude-plan", "max_calls_per_window": cap,
                              "window_hours": 5})
             for n in ("opus", "sup")]
    return Router(specs, ledger=led, adapters={s.name: ScriptedAdapter(s.name, ["ok"]) for s in specs})


def test_window_pause_ends_when_cap_is_raised(tmp_path):
    led = Ledger(tmp_path / "spend.sqlite")
    r = _plan_router(led, 2)
    r.complete("opus", [], role="proposer")
    r.complete("sup", [], role="supervisor")
    try:
        r.complete("sup", [], role="supervisor")
        raise AssertionError("cap should pause")
    except RateLimited as exc:
        assert "local cap 2/2" in str(exc) and "max_calls_per_window" in str(exc)
    st = r.window_status("opus")
    assert st["pause_kind"] == "window" and st["calls"] == 2 and st["quota"] == "claude-plan"
    # one history row per pause, not one per check
    try:
        r.complete("opus", [], role="proposer")
    except RateLimited:
        pass
    rows = led.conn.execute("SELECT COUNT(*) FROM rate_limit_event WHERE source='window'").fetchone()[0]
    assert rows == 1
    # a restart with a higher cap carries on at once, despite the stored window row
    r2 = _plan_router(led, 10)
    assert r2.window_status("sup")["paused_until"] is None
    r2.complete("sup", [], role="supervisor")


def test_reply_pause_still_holds(tmp_path):
    led = Ledger(tmp_path / "spend.sqlite")
    led.add_rate_limit_event("opus", time.time(), time.time() + 3600, "reply", True, "limit")
    r = _plan_router(led, 100)
    st = r.window_status("sup")
    assert st["pause_kind"] == "reply" and st["paused_until"] > time.time()
    try:
        r.complete("sup", [], role="supervisor")
        raise AssertionError("reply pause should hold")
    except RateLimited as exc:
        assert "reported by the CLI" in str(exc)


def test_doctor_counts_the_whole_quota_group(tmp_path):
    from lpswarm.doctor import run_checks
    led_path = tmp_path / "spend.sqlite"
    led = Ledger(led_path)
    for n in ("claude-opus", "claude-opus", "claude-supervisor"):
        led.add_budget_event("claude_code", n, 1, 1, 0.0, None)
    led.commit()
    led.close()
    exe = sys.executable.replace("\\", "/")
    models = tmp_path / "m.toml"
    models.write_text("".join(
        f'[models.{n}]\nprovider = "claude_code"\nmodel = "opus"\nroles = ["{role}"]\nexe = "{exe}"\n'
        'quota_group = "claude-plan"\nmax_calls_per_window = 120\n\n'
        for n, role in (("claude-opus", "proposer"), ("claude-supervisor", "supervisor"))),
        encoding="utf-8")
    checks = run_checks(str(models), ledgers=[str(led_path)])
    usage = {c.name: c.detail for c in checks if c.name.startswith("usage ")}
    assert usage["usage claude-supervisor"].startswith("3 call(s)")
    assert "group claude-plan" in usage["usage claude-opus"]


def test_router_is_thread_safe(tmp_path):
    led = Ledger(tmp_path / "spend.sqlite")
    specs = [ModelSpec(f"m{i}", "scripted", "x", (Role.PROPOSER,)) for i in range(4)]
    r = Router(specs, ledger=led, adapters={s.name: ScriptedAdapter(s.name, ["ok"]) for s in specs})

    def work(name):
        for _ in range(10):
            r.complete(name, [], role="proposer")
    ts = [threading.Thread(target=work, args=(s.name,)) for s in specs]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert led.conn.execute("SELECT COUNT(*) FROM budget_event").fetchone()[0] == 40


def test_backend_keys():
    o1 = ModelSpec("qwen", "ollama", "q", (Role.PROPOSER,), endpoint="http://localhost:11434")
    o2 = ModelSpec("gemma", "ollama", "g", (Role.PROPOSER,), endpoint="http://localhost:11434/")
    o3 = ModelSpec("granite", "ollama", "g", (Role.WEIGHTING,), endpoint="http://localhost:11435")
    cx = ModelSpec("codex", "codex", "default", (Role.PROPOSER,), extra={"quota_group": "codex-plan"})
    assert backend_key(o1) == backend_key(o2) != backend_key(o3)
    assert backend_key(cx) == "codex-plan"


# ------------------------------------------------------------- swarm rounds
class _SlowGen:
    role = "proposer"

    def __init__(self, name, router=None, delay=0.4):
        self.model, self.router, self.delay = name, router, delay
        self.calls = []

    def propose(self, ctx):
        self.calls.append((time.monotonic(), threading.current_thread().name))
        time.sleep(self.delay)
        return []


class _FakeRouter:
    def __init__(self, specs):
        self._s = {s.name: s for s in specs}

    def spec(self, name):
        return self._s[name]


def _run(gens, parallel):
    from lpswarm.alphabet import Alphabet
    from lpswarm.executor import Target
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.swarm import SwarmConfig, run_swarm
    from lpswarm.textgen.synth import generate_case
    a = Alphabet.latin26()
    case = generate_case("caesar", 60, seed=1)
    t0 = time.monotonic()
    run_swarm(Target(a, case.ciphertext, "t", is_synthetic=True), Ledger(),
              FullOracle(a, OracleConfig(null_samples=100)), gens,
              SwarmConfig(rounds=1, per_round=2, stop_file=None, parallel=parallel), progress=False)
    return time.monotonic() - t0


def test_swarm_calls_different_backends_at_once():
    gens = [_SlowGen("codex"), _SlowGen("qwen")]
    dt = _run(gens, parallel=True)
    a, b = gens[0].calls[0][0], gens[1].calls[0][0]
    assert abs(a - b) < 0.3 and dt < 5
    serial = [_SlowGen("codex"), _SlowGen("qwen")]
    _run(serial, parallel=False)
    assert serial[1].calls[0][0] - serial[0].calls[0][0] >= 0.35


def test_swarm_keeps_one_gpu_serial():
    specs = [ModelSpec(n, "ollama", n, (Role.PROPOSER,), endpoint="http://localhost:11434")
             for n in ("qwen", "gemma")]
    fr = _FakeRouter(specs)
    gens = [_SlowGen("qwen", fr), _SlowGen("gemma", fr)]
    _run(gens, parallel=True)
    assert gens[1].calls[0][0] - gens[0].calls[0][0] >= 0.35


# ----------------------------------------------------------- overnight jobs
def _night(tmp_path, gens_per_job, sleep_s=1.5, **kw):
    tmp_path.mkdir(parents=True, exist_ok=True)
    models = tmp_path / "m.toml"
    models.write_text("".join(f'[models.{n}]\nprovider = "scripted"\nmodel = "x"\nroles = ["proposer"]\n'
                              f'replies = ["{{}}"]\n\n' for n in ("a", "b")), encoding="utf-8")
    jobs = [{"id": f"j{i}", "kind": "swarm", "args": ["--generators", g]} for i, g in enumerate(gens_per_job)]
    cfg = OvernightConfig(models=str(models), spend_ledger=str(tmp_path / "s.sqlite"), publish=False,
                          jobs=jobs)
    run = Overnight(cfg, tmp_path / "run", stop_file=tmp_path / "STOP", poll_s=0.1, **kw)
    code = f"import time; print('hello from job', flush=True); time.sleep({sleep_s}); print('bye')"
    run.job_command = lambda job: [sys.executable, "-c", code]
    return run


def _times(st):
    from datetime import datetime
    f = "%Y-%m-%d %H:%M:%S"
    return {j["id"]: (datetime.strptime(j["started"], f), datetime.strptime(j["ended"], f))
            for j in st["jobs"]}


def test_jobs_on_different_backends_run_side_by_side(tmp_path, capsys):
    run = _night(tmp_path, ["a", "b"], sleep_s=2.5)
    assert run.job_resources(run.state["jobs"][0]) != run.job_resources(run.state["jobs"][1])
    t0 = time.monotonic()
    st = run.run()
    assert all(j["status"] == "done" for j in st["jobs"])
    assert time.monotonic() - t0 < 4.5          # serial would take > 5 s
    out = capsys.readouterr().out
    assert "[j0] hello from job" in out and "[j1] bye" in out and "2 running" in out


def test_jobs_sharing_a_backend_wait(tmp_path, capsys):
    run = _night(tmp_path, ["a", "a"], sleep_s=1.2)
    st = run.run()
    t = _times(st)
    assert t["j1"][0] >= t["j0"][1]
    assert "j1 waiting: scripted:a in use by j0" in capsys.readouterr().out


def test_serial_mode_and_stop_kills_all(tmp_path):
    run = _night(tmp_path, ["a", "b"], sleep_s=1.2, progress=False)
    run.max_parallel = 1
    st = run.run()
    t = _times(st)
    assert t["j1"][0] >= t["j0"][1]

    run2 = _night(tmp_path / "x", ["a", "b"], sleep_s=60, progress=False)
    stop = tmp_path / "x" / "STOP"
    threading.Timer(1.5, lambda: stop.write_text("", encoding="utf-8")).start()
    t0 = time.monotonic()
    st2 = run2.run()
    assert time.monotonic() - t0 < 30
    assert [j["status"] for j in st2["jobs"]] == ["interrupted", "interrupted"]
    assert st2["status"] == "stopped"


def test_cap_raised_in_config_lifts_pause_without_restart(tmp_path):
    cfg = tmp_path / "m.toml"
    body = ('[models.opus]\nprovider = "scripted"\nmodel = "x"\nroles = ["proposer"]\n'
            'replies = ["ok"]\nquota_group = "claude-plan"\nmax_calls_per_window = {cap}\n')
    cfg.write_text(body.format(cap=1), encoding="utf-8")
    r = Router.from_toml(cfg, ledger=Ledger(tmp_path / "s.sqlite"))
    r.complete("opus", [], role="proposer")
    try:
        r.complete("opus", [], role="proposer")
        raise AssertionError("cap should pause")
    except RateLimited:
        pass
    import os
    cfg.write_text(body.format(cap=50), encoding="utf-8")
    st = os.stat(cfg)
    os.utime(cfg, (st.st_atime, st.st_mtime + 5))      # make sure the mtime moves
    r.complete("opus", [], role="proposer")             # same router, new cap
    assert r.spec("opus").extra["max_calls_per_window"] == 50


def test_swarm_wait_ends_when_pause_lifts():
    from lpswarm.swarm.loop import _wait_until
    t0 = time.monotonic()
    flag = {"n": 0}

    def still():
        flag["n"] += 1
        return flag["n"] < 2
    assert _wait_until(time.time() + 3600, None, lambda: None, False, still_paused=still,
                       recheck_s=0.2) is None
    assert time.monotonic() - t0 < 5


def test_blocked_jobs_are_reported_once(tmp_path, capsys):
    models = tmp_path / "m.toml"
    models.write_text('[models.ds]\nprovider = "openai_compatible"\nendpoint = "https://x.invalid"\n'
                      'model = "m"\napi_key_env = "K"\nroles = ["proposer"]\nmax_usd = 1.0\n',
                      encoding="utf-8")
    jobs = [{"id": f"u/{i}", "kind": "swarm", "args": ["--generators", "ds"]} for i in range(3)]
    cfg = OvernightConfig(models=str(models), spend_ledger=str(tmp_path / "s.sqlite"), publish=False,
                          jobs=jobs)
    st = Overnight(cfg, tmp_path / "run", stop_file=tmp_path / "STOP", poll_s=0.1).run()
    out = capsys.readouterr().out
    assert out.count("prices are 0") == 1 and "blocked 3 jobs (u/0 ... u/2)" in out
    assert all(j["status"] == "blocked" and "prices are 0" in j["reason"] for j in st["jobs"])


def test_job_env_mutes_the_prices_warning(tmp_path):
    import subprocess as sp
    from lpswarm.router.router import PRICES_ZERO_WARNING
    run = _night(tmp_path, ["a"], sleep_s=0, progress=False)
    seen = {}
    real = sp.Popen

    def spy(cmd, **kw):
        seen["env"] = kw["env"]
        return real(cmd, **kw)
    import lpswarm.overnight as ov
    ov.subprocess.Popen = spy
    try:
        run.run()
    finally:
        ov.subprocess.Popen = real
    assert f"ignore:{PRICES_ZERO_WARNING}" in seen["env"]["PYTHONWARNINGS"]
    # and the filter really matches the warning text
    code = ("import warnings; from lpswarm.router import Router, ModelSpec, Role;"
            "Router([ModelSpec('ds','openai_compatible','m',(Role.PROPOSER,),endpoint='https://x.invalid',"
            "max_usd=1.0)], ledger=__import__('lpswarm.ledger',fromlist=['Ledger']).Ledger())")
    out = sp.run([sys.executable, "-c", code], env=seen["env"], capture_output=True, text=True)
    assert out.returncode == 0 and "prices are 0" not in out.stderr

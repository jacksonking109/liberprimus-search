"""Live window caps, thread-safe router, parallel swarm rounds, parallel overnight jobs."""
import os
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


def test_short_sections_skipped_or_flagged(tmp_path):
    import subprocess as sp
    man = str(ROOT / "data" / "lp" / "manifest.json")
    alpha = str(ROOT / "data" / "alphabet" / "gematria_primus.json")

    def swarm(section):
        out = tmp_path / f"s{section}"
        r = sp.run([sys.executable, "-m", "lpswarm", "swarm", "--manifest", man, "--alphabet", alpha,
                    "--sections", str(section), "--generators", "random_program", "--rounds", "1",
                    "--per-round", "2", "--null-samples", "100", "--ledger", str(out / "l.sqlite"),
                    "--report-dir", str(out)], capture_output=True, text=True, encoding="utf-8",
                   cwd=ROOT)
        assert r.returncode == 0, r.stderr[-500:]
        return r.stdout, out
    so, _ = swarm(15)                       # 9 runes: skipped
    assert "skip" in so and "minimum 20" in so
    so, out = swarm(19)                     # 91 runes: run, but flagged
    assert "short section (91 runes)" in so
    rep = (out / "report.md").read_text(encoding="utf-8")
    assert "91 (short)" in rep and "Caution: short section" in rep


def test_per_model_cap_inside_group(tmp_path):
    led = Ledger(tmp_path / "s.sqlite")
    specs = [ModelSpec("opus", "scripted", "x", (Role.PROPOSER,),
                       extra={"quota_group": "g", "max_calls_per_window": 10,
                              "model_max_calls_per_window": 2}),
             ModelSpec("sonnet", "scripted", "x", (Role.PROPOSER,),
                       extra={"quota_group": "g", "max_calls_per_window": 10})]
    r = Router(specs, ledger=led, adapters={s.name: ScriptedAdapter(s.name, ["ok"]) for s in specs})
    r.complete("opus", [], role="proposer")
    r.complete("opus", [], role="proposer")
    try:
        r.complete("opus", [], role="proposer")
        raise AssertionError("opus share should be full")
    except RateLimited as exc:
        assert "for opus alone" in str(exc)
    for _ in range(8):                     # sonnet uses the rest of the group total
        r.complete("sonnet", [], role="proposer")
    try:
        r.complete("sonnet", [], role="proposer")
        raise AssertionError("group total should be full")
    except RateLimited as exc:
        assert "10/10" in str(exc) and "for g" in str(exc)


def test_supervisor_brief_reaches_the_prompt(tmp_path):
    from lpswarm.alphabet import Alphabet
    from lpswarm.overnight import apply_supervisor_reply
    from lpswarm.swarm.generators import GenContext, build_prompt
    import json as _json
    import numpy as np
    led = Ledger(tmp_path / "spend.sqlite")
    specs = [ModelSpec("sup", "scripted", "sup", (Role.SUPERVISOR,)),
             ModelSpec("claude-sonnet", "scripted", "s", (Role.PROPOSER,))]
    router = Router(specs, ledger=led, adapters={s.name: ScriptedAdapter(s.name, ["{}"]) for s in specs})
    cfg = OvernightConfig(models=str(tmp_path / "none.toml"), spend_ledger=str(tmp_path / "s.sqlite"),
                          publish=False, manifest=str(ROOT / "data" / "lp" / "manifest.json"),
                          alphabet=str(ROOT / "data" / "alphabet" / "gematria_primus.json"),
                          jobs=[{"id": "x", "kind": "validate"}], supervisor="sup")
    run = Overnight(cfg, tmp_path / "run", router=router, stop_file=tmp_path / "STOP", progress=False)
    reply = _json.dumps({"actions": [{"type": "add_job", "sections": [16], "generators": ["claude-sonnet"],
                                      "rounds": 2, "per_round": 4, "reason": "test",
                                      "brief": "Try totient-prime streams with offsets 0-28."}]})
    msgs = apply_supervisor_reply(run, reply)
    assert "brief: Try totient" in msgs[0]
    job = run.state["jobs"][-1]
    assert job["brief"].startswith("Try totient")
    cmd = run.job_command(job)
    assert "--brief-file" in cmd
    assert (run.job_dir(job) / "brief.txt").read_text(encoding="utf-8").startswith("Try totient")
    assert any("brief for sup1" in n for n in run.state["notes"])
    a = Alphabet.latin26()
    ctx = GenContext("t", a, np.arange(20) % 26, 1, 4, brief="Try totient-prime streams.")
    assert "Direction from the run supervisor" in build_prompt(ctx)[1]["content"]


def test_lane_orders_and_auto_brief_job(tmp_path):
    from lpswarm.overnight import _ordered, expand_jobs, load_config
    assert _ordered([1, 2, 3, 4, 5], "reverse") == [5, 4, 3, 2, 1]
    mid = _ordered([1, 2, 3, 4, 5], "middle")
    assert mid[0] == 3 and sorted(mid) == [1, 2, 3, 4, 5]
    cfg = load_config(ROOT / "config" / "overnight.example.toml")
    cfg.manifest = str(ROOT / "data" / "lp" / "manifest.json")
    jobs = expand_jobs(cfg)
    firsts = {}
    for j in jobs:
        firsts.setdefault(j["id"].split("/")[0], j["id"])
    assert len({firsts["sonnet"].split("/")[1], firsts["codex"].split("/")[1],
                firsts["local"].split("/")[1]}) == 3          # lanes start on different sections
    sj = next(j for j in jobs if j["id"].startswith("sonnet/"))
    assert sj["auto_brief"] is True
    cfg.supervisor = "claude-supervisor"
    run = Overnight(cfg, tmp_path / "run", stop_file=tmp_path / "STOP", progress=False)
    cmd = run.job_command(sj)
    assert cmd[cmd.index("--auto-brief") + 1] == "claude-supervisor"
    assert (run.job_dir(sj) / "brief_context.txt").is_file()


def test_auto_brief_in_swarm_cli(tmp_path):
    import json as _json
    import subprocess as sp
    models = tmp_path / "m.toml"
    models.write_text(
        '[models.sup]\nprovider = "scripted"\nmodel = "x"\nroles = ["supervisor"]\n'
        'replies = ["1. Try prime streams, combine sub, offsets 0-5."]\n\n'
        '[models.son]\nprovider = "scripted"\nmodel = "x"\nroles = ["proposer"]\n'
        'replies = [\'{"proposals": [{"spec": {"stream": {"kind": "constant", "value": 3}}}]}\']\n',
        encoding="utf-8")
    ctx = tmp_path / "ctx.txt"
    ctx.write_text("job codex/11: 40 attempts; near_miss margin -0.10 by codex: primes", encoding="utf-8")
    tr = tmp_path / "t.jsonl"
    r = sp.run([sys.executable, "-m", "lpswarm", "swarm", "--manifest", str(ROOT / "data/lp/manifest.json"),
                "--alphabet", str(ROOT / "data/alphabet/gematria_primus.json"), "--sections", "11",
                "--generators", "son", "--models", str(models), "--spend-ledger", str(tmp_path / "s.sqlite"),
                "--rounds", "1", "--per-round", "1", "--null-samples", "100",
                "--ledger", str(tmp_path / "l.sqlite"), "--report-dir", str(tmp_path / "r"),
                "--auto-brief", "sup", "--brief-context", str(ctx)],
               capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
               env={**__import__("os").environ, "LPSWARM_TRANSCRIPT": str(tr)})
    assert r.returncode == 0, r.stderr[-800:]
    assert "brief from sup" in r.stdout and "| 1. Try prime streams" in r.stdout
    recs = [_json.loads(x) for x in tr.read_text(encoding="utf-8").splitlines()]
    brief_call = next(x for x in recs if x["model"] == "sup")
    assert "near_miss margin -0.10" in brief_call["messages"][1]["content"]
    prop_call = next(x for x in recs if x["model"] == "son")
    assert "Try prime streams" in prop_call["messages"][1]["content"]


def test_group_total_is_the_largest_member_cap(tmp_path):
    led = Ledger(tmp_path / "s.sqlite")
    specs = [ModelSpec(n, "scripted", "x", (Role.PROPOSER,),
                       extra={"quota_group": "g", "max_calls_per_window": c})
             for n, c in (("opus", 2), ("sonnet", 5))]
    r = Router(specs, ledger=led, adapters={s.name: ScriptedAdapter(s.name, ["ok"]) for s in specs})
    for _ in range(4):
        r.complete("opus", [], role="proposer")      # not stopped at its own 2
    assert r.window_status("opus")["cap"] == 5


def test_equivalent_programs_are_one_attempt():
    from lpswarm.alphabet import get_alphabet
    from lpswarm.executor import Executor, ExplicitKeys, Target
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.programs import compile_spec
    import numpy as np
    a = get_alphabet(str(ROOT / "data" / "alphabet" / "gematria_primus.json"))
    assert a.size == 29
    o = FullOracle(a, OracleConfig(null_samples=100))
    ct = np.random.default_rng(0).integers(0, 29, 120)
    led = Ledger()
    tot = compile_spec({"stream": {"kind": "sequence", "name": "prime_totients"}, "combine": "sub"}, a)
    p28 = compile_spec({"stream": {"kind": "sequence", "name": "primes", "add": 28}, "combine": "sub"}, a)
    h = led.add_hypothesis("program", "x", "t", "proposer")
    ex = Executor(led, o, stop_file=None)
    s1 = ex.run(Target(a, ct, "t"), h, "program", ExplicitKeys([tot]))
    s2 = ex.run(Target(a, ct, "t"), h, "program", ExplicitKeys([p28]))
    assert s1.new_attempts == 1 and s2.new_attempts == 0 and s2.equivalent == 1
    assert led.attempt_count(s1.target_id) == 1


def test_chance_level_is_monotone_and_sane():
    from lpswarm.alphabet import Alphabet
    from lpswarm.oracle import FullOracle, OracleConfig
    o = FullOracle(Alphabet.latin26(), OracleConfig())   # enough nulls that nothing clamps
    L, N = 200, 30000
    thr_final = o.final_threshold(L, N)[1]
    thr0 = o.threshold(L, 1)
    at_final = o.chance_level(thr_final, L, N)
    # at most alpha at the final threshold (less when the threshold is clamped up to the
    # largest null sample, the conservative direction)
    assert 0 < at_final <= 0.0101
    assert o.chance_level(thr0, L, N) > 50            # the near-miss floor is noise level
    assert o.chance_level(thr_final + 1, L, N) < at_final < o.chance_level(thr_final - 0.2, L, N)


def test_ranker_backend_is_its_own_resource(tmp_path):
    models = tmp_path / "m.toml"
    models.write_text(
        '[models.qwen-local]\nprovider = "ollama"\nendpoint = "http://127.0.0.1:11434"\nmodel = "q"\n'
        'roles = ["proposer"]\n\n[models.granite]\nprovider = "ollama"\n'
        'endpoint = "http://127.0.0.1:11435"\nmodel = "g"\nroles = ["weighting"]\n', encoding="utf-8")
    cfg = OvernightConfig(models=str(models), spend_ledger=str(tmp_path / "s.sqlite"), publish=False,
                          jobs=[{"id": "local", "kind": "swarm",
                                 "args": ["--generators", "qwen-local", "--ranker", "granite"]}])
    run = Overnight(cfg, tmp_path / "run", stop_file=tmp_path / "STOP", progress=False)
    assert run.job_resources(run.state["jobs"][0]) == {"ollama:http://127.0.0.1:11434",
                                                       "ollama:http://127.0.0.1:11435"}


def test_capacity_lets_two_jobs_share_a_backend(tmp_path, capsys):
    import pytest
    from lpswarm.overnight import load_config
    run = _night(tmp_path, ["a", "a", "a"], sleep_s=1.5)
    run.cfg.capacity = {"scripted:a": 2}
    st = run.run()
    t = _times(st)
    assert t["j1"][0] < t["j0"][1]                  # j0 and j1 overlapped
    assert t["j2"][0] >= min(t["j0"][1], t["j1"][1])  # the third waited for a free slot
    assert "scripted:a full (2/2" in capsys.readouterr().out
    bad = tmp_path / "bad.toml"
    bad.write_text('[overnight]\ncapacity = { "x" = 0 }\n[[job]]\nid = "a"\nkind = "validate"\n',
                   encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(bad)


def test_resume_picks_up_auto_brief_for_unstarted_jobs(tmp_path):
    from lpswarm.overnight import _job
    jobs = [{"id": "codex", "kind": "validate"}]
    cfg = OvernightConfig(models=str(tmp_path / "none.toml"), spend_ledger=str(tmp_path / "s.sqlite"),
                          publish=False, jobs=jobs)
    run = Overnight(cfg, tmp_path / "run", stop_file=tmp_path / "STOP", progress=False)
    run.state["jobs"] = [_job("codex/25", "swarm", [], "config"), _job("codex/24", "swarm", [], "config")]
    run.state["jobs"][0]["status"] = "done"
    run.save()
    cfg2 = OvernightConfig(models=str(tmp_path / "none.toml"), spend_ledger=str(tmp_path / "s.sqlite"),
                           publish=False, jobs=[{"id": "codex", "kind": "swarm", "auto_brief": "codex"}])
    again = Overnight(cfg2, tmp_path / "run", stop_file=tmp_path / "STOP", progress=False)
    js = {j["id"]: j for j in again.state["jobs"]}
    assert js["codex/24"]["auto_brief"] == "codex"      # not started: updated
    assert "auto_brief" not in js["codex/25"]           # finished: left alone


def test_auto_brief_by_a_proposer_model(tmp_path):
    import subprocess as sp
    models = tmp_path / "m.toml"
    models.write_text(
        '[models.cx]\nprovider = "scripted"\nmodel = "x"\nroles = ["proposer"]\n'
        'replies = ["1. Try totient streams."]\n', encoding="utf-8")
    r = sp.run([sys.executable, "-m", "lpswarm", "swarm", "--manifest", str(ROOT / "data/lp/manifest.json"),
                "--alphabet", str(ROOT / "data/alphabet/gematria_primus.json"), "--sections", "11",
                "--generators", "cx", "--models", str(models), "--spend-ledger", str(tmp_path / "s.sqlite"),
                "--rounds", "1", "--per-round", "1", "--null-samples", "100",
                "--ledger", str(tmp_path / "l.sqlite"), "--report-dir", str(tmp_path / "r"),
                "--auto-brief", "cx"], capture_output=True, text=True, encoding="utf-8", cwd=ROOT)
    assert r.returncode == 0, r.stderr[-800:]
    assert "brief from cx" in r.stdout and "| 1. Try totient streams." in r.stdout


def test_supervisor_generators_and_checkin_gap(tmp_path):
    import json as _json
    from lpswarm.overnight import apply_supervisor_reply
    led = Ledger(tmp_path / "spend.sqlite")
    specs = [ModelSpec("sup", "scripted", "s", (Role.SUPERVISOR,)),
             ModelSpec("claude-opus", "scripted", "o", (Role.PROPOSER,)),
             ModelSpec("codex", "scripted", "c", (Role.PROPOSER,))]
    router = Router(specs, ledger=led, adapters={s.name: ScriptedAdapter(s.name, [_json.dumps({"actions": []})])
                                                 for s in specs})
    cfg = OvernightConfig(models=str(tmp_path / "none.toml"), spend_ledger=str(tmp_path / "s.sqlite"),
                          publish=False, manifest=str(ROOT / "data" / "lp" / "manifest.json"),
                          alphabet=str(ROOT / "data" / "alphabet" / "gematria_primus.json"),
                          jobs=[{"id": "x", "kind": "validate"}], supervisor="sup",
                          supervisor_generators=["codex"])
    run = Overnight(cfg, tmp_path / "run", router=router, stop_file=tmp_path / "STOP", progress=False)
    msg = apply_supervisor_reply(run, _json.dumps({"actions": [
        {"type": "add_job", "sections": [16], "generators": ["claude-opus"]}]}))[0]
    assert "refused" in msg and "allowed: codex" in msg
    msg = apply_supervisor_reply(run, _json.dumps({"actions": [
        {"type": "add_job", "sections": [16], "generators": ["codex"]}]}))[0]
    assert msg.startswith("added")
    run.last_tick = time.time() - 20 * 60          # 20 min ago: under the 30-minute gap
    run.maybe_tick(force=True)
    assert run.state["ticks"] == 0
    run.last_tick = time.time() - 31 * 60
    run.maybe_tick(force=True)
    assert run.state["ticks"] == 1


def test_near_miss_means_better_than_the_best_noise():
    from lpswarm.alphabet import Alphabet
    from lpswarm.oracle import FullOracle, OracleConfig
    a = Alphabet.latin26()
    new, old = FullOracle(a, OracleConfig()), FullOracle(a, OracleConfig(near_miss="alpha"))
    L, N = 200, 500      # 1/N below alpha, and both quantiles inside the null sample
    thr0 = old.threshold(L, 1)
    final = new.final_threshold(L, N)[1]
    near = max(new._upper_quantile(v, 1.0 / N, clamp=False) for v in new.calibrate(L).combined.values())
    assert thr0 < near < final
    # a score between the alpha line and the noise ceiling: near miss before, fail now
    x = (thr0 + near) / 2
    def verdict(o):
        import numpy as np
        from unittest import mock
        with mock.patch.object(o, "_full", return_value=(x, "en", 0.0, 0.0, None)), \
                mock.patch.object(o, "_screen", return_value=1e9):
            return o.score(np.zeros(L, dtype=np.int16), attempt_count=N).verdict
    assert verdict(old) == "near_miss" and verdict(new) == "fail"
    assert new.chance_level(near, L, N) <= 1.5


def test_extra_body_from_models_toml(tmp_path):
    import pytest
    from lpswarm.router import load_model_specs, make_adapter
    f = tmp_path / "m.toml"
    f.write_text('[models.ds]\nprovider = "openai_compatible"\nendpoint = "https://x.invalid"\n'
                 'model = "m"\napi_key_env = "K"\nextra_body = { thinking = { type = "disabled" } }\n',
                 encoding="utf-8")
    ad = make_adapter(load_model_specs(f)[0])
    assert ad.extra_body == {"thinking": {"type": "disabled"}}
    f.write_text('[models.ds]\nprovider = "openai_compatible"\nendpoint = "https://x.invalid"\n'
                 'model = "m"\nextra_body = "nope"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load_model_specs(f)


def test_shared_context_peer_ledgers_and_strategy(tmp_path):
    import json as _json
    import numpy as np
    from lpswarm.alphabet import Alphabet
    from lpswarm.executor import Executor, ExplicitKeys, Target
    from lpswarm.ledger.db import peer_tried
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.overnight import apply_supervisor_reply
    from lpswarm.programs import compile_spec
    from lpswarm.swarm.generators import GenContext, build_prompt, build_shared_context
    a = Alphabet.latin26()
    ct = np.random.default_rng(0).integers(0, 26, 80)
    # another lane's ledger with one attempt on this target
    other = tmp_path / "other.sqlite"
    with Ledger(other) as led:
        h = led.add_hypothesis("program", "sub; sequence primes*1+0 @7 | why: secret idea", "codex", "proposer")
        spec = compile_spec({"stream": {"kind": "sequence", "name": "primes", "offset": 7}, "combine": "sub"}, a)
        s = Executor(led, FullOracle(a, OracleConfig(null_samples=100)), stop_file=None).run(
            Target(a, ct, "t"), h, "program", ExplicitKeys([spec]))
        tid = s.target_id
        led.commit()
    rows = peer_tried(other, tid)
    assert len(rows) == 1 and rows[0]["proposer_model"] == "codex"
    assert peer_tried(tmp_path / "missing.sqlite", tid) == []
    text = build_shared_context(rows, "Favour transpositions next.")
    assert "primes*1+0 @7" in text and "by codex" in text and "secret idea" not in text
    assert "Favour transpositions" in text
    ctx = GenContext("t", a, ct, 1, 4, shared=text)
    assert "already tested these on this same target" in build_prompt(ctx)[1]["content"]
    # the supervisor's strategy action writes the file every lane re-reads
    cfg = OvernightConfig(models=str(tmp_path / "none.toml"), spend_ledger=str(tmp_path / "s.sqlite"),
                          publish=False, jobs=[{"id": "x", "kind": "validate"}])
    run = Overnight(cfg, tmp_path / "run", stop_file=tmp_path / "STOP", progress=False)
    msg = apply_supervisor_reply(run, _json.dumps({"actions": [{"type": "strategy", "text": "X" * 2000}]}))[0]
    assert msg.startswith("strategy note set (800 chars)")
    assert (tmp_path / "run" / "strategy.txt").read_text(encoding="utf-8") == "X" * 800
    # swarm jobs on the same section get each other's ledgers and the strategy file
    from lpswarm.overnight import _job
    j1 = _job("a/9", "swarm", ["--sections", "9"], "config")
    j2 = _job("b/9", "swarm", ["--sections", "9"], "config")
    j3 = _job("c/10", "swarm", ["--sections", "10"], "config")
    run.state["jobs"] = [j1, j2, j3]
    run.job_dir(j1).mkdir(parents=True)
    (run.job_dir(j1) / "ledger.sqlite").write_text("", encoding="utf-8")
    cmd = run.job_command(j2)
    assert cmd[cmd.index("--peer-ledger") + 1].endswith("a_9" + os.sep + "ledger.sqlite")
    assert cmd[cmd.index("--strategy-file") + 1].endswith("strategy.txt")
    assert "--peer-ledger" not in run.job_command(j3)


def test_pasted_key_is_refused_without_echo_and_never_published(tmp_path):
    import pytest
    from lpswarm.overnight import publish_results
    from lpswarm.router import load_model_specs
    fake = "sk-" + "a1b2c3d4" * 4
    f = tmp_path / "m.toml"
    f.write_text(f'[models.ds]\nprovider = "openai_compatible"\nendpoint = "https://x.invalid"\n'
                 f'model = "m"\napi_key_env = "{fake}"\n', encoding="utf-8")
    with pytest.raises(ValueError) as ei:
        load_model_specs(f)
    assert fake not in str(ei.value) and "NAME of an environment variable" in str(ei.value)
    f.write_text(f'[models.ds]\nprovider = "openai_compatible"\nendpoint = "https://x.invalid"\n'
                 f'model = "m"\napi_key_env = "DEEPSEEK-API-KEY"\n', encoding="utf-8")
    with pytest.raises(ValueError):
        load_model_specs(f)
    # publishing redacts anything key-shaped, even if one reached a summary
    import subprocess
    repo = tmp_path / "repo"
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t")):
        subprocess.run(["git", "-C", str(repo), "config", k, v], check=True)
    (repo / "README").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "init"], check=True)
    run = tmp_path / "run1"
    run.mkdir()
    (run / "SUMMARY.md").write_text(f"blocked: environment variable {fake} is not set\n", encoding="utf-8")
    try:
        publish_results(run, "results", repo=repo, worktree=tmp_path / "wt")
    except RuntimeError:
        pass   # no remote to push to; the commit is what we check
    out = subprocess.run(["git", "-C", str(tmp_path / "wt"), "show", "HEAD:run1/SUMMARY.md"],
                         capture_output=True, text=True).stdout
    assert fake not in out and "[redacted]" in out


# ----------------------------------------------------------- new transpositions
import numpy as np  # noqa: E402

_NEW_TRANSPOSES = (
    [{"grid": {"width": w, "read": r}} for w in (2, 3, 7, 9, 27)
     for r in ("rows_reversed", "columns", "columns_reversed", "boustrophedon_rows",
               "boustrophedon_columns", "diagonal", "spiral_in", "spiral_out")]
    + [{"railfence": {"rails": r}} for r in (2, 3, 5, 9)]
    + [{"decimate": {"step": k}} for k in (2, 3, 7, 13)])


def test_new_transpositions_are_permutations_and_round_trip():
    from lpswarm.alphabet import get_alphabet
    from lpswarm.programs import compile_spec, decrypt, encrypt
    from lpswarm.programs import spec as S
    a = get_alphabet(str(ROOT / "data" / "alphabet" / "gematria_primus.json"))
    rng = np.random.default_rng(5)
    for L in (1, 2, 7, 29, 91, 100, 333):
        pt = rng.integers(0, 29, L)
        for tr in _NEW_TRANSPOSES:
            try:
                perm = S._transpose_perm(tr, L)
            except S.SpecError:
                assert "decimate" in tr and np.gcd(tr["decimate"]["step"], L) != 1
                continue
            assert sorted(perm.tolist()) == list(range(L)), (tr, L)
            spec = compile_spec({"stream": {"kind": "constant", "value": 4}, "transpose": tr}, a)
            assert np.array_equal(decrypt(encrypt(pt, spec, 29), spec, 29), pt), (tr, L)


def test_transposition_semantics_small_cases():
    from lpswarm.programs import spec as S
    # 7 cells in a width-3 grid: rows 012 / 345 / 6
    assert S._transpose_perm({"grid": {"width": 3, "read": "columns"}}, 7).tolist() == [0, 3, 6, 1, 4, 2, 5]
    assert S._transpose_perm({"grid": {"width": 3, "read": "boustrophedon_rows"}}, 7).tolist() == \
        [0, 1, 2, 5, 4, 3, 6]
    assert S._transpose_perm({"grid": {"width": 3, "read": "spiral_in"}}, 9).tolist() == \
        [0, 1, 2, 5, 8, 7, 6, 3, 4]
    # rail fence, 3 rails, "WEAREDISCOVERED" style positions: rails 0 1 2 1 0 1 2 1 0
    assert S._transpose_perm({"railfence": {"rails": 3}}, 9).tolist() == [0, 4, 8, 1, 3, 5, 7, 2, 6]
    assert S._transpose_perm({"decimate": {"step": 3}}, 7).tolist() == [0, 3, 6, 2, 5, 1, 4]


def test_old_specs_keep_their_hashes_and_new_fields_are_opt_in():
    from lpswarm.alphabet import get_alphabet
    from lpswarm.programs import compile_spec, spec_hash
    a = get_alphabet(str(ROOT / "data" / "alphabet" / "gematria_primus.json"))
    s = compile_spec({"stream": {"kind": "sequence", "name": "primes", "offset": 5}, "skip": [0],
                      "transpose": {"columnar": [2, 0, 1]}}, a)
    assert set(s) == {"v", "combine", "map", "reverse_text", "skip", "transpose", "stream", "offset_range"}
    assert "transpose_range" not in s and "exhaustive" not in s["stream"]
    assert spec_hash(s) == spec_hash(compile_spec(dict(s), a))


def test_ranges_and_exhaustive_expansion_and_limits():
    import pytest
    from lpswarm.alphabet import get_alphabet
    from lpswarm.programs import SpecError, compile_spec, expand, expand_iter
    a = get_alphabet(str(ROOT / "data" / "alphabet" / "gematria_primus.json"))
    sw = compile_spec({"stream": {"kind": "constant", "value": 3},
                       "transpose": {"grid": {"width": 5, "read": "columns"}},
                       "transpose_range": [2, 40]}, a)
    ex = expand(sw)
    assert len(ex) == 39 and {e["transpose"]["grid"]["width"] for e in ex} == set(range(2, 41))
    assert all("transpose_range" not in e and e["offset_range"] is None for e in ex)
    both = compile_spec({"stream": {"kind": "sequence", "name": "primes"}, "offset_range": [0, 9],
                         "transpose": {"railfence": {"rails": 3}}, "transpose_range": [2, 6]}, a)
    assert len(expand(both)) == 50
    dec = compile_spec({"stream": {"kind": "constant", "value": 1}, "transpose": {"decimate": {"step": 2}},
                        "transpose_range": [2, 12]}, a)
    steps = [e["transpose"]["decimate"]["step"] for e in expand(dec, length=30)]
    assert steps == [7, 11]          # only steps coprime to 30
    e2 = compile_spec({"stream": {"kind": "repeat", "exhaustive": True, "key_length": 2}}, a)
    it = expand_iter(e2)
    assert next(it)["stream"]["key"] == [0, 0]
    assert len(expand(e2)) == 29 ** 2
    assert all("exhaustive" not in e["stream"] and e["stream"]["kind"] == "repeat" for e in expand(e2)[40:50])
    e4 = compile_spec({"stream": {"kind": "repeat", "exhaustive": True, "key_length": 4}}, a)
    assert e4["stream"]["n"] == 29 and len(e4["stream"]["key"]) == 4        # lazy template only
    for bad in ({"stream": {"kind": "repeat", "exhaustive": True, "key_length": 5}},
                {"stream": {"kind": "repeat", "exhaustive": True, "key_length": 2, "word": "AB"}},
                {"stream": {"kind": "repeat", "exhaustive": True, "key_length": 3},
                 "offset_range": [0, 5]},
                {"stream": {"kind": "constant", "value": 1}, "transpose_range": [2, 5]},
                {"stream": {"kind": "constant", "value": 1}, "transpose": {"grid": {"width": 3}}},
                {"stream": {"kind": "constant", "value": 1}, "transpose": {"grid": {"width": 3, "read": "x"}}},
                {"stream": {"kind": "constant", "value": 1}, "transpose": {"railfence": {"rails": 1}}},
                {"stream": {"kind": "constant", "value": 1}, "transpose": {"columnar": [0, 1], "grid": {}}},
                {"stream": {"kind": "sequence", "name": "primes"}, "offset_range": [0, 1999],
                 "transpose": {"grid": {"width": 5, "read": "columns"}}, "transpose_range": [2, 400]}):
        with pytest.raises(SpecError):
            compile_spec(bad, a)


def test_exhaustive_search_finds_the_key_and_skips_equivalents():
    from lpswarm.alphabet import get_alphabet
    from lpswarm.executor import Executor, ExplicitKeys, Target
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.programs import compile_spec, expand_iter
    from lpswarm.programs import spec as S
    a = get_alphabet(str(ROOT / "data" / "alphabet" / "gematria_primus.json"))
    rng = np.random.default_rng(1)
    pt = rng.integers(0, 29, 200)
    true = compile_spec({"stream": {"kind": "repeat", "key": [5, 11]}, "combine": "sub"}, a)
    ct = S.encrypt(pt, true, 29)
    led = Ledger()
    o = FullOracle(a, OracleConfig(null_samples=100))
    h = led.add_hypothesis("program", "all length-2 keys", "t", "proposer")
    sub = compile_spec({"stream": {"kind": "repeat", "exhaustive": True, "key_length": 2}, "combine": "sub"}, a)
    add = compile_spec({"stream": {"kind": "repeat", "exhaustive": True, "key_length": 2}, "combine": "add"}, a)
    ex = Executor(led, o, stop_file=None)
    tgt = Target(a, ct, "t", is_synthetic=True)
    s1 = ex.run(tgt, h, "program", ExplicitKeys(expand_iter(sub)))
    assert s1.new_attempts + s1.skipped == 29 ** 2
    # the add sweep is the same set of ciphers (keys negate): nothing new is tested
    s2 = ex.run(tgt, h, "program", ExplicitKeys(expand_iter(add)))
    assert s2.new_attempts == 0 and s2.equivalent == 29 ** 2
    assert s1.new_attempts == len({tuple(S.decrypt(ct, e, 29)) for e in expand_iter(sub)})


def test_synthetic_recovery_with_a_railfence_plus_stream():
    from lpswarm.alphabet import Alphabet
    from lpswarm.executor import Executor, ExplicitKeys, Target
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.programs import compile_spec, expand_iter
    from lpswarm.programs import spec as S
    from lpswarm.textgen.synth import generate_case
    a = Alphabet.latin26()
    case = generate_case("caesar", 240, seed=4)
    pt = np.asarray(case.plaintext_ints if hasattr(case, "plaintext_ints") else case.plaintext, dtype=np.int64)
    if pt.dtype.kind not in "iu" or len(pt) < 100:
        import pytest
        pytest.skip("synthetic case has no integer plaintext")
    true = compile_spec({"stream": {"kind": "sequence", "name": "primes", "offset": 3}, "combine": "sub",
                         "transpose": {"railfence": {"rails": 4}}}, a)
    ct = S.encrypt(pt, true, 26)
    guess = compile_spec({"stream": {"kind": "sequence", "name": "primes", "offset": 3}, "combine": "sub",
                          "transpose": {"railfence": {"rails": 2}}, "transpose_range": [2, 9]}, a)
    led = Ledger()
    h = led.add_hypothesis("program", "rail sweep", "t", "proposer")
    ex = Executor(led, FullOracle(a, OracleConfig(null_samples=200)), stop_file=None)
    s = ex.run(Target(a, ct, "t", is_synthetic=True), h, "program", ExplicitKeys(expand_iter(guess)))
    assert s.passes >= 1


def test_report_flags_searches_too_large_to_confirm():
    from lpswarm.alphabet import Alphabet
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.reports import _confirmable
    led = Ledger()
    o = FullOracle(Alphabet.latin26(), OracleConfig(null_samples=300))
    assert _confirmable(led, o, "none", 200) is True            # tiny search: fine
    o2 = FullOracle(Alphabet.latin26(), OracleConfig(null_samples=300))
    o2._max_combined = -100.0                                    # force "unreachable"
    assert _confirmable(led, o2, "none", 200) is False


def test_example_queue_structure_and_exhaustive_jobs_carry_briefs():
    from lpswarm.overnight import expand_jobs, load_config
    cfg = load_config(ROOT / "config" / "overnight.example.toml")
    cfg.manifest = str(ROOT / "data" / "lp" / "manifest.json")
    jobs = expand_jobs(cfg)
    st = [j for j in jobs if j["id"].startswith("structure/")]
    ex = [j for j in jobs if j["id"].startswith("exhaustive/")]
    assert [j["id"] for j in st] == [f"structure/{i}" for i in (10, 12, 13, 14, 17, 18, 24)]
    assert [j["id"] for j in ex] == [f"exhaustive/{i}" for i in (11, 19, 21, 25)]
    assert "transpose_range" in st[0]["brief"] and "key_length" in ex[0]["brief"]
    assert len(st[0]["brief"]) <= 2000 and len(ex[0]["brief"]) <= 2000


def test_new_run_sees_earlier_runs_ledgers_and_brief_is_saved(tmp_path):
    import json
    from lpswarm.overnight import _job
    base = tmp_path / "overnight"
    old = base / "20261101-0000"
    (old / "sw_9").mkdir(parents=True)
    (old / "sw_9" / "ledger.sqlite").write_bytes(b"x")
    j = _job("sw/9", "swarm", ["--sections", "9"], "config")
    (old / "state.json").write_text(json.dumps({"jobs": [j]}), encoding="utf-8")
    cfg = OvernightConfig(models=str(tmp_path / "none.toml"), spend_ledger=str(tmp_path / "s.sqlite"),
                          publish=False, jobs=[{"id": "x", "kind": "validate"}])
    run = Overnight(cfg, base / "20261102-0000", stop_file=tmp_path / "STOP", progress=False)
    now = _job("c/9", "swarm", ["--sections", "9"], "config")
    other = _job("c/10", "swarm", ["--sections", "10"], "config")
    run.state["jobs"] = [now, other]
    assert [p.parent.name for p in run.peer_ledgers(now)] == ["sw_9"]
    assert run.peer_ledgers(other) == []
    assert "--peer-ledger" in run.job_command(now) and "--peer-ledger" not in run.job_command(other)


def test_autokey_primer_note_in_the_language_doc():
    from lpswarm.swarm.generators import LANGUAGE_DOC
    assert "ONE proposal covers all primers" in LANGUAGE_DOC

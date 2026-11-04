"""Unattended queue runner: `lpswarm overnight`.

Runs a list of jobs (tier tests, swarms, baselines), each as a subprocess with its own
log, and keeps a SUMMARY.md up to date. Jobs that use different backends (the Claude
plan, the Codex plan, one GPU's Ollama server, an API; see router.backend_key) run at
the same time, up to `max_parallel`; jobs that share one wait their turn, in queue
order. The main window shows every running job's log lines as they appear, prefixed
with the job id. Safe to leave alone:

- a crashing job fails that job, not the run;
- state is saved after every step; re-running the command resumes (finished jobs
  are skipped, swarms are split per section, tier tests use --resume);
- Windows is kept awake while it runs (the screen may still turn off);
- Ollama is restarted (Windows) if a health check finds it down;
- jobs that use a paid API model with prices set to 0 are refused (a USD cap
  could not protect you);
- results (report .md/.csv and SUMMARY.md only) can be pushed to a `results`
  branch so you can read them on GitHub from your phone.

Optional supervisor: a model with role "supervisor" (e.g. Claude Code Opus on your
plan, tools off) is shown a status digest every `tick_minutes` and after each job,
and answers with JSON actions from a fixed menu (note, add_job, skip_job,
retry_job, restart_ollama, stop). Code validates every action; the supervisor has
no tools and cannot change code, scores or prompts.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path

from lpswarm.textio import read_text

STATUSES = ("pending", "running", "done", "failed", "skipped", "interrupted", "blocked")
KINDS = ("tiertest", "swarm", "baseline", "validate")
MAX_ROUNDS_ADDED = 8
MAX_PER_ROUND_ADDED = 8
MIN_FORCED_TICK_S = 600   # after-job supervisor check-ins at least 10 minutes apart


# --------------------------------------------------------------------- config
@dataclass
class OvernightConfig:
    models: str = "config/models.toml"
    spend_ledger: str = "reports/model_spend.sqlite"
    supervisor: str | None = None
    tick_minutes: float = 60.0
    publish: bool = True
    results_branch: str = "results"
    until: str | None = None            # "HH:MM" local time
    max_added_jobs: int = 5
    max_parallel: int = 2               # jobs at once (only ones on different backends)
    manifest: str = "data/lp/manifest.json"
    alphabet: str = "data/alphabet/gematria_primus.json"
    jobs: list[dict] = field(default_factory=list)


def load_config(path: str | Path) -> OvernightConfig:
    data = tomllib.loads(read_text(path))
    sec = dict(data.get("overnight", {}))
    jobs = list(data.get("job", []))
    if not jobs:
        raise ValueError(f"{path}: no [[job]] entries")
    seen = set()
    for j in jobs:
        if "id" not in j or "kind" not in j:
            raise ValueError(f"{path}: every [[job]] needs id and kind")
        if j["kind"] not in KINDS:
            raise ValueError(f"{path}: job {j['id']}: kind must be one of {KINDS}")
        if j["id"] in seen:
            raise ValueError(f"{path}: duplicate job id {j['id']}")
        seen.add(j["id"])
        if not isinstance(j.get("args", []), list):
            raise ValueError(f"{path}: job {j['id']}: args must be a list of strings")
        if "lane" in j and not isinstance(j["lane"], str):
            raise ValueError(f"{path}: job {j['id']}: lane must be a string")
    known = {k for k in OvernightConfig.__dataclass_fields__ if k != "jobs"}
    bad = set(sec) - known
    if bad:
        raise ValueError(f"{path}: unknown [overnight] keys {sorted(bad)}")
    cfg = OvernightConfig(**sec, jobs=jobs)
    if int(cfg.max_parallel) < 1:
        raise ValueError(f"{path}: max_parallel must be >= 1")
    return cfg


# ------------------------------------------------------------------ manifest
def manifest_sections(manifest: str | Path, which: str) -> list[int]:
    """'unsolved' (source note '?'), 'solved', 'all', or a comma list of indexes."""
    man = json.loads(read_text(manifest))
    secs = [s for s in man["sections"] if s.get("runes", 0) >= 8]
    if which == "unsolved":
        return [s["index"] for s in secs if s.get("source_note", "").strip() == "?"]
    if which == "solved":
        return [s["index"] for s in secs if s.get("source_note", "").strip() not in ("?", "")]
    if which == "all":
        return [s["index"] for s in secs]
    idx = {s["index"] for s in man["sections"]}
    out = [int(x) for x in str(which).split(",") if x.strip()]
    bad = [x for x in out if x not in idx]
    if bad:
        raise ValueError(f"unknown section index(es) {bad}")
    return out


def _arg_value(args: list[str], flag: str) -> str | None:
    if flag in args:
        i = args.index(flag)
        return args[i + 1] if i + 1 < len(args) else None
    return None


def _set_arg(args: list[str], flag: str, value: str) -> list[str]:
    args = list(args)
    if flag in args:
        args[args.index(flag) + 1] = value
    else:
        args += [flag, value]
    return args


def expand_jobs(cfg: OvernightConfig) -> list[dict]:
    """State entries for the configured jobs; swarm/baseline jobs over several sections
    are split into one sub-job per section so a restart only redoes the unfinished one."""
    out = []
    for j in cfg.jobs:
        args = [str(a) for a in j.get("args", [])]
        sections = _arg_value(args, "--sections")
        if j["kind"] in ("swarm", "baseline") and sections and "--manifest" in args:
            man = _arg_value(args, "--manifest") or cfg.manifest
            for idx in manifest_sections(man, sections):
                out.append(_job(f"{j['id']}/{idx}", j["kind"], _set_arg(args, "--sections", str(idx)),
                                "config", j.get("note", ""), j.get("lane")))
        else:
            out.append(_job(j["id"], j["kind"], args, "config", j.get("note", ""), j.get("lane")))
    return out


def _job(jid: str, kind: str, args: list[str], added_by: str, note: str = "",
         lane: str | None = None) -> dict:
    j = {"id": jid, "kind": kind, "args": args, "status": "pending", "added_by": added_by,
         "note": note, "retries": 0, "started": None, "ended": None, "returncode": None,
         "reason": None}
    if lane:
        j["lane"] = lane
    return j


@dataclass
class _Running:
    job: dict
    proc: subprocess.Popen
    logf: object
    log_path: Path
    t_start: float
    last_beat: float
    offset: int = 0          # bytes of job.log already echoed to the console
    partial: str = ""
    killed: str | None = None


# ---------------------------------------------------------------- the runner
def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _until_epoch(until: str | None) -> float | None:
    if not until:
        return None
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", until.strip())
    if not m:
        raise ValueError("until must be HH:MM")
    now = datetime.now()
    t = now.replace(hour=int(m.group(1)), minute=int(m.group(2)), second=0, microsecond=0)
    if t <= now:
        t += timedelta(days=1)
    return t.timestamp()


class KeepAwake:
    """Ask Windows not to sleep while the run is active (screen may still turn off)."""
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001

    def __enter__(self):
        if os.name == "nt":
            try:
                import ctypes
                ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS | self.ES_SYSTEM_REQUIRED)
            except Exception:  # noqa: BLE001
                pass
        return self

    def __exit__(self, *exc):
        if os.name == "nt":
            try:
                import ctypes
                ctypes.windll.kernel32.SetThreadExecutionState(self.ES_CONTINUOUS)
            except Exception:  # noqa: BLE001
                pass


class Overnight:
    def __init__(self, cfg: OvernightConfig, run_dir: str | Path, *, publish: bool | None = None,
                 router=None, stop_file: str | Path = "STOP", poll_s: float = 5.0,
                 python: str | None = None, progress: bool = True, retry_failed: bool = False,
                 heartbeat_s: float = 300.0, echo_jobs: bool = True, echo_max_lines: int = 20):
        self.cfg = cfg
        self.dir = Path(run_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.dir / "state.json"
        self.publish_enabled = cfg.publish if publish is None else publish
        self.router = router
        self.stop_file = Path(stop_file)
        self.poll_s = poll_s
        self.python = python or sys.executable
        self.progress = progress
        self.until = _until_epoch(cfg.until)
        self.heartbeat_s = heartbeat_s
        self.echo_jobs = echo_jobs
        self.echo_max_lines = echo_max_lines
        self.max_parallel = max(1, int(cfg.max_parallel))
        self.running: dict[str, _Running] = {}
        self._last_wait = ""
        self._blocked_sink: dict | None = None
        self._specs_cache: tuple[float, dict] | None = None
        self.state = self._load_state()
        self.last_tick = 0.0
        if retry_failed:
            for j in self.state["jobs"]:
                if j["status"] in ("failed", "blocked"):
                    j.update(status="pending", reason="retry requested")
            self.log("failed and blocked jobs reset to pending (--retry-failed)")

    # ----------------------------------------------------------------- state
    def _load_state(self) -> dict:
        if self.state_path.is_file():
            st = json.loads(self.state_path.read_text(encoding="utf-8"))
            for j in st["jobs"]:
                if j["status"] == "running":       # killed or crashed mid-job: resume it
                    j["status"] = "interrupted"
            st["status"] = "running"
            st.setdefault("events", []).append(f"{_now()} resumed")
            return st
        return {"started": _now(), "status": "running", "jobs": expand_jobs(self.cfg),
                "notes": [], "events": [f"{_now()} started"], "added_jobs": 0, "ticks": 0}

    def save(self) -> None:
        self.state["updated"] = _now()
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        tmp.replace(self.state_path)

    def log(self, msg: str) -> None:
        self.state["events"].append(f"{_now()} {msg}")
        self.state["events"] = self.state["events"][-200:]
        if self.progress:
            print(f"[overnight] {msg}", flush=True)

    # ------------------------------------------------------------- job paths
    def job_dir(self, job: dict) -> Path:
        return self.dir / re.sub(r"[^A-Za-z0-9_.-]+", "_", job["id"])

    def job_command(self, job: dict) -> list[str]:
        d = self.job_dir(job)
        args = list(job["args"])
        models = self.cfg.models
        if job["kind"] == "tiertest":
            args = _set_arg(args, "--out", str(d))
            if Path(models).is_file() and "--models" not in args:
                args += ["--models", models]
            args = _set_arg(args, "--spend-ledger", self.cfg.spend_ledger)
            if (d / "run.json").is_file():
                args.append("--resume")
        elif job["kind"] in ("swarm", "baseline"):
            args = _set_arg(args, "--report-dir", str(d))
            args = _set_arg(args, "--ledger", str(d / "ledger.sqlite"))
            if job["kind"] == "swarm" and job.get("brief"):
                d.mkdir(parents=True, exist_ok=True)
                (d / "brief.txt").write_text(job["brief"], encoding="utf-8")
                args = _set_arg(args, "--brief-file", str(d / "brief.txt"))
            if job["kind"] == "swarm":
                if Path(models).is_file() and "--models" not in args:
                    args += ["--models", models]
                args = _set_arg(args, "--spend-ledger", self.cfg.spend_ledger)
        elif job["kind"] == "validate":
            args = _set_arg(args, "--out", str(d))
        # Not --quiet: job.log gets round-by-round progress (and one line per model call).
        return [self.python, "-m", "lpswarm", job["kind"], *args]

    def job_models(self, job: dict) -> list[str]:
        names = []
        for flag in ("--arms", "--generators", "--ranker"):
            v = _arg_value(job["args"], flag)
            if v:
                names += [x.strip() for x in v.split(",") if x.strip()]
        return [n for n in names if n != "baseline" and not n.startswith("random_program")]

    def _specs(self) -> dict:
        try:
            mtime = Path(self.cfg.models).stat().st_mtime
        except OSError:
            return {}
        if self._specs_cache is None or self._specs_cache[0] != mtime:
            try:
                from lpswarm.router.base import load_model_specs
                self._specs_cache = (mtime, {s.name: s for s in load_model_specs(self.cfg.models)})
            except Exception:  # noqa: BLE001 - preflight reports a broken config
                self._specs_cache = (mtime, {})
        return self._specs_cache[1]

    def job_resources(self, job: dict) -> set[str]:
        """What a job occupies while it runs: the backend of each model it uses (a plan
        quota, a GPU's Ollama server, an API), plus its `lane` if set. Jobs without
        models (baselines, random-only tests) take "cpu". Jobs sharing anything run one
        after another."""
        from lpswarm.router.router import backend_key
        specs = self._specs()
        res = set()
        for n in self.job_models(job):
            res.add(backend_key(specs[n]) if n in specs else f"model:{n}")
        if not res:
            res.add("cpu")
        if job.get("lane"):
            res.add(f"lane:{job['lane']}")
        return res

    # ---------------------------------------------------------------- checks
    def preflight(self, job: dict) -> str | None:
        """Reason to refuse the job, or None. Also restarts Ollama if it is down."""
        names = self.job_models(job)
        if not names:
            return None
        try:
            from lpswarm.router.base import load_model_specs
            specs = {s.name: s for s in load_model_specs(self.cfg.models)}
        except Exception as exc:  # noqa: BLE001
            return f"models config unusable: {exc}"
        for n in names:
            s = specs.get(n)
            if s is None:
                return f"model {n} is not in {self.cfg.models}"
            if s.provider == "openai_compatible" and not (s.extra.get("price_in_per_mtok")
                                                          or s.extra.get("price_out_per_mtok")):
                return (f"model {n}: prices are 0 in {self.cfg.models}, so its USD cap cannot "
                        "work; fill in price_in_per_mtok / price_out_per_mtok")
            if s.provider == "openai_compatible" and s.api_key_env and not os.environ.get(s.api_key_env):
                return f"model {n}: environment variable {s.api_key_env} is not set"
        if any(specs[n].provider == "ollama" for n in names):
            from lpswarm.doctor import run_checks
            down = [c for c in run_checks(self.cfg.models)
                    if c.status == "FAIL" and "not reachable" in c.detail]
            if down:
                self.restart_ollama("Ollama not reachable before " + job["id"])
        return None

    def restart_ollama(self, why: str) -> None:
        script = Path("scripts") / "start_ollama.ps1"
        if os.name != "nt" or not script.is_file():
            self.log(f"Ollama restart wanted ({why}) but only supported on Windows")
            return
        self.log(f"restarting Ollama: {why}")
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)],
                       capture_output=True, timeout=300)

    def should_stop(self) -> str | None:
        if self.stop_file.exists():
            return "STOP file"
        if self.until is not None and time.time() >= self.until:
            return f"until {self.cfg.until}"
        if self.state.get("stop_requested"):
            return self.state["stop_requested"]
        return None

    # ------------------------------------------------------------------- run
    def run(self) -> dict:
        with KeepAwake():
            self.save()
            self.write_summary()
            try:
                while True:
                    reason = self.should_stop()
                    if reason:
                        self.log(f"stopping: {reason}")
                        for r in list(self.running.values()):
                            self.kill(r, reason)
                        self.poll_jobs(wait=True)
                        break
                    self.start_ready_jobs()
                    if not self.running:
                        if not any(j["status"] in ("pending", "interrupted") for j in self.state["jobs"]):
                            self.log("queue empty")
                            break
                        continue   # every startable job was refused; look again
                    time.sleep(self.poll_s)
                    self.poll_jobs()
                    self.maybe_tick()
            finally:
                for r in list(self.running.values()):   # crash or Ctrl+C: leave nothing behind
                    self.kill(r, "runner exiting")
                if self.running:
                    self.poll_jobs(wait=True)
            self.state["status"] = "finished" if not any(
                j["status"] in ("pending", "interrupted") for j in self.state["jobs"]) else "stopped"
            self.save()
            self.write_summary()
            self.publish()
        return self.state

    def start_ready_jobs(self) -> None:
        """Start queued jobs, in order, whose backends are free, up to max_parallel."""
        busy: dict[str, str] = {}
        for r in self.running.values():
            for res in self.job_resources(r.job):
                busy[res] = r.job["id"]
        waiting = ""
        blocked: dict[str, list[str]] = {}       # reason -> job ids (one console line each)
        self._blocked_sink = blocked
        for job in self.state["jobs"]:
            if len(self.running) >= self.max_parallel:
                break
            if job["status"] not in ("pending", "interrupted"):
                continue
            res = self.job_resources(job)
            clash = sorted(res & busy.keys())
            if clash:
                if not waiting:
                    waiting = (f"{job['id']} waiting: {clash[0]} in use by {busy[clash[0]]}")
                continue
            started = self.start_job(job)
            if started is not None:
                for x in res:
                    busy[x] = job["id"]
                if len(self.running) > 1:
                    self.log(f"{len(self.running)} running: {', '.join(self.running)}")
            elif job["status"] != "blocked":
                after = job["status"]
                self.log(f"{job['id']}: {after}")
        self._blocked_sink = None
        for reason, ids in blocked.items():
            if len(ids) == 1:
                self.log(f"{ids[0]}: blocked: {reason}")
            else:
                self.log(f"blocked {len(ids)} jobs ({ids[0]} ... {ids[-1]}): {reason}")
        if waiting and waiting != self._last_wait:
            self.log(waiting)
        self._last_wait = waiting

    def start_job(self, job: dict) -> _Running | None:
        refuse = self.preflight(job)
        if refuse:
            job.update(status="blocked", reason=refuse, ended=_now())
            sink = getattr(self, "_blocked_sink", None)
            if sink is not None:
                sink.setdefault(refuse, []).append(job["id"])
            else:
                self.log(f"{job['id']}: blocked: {refuse}")
            self.save()
            return None
        d = self.job_dir(job)
        d.mkdir(parents=True, exist_ok=True)
        cmd = self.job_command(job)
        kw: dict = {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt" \
            else {"start_new_session": True}
        from lpswarm.router.router import PRICES_ZERO_WARNING
        # The prices-are-0 warning is shown once in the main window; not again per job.
        warn = ",".join(x for x in (os.environ.get("PYTHONWARNINGS", ""),
                                    f"ignore:{PRICES_ZERO_WARNING}") if x)
        env = dict(os.environ, LPSWARM_LOG_CALLS="1", PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8",
                   PYTHONWARNINGS=warn, LPSWARM_TRANSCRIPT=str(d / "transcript.jsonl"))
        log_path = d / "job.log"
        logf = log_path.open("a", encoding="utf-8")
        logf.write(f"\n===== {_now()} {' '.join(cmd)}\n")
        logf.flush()
        offset = log_path.stat().st_size
        try:
            proc = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, env=env, **kw)
        except OSError as exc:
            logf.close()
            job.update(status="failed", reason=f"could not start: {exc}", ended=_now())
            self.save()
            return None
        job.update(status="running", started=job["started"] or _now(), reason=None)
        lanes = ", ".join(sorted(self.job_resources(job)))
        self.log(f"{job['id']}: start (uses {lanes})")
        now = time.monotonic()
        r = _Running(job, proc, logf, log_path, now, now, offset=offset)
        self.running[job["id"]] = r
        self.save()
        self.write_summary()
        return r

    def kill(self, r: _Running, reason: str) -> None:
        if r.killed is None:
            r.killed = reason
            from lpswarm.router.cli_adapters import _kill_tree
            try:
                _kill_tree(r.proc)
            except Exception:  # noqa: BLE001
                pass

    def poll_jobs(self, wait: bool = False) -> None:
        """Echo new log lines, print heartbeats, honour kill requests, finish exited jobs."""
        for jid, r in list(self.running.items()):
            if r.killed is None and r.job.get("kill_requested"):
                self.kill(r, r.job.pop("kill_requested"))
            if wait:
                try:
                    r.proc.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    pass
            self.echo_log(r)
            done = r.proc.poll() is not None
            if not done and time.monotonic() - r.last_beat >= self.heartbeat_s:
                r.last_beat = time.monotonic()
                mins = (r.last_beat - r.t_start) / 60
                tail = _log_tail(r.log_path, 1)
                self.log(f"{jid}: running {mins:.0f} min | {tail[-1] if tail else 'no output yet'}")
                self.save()
                self.write_summary()
            if done:
                self.finish_job(r)

    def echo_log(self, r: _Running) -> None:
        """Print a running job's new log lines to the console, prefixed with its id."""
        if not (self.progress and self.echo_jobs):
            return
        try:
            with open(r.log_path, "rb") as f:
                f.seek(r.offset)
                data = f.read()
        except OSError:
            return
        if not data:
            return
        r.offset += len(data)
        text = r.partial + data.decode("utf-8", errors="replace")
        lines = text.split("\n")
        r.partial = lines.pop()          # an unfinished last line waits for the next poll
        lines = [x.rstrip() for x in lines if x.strip() and not _noise(x)]
        extra = len(lines) - self.echo_max_lines
        if extra > 0:
            lines = lines[:self.echo_max_lines // 2] + [f"... (+{extra} more lines in job.log)"] \
                + lines[-(self.echo_max_lines // 2):]
        for x in lines:
            _echo(f"[{r.job['id']}] {x[:240]}")

    def finish_job(self, r: _Running) -> None:
        job = r.job
        self.running.pop(job["id"], None)
        try:
            r.logf.close()
        except OSError:
            pass
        if r.partial.strip() and self.progress and self.echo_jobs:
            _echo(f"[{job['id']}] {r.partial.rstrip()[:240]}")
        job["returncode"] = r.proc.returncode
        job["ended"] = _now()
        if r.killed:
            job["status"] = "skipped" if r.killed == "skip" else "interrupted"
            job["reason"] = r.killed
        else:
            job["status"] = "done" if r.proc.returncode == 0 else "failed"
        mins = (time.monotonic() - r.t_start) / 60
        self.log(f"{job['id']}: {job['status']} (exit {r.proc.returncode}, {mins:.0f} min)")
        self.save()
        if job["status"] in ("done", "failed", "skipped") or (r.killed == "skip"):
            self.after_job(job)
        else:
            self.write_summary()

    def run_job(self, job: dict) -> None:
        """Run one job to the end (used by tests and as the serial path)."""
        r = self.start_job(job)
        while r is not None and job["id"] in self.running:
            time.sleep(self.poll_s)
            reason = self.should_stop()
            if reason:
                self.kill(r, reason)
            self.poll_jobs(wait=bool(reason))

    def after_job(self, job: dict) -> None:
        self.write_summary()
        self.publish()
        self.maybe_tick(force=True)

    # ------------------------------------------------------------- summary
    def job_headline(self, job: dict) -> list[str]:
        d = self.job_dir(job)
        out: list[str] = []
        if job["kind"] == "tiertest" and (d / "tiertest.json").is_file():
            res = json.loads((d / "tiertest.json").read_text(encoding="utf-8"))
            for s in res.get("summary", []):
                if s["length"] == "all":
                    out.append(f"  - {s['arm']}: recall {s['recall']:.2f} ({s['recovered']}/{s['cases']}), "
                               f"{s['attempts']} attempts, {s['model_calls']} model calls, ${s['usd']:.4f}")
        elif (d / "report.json").is_file():
            rep = json.loads((d / "report.json").read_text(encoding="utf-8"))
            from lpswarm.reports import short_note
            for t in rep.get("targets", []):
                out.append(f"  - {t['label']}: {t['attempts']} attempts, {t['hypotheses']} hypotheses, "
                           f"**{t['final_passes']} final pass(es)**"
                           + (f", stopped: {t['stopped']}" if t.get("stopped") else "")
                           + (f" (caution: {short_note(t['symbols'])})" if short_note(t.get("symbols", 999))
                              else ""))
                for ld in t.get("leads", [])[:3]:
                    if ld["final"]:
                        out.append(f"    - FINAL by {ld['by']}: `{ld['key']}` -> `{ld['plaintext'][:70]}`")
        if not out and job["status"] == "done" and job["kind"] in ("swarm", "baseline"):
            skips = [x for x in _log_tail(d / "job.log", 20) if x.startswith("skip ")]
            if skips:      # e.g. a section below --min-length: say why there is no result
                out.append(f"  - {skips[-1]}")
        if job["status"] == "failed" and (d / "job.log").is_file():
            tail = (d / "job.log").read_text(encoding="utf-8", errors="replace").splitlines()[-12:]
            out.append("  - last log lines:")
            out += [f"    > {x[:160]}" for x in tail]
        return out

    def usage_lines(self) -> list[str]:
        if self.router is None:
            return []
        lines = []
        for n in self.router.names():
            try:
                st = self.router.window_status(n)
                spent = self.router.spent(n)
            except Exception:  # noqa: BLE001
                continue
            from lpswarm.router.limits import pause_text
            pause = pause_text(st, "%H:%M")
            if st["calls"] or spent or pause:
                lines.append(f"- {n}: {st['calls']} call(s) in the last {st['window_hours']:g}h "
                             f"(cap {st['cap'] or 'none'}), spent ${spent:.4f}{pause}")
        return lines

    def write_summary(self) -> Path:
        st = self.state
        counts = {s: sum(1 for j in st["jobs"] if j["status"] == s) for s in STATUSES}
        lines = [f"# Overnight run {self.dir.name}", "",
                 f"Started {st['started']}, updated {st.get('updated', _now())}, status "
                 f"**{st['status']}**. Jobs: " + ", ".join(f"{k} {v}" for k, v in counts.items() if v),
                 "", "| job | status | started | ended | note |", "| --- | --- | --- | --- | --- |"]
        for j in st["jobs"]:
            note = j.get("reason") or j.get("note") or ""
            if j["added_by"] != "config":
                note = f"added by {j['added_by']}. {note}"
            lines.append(f"| {j['id']} | {j['status']} | {j['started'] or ''} | {j['ended'] or ''} | "
                         f"{note[:120]} |")
        running = [j for j in st["jobs"] if j["status"] == "running"]
        if running:
            lines += ["", "## Now running", ""]
            for j in running:
                lines.append(f"**{j['id']}** (since {j['started']}), latest log lines:")
                lines += ["```"] + _log_tail(self.job_dir(j) / "job.log", 10) + ["```"]
        lines += ["", "## Results so far", ""]
        any_res = False
        for j in st["jobs"]:
            head = self.job_headline(j)
            if head:
                any_res = True
                lines.append(f"- **{j['id']}** ({j['status']})")
                lines += head
        if not any_res:
            lines.append("Nothing finished yet.")
        usage = self.usage_lines()
        if usage:
            lines += ["", "## Model usage", ""] + usage
        if st["notes"]:
            lines += ["", "## Supervisor notes", ""] + [f"- {n}" for n in st["notes"][-30:]]
        lines += ["", "## Events", ""] + [f"- {e}" for e in st["events"][-25:]]
        path = self.dir / "SUMMARY.md"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    # ----------------------------------------------------------- supervisor
    def maybe_tick(self, force: bool = False) -> None:
        if not self.cfg.supervisor or self.router is None:
            return
        gap = time.time() - self.last_tick
        if not force and gap < self.cfg.tick_minutes * 60:
            return
        if force and gap < MIN_FORCED_TICK_S:
            return   # after-job check-ins at most every few minutes (saves plan quota)
        self.last_tick = time.time()
        self.state["ticks"] += 1
        try:
            reply = self.router.complete(self.cfg.supervisor, supervisor_prompt(self), role="supervisor",
                                         task_id=f"overnight:{self.dir.name}#tick{self.state['ticks']}",
                                         temperature=0.2, max_tokens=1500).text
        except Exception as exc:  # noqa: BLE001 - a paused or failing supervisor never stops the run
            self.log(f"supervisor unavailable: {str(exc)[:160]}")
            return
        for msg in apply_supervisor_reply(self, reply):
            self.log(f"supervisor: {msg}")
        self.save()
        self.write_summary()

    # --------------------------------------------------------------- publish
    def publish(self) -> None:
        if not self.publish_enabled:
            return
        try:
            msg = publish_results(self.dir, self.cfg.results_branch)
            self.log(f"published: {msg}")
        except Exception as exc:  # noqa: BLE001 - publishing never stops the run
            self.log(f"publish failed (will retry later): {str(exc)[:200]}")
        self.save()


# ---------------------------------------------------------- supervisor menu
SUPERVISOR_MENU = """You are supervising an unattended cryptanalysis run while its owner is away.
Code runs the jobs; you can only answer with JSON choosing actions from this menu:
  {"type": "note", "text": "..."}                     a short note for the owner's summary
  {"type": "add_job", "sections": "unsolved" | [section indexes], "generators": [model names],
   "rounds": 1-8, "per_round": 1-8, "reason": "...",
   "brief": "..."}                                     queue a swarm job (limited per night)
  {"type": "skip_job", "id": "..."}                    skip a pending or running job
  {"type": "retry_job", "id": "..."}                   retry a failed/interrupted job (once)
  {"type": "restart_ollama", "reason": "..."}          restart the local model servers
  {"type": "stop", "reason": "..."}                    end the run early
Reply exactly: {"actions": [...]} . Prefer few actions; an empty list is fine.
Do not add jobs that repeat ones already queued. A FINAL lead is a strong candidate that the
owner should read; don't stop the run because of one.

Delegating: you are the planner; the proposer models do the volume work. To hand work to a
model (e.g. claude-sonnet), add_job with it in "generators" and a "brief" (up to 2000
characters) that every generator in that job reads before proposing. A good brief is
concrete: which cipher-program ideas to try on these sections and why (stream kinds,
sequences, offsets, skip rules, transpositions), what the digest shows was already tried or
came close, and what to avoid. The proposers reply in a fixed JSON language that code checks;
the brief only steers their choices. Keep each job to the sections the brief is about."""


def supervisor_prompt(run: Overnight) -> list[dict]:
    summary = (run.dir / "SUMMARY.md").read_text(encoding="utf-8") if (run.dir / "SUMMARY.md").is_file() \
        else ""
    gens = []
    if run.router is not None:
        from lpswarm.router.base import Role
        gens = run.router.names(Role.PROPOSER)
    extra = (f"Configured proposer models: {', '.join(gens) or 'none'}. Jobs added so far tonight: "
             f"{run.state['added_jobs']} of {run.cfg.max_added_jobs}. Time now: {_now()}.")
    digest = section_digest(run)
    return [{"role": "system", "content": SUPERVISOR_MENU},
            {"role": "user", "content": extra + "\n\nCurrent summary:\n" + summary[-9000:]
             + ("\n\nPer-section results so far (best leads, for writing briefs):\n" + digest
                if digest else "")}]


def section_digest(run: Overnight, per_section: int = 4, limit_chars: int = 6000) -> str:
    """Best leads per finished swarm section (verdict, margin, key, who proposed it), so
    the supervisor can write briefs that build on what came close."""
    rows: dict[str, list[str]] = {}
    for j in run.state["jobs"]:
        if j["kind"] != "swarm" or j["status"] not in ("done", "interrupted", "skipped"):
            continue
        rp = run.job_dir(j) / "report.json"
        if not rp.is_file():
            continue
        try:
            rep = json.loads(rp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for t in rep.get("targets", []):
            key = f"{t['label']} ({t['symbols']} runes)"
            lst = rows.setdefault(key, [])
            lst.append(f"  job {j['id']}: {t['attempts']} attempts, {t['hypotheses']} hypotheses, "
                       f"{t['final_passes']} final")
            for ld in t.get("leads", [])[:per_section]:
                lst.append(f"    {'FINAL ' if ld['final'] else ''}{ld['verdict']} margin "
                           f"{ld['margin']:+.2f} by {ld['by']}: {str(ld['key'])[:140]}")
    text = "\n".join(f"{k}\n" + "\n".join(v) for k, v in rows.items())
    return text[-limit_chars:]


def apply_supervisor_reply(run: Overnight, reply: str) -> list[str]:
    """Validate and apply the supervisor's actions. Returns a log line per action."""
    from lpswarm.swarm.generators import _iter_json_values
    actions = None
    for val in _iter_json_values(reply[:50_000]):
        if isinstance(val, dict) and isinstance(val.get("actions"), list):
            actions = val["actions"]
            break
    if actions is None:
        return ["reply had no {\"actions\": [...]} object; ignored"]
    out = []
    jobs = {j["id"]: j for j in run.state["jobs"]}
    for a in actions[:10]:
        if not isinstance(a, dict):
            out.append("ignored a non-object action")
            continue
        t = a.get("type")
        if t == "note":
            text = str(a.get("text", ""))[:1000].strip()
            if text:
                run.state["notes"].append(f"{_now()}: {text}")
                out.append("note: " + (text if len(text) <= 300 else text[:297] + "..."))
        elif t == "add_job":
            out.append(_add_job(run, a))
        elif t == "skip_job":
            j = jobs.get(str(a.get("id")))
            if j and j["status"] in ("pending", "interrupted"):
                j.update(status="skipped", reason="skipped by supervisor")
                out.append(f"skipped {j['id']}")
            elif j and j["status"] == "running":
                j["kill_requested"] = "skip"
                out.append(f"stopping running job {j['id']}")
            else:
                out.append(f"skip_job ignored (no pending/running job {a.get('id')!r})")
        elif t == "retry_job":
            j = jobs.get(str(a.get("id")))
            if j and j["status"] in ("failed", "interrupted", "blocked") and j["retries"] < 1:
                j.update(status="pending", retries=j["retries"] + 1, reason="retry by supervisor")
                out.append(f"retrying {j['id']}")
            else:
                out.append(f"retry_job ignored for {a.get('id')!r}")
        elif t == "restart_ollama":
            run.restart_ollama(str(a.get("reason", "supervisor request"))[:200])
            out.append("Ollama restart requested")
        elif t == "stop":
            run.state["stop_requested"] = "supervisor: " + str(a.get("reason", ""))[:200]
            out.append("stop requested")
        else:
            out.append(f"unknown action {str(t)[:30]!r} ignored")
    return out


def _add_job(run: Overnight, a: dict) -> str:
    try:
        from lpswarm.router.base import Role
        allowed = set(run.router.names(Role.PROPOSER)) | {"random_program"} if run.router else {"random_program"}
        gens = [str(g) for g in a.get("generators", []) if str(g) in allowed]
        if not gens:
            return "add_job refused: no configured proposer among generators"
        rounds = max(1, min(MAX_ROUNDS_ADDED, int(a.get("rounds", 3))))
        per_round = max(1, min(MAX_PER_ROUND_ADDED, int(a.get("per_round", 6))))
        sec = a.get("sections", "unsolved")
        which = sec if isinstance(sec, str) else ",".join(str(int(x)) for x in sec)
        sections = manifest_sections(run.cfg.manifest, which)
    except (ValueError, TypeError) as exc:
        return f"add_job refused: {exc}"
    if not sections:
        return "add_job refused: no sections"
    if run.state["added_jobs"] >= run.cfg.max_added_jobs:
        return "add_job refused: nightly limit reached"
    from lpswarm.swarm.generators import MAX_BRIEF_CHARS
    brief = str(a.get("brief") or "").strip()[:MAX_BRIEF_CHARS]
    n = run.state["added_jobs"] + 1
    base = f"sup{n}"
    for idx in sections:
        args = ["--manifest", run.cfg.manifest, "--alphabet", run.cfg.alphabet, "--sections", str(idx),
                "--generators", ",".join(gens), "--rounds", str(rounds), "--per-round", str(per_round)]
        job = _job(f"{base}/{idx}", "swarm", args, "supervisor", str(a.get("reason", ""))[:200])
        if brief:
            job["brief"] = brief
        run.state["jobs"].append(job)
    run.state["added_jobs"] = n
    if brief:
        run.state["notes"].append(f"{_now()}: brief for {base} ({','.join(gens)}): {brief}")
    return (f"added {base}: swarm on {len(sections)} section(s) with {','.join(gens)}"
            + (f"; brief: {brief[:200]}" + ("..." if len(brief) > 200 else "") if brief else ""))


# ---------------------------------------------------------------- publishing
def _git(args: list[str], cwd: str | Path) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:3])}: {(r.stderr or r.stdout).strip()[:300]}")
    return r


def publish_results(run_dir: Path, branch: str = "results", repo: str | Path = ".",
                    worktree: str | Path = ".results-worktree") -> str:
    """Commit SUMMARY.md and report .md/.csv files of this run to `branch` (an orphan
    branch kept in a separate worktree) and push it. Never copies ledgers, logs or configs."""
    if shutil.which("git") is None:
        raise RuntimeError("git not found")
    repo = Path(repo).resolve()
    wt = (repo / worktree) if not Path(worktree).is_absolute() else Path(worktree)
    if not (wt / ".git").exists():
        remote_has = subprocess.run(["git", "ls-remote", "--exit-code", "--heads", "origin", branch],
                                    cwd=repo, capture_output=True, timeout=120).returncode == 0
        local_has = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
                                   cwd=repo, capture_output=True).returncode == 0
        if local_has:
            _git(["worktree", "add", str(wt), branch], repo)
        elif remote_has:
            _git(["fetch", "origin", branch], repo)
            _git(["worktree", "add", "-b", branch, str(wt), f"origin/{branch}"], repo)
        else:
            _git(["worktree", "add", "--detach", str(wt)], repo)
            _git(["checkout", "--orphan", branch], wt)
            _git(["rm", "-rf", "--quiet", "."], wt)
    dest = wt / run_dir.name
    dest.mkdir(parents=True, exist_ok=True)
    copied = 0
    for src in [run_dir / "SUMMARY.md", *run_dir.rglob("*.md"), *run_dir.rglob("*.csv")]:
        if not src.is_file():
            continue
        rel = src.relative_to(run_dir)
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        copied += 1
    _git(["add", "-A", "."], wt)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=wt).returncode == 0:
        return "nothing new"
    _git(["commit", "-q", "-m", f"results: {run_dir.name} {_now()}"], wt)
    _git(["push", "-q", "-u", "origin", branch], wt)
    return f"{copied} file(s) to branch {branch}"


def _noise(line: str) -> bool:
    """Python warning output in a job log: the warning line and the source line after it."""
    return "UserWarning" in line or "load_model_specs(" in line


def _echo(line: str) -> None:
    try:
        print(line, flush=True)
    except UnicodeEncodeError:   # a console that cannot show rune glyphs
        enc = getattr(sys.stdout, "encoding", None) or "ascii"
        print(line.encode(enc, errors="replace").decode(enc, errors="replace"), flush=True)


def _log_tail(path: Path, n: int) -> list[str]:
    """Last n meaningful lines of a job log (skips Python warning noise)."""
    try:
        with open(path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 16384))
            text = f.read().decode("utf-8", errors="replace")
    except OSError:
        return []
    lines = [x.rstrip() for x in text.splitlines() if x.strip()]
    lines = [x for x in lines if not _noise(x)]
    return [x[:200] for x in lines[-n:]]


def latest_unfinished(base: Path) -> Path | None:
    if not base.is_dir():
        return None
    for d in sorted((p for p in base.iterdir() if p.is_dir()), reverse=True):
        st = d / "state.json"
        if st.is_file():
            try:
                if json.loads(st.read_text(encoding="utf-8")).get("status") != "finished":
                    return d
            except json.JSONDecodeError:
                continue
    return None

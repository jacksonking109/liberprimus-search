"""`lpswarm doctor`: check that everything needed for a run is in place.

Read-only. Never prints secrets: for API models it only says whether the
environment variable is set. `--ping` (opt-in) sends one tiny prompt per model,
which costs a fraction of a cent on paid APIs.
"""
from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

OK, WARN, FAIL = "OK", "WARN", "FAIL"


@dataclass
class Check:
    status: str
    name: str
    detail: str = ""


def _tag_present(tag: str, available: list[str]) -> bool:
    want = tag if ":" in tag else tag + ":latest"
    return tag in available or want in available


def run_checks(models_config: str | None = None, ping: bool = False,
               data_root: str | Path = ".", ledgers: list[str] | None = None) -> list[Check]:
    out: list[Check] = []
    v = sys.version_info
    out.append(Check(OK if v >= (3, 11) else FAIL, "python", f"{v.major}.{v.minor}.{v.micro}"))
    try:
        import numpy  # noqa: F401

        import lpswarm
        out.append(Check(OK, "lpswarm package", lpswarm.__version__))
    except Exception as exc:  # noqa: BLE001
        out.append(Check(FAIL, "lpswarm package", str(exc)))
        return out

    root = Path(data_root)
    for rel in ("data/alphabet/gematria_primus.json", "data/lp/manifest.json"):
        p = root / rel
        out.append(Check(OK if p.is_file() else WARN, rel,
                         "" if p.is_file() else "missing (only needed for real Liber Primus runs)"))

    if not models_config:
        out.append(Check(WARN, "models config", "none given (--models); model checks skipped"))
        return out
    from lpswarm.router.adapters import AdapterError, ollama_tags
    from lpswarm.router.base import Role, load_model_specs
    try:
        specs = load_model_specs(models_config)
    except Exception as exc:  # noqa: BLE001
        out.append(Check(FAIL, "models config", f"{models_config}: {exc}"))
        return out
    out.append(Check(OK, "models config", f"{models_config}: {len(specs)} model(s)"))
    if not any(Role.WEIGHTING in s.roles for s in specs):
        out.append(Check(WARN, "ranker", "no model has the 'weighting' role (--ranker unavailable)"))

    tags_cache: dict[str, list[str] | AdapterError] = {}
    for s in specs:
        label = f"model {s.name}"
        if s.provider == "ollama":
            ep = s.endpoint or "http://localhost:11434"
            if ep not in tags_cache:
                try:
                    tags_cache[ep] = ollama_tags(ep)
                except AdapterError as exc:
                    tags_cache[ep] = exc
            got = tags_cache[ep]
            if isinstance(got, AdapterError):
                out.append(Check(FAIL, label, f"Ollama at {ep} not reachable (is it running? "
                                              "scripts\\start_ollama.ps1)"))
                continue
            if not _tag_present(s.model, got):
                out.append(Check(FAIL, label, f"'{s.model}' not pulled on {ep}; have: "
                                              + (", ".join(sorted(got)) or "nothing")))
                continue
            out.append(Check(OK, label, f"{s.model} on {ep}"))
        elif s.provider == "openai_compatible":
            if not s.api_key_env or not os.environ.get(s.api_key_env):
                out.append(Check(WARN, label, f"environment variable {s.api_key_env} is not set "
                                              "(needed only when this model is used)"))
                continue
            prices = (s.extra.get("price_in_per_mtok") or 0, s.extra.get("price_out_per_mtok") or 0)
            if not any(prices):
                out.append(Check(WARN, label, "key is set, but prices are 0: spend is recorded as "
                                              "$0 and max_usd cannot protect you"))
                continue
            out.append(Check(OK, label, f"key in {s.api_key_env}, prices set, cap "
                                        f"{'$%.2f' % s.max_usd if s.max_usd is not None else 'none'}"))
        elif s.provider in ("claude_code", "codex"):
            from lpswarm.router.cli_adapters import ClaudeCodeAdapter, CodexAdapter, cli_version
            exe = str(s.extra.get("exe", "claude" if s.provider == "claude_code" else "codex"))
            ver = cli_version(exe)
            if ver is None:
                out.append(Check(FAIL, label, f"'{exe}' not found on PATH (install it and sign in)"))
                continue
            drop = ClaudeCodeAdapter.DROP_ENV if s.provider == "claude_code" else CodexAdapter.DROP_ENV
            ignored = [k for k in drop if os.environ.get(k)]
            note = (f"; {', '.join(ignored)} is set but is removed for this model, so calls use "
                    "your plan" if ignored else "")
            cap = s.extra.get("max_calls_per_window")
            out.append(Check(OK, label, f"{exe} {ver}; plan sign-in (not checked without --ping); "
                                        f"cap {cap or 'none'} calls per "
                                        f"{s.extra.get('window_hours', 5)}h{note}"))
            for lpath in ledgers or []:
                if not _is_ledger(lpath):
                    continue
                from lpswarm.ledger import Ledger
                from lpswarm.router import Router
                from lpswarm.router.limits import pause_text
                group = s.extra.get("quota_group")
                members = [m for m in specs if m.name == s.name
                           or (group and m.extra.get("quota_group") == group)]
                with Ledger(lpath) as led:
                    st = Router(members, ledger=led).window_status(s.name)
                when = pause_text(st).replace(", paused", "; PAUSED")
                share = f" (group {group}: {', '.join(st['group'])})" if group else ""
                if group:
                    vals = {m.name: m.extra.get("max_calls_per_window") for m in members}
                    if len({v for v in vals.values()}) > 1 and s.name == st["group"][0]:
                        out.append(Check(WARN, f"quota group {group}",
                                         "members set different max_calls_per_window ("
                                         + ", ".join(f"{k} {v}" for k, v in vals.items())
                                         + f"); the group total used is {st['cap']}. For a "
                                         "per-model share, set model_max_calls_per_window"))
                if st.get("model_cap"):
                    share += f"; this model {st['model_calls']}/{st['model_cap']}"
                out.append(Check(WARN if st["paused_until"] else OK, f"usage {s.name}",
                                 f"{st['calls']} call(s) in the last {st['window_hours']:g}h "
                                 f"(cap {cap or 'none'}){share} in {lpath}{when}"))
        elif s.provider == "command":
            cmd = list(s.extra.get("command") or [])
            exe = shutil.which(cmd[0]) if cmd else None
            out.append(Check(OK if exe else FAIL, label,
                             f"runs {exe}" if exe else f"command not found: {cmd[:1]}"))
        elif s.provider == "scripted":
            out.append(Check(OK, label, "scripted (offline dry run)"))
        else:
            out.append(Check(FAIL, label, f"unknown provider {s.provider!r}"))

    if ping:
        from lpswarm.ledger import Ledger
        from lpswarm.router import Router
        healthy = {c.name for c in out if c.status == OK}
        # Pings go through the shared spend ledger, so they respect active pauses and
        # call caps and are counted like any other call.
        spend_path = next((p for p in (ledgers or []) if _is_ledger(p) or not Path(p).exists()), None)
        if spend_path is None:
            Path("reports").mkdir(exist_ok=True)
            spend_path = "reports/model_spend.sqlite"
        router = Router(specs, ledger=Ledger(spend_path))
        for s in specs:
            if f"model {s.name}" not in healthy:
                continue
            role = s.roles[0].value
            try:
                c = router.complete(s.name, [{"role": "user", "content":
                                              'Reply with the JSON {"ok": true} and nothing else.'}],
                                    role=role, max_tokens=20, temperature=0.0)
                if not c.text.strip():
                    out.append(Check(WARN, f"ping {s.name}",
                                     f"{c.latency_s:.1f}s but the reply was empty: a thinking model may "
                                     "have used its whole budget on hidden reasoning; add think = false "
                                     "to this model in the models config"))
                else:
                    out.append(Check(OK, f"ping {s.name}", f"{c.latency_s:.1f}s, reply: {c.text[:40]!r}"))
            except Exception as exc:  # noqa: BLE001
                out.append(Check(FAIL, f"ping {s.name}", str(exc)[:200]))
    return out


def _is_ledger(path: str) -> bool:
    """True only for an existing SQLite file that already has lpswarm's tables (doctor
    must not add tables to, or crash on, some other file the user names)."""
    import sqlite3
    p = Path(path)
    if not p.is_file():
        return False
    try:
        con = sqlite3.connect(f"file:{p.as_posix()}?mode=ro", uri=True)
        try:
            names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        finally:
            con.close()
    except sqlite3.Error:
        return False
    return {"budget_event", "attempt"} <= names


def print_report(checks: list[Check]) -> int:
    width = max(len(c.name) for c in checks)
    for c in checks:
        print(f"[{c.status:<4}] {c.name:<{width}}  {c.detail}")
    fails = sum(c.status == FAIL for c in checks)
    warns = sum(c.status == WARN for c in checks)
    print(f"\n{fails} problem(s), {warns} warning(s)")
    return 1 if fails else 0

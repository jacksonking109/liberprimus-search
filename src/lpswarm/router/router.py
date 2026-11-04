"""Model router: one interface over local and hosted models, with budgets.

Every call is recorded in the ledger's budget_event table (vendor = provider,
model = the config alias, tokens, usd, task_id). Before each call the router
checks the model's spend so far against its `max_usd` and the global cap, so a
budget holds across runs that share a ledger.
"""
from __future__ import annotations

import json
import os
import threading
import time
import warnings
from dataclasses import dataclass
from typing import Sequence

from lpswarm.router.adapters import (AdapterError, CommandAdapter, Completion,
                                     OllamaAdapter, OpenAICompatibleAdapter, ScriptedAdapter)
from lpswarm.router.base import ModelSpec, Role
from lpswarm.router.limits import RateLimited


class BudgetExceeded(RuntimeError):
    pass


SUBSCRIPTION_PROVIDERS = ("claude_code", "codex")
PRICES_ZERO_WARNING = "max_usd is set but prices are 0"


def backend_key(spec: ModelSpec) -> str:
    """What a model's calls queue on: one Ollama server (one GPU), one plan quota, one API
    endpoint. Calls on different backends can run at the same time; calls on the same
    backend are made one after another (two local models on one GPU would swap or run
    out of memory; one plan quota is counted call by call)."""
    x = spec.extra
    if spec.provider == "ollama":
        return f"ollama:{(spec.endpoint or 'http://localhost:11434').rstrip('/')}"
    if x.get("quota_group"):
        return str(x["quota_group"])
    if spec.provider in SUBSCRIPTION_PROVIDERS:
        return spec.provider
    if spec.provider == "openai_compatible":
        return f"api:{(spec.endpoint or '').rstrip('/')}"
    return f"{spec.provider}:{spec.name}"


def _accepts(fn, name: str) -> bool:
    import inspect
    try:
        return name in inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return False


def make_adapter(spec: ModelSpec):
    x = spec.extra
    if spec.provider == "ollama":
        return OllamaAdapter(spec.model, spec.endpoint or "http://localhost:11434",
                             timeout=float(x.get("timeout", 300)), json_mode=bool(x.get("json_mode")),
                             options=x.get("options"),
                             think=bool(x["think"]) if "think" in x else None)
    if spec.provider == "openai_compatible":
        if not spec.endpoint:
            raise ValueError(f"model {spec.name}: openai_compatible needs an endpoint")
        return OpenAICompatibleAdapter(spec.model, spec.endpoint, spec.api_key_env,
                                       timeout=float(x.get("timeout", 120)),
                                       price_in_per_mtok=float(x.get("price_in_per_mtok", 0.0)),
                                       price_out_per_mtok=float(x.get("price_out_per_mtok", 0.0)),
                                       json_mode=bool(x.get("json_mode")))
    if spec.provider == "scripted":
        # Offline dry runs: replies from the config (cycled) or from a JSON file of strings.
        replies = x.get("replies")
        if x.get("replies_file"):
            from lpswarm.textio import read_text
            replies = json.loads(read_text(x["replies_file"]))
        if not replies:
            raise ValueError(f"model {spec.name}: scripted provider needs replies or replies_file")
        return ScriptedAdapter(spec.name, list(replies))
    if spec.provider == "claude_code":
        from lpswarm.router.cli_adapters import ClaudeCodeAdapter
        return ClaudeCodeAdapter(spec.model, exe=str(x.get("exe", "claude")),
                                 timeout=float(x.get("timeout", 600)),
                                 extra_args=list(x.get("extra_args") or []))
    if spec.provider == "codex":
        from lpswarm.router.cli_adapters import CodexAdapter
        return CodexAdapter(spec.model, exe=str(x.get("exe", "codex")),
                            timeout=float(x.get("timeout", 600)),
                            extra_args=list(x.get("extra_args") or []))
    if spec.provider == "command":
        return CommandAdapter(spec.model, list(x.get("command") or []),
                              timeout=float(x.get("timeout", 600)))
    raise ValueError(f"model {spec.name}: unknown provider {spec.provider!r}")


@dataclass
class _Entry:
    spec: ModelSpec
    adapter: object


class Router:
    def __init__(self, specs: Sequence[ModelSpec], ledger=None, global_max_usd: float | None = None,
                 adapters: dict | None = None, retries: int = 1):
        self.ledger = ledger
        self.global_max_usd = global_max_usd
        self.retries = retries
        self._models: dict[str, _Entry] = {}
        # Models may be called from several threads (one per backend, see backend_key);
        # budget/limit checks and ledger writes are serialised here.
        self._lock = threading.RLock()
        self._config_path: str | None = None    # set by from_toml: caps are re-read on change
        self._config_mtime: float | None = None
        if ledger is None and (global_max_usd is not None or any(s.max_usd is not None for s in specs)):
            raise ValueError("USD caps need a ledger to count spending; pass ledger=...")
        if ledger is None and any(s.extra.get("max_calls_per_window") for s in specs):
            raise ValueError("max_calls_per_window needs a ledger to count calls; pass ledger=...")
        for s in specs:
            if (s.provider == "openai_compatible" and s.max_usd is not None
                    and not s.extra.get("price_in_per_mtok") and not s.extra.get("price_out_per_mtok")):
                # The text starts with PRICES_ZERO_WARNING so `-W ignore:<prefix>` can mute it.
                warnings.warn(f"{PRICES_ZERO_WARNING} (model {s.name}), so spend is recorded as "
                              "$0 and the cap can never trigger; fill in price_in_per_mtok / "
                              "price_out_per_mtok", stacklevel=2)
            ad = (adapters or {}).get(s.name) or make_adapter(s)
            self._models[s.name] = _Entry(s, ad)

    @classmethod
    def from_toml(cls, path, ledger=None, **kw) -> "Router":
        from lpswarm.router.base import load_model_specs
        r = cls(load_model_specs(path), ledger=ledger, **kw)
        r._config_path = str(path)
        try:
            r._config_mtime = os.stat(path).st_mtime
        except OSError:
            pass
        return r

    LIVE_KEYS = ("max_calls_per_window", "model_max_calls_per_window", "window_hours", "quota_group")

    def refresh_limits(self) -> bool:
        """Re-read the plan-cap settings (LIVE_KEYS) from the models config if the file
        changed since it was loaded, so raising max_calls_per_window takes effect in a
        running job without a restart. Adapters, roles and prices are never reloaded.
        Returns True if anything was updated."""
        path = self._config_path
        if not path:
            return False
        try:
            mtime = os.stat(path).st_mtime
        except OSError:
            return False
        if mtime == self._config_mtime:
            return False
        self._config_mtime = mtime
        try:
            from lpswarm.router.base import load_model_specs
            fresh = {s.name: s for s in load_model_specs(path)}
        except Exception:  # noqa: BLE001 - a half-saved or broken file: keep the old settings
            self._config_mtime = None   # try again next time
            return False
        changed = False
        with self._lock:
            for name, e in self._models.items():
                f = fresh.get(name)
                if f is None:
                    continue
                for k in self.LIVE_KEYS:
                    if e.spec.extra.get(k) != f.extra.get(k):
                        changed = True
                        if k in f.extra:
                            e.spec.extra[k] = f.extra[k]
                        else:
                            e.spec.extra.pop(k, None)
        if changed:
            self._log_call(f"[model] plan caps reloaded from {path}")
        return changed

    def names(self, role: Role | str | None = None) -> list[str]:
        if role is None:
            return list(self._models)
        r = Role(role)
        return [n for n, e in self._models.items() if r in e.spec.roles]

    def spec(self, name: str) -> ModelSpec:
        try:
            return self._models[name].spec
        except KeyError:
            raise ValueError(f"unknown model {name!r}; configured: {sorted(self._models)}") from None

    def spent(self, name: str | None = None) -> float:
        if self.ledger is None:
            return 0.0
        if name is None:
            row = self.ledger.conn.execute("SELECT COALESCE(SUM(usd), 0) FROM budget_event").fetchone()
        else:
            row = self.ledger.conn.execute("SELECT COALESCE(SUM(usd), 0) FROM budget_event"
                                           " WHERE model=?", (name,)).fetchone()
        return float(row[0])

    def _check_budget(self, name: str) -> None:
        cap = self._models[name].spec.max_usd
        if cap is not None and self.spent(name) >= cap:
            raise BudgetExceeded(f"model {name} reached its budget of ${cap:.2f}")
        if self.global_max_usd is not None and self.spent() >= self.global_max_usd:
            raise BudgetExceeded(f"global model budget of ${self.global_max_usd:.2f} reached")

    def quota_members(self, name: str) -> list[str]:
        """Models sharing `name`'s plan quota (same `quota_group`), including itself."""
        group = self.spec(name).extra.get("quota_group")
        if not group:
            return [name]
        return [n for n, e in self._models.items() if e.spec.extra.get("quota_group") == group]

    def quota_label(self, name: str) -> str:
        return str(self.spec(name).extra.get("quota_group") or name)

    def window_status(self, name: str, now: float | None = None) -> dict:
        """Calls in the current rolling window (summed over the quota group), the cap,
        and any active pause (a limit hit by any group member pauses them all).

        `pause_kind` is 'reply' (the CLI reported a usage limit; recorded, holds until
        its reset) or 'window' (the local call cap is full; worked out live from the
        call count and the current cap, so raising the cap ends it at once)."""
        now = time.time() if now is None else now
        self.refresh_limits()
        spec = self.spec(name)
        hours = float(spec.extra.get("window_hours", 5))
        cap = spec.extra.get("max_calls_per_window")
        members = self.quota_members(name)
        since = now - hours * 3600
        calls = self.ledger.calls_since(members, since) if self.ledger is not None else []
        reply = self.ledger.active_limit(members, now) if self.ledger is not None else None
        # Optional cap on this model alone, inside the group's total (e.g. Opus 60 of 200).
        mcap = spec.extra.get("model_max_calls_per_window")
        own = (self.ledger.calls_since(name, since) if self.ledger is not None and len(members) > 1
               else calls) if mcap else []
        window, limiter = None, None

        def _resume(times, c):
            # the call that must age out for the count to drop below the cap
            return times[len(times) - int(c)] + hours * 3600 + 5
        if cap and int(cap) > 0 and len(calls) >= int(cap):
            window, limiter = _resume(calls, cap), "group"
        if mcap and int(mcap) > 0 and len(own) >= int(mcap):
            t = _resume(own, mcap)
            if window is None or t > window:
                window, limiter = t, "model"
        paused, kind = None, None
        if reply is not None or window is not None:
            paused = max(t for t in (reply, window) if t is not None)
            kind = "reply" if reply is not None and reply >= (window or 0) else "window"
        return {"window_hours": hours, "calls": len(calls), "cap": cap, "paused_until": paused,
                "pause_kind": kind, "oldest_call": calls[0] if calls else None, "group": members,
                "quota": self.quota_label(name), "model_calls": len(own) if mcap else None,
                "model_cap": mcap, "limiter": limiter}

    def _check_limits(self, name: str) -> None:
        """Raise RateLimited if a CLI-reported limit is active or the local window cap is full."""
        if self.ledger is None:
            return
        now = time.time()
        st = self.window_status(name, now)
        if st["pause_kind"] == "reply":
            raise RateLimited(name, st["paused_until"],
                              f"usage limit reported by the CLI for {st['quota']}")
        if st["pause_kind"] == "window":
            resume, cap = st["paused_until"], st["cap"]
            # history only (doctor / SUMMARY); one row per pause, not one per check
            last = self.ledger.active_limit(st["group"], now, include_window=True)
            if last is None or last < resume - 1:
                self.ledger.add_rate_limit_event(name, now, resume, "window", False,
                                                 f"{st['calls']} calls in {st['window_hours']:g}h "
                                                 f"(cap {cap})")
            if st["limiter"] == "model":
                raise RateLimited(name, resume,
                                  f"local cap {st['model_calls']}/{st['model_cap']} calls per "
                                  f"{st['window_hours']:g}h for {name} alone; raise "
                                  "model_max_calls_per_window in the models config to allow more")
            raise RateLimited(name, resume,
                              f"local cap {st['calls']}/{cap} calls per {st['window_hours']:g}h "
                              f"for {st['quota']}; raise max_calls_per_window in the models "
                              "config to allow more")

    def complete(self, name: str, messages: Sequence[dict], role: Role | str,
                 task_id: str | None = None, temperature: float = 0.7,
                 max_tokens: int = 2048, schema: dict | None = None) -> Completion:
        """Call a model, with optional per-call logging (LPSWARM_LOG_CALLS=1: one line per
        call on stdout) and transcripts (LPSWARM_TRANSCRIPT=<file.jsonl>: every prompt and
        reply appended). Both are set by `lpswarm overnight` for its jobs."""
        t0 = time.monotonic()
        role_s = Role(role).value if isinstance(role, (str, Role)) else str(role)
        try:
            c = self._complete(name, messages, role, task_id, temperature, max_tokens, schema)
        except RateLimited as exc:
            self._log_call(f"[model] {name} ({role_s}) paused: {exc}")
            self._transcript(name, role_s, task_id, messages, None, f"paused: {exc}", t0)
            raise
        except BudgetExceeded as exc:
            self._log_call(f"[model] {name} ({role_s}) budget: {exc}")
            raise
        except AdapterError as exc:
            self._log_call(f"[model] {name} ({role_s}) error after {time.monotonic() - t0:.1f}s: "
                           f"{str(exc)[:200]}")
            self._transcript(name, role_s, task_id, messages, None, str(exc)[:500], t0)
            raise
        self._log_call(f"[model] {name} ({role_s}) ok {c.latency_s or time.monotonic() - t0:.1f}s, "
                       f"tokens in/out {c.tokens_in}/{c.tokens_out}, reply {len(c.text)} chars")
        self._transcript(name, role_s, task_id, messages, c.text, None, t0)
        return c

    def _log_call(self, line: str) -> None:
        if os.environ.get("LPSWARM_LOG_CALLS") == "1":
            print(f"{time.strftime('%H:%M:%S')} {line}", flush=True)

    def _transcript(self, name, role, task_id, messages, reply, error, t0) -> None:
        path = os.environ.get("LPSWARM_TRANSCRIPT")
        if not path:
            return
        rec = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "model": name, "role": role,
               "task": task_id, "seconds": round(time.monotonic() - t0, 2),
               "messages": list(messages), "reply": reply, "error": error}
        try:
            with self._lock, open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def _complete(self, name: str, messages: Sequence[dict], role: Role | str,
                  task_id: str | None = None, temperature: float = 0.7,
                  max_tokens: int = 2048, schema: dict | None = None) -> Completion:
        """`schema` (JSON schema for the reply) is used by adapters that support
        structured output (Ollama) and ignored by the others."""
        entry = self._models.get(name)
        if entry is None:
            raise ValueError(f"unknown model {name!r}")
        if Role(role) not in entry.spec.roles:
            raise ValueError(f"model {name} is not configured for role {Role(role).value}")
        with self._lock:
            self._check_budget(name)
            self._check_limits(name)
        self._log_call(f"[model] {name} ({Role(role).value}) calling...")
        last: AdapterError | None = None
        c: Completion | None = None
        for attempt in range(self.retries + 1):
            try:
                kw = {"temperature": temperature, "max_tokens": max_tokens}
                if schema is not None and _accepts(entry.adapter.complete, "schema") \
                        and entry.spec.extra.get("structured_output", True):
                    kw["schema"] = schema
                c = entry.adapter.complete(messages, **kw)
                break
            except AdapterError as exc:
                last = exc
                if getattr(exc, "rate_limited", False):
                    now = time.time()
                    if self.ledger is not None:
                        with self._lock:
                            self.ledger.add_rate_limit_event(name, now, exc.resume_at, "reply",
                                                             getattr(exc, "parsed", False), str(exc))
                    raise RateLimited(name, exc.resume_at,
                                      "usage limit reported by the CLI"
                                      + ("" if getattr(exc, "parsed", False)
                                         else " (no reset time given; cool-down)")) from None
                if not exc.transient:
                    break  # e.g. 400/401/404: retrying cannot help
                if attempt < self.retries:
                    time.sleep(1.5 * (attempt + 1))
        if c is None:
            raise AdapterError(f"{name}: {last}", getattr(last, "transient", False))
        if self.ledger is not None:
            with self._lock:
                self.ledger.add_budget_event(entry.spec.provider, name, c.tokens_in, c.tokens_out,
                                             c.usd, task_id)
                self.ledger.commit()
        return c


__all__ = ["AdapterError", "BudgetExceeded", "Completion", "RateLimited", "Router",
           "SUBSCRIPTION_PROVIDERS", "ScriptedAdapter", "backend_key", "make_adapter"]

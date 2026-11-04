"""Model router: one interface over local and hosted models, with budgets.

Every call is recorded in the ledger's budget_event table (vendor = provider,
model = the config alias, tokens, usd, task_id). Before each call the router
checks the model's spend so far against its `max_usd` and the global cap, so a
budget holds across runs that share a ledger.
"""
from __future__ import annotations

import json
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
        if ledger is None and (global_max_usd is not None or any(s.max_usd is not None for s in specs)):
            raise ValueError("USD caps need a ledger to count spending; pass ledger=...")
        if ledger is None and any(s.extra.get("max_calls_per_window") for s in specs):
            raise ValueError("max_calls_per_window needs a ledger to count calls; pass ledger=...")
        for s in specs:
            if (s.provider == "openai_compatible" and s.max_usd is not None
                    and not s.extra.get("price_in_per_mtok") and not s.extra.get("price_out_per_mtok")):
                warnings.warn(f"model {s.name}: max_usd is set but prices are 0, so spend is "
                              "recorded as $0 and the cap can never trigger; fill in "
                              "price_in_per_mtok / price_out_per_mtok", stacklevel=2)
            ad = (adapters or {}).get(s.name) or make_adapter(s)
            self._models[s.name] = _Entry(s, ad)

    @classmethod
    def from_toml(cls, path, ledger=None, **kw) -> "Router":
        from lpswarm.router.base import load_model_specs
        return cls(load_model_specs(path), ledger=ledger, **kw)

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

    def window_status(self, name: str, now: float | None = None) -> dict:
        """Calls in the current rolling window (summed over the quota group), the cap,
        and any active pause (a limit hit by any group member pauses them all)."""
        now = time.time() if now is None else now
        spec = self.spec(name)
        hours = float(spec.extra.get("window_hours", 5))
        cap = spec.extra.get("max_calls_per_window")
        members = self.quota_members(name)
        calls = self.ledger.calls_since(members, now - hours * 3600) if self.ledger is not None else []
        paused = self.ledger.active_limit(members, now) if self.ledger is not None else None
        return {"window_hours": hours, "calls": len(calls), "cap": cap, "paused_until": paused,
                "oldest_call": calls[0] if calls else None, "group": members}

    def _check_limits(self, name: str) -> None:
        """Raise RateLimited if a recorded limit is active or the local window cap is full."""
        if self.ledger is None:
            return
        now = time.time()
        until = self.ledger.active_limit(self.quota_members(name), now)
        if until is not None:
            raise RateLimited(name, until, "usage limit active for this plan")
        st = self.window_status(name, now)
        cap = st["cap"]
        if cap and st["calls"] >= int(cap):
            resume = st["oldest_call"] + st["window_hours"] * 3600 + 5
            self.ledger.add_rate_limit_event(name, now, resume, "window", False,
                                             f"{st['calls']} calls in {st['window_hours']}h (cap {cap})")
            raise RateLimited(name, resume, f"local cap of {cap} calls per {st['window_hours']:g}h")

    def complete(self, name: str, messages: Sequence[dict], role: Role | str,
                 task_id: str | None = None, temperature: float = 0.7,
                 max_tokens: int = 2048, schema: dict | None = None) -> Completion:
        """`schema` (JSON schema for the reply) is used by adapters that support
        structured output (Ollama) and ignored by the others."""
        entry = self._models.get(name)
        if entry is None:
            raise ValueError(f"unknown model {name!r}")
        if Role(role) not in entry.spec.roles:
            raise ValueError(f"model {name} is not configured for role {Role(role).value}")
        self._check_budget(name)
        self._check_limits(name)
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
            self.ledger.add_budget_event(entry.spec.provider, name, c.tokens_in, c.tokens_out,
                                         c.usd, task_id)
            self.ledger.commit()
        return c


__all__ = ["AdapterError", "BudgetExceeded", "Completion", "RateLimited", "Router",
           "SUBSCRIPTION_PROVIDERS", "ScriptedAdapter", "make_adapter"]

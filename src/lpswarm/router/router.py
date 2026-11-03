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


class BudgetExceeded(RuntimeError):
    pass


def make_adapter(spec: ModelSpec):
    x = spec.extra
    if spec.provider == "ollama":
        return OllamaAdapter(spec.model, spec.endpoint or "http://localhost:11434",
                             timeout=float(x.get("timeout", 300)), json_mode=bool(x.get("json_mode")),
                             options=x.get("options"))
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

    def complete(self, name: str, messages: Sequence[dict], role: Role | str,
                 task_id: str | None = None, temperature: float = 0.7,
                 max_tokens: int = 2048) -> Completion:
        entry = self._models.get(name)
        if entry is None:
            raise ValueError(f"unknown model {name!r}")
        if Role(role) not in entry.spec.roles:
            raise ValueError(f"model {name} is not configured for role {Role(role).value}")
        self._check_budget(name)
        last: AdapterError | None = None
        c: Completion | None = None
        for attempt in range(self.retries + 1):
            try:
                c = entry.adapter.complete(messages, temperature=temperature, max_tokens=max_tokens)
                break
            except AdapterError as exc:
                last = exc
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


__all__ = ["AdapterError", "BudgetExceeded", "Completion", "Router", "ScriptedAdapter",
           "make_adapter"]

"""Model router interface (Phase 3). STUB: nothing here calls a model.

Planned shape, so later phases slot in without touching the oracle/ledger:

  - Model IDs and endpoints live in a config file (see
    config/models.example.toml), never in code.
  - Roles: `proposer` (hypotheses and key candidates), `triage` (dedupe
    proposals against the ledger), `weighting` (cheap prioritisation of
    proposals). A model never decides pass/fail; only the oracle does.
  - Every call is logged with model + role, and its token/cost usage goes to
    the ledger's budget_event table.
  - Credentials: API keys are read from an environment variable named in the
    config, at call time only. They are never written to the ledger, logs,
    config files, or the repo.
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Protocol


class Role(str, Enum):
    PROPOSER = "proposer"
    TRIAGE = "triage"
    WEIGHTING = "weighting"


@dataclass
class ModelSpec:
    name: str                   # local alias used in the ledger, e.g. "qwen-local"
    provider: str               # "ollama", "llamacpp", "openai_compatible", ...
    model: str                  # provider-side model id / tag
    roles: tuple[Role, ...]
    endpoint: str | None = None
    api_key_env: str | None = None   # NAME of the env var; the value is never stored
    max_usd: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class Proposal:
    cipher_family: str
    description: str
    params: dict
    key_candidates: list[str]
    proposer_model: str
    proposer_role: str


class ModelRouter(Protocol):
    def propose(self, role: Role, context: dict) -> list[Proposal]: ...


class NullRouter:
    """Phase 1 router: refuses every call."""

    def propose(self, role: Role, context: dict) -> list[Proposal]:
        raise NotImplementedError("model router is not implemented in Phase 1")


def load_model_specs(path: str | Path) -> list[ModelSpec]:
    """Parse a models TOML file. Reads no environment variables and opens no connections."""
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    specs = []
    for name, d in data.get("models", {}).items():
        specs.append(ModelSpec(
            name=name, provider=d["provider"], model=d["model"],
            roles=tuple(Role(r) for r in d.get("roles", ["proposer"])),
            endpoint=d.get("endpoint"), api_key_env=d.get("api_key_env"),
            max_usd=d.get("max_usd"),
            extra={k: v for k, v in d.items() if k not in
                   {"provider", "model", "roles", "endpoint", "api_key_env", "max_usd"}}))
    return specs

"""Model router: config-driven adapters for local and hosted models, with budgets."""
from lpswarm.router.adapters import (AdapterError, CommandAdapter, Completion, OllamaAdapter,
                                     OpenAICompatibleAdapter, ScriptedAdapter)
from lpswarm.router.base import ModelRouter, ModelSpec, NullRouter, Proposal, Role, load_model_specs
from lpswarm.router.limits import RateLimited
from lpswarm.router.router import SUBSCRIPTION_PROVIDERS, BudgetExceeded, Router, make_adapter

__all__ = ["AdapterError", "BudgetExceeded", "CommandAdapter", "Completion", "ModelRouter",
           "ModelSpec", "NullRouter", "OllamaAdapter", "OpenAICompatibleAdapter", "Proposal", "Role",
           "RateLimited", "Router", "SUBSCRIPTION_PROVIDERS", "ScriptedAdapter", "load_model_specs", "make_adapter"]

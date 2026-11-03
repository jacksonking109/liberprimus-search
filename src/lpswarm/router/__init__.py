"""Model router: config-driven adapters for local and hosted models, with budgets."""
from lpswarm.router.adapters import (AdapterError, CommandAdapter, Completion, OllamaAdapter,
                                     OpenAICompatibleAdapter, ScriptedAdapter)
from lpswarm.router.base import ModelRouter, ModelSpec, NullRouter, Proposal, Role, load_model_specs
from lpswarm.router.router import BudgetExceeded, Router, make_adapter

__all__ = ["AdapterError", "BudgetExceeded", "CommandAdapter", "Completion", "ModelRouter",
           "ModelSpec", "NullRouter", "OllamaAdapter", "OpenAICompatibleAdapter", "Proposal", "Role",
           "Router", "ScriptedAdapter", "load_model_specs", "make_adapter"]

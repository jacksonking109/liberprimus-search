"""Cipher families and registry."""
from __future__ import annotations

from lpswarm.ciphers.base import CipherFamily, DIFFICULTIES
from lpswarm.ciphers.families import (VARIANTS, Autokey, Caesar, Columnar, RunningKey,
                                      Substitution, Vigenere)

REGISTRY: dict[str, CipherFamily] = {
    f.name: f for f in (Caesar(), Vigenere(), Autokey(), RunningKey(), Substitution(), Columnar())
}


def _register_programs() -> None:
    # Imported lazily: programs depends on ciphers.base.
    from lpswarm.programs.family import ProgramFamily
    REGISTRY.setdefault(ProgramFamily.name, ProgramFamily())


def get_family(name: str) -> CipherFamily:
    if name not in REGISTRY:
        _register_programs()
    try:
        return REGISTRY[name]
    except KeyError:
        raise ValueError(f"unknown cipher family {name!r}; known: {sorted(REGISTRY)}") from None


_register_programs()

__all__ = ["CipherFamily", "DIFFICULTIES", "VARIANTS", "REGISTRY", "get_family",
           "Caesar", "Vigenere", "Autokey", "RunningKey", "Substitution", "Columnar"]

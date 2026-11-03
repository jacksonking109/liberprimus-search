"""Declarative cipher programs proposed by generators and run by deterministic code."""
from lpswarm.programs.sequences import SEQUENCES
from lpswarm.programs.spec import (SpecError, canonical, compile_spec, decrypt, describe, encrypt,
                                   expand, roundtrips, spec_hash, with_offset)

__all__ = ["SEQUENCES", "SpecError", "canonical", "compile_spec", "decrypt", "describe", "encrypt", "expand",
           "roundtrips", "spec_hash", "with_offset"]

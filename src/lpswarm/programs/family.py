"""The `program` cipher family: a compiled cipher-program spec as the key."""
from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np

from lpswarm.ciphers.base import CipherFamily
from lpswarm.programs import spec as S


class ProgramFamily(CipherFamily):
    """Key = compiled spec (dict with integers only, see programs.spec).

    Params are always {}. Specs must be compiled with `compile_spec` and, if they
    carry an offset_range, expanded with `programs.expand` into one spec per
    offset, so every concrete cipher has exactly one ledger identity.
    """
    name = "program"
    word_keys = False

    def _resolve(self, key: dict, params: dict) -> dict:
        if not isinstance(key, dict) or key.get("v") != S.SPEC_VERSION:
            raise ValueError("program key must be a compiled spec (use programs.compile_spec)")
        if key.get("offset_range") or key.get("transpose_range") or key["stream"].get("exhaustive"):
            raise ValueError("program key has a range or exhaustive stream; run programs.expand() first")
        return key

    def encrypt(self, pt, key, n, **params):
        return S.encrypt(pt, self._resolve(key, params), n)

    def decrypt(self, ct, key, n, lm=None, **params):
        spec = self._resolve(key, params)
        if spec.get("skip_mode") == "resolve":
            if lm is None:
                raise ValueError('skip_mode "resolve" needs a language model (lm=bigram table)')
            from lpswarm.programs.resolve import resolve_decrypt
            return resolve_decrypt(ct, spec, n, lm)
        return S.decrypt(ct, spec, n)

    def null_variant(self, key) -> str | None:
        """Attempts whose decryption is optimised for English (skip resolution) must be
        judged against nulls produced by the same search."""
        if isinstance(key, dict) and key.get("skip_mode") == "resolve":
            return "skipdp:" + ",".join(str(int(x)) for x in key["skip"])
        return None

    def param_grid(self, length, key=None, **limits):
        return [{}]

    def random_key(self, rng, n, difficulty="medium", words=None, length=None):
        from lpswarm.programs.sampler import sample_spec
        raw = sample_spec(rng, n, words, difficulty, length)
        # Integers only, so any alphabet of size n compiles it identically.
        return S.compile_spec(raw, _IntAlphabet(n))

    def random_params(self, rng, length, key=None):
        return {}

    def key_json(self, key: Any) -> Any:
        return json.loads(S.canonical(key))

    def key_hash(self, key: Any) -> str:
        payload = json.dumps([self.name, self.key_json(key)], sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()

    def key_preview(self, key: Any, max_len: int = 200) -> str:
        s = S.describe(key)
        return s if len(s) <= max_len else s[: max_len - 3] + "..."


class _IntAlphabet:
    """Minimal stand-in so integer-only specs compile without a real alphabet."""

    def __init__(self, n: int):
        self.size = n

    def encode(self, text: str) -> np.ndarray:
        raise S.SpecError("words are not allowed here; use integer symbols")

    def decode(self, arr) -> str:
        return " ".join(str(int(x)) for x in arr)


def _self_register() -> None:
    from lpswarm.ciphers import REGISTRY
    REGISTRY.setdefault(ProgramFamily.name, ProgramFamily())


_self_register()

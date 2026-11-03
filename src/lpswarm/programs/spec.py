"""Cipher programs: a small declarative language that generators (including LLMs)
use to propose ciphers. Models never write code; they write a JSON spec that this
module validates, compiles to integers, and interprets deterministically.

Decryption of ciphertext c (integers mod N), in order:
  1. transpose  : undo a columnar transposition            {"columnar": [order]}
  2. reverse_text: read the text backwards                 true / false
  3. skip       : positions whose ciphertext symbol is in `skip` are literal:
                  plaintext = ciphertext there, and the keystream does NOT advance
  4. map        : "identity" or "reverse" (symbol i -> N-1-i) on the other symbols
  5. combine    : p = c - k ("sub"), c + k ("add"), or k - c ("beaufort"), mod N
  6. stream     : k_t for t = 0, 1, ... over non-skipped positions only

Streams:
  {"kind": "constant", "value": 3}
  {"kind": "repeat", "key": [1, 2, 3]}           or {"kind": "repeat", "word": "DIVINITY"}
  {"kind": "autokey", "primer": [..] | "word": "..", "source": "plaintext"|"ciphertext"}
  {"kind": "sequence", "name": "primes", "offset": 0, "scale": 1, "add": 0}

A spec may also give "offset_range": [lo, hi] (sequence/repeat start offsets to
try, at most MAX_OFFSET_SPAN values) which the executor expands into attempts.

Words and symbol names are resolved through the alphabet at compile time, so a
compiled spec contains integers only and hashes canonically for the ledger.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from typing import Any

import numpy as np

from lpswarm.alphabet import Alphabet
from lpswarm.programs.sequences import MAX_INDEX, SEQUENCES, window

SPEC_VERSION = 1
MAX_KEY_LEN = 64
MAX_OFFSET = 1_000_000
MAX_OFFSET_SPAN = 2000
MAX_WIDTH = 12
COMBINES = ("sub", "add", "beaufort")
MAPS = ("identity", "reverse")
STREAM_KINDS = ("constant", "repeat", "autokey", "sequence")
_TOP_KEYS = {"v", "stream", "combine", "map", "skip", "reverse_text", "transpose", "offset_range",
             "note"}


class SpecError(ValueError):
    """A proposal that is not a valid cipher program (reported back to the generator)."""


def _short(x: Any, limit: int = 60) -> str:
    r = repr(x)
    return r if len(r) <= limit else r[: limit - 3] + "..."


def _int(x: Any, what: str, lo: int | None = None, hi: int | None = None) -> int:
    if isinstance(x, bool) or not isinstance(x, (int, float)) or (
            isinstance(x, float) and not (math.isfinite(x) and x.is_integer())):
        raise SpecError(f"{what} must be an integer, got {_short(x)}")
    v = int(x)
    if lo is not None and v < lo or hi is not None and v > hi:
        raise SpecError(f"{what} must be in [{lo}, {hi}], got {v}")
    return v


def _bool(x: Any, what: str) -> bool:
    if not isinstance(x, bool):
        raise SpecError(f"{what} must be true or false, got {_short(x)}")
    return x


def _symbols(x: Any, alphabet: Alphabet, what: str, max_len: int = MAX_KEY_LEN,
             allow_word: bool = True) -> list[int]:
    """A list of symbol ints/tokens, or (if allow_word) a word spelled with tokens."""
    n = alphabet.size
    if isinstance(x, str) and allow_word:
        if len(x) > 4 * max_len:
            raise SpecError(f"{what} is too long")
        arr = alphabet.encode(x)
        if len(arr) == 0:
            raise SpecError(f"{what}: {_short(x)} contains no symbols of the alphabet")
        out = [int(v) for v in arr]
    elif isinstance(x, list):
        if len(x) > max_len:
            raise SpecError(f"{what} longer than {max_len}")
        out = []
        for item in x:
            if isinstance(item, str):
                arr = alphabet.encode(item) if len(item) <= 8 else []
                if len(arr) != 1:
                    raise SpecError(f"{what}: {_short(item)} is not a single symbol")
                out.append(int(arr[0]))
            else:
                out.append(_int(item, what) % n)
    else:
        raise SpecError(f"{what} must be a list" + (" or a word" if allow_word else "")
                        + f", got {_short(x)}")
    if not out:
        raise SpecError(f"{what} is empty")
    if len(out) > max_len:
        raise SpecError(f"{what} longer than {max_len}")
    return out


def _seq_limit(name: str) -> int:
    # Leave room for the longest ciphertext we expect to decrypt.
    return max(0, MAX_INDEX[name] - 10_000)


def compile_spec(raw: Any, alphabet: Alphabet) -> dict:
    """Validate a proposed spec and return its canonical integer form.

    Canonical form: integers only, scale/add reduced mod N, a repeat offset
    reduced mod the key length, a one-symbol repeat written as a constant, so
    equivalent proposals hash (and dedupe) identically. `offset_range` is kept
    for `expand`, which turns it into one fixed-offset spec per value.
    """
    if isinstance(raw, str):
        if len(raw) > 20_000:
            raise SpecError("spec text too long")
        try:
            raw = json.loads(raw)
        except (json.JSONDecodeError, RecursionError) as exc:
            raise SpecError(f"not JSON: {exc}") from None
    if not isinstance(raw, dict):
        raise SpecError("a spec must be a JSON object")
    unknown = [k for k in raw if k not in _TOP_KEYS]
    if unknown:
        raise SpecError(f"unknown fields {sorted(map(str, unknown))[:5]}")
    n = alphabet.size
    out: dict[str, Any] = {"v": SPEC_VERSION}
    combine = raw.get("combine", "sub")
    if not isinstance(combine, str) or combine not in COMBINES:
        raise SpecError(f"combine must be one of {COMBINES}")
    out["combine"] = combine
    mp = raw.get("map", "identity")
    if not isinstance(mp, str) or mp not in MAPS:
        raise SpecError(f"map must be one of {MAPS}")
    out["map"] = mp
    out["reverse_text"] = _bool(raw.get("reverse_text", False), "reverse_text")
    skip = raw.get("skip")
    if skip in (None, []):
        out["skip"] = []
    else:
        out["skip"] = sorted(set(_symbols(skip, alphabet, "skip", n, allow_word=False)))
        if len(out["skip"]) >= n:
            raise SpecError("skip cannot cover the whole alphabet")
    tr = raw.get("transpose")
    if tr is None or tr is False:
        out["transpose"] = None
    else:
        if not isinstance(tr, dict) or set(tr) != {"columnar"} or not isinstance(tr["columnar"], list):
            raise SpecError('transpose must be {"columnar": [column order]}')
        if not 2 <= len(tr["columnar"]) <= MAX_WIDTH:
            raise SpecError(f"columnar width must be 2..{MAX_WIDTH}")
        order = [_int(v, "columnar order", 0, MAX_WIDTH - 1) for v in tr["columnar"]]
        if sorted(order) != list(range(len(order))):
            raise SpecError("columnar order must be a permutation of 0..width-1")
        out["transpose"] = {"columnar": order}

    st = raw.get("stream")
    kind = st.get("kind") if isinstance(st, dict) else None
    if not isinstance(kind, str) or kind not in STREAM_KINDS:
        raise SpecError(f"stream must be an object with kind in {STREAM_KINDS}")
    allowed = {"constant": {"kind", "value"}, "repeat": {"kind", "key", "word", "offset"},
               "autokey": {"kind", "primer", "word", "source"},
               "sequence": {"kind", "name", "offset", "scale", "add"}}[kind]
    extra = [k for k in st if k not in allowed]
    if extra:
        raise SpecError(f"unknown stream fields {sorted(map(str, extra))[:5]} for kind {kind}")
    if kind == "constant":
        s: dict[str, Any] = {"kind": kind, "value": _int(st.get("value", 0), "value") % n}
    elif kind == "repeat":
        src = st.get("key", st.get("word"))
        if src is None:
            raise SpecError("repeat stream needs key or word")
        key = _symbols(src, alphabet, "key")
        s = {"kind": kind, "key": key, "offset": _int(st.get("offset", 0), "offset", 0, MAX_OFFSET)}
    elif kind == "autokey":
        src = st.get("primer", st.get("word"))
        if src is None:
            raise SpecError("autokey stream needs primer or word")
        source = st.get("source", "plaintext")
        if not isinstance(source, str) or source not in ("plaintext", "ciphertext"):
            raise SpecError("autokey source must be plaintext or ciphertext")
        s = {"kind": kind, "primer": _symbols(src, alphabet, "primer"), "source": source}
    else:
        name = st.get("name")
        if not isinstance(name, str) or name not in SEQUENCES:
            raise SpecError(f"unknown sequence {_short(name)}; known: {sorted(SEQUENCES)}")
        s = {"kind": kind, "name": name,
             "offset": _int(st.get("offset", 0), "offset", 0, _seq_limit(name)),
             "scale": _int(st.get("scale", 1), "scale", -10_000, 10_000) % n,
             "add": _int(st.get("add", 0), "add", -10_000, 10_000) % n}
    out["stream"] = s

    rng = raw.get("offset_range")
    if rng is not None:
        if kind not in ("repeat", "sequence"):
            raise SpecError("offset_range only applies to repeat and sequence streams")
        if not (isinstance(rng, list) and len(rng) == 2):
            raise SpecError("offset_range must be [lo, hi]")
        cap = _seq_limit(s["name"]) if kind == "sequence" else MAX_OFFSET
        lo, hi = _int(rng[0], "offset_range", 0, cap), _int(rng[1], "offset_range", 0, cap)
        if hi < lo or hi - lo + 1 > MAX_OFFSET_SPAN:
            raise SpecError(f"offset_range must have lo <= hi and at most {MAX_OFFSET_SPAN} values")
        out["offset_range"] = [lo, hi]
    else:
        out["offset_range"] = None
    return _normalise(out)


def _normalise(spec: dict) -> dict:
    st = spec["stream"]
    if st["kind"] == "repeat" and not spec.get("offset_range"):
        if len(st["key"]) == 1:
            spec["stream"] = {"kind": "constant", "value": st["key"][0]}
        else:
            st["offset"] %= len(st["key"])
    return spec


def canonical(spec: dict) -> str:
    return json.dumps(spec, sort_keys=True, separators=(",", ":"))


def spec_hash(spec: dict) -> str:
    return hashlib.sha256(canonical(spec).encode()).hexdigest()


def with_offset(spec: dict, offset: int) -> dict:
    s = copy.deepcopy(spec)
    s["stream"]["offset"] = int(offset)
    s["offset_range"] = None
    return _normalise(s)


def expand(spec: dict) -> list[dict]:
    """One fixed-offset spec per value of offset_range (deduplicated after
    normalisation, e.g. repeat offsets mod the key length); [spec] if no range."""
    if not spec.get("offset_range"):
        return [spec]
    lo, hi = spec["offset_range"]
    out, seen = [], set()
    for o in range(lo, hi + 1):
        s = with_offset(spec, o)
        h = canonical(s)
        if h not in seen:
            seen.add(h)
            out.append(s)
    return out


def describe(spec: dict, alphabet: Alphabet | None = None) -> str:
    """Short human-readable summary for the ledger and prompts."""
    st = spec["stream"]
    if st["kind"] == "constant":
        k = f"constant {st['value']}"
    elif st["kind"] == "repeat":
        key = st["key"]
        word = alphabet.decode(key) if alphabet else key
        k = f"repeat key {word}" + (f" @{st['offset']}" if st.get("offset") else "")
    elif st["kind"] == "autokey":
        word = alphabet.decode(st["primer"]) if alphabet else st["primer"]
        k = f"autokey({st['source']}) primer {word}"
    else:
        k = f"sequence {st['name']}*{st['scale']}+{st['add']} @{st['offset']}"
    parts = [spec["combine"], k]
    if spec["map"] != "identity":
        parts.append("map reverse")
    if spec["skip"]:
        sk = alphabet.decode(spec["skip"]) if alphabet else spec["skip"]
        parts.append(f"skip {sk}")
    if spec["reverse_text"]:
        parts.append("reverse text")
    if spec["transpose"]:
        parts.append(f"columnar {spec['transpose']['columnar']}")
    if spec.get("offset_range"):
        parts.append(f"offsets {spec['offset_range'][0]}..{spec['offset_range'][1]}")
    return "; ".join(parts)


# ---------------------------------------------------------------- interpreter
def _stream_values(st: dict, count: int, n: int) -> np.ndarray:
    if count == 0:
        return np.zeros(0, dtype=np.int64)
    if st["kind"] == "constant":
        return np.full(count, st["value"], dtype=np.int64)
    if st["kind"] == "repeat":
        key = np.asarray(st["key"], dtype=np.int64)
        idx = (np.arange(count) + st.get("offset", 0)) % len(key)
        return key[idx]
    if st["kind"] == "sequence":
        try:
            seq = window(st["name"], st["offset"], count, n)
        except ValueError as exc:
            raise SpecError(str(exc)) from None
        return (seq * st["scale"] + st["add"]) % n
    raise ValueError(st["kind"])


def _combine_dec(c: np.ndarray, k: np.ndarray, n: int, how: str) -> np.ndarray:
    c = c.astype(np.int64)
    k = np.asarray(k, dtype=np.int64)
    if how == "sub":
        return (c - k) % n
    if how == "add":
        return (c + k) % n
    return (k - c) % n


def _combine_enc(p: np.ndarray, k: np.ndarray, n: int, how: str) -> np.ndarray:
    p = p.astype(np.int64)
    k = np.asarray(k, dtype=np.int64)
    if how == "sub":
        return (p + k) % n
    if how == "add":
        return (p - k) % n
    return (k - p) % n


def _columnar_perm(order: list[int], length: int) -> np.ndarray:
    w = len(order)
    read_cols = np.argsort(np.asarray(order), kind="stable")
    idx = [np.arange(c, length, w) for c in read_cols]
    return np.concatenate(idx) if idx else np.arange(0)


def decrypt(ct: np.ndarray, spec: dict, n: int) -> np.ndarray:
    c = np.asarray(ct, dtype=np.int64).copy()
    if spec.get("transpose"):
        perm = _columnar_perm(spec["transpose"]["columnar"], len(c))
        tmp = np.empty_like(c)
        tmp[perm] = c
        c = tmp
    if spec.get("reverse_text"):
        c = c[::-1].copy()
    lit = np.isin(c, spec["skip"]) if spec["skip"] else np.zeros(len(c), dtype=bool)
    work = c[~lit]
    if spec["map"] == "reverse":
        work = (n - 1) - work
    st = spec["stream"]
    if st["kind"] == "autokey":
        p = _autokey_dec(work, st, n, spec["combine"])
    else:
        p = _combine_dec(work, _stream_values(st, len(work), n), n, spec["combine"])
    out = c.copy()
    out[~lit] = p
    return out.astype(np.int16)


def _autokey_dec(c: np.ndarray, st: dict, n: int, how: str) -> np.ndarray:
    primer = list(st["primer"])
    m = len(primer)
    p = np.empty(len(c), dtype=np.int64)
    for i in range(len(c)):
        if i < m:
            k = primer[i]
        else:
            k = p[i - m] if st["source"] == "plaintext" else c[i - m]
        p[i] = _combine_dec(c[i:i + 1], np.array([k]), n, how)[0]
    return p


def encrypt(pt: np.ndarray, spec: dict, n: int) -> np.ndarray:
    """Inverse of decrypt (used for synthetic data). Plaintext symbols in `skip`
    are written literally. Round trips only if no other position encrypts to a
    skip symbol; `roundtrips` checks that."""
    p = np.asarray(pt, dtype=np.int64)
    lit = np.isin(p, spec["skip"]) if spec["skip"] else np.zeros(len(p), dtype=bool)
    work = p[~lit]
    st = spec["stream"]
    if st["kind"] == "autokey":
        primer = list(st["primer"])
        m = len(primer)
        cw = np.empty(len(work), dtype=np.int64)
        for i in range(len(work)):
            if i < m:
                k = primer[i]
            else:
                k = work[i - m] if st["source"] == "plaintext" else cw[i - m]
            cw[i] = _combine_enc(work[i:i + 1], np.array([k]), n, spec["combine"])[0]
    else:
        cw = _combine_enc(work, _stream_values(st, len(work), n), n, spec["combine"])
    if spec["map"] == "reverse":
        cw = (n - 1) - cw
    c = p.copy()
    c[~lit] = cw
    if spec.get("reverse_text"):
        c = c[::-1].copy()
    if spec.get("transpose"):
        c = c[_columnar_perm(spec["transpose"]["columnar"], len(c))]
    return c.astype(np.int16)


def roundtrips(pt: np.ndarray, spec: dict, n: int) -> bool:
    return bool(np.array_equal(decrypt(encrypt(pt, spec, n), spec, n), np.asarray(pt)))

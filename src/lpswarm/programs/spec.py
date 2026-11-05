"""Cipher programs: a small declarative language that generators (including LLMs)
use to propose ciphers. Models never write code; they write a JSON spec that this
module validates, compiles to integers, and interprets deterministically.

Decryption of ciphertext c (integers mod N), in order:
  1. transpose  : undo a transposition: {"columnar": [order]}, {"grid": {"width": w,
                  "read": R}}, {"railfence": {"rails": r}} or {"decimate": {"step": k}}
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
try, at most MAX_OFFSET_SPAN values), "transpose_range": [lo, hi] (the grid width, rail
count or decimation step to try), or a repeat stream with "exhaustive": true and a
"key_length" of 1..4 (every key of that length); `expand` turns these into attempts.

Words and symbol names are resolved through the alphabet at compile time, so a
compiled spec contains integers only and hashes canonically for the ledger.
"""
from __future__ import annotations

import copy
import functools
import hashlib
import itertools
import json
import math
from typing import Any, Iterator

import numpy as np

from lpswarm.alphabet import Alphabet
from lpswarm.programs.sequences import MAX_INDEX, SEQUENCES, window

SPEC_VERSION = 1
MAX_KEY_LEN = 64
MAX_OFFSET = 1_000_000
MAX_OFFSET_SPAN = 2000
MAX_WIDTH = 12
MAX_GRID_WIDTH = 500
MAX_RAILS = 64
MAX_STEP = 1000
MAX_EXPANSION = 5000          # concrete specs one proposal may expand to (ranges)
MAX_EXHAUSTIVE = 1_000_000    # ... or with an exhaustive key space
MAX_EXHAUSTIVE_LEN = 4
GRID_READS = ("rows_reversed", "columns", "columns_reversed", "boustrophedon_rows",
              "boustrophedon_columns", "diagonal", "spiral_in", "spiral_out")
TRANSPOSE_KINDS = ("columnar", "grid", "railfence", "decimate")
COMBINES = ("sub", "add", "beaufort")
MAPS = ("identity", "reverse")
STREAM_KINDS = ("constant", "repeat", "autokey", "sequence")
_TOP_KEYS = {"v", "stream", "combine", "map", "skip", "skip_mode", "reverse_text", "transpose",
             "transpose_range", "offset_range", "note"}


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
    mode = raw.get("skip_mode", "all")
    if mode not in ("all", "resolve"):
        raise SpecError('skip_mode must be "all" or "resolve"')
    if mode == "resolve":
        # Only stored when used, so existing specs keep their ledger identity.
        if not out["skip"]:
            raise SpecError('skip_mode "resolve" needs a skip list')
        out["skip_mode"] = "resolve"
    out["transpose"] = _compile_transpose(raw.get("transpose"))
    trr = raw.get("transpose_range")
    if trr is not None:
        kind = next(iter(out["transpose"])) if out["transpose"] else None
        if kind not in ("grid", "railfence", "decimate"):
            raise SpecError("transpose_range needs a grid, railfence or decimate transpose "
                            "(it sweeps the width, rail count or step)")
        if not (isinstance(trr, list) and len(trr) == 2):
            raise SpecError("transpose_range must be [lo, hi]")
        cap = {"grid": MAX_GRID_WIDTH, "railfence": MAX_RAILS, "decimate": MAX_STEP}[kind]
        lo, hi = _int(trr[0], "transpose_range", 2, cap), _int(trr[1], "transpose_range", 2, cap)
        if hi < lo or hi - lo + 1 > MAX_OFFSET_SPAN:
            raise SpecError(f"transpose_range must have lo <= hi and at most {MAX_OFFSET_SPAN} values")
        out["transpose_range"] = [lo, hi]     # only stored when used (old hashes unchanged)

    st = raw.get("stream")
    kind = st.get("kind") if isinstance(st, dict) else None
    if not isinstance(kind, str) or kind not in STREAM_KINDS:
        raise SpecError(f"stream must be an object with kind in {STREAM_KINDS}")
    allowed = {"constant": {"kind", "value"},
               "repeat": {"kind", "key", "word", "offset", "key_length", "exhaustive"},
               "autokey": {"kind", "primer", "word", "source"},
               "sequence": {"kind", "name", "offset", "scale", "add"}}[kind]
    extra = [k for k in st if k not in allowed]
    if extra:
        raise SpecError(f"unknown stream fields {sorted(map(str, extra))[:5]} for kind {kind}")
    if kind == "constant":
        s: dict[str, Any] = {"kind": kind, "value": _int(st.get("value", 0), "value") % n}
    elif kind == "repeat" and st.get("exhaustive") is not None and _bool(st["exhaustive"], "exhaustive"):
        if "key" in st or "word" in st or "offset" in st:
            raise SpecError("an exhaustive repeat stream takes only key_length (no key, word or offset)")
        m = _int(st.get("key_length"), "key_length", 1, MAX_EXHAUSTIVE_LEN)
        if n ** m > MAX_EXHAUSTIVE:
            raise SpecError(f"{n}^{m} keys is more than the limit of {MAX_EXHAUSTIVE}")
        # A template: `expand` enumerates the keys. Only stored when used.
        s = {"kind": kind, "key": [0] * m, "offset": 0, "exhaustive": True, "n": n}
    elif kind == "repeat":
        if st.get("key_length") is not None:
            raise SpecError('key_length is only for {"exhaustive": true} repeat streams')
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
    if out.get("skip_mode") == "resolve" and kind == "autokey":
        raise SpecError('skip_mode "resolve" does not support autokey streams')

    rng = raw.get("offset_range")
    if rng is not None:
        if kind not in ("repeat", "sequence"):
            raise SpecError("offset_range only applies to repeat and sequence streams")
        if s.get("exhaustive"):
            raise SpecError("offset_range does not combine with an exhaustive repeat stream")
        if not (isinstance(rng, list) and len(rng) == 2):
            raise SpecError("offset_range must be [lo, hi]")
        cap = _seq_limit(s["name"]) if kind == "sequence" else MAX_OFFSET
        lo, hi = _int(rng[0], "offset_range", 0, cap), _int(rng[1], "offset_range", 0, cap)
        if hi < lo or hi - lo + 1 > MAX_OFFSET_SPAN:
            raise SpecError(f"offset_range must have lo <= hi and at most {MAX_OFFSET_SPAN} values")
        out["offset_range"] = [lo, hi]
    else:
        out["offset_range"] = None
    total = ((out["transpose_range"][1] - out["transpose_range"][0] + 1) if out.get("transpose_range") else 1)
    total *= (out["offset_range"][1] - out["offset_range"][0] + 1) if out["offset_range"] else 1
    if s.get("exhaustive"):
        total *= n ** len(s["key"])
        if total > MAX_EXHAUSTIVE:
            raise SpecError(f"proposal expands to {total} ciphers; the limit is {MAX_EXHAUSTIVE}")
    elif total > MAX_EXPANSION:
        raise SpecError(f"proposal expands to {total} ciphers; the limit is {MAX_EXPANSION}")
    return _normalise(out)


def _compile_transpose(tr: Any) -> dict | None:
    if tr is None or tr is False:
        return None
    if not isinstance(tr, dict) or len(tr) != 1 or next(iter(tr)) not in TRANSPOSE_KINDS:
        raise SpecError('transpose must have exactly one of {"columnar": [order]}, '
                        '{"grid": {"width": w, "read": R}}, {"railfence": {"rails": r}}, '
                        '{"decimate": {"step": k}}')
    kind, val = next(iter(tr.items()))
    if kind == "columnar":
        if not isinstance(val, list):
            raise SpecError('transpose must be {"columnar": [column order]}')
        if not 2 <= len(val) <= MAX_WIDTH:
            raise SpecError(f"columnar width must be 2..{MAX_WIDTH}")
        order = [_int(v, "columnar order", 0, MAX_WIDTH - 1) for v in val]
        if sorted(order) != list(range(len(order))):
            raise SpecError("columnar order must be a permutation of 0..width-1")
        return {"columnar": order}
    if not isinstance(val, dict):
        raise SpecError(f"transpose {kind} must be an object")
    if kind == "grid":
        if set(val) != {"width", "read"}:
            raise SpecError('grid needs exactly {"width": w, "read": R}')
        read = val["read"]
        if not isinstance(read, str) or read not in GRID_READS:
            raise SpecError(f"grid read must be one of {GRID_READS}")
        return {"grid": {"width": _int(val["width"], "grid width", 2, MAX_GRID_WIDTH), "read": read}}
    if kind == "railfence":
        if set(val) != {"rails"}:
            raise SpecError('railfence needs exactly {"rails": r}')
        return {"railfence": {"rails": _int(val["rails"], "rails", 2, MAX_RAILS)}}
    if set(val) != {"step"}:
        raise SpecError('decimate needs exactly {"step": k}')
    return {"decimate": {"step": _int(val["step"], "decimate step", 2, MAX_STEP)}}


def _spiral(rows: int, cols: int) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    top, bot, left, right = 0, rows - 1, 0, cols - 1
    while top <= bot and left <= right:
        out += [(top, c) for c in range(left, right + 1)]
        out += [(r, right) for r in range(top + 1, bot + 1)]
        if top < bot:
            out += [(bot, c) for c in range(right - 1, left - 1, -1)]
        if left < right:
            out += [(r, left) for r in range(bot - 1, top, -1)]
        top, bot, left, right = top + 1, bot - 1, left + 1, right - 1
    return out


@functools.lru_cache(maxsize=512)
def _perm_cached(kind: str, a: Any, b: Any, length: int) -> np.ndarray:
    """perm such that ciphertext[j] = plaintext[perm[j]] for a transposition of `length`
    symbols. Grids are written row by row (the last row may be short) and read by `a`."""
    if kind == "railfence":
        period = 2 * (a - 1)
        m = np.arange(length) % period
        rails = np.where(m < a, m, period - m)
        return np.argsort(rails, kind="stable")
    if kind == "decimate":
        if math.gcd(a, length) != 1:
            raise SpecError(f"decimate step {a} must be coprime to the text length {length}")
        return (np.arange(length) * a) % length
    width, read = a, b          # grid
    rows = -(-length // width)
    if read == "rows_reversed":
        order = [(r, c) for r in range(rows - 1, -1, -1) for c in range(width)]
    elif read == "columns":
        order = [(r, c) for c in range(width) for r in range(rows)]
    elif read == "columns_reversed":
        order = [(r, c) for c in range(width - 1, -1, -1) for r in range(rows)]
    elif read == "boustrophedon_rows":
        order = [(r, c) for r in range(rows)
                 for c in (range(width) if r % 2 == 0 else range(width - 1, -1, -1))]
    elif read == "boustrophedon_columns":
        order = [(r, c) for c in range(width)
                 for r in (range(rows) if c % 2 == 0 else range(rows - 1, -1, -1))]
    elif read == "diagonal":
        order = [(r, d - r) for d in range(rows + width - 1) for r in range(rows) if 0 <= d - r < width]
    elif read == "spiral_in":
        order = _spiral(rows, width)
    else:                        # spiral_out
        order = _spiral(rows, width)[::-1]
    idx = [r * width + c for r, c in order if r * width + c < length]
    return np.asarray(idx, dtype=np.int64)


def _transpose_perm(tr: dict, length: int) -> np.ndarray:
    if "columnar" in tr:
        return _columnar_perm(tr["columnar"], length)
    if "grid" in tr:
        return _perm_cached("grid", tr["grid"]["width"], tr["grid"]["read"], length)
    if "railfence" in tr:
        return _perm_cached("railfence", tr["railfence"]["rails"], None, length)
    return _perm_cached("decimate", tr["decimate"]["step"], None, length)


def _normalise(spec: dict) -> dict:
    st = spec["stream"]
    if st["kind"] == "repeat" and not spec.get("offset_range") and not st.get("exhaustive"):
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


def _with_transpose_param(tr: dict, v: int) -> dict:
    if "grid" in tr:
        return {"grid": {"width": v, "read": tr["grid"]["read"]}}
    if "railfence" in tr:
        return {"railfence": {"rails": v}}
    return {"decimate": {"step": v}}


def expand_iter(spec: dict, length: int | None = None) -> Iterator[dict]:
    """Lazily yield one concrete spec per combination of offset_range, transpose_range and
    (for an exhaustive repeat stream) every key of that length. Duplicates after
    normalisation are skipped, except for exhaustive keys, which are unique by
    construction. With `length` (the text length), decimation steps that are not
    coprime to it are skipped (they are not ciphers for a text of that length)."""
    st = spec["stream"]
    exhaustive = bool(st.get("exhaustive"))
    if not (exhaustive or spec.get("offset_range") or spec.get("transpose_range")):
        yield spec
        return
    trs = [spec["transpose"]]
    if spec.get("transpose_range"):
        lo, hi = spec["transpose_range"]
        trs = [_with_transpose_param(spec["transpose"], v) for v in range(lo, hi + 1)]
        if length is not None:
            trs = [t for t in trs if "decimate" not in t or math.gcd(t["decimate"]["step"], length) == 1]
    offs: list[int | None] = [None]
    if spec.get("offset_range"):
        lo, hi = spec["offset_range"]
        offs = list(range(lo, hi + 1))
    keys: Any = [None]
    if exhaustive:
        keys = itertools.product(range(st["n"]), repeat=len(st["key"]))
    seen: set[str] = set()
    for k in keys:
        for tr in trs:
            for o in offs:
                s = dict(spec)
                s["transpose"] = tr
                s["offset_range"] = None
                s.pop("transpose_range", None)
                stream = dict(st)
                stream.pop("exhaustive", None)
                stream.pop("n", None)
                if k is not None:
                    stream["key"] = list(k)
                if o is not None:
                    stream["offset"] = int(o)
                s["stream"] = stream
                s = _normalise(s)
                if not exhaustive:
                    h = canonical(s)
                    if h in seen:
                        continue
                    seen.add(h)
                yield s


def expand(spec: dict, length: int | None = None) -> list[dict]:
    """`expand_iter` as a list ([spec] if the spec has no ranges)."""
    return list(expand_iter(spec, length))


def describe(spec: dict, alphabet: Alphabet | None = None) -> str:
    """Short human-readable summary for the ledger and prompts."""
    st = spec["stream"]
    if st["kind"] == "constant":
        k = f"constant {st['value']}"
    elif st["kind"] == "repeat":
        key = st["key"]
        word = alphabet.decode(key) if alphabet else key
        if st.get("exhaustive"):
            k = f"repeat EVERY key of length {len(st['key'])}"
        else:
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
        parts.append(f"skip {sk}" + (" (resolve)" if spec.get("skip_mode") == "resolve" else ""))
    if spec["reverse_text"]:
        parts.append("reverse text")
    if spec["transpose"]:
        tr = spec["transpose"]
        if "columnar" in tr:
            parts.append(f"columnar {tr['columnar']}")
        elif "grid" in tr:
            parts.append(f"grid width {tr['grid']['width']} read {tr['grid']['read']}")
        elif "railfence" in tr:
            parts.append(f"railfence {tr['railfence']['rails']} rails")
        else:
            parts.append(f"decimate step {tr['decimate']['step']}")
    if spec.get("transpose_range"):
        parts.append(f"transpose param {spec['transpose_range'][0]}..{spec['transpose_range'][1]}")
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
        perm = _transpose_perm(spec["transpose"], len(c))
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
        c = c[_transpose_perm(spec["transpose"], len(c))]
    return c.astype(np.int16)


def roundtrips(pt: np.ndarray, spec: dict, n: int) -> bool:
    return bool(np.array_equal(decrypt(encrypt(pt, spec, n), spec, n), np.asarray(pt)))

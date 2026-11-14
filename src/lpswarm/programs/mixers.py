"""The `mix` stage of cipher programs: transformations that combine a rune with its
neighbours or work on small groups of runes.

A mix is applied to the whole integer sequence (mod N) either before the skip/map/combine/
stream core of a decryption (`"at": "before"`, the default) or after it (`"at": "after"`).
Kinds (all JSON objects with a "kind" field):

  neighbor   out_i = x_i OP x_(i+-lag)               OP: add sub rsub mul div rdiv
             {"kind": "neighbor", "op": "add", "lag": 1, "dir": "next", "times": 1}
  chain      out_i = x_i OP out_(i+-lag)             (the recursive form), OP: add sub rsub mul div
             {"kind": "chain", "op": "sub", "lag": 1, "dir": "prev"}
  window     out_i = x_i + x_(i-1) + ... + x_(i-size+1)
             {"kind": "window", "size": 3}
  hill       blocks of `size` runes (2..4) are multiplied by a matrix mod N
             {"kind": "hill", "size": 2, "matrix": [a, b, c, d]}  or  {"kind": "hill", "size": 2,
              "exhaustive": true}  (every invertible matrix; "family": circulant |
              upper_triangular | diagonal for sizes 3 and 4)
  block_perm positions inside each block of `size` runes (2..8) are permuted
             {"kind": "block_perm", "size": 3, "perm": [2, 0, 1]} or {... "exhaustive": true}

neighbor / chain / window take an optional "reset": "word" (never cross a word boundary;
needs word breaks and no transposition) or {"every": k}. Edges, partial trailing blocks and
the first element of each segment are left unchanged. Multiplication and division use the
usual inverse mod N for symbols that have one; the zero symbol (and any non-unit) is
absorbing for `mul`, and `div`/`rdiv` leave the symbol unchanged when the divisor has no inverse.
"""
from __future__ import annotations

import itertools
import math
from typing import Any, Iterator

import numpy as np

from lpswarm.programs.spec import MAX_EXHAUSTIVE, SpecError

MIX_KINDS = ("neighbor", "chain", "window", "hill", "block_perm")
NEIGHBOR_OPS = ("add", "sub", "rsub", "mul", "div", "rdiv")
CHAIN_OPS = ("add", "sub", "rsub", "mul", "div")
HILL_FAMILIES = ("full", "circulant", "upper_triangular", "diagonal")
MAX_LAG = 16
MAX_TIMES = 3
MAX_WINDOW = 16
MAX_EVERY = 4096
_COMMON = {"kind", "at"}


def _int(x: Any, what: str, lo: int, hi: int) -> int:
    if isinstance(x, bool) or not isinstance(x, int):
        raise SpecError(f"mix {what} must be an integer, got {x!r}")
    if not lo <= x <= hi:
        raise SpecError(f"mix {what} must be in [{lo}, {hi}], got {x}")
    return x


def _units(n: int) -> list[int]:
    return [u for u in range(1, n) if math.gcd(u, n) == 1]


def _inv_table(n: int) -> np.ndarray:
    t = np.full(n, -1, dtype=np.int64)
    for u in _units(n):
        t[u] = pow(u, -1, n)
    return t


# ------------------------------------------------------------------ matrices
def _det(m: list[list[int]], n: int) -> int:
    k = len(m)
    if k == 1:
        return m[0][0] % n
    total = 0
    for j in range(k):
        minor = [row[:j] + row[j + 1:] for row in m[1:]]
        total += (-1) ** j * m[0][j] * _det(minor, n)
    return total % n


def _rows(flat: list[int], g: int) -> list[list[int]]:
    return [list(flat[i * g:(i + 1) * g]) for i in range(g)]


def invertible(flat: list[int], g: int, n: int) -> bool:
    return math.gcd(_det(_rows(flat, g), n), n) == 1


def mat_inverse(flat: list[int], g: int, n: int) -> list[int]:
    m = _rows(flat, g)
    det = _det(m, n)
    if math.gcd(det, n) != 1:
        raise SpecError("hill matrix is not invertible mod N")
    dinv = pow(det, -1, n)
    if g == 1:
        return [dinv]
    out = [0] * (g * g)
    for i in range(g):
        for j in range(g):
            minor = [row[:i] + row[i + 1:] for k, row in enumerate(m) if k != j]
            out[i * g + j] = ((-1) ** (i + j) * _det(minor, n) * dinv) % n
    return out


def _hill_matrices(size: int, family: str, n: int) -> Iterator[list[int]]:
    g = size
    if family == "full":
        for flat in itertools.product(range(n), repeat=g * g):
            if invertible(list(flat), g, n):
                yield list(flat)
    elif family == "circulant":
        for row in itertools.product(range(n), repeat=g):
            flat = [row[(j - i) % g] for i in range(g) for j in range(g)]
            if invertible(flat, g, n):
                yield flat
    elif family == "upper_triangular":     # unit diagonal, so always invertible
        pos = [(i, j) for i in range(g) for j in range(i + 1, g)]
        for vals in itertools.product(range(n), repeat=len(pos)):
            m = [[1 if i == j else 0 for j in range(g)] for i in range(g)]
            for (i, j), v in zip(pos, vals):
                m[i][j] = v
            yield [x for row in m for x in row]
    else:                                  # diagonal
        for d in itertools.product(_units(n), repeat=g):
            yield [d[i] if i == j else 0 for i in range(g) for j in range(g)]


def _family_count(size: int, family: str, n: int) -> int:
    """Upper bound on the matrices of a family (invertibility filters a few out)."""
    if family == "full":
        return n ** (size * size)
    if family == "circulant":
        return n ** size
    if family == "upper_triangular":
        return n ** (size * (size - 1) // 2)
    return max(1, len(_units(n))) ** size


# ------------------------------------------------------------------- compile
def compile_mix(raw: Any, n: int) -> dict | None:
    """Validate a `mix` object and return its canonical form (None for no mix)."""
    if raw is None or raw is False:
        return None
    if not isinstance(raw, dict):
        raise SpecError("mix must be an object with a kind")
    kind = raw.get("kind")
    if not isinstance(kind, str) or kind not in MIX_KINDS:
        raise SpecError(f"mix kind must be one of {MIX_KINDS}")
    at = raw.get("at", "before")
    if at not in ("before", "after"):
        raise SpecError('mix at must be "before" or "after"')
    out: dict[str, Any] = {"kind": kind, "at": at}

    def only(allowed: set[str]) -> None:
        extra = [k for k in raw if k not in allowed | _COMMON]
        if extra:
            raise SpecError(f"unknown mix fields {sorted(map(str, extra))[:5]} for kind {kind}")

    if kind in ("neighbor", "chain", "window"):
        only({"op", "lag", "dir", "times", "reset", "size"})
        if kind != "window":
            ops = NEIGHBOR_OPS if kind == "neighbor" else CHAIN_OPS
            op = raw.get("op")
            if not isinstance(op, str) or op not in ops:
                raise SpecError(f"{kind} op must be one of {ops}")
            d = raw.get("dir", "next" if kind == "neighbor" else "prev")
            if d not in ("next", "prev"):
                raise SpecError('dir must be "next" or "prev"')
            out.update(op=op, lag=_int(raw.get("lag", 1), "lag", 1, MAX_LAG), dir=d,
                       times=_int(raw.get("times", 1), "times", 1, MAX_TIMES))
        else:
            out["size"] = _int(raw.get("size"), "window size", 2, MAX_WINDOW)
        reset = raw.get("reset")
        if reset in (None, "none"):
            out["reset"] = None
        elif reset == "word":
            out["reset"] = "word"
        elif isinstance(reset, dict) and set(reset) == {"every"}:
            out["reset"] = {"every": _int(reset["every"], "reset every", 2, MAX_EVERY)}
        else:
            raise SpecError('reset must be "none", "word" or {"every": k}')
        out["count"] = 1
        return out
    if kind == "hill":
        only({"size", "matrix", "exhaustive", "family"})
        g = _int(raw.get("size"), "hill size", 2, 4)
        if raw.get("exhaustive"):
            fam = raw.get("family", "full")
            if fam not in HILL_FAMILIES:
                raise SpecError(f"hill family must be one of {HILL_FAMILIES}")
            if "matrix" in raw:
                raise SpecError("an exhaustive hill mix takes no matrix")
            count = _family_count(g, fam, n)
            if count > MAX_EXHAUSTIVE:
                raise SpecError(f"{fam} {g}x{g} matrices ({count}) exceed the limit of "
                                f"{MAX_EXHAUSTIVE}; pick a smaller family or size")
            out.update(size=g, exhaustive=True, family=fam, matrix=[0] * (g * g), n=n, count=count)
            return out
        mat = raw.get("matrix")
        if not (isinstance(mat, list) and len(mat) == g * g):
            raise SpecError(f"hill matrix must be a list of {g * g} integers (row by row)")
        flat = [_int(v, "hill entry", -10_000, 10_000) % n for v in mat]
        if not invertible(flat, g, n):
            raise SpecError("hill matrix is not invertible mod N (its determinant shares a factor with N)")
        out.update(size=g, matrix=flat, count=1)
        return out
    only({"size", "perm", "exhaustive"})              # block_perm
    g = _int(raw.get("size"), "block size", 2, 8)
    if raw.get("exhaustive"):
        if "perm" in raw:
            raise SpecError("an exhaustive block_perm takes no perm")
        out.update(size=g, exhaustive=True, perm=list(range(g)), count=math.factorial(g))
        return out
    perm = raw.get("perm")
    if not (isinstance(perm, list) and sorted(perm) == list(range(g))
            and all(isinstance(v, int) and not isinstance(v, bool) for v in perm)):
        raise SpecError(f"block_perm perm must be a permutation of 0..{g - 1}")
    out.update(size=g, perm=list(perm), count=1)
    return out


def mix_count(mix: dict | None) -> int:
    return int(mix.get("count", 1)) if mix else 1


def expand_mix(mix: dict) -> Iterator[dict]:
    """Concrete mixes of an exhaustive one (lazy); [mix] otherwise."""
    if not mix.get("exhaustive"):
        yield mix
        return
    base = {k: v for k, v in mix.items() if k not in ("exhaustive", "family", "n", "count")}
    if mix["kind"] == "hill":
        for flat in _hill_matrices(mix["size"], mix["family"], mix["n"]):
            yield {**base, "matrix": flat, "count": 1}
    else:
        for perm in itertools.permutations(range(mix["size"])):
            yield {**base, "perm": list(perm), "count": 1}


def describe_mix(mix: dict) -> str:
    k = mix["kind"]
    if k in ("neighbor", "chain"):
        s = f"{k} {mix['op']} lag {mix['lag']} {mix['dir']}" + (f" x{mix['times']}" if mix["times"] > 1 else "")
    elif k == "window":
        s = f"window sum {mix['size']}"
    elif k == "hill":
        s = (f"hill {mix['size']}x{mix['size']} ALL {mix['family']} matrices" if mix.get("exhaustive")
             else f"hill {mix['size']}x{mix['size']} {mix['matrix']}")
    else:
        s = (f"block permutation size {mix['size']} ALL orders" if mix.get("exhaustive")
             else f"block permutation {mix['perm']}")
    if mix.get("reset"):
        s += f" reset {mix['reset'] if mix['reset'] == 'word' else 'every ' + str(mix['reset']['every'])}"
    return s + f" ({mix['at']} the key)"


# ------------------------------------------------------------------- apply
def _spans(length: int, reset: Any, breaks) -> list[tuple[int, int]]:
    if reset is None:
        return [(0, length)]
    if reset == "word":
        if not breaks:
            return [(0, length)]
        cuts = [0] + sorted({int(b) for b in breaks if 0 < int(b) < length}) + [length]
        return [(a, b) for a, b in zip(cuts, cuts[1:]) if b > a]
    k = reset["every"]
    return [(a, min(a + k, length)) for a in range(0, length, k)]


def _op(a: np.ndarray, b: np.ndarray, op: str, n: int, inv: np.ndarray) -> np.ndarray:
    if op == "add":
        return (a + b) % n
    if op == "sub":
        return (a - b) % n
    if op == "rsub":
        return (b - a) % n
    if op == "mul":
        return (a * b) % n
    if op == "div":
        ib = inv[b]
        return np.where(ib >= 0, (a * ib) % n, a)
    ia = inv[a]                                   # rdiv
    return np.where(ia >= 0, (b * ia) % n, b)


def _neighbor(x: np.ndarray, m: dict, n: int, inv: np.ndarray) -> np.ndarray:
    d, op = m["lag"], m["op"]
    for _ in range(m["times"]):
        if len(x) <= d:
            break
        out = x.copy()
        if m["dir"] == "next":
            out[:-d] = _op(x[:-d], x[d:], op, n, inv)
        else:
            out[d:] = _op(x[d:], x[:-d], op, n, inv)
        x = out
    return x


def _chain_forward(x: np.ndarray, op: str, d: int, n: int, inv: np.ndarray) -> np.ndarray:
    """out_i = x_i OP out_(i-d), the first d elements unchanged."""
    L = len(x)
    if L <= d:
        return x
    if op in ("add", "sub"):
        rows = -(-L // d)
        pad = np.zeros(rows * d, dtype=np.int64)
        pad[:L] = x
        mat = pad.reshape(rows, d)
        sign = np.where(np.arange(rows) % 2 == 0, 1, -1)[:, None] if op == "sub" else 1
        out = (sign * np.cumsum(sign * mat, axis=0)) % n
        return out.reshape(-1)[:L]
    out = x.copy()
    for i in range(d, L):
        prev, xi = int(out[i - d]), int(x[i])
        if op == "rsub":
            out[i] = (prev - xi) % n
        elif op == "mul":
            out[i] = (xi * prev) % n
        else:                                       # div
            out[i] = (xi * int(inv[prev])) % n if inv[prev] >= 0 else xi
    return out


def _chain(x: np.ndarray, m: dict, n: int, inv: np.ndarray) -> np.ndarray:
    for _ in range(m["times"]):
        if m["dir"] == "prev":
            x = _chain_forward(x, m["op"], m["lag"], n, inv)
        else:
            x = _chain_forward(x[::-1].copy(), m["op"], m["lag"], n, inv)[::-1].copy()
    return x


def _window(x: np.ndarray, size: int, n: int) -> np.ndarray:
    s = np.cumsum(x)
    out = s.copy()
    out[size:] = s[size:] - s[:-size]
    return out % n


def apply_mix(mix: dict, arr: np.ndarray, n: int, breaks=None) -> np.ndarray:
    """The decryption-direction transformation (see the module doc)."""
    x = np.asarray(arr, dtype=np.int64)
    k = mix["kind"]
    if k in ("neighbor", "chain", "window"):
        inv = _inv_table(n)
        out = x.copy()
        for a, b in _spans(len(x), mix.get("reset"), breaks):
            seg = x[a:b]
            if k == "neighbor":
                out[a:b] = _neighbor(seg, mix, n, inv)
            elif k == "chain":
                out[a:b] = _chain(seg, mix, n, inv)
            else:
                out[a:b] = _window(seg, mix["size"], n)
        return out
    g = mix["size"]
    nb = len(x) // g
    out = x.copy()
    if nb == 0:
        return out
    blocks = x[:nb * g].reshape(nb, g)
    if k == "hill":
        mat = np.asarray(mix["matrix"], dtype=np.int64).reshape(g, g)
        out[:nb * g] = ((blocks @ mat.T) % n).reshape(-1)
    else:
        out[:nb * g] = blocks[:, mix["perm"]].reshape(-1)
    return out


def invert_mix(mix: dict, arr: np.ndarray, n: int, breaks=None) -> np.ndarray:
    """The encryption-direction transformation: apply_mix(mix, invert_mix(mix, p)) == p.
    Defined for add / sub / rsub neighbour and chain mixes, hill and block_perm."""
    x = np.asarray(arr, dtype=np.int64)
    k = mix["kind"]
    if k in ("neighbor", "chain"):
        if mix["op"] not in ("add", "sub", "rsub"):
            raise SpecError(f"a {k} mix with op {mix['op']} has no inverse (zero and non-units)")
        out = x.copy()
        for a, b in _spans(len(x), mix.get("reset"), breaks):
            seg = x[a:b]
            for _ in range(mix["times"]):
                seg = _invert_segment(k, mix, seg, n)
            out[a:b] = seg
        return out
    if k == "window":
        raise SpecError("a window mix has no inverse")
    g = mix["size"]
    nb = len(x) // g
    out = x.copy()
    if nb == 0:
        return out
    blocks = x[:nb * g].reshape(nb, g)
    if k == "hill":
        inv = np.asarray(mat_inverse(mix["matrix"], g, n), dtype=np.int64).reshape(g, g)
        out[:nb * g] = ((blocks @ inv.T) % n).reshape(-1)
    else:
        inv_perm = np.argsort(mix["perm"])
        out[:nb * g] = blocks[:, inv_perm].reshape(-1)
    return out


def _invert_segment(kind: str, m: dict, p: np.ndarray, n: int) -> np.ndarray:
    d, op = m["lag"], m["op"]
    L = len(p)
    if L <= d:
        return p
    x = p.copy()
    if kind == "chain":
        # out_i = x_i OP out_(i-d) (prev) or out_(i+d) (next): solve for x from out = p
        if m["dir"] == "prev":
            q, r = p[d:], p[:-d]
            x[d:] = _solve(q, r, op, n)
        else:
            q, r = p[:-d], p[d:]
            x[:-d] = _solve(q, r, op, n)
        return x % n
    # neighbor: out_i = x_i OP x_(i+d) (next, solve backwards) or x_(i-d) (prev, forwards)
    if m["dir"] == "next":
        for i in range(L - d - 1, -1, -1):
            x[i] = _solve(p[i:i + 1], x[i + d:i + d + 1], op, n)[0]
    else:
        for i in range(d, L):
            x[i] = _solve(p[i:i + 1], x[i - d:i - d + 1], op, n)[0]
    return x % n


def _solve(out: np.ndarray, partner: np.ndarray, op: str, n: int) -> np.ndarray:
    """x such that x OP partner = out (for the chain form `partner` is the partner's output)."""
    if op == "add":
        return (out - partner) % n
    if op == "sub":
        return (out + partner) % n
    return (partner - out) % n                      # rsub

"""Phase 2 generators: three families of stateful ciphers outside the cipher language, screened against the repeat signature.

    python -m lpswarm.research_generators --out reports/diag

Brief: docs/plan_repeat_shortage.md and the Phase 2 brief ("non-zero-step generators"). No model, no oracle, no key text, no added leak.

A machine has a state; each plaintext rune p gives a new state and an output rune c. English plaintext goes through it (6 windows of 5,000 runes)
and the same four numbers as `research_signature` are measured (lag-1 ratio, lags 2-8, unigram IC, first-difference IC) plus the step-stream IC
(steps c[t] - c[t-1] mod 29, zeros dropped, step - 1 in 0..27, IC x 28; real text 1.001). For each variant: whether it can carry a message at all
(`invertible`: the share of reachable states in which the 29 plaintext runes give 29 different outputs), where its zero steps come from (the plaintext
rune that triggers them, if one does), and whether the plaintext word positions of its zero steps look like the real doubles' (which a plaintext-triggered
rule must, and EA's did not).

  1 table walk        a table of runes, state = current cell, each plaintext rune selects a move, output = the rune at the new cell
  2 permuting alphabet state = a permutation of the runes; encipher by lookup, then the emitted rune moves (to a slot, by a keyed swap, or Chaocipher
                       style on both alphabets)
  3 non-zero step     c[t] = c[t-1] + s[t], s[t] in 1..28 from a seeded state and the plaintext; the plaintext needs 28 symbols, so one rune is
                       skipped or folded into a neighbour

A family that gives exactly zero doubles is a near miss, not a pass. If a leak would be needed to match, the variant is reported as not passing.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np

from lpswarm import research_signature as S

N = 29
SEED = 20261111
WINDOWS = 6
WINDOW_LEN = 5000
INVERTIBLE_TRIALS = 40


# ----------------------------------------------------------------------------------------------------------- machines
class Machine:
    family = ""
    variant = ""
    symbols = N                          # plaintext alphabet size (28 for the non-zero-step machines)

    def init(self, rng):                 # -> state
        raise NotImplementedError

    def step(self, state, p):            # -> (state, c)
        raise NotImplementedError

    def outputs(self, state):            # the output for every plaintext symbol in this state (for invertibility and decipher)
        return [self.step(state, p)[1] for p in range(self.symbols)]


def encipher(m: Machine, plain, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    st = m.init(rng)
    out = np.empty(len(plain), dtype=np.int64)
    for t, p in enumerate(plain):
        st, out[t] = m.step(st, int(p))
    return out


def decipher(m: Machine, cipher, seed: int = 0) -> np.ndarray:
    """Inverse of `encipher` (same seed). Where two plaintext symbols give the same output the first is taken."""
    rng = np.random.default_rng(seed)
    st = m.init(rng)
    out = np.empty(len(cipher), dtype=np.int64)
    for t, c in enumerate(cipher):
        outs = m.outputs(st)
        p = outs.index(int(c))
        out[t] = p
        st = m.step(st, p)[0]
    return out


def invertible_share(m: Machine, trials: int = INVERTIBLE_TRIALS, seed: int = 1) -> float:
    """Share of states reached by a random walk in which every plaintext symbol has its own output."""
    rng = np.random.default_rng(seed)
    st = m.init(rng)
    ok = 0
    for _ in range(trials):
        for _ in range(int(rng.integers(1, 30))):
            st, _c = m.step(st, int(rng.integers(0, m.symbols)))
        ok += len(set(m.outputs(st))) == m.symbols
    return ok / trials


# 1 ---------------------------------------------------------------------------------------------------- table walk
GRID05 = np.array([[272, 138, 341, 131, 151], [366, 199, 130, 320, 18], [226, 245, 91, 245, 226],
                   [18, 320, 130, 199, 366], [151, 131, 341, 138, 272]]) % N


def make_table(kind: str) -> np.ndarray:
    rng = np.random.default_rng(7)
    r = np.arange(N)
    if kind == "cyclic Latin":
        return (r[:, None] + r[None, :]) % N
    if kind == "keyed Latin":
        pi, sg, ta = rng.permutation(N), rng.permutation(N), rng.permutation(N)
        return pi[(sg[:, None] + ta[None, :]) % N]
    if kind == "random 29x29":
        return rng.integers(0, N, size=(N, N))
    if kind == "page-05 grid 5x5":
        return GRID05.copy()
    if kind == "page-05 grid tiled":
        return np.tile(GRID05, (6, 6))[:N, :N]
    raise ValueError(kind)


def make_moves(kind: str) -> list[tuple[int, int]]:
    if kind == "row (0,j)":
        return [(0, j) for j in range(N)]
    if kind == "rook":
        m = []
        for j in range(1, 15):
            m += [(0, j), (j, 0)]
        return m + [(0, 15)]
    if kind == "diagonal (j,j)":
        return [(j, j) for j in range(N)]
    if kind == "near list":
        offs = sorted(((a, b) for a in range(-3, 4) for b in range(-3, 4) if (a, b) != (0, 0)), key=lambda t: (t[0] ** 2 + t[1] ** 2, t))
        return offs[:N]
    raise ValueError(kind)


class TableWalk(Machine):
    family = "1 table walk"

    def __init__(self, table: str, moves: str, edge: str):
        self.T, self.k = make_table(table), len(make_table(table))
        self.moves, self.edge = make_moves(moves), edge
        self.variant = f"{table}, {moves}, {edge}"

    def _fold(self, x: int) -> int:
        k = self.k
        if self.edge == "wrap":
            return x % k
        per = max(2 * k - 2, 1)
        x %= per
        return x if x < k else per - x

    def init(self, rng):
        return (int(rng.integers(0, self.k)), int(rng.integers(0, self.k)))

    def step(self, state, p):
        dr, dc = self.moves[p]
        r, c = self._fold(state[0] + dr), self._fold(state[1] + dc)
        return (r, c), int(self.T[r, c])


# 2 ------------------------------------------------------------------------------------------------ permuting alphabet
def _move(lst: list, i: int, slot: int) -> list:
    x = lst[i]
    rest = lst[:i] + lst[i + 1:]
    return rest[:slot] + [x] + rest[slot:]


class PermAlphabet(Machine):
    family = "2 permuting alphabet"

    def __init__(self, kind: str, param: int = 0):
        self.kind, self.param = kind, param
        self.variant = {"slot": f"emitted rune moves to slot {param}", "swap": f"emitted rune swaps with the one {param} places on",
                        "slot2": f"both alphabets, used rune moves to slot {param}", "chao": "Chaocipher (both alphabets)"}[kind]

    def init(self, rng):
        return (tuple(int(x) for x in rng.permutation(N)), tuple(int(x) for x in rng.permutation(N)))   # cipher alphabet, plain alphabet

    def step(self, state, p):
        pi, ro = list(state[0]), list(state[1])
        if self.kind in ("slot", "swap"):
            c = pi[p]
            if self.kind == "slot":
                pi = _move(pi, p, self.param)
            else:
                j = (p + self.param) % N
                pi[p], pi[j] = pi[j], pi[p]
            return (tuple(pi), tuple(ro)), c
        i = ro.index(p)
        c = pi[i]
        if self.kind == "slot2":
            return (tuple(_move(pi, i, self.param)), tuple(_move(ro, i, self.param))), c
        # Chaocipher: left alphabet (cipher) rotates so c is first, then the second letter moves to the nadir; right (plain) likewise with the third
        pi = pi[i:] + pi[:i]
        pi = pi[:1] + pi[2:14] + [pi[1]] + pi[14:]
        ro = ro[i:] + ro[:i]
        ro = ro[1:] + ro[:1]
        ro = ro[:2] + ro[3:14] + [ro[2]] + ro[14:]
        return (tuple(pi), tuple(ro)), c


# 3 ------------------------------------------------------------------------------------------------ non-zero-step machine
class NonZeroStep(Machine):
    """c[t] = c[t-1] + s[t] with s[t] = 1 + ((p'[t] + x[t]) mod 28), x from a seeded generator; p' is the plaintext in 28 symbols."""
    family = "3 non-zero step"
    symbols = 28

    def __init__(self, gen: str):
        self.gen = gen
        self.variant = {"lcg": "x = 2x mod 29 (primitive root, 1..28)", "lagfib": "lagged Fibonacci mod 28 (3, 7)", "matrix": "2x2 matrix power mod 29",
                        "autokey": "x += p' + 1 (plaintext feedback)"}[gen]

    def init(self, rng):
        c0 = int(rng.integers(0, N))
        if self.gen == "lcg":
            x = int(rng.integers(1, N))
        elif self.gen == "lagfib":
            x = tuple(int(v) for v in rng.integers(0, 28, size=7))
        elif self.gen == "matrix":
            x = (int(rng.integers(1, N)), int(rng.integers(1, N)))
        else:
            x = int(rng.integers(0, 28))
        return (c0, x)

    def step(self, state, p):
        c0, x = state
        if self.gen == "lcg":
            k, x2 = x % 28, (2 * x) % N
        elif self.gen == "lagfib":
            k, x2 = x[-1], x[1:] + ((x[-3] + x[-7]) % 28,)
        elif self.gen == "matrix":
            k, x2 = x[0] % 28, ((3 * x[0] + x[1]) % N, (x[0] + 2 * x[1]) % N)
        else:
            k, x2 = x, (x + p + 1) % 28
        s = 1 + ((p + k) % 28)
        c = (c0 + s) % N
        return (c, x2), c

    def outputs(self, state):            # outputs depend on the step from the previous output, which is state[0]
        return [self.step(state, p)[1] for p in range(self.symbols)]


def fold_plaintext(plain: np.ndarray, mode: str, rune: int):
    """Plaintext in 28 symbols: drop every `rune` (skip) or fold it into the next rune (fold). Returns (symbols 0..27, original index of each)."""
    plain = np.asarray(plain, dtype=np.int64)
    idx = np.arange(len(plain))
    if mode == "skip":
        keep = plain != rune
        p, idx = plain[keep], idx[keep]
    else:
        p = np.where(plain == rune, (rune + 1) % N, plain)
    return np.where(p > rune, p - 1, p).astype(np.int64), idx


# ------------------------------------------------------------------------------------------------------- screening
def word_categories(n: int, breaks) -> np.ndarray:
    starts = np.zeros(n + 1, bool)
    starts[[b for b in breaks if b < n]] = True
    starts[n] = True
    out = np.empty(n, dtype=object)
    for j in range(n):
        a, b = starts[j], starts[j + 1]
        out[j] = "single" if (a and b) else "initial" if a else "final" if b else "internal"
    return out


def run_variant(m: Machine, windows, ref: dict, rune: int | None = None, mode: str | None = None) -> dict:
    units, steps, zero_plain, zero_cat = {}, [], [], []
    for w, (pt, br) in enumerate(windows):
        cats = word_categories(len(pt), br)
        if rune is not None:
            p, idx = fold_plaintext(pt, mode, rune)
        else:
            p, idx = pt, np.arange(len(pt))
        c = encipher(m, p, seed=w + 1)
        units[str(w)] = c
        d = (c[1:] - c[:-1]) % N
        steps.append(d[d != 0] - 1)
        z = np.nonzero(d == 0)[0] + 1
        zero_plain += [int(pt[idx[t]]) for t in z]
        zero_cat += [cats[idx[t]] for t in z]
    pr = S.profile(units)
    cl = S.classify(pr["ratio"], ref, None, None, pr["uni_ic"], pr["diff_ic"])
    st = np.concatenate(steps)
    ic28 = float(28 * (np.bincount(st, minlength=28) * (np.bincount(st, minlength=28) - 1)).sum() / (len(st) * (len(st) - 1))) if len(st) > 1 else float("nan")
    nz = len(zero_plain)
    top = Counter(zero_plain).most_common(1)[0] if nz else (None, 0)
    cats = Counter(zero_cat)
    real = {"initial": 21, "internal": 47, "final": 18, "single": 0}
    pos_p = None
    if nz >= 20:
        names = ["initial", "internal", "final", "single"]
        prop = np.array([cats.get(k, 0) for k in names], float)
        prop /= prop.sum()
        o = np.array([real[k] for k in names])
        e = o.sum() * prop
        use = e > 0
        stat = float(((o - e)[use] ** 2 / e[use]).sum())
        rng = np.random.default_rng(1)
        null = rng.multinomial(o.sum(), prop, size=5000)
        ns = (((null - e) ** 2 / np.where(use, e, 1)) * use).sum(axis=1)
        pos_p = (1 + int((ns >= stat).sum())) / 5001
    lag1 = float(pr["ratio"][0])
    lo, hi = ref["ci"]
    flat = cl["flat"] and cl["ic_ok"]
    verdict = "full match" if cl["full"] else ("near miss: too few repeats" if flat and lag1 < lo else "no")
    if nz == 0:
        source = "none (no zero steps)"
    elif top[1] / nz > 0.6:
        source = f"plaintext rune {top[0]} ({100 * top[1] / nz:.0f}% of zeros)"
    else:
        source = "state / key dependent (no single plaintext rune)"
    return {"family": m.family, "variant": m.variant + (f"; rune {rune} {mode}" if rune is not None else ""), "invertible": invertible_share(m),
            "lag1": lag1, "rest": [float(pr["ratio"][1:].min()), float(pr["ratio"][1:].max())], "uni_ic": float(pr["uni_ic"]),
            "diff_ic": float(pr["diff_ic"]), "step_ic28": ic28, "zeros": nz, "verdict": verdict, "source": source, "word_position_p": pos_p}


def all_machines() -> list[tuple[Machine, dict]]:
    out = []
    for table in ("cyclic Latin", "keyed Latin", "random 29x29", "page-05 grid 5x5", "page-05 grid tiled"):
        for moves in ("row (0,j)", "rook", "diagonal (j,j)", "near list"):
            for edge in ("wrap", "reflect"):
                out.append((TableWalk(table, moves, edge), {}))
    for slot in (0, 7, 14, 21, 28):
        out.append((PermAlphabet("slot", slot), {}))
        out.append((PermAlphabet("slot2", slot), {}))
    for d in (1, 7, 14):
        out.append((PermAlphabet("swap", d), {}))
    out.append((PermAlphabet("chao"), {}))
    for gen in ("lcg", "lagfib", "matrix", "autokey"):
        for rune in (28, 0, 14):                      # EA, F, X
            for mode in ("skip", "fold"):
                out.append((NonZeroStep(gen), {"rune": rune, "mode": mode}))
    return out


def markdown(rows: list[dict], ref: dict) -> str:
    L = ["# Phase 2 generators: three stateful families against the repeat signature", "",
         "**SYNTHETIC: English plaintext (training split), 6 windows of 5,000 runes; no oracle, no model, no added leak.** Real text: lag 1 "
         f"{ref['ratio']:.2f} (95% interval {ref['ci'][0]:.2f}-{ref['ci'][1]:.2f}), lags 2-8 at chance, unigram IC {ref['uni_ic']:.2f}, first-difference IC "
         f"{ref['diff_ic']:.2f}, step-stream IC x 28 1.001. `invertible` = share of reachable states where all plaintext symbols give different outputs "
         "(a machine below 1.00 cannot carry every message). `word-position p` = do the plaintext word positions of the machine's zero steps look like the real "
         "doubles' (21 / 47 / 18 initial / internal / final)?", "",
         "| family | variant | invertible | lag 1 | lags 2-8 | unigram IC | diff IC | step IC x 28 | zeros | verdict | source of zeros | word-position p |",
         "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | ---: |"]
    for r in rows:
        wp = "" if r["word_position_p"] is None else f"{r['word_position_p']:.4f}"
        L.append(f"| {r['family']} | {r['variant']} | {r['invertible']:.2f} | {r['lag1']:.2f} | {r['rest'][0]:.2f}-{r['rest'][1]:.2f} | {r['uni_ic']:.2f} | "
                 f"{r['diff_ic']:.2f} | {r['step_ic28']:.3f} | {r['zeros']} | **{r['verdict']}** | {r['source']} | {wp} |")
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> int:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET, load_sections
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_generators", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="reports/diag")
    args = ap.parse_args(argv)
    alpha = get_alphabet(ALPHABET)
    ref = S.reference(load_sections(indexes=list(S.SECTIONS)))
    windows = S.english_windows(alpha, WINDOWS, WINDOW_LEN, SEED)
    rows = [run_variant(m, windows, ref, kw.get("rune"), kw.get("mode")) for m, kw in all_machines()]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "generators.json").write_text(json.dumps({"reference": ref, "rows": rows}, indent=1, default=str) + "\n", encoding="utf-8")
    text = markdown(rows, ref)
    (out / "generators.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

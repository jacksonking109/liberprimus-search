"""Literal readings of the 2016 hint ("its words are the map, their meaning is the road, and their numbers are the direction").

    python -m lpswarm.research_literal --out reports/diag

No oracle, no models; exploratory. "Numbers" are the Gematria prime values of the runes (F = 2 ... EA = 109).

prime-keyed   the number of a rune as the key for the next one: p[t] = c[t] -/+ g(c[t-k]) (mod 29), k = 1..3, with g = the prime value, or
              the running sum of the prime values of everything before. A self-keyed cipher outside the cipher language. Scored by the index of
              coincidence (IC) of the result per section (language 1.7-2.0, flag 1.25), and screened against the repeat signature.
jumps         the numbers as steps through a page: from each start, move forward (or back) by the prime value of the current rune (wrapping on
              the page) and read the runes visited. Scored by English bigram log-likelihood against the same walk on the page's runes shuffled.
grids         pages whose rune count is a square, laid out as a grid: row, column and diagonal prime sums, against the numbers the hints
              supply (563, 569, 1136, 1033, 3301, 121).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

N = 29
PRIMES = np.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109])
HINT_NUMBERS = (563, 569, 1136, 1033, 3301, 121, 464)
SEED = 20261109


def ic29(x) -> float:
    x = np.asarray(x, dtype=np.int64)
    if len(x) < 2:
        return 0.0
    c = np.bincount(x, minlength=N)
    return float(N * (c * (c - 1)).sum() / (len(x) * (len(x) - 1)))


# --------------------------------------------------------------------------------------------- prime-keyed
def key_stream(c: np.ndarray, kind: str, lag: int) -> np.ndarray:
    """Key for position t from the ciphertext before it (positions without a key get 0 and are dropped)."""
    c = np.asarray(c, dtype=np.int64)
    k = np.zeros(len(c), dtype=np.int64)
    if kind == "prime of rune t-lag":
        k[lag:] = PRIMES[c[:-lag]] % N
    elif kind == "running sum of primes before t":
        k[1:] = np.cumsum(PRIMES[c])[:-1] % N
    return k


def decrypt_self_keyed(c: np.ndarray, kind: str, lag: int, sign: int) -> np.ndarray:
    start = lag if kind == "prime of rune t-lag" else 1
    c = np.asarray(c, dtype=np.int64)
    return ((c - sign * key_stream(c, kind, lag)) % N)[start:]


def encrypt_self_keyed(p: np.ndarray, kind: str, lag: int, sign: int, seed: int = 0) -> np.ndarray:
    """Inverse of decrypt_self_keyed (the first `lag` runes are random, as an unknown start)."""
    rng = np.random.default_rng(seed)
    p = np.asarray(p, dtype=np.int64)
    start = lag if kind == "prime of rune t-lag" else 1
    c = np.zeros(len(p) + start, dtype=np.int64)
    c[:start] = rng.integers(0, N, size=start)
    run = int(PRIMES[c[:start]].sum())
    for t in range(start, len(c)):
        key = PRIMES[c[t - lag]] % N if kind == "prime of rune t-lag" else run % N
        c[t] = (p[t - start] + sign * key) % N
        run += int(PRIMES[c[t]])
    return c


VARIANTS = [(kind, lag, sign) for kind, lags in (("prime of rune t-lag", (1, 2, 3)), ("running sum of primes before t", (1,)))
            for lag in lags for sign in (1, -1)]


MIN_SECTION = 300            # IC on a short section means nothing (section 15 has 9 runes and reads 2-3 by chance)


def prime_keyed(secs: dict, ids, shuffles: int = 50, seed: int = SEED) -> dict:
    """Best IC over the sections of MIN_SECTION+ runes, against the same decryption of each section shuffled."""
    ids = [i for i in ids if len(secs[i]["ct"]) >= MIN_SECTION]
    rng = np.random.default_rng(seed)
    rows = []
    for kind, lag, sign in VARIANTS:
        ics = {str(i): ic29(decrypt_self_keyed(secs[i]["ct"], kind, lag, sign)) for i in ids}
        null = [max(ic29(decrypt_self_keyed(rng.permutation(secs[i]["ct"]), kind, lag, sign)) for i in ids) for _ in range(shuffles)]
        best = max(ics.values())
        rows.append({"variant": f"p = c {'-' if sign > 0 else '+'} key, key = {kind.replace('t-lag', f't-{lag}')}", "best_ic": best,
                     "null_mean": float(np.mean(null)), "null_max": float(max(null)), "flag": bool(best >= 1.25 and best > max(null)),
                     "per_section": ics})
    return {"sections": [str(i) for i in ids], "rows": rows}


def prime_keyed_signature(alpha, reps: int = 4, length: int = 5000) -> list[dict]:
    """English through each variant (the encryption direction): do any reproduce the repeat signature?"""
    from lpswarm import research_signature as S
    from lpswarm.research_packets import load_sections
    from lpswarm.textgen.synth import encoded_text
    text = encoded_text(alpha, "english", "train").astype(np.int64)
    ref = S.reference(load_sections(indexes=list(S.SECTIONS)))
    rng = np.random.default_rng(SEED)
    out = []
    for kind, lag, sign in VARIANTS:
        units = {}
        for i in range(reps):
            s = int(rng.integers(0, len(text) - length))
            units[str(i)] = encrypt_self_keyed(text[s:s + length], kind, lag, sign, seed=i)
        pr = S.profile(units)
        c = S.classify(pr["ratio"], ref, None, None, pr["uni_ic"], pr["diff_ic"])
        out.append({"variant": f"{kind.replace('t-lag', f't-{lag}')}, sign {'+' if sign > 0 else '-'}", "lag1": float(pr["ratio"][0]),
                    "rest": [float(pr["ratio"][1:].min()), float(pr["ratio"][1:].max())], "uni_ic": float(pr["uni_ic"]),
                    "diff_ic": float(pr["diff_ic"]), "full": bool(c["full"])})
    return out


# -------------------------------------------------------------------------------------------------- jumps
def jump_walk(runes: np.ndarray, start: int, direction: int = 1, length: int | None = None) -> np.ndarray:
    """Visit positions start, start + d*prime(rune), ... (wrapping), stopping before a position repeats or after `length` steps."""
    n = len(runes)
    seen, out, pos = set(), [], start
    for _ in range(length or n):
        if pos in seen:
            break
        seen.add(pos)
        out.append(int(runes[pos]))
        pos = (pos + direction * int(PRIMES[runes[pos]])) % n
    return np.array(out, dtype=np.int64)


def bigram_score(x: np.ndarray, big: np.ndarray) -> float:
    return float(big[x[:-1], x[1:]].mean()) if len(x) > 1 else -99.0


def jumps(t: dict, big: np.ndarray, pages, shuffles: int = 50, min_len: int = 30, seed: int = SEED) -> list[dict]:
    rng = np.random.default_rng(seed)
    out = []
    for pg in pages:
        r = t["rune"][t["page"] == pg]
        if len(r) < min_len:
            continue
        best = None
        for d in (1, -1):
            for s in range(len(r)):
                w = jump_walk(r, s, d)
                if len(w) >= min_len:
                    sc = bigram_score(w, big)
                    if best is None or sc > best[0]:
                        best = (sc, s, d, len(w))
        if best is None:
            continue
        null = []
        for _ in range(shuffles):
            q = rng.permutation(r)
            nb = max((bigram_score(w, big) for d in (1, -1) for s in range(len(q)) for w in [jump_walk(q, s, d)] if len(w) >= min_len), default=-99.0)
            null.append(nb)
        null = np.array(null)
        out.append({"page": int(pg), "runes": int(len(r)), "best": best[0], "start": best[1], "direction": best[2], "walk_length": best[3],
                    "null_mean": float(null.mean()), "null_max": float(null.max()), "p": (1 + int((null >= best[0]).sum())) / (len(null) + 1)})
    return out


# -------------------------------------------------------------------------------------------------- grids
def grid_sums(runes: np.ndarray) -> dict:
    n = int(round(len(runes) ** 0.5))
    g = PRIMES[np.asarray(runes)].reshape(n, n)
    sums = {"rows": g.sum(1).tolist(), "columns": g.sum(0).tolist(), "diagonals": [int(np.trace(g)), int(np.trace(g[::-1]))], "total": int(g.sum())}
    hits = []
    for name in ("rows", "columns", "diagonals"):
        for i, v in enumerate(sums[name]):
            if v in HINT_NUMBERS:
                hits.append(f"{name[:-1]} {i + 1} = {v}")
    for size in range(3, n + 1):
        for i in range(n - size + 1):
            for j in range(n - size + 1):
                s = g[i:i + size, j:j + size]
                circ = int(s.sum() - (s[1:-1, 1:-1].sum() if size > 2 else 0))
                if circ in HINT_NUMBERS:
                    hits.append(f"{size}x{size} at row {i + 1} col {j + 1}: circumference {circ}")
                if int(s.sum()) in HINT_NUMBERS:
                    hits.append(f"{size}x{size} at row {i + 1} col {j + 1}: sum {int(s.sum())}")
    return {"side": n, **sums, "hint_number_hits": hits}


def grid_null(runes: np.ndarray, reps: int = 300, seed: int = SEED) -> float:
    """Mean number of hint-number hits in grids of the same runes shuffled (how many hits chance gives)."""
    rng = np.random.default_rng(seed)
    return float(np.mean([len(grid_sums(rng.permutation(runes))["hint_number_hits"]) for _ in range(reps)]))


# ------------------------------------------------------------------------------------------------- report
def main(argv: list[str] | None = None) -> int:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.lp_table import load_table
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.research_packets import ALPHABET, load_sections
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_literal", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="reports/diag")
    ap.add_argument("--table", default="data/lp_derived/lp2_runes.csv")
    ap.add_argument("--shuffles", type=int, default=50)
    args = ap.parse_args(argv)
    alpha = get_alphabet(ALPHABET)
    ids = list(range(10, 26))
    secs = {i: s for i, s in load_sections(indexes=ids).items() if len(s["ct"]) > 1}
    t = load_table(args.table)
    big = FullOracle(alpha, OracleConfig(null_samples=300)).bigram_table()
    pages = sorted(set(t["page"].tolist()))
    sq = [p for p in pages if int(round((t["page"] == p).sum() ** 0.5)) ** 2 == (t["page"] == p).sum()]
    rep = {"prime_keyed": prime_keyed(secs, sorted(secs)), "prime_keyed_signature": prime_keyed_signature(alpha),
           "jumps": jumps(t, big, pages, args.shuffles),
           "grids": {str(p): {**grid_sums(t["rune"][t["page"] == p]), "null_mean_hits": grid_null(t["rune"][t["page"] == p])} for p in sq}}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "literal.json").write_text(json.dumps(rep, indent=1, default=str) + "\n", encoding="utf-8")
    L = ["# Literal readings of \"their numbers are the direction\"", "", "**EXPLORATORY; no oracle, no models.**", "",
         "## 1. The prime value of a rune as the key for the next (self-keyed)", "",
         f"Sections of {MIN_SECTION}+ runes ({', '.join(rep['prime_keyed']['sections'])}); null: the same decryption of each section shuffled (50 times). "
         "Flag: IC x 29 >= 1.25 and above the null maximum.", "",
         "| variant | best IC x 29 | null mean / max | flag |", "| --- | ---: | --- | --- |"]
    for r in rep["prime_keyed"]["rows"]:
        L.append(f"| {r['variant']} | {r['best_ic']:.3f} | {r['null_mean']:.3f} / {r['null_max']:.3f} | {'**FLAG**' if r['flag'] else 'no'} |")
    L += ["", "English enciphered the same way, against the repeat signature (real: lag 1 0.19, lags 2-8 at chance, ICs 1.00 / 1.03):", "",
          "| variant | lag 1 | lags 2-8 | unigram IC | difference IC | full match |", "| --- | ---: | --- | ---: | ---: | --- |"]
    for r in rep["prime_keyed_signature"]:
        L.append(f"| {r['variant']} | {r['lag1']:.2f} | {r['rest'][0]:.2f}-{r['rest'][1]:.2f} | {r['uni_ic']:.2f} | {r['diff_ic']:.2f} | {'yes' if r['full'] else 'no'} |")
    L += ["", "## 2. Prime values as steps through a page (best walk of 30+ runes, English bigram score)", "",
          f"Null: the same search on the page's runes shuffled ({args.shuffles} times). p = share of shuffles whose best walk scores at least as well. A walk "
          "stops when it would revisit a position, so short pages often have no walk of 30 runes (score -99 in a shuffle, which lowers the null mean).", "",
          "| page | runes | best score | null mean / max | p |", "| ---: | ---: | ---: | --- | ---: |"]
    for r in rep["jumps"]:
        L.append(f"| {r['page']} | {r['runes']} | {r['best']:.3f} | {r['null_mean']:.3f} / {r['null_max']:.3f} | {r['p']:.3f} |")
    ps = [r["p"] for r in rep["jumps"]]
    L += ["", f"{sum(p <= 0.05 for p in ps)} of {len(ps)} pages at p <= 0.05 (about {0.05 * len(ps):.1f} expected by chance); smallest p {min(ps):.3f}."]
    L += ["", "## 3. Square pages as grids, against the hint numbers " + ", ".join(map(str, HINT_NUMBERS)), ""]
    for p, g in rep["grids"].items():
        L += [f"Page {p} ({g['side']} x {g['side']}): rows {g['rows']}; columns {g['columns']}; diagonals {g['diagonals']}; total {g['total']}.",
              f"Hits: {len(g['hint_number_hits'])} ({'; '.join(g['hint_number_hits'][:12]) or 'none'}); the same runes shuffled give {g['null_mean_hits']:.1f} on average.", ""]
    text = "\n".join(L) + "\n"
    (out / "literal.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

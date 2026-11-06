"""Running sums with a multiplicatively keyed step: c[t] = c[t-1] + a[t] * n[t] (mod 29).

    python -m lpswarm.research_muldiff --out reports/diag

Why this family: a step that is a keyed multiple of the plaintext rune number has flat first differences whatever the plaintext is, because
a[t] uniform on the non-zero residues hides n[t]; and a zero step happens only where n[t] is zero. With 1-based rune numbers the 29th rune
(EA) is zero mod 29, and its English frequency (0.0065) is almost exactly the real double rate (0.0066), so this family can reproduce the
four numbers of the repeat signature (the screen below confirms it). The position test in `main` then rejects EA as the trigger: the doubles'
second runes sit at word starts and ends as often as any rune does (24% / 21%), EA is 7% / 4% in English words.

The attack that does not depend on which rune is zero: u[t] = a[t]^-1 * (c[t] - c[t-1]) is the plaintext number n[t] up to a relabelling, and
the index of coincidence (IC) does not change under a relabelling, so the sweep scores IC x 29 of u for a[t] = sequence(t + offset) mod 29 (and
of a[t] * (c[t] - c[t-1]) for the inverse-keyed form), for the position-keyed sequences of the cipher language. No oracle, no models; exploratory.
Blind spot as in `research_views`: an F-skip (key not advancing at F) or a stream out of step breaks the alignment over the window.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

N = 29
SEED = 20261106
OFFSETS = 3000
WINDOW = 600
SEQUENCES = ("primes", "prime_totients", "fibonacci", "naturals", "squares", "triangular", "pi_digits", "e_digits")
FLAG_IC = 1.25
NULL_REPS = 3
INV = np.array([0] + [pow(a, -1, N) for a in range(1, N)], dtype=np.int64)


def ic29(rows: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """IC x 29 of each row of symbols, using only the entries where `valid`."""
    counts = np.zeros((rows.shape[0], N), dtype=np.int64)
    for v in range(N):
        counts[:, v] = ((rows == v) & valid).sum(axis=1)
    n = counts.sum(axis=1).astype(float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(n > 1, N * (counts * (counts - 1)).sum(axis=1) / np.maximum(n * (n - 1), 1), 0.0)


def sweep(delta: np.ndarray, seq: np.ndarray, offsets: int = OFFSETS) -> dict:
    """Best IC x 29 of a^-1 * delta and a * delta over the offsets of one sequence (seq is the sequence mod 29)."""
    L = len(delta)
    idx = np.arange(offsets)[:, None] + np.arange(L)[None, :]
    a = seq[idx]
    valid = a != 0
    out = {}
    for name, key in (("a^-1 * step", INV[a]), ("a * step", a)):
        u = (key * delta[None, :]) % N
        ic = ic29(u, valid)
        k = int(ic.argmax())
        out[name] = {"best_ic": float(ic[k]), "offset": k}
    return out


def run_section(ct: np.ndarray, seqs: dict, offsets: int = OFFSETS, window: int = WINDOW) -> dict:
    x = np.asarray(ct[:window + 1], dtype=np.int64)
    delta = (x[1:] - x[:-1]) % N
    best = {"best_ic": 0.0}
    for name, s in seqs.items():
        for form, r in sweep(delta, s, offsets).items():
            if r["best_ic"] > best["best_ic"]:
                best = {**r, "sequence": name, "form": form}
    return best


def sequences(length: int) -> dict:
    from lpswarm.programs.sequences import window
    return {name: np.asarray(window(name, 0, length, N), dtype=np.int64) for name in SEQUENCES}


def encipher_muldiff(plain: np.ndarray, key: np.ndarray, zero_rune: int = 28) -> np.ndarray:
    """c[t] = c[t-1] + key[t] * ((plain[t] - zero_rune + N) % N)  (zero_rune 28: 1-based numbers, the 29th rune is zero)."""
    n = (np.asarray(plain, dtype=np.int64) + 1 - (zero_rune + 1)) % N if zero_rune != 28 else (np.asarray(plain, dtype=np.int64) + 1) % N
    steps = (np.asarray(key, dtype=np.int64) * n) % N
    return np.cumsum(steps) % N


def word_position_test(table_path: str, alpha, reps: int = 20000, seed: int = SEED) -> dict:
    """Do the second runes of the doubles sit in words where EA sits in English words, or where any rune sits?"""
    from collections import Counter
    from lpswarm.lp_table import load_table
    from lpswarm.textgen.synth import encoded_breaks, encoded_text
    eng = encoded_text(alpha, "english", "train").astype(int)
    starts = np.zeros(len(eng) + 2, bool)
    starts[[int(s) for s in encoded_breaks(alpha, "english", "train") if s <= len(eng)]] = True
    starts[len(eng)] = True

    def cats(is_start, n):
        out = []
        for j in range(n):
            a, b = is_start[j], is_start[j + 1]
            out.append("single" if (a and b) else "initial" if a else "final" if b else "internal")
        return np.array(out)

    ec = cats(starts, len(eng))
    ea = Counter(ec[eng == N - 1])
    t = load_table(table_path)
    c, page = t["rune"], t["page"]
    boundary = (t["sep"] != "none") | np.r_[page[:-1] != page[1:], True]
    istart = np.r_[np.r_[True, boundary[:-1]], True]
    rc = cats(istart, len(c))
    d2 = np.nonzero(c[:-1] == c[1:])[0] + 1
    obs, allc = Counter(rc[d2]), Counter(rc)
    names = ["initial", "internal", "final", "single"]
    o = np.array([obs.get(k, 0) for k in names])
    rng = np.random.default_rng(seed)
    res = {"doubles": int(o.sum()), "observed": dict(zip(names, o.tolist()))}
    for label, ctr in (("EA in English words", ea), ("all runes of the real text", allc)):
        p = np.array([ctr.get(k, 0) for k in names], float)
        p /= p.sum()
        e = o.sum() * p
        use = e > 0
        stat = float(((o - e)[use] ** 2 / e[use]).sum())
        null = rng.multinomial(o.sum(), p, size=reps)
        nstat = (((null - e) ** 2 / np.where(use, e, 1)) * use).sum(axis=1)
        res[label] = {"proportions": dict(zip(names, np.round(p, 3).tolist())), "chi_square": stat, "p": (1 + int((nstat >= stat).sum())) / (reps + 1)}
    return res


def screen_family(alpha, reps: int = 6, length: int = 5000, seed: int = SEED) -> dict:
    """Run English through the family with a uniform non-zero key and measure the four numbers of the repeat signature."""
    from lpswarm import research_signature as S
    from lpswarm.research_packets import load_sections
    from lpswarm.textgen.synth import encoded_text
    text = encoded_text(alpha, "english", "train").astype(np.int64)
    rng = np.random.default_rng(seed)
    secs = load_sections(indexes=list(S.SECTIONS))
    ref = S.reference(secs)
    out = {}
    for zero in (28, 0, 9):
        units = {}
        for i in range(reps):
            s = int(rng.integers(0, len(text) - length))
            key = rng.integers(1, N, size=length)
            units[str(i)] = encipher_muldiff(text[s:s + length], key, zero)
        pr = S.profile(units)
        c = S.classify(pr["ratio"], ref, None, None, pr["uni_ic"], pr["diff_ic"])
        out[zero] = {"lag1": float(pr["ratio"][0]), "rest": [float(pr["ratio"][1:].min()), float(pr["ratio"][1:].max())],
                     "uni_ic": float(pr["uni_ic"]), "diff_ic": float(pr["diff_ic"]), "full": bool(c["full"])}
    return out


def main(argv: list[str] | None = None) -> int:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET, load_sections
    from lpswarm.research_structure import UNSOLVED
    from lpswarm.textgen.synth import encoded_text
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_muldiff", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="reports/diag")
    ap.add_argument("--table", default="data/lp_derived/lp2_runes.csv")
    ap.add_argument("--offsets", type=int, default=OFFSETS)
    args = ap.parse_args(argv)
    alpha = get_alphabet(ALPHABET)
    seqs = sequences(args.offsets + 3005)
    secs = load_sections(indexes=sorted(UNSOLVED))
    rng = np.random.default_rng(SEED)
    rep = {"family_screen": screen_family(alpha), "word_position": word_position_test(args.table, alpha), "sections": {}, "controls": {}}
    nulls = []
    for i in UNSOLVED:
        ct = secs[i]["ct"]
        r = run_section(ct, seqs, args.offsets)
        shuf = [run_section(rng.permutation(ct), seqs, args.offsets)["best_ic"] for _ in range(NULL_REPS)]
        r["null_max"] = float(max(shuf))
        r["flag"] = bool(r["best_ic"] >= FLAG_IC and r["best_ic"] > r["null_max"])
        rep["sections"][str(i)] = r
        nulls += shuf
    text = encoded_text(alpha, "english", "train").astype(np.int64)
    for label, name, off in (("English through primes x n, offset 777", "primes", 777), ("English through Fibonacci x n, offset 123", "fibonacci", 123)):
        key = seqs[name][off:off + 3000]
        key = np.where(key == 0, 1, key)                             # a zero key would zero the step; planted control keeps it non-zero
        pt = text[40000:40000 + 3000]
        ct = encipher_muldiff(pt, key, 28)
        r = run_section(ct, seqs, args.offsets)
        # the first difference at index j uses key[j + 1], so the planted offset shows up as offset + 1 (or an equivalent one, for periodic sequences)
        rep["controls"][label] = {**r, "found": bool(r.get("sequence") == name and r["best_ic"] >= FLAG_IC)}
    rng2 = np.random.default_rng(1)
    r = run_section(rng2.integers(0, N, size=3000), seqs, args.offsets)
    rep["controls"]["iid noise"] = r
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "muldiff.json").write_text(json.dumps(rep, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    L = ["# Running sums with a multiplicatively keyed step", "", "**EXPLORATORY; no oracle, no models.** See the module docstring for the reasoning.", "",
         "## Can the family reproduce the repeat signature? (English plaintext, uniform non-zero key, 6 windows of 5000)", "",
         "| zero rune (the one whose step is zero) | lag 1 | lags 2-8 | unigram IC | first-difference IC | full match |", "| --- | ---: | --- | ---: | ---: | --- |"]
    for z, v in rep["family_screen"].items():
        L.append(f"| {alpha.tokens[int(z)]} | {v['lag1']:.2f} | {v['rest'][0]:.2f}-{v['rest'][1]:.2f} | {v['uni_ic']:.2f} | {v['diff_ic']:.2f} | {'yes' if v['full'] else 'no'} |")
    wp = rep["word_position"]
    L += ["", "## Is the zero step triggered by plaintext EA? (position of the doubles' second runes in words)", "",
          f"{wp['doubles']} doubles; second rune word-initial / internal / final / single: {wp['observed']}.", "", "| compared with | proportions | chi-square | p |", "| --- | --- | ---: | ---: |"]
    for k in ("EA in English words", "all runes of the real text"):
        L.append(f"| {k} | {wp[k]['proportions']} | {wp[k]['chi_square']:.1f} | {wp[k]['p']:.4f} |")
    L += ["", f"## IC sweep: a[t]^-1 or a[t] times the first difference, {len(SEQUENCES)} sequences x {args.offsets} offsets, first {WINDOW} runes", "",
          f"Flag: IC x 29 >= {FLAG_IC} and above the maximum of {NULL_REPS} shuffled copies of the section. Language gives about 1.6-2.0; noise about 1.1.", "",
          "| section | best IC | null max | best sequence / form / offset | flag |", "| ---: | ---: | ---: | --- | --- |"]
    for s, r in rep["sections"].items():
        L.append(f"| {s} | {r['best_ic']:.3f} | {r['null_max']:.3f} | {r['sequence']} / {r['form']} / {r['offset']} | {'**FLAG**' if r['flag'] else 'no'} |")
    L += ["", "Controls (3000 runes):", "", "| case | best IC | best sequence / offset | found |", "| --- | ---: | --- | --- |"]
    for k, r in rep["controls"].items():
        L.append(f"| {k} | {r['best_ic']:.3f} | {r.get('sequence')} / {r.get('offset')} | {r.get('found', '')} |")
    text_out = "\n".join(L) + "\n"
    (out / "muldiff.md").write_text(text_out, encoding="utf-8")
    print(text_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

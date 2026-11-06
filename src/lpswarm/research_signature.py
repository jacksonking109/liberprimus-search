"""Which mechanisms in the cipher DSL can reproduce the repeat signature of the unsolved sections?

    python -m lpswarm.research_signature --out reports/diag

The signature (measured on the manifest text, see `research_doubles`): adjacent identical runes occur at about 0.20 of
the shuffle expectation (lag 1), while lags 2-8 sit at chance. This puts English plaintext through every cipher in the
packet families (and the other position-keyed sequences of the DSL) with `programs.spec.encrypt`, measures the same
lag profile on the result, and reports which families can produce it. No oracle, no models, no ledger; fixed seeds.

A match is pre-specified, not tuned on the results: lag-1 ratio inside the 95% interval of the real ratio, and every
lag from 2 to 8 inside FLAT (0.85-1.15). A first pass used only those lag conditions; it let a feedback cipher through
whose first differences are the plaintext itself, which the real first differences (flat: IC x 29 = 1.03, language 1.7-2.0)
contradict. The unigram and first-difference IC conditions (both <= IC_MAX) were therefore added after that pass, from
statistics `research_structure` had already reported; the report shows both the lag-only and the full match.
Compatibility with the signature is a necessary condition for a mechanism, not evidence for it, and it is only as good
as the synthetic plaintext (English, training split).
"""
from __future__ import annotations

import argparse
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

from lpswarm.research_doubles import expected, observed

N = 29
SEED = 20261105
LAGS = 8
WINDOWS = 6
WINDOW_LEN = 5000
REFINE_WINDOWS = 60
REFINE_TOP = 40
FLAT = (0.85, 1.15)
IC_MAX = 1.15                      # unigram and first-difference IC x 29: real text 1.0x, language 1.6-2.0
SECTIONS = tuple(range(10, 26))
EXTRA_SEQUENCES = ("primes", "prime_totients", "fibonacci", "pi_digits", "e_digits")
EXTRA_OFFSETS = (0, 7, 1000)
LABEL = "SYNTHETIC: English plaintext (training split) through the DSL's ciphers; compatibility is necessary, not evidence"


# ------------------------------------------------------------------------------------------ statistics
def poisson_ci(k: int, level: float = 0.95) -> tuple[float, float]:
    """Exact (Garwood) interval for a Poisson mean given a count k."""
    a = (1 - level) / 2

    def cdf(x, lam):                                    # P(X <= x)
        if x < 0:
            return 0.0
        term, s = math.exp(-lam), 0.0
        for i in range(x + 1):
            if i:
                term *= lam / i
            s += term
        return min(s, 1.0)

    def solve(f, lo, hi):
        for _ in range(100):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) else (lo, mid)
        return (lo + hi) / 2

    hi_cap = k + 10 * math.sqrt(k + 1) + 20
    lower = 0.0 if k == 0 else solve(lambda lam: 1 - cdf(k - 1, lam) < a, 0.0, float(k))
    upper = solve(lambda lam: cdf(k, lam) > a, float(k), hi_cap)
    return lower, upper


def _ic29(arrays) -> float:
    """Unbiased index of coincidence x 29, pooled over arrays (1.0 for uniform symbols, 1.6-2.0 for language)."""
    num = den = 0.0
    for x in arrays:
        c = np.bincount(np.asarray(x, dtype=np.int64), minlength=N).astype(float)
        num += float((c * (c - 1)).sum())
        den += len(x) * (len(x) - 1)
    return N * num / den if den else float("nan")


def profile(units: dict) -> dict:
    """Lag-1..8 equal-pair counts against the exact shuffle expectation (the research_doubles definitions), plus the
    unigram IC and the IC of the first differences c[i] - c[i-1] (mod 29), each within a unit."""
    e, o = expected(units, LAGS), observed(units, LAGS)
    arrays = [np.asarray(x, dtype=np.int64) for x in units.values()]
    return {"equal": o["lag"].astype(int), "expected": e["lag"], "ratio": o["lag"] / np.maximum(e["lag"], 1e-9),
            "uni_ic": _ic29(arrays), "diff_ic": _ic29([(x[1:] - x[:-1]) % N for x in arrays])}


def reference(secs: dict, ids=SECTIONS) -> dict:
    units = {str(i): np.asarray(secs[i]["ct"], dtype=np.int64) for i in ids if i in secs}
    p = profile(units)
    d, e = int(p["equal"][0]), float(p["expected"][0])
    lo, hi = poisson_ci(d)
    return {"doubles": d, "expected": e, "ratio": d / e, "ci": [lo / e, hi / e], "lags": [float(x) for x in p["ratio"]],
            "uni_ic": p["uni_ic"], "diff_ic": p["diff_ic"]}


def classify(ratio: np.ndarray, ref: dict, plain_r1: float | None = None, loose_band=None,
             uni_ic: float | None = None, diff_ic: float | None = None) -> dict:
    """`match` (lag conditions only) and `full` (also both ICs <= IC_MAX) are pre-specified bands. `loose` is a post-hoc
    sensitivity check for the plaintext level: the factor by which the cipher lowers the plaintext's own lag-1 ratio must
    fall in `loose_band` (see `main`), with the same flat-lag and IC conditions."""
    r1, rest = float(ratio[0]), [float(x) for x in ratio[1:]]
    in_ci = ref["ci"][0] <= r1 <= ref["ci"][1]
    flat = all(FLAT[0] <= x <= FLAT[1] for x in rest)
    ic_ok = uni_ic is not None and diff_ic is not None and uni_ic <= IC_MAX and diff_ic <= IC_MAX
    out = {"r1": r1, "rest_min": min(rest), "rest_max": max(rest), "in_ci": bool(in_ci), "flat": bool(flat),
           "match": bool(in_ci and flat), "uni_ic": uni_ic, "diff_ic": diff_ic, "ic_ok": bool(ic_ok),
           "full": bool(in_ci and flat and ic_ok)}
    if plain_r1 and loose_band:
        factor = r1 / plain_r1
        out["factor"] = factor
        out["loose"] = bool(loose_band[0] <= factor <= loose_band[1] and flat and ic_ok)
    return out


# ------------------------------------------------------------------------------------------- plaintext
def english_windows(alpha, n_windows: int = WINDOWS, length: int = WINDOW_LEN, seed: int = SEED, split: str = "train"):
    """Non-overlapping windows of English (one random start per stretch) with their true word starts."""
    from lpswarm.textgen.synth import encoded_text, window_breaks
    text = encoded_text(alpha, "english", split)
    stretch = (len(text) - length) // n_windows
    rng = np.random.default_rng(seed)
    out = []
    for w in range(n_windows):
        s = w * stretch + int(rng.integers(0, stretch))
        out.append((text[s:s + length].astype(np.int64), tuple(window_breaks(alpha, "english", split, s, length))))
    return out


def thinned_walk(length: int, rng: np.random.Generator, keep_zero: float = 0.2) -> np.ndarray:
    """Positive control, not a DSL cipher: a random walk c[i] = c[i-1] + d with d uniform on 0..28, where a zero step is
    kept only with probability `keep_zero` (otherwise redrawn uniformly from 1..28). Its symbols and non-zero differences
    are uniform and the only short lag is 1, so it has the real text's signature by construction."""
    steps = rng.integers(0, N, size=length)
    drop = (steps == 0) & (rng.random(length) > keep_zero)
    steps[drop] = rng.integers(1, N, size=int(drop.sum()))
    return np.cumsum(steps) % N


# ------------------------------------------------------------------------------------------ candidates
def _spec_label(spec: dict, alpha) -> str:
    from lpswarm.programs.spec import describe
    try:
        return describe(spec, alpha)
    except Exception:                                   # a label must never stop the screen
        return json.dumps(spec, sort_keys=True)[:120]


def packet_candidates(alpha, wordkey_limit: int = 5000):
    """(family, label, concrete spec) for every cipher in the four packet families, as the packets expand them."""
    from lpswarm.programs.spec import compile_spec, expand
    from lpswarm.research_packets import exp1_replies, exp2_replies, exp3_replies, exp4_replies
    families = {"exp1 feedback (neighbour/chain, 8 forms x b)": exp1_replies()[0],
                "exp2b two-shear Hill blocks, all shifts": exp2_replies(True)[0],
                "exp3 progressive keys": exp3_replies()[0],
                "exp4 word keys under the reversed alphabet": exp4_replies(wordkey_limit)[0]}
    for fam, replies in families.items():
        for reply in replies:
            for prop in json.loads(reply)["proposals"]:
                for spec in expand(compile_spec(prop["spec"], alpha), None):
                    yield fam, _spec_label(spec, alpha), spec


def sequence_candidates(alpha):
    """The other position-keyed sequences of the DSL: scale 1..28, two combine forms, a few start offsets."""
    from lpswarm.programs.spec import compile_spec
    for seq in EXTRA_SEQUENCES:
        for combine in ("sub", "beaufort"):
            for scale in range(1, N):
                for off in EXTRA_OFFSETS:
                    spec = compile_spec({"stream": {"kind": "sequence", "name": seq, "scale": scale, "offset": off,
                                                    "add": 0}, "combine": combine}, alpha)
                    yield "other position-keyed sequences", _spec_label(spec, alpha), spec


WIDE_LAGS = (1, 2, 3, 4, 8, 16)
FEEDBACK_FAMILY = "wider feedback mixers (kind x op x lag x dir x times x reset x position x shift)"
HILL_FAMILY = "random Hill blocks, sizes 2-4 (sample, no shift)"
PERM_FAMILY = "block permutations, sizes 2-5 (all, no shift)"


def mixer_candidates(alpha, lags=WIDE_LAGS, hill_samples: int = 2000, seed: int = SEED):
    """The invertible mixers of the DSL beyond what the packets use: neighbour and chain feedback with every op that has
    an inverse, longer lags, both directions, repeated stages, word resets and a stage before or after the shift; random
    Hill matrices of size 2-4; every block permutation of size 2-5. (window, mul and div mixers have no inverse.)"""
    from lpswarm.programs.mixers import invertible
    from lpswarm.programs.spec import compile_spec

    def spec(mix, b):
        return compile_spec({"stream": {"kind": "constant", "value": b}, "combine": "sub", "mix": mix}, alpha)

    for kind in ("neighbor", "chain"):
        for op in ("add", "sub", "rsub"):
            for lag in lags:
                for d in ("prev", "next"):
                    for times in (1, 2, 3):
                        for reset in ("none", "word"):
                            for at in ("before", "after"):
                                mix = {"kind": kind, "op": op, "lag": lag, "dir": d, "times": times, "reset": reset, "at": at}
                                for b in range(N):
                                    yield FEEDBACK_FAMILY, _spec_label(spec(mix, b), alpha), spec(mix, b)
    rng = np.random.default_rng(seed)
    for g in (2, 3, 4):
        made = 0
        while made < hill_samples:
            flat = [int(v) for v in rng.integers(0, N, size=g * g)]
            if invertible(flat, g, N):
                mix = {"kind": "hill", "size": g, "matrix": flat, "at": "before"}
                yield HILL_FAMILY, _spec_label(spec(mix, 0), alpha), spec(mix, 0)
                made += 1
    import itertools
    for g in (2, 3, 4, 5):
        for perm in itertools.permutations(range(g)):
            mix = {"kind": "block_perm", "size": g, "perm": list(perm), "at": "before"}
            yield PERM_FAMILY, _spec_label(spec(mix, 0), alpha), spec(mix, 0)


def control_candidates(alpha):
    from lpswarm.programs.spec import compile_spec
    yield "control: no cipher", "identity", compile_spec({"stream": {"kind": "constant", "value": 0}, "combine": "sub"}, alpha)
    yield "control: no cipher", "constant shift 5", compile_spec({"stream": {"kind": "constant", "value": 5},
                                                                  "combine": "sub"}, alpha)
    yield "control: no cipher", "reversed alphabet alone", compile_spec(
        {"stream": {"kind": "constant", "value": 0}, "combine": "sub", "map": "reverse"}, alpha)


# ------------------------------------------------------------------------------------------- screening
_WINDOWS: list = []


def _init(windows):
    global _WINDOWS
    _WINDOWS = windows


def screen_spec(spec: dict, windows=None, n: int = N) -> np.ndarray:
    """Lag-1..8 ratios of the ciphertext obtained by enciphering every plaintext window with `spec`."""
    return screen_full(spec, windows, n)["ratio"]


def screen_full(spec: dict, windows=None, n: int = N) -> dict:
    """`profile` of the ciphertext obtained by enciphering every plaintext window with `spec`."""
    from lpswarm.programs.spec import encrypt
    windows = _WINDOWS if windows is None else windows
    units = {str(w): np.asarray(encrypt(pt, spec, n, breaks=list(br) or None), dtype=np.int64)
             for w, (pt, br) in enumerate(windows)}
    return profile(units)


def _work(item):
    fam, label, spec = item
    try:
        pr = screen_full(spec)
        return fam, label, {"ratio": pr["ratio"].tolist(), "uni_ic": pr["uni_ic"], "diff_ic": pr["diff_ic"]}, None
    except Exception as exc:                            # a spec the encryption direction cannot handle
        return fam, label, None, f"{type(exc).__name__}: {exc}"[:120]


def screen_all(candidates: list, windows: list, workers: int = 4) -> list:
    if workers <= 1:
        _init(windows)
        return [_work(c) for c in candidates]
    with ProcessPoolExecutor(max_workers=workers, initializer=_init, initargs=(windows,)) as ex:
        return list(ex.map(_work, candidates, chunksize=64))


def summarise(results: list, ref: dict, plain_r1: float | None = None, loose_band=None) -> dict:
    fams: dict = {}
    for fam, label, pr, err in results:
        f = fams.setdefault(fam, {"candidates": 0, "errors": 0, "r1": [], "short": 0, "in_ci": 0, "flat": 0, "match": 0, "ic_ok": 0, "full": 0, "loose": 0,
                                  "matches": [], "closest": [], "first_error": None})
        f["candidates"] += 1
        if err:
            f["errors"] += 1
            f["first_error"] = f["first_error"] or err
            continue
        ratio = pr["ratio"]
        c = classify(np.asarray(ratio), ref, plain_r1, loose_band, pr["uni_ic"], pr["diff_ic"])
        f["r1"].append(c["r1"])
        f["loose"] += c.get("loose", False)
        f["ic_ok"] += c["ic_ok"]
        f["full"] += c["full"]
        f["in_ci"] += c["in_ci"]
        f["flat"] += c["flat"]
        f["match"] += c["match"]
        f["short"] += c["r1"] <= 0.35
        row = {"label": label, **c, "ratio": ratio}
        if c["match"] or c.get("loose"):
            f["matches"].append(row)
        if c["flat"] and c["ic_ok"]:
            f["closest"].append(row)
    for f in fams.values():
        r1 = np.asarray(f.pop("r1")) if f["r1"] else np.array([np.nan])
        f["r1_min"], f["r1_median"], f["r1_max"] = float(np.min(r1)), float(np.median(r1)), float(np.max(r1))
        f["closest"] = sorted(f["closest"], key=lambda r: abs(math.log(max(r["r1"], 1e-6) / ref["ratio"])))[:REFINE_TOP]
    return fams


def refine(fams: dict, ref: dict, alpha, cands: list, seed: int, workers: int, plain_r1=None, loose_band=None) -> list:
    """Re-screen the matches and the closest lag-flat candidates on many more windows."""
    by_label: dict = {}
    for fam, f in fams.items():
        for row in (f["matches"] + f["closest"])[:REFINE_TOP]:
            by_label[(fam, row["label"])] = row
    if not by_label:
        return []
    windows = english_windows(alpha, REFINE_WINDOWS, WINDOW_LEN, seed + 1)
    wanted = set(by_label)
    items = [c for c in cands if (c[0], c[1]) in wanted]
    out = []
    for fam, label, pr, err in screen_all(items, windows, workers):
        if err:
            continue
        out.append({"family": fam, "label": label,
                    **classify(np.asarray(pr["ratio"]), ref, plain_r1, loose_band, pr["uni_ic"], pr["diff_ic"]),
                    "ratio": pr["ratio"]})
    return sorted(out, key=lambda r: (not r["full"], not r["match"], not r.get("loose", False),
                                      abs(math.log(max(r["r1"], 1e-6) / ref["ratio"]))))


_WORDKEYS = 5000
_WIDE = True


def _all_candidates(alpha):
    yield from control_candidates(alpha)
    yield from packet_candidates(alpha, _WORDKEYS)
    yield from sequence_candidates(alpha)
    if _WIDE:
        yield from mixer_candidates(alpha)


# ------------------------------------------------------------------------------------------- rendering
def _pct(x) -> str:
    return f"{x:.2f}"


def markdown(rep: dict) -> str:
    ref, ctl = rep["reference"], rep["controls"]
    L = ["# Which cipher families can reproduce the repeat signature?", "", f"**{LABEL}.**", "",
         "A match is pre-specified: lag-1 ratio inside the 95% interval of the real ratio, and every lag from 2 to 8 inside "
         f"{FLAT[0]}-{FLAT[1]}. Ratios are equal-neighbour counts over the exact shuffle expectation of the same ciphertext.", "",
         f"Real signature (manifest sections 10-25): lag 1 {ref['doubles']} doubles against {ref['expected']:.0f} expected, "
         f"ratio {_pct(ref['ratio'])} (95% interval {_pct(ref['ci'][0])}-{_pct(ref['ci'][1])}); lags 2-8: "
         + ", ".join(_pct(x) for x in ref["lags"][1:]) + ".", "",
         f"Solved plain-substitution text (sections 3, 7, 9, 27) has lag 1 at {_pct(rep['language']['ratio'])} (95% interval "
         f"{_pct(rep['language']['ci'][0])}-{_pct(rep['language']['ci'][1])}), below the synthetic English control, so the plaintext "
         "level is uncertain. Sensitivity (post hoc, not the pre-specified match): `loose` asks that the cipher lower the plaintext's own "
         f"lag-1 ratio by a factor in {_pct(rep['loose_band'][0])}-{_pct(rep['loose_band'][1])} (real interval over the solved-text "
         "interval) with lags 2-8 flat.", "",
         f"Real text: unigram IC x 29 = {ref['uni_ic']:.3f}, first-difference IC x 29 = {ref['diff_ic']:.3f} (uniform 1.0, language "
         f"1.6-2.0); both must be <= {IC_MAX} for a `full` match.", "",
         f"Controls on {rep['windows']} English windows of {rep['window_len']}: plaintext lag 1 {_pct(ctl['english'][0])}, "
         f"lags 2-8 " + ", ".join(_pct(x) for x in ctl["english"][1:]) + f", unigram IC {ctl['english_uni_ic']:.2f}, first-difference "
         f"IC {ctl['english_diff_ic']:.2f}; iid noise lag 1 {_pct(ctl['noise'][0])}. Positive control (not a DSL cipher): a random walk "
         f"whose zero steps are thinned to 20% has lag 1 {_pct(ctl['thinned_walk']['ratio'][0])}, lags 2-8 "
         f"{_pct(ctl['thinned_walk']['rest_min'])}-{_pct(ctl['thinned_walk']['rest_max'])}, unigram IC {ctl['thinned_walk']['uni_ic']:.2f}, "
         f"first-difference IC {ctl['thinned_walk']['diff_ic']:.2f}: full match "
         f"{'yes' if ctl['thinned_walk']['full'] else 'no'}.", "",
         "| family | candidates | errors | lag-1 ratio min / median / max | lag 1 in real interval | lags 2-8 flat | lag-only match | both ICs ok | full match | loose |",
         "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for fam, f in rep["families"].items():
        L.append(f"| {fam} | {f['candidates']} | {f['errors']} | {_pct(f['r1_min'])} / {_pct(f['r1_median'])} / {_pct(f['r1_max'])} | "
                 f"{f['in_ci']} | {f['flat']} | {f['match']} | {f['ic_ok']} | **{f['full']}** | {f['loose']} |")
    L += ["", f"Re-screened on {REFINE_WINDOWS} windows ({REFINE_WINDOWS * WINDOW_LEN} runes): matches first, then the closest "
          "lag-flat candidates.", "",
          "| family | cipher | lag 1 | lags 2-8 min-max | unigram IC | diff IC | lag-only match | full | loose |",
          "| --- | --- | ---: | --- | ---: | ---: | --- | --- | --- |"]
    for r in rep["refined"][:30]:
        L.append(f"| {r['family']} | {r['label']} | {_pct(r['r1'])} | {_pct(r['rest_min'])}-{_pct(r['rest_max'])} | "
                 f"{r['uni_ic']:.2f} | {r['diff_ic']:.2f} | {'yes' if r['match'] else 'no'} | {'**yes**' if r['full'] else 'no'} | "
                 f"{'yes' if r.get('loose') else 'no'} |")
    if not rep["refined"]:
        L.append("| none | | | | | | | | |")
    L += ["", f"Seconds: {rep['seconds']}.", ""]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    global _WORDKEYS, _WIDE
    from lpswarm.alphabet import get_alphabet
    from lpswarm.research_packets import ALPHABET, load_sections
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_signature", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="reports/diag")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--windows", type=int, default=WINDOWS)
    ap.add_argument("--wordkeys", type=int, default=5000)
    ap.add_argument("--no-wide", action="store_true", help="skip the wider mixer sweep (about 31,000 more ciphers)")
    args = ap.parse_args(argv)
    _WORDKEYS = args.wordkeys
    _WIDE = not args.no_wide
    t0 = time.monotonic()
    alpha = get_alphabet(ALPHABET)
    secs = load_sections(indexes=list(SECTIONS) + [3, 7, 9, 27])
    ref = reference(secs)
    language = reference(secs, (3, 7, 9, 27))
    loose_band = [ref["ci"][0] / language["ci"][1], ref["ci"][1] / language["ci"][0]]
    windows = english_windows(alpha, args.windows)
    rng = np.random.default_rng(SEED)
    noise = profile({str(i): rng.integers(0, N, size=WINDOW_LEN) for i in range(args.windows)})["ratio"]
    eng_pr = profile({str(i): pt for i, (pt, _b) in enumerate(windows)})
    english = eng_pr["ratio"]
    walk_pr = profile({str(i): thinned_walk(WINDOW_LEN, rng) for i in range(args.windows)})
    walk = {"ratio": [float(x) for x in walk_pr["ratio"]], "uni_ic": float(walk_pr["uni_ic"]),
            "diff_ic": float(walk_pr["diff_ic"]), **classify(walk_pr["ratio"], ref, None, None, walk_pr["uni_ic"], walk_pr["diff_ic"])}
    cands = list(_all_candidates(alpha))
    results = screen_all(cands, windows, args.workers)
    fams = summarise(results, ref, float(english[0]), loose_band)
    refined = refine(fams, ref, alpha, cands, SEED, args.workers, float(english[0]), loose_band)
    rep = {"label": LABEL, "reference": ref, "language": language, "loose_band": loose_band, "windows": args.windows, "window_len": WINDOW_LEN,
           "controls": {"english": [float(x) for x in english], "noise": [float(x) for x in noise],
                        "english_uni_ic": float(eng_pr["uni_ic"]), "english_diff_ic": float(eng_pr["diff_ic"]),
                        "thinned_walk": walk},
           "families": fams, "refined": refined, "flat_band": list(FLAT), "candidates": len(cands),
           "seconds": round(time.monotonic() - t0, 1)}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "signature_screen.json").write_text(json.dumps(rep, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    text = markdown(rep)
    (out / "signature_screen.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

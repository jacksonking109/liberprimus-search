"""Local-window search for a prime-style stream that is out of step with the text as a whole.

The solved prime page (a stream of primes minus one with F skipped and one skipped index, per the
source notes) only decodes cleanly from its start: any desynchronisation, a skip at one index or a
corrupted rune, makes a whole-text test fail even with the right stream. This searches locally instead.

    python -m lpswarm.research_windows --out reports/diag

Stage 1 (cheap, vectorised): for each of the longest F-free stretches of a section (an F-free stretch
is unaffected by how an F is treated) score the English bigram log-likelihood of every decryption
p = orient(c) - (a * S[o + t] + b) over orientation x scale x constant x start offset o.
Stage 2 (verification on text the selection never saw): for the best stage-1 candidates, decrypt the first
`window` runes with the resolved F-skip (each F literal or encrypted, a Viterbi search) at every global
offset consistent with the stretch's offset, and score only the runes OUTSIDE the stretch, against random
candidates run the same way. A stage-2 z at or above `FLAG_Z` is a lead to inspect, not a result: it still
has to go through the real oracle.

No ledger, no models; fixed seeds; exploratory. Uses the English bigram model of the oracle, so a plaintext
in another language will not be recognised (see research_views for the language-agnostic checks).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from lpswarm.programs.sequences import window
from lpswarm.research_packets import ALPHABET, load_sections
from lpswarm.research_structure import SEED, UNSOLVED, _jsonable

N = 29
OFFSETS = 6000
SCALES = (1, 28)
STRETCHES = 3
STRETCH_MIN = 60
TOP_K = 10
FLAG_Z = 8.0
NULL_CANDIDATES = 40
WINDOW = 800
LABEL = "EXPLORATORY: a stage-2 flag is a lead for the real oracle, not a result"


def stretches(x: np.ndarray, count: int = STRETCHES, min_len: int = STRETCH_MIN, limit: int | None = None):
    """The `count` longest runs of non-F runes (start, length), longest first, within the first `limit` runes."""
    xs = x[:limit] if limit else x
    runs, start = [], None
    for i, v in enumerate(list(xs) + [0]):
        if v != 0 and start is None:
            start = i
        elif v == 0 and start is not None:
            if i - start >= min_len:
                runs.append((start, i - start))
            start = None
    return sorted(runs, key=lambda r: -r[1])[:count]


def stage1(stretch: np.ndarray, bigram: np.ndarray, offsets: int = OFFSETS, seqs=("primes",), scales=SCALES,
           top_k: int = TOP_K) -> dict:
    """Bigram log-likelihood of every decryption of one F-free stretch."""
    L = len(stretch)
    flat = bigram.ravel()
    count, total, total2, top = 0, 0.0, 0.0, []
    for seq in seqs:
        S = window(seq, 0, offsets + L, N)
        V = sliding_window_view(S, L)[:offsets]
        for orient in (0, 1):
            m = (N - 1 - stretch) if orient else stretch
            for a in scales:
                base = (m[None, :] - (a * V) % N) % N
                for b in range(N):
                    D = (base - b) % N
                    sc = flat[D[:, :-1] * N + D[:, 1:]].sum(axis=1)
                    count += sc.size
                    total += float(sc.sum())
                    total2 += float((sc * sc).sum())
                    j = int(sc.argmax())
                    top.append((float(sc[j]), seq, orient, int(a), int(b), j))
                    top = sorted(top, reverse=True)[:top_k]
    mean = total / count
    sd = math.sqrt(max(total2 / count - mean * mean, 1e-18))
    return {"candidates": count, "mean": mean, "sd": sd, "top": top}


def _spec(seq: str, orient: int, a: int, b: int, offset: int) -> dict:
    return {"stream": {"kind": "sequence", "name": seq, "scale": a, "offset": offset, "add": b}, "combine": "sub",
            "map": "reverse" if orient else "identity", "skip": ["F"], "skip_mode": "resolve"}


def _outside_mean(plain: np.ndarray, bigram: np.ndarray, t0: int, length: int) -> float:
    """Mean bigram log-likelihood over adjacent pairs that do not touch the stretch [t0, t0 + length)."""
    i = np.arange(1, len(plain))
    keep = ~((i >= t0) & (i <= t0 + length))
    return float(bigram[plain[i[keep] - 1], plain[i[keep]]].mean())


def stage2(x: np.ndarray, st0: int, stl: int, cands, bigram: np.ndarray, alpha, window_len: int = WINDOW,
           offsets: int = OFFSETS, null_n: int = NULL_CANDIDATES, seed: int = SEED, cap_end: float = 1e18) -> dict:
    from lpswarm.programs import compile_spec
    from lpswarm.programs.resolve import resolve_decrypt
    xw = np.asarray(x[:window_len], dtype=np.int64)
    f_before = int((xw[:st0] == 0).sum())
    results = []
    for score, seq, orient, a, b, o in cands:
        best = None
        for j in range(f_before + 1):                          # F's before the stretch that did not advance the key
            og = o - st0 + j
            if og < 0:
                continue
            if time.monotonic() > cap_end:
                break
            try:
                spec = compile_spec(_spec(seq, orient, a, b, og), alpha)
                plain = resolve_decrypt(xw, spec, N, bigram)
            except Exception:                                  # noqa: BLE001 - an unusable alignment is skipped
                continue
            v = _outside_mean(np.asarray(plain, dtype=np.int64), bigram, st0, stl)
            if best is None or v > best["outside_mean_lm"]:
                best = {"outside_mean_lm": v, "global_offset": og, "literal_fs_before_stretch": j,
                        "preview": alpha.decode(np.asarray(plain[:48], dtype=np.int64))}
        if best:
            results.append({"stage1_score": score, "sequence": seq, "orientation": "reversed" if orient else "plain",
                            "scale": a, "constant": b, "stretch_offset": o, **best})
    rng = np.random.default_rng(seed + st0)
    nulls = []
    for _ in range(null_n):
        if time.monotonic() > cap_end:
            break
        try:
            spec = compile_spec(_spec(cands[0][1], int(rng.integers(0, 2)), int(rng.choice(SCALES)),
                                      int(rng.integers(0, N)), int(rng.integers(0, offsets))), alpha)
            nulls.append(_outside_mean(np.asarray(resolve_decrypt(xw, spec, N, bigram), dtype=np.int64), bigram, st0, stl))
        except Exception:                                      # noqa: BLE001
            continue
    nm, nsd = (float(np.mean(nulls)), float(np.std(nulls, ddof=1))) if len(nulls) > 5 else (float("nan"), float("nan"))
    for r in results:
        r["stage2_z"] = (r["outside_mean_lm"] - nm) / max(nsd, 1e-9) if not math.isnan(nm) else float("nan")
    results.sort(key=lambda r: -(r["stage2_z"] if not math.isnan(r["stage2_z"]) else -1e9))
    return {"null_mean_lm": nm, "null_sd_lm": nsd, "null_n": len(nulls), "verified": results[:5],
            "best_z": results[0]["stage2_z"] if results else float("nan"),
            "flag": bool(results and not math.isnan(results[0]["stage2_z"]) and results[0]["stage2_z"] >= FLAG_Z)}


def section_search(x: np.ndarray, bigram: np.ndarray, alpha, offsets: int = OFFSETS, seqs=("primes",),
                   scales=SCALES, window_len: int = WINDOW, nstretch: int = STRETCHES, seed: int = SEED,
                   cap_end: float = 1e18, null_reps: int = 2) -> dict:
    t0 = time.monotonic()
    xw = np.asarray(x[:window_len], dtype=np.int64)
    out = {"runes": len(x), "window": len(xw), "stretches": []}
    rng = np.random.default_rng(seed + len(x))
    for st0, stl in stretches(xw, nstretch):
        if time.monotonic() > cap_end:
            break
        s1 = stage1(xw[st0:st0 + stl], bigram, offsets, seqs, scales)
        best = s1["top"][0][0]
        shuffled = [stage1(rng.permutation(xw)[st0:st0 + stl], bigram, offsets, seqs, scales, top_k=1)["top"][0][0]
                    for _ in range(null_reps)]
        s2 = stage2(xw, st0, stl, s1["top"], bigram, alpha, window_len, offsets, seed=seed, cap_end=cap_end)
        out["stretches"].append({
            "start": st0, "length": stl, "candidates": s1["candidates"], "best_score": best,
            "best_per_symbol": best / (stl - 1), "z_vs_bulk": (best - s1["mean"]) / s1["sd"],
            "shuffled_best": max(shuffled) if shuffled else float("nan"),
            "stage1_top": [{"score": t[0], "sequence": t[1], "orientation": "reversed" if t[2] else "plain",
                            "scale": t[3], "constant": t[4], "offset": t[5]} for t in s1["top"][:3]],
            "stage2": s2})
    out["flag"] = any(s["stage2"]["flag"] for s in out["stretches"])
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


def make_controls(alpha, seed: int = SEED):
    """Synthetic ciphertexts: English through a prime-minus-one stream with the F-skip (F literal iff plaintext F),
    with and without one extra non-advancing index, plus uniform noise."""
    from lpswarm.textgen.synth import encoded_text
    text = np.asarray(encoded_text(alpha, "english", "train"), dtype=np.int64)
    rng = np.random.default_rng(seed + 21)
    S = window("primes", 0, 3000, N)

    def encipher(pt, skip_index=None, offset=500, b=1):
        ct, j = np.empty_like(pt), 0
        for t, v in enumerate(pt):
            if v == 0 or t == skip_index:
                ct[t] = v
            else:
                ct[t] = (int(v) + int(S[offset + j]) - b) % N          # decrypt: p = c - (prime - 1) with b = 1
                j += 1
        return ct
    pt = text[70000:70800]
    return [("English, prime-minus-one stream, F-skip", encipher(pt)),
            ("same, plus one extra skipped index at 200", encipher(pt, skip_index=200)),
            ("uniform noise", rng.integers(0, N, size=800))]


def to_markdown(rep: dict) -> str:
    L = ["# Local-window search for an out-of-step prime stream", "", f"**{LABEL}.**", "",
         f"Stage 1: bigram log-likelihood of every decryption of the longest F-free stretches "
         f"(orientation x scale x constant x offset 0..{rep['offsets']}, sequences {rep['sequences']}). Stage 2: the best "
         f"stage-1 candidates decrypted over the first {rep['window']} runes with the resolved F-skip and scored on the "
         f"runes outside the stretch, against {NULL_CANDIDATES} random candidates. Lead if z >= {FLAG_Z:g}. "
         + ("" if rep["complete"] else "**PARTIAL: time cap.** "), "",
         "| section | stretch | stage-1 best per symbol (z vs bulk; shuffled best per symbol) | best stage-2 z | best candidate | flag |",
         "| --- | --- | --- | ---: | --- | --- |"]
    rows = list(rep["sections"].items()) + [(f"control: {k}", v) for k, v in rep["controls"].items()]
    for sid, r in rows:
        for s in r["stretches"]:
            v = s["stage2"]["verified"][0] if s["stage2"]["verified"] else None
            L.append(f"| {sid} | {s['length']} runes at {s['start']} | {s['best_per_symbol']:.2f} ({s['z_vs_bulk']:.1f}; "
                     f"{s['shuffled_best'] / (s['length'] - 1):.2f}) | {s['stage2']['best_z']:.1f} | "
                     + (f"{v['sequence']} {v['orientation']} x{v['scale']} +{v['constant']} @{v['global_offset']}" if v else "none")
                     + f" | {'**LEAD**' if s['stage2']['flag'] else 'no'} |")
    L += ["", "Limits: English bigram model only; one sequence family (primes, which includes prime-minus-one through the "
          "constant) unless widened; stretches of 60 or more runes, so a stream broken more often than that is not "
          "reachable; the verification window is the first runes of the section.", ""]
    return "\n".join(L)


def main(argv: list[str] | None = None) -> int:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.oracle import FullOracle, OracleConfig
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_windows", description=__doc__.split("\n")[0])
    ap.add_argument("--sections", help="comma-separated manifest ids (default: unsolved sections of 300+ runes)")
    ap.add_argument("--offsets", type=int, default=OFFSETS)
    ap.add_argument("--sequences", default="primes", help="comma-separated sequence names (default: primes)")
    ap.add_argument("--window", type=int, default=WINDOW)
    ap.add_argument("--stretches", type=int, default=STRETCHES)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cap", type=float, default=2400.0, help="wall-clock seconds")
    ap.add_argument("--out", default="reports/diag")
    args = ap.parse_args(argv)
    ids = [int(v) for v in args.sections.split(",")] if args.sections else list(UNSOLVED)
    seqs = tuple(args.sequences.split(","))
    alpha = get_alphabet(ALPHABET)
    bigram = FullOracle(alpha, OracleConfig(null_samples=300)).bigram_table()
    secs = load_sections(indexes=ids)
    t0 = time.monotonic()
    end = t0 + args.cap
    rep = {"offsets": args.offsets, "sequences": list(seqs), "window": args.window, "complete": True, "sections": {},
           "controls": {}, "seed": args.seed}
    for name, ct in make_controls(alpha, args.seed):
        rep["controls"][name] = section_search(ct, bigram, alpha, args.offsets, seqs, SCALES, args.window,
                                                args.stretches, args.seed, end)
    for i in ids:
        if time.monotonic() > end:
            rep["complete"] = False
            break
        rep["sections"][str(i)] = section_search(secs[i]["ct"], bigram, alpha, args.offsets, seqs, SCALES, args.window,
                                                  args.stretches, args.seed, end)
    rep["seconds"] = round(time.monotonic() - t0, 2)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "diagnostics_windows.json").write_text(json.dumps(_jsonable(rep), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    md = to_markdown(rep)
    (out / "diagnostics_windows.md").write_text(md + "\n", encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Assumption audit: ways of looking at the ciphertext that do not assume English text.

No oracle, no models, no ledger. Fixed seeds, wall-clock caps (partial results marked), exploratory.

    python -m lpswarm.research_views agnostic --out reports/diag
    python -m lpswarm.research_views bytes    --out reports/diag
    python -m lpswarm.research_views numbers  --out reports/diag
    python -m lpswarm.research_views all      --out reports/diag

agnostic  decrypt with position-keyed streams (and the packet candidates) and score by the index of
          coincidence of the result: high for ANY natural language, no word list or language model
bytes     read the runes as binary data: base-29 integer to bytes, 5-bit packing, one byte per rune,
          rune pairs; decompression attempts, magic numbers, printable text, entropy, compressibility
numbers   read words and lines as numbers (primality, squares, Fibonacci) and test whether the text is
          itself a low-degree polynomial or a linear recurrence mod 29

The flag rule for the two IC-based checks was fixed before running on the real sections: IC x 29 of the
result >= FLAG_IC and above the maximum over the shuffled-ciphertext replicates of the same sweep. (The
plan's first guess for the null scale was too high: the unbiased IC x 29 of n random runes has mean 1 and
standard deviation about 7.5 / n, so the null maximum over a million candidates is about 1.1 at n = 600,
not 1.3-1.45; the rule's floor was corrected from 1.55 to 1.25 on that analytic argument, before any real
section was swept. Natural language gives about 1.6-2.0.)
"""
from __future__ import annotations

import argparse
import bz2
import json
import lzma
import math
import sys
import time
import zlib
from pathlib import Path

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from lpswarm.programs.sequences import window
from lpswarm.research_packets import ALPHABET, MANIFEST, load_sections
from lpswarm.research_structure import REFERENCE, SEED, UNSOLVED, _jsonable, _p_max

N = 29
WINDOW = 600
FLAG_IC = 1.25
OFFSETS = 3000
SCALES = tuple(range(1, N))
SEQS = ("primes", "prime_totients", "fibonacci", "naturals", "squares", "triangular", "pi_digits", "e_digits")
TREATMENTS = ("F untouched", "F literal, key does not advance", "F literal, key advances")
REPLICATES = 2
LABEL = "EXPLORATORY: fixed readings and sweeps, no language model; a flag is a lead to inspect, not a result"
BYTES_REPS = 99
NUMBER_REPS = 99
MAGICS = (("gzip", b"\x1f\x8b\x08"), ("bzip2", b"BZh"), ("xz", b"\xfd7zXZ\x00"), ("PGP armor", b"-----BEGIN PGP"),
          ("PNG", b"\x89PNG"), ("ZIP", b"PK\x03\x04"), ("ELF", b"\x7fELF"), ("PDF", b"%PDF"),
          ("JPEG", b"\xff\xd8\xff"), ("GIF", b"GIF8"), ("7z", b"7z\xbc\xaf\x27\x1c"))
DIGITS29 = "0123456789abcdefghijklmnopqrs"


def _z_loo(obs: np.ndarray, null: np.ndarray, floor: np.ndarray | float = 1e-9):
    """z of the observed statistics and of every shuffle, each against mean and sd taken over the OTHER
    shuffles (leave-one-out), so every sample is judged out-of-sample and none inflates its own scale.
    `null` is (stats, r). `floor` is the smallest meaningful sd (half a count for fractions of units)."""
    r = null.shape[1]
    s1, s2 = null.sum(axis=1), (null ** 2).sum(axis=1)
    m = s1 / r
    sd = np.sqrt(np.maximum((s2 - r * m * m) / (r - 1), 0))
    z_obs = (obs - m) / np.maximum(sd, floor)
    n1 = r - 1
    mj = (s1[:, None] - null) / n1
    vj = np.maximum((s2[:, None] - null ** 2 - n1 * mj ** 2) / (n1 - 1), 0)
    z_null = (null - mj) / np.maximum(np.sqrt(vj), np.asarray(floor).reshape(-1, 1) if np.ndim(floor) else floor)
    return z_obs, z_null


def ic_rows(D: np.ndarray) -> np.ndarray:
    """Unbiased index of coincidence x 29 for every row of D (values 0..28); null mean 1."""
    rows, n = D.shape
    idx = (np.arange(rows, dtype=np.int64)[:, None] * N + D).ravel()
    cnt = np.bincount(idx, minlength=rows * N).reshape(rows, N).astype(np.float64)
    return N * (cnt * (cnt - 1)).sum(axis=1) / (n * (n - 1))


def ic_of(x: np.ndarray) -> float:
    return float(ic_rows(np.asarray(x, dtype=np.int64)[None, :])[0])


# ------------------------------------------------------------------------------ agnostic
def _sweep(x: np.ndarray, offsets: int, scales, seqs, top_k: int = 5, treatments=(0, 1, 2)) -> dict:
    """IC of every decryption c - a*S[o + t] (S a sequence) over seq x treatment x scale x offset."""
    n = len(x)
    isF = x == 0
    before = np.concatenate([[0], np.cumsum(~isF)[:-1]])
    count, total, total2, best = 0, 0.0, 0.0, []
    for seq in seqs:
        S = window(seq, 0, offsets + n, N)
        V = sliding_window_view(S, n)[:offsets]
        G1 = S[np.arange(offsets)[:, None] + before[None, :]]
        for ti, G in enumerate((V, G1, V)):
            if ti not in treatments:
                continue
            for a in scales:
                D = (x[None, :] - a * G) % N
                if ti:
                    D = np.where(isF[None, :], x[None, :], D)
                ic = ic_rows(D)
                count += ic.size
                total += float(ic.sum())
                total2 += float((ic * ic).sum())
                j = int(ic.argmax())
                best.append((float(ic[j]), seq, TREATMENTS[ti], int(a), int(j)))
                best = sorted(best, reverse=True)[:top_k]
    mean = total / count
    sd = math.sqrt(max(total2 / count - mean * mean, 1e-18))
    return {"candidates": count, "mean": mean, "sd": sd, "best": best}


def _packet_specs():
    """Every packet candidate that `decrypt` can evaluate (resolved-skip specs need a language model)."""
    from lpswarm.alphabet import get_alphabet
    from lpswarm.programs import compile_spec, expand
    from lpswarm import research_packets as P
    alpha = get_alphabet(ALPHABET)
    out = []
    for name in ("exp1_feedback", "exp2_two_shear", "exp3_progressive", "exp4_wordkeys_reversed"):
        replies, _t = P.PACKETS[name]["replies"]()
        for r in replies:
            for p in json.loads(r)["proposals"]:
                for c in expand(compile_spec(p["spec"], alpha), None):
                    if c.get("skip_mode") != "resolve":
                        out.append((name, c))
    return out


def _packet_best(x: np.ndarray, breaks, specs, cap_end: float) -> dict:
    from lpswarm.programs import decrypt
    m = len(x) - (len(x) % 2)
    xs, bs = x[:m], [b for b in breaks if 0 < b < m]
    best, done = [], 0
    for name, spec in specs:
        if time.monotonic() >= cap_end:
            break
        try:
            ic = ic_of(decrypt(xs, spec, N, breaks=bs))
        except Exception:               # noqa: BLE001 - a spec that cannot run on this text is skipped
            continue
        done += 1
        best.append((ic, name))
        if len(best) > 64:
            best = sorted(best, reverse=True)[:5]
    return {"evaluated": done, "best": sorted(best, reverse=True)[:5]}


STRETCH_MIN = 40


def longest_f_free(x: np.ndarray) -> tuple[int, int]:
    """(start, length) of the longest run of non-F runes. Inside it nothing depends on how an F is treated."""
    best = (0, 0)
    start = None
    for i, v in enumerate(list(x) + [0]):
        if v != 0 and start is None:
            start = i
        elif v == 0 and start is not None:
            if i - start > best[1]:
                best = (start, i - start)
            start = None
    return best


STRETCH_REPLICATES = 20
STRETCH_SIGMAS = 4.0


def agnostic_section(x: np.ndarray, breaks=(), offsets: int = OFFSETS, scales=SCALES, seqs=SEQS,
                     replicates: int = REPLICATES, seed: int = SEED, window_len: int = WINDOW,
                     specs=None, cap_s: float = 1e9, stretch_reps: int = STRETCH_REPLICATES) -> dict:
    t0 = time.monotonic()
    xw = np.asarray(x[:window_len], dtype=np.int64)
    rng = np.random.default_rng(seed + len(xw))
    real = _sweep(xw, offsets, scales, seqs)
    null_max = [_sweep(rng.permutation(xw), offsets, scales, seqs)["best"][0][0] for _ in range(replicates)]
    top = real["best"][0][0]
    nm = max(null_max) if null_max else float("nan")
    st0, stl = longest_f_free(xw)
    stretch = None
    if stl >= STRETCH_MIN:
        real_s = _sweep(xw[st0:st0 + stl], offsets, scales, seqs, treatments=(0,))
        null_s = np.array([_sweep(rng.permutation(xw)[st0:st0 + stl], offsets, scales, seqs,
                                  treatments=(0,))["best"][0][0] for _ in range(stretch_reps)])
        bs = real_s["best"][0][0]
        thr = float(null_s.mean() + STRETCH_SIGMAS * null_s.std(ddof=1)) if len(null_s) > 2 else float("nan")
        stretch = {"start": st0, "length": stl, "best_ic": bs, "null_max_ic": float(null_s.max()),
                   "null_mean_ic": float(null_s.mean()), "threshold": thr, "null_replicates": len(null_s),
                   "z_vs_bulk": (bs - real_s["mean"]) / real_s["sd"],
                   "top": [{"ic": b[0], "sequence": b[1], "scale": b[3], "offset": b[4]} for b in real_s["best"][:3]],
                   "flag": bool(len(null_s) > 2 and bs > null_s.max() and bs >= thr)}
    out = {"window": len(xw), "candidates": real["candidates"], "bulk_mean": real["mean"], "bulk_sd": real["sd"],
           "best_ic": top, "z_vs_bulk": (top - real["mean"]) / real["sd"], "null_max_ic": nm,
           "null_replicates": replicates,
           "top": [{"ic": b[0], "sequence": b[1], "treatment": b[2], "scale": b[3], "offset": b[4]}
                   for b in real["best"]],
           "flag": bool((top >= FLAG_IC and top > nm) or (stretch and stretch["flag"])), "stretch": stretch}
    if specs is not None:
        pk = _packet_best(x, breaks, specs, t0 + cap_s)
        pnull = _packet_best(rng.permutation(xw), [], specs, t0 + cap_s) if replicates else {"best": []}
        pb = pk["best"][0][0] if pk["best"] else float("nan")
        pn = pnull["best"][0][0] if pnull["best"] else float("nan")
        out["packets"] = {"evaluated": pk["evaluated"], "best_ic": pb, "best_packet": pk["best"][0][1] if pk["best"] else None,
                          "null_max_ic": pn, "flag": bool(pb >= FLAG_IC and pb > pn),
                          "note": "packet candidates scored by IC only; not run through the oracle or any ledger"}
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


def agnostic_controls(offsets: int = OFFSETS, replicates: int = REPLICATES, seed: int = SEED,
                      scales=SCALES, seqs=SEQS) -> list[dict]:
    """Synthetic cases with their own answers: English / non-English letters through position-keyed streams."""
    from lpswarm.alphabet import get_alphabet
    from lpswarm.programs import compile_spec, encrypt, roundtrips
    from lpswarm.textgen.synth import encoded_text
    alpha = get_alphabet(ALPHABET)
    text = np.asarray(encoded_text(alpha, "english", "train"), dtype=np.int64)
    rng = np.random.default_rng(seed + 99)
    zipf = 1.0 / np.arange(1, N + 1)
    zipf /= zipf.sum()
    cases = [
        ("English through a totient stream, offset 777",
         {"stream": {"kind": "sequence", "name": "prime_totients", "scale": 1, "offset": 777, "add": 0}, "combine": "sub"},
         lambda: text[40000:40600]),
        ("English through a Fibonacci stream with the F-skip (F literal iff plaintext F; ambiguous as on the real pages)",
         "fskip", lambda: text[60000:60600]),
        ("non-English letters (iid, skewed) through a prime stream",
         {"stream": {"kind": "sequence", "name": "primes", "scale": 2, "offset": 345, "add": 0}, "combine": "sub"},
         lambda: rng.choice(N, size=600, p=zipf)),
        ("iid uniform noise (no cipher)", None, lambda: rng.integers(0, N, size=600)),
    ]
    out = []
    for name, spec, make in cases:
        pt = np.asarray(make(), dtype=np.int64)
        if spec is None:
            ct = pt
        elif spec == "fskip":
            S = window("fibonacci", 0, 91 + len(pt) + 5, N)
            ct, j = np.empty_like(pt), 0
            for t, v in enumerate(pt):
                if v == 0:
                    ct[t] = 0
                else:
                    ct[t] = (int(v) + 3 * int(S[91 + j])) % N
                    j += 1
        else:
            comp = compile_spec(spec, alpha)
            for _ in range(200):
                if roundtrips(pt, comp, N):
                    break
                pt = np.asarray(make(), dtype=np.int64)
            ct = np.asarray(encrypt(pt, comp, N), dtype=np.int64)
        r = agnostic_section(ct, offsets=offsets, scales=scales, seqs=seqs, replicates=replicates, seed=seed)
        r["case"] = name
        out.append(r)
    return out


# --------------------------------------------------------------------------------- bytes
def _to_bytes(value: int) -> bytes:
    return value.to_bytes(max((value.bit_length() + 7) // 8, 1), "big")


def base29_value(x, msb: bool = True) -> int:
    seq = x if msb else x[::-1]
    return int("".join(DIGITS29[int(d)] for d in seq), 29) if len(seq) else 0


def readings(x: np.ndarray) -> dict[str, bytes]:
    x = np.asarray(x, dtype=np.int64)
    out = {"base 29, digits most significant first": _to_bytes(base29_value(x, True)),
           "base 29, digits least significant first": _to_bytes(base29_value(x, False))}
    bits = "".join(format(int(v), "05b") for v in x)
    bits += "0" * (-len(bits) % 8)
    out["5-bit packing"] = int(bits, 2).to_bytes(len(bits) // 8, "big") if bits else b""
    out["one byte per rune"] = bytes(int(v) for v in x)
    pairs = x[: len(x) - len(x) % 2].reshape(-1, 2)
    out["two runes to one byte"] = bytes(int((a * N + b) & 0xFF) for a, b in pairs)
    return out


def _stream_hit(kind: str, data: bytes) -> bool:
    try:
        if kind == "zlib":
            d = zlib.decompressobj()
        elif kind == "gzip":
            d = zlib.decompressobj(16 + zlib.MAX_WBITS)
        elif kind == "bz2":
            d = bz2.BZ2Decompressor()
        else:
            d = lzma.LZMADecompressor()
        out = d.decompress(data)
        return bool(d.eof and len(out) > 0)
    except Exception:                    # noqa: BLE001 - any decoder error means "not a valid stream"
        return False


def structure_hits(data: bytes, max_offset: int = 32) -> list[dict]:
    hits = []
    for off in range(min(max_offset, max(len(data) - 8, 0))):
        chunk = data[off:]
        for kind in ("zlib", "gzip", "bz2", "xz"):
            if _stream_hit(kind, chunk):
                hits.append({"offset": off, "kind": f"valid {kind} stream"})
        for name, magic in MAGICS:
            if chunk.startswith(magic):
                hits.append({"offset": off, "kind": f"magic number: {name}"})
    return hits


def _byte_stats(b: bytes) -> list[float]:
    """printable fraction, longest printable run, entropy (bits/byte), zlib ratio, lzma ratio."""
    if len(b) < 16:
        return [float("nan")] * 5
    arr = np.frombuffer(b, dtype=np.uint8)
    printable = ((arr >= 32) & (arr < 127)) | (arr == 10) | (arr == 9)
    run = best = 0
    for v in printable:
        run = run + 1 if v else 0
        best = max(best, run)
    p = np.bincount(arr, minlength=256) / len(arr)
    nz = p > 0
    return [float(printable.mean()), float(best), float(-(p[nz] * np.log2(p[nz])).sum()),
            len(zlib.compress(b, 9)) / len(b), len(lzma.compress(b)) / len(b)]


STAT_NAMES = ("printable fraction", "longest printable run", "entropy", "zlib ratio", "lzma ratio")


def bytes_section(x: np.ndarray, reps: int = BYTES_REPS, seed: int = SEED, cap_s: float = 1e9) -> dict:
    t0 = time.monotonic()
    x = np.asarray(x, dtype=np.int64)
    rd = readings(x)
    names = list(rd)
    obs = np.array([_byte_stats(rd[k]) for k in names]).ravel()
    obs_idx = _byte_stats(bytes(int(v) for v in x))         # rune-index bytes: catches long repeats
    rng = np.random.default_rng(seed + len(x))
    null = []
    complete = True
    for _ in range(reps):
        if time.monotonic() - t0 >= cap_s:
            complete = False
            break
        xs = rng.permutation(x)
        null.append(np.array([_byte_stats(readings(xs)[k]) for k in names]).ravel())
    out: dict = {"runes": len(x), "complete": complete, "shuffles": len(null),
                 "hits": {k: structure_hits(rd[k]) for k in names}, "bytes": {k: len(rd[k]) for k in names}}
    if len(null) >= 20:
        NU = np.array(null).T                                # (stats, r)
        ok = ~np.isnan(obs) & ~np.isnan(NU).any(axis=1)
        lens = np.array([max(len(rd[k]), 1) for k in names for _ in STAT_NAMES], dtype=float)
        unit = np.array([0.5, 0.5, 1e-3, 0.5, 0.5])                   # smallest meaningful sd per statistic
        floor = np.tile(unit, len(names))
        floor[0::5] = 0.5 / lens[0::5]                                # fractions: half a byte
        floor[3::5] = 0.5 / lens[3::5]                                # compression ratios: half a byte
        floor[4::5] = 0.5 / lens[4::5]
        z, zn = _z_loo(obs[ok], NU[ok], floor=floor[ok])
        zmax = float(np.abs(z).max()) if ok.any() else float("nan")
        order = np.argsort(-np.abs(z))[:4]
        labels = [f"{names[i // 5]}: {STAT_NAMES[i % 5]}" for i in np.nonzero(ok)[0]]
        out["max_abs_z"] = zmax
        out["p_max_over_stats"] = _p_max(zmax, np.abs(zn).max(axis=0))
        out["stats_tested"] = int(ok.sum())
        out["top"] = [{"stat": labels[i], "z": float(z[i])} for i in order]
    out["rune_index_bytes"] = dict(zip(STAT_NAMES, obs_idx))
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


def bytes_controls(reps: int = BYTES_REPS, seed: int = SEED) -> list[dict]:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.textgen.synth import encoded_text
    alpha = get_alphabet(ALPHABET)
    text = np.asarray(encoded_text(alpha, "english", "train"), dtype=np.int64)
    rng = np.random.default_rng(seed + 7)
    english_bytes = bytes(int(v) + 65 for v in text[:3000])
    z = zlib.compress(english_bytes, 9)

    def runes_of(data: bytes) -> np.ndarray:
        v, digs = int.from_bytes(data, "big"), []
        while v:
            v, r = divmod(v, N)
            digs.append(r)
        return np.array(digs[::-1], dtype=np.int64)

    cases = [("zlib-compressed text written in base 29", runes_of(z)),
             ("random bytes written in base 29", runes_of(bytes(rng.integers(0, 256, size=400, dtype=np.uint8)))),
             ("uniform random runes", rng.integers(0, N, size=600)),
             ("English plaintext runes", text[30000:30600])]
    out = []
    for name, x in cases:
        r = bytes_section(x, reps=reps, seed=seed)
        r["case"] = name
        out.append(r)
    return out


# ------------------------------------------------------------------------------ numbers
SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in SMALL_PRIMES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in SMALL_PRIMES:
        y = pow(a, d, n)
        if y in (1, n - 1):
            continue
        for _ in range(s - 1):
            y = y * y % n
            if y == n - 1:
                break
        else:
            return False
    return True


def is_square(n: int) -> bool:
    return n >= 0 and math.isqrt(n) ** 2 == n


def is_fibonacci(n: int) -> bool:
    return n >= 0 and (is_square(5 * n * n + 4) or is_square(5 * n * n - 4))


def parse_units(raw: str, alpha) -> tuple[np.ndarray, list[int], list[int]]:
    """(flat rune indexes, rune count per word, rune count per line) from raw rune text. Words end at a
    bullet or whitespace; lines end at a line break."""
    flat, words, lines = [], [], []
    wlen = llen = 0
    for ch in raw:
        a = alpha.encode(ch, glyphs_only=True)
        if len(a) == 1:
            flat.append(int(a[0]))
            wlen += 1
            llen += 1
        elif ch == "•" or ch.isspace():
            if wlen:
                words.append(wlen)
                wlen = 0
            if ch == "\n" and llen:
                lines.append(llen)
                llen = 0
    if wlen:
        words.append(wlen)
    if llen:
        lines.append(llen)
    return np.array(flat, dtype=np.int64), words, lines


NUMBER_READINGS = ("W1 base 29, most significant first", "W2 base 29, least significant first",
                   "W3 decimal concatenation of indexes", "W4 sum of Gematria prime values", "W5 sum of indexes")
LINE_READINGS = ("L1 base 29, most significant first", "L2 base 29, least significant first")
PROPS = (("prime", is_prime), ("square", is_square), ("Fibonacci", is_fibonacci))


def unit_numbers(flat: np.ndarray, lens: list[int], values, line: bool = False) -> list[list[int]]:
    """One list of numbers per reading, one number per unit."""
    cols = [[] for _ in (LINE_READINGS if line else NUMBER_READINGS)]
    pos = 0
    for L in lens:
        seg = flat[pos:pos + L]
        pos += L
        s = "".join(DIGITS29[int(d)] for d in seg)
        cols[0].append(int(s, 29))
        cols[1].append(int(s[::-1], 29))
        if not line:
            cols[2].append(int("".join(str(int(d)) for d in seg)))
            cols[3].append(int(sum(values[int(d)] for d in seg)))
            cols[4].append(int(seg.sum()))
    return cols


def _fractions(cols: list[list[int]]) -> np.ndarray:
    return np.array([[sum(f(v) for v in col) / max(len(col), 1) for _n, f in PROPS] for col in cols]).ravel()


def numbers_section(items: list[dict], values, reps: int = NUMBER_REPS, seed: int = SEED, cap_s: float = 1e9,
                    lines: bool = True) -> dict:
    """items: one dict per section with flat runes, word lengths and line lengths. Primality / square /
    Fibonacci fractions of the words (and lines) read as numbers, against shuffles that permute the runes
    across the pooled sections with every word and line length fixed."""
    t0 = time.monotonic()
    flat = np.concatenate([it["flat"] for it in items])
    wl = [L for it in items for L in it["words"]]
    ll = [L for it in items for L in it["lines"]]

    def stats(f):
        a = _fractions(unit_numbers(f, wl, values))
        if lines:
            a = np.concatenate([a, _fractions(unit_numbers(f, ll, values, line=True))])
        return a

    obs = stats(flat)
    rng = np.random.default_rng(seed + len(flat))
    null, complete = [], True
    for _ in range(reps):
        if time.monotonic() - t0 >= cap_s:
            complete = False
            break
        null.append(stats(rng.permutation(flat)))
    names = [f"{r}: fraction {p}" for r in NUMBER_READINGS for p, _f in PROPS]
    if lines:
        names += [f"{r}: fraction {p}" for r in LINE_READINGS for p, _f in PROPS]
    out: dict = {"words": len(wl), "lines": len(ll), "shuffles": len(null), "complete": complete}
    if len(null) >= 20:
        NU = np.array(null).T
        units = np.array([len(wl)] * (len(PROPS) * len(NUMBER_READINGS)) +
                         [len(ll)] * (len(PROPS) * len(LINE_READINGS) if lines else 0), dtype=float)
        z, zn = _z_loo(obs, NU, floor=0.5 / units)            # half a unit is the smallest meaningful sd
        order = np.argsort(-np.abs(z))[:6]
        out["max_abs_z"] = float(np.abs(z).max())
        out["p_max_over_readings"] = _p_max(float(np.abs(z).max()), np.abs(zn).max(axis=0))
        out["readings_tested"] = len(names)
        out["top"] = [{"reading": names[i], "observed": float(obs[i]), "shuffle_mean": float(NU[i].mean()),
                       "z": float(z[i])} for i in order]
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


def finite_difference_ic(x: np.ndarray, max_order: int = 8) -> list[float]:
    out, d = [], np.asarray(x, dtype=np.int64)
    for _ in range(max_order):
        d = np.diff(d) % N
        out.append(ic_of(d) if len(d) > 20 else float("nan"))
    return out


def recurrence_best(x: np.ndarray, order: int) -> tuple[float, tuple]:
    """Best IC x 29 of the residual c_t - a1 c_(t-1) - ... - ak c_(t-k) over all coefficients mod 29."""
    x = np.asarray(x, dtype=np.int64)
    k = order
    lags = [x[k - j: len(x) - j] for j in range(1, k + 1)]
    base = x[k:]
    grid = np.stack(np.meshgrid(*[np.arange(N)] * (k - 1), indexing="ij"), axis=-1).reshape(-1, k - 1) \
        if k > 1 else np.zeros((1, 0), dtype=np.int64)
    best, arg = -1.0, None
    for a1 in range(N):
        R = base[None, :] - a1 * lags[0][None, :]
        for j in range(1, k):
            R = R - grid[:, j - 1][:, None] * lags[j][None, :]
        ic = ic_rows(R % N)
        i = int(ic.argmax())
        if ic[i] > best:
            best, arg = float(ic[i]), (a1, *[int(v) for v in grid[i]])
    return best, arg


def sequence_fits(x: np.ndarray, replicates: int = REPLICATES, seed: int = SEED, window_len: int = WINDOW,
                  orders=(2, 3)) -> dict:
    t0 = time.monotonic()
    xw = np.asarray(x[:window_len], dtype=np.int64)
    rng = np.random.default_rng(seed + len(xw) + 5)
    out: dict = {"window": len(xw)}
    diffs = finite_difference_ic(xw)
    nd = [max(v for v in finite_difference_ic(rng.permutation(xw)) if not math.isnan(v)) for _ in range(replicates)]
    out["finite_differences"] = {"ic_by_order": diffs, "null_max_ic": max(nd) if nd else float("nan"),
                                 "flag": bool(max(v for v in diffs if not math.isnan(v)) >= FLAG_IC and
                                              max(v for v in diffs if not math.isnan(v)) > (max(nd) if nd else 0))}
    for k in orders:
        best, coef = recurrence_best(xw, k)
        nm = [recurrence_best(rng.permutation(xw), k)[0] for _ in range(replicates)]
        out[f"recurrence_order_{k}"] = {"best_ic": best, "coefficients": coef, "null_max_ic": max(nm) if nm else float("nan"),
                                        "flag": bool(best >= FLAG_IC and best > (max(nm) if nm else 0))}
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


def number_controls(values, reps: int = NUMBER_REPS, seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed + 11)
    primes = [p for p in range(29 ** 3, 29 ** 4) if is_prime(p)]

    def digits(v: int, k: int = 4) -> list[int]:
        return [(v // N ** (k - 1 - i)) % N for i in range(k)]

    def section(word_values):
        flat = np.array([d for v in word_values for d in digits(v)], dtype=np.int64)
        return {"flat": flat, "words": [4] * len(word_values), "lines": [40] * (len(flat) // 40)}

    prime_words = section([int(rng.choice(primes)) for _ in range(400)])
    random_words = section([int(rng.integers(29 ** 3, 29 ** 4)) for _ in range(400)])
    return {"words that are primes written in base 29": numbers_section([prime_words], values, reps, seed, lines=False),
            "words from random runes": numbers_section([random_words], values, reps, seed, lines=False)}


def sequence_controls(seed: int = SEED, replicates: int = REPLICATES) -> dict:
    t = np.arange(600)
    rng = np.random.default_rng(seed + 3)
    poly = (3 * t ** 3 + 5 * t ** 2 + 7 * t + 11) % N
    rec = np.zeros(600, dtype=np.int64)
    rec[:2] = (4, 9)
    for i in range(2, 600):
        rec[i] = (3 * rec[i - 1] + 5 * rec[i - 2]) % N
    return {"cubic polynomial in position": sequence_fits(poly, replicates, seed),
            "second-order recurrence (3, 5)": sequence_fits(rec, replicates, seed),
            "uniform random runes": sequence_fits(rng.integers(0, N, size=600), replicates, seed)}


# ------------------------------------------------------------------------------ output
def _f(v, d=2):
    return "n/a" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:.{d}f}"


def to_markdown(rep: dict) -> str:
    L = ["# Assumption audit: language-agnostic and data views", "", f"**{LABEL}.**", ""]
    if rep.get("derive", "none") != "none":
        L += [f"**Run on the {'first differences c[i]-c[i-1]' if rep['derive'] == 'diff' else 'neighbour sums c[i]+c[i-1]'} "
              "(mod 29) of each section, not on the runes themselves.**", ""]
    ag = rep.get("agnostic")
    if ag:
        L += ["## 1. Decrypt, then index of coincidence (any language)", "",
              f"Window: first {WINDOW} runes. Families: {len(SEQS)} sequences x {len(SCALES)} scales x "
              f"{ag['offsets']} offsets x 3 F treatments; plus every packet candidate that can be evaluated. "
              f"Flag: IC x 29 >= {FLAG_IC} and above the shuffled-ciphertext maximum "
              f"({ag['replicates']} replicates). Natural language gives about 1.6-2.0. "
              + ("" if ag["complete"] else "**PARTIAL: time cap.** "), "",
              "| section | best IC | z vs bulk | shuffled max | best candidate | longest F-free stretch: IC (null max, floor) | flag | packets: best IC (null max) |",
              "| ---: | ---: | ---: | ---: | --- | --- | --- | --- |"]
        for sid, r in ag["sections"].items():
            t = r["top"][0]
            pk = r.get("packets")
            L.append(f"| {sid} | {_f(r['best_ic'], 3)} | {_f(r['z_vs_bulk'], 1)} | {_f(r['null_max_ic'], 3)} | "
                     f"{t['sequence']} x{t['scale']} @{t['offset']} ({t['treatment']}) | "
                     + (f"{r['stretch']['length']} runes: {_f(r['stretch']['best_ic'], 3)} ({_f(r['stretch']['null_max_ic'], 3)}, "
                        f"{_f(r['stretch']['threshold'], 2)}) | " if r.get("stretch") else "none >= 40 runes | ")
                     + f"{'**FLAG**' if r['flag'] else 'no'} | "
                     + (f"{_f(pk['best_ic'], 3)} ({_f(pk['null_max_ic'], 3)}){' **FLAG**' if pk['flag'] else ''}"
                        if pk else "n/a") + " |")
        L += ["", "Synthetic controls (their answers are known):", "",
              "| case | best IC | shuffled max | flag | best candidate |", "| --- | ---: | ---: | --- | --- |"]
        for c in ag["controls"]:
            t = c["top"][0]
            L.append(f"| {c['case']} | {_f(c['best_ic'], 3)} | {_f(c['null_max_ic'], 3)} | "
                     f"{'**FLAG**' if c['flag'] else 'no'} | {t['sequence']} x{t['scale']} @{t['offset']} ({t['treatment']}) |")
        L += ["", "Limits: the three F treatments assume each F is literal for every F or for none; the documented F-skip "
              "pages need each F resolved separately, so those are only reachable through the longest F-free stretch, "
              "and a stretch of 60-120 runes searched over about 700,000 candidates reaches an IC from noise alone that "
              "language also reaches (see the null mean and maximum): the check is blind there. A stream that falls out "
              "of step partway (a skip at one index) is in the same position.", ""]
    by = rep.get("bytes")
    if by:
        L += ["## 2. Runes as binary data", "",
              "Readings: base-29 integer to bytes (both digit orders), 5-bit packing, one byte per rune, rune pairs. "
              "Hits are valid zlib/gzip/bzip2/xz streams or magic numbers at offsets 0-31 (chance is negligible). "
              "The statistics are calibrated as the maximum over all readings x statistics, 99 shuffles.", "",
              "| section | runes | hits | max |z| | p (max over stats) | top statistic |", "| --- | ---: | --- | ---: | ---: | --- |"]
        for sid, r in {**by["sections"], **{f"{k} (reference)": v for k, v in by.get("references", {}).items()}}.items():
            nh = sum(len(v) for v in r["hits"].values())
            top = r.get("top", [{}])[0]
            L.append(f"| {sid} | {r['runes']} | {nh} | {_f(r.get('max_abs_z'), 1)} | {_f(r.get('p_max_over_stats'), 3)} | "
                     f"{top.get('stat', 'n/a')} ({_f(top.get('z'), 1)}) |")
        L += ["", "Controls:", "", "| case | hits | max |z| | p | top statistic |", "| --- | --- | ---: | ---: | --- |"]
        for c in by["controls"]:
            hs = [f"{k.split(',')[0]}: {h['kind']}" for k, v in c["hits"].items() for h in v][:2]
            top = c.get("top", [{}])[0]
            L.append(f"| {c['case']} | {'; '.join(hs) or 'none'} | {_f(c.get('max_abs_z'), 1)} | "
                     f"{_f(c.get('p_max_over_stats'), 3)} | {top.get('stat', 'n/a')} |")
        L += ["", "Limit: encrypted binary data (uniform bytes) is undetectable by these views.", ""]
    nu = rep.get("numbers")
    if nu:
        w = nu["words_and_lines"]
        L += ["## 3. Numbers as text", "",
              f"{w['words']} words and {w['lines']} lines of the unsolved sections read as numbers; fractions that are "
              f"prime / square / Fibonacci against {w['shuffles']} shuffles (runes permuted, word and line lengths "
              f"fixed). Max |z| {_f(w.get('max_abs_z'), 1)} over {w.get('readings_tested', 0)} readings, "
              f"p {_f(w.get('p_max_over_readings'), 3)}.", "",
              "| reading | observed | shuffle mean | z |", "| --- | ---: | ---: | ---: |"]
        for t in w.get("top", []):
            L.append(f"| {t['reading']} | {t['observed']:.4f} | {t['shuffle_mean']:.4f} | {t['z']:+.1f} |")
        L += ["", "Controls:", "", "| case | max |z| | p |", "| --- | ---: | ---: |"]
        for k, v in nu["controls"].items():
            L.append(f"| {k} | {_f(v.get('max_abs_z'), 1)} | {_f(v.get('p_max_over_readings'), 3)} |")
        L += ["", "Does the text itself look like a generated number sequence? IC x 29 of the finite differences "
              f"(orders 1-8) and of the best linear-recurrence residual (orders 2 and 3), flag rule IC >= {FLAG_IC} "
              "and above the shuffled maximum:", "",
              "| section | best difference IC | best order-2 IC | best order-3 IC | flag |", "| ---: | ---: | ---: | ---: | --- |"]
        for sid, r in nu["sequence_fits"].items():
            fd = [v for v in r["finite_differences"]["ic_by_order"] if not math.isnan(v)]
            flag = any(r[k]["flag"] for k in ("finite_differences", "recurrence_order_2", "recurrence_order_3"))
            L.append(f"| {sid} | {_f(max(fd), 3)} | {_f(r['recurrence_order_2']['best_ic'], 3)} | "
                     f"{_f(r['recurrence_order_3']['best_ic'], 3)} | {'**FLAG**' if flag else 'no'} |")
        L += ["", "Sequence-fit controls:", "", "| case | best order-2 IC | best order-3 IC | flag |", "| --- | ---: | ---: | --- |"]
        for k, r in nu["sequence_controls"].items():
            flag = any(r[x]["flag"] for x in ("finite_differences", "recurrence_order_2", "recurrence_order_3"))
            L.append(f"| {k} | {_f(r['recurrence_order_2']['best_ic'], 3)} | {_f(r['recurrence_order_3']['best_ic'], 3)} | "
                     f"{'**FLAG**' if flag else 'no'} |")
        L.append("")
    return "\n".join(L)


def run_agnostic(secs: dict, ids, offsets: int, replicates: int, cap_s: float, seed: int, with_packets: bool) -> dict:
    t0 = time.monotonic()
    specs = _packet_specs() if with_packets else None
    out = {"offsets": offsets, "replicates": replicates, "complete": True, "sections": {}}
    for i in ids:
        left = cap_s - (time.monotonic() - t0)
        if left <= 0:
            out["complete"] = False
            break
        out["sections"][str(i)] = agnostic_section(secs[i]["ct"], secs[i]["breaks"], offsets=offsets,
                                                   replicates=replicates, seed=seed, specs=specs, cap_s=left)
    out["controls"] = agnostic_controls(offsets=offsets, replicates=replicates, seed=seed)
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


def run_bytes(secs: dict, ids, reps: int, cap_s: float, seed: int) -> dict:
    t0 = time.monotonic()
    out = {"sections": {}, "references": {}, "complete": True}
    for i in ids:
        out["sections"][str(i)] = bytes_section(secs[i]["ct"], reps, seed, max(cap_s - (time.monotonic() - t0), 1))
    for i in REFERENCE:
        if i in secs:
            out["references"][str(i)] = bytes_section(secs[i]["ct"], reps, seed, max(cap_s - (time.monotonic() - t0), 1))
    out["controls"] = bytes_controls(reps, seed)
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


def run_numbers(secs: dict, ids, reps: int, cap_s: float, seed: int) -> dict:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.textio import read_text
    t0 = time.monotonic()
    alpha = get_alphabet(ALPHABET)
    values = [int(v) for v in json.loads(read_text(Path("data/alphabet/gematria_primus.json")))["values"]]
    man = json.loads(read_text(Path(MANIFEST)))
    files = {s["index"]: Path(MANIFEST).parent / s["file"] for s in man["sections"]}
    items = []
    for i in ids:
        flat, words, lines = parse_units(read_text(files[i]), alpha)
        items.append({"flat": flat, "words": words, "lines": lines})
    out = {"words_and_lines": numbers_section(items, values, reps, seed, cap_s),
           "controls": number_controls(values, reps, seed), "sequence_fits": {}, "sequence_controls": sequence_controls(seed)}
    for i in ids:
        out["sequence_fits"][str(i)] = sequence_fits(secs[i]["ct"], seed=seed)
    out["seconds"] = round(time.monotonic() - t0, 2)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_views", description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["agnostic", "bytes", "numbers", "all"])
    ap.add_argument("--sections", help="comma-separated manifest ids (default: unsolved sections of 300+ runes)")
    ap.add_argument("--offsets", type=int, default=OFFSETS)
    ap.add_argument("--replicates", type=int, default=REPLICATES)
    ap.add_argument("--reps", type=int, default=BYTES_REPS)
    ap.add_argument("--no-packets", action="store_true", help="skip the packet-candidate IC scoring")
    ap.add_argument("--derive", choices=["none", "diff", "sum"], default="none",
                    help="run the checks on the first differences (c[i]-c[i-1]) or neighbour sums (c[i]+c[i-1]) mod 29 "
                         "instead of the runes: tests a running-sum / chain construction")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--cap", type=float, default=1800.0, help="wall-clock seconds per command")
    ap.add_argument("--out", default="reports/diag")
    args = ap.parse_args(argv)
    ids = [int(v) for v in args.sections.split(",")] if args.sections else list(UNSOLVED)
    secs = load_sections(indexes=sorted(set(ids) | set(REFERENCE)))
    if args.derive != "none":
        for sec in secs.values():
            c = sec["ct"]
            sec["ct"] = ((c[1:] - c[:-1]) if args.derive == "diff" else (c[1:] + c[:-1])) % N
            sec["breaks"] = [b - 1 for b in sec["breaks"] if b > 1]
            sec["label"] += f" [{args.derive}]"
    rep: dict = {"label": LABEL, "seed": args.seed, "derive": args.derive}
    if args.command in ("agnostic", "all"):
        rep["agnostic"] = run_agnostic(secs, ids, args.offsets, args.replicates, args.cap, args.seed, not args.no_packets)
    if args.command in ("bytes", "all"):
        rep["bytes"] = run_bytes(secs, ids, args.reps, args.cap, args.seed)
    if args.command in ("numbers", "all"):
        rep["numbers"] = run_numbers(secs, ids, args.reps, args.cap, args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "diagnostics_views.json").write_text(json.dumps(_jsonable(rep), indent=1, sort_keys=True, default=str) + "\n",
                                                encoding="utf-8")
    md = to_markdown(rep)
    (out / "diagnostics_views.md").write_text(md + "\n", encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Cicada identifiers as keys: PGP key ID 7A35090F and friends as autokey primers or repeating keys.

    python -m lpswarm.research_primers --out reports/diag

No models, no oracle thresholds; exploratory. For each identifier string, a few conventions turn it into numbers mod 29, and each is tried as

  * a plaintext autokey (key = the plaintext m symbols back, primer = the identifier), and
  * a repeating key (a Vigenere with the identifier as the key),

with combine sub / add / beaufort, identity or reversed alphabet map, and with or without F kept literal (skip). Each decryption of a
section of 300+ runes is scored by the mean English bigram log-likelihood; the best over all candidates is compared with the best over
the same candidates applied to the section's runes shuffled (the multiple-comparison null). A planted control (English encrypted with one
candidate) must come out on top. A ciphertext autokey ignores the primer after its first m symbols, so it is not part of this test.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

N = 29
SEED = 20261112
MIN_SECTION = 300
# The key ID is the issuer of the PGP signatures in the OutGuess payloads of pages 00-03 (long ID 181F01E57A35090F).
STRINGS = ("7A35090F", "181F01E57A35090F", "845145127", "3301", "CICADA", "CICADA3301", "CICADA3301845145127")
HEX = set("0123456789ABCDEF")


def conventions(s: str, alpha) -> dict[str, list[int]]:
    """Ways of turning a string into key numbers mod 29."""
    out: dict[str, list[int]] = {}
    out["base36"] = [(int(ch, 36)) % N for ch in s]
    out["ascii"] = [ord(ch) % N for ch in s]
    out["position"] = [(int(ch) if ch.isdigit() else ord(ch) - 65) % N for ch in s]
    gem = []
    for ch in s:
        e = [] if ch.isdigit() else list(alpha.encode(ch))
        gem.append(int(ch) if ch.isdigit() else int(e[0]) % N if e else ord(ch) % N)
    out["gematria"] = gem
    if set(s) <= HEX and len(s) % 2 == 0:
        out["hex bytes"] = [int(s[i:i + 2], 16) % N for i in range(0, len(s), 2)]
    if set(s) <= HEX:
        out["number"] = [int(s, 16) % N if not s.isdigit() else int(s) % N]
    return out


def candidate_keys(alpha) -> list[tuple[str, tuple[int, ...]]]:
    seen: dict[tuple[int, ...], str] = {}
    for s in STRINGS:
        for name, key in conventions(s, alpha).items():
            for rev in (False, True):
                k = tuple(key[::-1] if rev else key)
                seen.setdefault(k, f"{s}{' reversed' if rev else ''} / {name}")
    return [(label, k) for k, label in seen.items()]


def decrypt(c: np.ndarray, key: tuple[int, ...], kind: str, how: str, rmap: bool, skip_f: bool) -> np.ndarray:
    """Plaintext autokey or repeating key; same conventions as programs.spec (sub: c-k, add: c+k, beaufort: k-c)."""
    c = np.asarray(c, dtype=np.int64)
    lit = (c == 0) if skip_f else np.zeros(len(c), dtype=bool)
    w = c[~lit]
    if rmap:
        w = (N - 1) - w
    m = len(key)
    if kind == "repeat":
        k = np.resize(np.array(key, dtype=np.int64), len(w))
        p = {"sub": w - k, "add": w + k, "beaufort": k - w}[how] % N
    else:
        buf = list(key) + [0] * len(w)           # key stream = primer, then the plaintext so far
        wl = w.tolist()
        for i, ci in enumerate(wl):
            k = buf[i]
            buf[m + i] = (ci - k if how == "sub" else ci + k if how == "add" else k - ci) % N
        p = np.array(buf[m:], dtype=np.int64)
    out = c.copy()
    out[~lit] = p
    return out


def encrypt(p: np.ndarray, key: tuple[int, ...], kind: str, how: str, rmap: bool, skip_f: bool) -> np.ndarray:
    """Inverse of decrypt (planted control)."""
    p = np.asarray(p, dtype=np.int64)
    lit = (p == 0) if skip_f else np.zeros(len(p), dtype=bool)
    w = p[~lit]
    m = len(key)
    if kind == "repeat":
        k = np.resize(np.array(key, dtype=np.int64), len(w))
        c = {"sub": w + k, "add": w - k, "beaufort": k - w}[how] % N
    else:
        pl = list(key) + w.tolist()
        c = np.array([{"sub": pl[m + i] + pl[i], "add": pl[m + i] - pl[i], "beaufort": pl[i] - pl[m + i]}[how] % N
                      for i in range(len(w))], dtype=np.int64)
    if rmap:
        c = (N - 1) - c
    out = p.copy()
    out[~lit] = c
    return out


GRID = [(kind, how, rmap, skip) for kind in ("autokey", "repeat") for how in ("sub", "add", "beaufort")
        for rmap in (False, True) for skip in (False, True)]


def score(x: np.ndarray, big: np.ndarray) -> float:
    return float(big[x[:-1], x[1:]].mean())


def best_over_candidates(c: np.ndarray, keys, big: np.ndarray) -> tuple[float, str]:
    best, label = -1e9, ""
    for lab, key in keys:
        for kind, how, rmap, skip in GRID:
            s = score(decrypt(c, key, kind, how, rmap, skip), big)
            if s > best:
                best, label = s, f"{lab} | {kind} {how} map={'reverse' if rmap else 'identity'} F={'literal' if skip else 'keyed'}"
    return best, label


def run(secs: dict, keys, big, shuffles: int, seed: int = SEED) -> list[dict]:
    rng = np.random.default_rng(seed)
    rows = []
    for i in sorted(secs):
        c = secs[i]["ct"]
        if len(c) < MIN_SECTION:
            continue
        obs, label = best_over_candidates(c, keys, big)
        null = np.array([best_over_candidates(rng.permutation(c), keys, big)[0] for _ in range(shuffles)])
        rows.append({"section": i, "runes": int(len(c)), "best": obs, "label": label, "null_mean": float(null.mean()),
                     "null_max": float(null.max()), "p": (1 + int((null >= obs).sum())) / (shuffles + 1)})
    return rows


def control(alpha, big, keys, seed: int = SEED) -> dict:
    """English window encrypted with 7A35090F / base36 as a plaintext autokey: is it the best candidate?"""
    from lpswarm import research_signature as S
    win = np.asarray(S.english_windows(alpha, n_windows=1, length=600, seed=seed)[0][0], dtype=np.int64)
    key = next(k for lab, k in keys if lab == "7A35090F / base36")
    c = encrypt(win, key, "autokey", "sub", False, False)
    best, label = best_over_candidates(c, keys, big)
    truth = score(decrypt(c, key, "autokey", "sub", False, False), big)
    return {"best": best, "label": label, "truth": truth, "found": abs(best - truth) < 1e-9,
            "roundtrip": bool((decrypt(c, key, "autokey", "sub", False, False) == win).all())}


def main(argv: list[str] | None = None) -> int:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.research_packets import ALPHABET, load_sections
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_primers", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="reports/diag")
    ap.add_argument("--shuffles", type=int, default=40)
    args = ap.parse_args(argv)
    alpha = get_alphabet(ALPHABET)
    big = FullOracle(alpha, OracleConfig(null_samples=300)).bigram_table()
    keys = candidate_keys(alpha)
    secs = load_sections(indexes=list(range(10, 26)))
    ctl = control(alpha, big, keys)
    rows = run(secs, keys, big, args.shuffles)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "primers.json").write_text(json.dumps({"candidates": len(keys) * len(GRID), "control": ctl, "rows": rows}, indent=1, default=str) + "\n",
                                      encoding="utf-8")
    L = ["# Cicada identifiers as autokey primers and repeating keys", "", "**EXPLORATORY; no models.**", "",
         f"{len(keys)} distinct key lists from {len(STRINGS)} strings (key ID, long ID, 845145127, 3301, CICADA ...), each forward and reversed, x {len(GRID)} "
         f"cipher settings = {len(keys) * len(GRID)} candidates per section. Score: mean English bigram log-likelihood of the decryption; the null is the best "
         f"candidate on the section shuffled ({args.shuffles} times).", "",
         f"Planted control (English, autokey, primer 7A35090F / base36): round trip {ctl['roundtrip']}, best candidate is the planted one: {ctl['found']} "
         f"(score {ctl['best']:.3f}).", "",
         "| section | runes | best | null mean | null max | p | best candidate |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        L.append(f"| {r['section']} | {r['runes']} | {r['best']:.3f} | {r['null_mean']:.3f} | {r['null_max']:.3f} | {r['p']:.3f} | {r['label']} |")
    flagged = [r for r in rows if r["p"] <= 1 / (args.shuffles + 1) + 1e-9]
    L += ["", f"Sections with the best candidate above every shuffle: {len(flagged)} of {len(rows)} (expected about {len(rows) / (args.shuffles + 1):.1f} by chance)."]
    (out / "primers.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Fibonacci keys that restart (page 32's table is the Fibonacci sequence as prime indices; see docs/community_state.md).

    python -m lpswarm.research_fibpage --out reports/diag

No models; exploratory. Fibonacci numbers mod 29 repeat with period 14, so an unbroken Fibonacci key is a period-14 repeating key, which the period scan
(research_structure) already excludes. What that scan cannot see is a key that RESTARTS: at each page, line or word, or whose phase depends on the page number.
Families, each with sub / add / beaufort, identity or reversed alphabet, F kept literal or keyed (a literal F neither advances the key nor is scored),
scales 1..28 and the 29 constant shifts of the result:

  continuous      key[t] = s * Fib[t + k]                       (baseline: the same as the period-14 scan)
  restart_page    key restarts at 0 on every page               (phase k = 0..13)
  restart_line    ... on every line
  restart_word    ... on every word
  page_constant   one shift per page: s * Fib[page + o]         (o = 0..13; numbering offsets are covered by o)
  page_phase      key[t] = s * Fib[t_in_page + page + o]

Score: mean English bigram log-likelihood of the decryption (pairs inside one page, never touching a literal F). Null: the same search on each page's runes
shuffled within the page; the statistic is the best candidate. Two bodies: pages after image 32 (the table's page) and all pages 17-72. A planted control
(English text over the real page structure encrypted by one restart candidate) must be recovered.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

N = 29
SEED = 20261112
MIN_PAGE = 100
FIB14 = np.array([0, 1], dtype=np.int64)
while len(FIB14) < 14:
    FIB14 = np.append(FIB14, (FIB14[-1] + FIB14[-2]) % N)
SCALES = np.arange(1, N)


def load_body(path: str = "data/lp_derived/lp2_runes.csv", first_page: int = 17) -> dict:
    rows = sorted(csv.DictReader(open(path, encoding="utf-8")), key=lambda r: int(r["global"]))
    pages: dict[int, list] = {}
    for r in rows:
        pages.setdefault(int(r["page"]), []).append(r)
    runes, page, line_start, word_start, page_start = [], [], [], [], []
    for p in sorted(pages):
        rs = pages[p]
        if p < first_page or len(rs) < MIN_PAGE:
            continue
        for i, r in enumerate(rs):
            runes.append(int(r["rune"]))
            page.append(p)
            page_start.append(i == 0)
            line_start.append(i == 0 or r["line"] != rs[i - 1]["line"])
            word_start.append(i == 0 or rs[i - 1]["sep"] != "none" or r["line"] != rs[i - 1]["line"])
    return {"c": np.array(runes), "page": np.array(page), "page_start": np.array(page_start), "line_start": np.array(line_start),
            "word_start": np.array(word_start)}


def _unit_index(starts: np.ndarray, lit: np.ndarray | None) -> np.ndarray:
    """Position within the unit, counting only non-literal symbols; a literal F gets the index of the next symbol (it is not scored)."""
    keep = np.ones(len(starts), dtype=np.int64) if lit is None else (~lit).astype(np.int64)
    cs = np.cumsum(keep)
    before = cs - keep
    idx_start = np.maximum.accumulate(np.where(starts, np.arange(len(starts)), 0))
    return before - before[idx_start]


def rolled_bigram(big: np.ndarray) -> np.ndarray:
    a = np.arange(N)
    return big[(a[:, None, None] + a[None, :, None]) % N, (a[:, None, None] + a[None, None, :]) % N]      # [shift, x, y]


def candidates():
    """(family, unit, k) triples; the other settings are looped over inside `score_all`."""
    out = [("continuous", "none", k) for k in range(14)]
    out += [("restart", u, k) for u in ("page", "line", "word") for k in range(14)]
    out += [("page_constant", "page", o) for o in range(14)] + [("page_phase", "page", o) for o in range(14)]
    return out


def decrypt_batch(c, key, how, rmap):
    """key: (S, n); returns (S, n) plaintext (before the constant shift)."""
    w = ((N - 1) - c) if rmap else c
    return {"sub": w[None, :] - key, "add": w[None, :] + key, "beaufort": key - w[None, :]}[how] % N


def score_all(body: dict, c: np.ndarray, B: np.ndarray, want_label: bool = True):
    """Best score over every candidate for ciphertext `c` laid out like `body`; returns (score, label)."""
    n = len(c)
    page = body["page"]
    same_page = page[1:] == page[:-1]
    best, label = -1e9, ""
    for skip in (False, True):
        lit = (c == 0) if skip else None
        valid = same_page if lit is None else same_page & ~lit[1:] & ~lit[:-1]
        nv = max(int(valid.sum()), 1)
        starts = {"none": np.arange(n) == 0, "page": body["page_start"], "line": body["line_start"], "word": body["word_start"]}
        idx_cache = {u: _unit_index(s, lit) for u, s in starts.items()}
        for fam, unit, k in candidates():
            idx = idx_cache[unit]
            if fam == "page_constant":
                ph = np.full(n, 0, dtype=np.int64) + (page + k)
            elif fam == "page_phase":
                ph = idx + page + k
            else:
                ph = idx + k
            base = FIB14[ph % 14]
            key = SCALES[:, None] * base[None, :] % N
            for how in ("sub", "add", "beaufort"):
                for rmap in (False, True):
                    P = decrypt_batch(c, key, how, rmap)
                    x, y = P[:, :-1], P[:, 1:]
                    flat = np.where(valid[None, :], np.arange(len(SCALES))[:, None] * (N * N) + x * N + y, len(SCALES) * N * N)
                    cnt = np.bincount(flat.ravel(), minlength=len(SCALES) * N * N + 1)[:-1].reshape(len(SCALES), N, N)
                    sc = np.einsum("sxy,axy->sa", cnt, B) / nv
                    j = int(sc.argmax())
                    if sc.flat[j] > best:
                        s_i, a_i = divmod(j, N)
                        best = float(sc.flat[j])
                        if want_label:
                            label = (f"{fam} unit={unit} k={k} scale={SCALES[s_i]} shift={a_i} {how} map={'reverse' if rmap else 'identity'} "
                                     f"F={'literal' if skip else 'keyed'}")
    return best, label


def shuffle_pages(c: np.ndarray, page: np.ndarray, rng) -> np.ndarray:
    out = c.copy()
    for p in np.unique(page):
        m = np.where(page == p)[0]
        out[m] = rng.permutation(c[m])
    return out


def encrypt_restart(plain: np.ndarray, body: dict, unit: str, k: int, scale: int, how: str = "sub") -> np.ndarray:
    n = len(plain)
    starts = {"page": body["page_start"], "line": body["line_start"], "word": body["word_start"]}[unit]
    idx = _unit_index(starts, None)
    key = scale * FIB14[(idx + k) % 14] % N
    return {"sub": plain + key, "add": plain - key, "beaufort": key - plain}[how] % N


def run_body(name: str, body: dict, big: np.ndarray, shuffles: int, seed: int = SEED) -> dict:
    B = rolled_bigram(big)
    obs, label = score_all(body, body["c"], B)
    rng = np.random.default_rng(seed)
    null = np.array([score_all(body, shuffle_pages(body["c"], body["page"], rng), B, want_label=False)[0] for _ in range(shuffles)])
    return {"body": name, "runes": int(len(body["c"])), "pages": int(len(np.unique(body["page"]))), "best": obs, "label": label, "null_mean": float(null.mean()),
            "null_max": float(null.max()), "p": float((1 + (null >= obs).sum()) / (shuffles + 1)), "shuffles": shuffles}


def control(body: dict, big: np.ndarray, alpha, seed: int = SEED) -> dict:
    from lpswarm import research_signature as S
    n = len(body["c"])
    win = np.asarray(S.english_windows(alpha, n_windows=1, length=n, seed=seed)[0][0], dtype=np.int64)
    out = {}
    B = rolled_bigram(big)
    for unit, k, scale in (("page", 3, 5), ("line", 7, 11), ("word", 2, 3)):
        c = encrypt_restart(win, body, unit, k, scale)
        best, label = score_all(body, c, B)
        out[unit] = {"planted": f"restart unit={unit} k={k} scale={scale} shift=0 sub", "best": best, "found": label}
    return out


def main(argv: list[str] | None = None) -> int:
    from lpswarm.alphabet import get_alphabet
    from lpswarm.oracle import FullOracle, OracleConfig
    from lpswarm.research_packets import ALPHABET
    ap = argparse.ArgumentParser(prog="python -m lpswarm.research_fibpage", description=__doc__.split("\n")[0])
    ap.add_argument("--out", default="reports/diag")
    ap.add_argument("--shuffles", type=int, default=40)
    args = ap.parse_args(argv)
    alpha = get_alphabet(ALPHABET)
    big = FullOracle(alpha, OracleConfig(null_samples=300)).bigram_table()
    after = load_body(first_page=33)
    allp = load_body(first_page=17)
    ctl = control(after, big, alpha)
    rows = [run_body("pages 33-72 (after the table)", after, big, args.shuffles), run_body("pages 17-72", allp, big, args.shuffles)]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "fibpage.json").write_text(json.dumps({"control": ctl, "rows": rows}, indent=1, default=str) + "\n", encoding="utf-8")
    L = ["# Fibonacci keys that restart (page, line, word) or depend on the page number", "", "**EXPLORATORY; no models.**", "",
         "Planted control (English over the real page structure, encrypted by one restart candidate): " +
         "; ".join(f"{u}: best {v['best']:.3f} found `{v['found']}`" for u, v in ctl.items()), "",
         "| body | runes | pages | best | null mean | null max | p | best candidate |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        L.append(f"| {r['body']} | {r['runes']} | {r['pages']} | {r['best']:.4f} | {r['null_mean']:.4f} | {r['null_max']:.4f} | {r['p']:.3f} | {r['label']} |")
    (out / "fibpage.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

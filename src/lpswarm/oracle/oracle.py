"""Null-calibrated scoring oracle.

Question answered: is this candidate plaintext distinguishable from noise at
a known false-positive rate?

Pipeline for one candidate of length L:
  1. Screen (cheap): bigram log-likelihood per symbol. Must exceed the
     null quantile at 1 - screen_alpha. Failing candidates stop here.
  2. Full: combined = ngram (order `order`) log-lik per symbol
                      + dict_weight * dictionary coverage,
     maximised over configured languages. IC and an optional LM score are
     recorded as evidence but do not enter the decision.
  3. Decision: combined >= T(L, alpha_eff), where alpha_eff = alpha / N
     (Bonferroni over N = attempts against this target so far, including this
     one) and T is the max over null types of each type's upper quantile.
     If alpha_eff is too small for the empirical null sample to resolve, the
     upper tail is extrapolated with an exponential (peaks-over-threshold) fit.

Null types per length: shuffled good text, uniform random symbols, and
wrong-key decryptions of good text under the configured cipher families.
Calibration is cached per exact length.

Two APIs:
  - FullOracle.score(): every signal, percentile and threshold (harness use).
  - CoarseOracle.judge(): 'fail' / 'near_miss' / 'pass' only (for future
    generators). It never returns signal values or thresholds.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Sequence

import numpy as np

from lpswarm.alphabet import Alphabet
from lpswarm.ciphers import get_family
from lpswarm.oracle.signals import Dictionary, LMScorer, NgramModel, index_of_coincidence
from lpswarm.textgen import corpus

NULL_TYPES = ("shuffled", "random", "wrong_key")
FAIL, NEAR_MISS, PASS = "fail", "near_miss", "pass"


@dataclass
class OracleConfig:
    alpha: float = 0.01                 # target false-positive rate per attempt, before adjustment
    screen_alpha: float = 0.5           # fraction of nulls allowed past the cheap screen
    order: int = 4                      # n-gram order for the full scorer
    smoothing: float = 0.5              # add-k
    dict_weight: float = 1.0
    dict_min_len: int = 3
    dict_max_len: int = 12
    dict_size: int = 5000
    null_samples: int = 3000            # per null type per length (>= ~30 exceedances at alpha=0.01)
    null_types: tuple[str, ...] = NULL_TYPES
    wrong_key_families: tuple[str, ...] = ("caesar", "vigenere", "autokey", "substitution",
                                           "columnar")
    tail_fraction: float = 0.1          # top fraction used for exponential tail fit
    min_tail_exceedances: int = 10      # below alpha_eff * M < this, use the tail fit
    multiple_comparisons: str = "bonferroni"   # or "none"
    languages: tuple[str, ...] = ("english",)
    seed: int = 0


@dataclass
class ScoreReport:
    length: int
    stage: str                       # "screen" or "full"
    verdict: str
    passed: bool
    screen_score: float
    screen_threshold: float
    ic: float | None = None
    ngram_score: float | None = None
    dict_score: float | None = None
    lm_loglik: float | None = None
    combined: float | None = None
    language: str | None = None
    threshold: float | None = None
    threshold_unadjusted: float | None = None
    null_percentile: float | None = None
    percentiles: dict = field(default_factory=dict)
    attempt_count: int = 1
    alpha_eff: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class _NullSet:
    screen: dict[str, np.ndarray]     # per type, sorted
    combined: dict[str, np.ndarray]   # per type, sorted
    pooled: dict[str, np.ndarray]     # signal name -> sorted pooled values
    screen_threshold: float


class FullOracle:
    def __init__(self, alphabet: Alphabet, config: OracleConfig | None = None,
                 lm_scorer: LMScorer | None = None,
                 training_texts: dict[str, str] | None = None):
        self.alphabet = alphabet
        self.cfg = config or OracleConfig()
        self.lm_scorer = lm_scorer
        n = alphabet.size
        self._good: dict[str, np.ndarray] = {}
        self._models: dict[str, tuple[NgramModel, NgramModel, Dictionary]] = {}
        self._words: list[np.ndarray] = []
        for lang in self.cfg.languages:
            text = (training_texts or {}).get(lang) or corpus.training_text(lang)
            arr = alphabet.encode(text)
            if len(arr) < 1000:
                raise ValueError(f"training text for {lang} too short after encoding")
            self._good[lang] = arr
            screen = NgramModel.train(arr, n, 2, self.cfg.smoothing, f"{lang}-2")
            full = NgramModel.train(arr, n, self.cfg.order, self.cfg.smoothing,
                                    f"{lang}-{self.cfg.order}")
            words = [alphabet.encode(w) for w in
                     corpus.wordlist(lang, min_len=self.cfg.dict_min_len, limit=self.cfg.dict_size)]
            self._words.extend(w for w in words if len(w) >= self.cfg.dict_min_len)
            self._models[lang] = (screen, full, Dictionary(words, self.cfg.dict_min_len,
                                                          self.cfg.dict_max_len))
        self._cache: dict[int, _NullSet] = {}

    # ------------------------------------------------------------ raw signals
    def _screen(self, arr: np.ndarray) -> float:
        return max(m[0].score(arr) for m in self._models.values())

    def _full(self, arr: np.ndarray) -> tuple[float, str, float, float]:
        best = None
        for lang, (_, full, dic) in self._models.items():
            ng = full.score(arr)
            dc = dic.coverage(arr)
            comb = ng + self.cfg.dict_weight * dc
            if best is None or comb > best[0]:
                best = (comb, lang, ng, dc)
        return best  # type: ignore[return-value]

    # ------------------------------------------------------------ null model
    def _null_samples(self, length: int, kind: str, rng: np.random.Generator) -> list[np.ndarray]:
        n = self.alphabet.size
        M = self.cfg.null_samples
        langs = list(self._good)
        out = []
        fams = [get_family(f) for f in self.cfg.wrong_key_families]
        for i in range(M):
            if kind == "random":
                out.append(rng.integers(0, n, size=length).astype(np.int16))
                continue
            good = self._good[langs[i % len(langs)]]
            start = int(rng.integers(0, len(good) - length))
            pt = good[start:start + length]
            if kind == "shuffled":
                out.append(rng.permutation(pt))
            elif kind == "wrong_key":
                fam = fams[i % len(fams)]
                k1 = fam.random_key(rng, n, "medium", words=self._words, length=length)
                p1 = fam.random_params(rng, length, k1)
                ct = fam.encrypt(pt, k1, n, **p1)
                for _ in range(20):
                    k2 = fam.random_key(rng, n, "medium", words=self._words, length=length)
                    if fam.key_json(k2) != fam.key_json(k1):
                        break
                cand = fam.decrypt(ct, k2, n, **p1)
                out.append(cand)
            else:
                raise ValueError(f"unknown null type {kind}")
        return out

    def calibrate(self, length: int) -> _NullSet:
        if length in self._cache:
            return self._cache[length]
        if length < max(2, self.cfg.order):
            raise ValueError(f"length {length} too short to score (order {self.cfg.order})")
        rng = np.random.default_rng([self.cfg.seed, length, 0xCA11])
        screen: dict[str, np.ndarray] = {}
        combined: dict[str, np.ndarray] = {}
        pooled: dict[str, list[float]] = {"screen": [], "ic": [], "ngram": [], "dict": [],
                                          "combined": []}
        n = self.alphabet.size
        for kind in self.cfg.null_types:
            sc, cb = [], []
            for arr in self._null_samples(length, kind, rng):
                s = self._screen(arr)
                c, _, ng, dc = self._full(arr)
                sc.append(s)
                cb.append(c)
                pooled["screen"].append(s)
                pooled["ic"].append(index_of_coincidence(arr, n))
                pooled["ngram"].append(ng)
                pooled["dict"].append(dc)
                pooled["combined"].append(c)
            screen[kind] = np.sort(np.asarray(sc))
            combined[kind] = np.sort(np.asarray(cb))
        q = 1.0 - self.cfg.screen_alpha
        screen_thr = max(float(np.quantile(v, q)) for v in screen.values())
        ns = _NullSet(screen, combined, {k: np.sort(np.asarray(v)) for k, v in pooled.items()},
                      screen_thr)
        self._cache[length] = ns
        return ns

    # ------------------------------------------------------------- thresholds
    def _upper_quantile(self, sorted_vals: np.ndarray, a: float) -> float:
        M = len(sorted_vals)
        if a * M >= self.cfg.min_tail_exceedances:
            return float(np.quantile(sorted_vals, 1.0 - a, method="higher"))
        # Exponential tail fit over the top `tail_fraction` of samples.
        tf = self.cfg.tail_fraction
        k = max(10, int(M * tf))
        tail = sorted_vals[-k:]
        u = float(sorted_vals[-k - 1]) if M > k else float(tail[0])
        beta = max(float((tail - u).mean()), 1e-9)
        p_u = k / M
        x = u + beta * math.log(p_u / a)
        return max(x, float(sorted_vals[-1]))

    def alpha_eff(self, attempt_count: int) -> float:
        if self.cfg.multiple_comparisons == "none":
            return self.cfg.alpha
        return self.cfg.alpha / max(1, int(attempt_count))

    def threshold(self, length: int, attempt_count: int = 1) -> float:
        ns = self.calibrate(length)
        a = self.alpha_eff(attempt_count)
        return max(self._upper_quantile(v, a) for v in ns.combined.values())

    # ------------------------------------------------------------------ score
    def score(self, arr: np.ndarray, attempt_count: int = 1) -> ScoreReport:
        arr = np.asarray(arr, dtype=np.int16)
        L = len(arr)
        ns = self.calibrate(L)
        s = self._screen(arr)
        a_eff = self.alpha_eff(attempt_count)
        if s < ns.screen_threshold:
            return ScoreReport(L, "screen", FAIL, False, s, ns.screen_threshold,
                               attempt_count=attempt_count, alpha_eff=a_eff)
        comb, lang, ng, dc = self._full(arr)
        ic = index_of_coincidence(arr, self.alphabet.size)
        lm = None
        if self.lm_scorer is not None:
            lm = float(self.lm_scorer(self.alphabet.decode(arr)))
        thr = max(self._upper_quantile(v, a_eff) for v in ns.combined.values())
        thr0 = max(self._upper_quantile(v, self.cfg.alpha) for v in ns.combined.values())
        pct = {k: float(np.searchsorted(v, x, side="right") / len(v))
               for k, v, x in (("ic", ns.pooled["ic"], ic), ("ngram", ns.pooled["ngram"], ng),
                               ("dict", ns.pooled["dict"], dc), ("screen", ns.pooled["screen"], s))}
        for kind, v in ns.combined.items():
            pct[f"combined_vs_{kind}"] = float(np.searchsorted(v, comb, side="right") / len(v))
        null_pct = float(np.searchsorted(ns.pooled["combined"], comb, side="right")
                         / len(ns.pooled["combined"]))
        if comb >= thr:
            verdict = PASS
        elif comb >= thr0:
            verdict = NEAR_MISS
        else:
            verdict = FAIL
        return ScoreReport(L, "full", verdict, verdict == PASS, s, ns.screen_threshold, ic, ng, dc,
                           lm, comb, lang, thr, thr0, null_pct, pct, attempt_count, a_eff)


class CoarseOracle:
    """Generator-facing API: verdict only. Holds the full oracle privately."""

    def __init__(self, full: FullOracle):
        self.__full = full

    def judge(self, arr: np.ndarray, attempt_count: int = 1) -> str:
        return self.__full.score(arr, attempt_count).verdict


def fpr_tolerance(alpha: float, n_test: int, n_calib: int, sigmas: float = 3.0) -> float:
    """Stated tolerance: `sigmas` binomial standard errors, counting both the test
    sample and the finite calibration sample the threshold was estimated from."""
    return sigmas * math.sqrt(alpha * (1 - alpha) * (1.0 / n_test + 1.0 / n_calib))


def null_fpr_check(oracle: FullOracle, lengths: Sequence[int], samples: int = 2000,
                   seed: int = 12345) -> dict:
    """Measure false-positive rate on *fresh* nulls (different seed from calibration)
    at the unadjusted alpha (attempt_count=1).

    Because the threshold is the max over null types, each type's FPR should be
    <= alpha + tol, and the worst type's FPR should be within +/- tol of alpha.
    Returns {"rows": per (length, type), "summary": per length}.
    """
    rows, summary = [], []
    cfg = oracle.cfg
    for L in lengths:
        oracle.calibrate(L)
        rng = np.random.default_rng([seed, L, 0xF00D])
        saved = cfg.null_samples
        cfg.null_samples = samples
        tol = fpr_tolerance(cfg.alpha, samples, saved)
        worst = 0.0
        ok_all = True
        try:
            for kind in cfg.null_types:
                arrs = oracle._null_samples(L, kind, rng)
                hits = sum(1 for arr in arrs if oracle.score(arr, attempt_count=1).passed)
                fpr = hits / len(arrs)
                lo, hi = wilson(hits, len(arrs))
                ok = fpr <= cfg.alpha + tol
                ok_all &= ok
                worst = max(worst, fpr)
                rows.append({"length": L, "null_type": kind, "n": len(arrs), "false_pos": hits,
                             "fpr": fpr, "ci_lo": lo, "ci_hi": hi, "alpha": cfg.alpha,
                             "tolerance": tol, "not_anticonservative": ok})
        finally:
            cfg.null_samples = saved
        summary.append({"length": L, "alpha": cfg.alpha, "worst_type_fpr": worst, "tolerance": tol,
                        "within_tolerance": ok_all and abs(worst - cfg.alpha) <= tol})
    return {"rows": rows, "summary": summary}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)

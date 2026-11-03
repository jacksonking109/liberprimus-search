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
import warnings
from dataclasses import asdict, dataclass, field
from typing import Sequence

import numpy as np

from lpswarm.alphabet import Alphabet, word_spans
from lpswarm.ciphers import get_family
from lpswarm.oracle.signals import Dictionary, LMScorer, NgramModel, index_of_coincidence
from lpswarm.textgen import corpus

NULL_TYPES = ("shuffled", "random", "wrong_key")
NEAR_SOLUTION = 0.5   # 4-gram overlap with the true plaintext above which a decryption is "near"


def gram_overlap(cand: np.ndarray, truth: np.ndarray, k: int = 4) -> float:
    """Fraction of distinct k-grams of `cand` that also occur in `truth`."""
    if len(cand) < k or len(truth) < k:
        return float(np.array_equal(cand, truth))
    from numpy.lib.stride_tricks import sliding_window_view
    wc = sliding_window_view(np.asarray(cand, dtype=np.int64), k)
    wt = sliding_window_view(np.asarray(truth, dtype=np.int64), k)
    base = 1 << 15
    w = base ** np.arange(k - 1, -1, -1, dtype=np.int64)
    gc = np.unique(wc @ w)
    gt = wt @ w
    return float(np.isin(gc, gt).mean())
FAIL, NEAR_MISS, PASS = "fail", "near_miss", "pass"


@dataclass
class OracleConfig:
    alpha: float = 0.01                 # target false-positive rate per attempt, before adjustment
    screen_alpha: float = 0.5           # fraction of nulls allowed past the cheap screen
    order: int = 4                      # n-gram order for the full scorer
    smoothing: float = 0.5              # add-k
    dict_weight: float = 1.0
    word_weight: float = 1.0            # weight of the word-break signal (used only with breaks)
    word_min_words: int = 3             # fewer words than this: breaks are ignored
    variant_null_samples: int = 1000    # per null type, for search-optimised decryptions
    dict_min_len: int = 3
    dict_max_len: int = 12
    dict_size: int = 5000
    null_samples: int = 3000            # per null type per length (>= ~30 exceedances at alpha=0.01)
    null_types: tuple[str, ...] = NULL_TYPES
    wrong_key_families: tuple[str, ...] = ("caesar", "vigenere", "autokey", "substitution",
                                           "columnar")
    tail_fraction: float = 0.1          # top fraction used for exponential tail fit
    min_tail_exceedances: int = 10      # below alpha_eff * M < this, use the tail fit
    multiple_comparisons: str = "bonferroni"   # "bonferroni" | "spending" | "none" (see module doc)
    languages: tuple[str, ...] = ("english",)
    max_table_size: int = 20_000_000    # n-gram order is lowered until N**order fits
    max_score_length: int = 500         # longer candidates are scored on their first N symbols
    seed: int = 0

    def __post_init__(self) -> None:
        def bad(msg: str) -> None:
            raise ValueError(f"OracleConfig: {msg}")
        if not 0.0 < self.alpha < 1.0:
            bad(f"alpha must be in (0, 1), got {self.alpha}")
        if not 0.0 < self.screen_alpha <= 1.0:
            bad(f"screen_alpha must be in (0, 1], got {self.screen_alpha}")
        if self.order < 1:
            bad("order must be >= 1")
        if self.smoothing <= 0:
            bad("smoothing must be > 0")
        if self.variant_null_samples < 100:
            bad("variant_null_samples must be >= 100")
        if self.null_samples < 100:
            bad(f"null_samples must be >= 100, got {self.null_samples}")
        if not 1 <= self.dict_min_len <= self.dict_max_len:
            bad("need 1 <= dict_min_len <= dict_max_len")
        if not 0.0 < self.tail_fraction < 1.0:
            bad("tail_fraction must be in (0, 1)")
        if self.multiple_comparisons not in ("bonferroni", "spending", "none"):
            bad(f"unknown multiple_comparisons {self.multiple_comparisons!r}")
        unknown = set(self.null_types) - set(NULL_TYPES)
        if unknown or not self.null_types:
            bad(f"null_types must be a non-empty subset of {NULL_TYPES}")
        if not self.languages:
            bad("at least one language is required")
        if self.max_score_length < 8:
            bad("max_score_length must be >= 8")
        self.null_types = tuple(self.null_types)
        self.wrong_key_families = tuple(self.wrong_key_families)
        self.languages = tuple(self.languages)
        if "wrong_key" in self.null_types and not self.wrong_key_families:
            bad("wrong_key nulls need at least one family")
        for f in self.wrong_key_families:
            get_family(f)  # raises on unknown names


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
    unreachable: bool = False         # threshold above the best score any text could get
    word_score: float | None = None   # share of symbols in dictionary words, given word breaks
    null_variant: str | None = None   # which null calibration judged this (e.g. skip resolution)

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
        if n < 2:
            raise ValueError("the oracle needs an alphabet of at least 2 symbols")
        # Lower the n-gram order for big alphabets so the table fits in memory.
        order = self.cfg.order
        while order > 1 and n ** order > self.cfg.max_table_size:
            order -= 1
        if order != self.cfg.order:
            warnings.warn(f"alphabet size {n}: n-gram order lowered from {self.cfg.order} to "
                          f"{order} to keep the table under {self.cfg.max_table_size} entries",
                          stacklevel=2)
        self.order = order
        screen_order = min(2, order)
        self._good: dict[str, np.ndarray] = {}
        self._models: dict[str, tuple[NgramModel, NgramModel, Dictionary]] = {}
        self._words: list[np.ndarray] = []
        self._lexicons: dict[str, set[str]] = {}
        self._max_combined = -math.inf
        supplied = training_texts or {}
        self.training_sources: dict[str, list[str]] = {}
        for lang in self.cfg.languages:
            if supplied.get(lang):
                text = supplied[lang]
                self.training_sources[lang] = ["<supplied text>"]
                vocab = corpus.wordlist_from_text(text, min_len=self.cfg.dict_min_len,
                                                  limit=self.cfg.dict_size)
            else:
                text = corpus.training_text(lang)
                self.training_sources[lang] = corpus.training_sources(lang)
                vocab = corpus.wordlist(lang, min_len=self.cfg.dict_min_len,
                                        limit=self.cfg.dict_size)
            arr = alphabet.encode(text)
            if len(arr) < 1000:
                raise ValueError(f"training text for {lang} has only {len(arr)} symbols under "
                                 f"alphabet {alphabet.name}; need >= 1000 (check the alphabet "
                                 "tokens cover the corpus letters)")
            self._good[lang] = arr
            screen = NgramModel.train(arr, n, screen_order, self.cfg.smoothing, f"{lang}-{screen_order}")
            full = NgramModel.train(arr, n, order, self.cfg.smoothing, f"{lang}-{order}")
            words = [w for w in (alphabet.encode(v) for v in vocab)
                     if len(w) >= self.cfg.dict_min_len]
            self._words.extend(words)
            self._models[lang] = (screen, full, Dictionary(words, self.cfg.dict_min_len,
                                                          self.cfg.dict_max_len))
            # Word lexicon for the word-break signal, in the alphabet's canonical spelling
            # (encode then decode), so digraph choices and aliases compare equal.
            lex_src = (corpus.wordlist_from_text(text, min_len=1, min_count=2)
                       if supplied.get(lang) else corpus.wordlist(lang, min_len=1, min_count=2))
            self._lexicons[lang] = {alphabet.decode(e) for e in (alphabet.encode(w) for w in lex_src)
                                    if len(e)}
            self._max_combined = max(self._max_combined,
                                     float(full.logprob.max()) + max(0.0, self.cfg.dict_weight))
        self._cache: dict[tuple, _NullSet] = {}
        self.min_length = max(2, order)
        self._max_word_bonus = max(0.0, self.cfg.word_weight)

    # ------------------------------------------------------------ raw signals
    def _screen(self, arr: np.ndarray) -> float:
        return max(m[0].score(arr) for m in self._models.values())

    def _word_score(self, arr: np.ndarray, spans, lang: str) -> float:
        lex = self._lexicons[lang]
        tok = self.alphabet.tokens
        hit = 0
        for a, b in spans:
            if "".join(tok[int(x)] for x in arr[a:b]) in lex:
                hit += b - a
        return hit / max(1, len(arr))

    def _full(self, arr: np.ndarray, spans=None) -> tuple[float, str, float, float, float | None]:
        best = None
        for lang, (_, full, dic) in self._models.items():
            ng = full.score(arr)
            dc = dic.coverage(arr)
            comb = ng + self.cfg.dict_weight * dc
            wd = None
            if spans:
                wd = self._word_score(arr, spans, lang)
                comb += self.cfg.word_weight * wd
            if best is None or comb > best[0]:
                best = (comb, lang, ng, dc, wd)
        return best  # type: ignore[return-value]

    def normalise_breaks(self, length: int, breaks) -> tuple[int, ...] | None:
        """Word boundaries usable for a candidate of `length` (after prefix scoring), or
        None when there are too few words for the signal to mean anything."""
        if not breaks or self.cfg.word_weight == 0:
            return None
        L = self.scored_length(length)
        b = tuple(sorted({int(x) for x in breaks if 0 < int(x) < L}))
        return b if len(b) + 1 >= self.cfg.word_min_words else None

    # ------------------------------------------------------------ null model
    def _null_samples(self, length: int, kind: str, rng: np.random.Generator,
                      count: int | None = None) -> list[np.ndarray]:
        n = self.alphabet.size
        M = self.cfg.null_samples if count is None else int(count)
        langs = list(self._good)
        out = []
        fams = [get_family(f) for f in self.cfg.wrong_key_families]
        for i in range(M):
            if kind == "random":
                out.append(rng.integers(0, n, size=length).astype(np.int16))
                continue
            good = self._good[langs[i % len(langs)]]
            pt = self._window(rng, good, length)
            if kind == "shuffled":
                out.append(rng.permutation(pt))
            elif kind == "wrong_key":
                fam = fams[i % len(fams)]
                out.append(self._wrong_key_sample(fams[i % len(fams)], pt, good, rng))
            else:
                raise ValueError(f"unknown null type {kind}")
        return out

    def _wrong_key_sample(self, fam, pt: np.ndarray, good: np.ndarray,
                          rng: np.random.Generator, tries: int = 20) -> np.ndarray:
        """Decrypt pt's encryption under a *wrong* key.

        A key can differ from the true one yet decrypt (almost) correctly:
        equivalent keys (identity column orders of different widths, periodic
        repeats like ABCABC vs ABC), keyword alphabets sharing their tail, a
        Vigenere key off by one letter. Those are near-solutions, not noise, so
        any candidate sharing >= NEAR_SOLUTION of its 4-grams with the true
        plaintext is redrawn. This matches the validation harness, which counts
        such decryptions as partial solutions rather than false positives.
        """
        n = self.alphabet.size
        L = len(pt)
        if fam.name == "running_key":
            k1 = self._window(rng, good, L + 200)
            p1 = fam.random_params(rng, L, k1)
            ct = fam.encrypt(pt, k1, n, **p1)
            for _ in range(tries):
                k2 = self._window(rng, good, L + 200)
                cand = fam.decrypt(ct, k2, n, **fam.random_params(rng, L, k2))
                if gram_overlap(cand, pt) < NEAR_SOLUTION:
                    return cand
            return rng.permutation(pt)
        k1 = fam.random_key(rng, n, "medium", words=self._words, length=L)
        p1 = fam.random_params(rng, L, k1)
        ct = fam.encrypt(pt, k1, n, **p1)
        for _ in range(tries):
            k2 = fam.random_key(rng, n, "medium", words=self._words, length=L)
            if fam.key_json(k2) == fam.key_json(k1):
                continue
            cand = fam.decrypt(ct, k2, n, **p1)
            if gram_overlap(cand, pt) < NEAR_SOLUTION:
                return cand
        # Tiny key spaces may offer no genuinely wrong key; never put the true
        # plaintext (or a near copy) into the null.
        return rng.permutation(pt)

    @staticmethod
    def _window(rng: np.random.Generator, good: np.ndarray, length: int) -> np.ndarray:
        if length > len(good):
            raise ValueError(f"length {length} exceeds the training text ({len(good)} symbols)")
        start = int(rng.integers(0, len(good) - length + 1))
        return good[start:start + length]

    def scored_length(self, length: int) -> int:
        """Candidates longer than max_score_length are scored on a prefix of this length."""
        return min(int(length), self.cfg.max_score_length)

    def bigram_table(self) -> np.ndarray:
        """(N, N) log P(next | previous) of the first configured language (used by
        search-based decryptions such as skip resolution)."""
        lang = self.cfg.languages[0]
        screen = self._models[lang][0]
        if screen.order != 2:
            raise ValueError("bigram table needs an n-gram order of at least 2")
        n = self.alphabet.size
        return screen.logprob.reshape(n, n)

    def _variant_transform(self, variant: str, length: int, rng: np.random.Generator):
        """Null samples for search-optimised decryptions: each base null sample is used
        as ciphertext and decrypted by the same search under a random (wrong) key."""
        if not variant.startswith("skipdp:"):
            raise ValueError(f"unknown null variant {variant!r}")
        from lpswarm.programs.resolve import resolve_decrypt
        from lpswarm.programs.sequences import SEQUENCES
        skip = [int(x) for x in variant.split(":", 1)[1].split(",") if x != ""]
        n = self.alphabet.size
        bigram = self.bigram_table()
        names = sorted(SEQUENCES)

        def transform(x: np.ndarray) -> np.ndarray:
            u = rng.random()
            if u < 0.2:
                stream = {"kind": "constant", "value": int(rng.integers(0, n))}
            elif u < 0.6:
                stream = {"kind": "repeat", "key": [int(v) for v in rng.integers(0, n, int(rng.integers(2, 14)))],
                          "offset": 0}
            else:
                stream = {"kind": "sequence", "name": names[int(rng.integers(len(names)))],
                          "offset": int(rng.integers(0, 50)), "scale": int(rng.integers(1, n)),
                          "add": int(rng.integers(0, n))}
            spec = {"v": 1, "combine": ("sub", "add", "beaufort")[int(rng.integers(3))],
                    "map": "reverse" if rng.random() < 0.3 else "identity", "reverse_text": False,
                    "skip": skip, "skip_mode": "resolve", "transpose": None, "stream": stream,
                    "offset_range": None}
            return resolve_decrypt(x, spec, n, bigram)
        return transform

    def calibrate(self, length: int, breaks=None, variant: str | None = None) -> _NullSet:
        """Null distributions for candidates of this length (and word-break pattern:
        every null sample is scored with the same breaks as the target; and null
        variant: search-optimised decryptions get nulls from the same search)."""
        length = self.scored_length(length)
        bk = self.normalise_breaks(length, breaks)
        key = (length, bk, variant)
        if key in self._cache:
            return self._cache[key]
        spans = word_spans(length, bk) if bk else None
        if length < self.min_length:
            raise ValueError(f"length {length} too short to score (minimum {self.min_length} "
                             f"for n-gram order {self.order})")
        if any(length + 200 > len(g) for g in self._good.values()):
            raise ValueError(f"length {length} too long for the training text; supply more corpus")
        rng = np.random.default_rng([self.cfg.seed, length, 0xCA11])
        screen: dict[str, np.ndarray] = {}
        combined: dict[str, np.ndarray] = {}
        pooled: dict[str, list[float]] = {"screen": [], "ic": [], "ngram": [], "dict": [],
                                          "combined": []}
        n = self.alphabet.size
        transform = self._variant_transform(variant, length, rng) if variant else None
        count = self.cfg.variant_null_samples if variant else None
        for kind in self.cfg.null_types:
            sc, cb = [], []
            for arr in self._null_samples(length, kind, rng, count=count):
                if transform is not None:
                    arr = transform(arr)
                s = self._screen(arr)
                c, _, ng, dc, _wd = self._full(arr, spans)
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
        self._cache[key] = ns
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
        """Per-attempt level for the i-th attempt on a target (i = attempt_count).

        bonferroni: alpha / i. Used in-run as a triage level; the binding,
            order-independent decision is final_check() at alpha / N_total.
        spending:   alpha / (i (i + 1)). Sums to < alpha over any number of
            attempts, so in-run passes already control the family-wise error
            rate, at the price of depending on search order.
        none:       alpha.
        """
        i = max(1, int(attempt_count))
        mode = self.cfg.multiple_comparisons
        if mode == "none":
            return self.cfg.alpha
        if mode == "spending":
            return self.cfg.alpha / (i * (i + 1.0))
        return self.cfg.alpha / i

    def final_threshold(self, length: int, total_attempts: int, breaks=None,
                        variant: str | None = None) -> tuple[float, float]:
        """(alpha_eff, threshold) for the end-of-search Bonferroni check over all attempts."""
        length = self.scored_length(length)
        ns = self.calibrate(length, breaks, variant)
        a = self.cfg.alpha if self.cfg.multiple_comparisons == "none" \
            else self.cfg.alpha / max(1, int(total_attempts))
        return a, max(self._upper_quantile(v, a) for v in ns.combined.values())

    def threshold(self, length: int, attempt_count: int = 1, breaks=None,
                  variant: str | None = None) -> float:
        ns = self.calibrate(self.scored_length(length), breaks, variant)
        a = self.alpha_eff(attempt_count)
        return max(self._upper_quantile(v, a) for v in ns.combined.values())

    # ------------------------------------------------------------------ score
    def score(self, arr: np.ndarray, attempt_count: int = 1, breaks=None,
              variant: str | None = None) -> ScoreReport:
        arr = np.asarray(arr, dtype=np.int16)[: self.cfg.max_score_length]
        L = len(arr)
        bk = self.normalise_breaks(L, breaks)
        ns = self.calibrate(L, bk, variant)
        s = self._screen(arr)
        a_eff = self.alpha_eff(attempt_count)
        thr = max(self._upper_quantile(v, a_eff) for v in ns.combined.values())
        unreachable = thr >= self._max_combined + (self._max_word_bonus if bk else 0.0)
        if s < ns.screen_threshold:
            return ScoreReport(L, "screen", FAIL, False, s, ns.screen_threshold,
                               threshold=thr, attempt_count=attempt_count, alpha_eff=a_eff,
                               unreachable=unreachable, null_variant=variant)
        comb, lang, ng, dc, wd = self._full(arr, word_spans(L, bk) if bk else None)
        ic = index_of_coincidence(arr, self.alphabet.size)
        lm = None
        if self.lm_scorer is not None:
            lm = float(self.lm_scorer(self.alphabet.decode(arr)))
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
                           lm, comb, lang, thr, thr0, null_pct, pct, attempt_count, a_eff,
                           unreachable, wd, variant)


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
                   seed: int = 12345, breaks_by_length: dict | None = None,
                   variant: str | None = None) -> dict:
    """Measure false-positive rate on *fresh* nulls (different seed from calibration)
    at the unadjusted alpha (attempt_count=1).

    Because the threshold is the max over null types, each type's FPR should be
    <= alpha + tol, and the worst type's FPR should be within +/- tol of alpha.
    Returns {"rows": per (length, type), "summary": per length}.
    """
    if samples < 1:
        raise ValueError("samples must be >= 1")
    rows, summary = [], []
    cfg = oracle.cfg
    for L in lengths:
        bk = (breaks_by_length or {}).get(L)
        oracle.calibrate(L, bk, variant)
        rng = np.random.default_rng([seed, L, 0xF00D])
        transform = oracle._variant_transform(variant, L, rng) if variant else None
        tol = fpr_tolerance(cfg.alpha, samples,
                            cfg.variant_null_samples if variant else cfg.null_samples)
        worst = 0.0
        ok_all = True
        for kind in cfg.null_types:
            arrs = oracle._null_samples(L, kind, rng, count=samples)
            if transform is not None:
                arrs = [transform(x) for x in arrs]
            hits = sum(1 for arr in arrs
                       if _passes_unadjusted(oracle.score(arr, attempt_count=1, breaks=bk,
                                                          variant=variant)))
            fpr = hits / len(arrs)
            lo, hi = wilson(hits, len(arrs))
            ok = fpr <= cfg.alpha + tol
            ok_all &= ok
            worst = max(worst, fpr)
            rows.append({"length": L, "null_type": kind, "n": len(arrs), "false_pos": hits,
                         "fpr": fpr, "ci_lo": lo, "ci_hi": hi, "alpha": cfg.alpha,
                         "tolerance": tol, "not_anticonservative": ok})
        summary.append({"length": L, "alpha": cfg.alpha, "worst_type_fpr": worst, "tolerance": tol,
                        "within_tolerance": ok_all and abs(worst - cfg.alpha) <= tol})
    return {"rows": rows, "summary": summary}


def _passes_unadjusted(rep: ScoreReport) -> bool:
    """Passed the screen and beat the threshold at the configured alpha, ignoring any
    multiple-comparison adjustment (pass or near_miss)."""
    return rep.stage == "full" and rep.verdict in (PASS, NEAR_MISS)


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)

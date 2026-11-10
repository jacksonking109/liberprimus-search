# Plan: anatomy of the repeat shortage, then constructions outside the cipher language

Status: Phases 0 and 1 done; Phase 2 mostly done (sections 14 and 16 of `avenues_explored.md`: three stateful families, 78 variants, none passes) (multiplicatively keyed running sum: signature reproducible, EA trigger rejected, no IC hit; the other generators are not built) (`data/lp_derived/lp2_runes.csv`, `docs/diagnostics_sample/leak_anatomy.md`; verdict: random thinning); Phase 2 next. Planned Written 2026-11-06 after `docs/avenues_explored.md`. Everything here is deterministic and model-free
until Phase 3; nothing touches the oracle, thresholds, budgets or packets.

## Why this is the next step
The one real anomaly is that adjacent identical runes are about five times too rare (86 against about 440 expected), only at lag 1,
uniform across runes, pages and sections, and present in both the image reading and the scream314 text. The signature, measured on
sections 10-25: lag-1 ratio 0.19 (95% interval 0.15-0.24), lags 2-8 at chance, unigram IC x 29 = 1.00, first-difference IC x 29 = 1.03.
A thinned random walk reproduces all four (a running sum whose step is nearly uniform over the 28 non-zero values, zero five times too
rare). No cipher in the DSL does (58,024 screened). So either a mechanism outside the DSL makes this, or the text is a generated
no-repeat stream with nothing to decrypt. Phase 1 is how we tell which.

## Phase 0: one clean data table (about 30 minutes)
Export the image reading as a small committed table (derived counts only, no images): `data/lp_derived/lp2_runes.csv` with page, line,
index in line, global index (pages 17-72 in reading order), rune id, separator after it (none, word dot, colon pair), red/black, drop cap,
plus the manifest section id. About 13,000 rows. This survives container resets and carries page and line structure the text files lack.
Three indexings are kept for every test: global (one continuous line over pages 17-72), per page, per section.

## Phase 1: leak anatomy (about 1-2 hours; the 86 doubles)
Pre-specified tests, each against an exact null that draws the same number of doubles from the valid adjacent pairs; p-values are the
maximum over the tests in a family, and all are exploratory.
1. **Position:** position in word, in line, distance from the page start and end, first or last rune of a word.
2. **Phase:** index mod m for m = 2..200, global and per page and per section (maximum chi-square over m).
3. **Spacing:** gaps between consecutive doubles against the geometric null; clustering; runs of doubles.
4. **Context:** the rune before and after, the step before and after (are doubles inside equal-step runs?), the rune pair.
5. **Conditional steps:** the step distribution right after a double; whether doubles follow non-zero steps of a particular size.
6. **Alphabet position:** do doubles avoid or favour F, the rune adjacent to a skip, or any rune class?
Decision rule, fixed now: any family with maximum-corrected p < 0.01 means the leak is structured, so we are looking for a cipher with
exceptions, and the structure says where. No family below 0.05 means the leak is a random thinning, which favours a generated stream.
Report both outcomes plainly; a negative is a result.

## Phase 2: constructions outside the DSL (about half a day)
Add generators to `research_signature.py` (the screen and its four numbers already exist) and run them with English plaintext:
* G1 non-zero-step running sum: c_t = c_(t-1) + 1 + ((x_t + k_t) mod 28), x_t a 28-symbol plaintext (F handled separately), k_t a stream key;
* G2 previous-output-excluded substitution: row chosen by the previous ciphertext symbol, never returning it (Latin-square rows);
* G3 running sum of keyed differences with a non-zero key step;
* G4 two interleaved streams (odd/even runes, or word-alternating);
* G5 leak variants: a small probability that the step is allowed to be zero, tied to a rune, a position or a word boundary;
* controls: the thinned walk (must pass), plain English (must fail), the DSL families (must still fail).
Pass criterion is the existing `full` match (lag-1 interval, lags 2-8 flat, both ICs <= 1.15) plus per-rune and per-page uniformity.
A survivor becomes a parametrised family; its inversion is then a normal oracle-scored search over its parameters.

## Phase 3: model budget (gate and brief built 2026-11-06; no model has been run)
Built: `--signature-gate` and `--facts-file config/briefs/lp2_signature.md` (see `docs/research_tools.md`), and a commented `codex-signature` lane in the overnight example. Still needs the owner's go-ahead and keys: the Codex / DeepSeek runs themselves. Important limit: the program language cannot express anything the gate lets through, so the next code step is a new construction in the language (e.g. a keyed multiplicative running sum).

Original text:
Wire `screen_full` and `classify` in front of the oracle as a gate, so a proposed program that cannot reproduce the signature never
reaches it. Brief Codex with the signature, the Phase 1 verdict and the Phase 2 survivors, and ask for constructions outside the DSL.
No live model call, paid run or packet run without the owner's go-ahead.

## Should scream314 be treated as one line?
Mostly it already is, and the plan keeps it that way for the signature: `research_structure`, `scans` and the lag profile ignore line
breaks, and word-gap type made no difference (within a word 62 against 336 expected, across a boundary 22 against 96, ratios 0.18 and
0.23). Two changes: use **one continuous stream over pages 17-72 in reading order** for the phase tests (a per-section index would
hide a period that runs across sections), and keep word and line position as covariates, not as structure. The images supply page
and line breaks that the markdown lacks, so Phase 0 builds on the image reading and uses scream314 as a cross-check (12,955 of 12,956 agree).
Spacing only matters for word-reset constructions, and the within/across-word ratios say that is not where the leak lives.

## Risks
The text may be a generated stream with nothing to decrypt; with 86 doubles, small rune-specific or position-specific effects stay
below detection (a mid-frequency rune at 2x is caught 11% of the time); many tests mean a maximum-corrected p is the honest number.

## Not doing
No key guessing against the oracle, no edits to the transcription, no OutGuess work (closed by the header test), no new packets.

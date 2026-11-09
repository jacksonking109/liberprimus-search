# Research packets and structure diagnostics

A one-page list of every avenue tried and what it found is in `docs/avenues_explored.md`.

Tools for looking at the unsolved sections without guessing a key. None of them calls a model or
the oracle, and none of them changes thresholds, null calibration or budgets.

## Packets (`python -m lpswarm.research_packets --out packets`)

A packet is a fixed list of cipher programs replayed by a scripted proposer through the normal swarm,
so the real oracle, ledger and comparison accounting apply. Each `packets/<name>/packet.md` gives the
exact targets, counts, caps, stop rule and run command. **Nothing in `packets/` has been run**; run
`lpswarm coverage --latest 3` first, then the command in the packet, only after review.

| packet | what it tests | ciphers per target |
| --- | --- | ---: |
| `exp1_feedback` | neighbour / chain feedback, with and without word reset | 261 |
| `exp2_two_shear` | determinant-one 2x2 Hill blocks, b = 0 | 33 |
| `exp2b_all_shifts` | the same with all 29 offsets (separate approval) | 957 |
| `exp4_wordkeys_reversed` | repeating word keys (verified keywords + 5,000 commonest corpus words) under the reversed alphabet, `p = (28 - c) -/+ key`, with and without the resolved F-skip; sections 10, 12, 13, 24, 25 | 19,882 |
| `exp3_progressive` | progressive keys `k_t = d * s(o + t)`: `naturals`, `squares`, `triangular` x scale 1..28 x offset 0..28 x (p = c - k, p = k - c) | 4,873 |

`p = k - c` is the reversed-alphabet form (reversed Gematria plus a shift, as the source notes give for
solved LP1 pages 1, 5 and 6); the interpreter calls it `beaufort`, which is only a sign convention here.
For `naturals` the exp3 packet is the complete arithmetic family `k_t = d*t + b` (the offset sweep
covers every b because d is invertible mod 29). `squares` and `triangular` with a scale and offset
are only a subfamily of quadratic keys; a general polynomial key would need a new stream kind.

## Structure diagnostics (`python -m lpswarm.research_structure {diffs,scans,periods,repeats,power,all}`)

Deterministic (fixed seeds), bounded (wall-clock cap, partial results marked) and exploratory: the
units were chosen after looking at the data and p-values calibrate a maximum over the inspected
units. The null keeps each section's symbol frequencies and shuffles their order; p-values are exact
Monte Carlo (the observed sample is one of the r+1 exchangeable samples), so the smallest possible p
with 199 shuffles is 0.005.

* `diffs`: histograms of `d = c[i]-c[i-1]` and `s = c[i]+c[i-1]` (mod 29) pooled over the unsolved
  sections of 300+ runes; the same non-zero-d statistics given the observed number of repeats (the
  missing repeats must appear somewhere, so the shuffles are rescaled to the observed non-zero
  total); repeats within words and across word boundaries; the 29x29 transition table (chi-square
  with and without the diagonal, cells with count <= 1); and whether the sections look like one
  population (chi-square of homogeneity, per-section z).
* `scans`: plug-in mutual information between `c[i]` and `c[i-k]`, k = 1..64, and the index of
  coincidence of `c[i] + r*c[i-k]`, r = 1..28, k = 1..16 (448 transforms; scaling relabels residues,
  so r = b/a covers every `a*c[i-k] + b*c[i]`). Run twice: on all pairs, and with equal pairs
  (`c[i] == c[i-k]`) excluded, which removes the known repeat shortage so that what is left is
  dependence beyond it.
* `periods`: column index of coincidence for repeating-key periods 2..200, with the F rune (rune 0)
  treated four ways: untouched; removed (the documented F-skip: F is literal and the key does not
  advance); ignored but counted (F literal, key advances); and an F-robust lag comb that uses only
  pairs with no F between them and combines each period's multiples. The F treatment matters: the
  solved pages with F-skip only decode when each F is resolved separately (see
  `docs/lp_baseline_run.md`), so a fixed treatment misaligns the columns after every F. The two
  Vigenere pages in the manifest (4: key length 8, 8: key length 13) are included as detector
  controls only; the scan recovers page 8 in every variant and page 4 only through the lag comb
  (as period 4, a divisor of 8). Periods above 60 are only reached by the first three variants.
* `repeats`: where the adjacent equal runes fall in the raw text: by what separates the two runes
  (nothing, a word dot, a line end, a quote), by rune, and by position in the section (deciles, and one
  permutation test of the mean relative position, which is a weak lead at most because it was chosen
  after looking at the same data). Also prints absolute repeat rates for other sections of the
  manifest (3, 4, 5, 7, 8, 9, 27) for context; uniform random text gives 3.4%.
* `power`: English plaintext (training split) put through neighbour feedback, chain autokey,
  a progressive key, a prime stream, 2x2 Hill blocks, a length-37 periodic key, plus plaintext and
  iid noise, at several lengths, with every test above run on each. It says what a diagnostic can see.
  A real section that shows nothing is only evidence against the mechanisms its row detects.
  Synthetic data only; no held-out split.

Outputs: `diagnostics_structure.json` and `diagnostics_structure.md` in `--out` (default
`reports/diag`). A reference run on the bundled transcription is in `docs/diagnostics_sample/`.

## Assumption audit (`python -m lpswarm.research_views {agnostic,bytes,numbers,all}`)

Checks that drop the assumption that the sections are English text enciphered letter by letter. No
models, no oracle, no ledger; fixed seeds, wall-clock caps, exploratory. Each result is printed next to
synthetic controls with known answers.

* `agnostic`: decrypt with position-keyed streams (8 sequences x 28 scales x 3,000 offsets x 3 treatments of
  the F rune) and score by the index of coincidence of the first 600 runes, which is high for any natural
  language and needs no word list. IC is unchanged by any relabelling of the alphabet, so affine maps,
  reversal and sign choices need no separate runs. It also re-scores every packet candidate that `decrypt`
  can evaluate by IC only (nothing goes through the oracle or a ledger, so packets stay unrun for
  accounting). Flag: IC x 29 >= 1.25 and above the maximum of shuffled-ciphertext replicates.
  **Blind spot:** the documented F-skip pages need each F resolved separately (see
  `docs/lp_baseline_run.md`), so a stream that behaves that way is reachable only through the longest
  F-free stretch (60-130 runes), and at that length noise alone reaches the IC that language reaches
  (the report prints the null mean and maximum). Streams that fall out of step partway are likewise
  hard to see.
* `bytes`: the section as binary data: base-29 integer to bytes (both digit orders), 5-bit packing, one byte
  per rune, rune pairs. Valid zlib / gzip / bzip2 / xz streams and magic numbers at offsets 0-31 (false
  positives are negligible), plus printable fraction, longest printable run, entropy and compressibility
  against 99 shuffles. Readable sections are included as sensitivity references. Encrypted binary (uniform
  bytes) is undetectable by design.
* `numbers`: words and lines read as numbers in fixed ways (base 29 either way round, decimal concatenation of
  rune indexes, Gematria prime-value sum, index sum) with primality / square / Fibonacci fractions against a
  shuffle null; and whether the text itself is a polynomial (finite differences up to order 8) or a linear
  recurrence of order 2 or 3 mod 29 (all coefficients).

`--derive diff|sum` runs the checks on the first differences `c[i]-c[i-1]` or neighbour sums `c[i]+c[i-1]` mod 29
instead of the runes, which tests a running-sum construction under which the hidden stream is what a sweep should
decrypt.

The z-scores here use leave-one-out means and spreads (every sample is judged out-of-sample) and a minimum
meaningful spread per statistic; p-values are the maximum over the readings tried.

## Out-of-step prime stream (`python -m lpswarm.research_windows`)

The solved prime page only decodes cleanly from its start (one skipped index, F-skip), so a whole-text test
fails on a stream that is right but out of step. This searches locally in two stages. Stage 1 scores, with the
oracle's English bigram model, every decryption `p = orient(c) - (a*prime[o+t] + b)` (orientation x scale +-1 x
constant 0..28 x offset 0..6,000) of the three longest F-free stretches (60+ runes) in the first 800 runes of
each section; an F-free stretch does not depend on how an F is treated. Stage 2 takes the best candidates,
decrypts the 800 runes with the resolved F-skip at every global offset consistent with the stretch, and scores
only the runes OUTSIDE the stretch (text the selection never saw) against 40 random candidates. A stage-2
z >= 8 is a lead for the real oracle, not a result. Planted controls (English through prime-minus-one with the
F-skip, with and without an extra skipped index) are found at z about 33-40; noise stays at 2-4. English
bigram model only. The reference run in `docs/diagnostics_sample/diagnostics_windows.md` is primes only; `diagnostics_windows_all.md` repeats it over primes, Fibonacci, naturals, squares, triangular, pi and e digits (`--sequences`, about 6 minutes): no flag on any section, best real stage-2 z 3.7 against 3.4 for noise and 32-38 for the planted stream.

## Page images (`python -m lpswarm.pageimages {fetch,headings}`)

The pages are drawn in one computer typeface, so the same rune is near pixel-identical wherever it appears (the
stroke distance between two copies is at most 3 px; between different runes at least 15 px). Reading a page is
therefore cutting glyphs and grouping identical shapes, with no trained model. `fetch` does a partial git clone of
`iBotPeaches/cicada_3301` into `data/lp_images/` (git-ignored: the images are never committed; their SHA-256 sums are
in `data/lp_images.sha256`). Needs Pillow and scipy (`pip install -e ".[images]"`).

What the images carry that the text files lose: line breaks, red runes, the large red drop cap (it is the first rune of
the text), the dotted red square that ends a red passage, and the separator after each glyph.

**Red text is a heading or closing line**, ended by the dotted square. Checked on the plain-substitution pages, where the
red runs read as written: SOME WISDOM / KNOW THIS (page 05), THE LOSS OF DIVINITY / CONSUMPTION (10), PRESERVATION (11),
ADHERENCE (12), SOME WISDOM / AN INSTRUCTION (13), AN INSTRUCTION / KNOW THIS (16), PARABLE (74), and A WARNING / FOR ALL
IS SACRED (page 01, reversed alphabet).

`headings` learns the shapes on all pages, labels them from pages 14-15 and 16 (their glyph counts equal the manifest's;
agreement 100% on both), re-reads every page, and tabulates the red runs. It then runs a **crib test** on the unsolved pages:
each red heading is tried against every title of the same length (the list above plus A KOAN, A WARNING, AN END, WELCOME);
the implied key `c - p` must be a window of one of seven sequences (every scale, offset 0..20,000) or a short repeating key.
Known-page controls: page 73's five-rune heading AN END recovers the prime stream (scale 1, offset 0) by itself, and page 74's
gives a constant key. On the unsolved pages: no hit, and 0 false matches in 108 random-plaintext tests.

Limits: agreement with the manifest is 98.8-100% on the pages compared; the early pages have vines that touch glyphs at the
left margin and page 05 has a grid of numbers and small runes, so those layouts lose or add a few glyphs (the unsolved LP2
pages mostly have the clean layout). Headings of 13, 19 or 50 runes have no matching title in the list and are only
tabulated. The crib test assumes the heading is enciphered with the same position-keyed stream as the body, as it is on
the solved pages.

## Direct repeat count (`python -m lpswarm.pageimages doubles`)

Counts adjacent identical glyphs straight from the page images, independent of any transcription, to settle whether the
repeat shortage in the unsolved sections is real or an effect of the text files. A pair is a double only if two tests agree:
the same learned shape id, and a stroke distance of at most 8 px between the two glyph crops (pairs whose widths differ by
more than 6 px are never doubles). Pairs touching an unknown or unresolved box are excluded and counted. Expected doubles use
each page's own shape frequencies; the shuffle null permutes each page's known shapes among its known positions (199
shuffles). It writes `doubles.md`, `doubles.json` and `doubles_montage.png` (every image-side double on pages 17-72, cropped
with page and line, for checking by eye; images stay local and are never committed). Gate: at least 99% of the glyph boxes on
the unsolved pages have a known shape, otherwise report the gap instead of counting.

Reference run (`docs/diagnostics_sample/doubles.md`, counts only): pages 17-72 give 86 doubles in 12,842 pairs (0.67%, ratio
0.18 to the frequency expectation, 0 disagreements between the two tests, coverage 99.42%; the unknown boxes are margin art, see below), against 84 in 12,605 from the
scream314 text (all of sections 10-25 give 86 in 12,941, the same 86), 2.4-2.5% on the solved pages and 3.4% for uniformly random text. The shortage is a property of the pages,
not of the transcription, and it holds across word dots (0.8%), line ends (0.8%) and plain gaps (0.6%). The montage
was inspected by eye: every tile shows two identical glyphs.

## Per-rune breakdown and transcription alignment (`python -m lpswarm.research_doubles {perrune,align,all}`)

`perrune`: is the shortage of adjacent identical runes the same for every rune, page and lag? Expected counts are exact under
a permutation of each unit's known runes among its known positions (the same null the shuffles use); the uniformity test
conditions on the observed total (multinomial, Monte Carlo p, 20,000 draws) and reports its own power. A rune's `p deficit`
is against chance; "is this rune different from the others" is its residual against the pooled rate, Holm-adjusted. Image and
text are the same pages, so they are a consistency check, not two samples. `align`: manifest sections 10-25 against the glyph
sequence of pages 17-72 (longest-matching-block alignment; image glyphs that have no counterpart are reported, not dropped).
`--cache FILE` keeps the rune sequences (no images) as JSON; reading the images takes about 3 minutes.

Reference run (`docs/diagnostics_sample/perrune.md`, `alignment.md`):

* The image and the text both give **86 doubles** (12,842 and 12,941 pairs), the same 86 at the same positions. The earlier 84 in
  12,605 was the 300+ rune sections only. With the exact shuffle expectation (437) the ratio is 0.20, not the 0.18 that the
  simpler frequency-squared expectation (490) gave.
* **Uniform across runes:** chi-square 26.3 on 28 df, Monte Carlo p = 0.56 (text 0.51). Every rune is short (ratios 0.00-0.48
  around the pooled 0.20, B 0 of 14.6 expected, A 1 of 17.4) and none differs from the pooled rate after Holm. Power at 86
  doubles: five most frequent runes never doubling is detected in 83% of simulations, one mid-frequency rune at 4x in 61%, a single
  mid-frequency rune at 3x in 34% and at 2x in 11% (5% is the false-positive level). Rune-specific effects of that size or smaller
  cannot be excluded at this sample size.
* **Uniform across units:** 56 pages p = 0.31, 16 sections p = 0.85.
* **Lag profile:** only lag 1 is short (ratio 0.20, z = -16.8). Lags 2-8 are at chance (ratios 0.98-1.06). The shortage is a
  property of adjacent positions, not a wider local effect.
* **Alignment:** 12,955 of the 12,956 transcribed runes agree with the image reading in order (the reader labels shapes from
  sections 8 and 9 only, so this is an independent check of the transcription on the unsolved pages). One position differs: page 41
  line 8, where the image glyph is 0 px from the AE shape and 49 px from A, so the text is wrong there (it is not part of a double). There are no text-only runes. The 75 extra image boxes are
  all unknown-shape boxes sitting first or last in a line, on pages 25-31 (one each) and 57-72 (2-6 each); they are twig and vine
  drawings in the margins, so every rune on pages 17-72 was read and the 99.42% coverage figure undercounts the reader.
  Every double is in both sources.

## Signature screen (`python -m lpswarm.research_signature`)

What the unsolved sections look like, as four numbers measured on the manifest text (sections 10-25): lag-1 equal-neighbour ratio
0.19 (95% interval 0.15-0.24; `research_doubles`), lags 2-8 at chance (0.98-1.08), unigram IC x 29 = 0.999 and first-difference
IC x 29 = 1.025 (uniform 1.0, language 1.6-2.0; the non-zero differences are flat, `research_structure diffs`). The screen puts
synthetic English (training split) through every cipher it can enumerate in the DSL, with `programs.spec.encrypt`, and measures the
same four numbers on the result. No oracle, no models, no ledger; fixed seeds; about 4 minutes on 4 cores.

A `full` match is pre-specified: lag 1 inside the real interval, every lag 2-8 inside 0.85-1.15, both ICs <= 1.15. The first pass
used only the lag conditions and let five feedback ciphers through whose first differences are the plaintext itself; the IC
conditions were added after that, from statistics already reported, and the report shows `lag-only` and `full` separately. `loose`
is a post-hoc sensitivity check for the plaintext level (the solved plain-substitution pages sit at 0.44, interval 0.29-0.65, below
the synthetic English 0.58): the cipher must lower the plaintext's own lag-1 ratio by a factor in 0.24-0.83, with the same flat-lag and
IC conditions.

Reference run (`docs/diagnostics_sample/signature_screen.md`), 58,024 ciphers: the four packet families as the packets expand them
(exp1 feedback 261, exp2b Hill 957, exp3 progressive 4,873, exp4 word keys 19,882), the other position-keyed sequences (840), and a
wider sweep of the invertible mixers (neighbour and chain feedback x add/sub/rsub x lags 1-16 x both directions x 1-3 stages x word
reset x before/after the shift x 29 shifts: 25,056; 6,000 random Hill blocks of size 2-4; every block permutation of size 2-5).

* **No cipher is a full match, and none passes the loose check.** Lag 1 never gets below 0.46 for progressive keys and word keys
  (the controls: English 0.58, random symbols 0.98), 0.35 for the Hill blocks, 0.56 for the random Hill sample.
* Five distinct feedback ciphers (seven counting duplicates across families) match the lag statistics: all are lag-1 `neighbor`
  with a word reset, shifts 7 or 15. Their first differences are language-like (IC 1.42-1.63), which the real text contradicts, so
  those forms are out on this evidence. The closest cipher that also has flat symbols and differences reaches 0.55
  (neighbor rsub lag 1, next, three stages, word reset, shift 18), three times the real ratio.
* **Positive control:** a random walk whose zero steps are thinned to 20% (not a DSL cipher) has lag 1 0.20, lags 2-8 0.99-1.02, unigram
  IC 1.00, first-difference IC 1.02, a full match, so the criteria can be met. It is a description of the data, not a mechanism: the
  real text behaves as if each rune were the previous one plus a nearly uniform non-zero step, with a zero step 5 times too rare.

Limits: English plaintext only, and the plaintext's own lag-1 level is uncertain (hence the loose check, which also finds nothing);
the Hill and word-key families are samples, not exhaustive; single-stage mixers with one shift, no transpositions and no F-skip
outside exp4. A match would be a necessary condition for a mechanism, not evidence for it. For a proposed cipher program the same
numbers come from `screen_full(spec, english_windows(alpha))` and `classify(...)`; this is not wired into the swarm loop.

## Reader audit (`python -m lpswarm.reader_audit`)

Checks the image-to-rune reading itself: the stroke distance of every glyph to its own shape and to the nearest other rune (the typeface
separates them by at least 14 px, the decision threshold is 8), agreement with the manifest on solved pages that were not used to label the
shapes, what a wrong glyph size does (wrong runes, or only unknown ones), a short image read at many scales against a known answer, the
word separators against the text's breaks, and every position where image and text differ. Reference run: no glyph within 14 px of a
different rune; 0 wrong runes in 24 rescaled page reads (it fails to unknown, never to a wrong rune); manifest agreement 97-99% on the
independent solved pages (page 13 has 124 runes the manifest lacks, which decode to English from the images alone). Details in
`docs/avenues_explored.md` section 12 and `docs/diagnostics_sample/reader_audit.md`. Limits: the reader needs glyph height of about 100-130 px
(rescale other images first), and page 05's small rune words in the number grid are not read.

## Leak anatomy (`python -m lpswarm.lp_table`, `python -m lpswarm.research_leak`)

`lp_table` writes `data/lp_derived/lp2_runes.csv`, one row per rune on pages 17-72 from the image reading (page, line, position, separators, colour,
manifest section), so analyses run without the images. `research_leak` asks where the 86 adjacent equal runes sit, in five pre-specified families
(layout, phase, spacing, context, alphabet class) against a null that places the same number of doubles uniformly among the valid pairs, with a
calibration and power check. Reference run: no family below p = 0.05 (smallest 0.115), so the leak looks like random thinning; power is high for
layout, spacing, context and alphabet effects and low (32%) for a period on a single residue. Details in `docs/avenues_explored.md` section 13.

## Multiplicatively keyed running sums (`python -m lpswarm.research_muldiff`)

c[t] = c[t-1] + a[t] * n[t] (mod 29): flat first differences whatever the plaintext is, and a zero step only where the plaintext number is zero. The
module (1) screens the family against the four numbers of the repeat signature (it matches with EA as the zero rune), (2) tests whether the doubles'
word positions look like that rune's (they do not: p < 0.0001 against EA, p = 0.66 against any rune), and (3) sweeps u[t] = a[t]^-1 x (c[t] - c[t-1]) and
a[t] x (c[t] - c[t-1]) for position-keyed sequences by index of coincidence (no section flagged; planted controls recovered at IC 1.77). Details in
`docs/avenues_explored.md` section 14.

## Signature gate and facts file (`--signature-gate`, `--facts-file`)

`swarm --signature-gate` runs each proposed program the other way (`programs.spec.encrypt`) on English and refuses it before the oracle if the
ciphertext misses the unsolved LP2 signature (lag 1 outside 0.08-0.40, lags 2-8 outside 0.70-1.30, or unigram or first-difference IC above 1.25; wide
bands on purpose). The numbers are fed back to the proposer and counted as `gated` in `report.json`, with the reason in `invalid_reasons`. It blocks only
when every expanded member (at most 64) is evaluable and fails; programs it cannot evaluate (no inverse such as window mixes, more ciphers than 64) pass.
It is specific to sections 10-25: never use it on solved or synthetic targets. `--facts-file config/briefs/lp2_signature.md` shows the measured facts of
those sections to the `--auto-brief` model (Opus), to `--refine-brief` and to every proposer. A commented `codex-signature` lane is in
`config/overnight.example.toml`. Limit: every family in the current program language is refused by the gate, so a lane can only get programs through that the gate
cannot evaluate until the language gains a construction that has the signature (for example the multiplicatively keyed running sum of `research_muldiff`).

## Literal readings (`python -m lpswarm.research_literal`)

Readings of the 2016 hint's "their numbers are the direction" with the runes' Gematria prime values: a self-keyed cipher (each rune's prime value as the key for the
next), steps through a page by prime values, and square pages as grids against the hint numbers. All negative so far; see `docs/avenues_explored.md` section 15.

## Limits

* The power table uses English plaintext. If the true plaintext is another language, abbreviated or
  not language at all, pairwise structure is weaker than the table suggests.
* Position-keyed streams with a non-repeating key (prime, totient, Fibonacci) leave no pairwise
  structure: the power table shows these diagnostics mostly cannot see them. Absence of pairwise
  dependence says nothing for or against those.
* Mutual information is the plug-in estimate (bias about 784 / 2m nats); only z against the shuffle
  null is used for decisions.
* Word breaks are those of the transcription (the bullet separators). `diffs` and `scans` ignore line
  breaks; `repeats` reports them as a separate kind of gap.
* The dependence scan did NOT recover the key length on the two Vigenere pages in the manifest
  (sections 4 and 8): pairwise dependence does not reliably show a short periodic key. Use `periods`
  for that, and read its limits: with many F runes only the F-robust comb survives, and it reaches
  periods up to about 60 on sections of a few hundred runes.

# Research packets and structure diagnostics

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
bigram model only; one sequence family (primes) unless widened with `--sequences`.

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

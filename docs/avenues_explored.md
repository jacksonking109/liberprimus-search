# Avenues explored on the unsolved Liber Primus pages

Status as of 2026-11-06, branch `claude/eager-pasteur-l0dsma` (latest commit when written: `92b57ef`). Everything below is
exploratory: units and tests were often chosen after looking at the data, and a p-value here is not confirmation. Nothing has
decrypted any unsolved section. Detail and commands for each tool are in `docs/research_tools.md`; reference outputs are in
`docs/diagnostics_sample/`.

## 1. What is known going in

* The solved pages, per the source notes in `data/lp/manifest.json`: reversed Gematria plus a shift (LP1 pages 1, 5, 6), plain
  Gematria (several pages), Vigenere with the keys DIVINITY and FIRFUMFERENFE with each F resolved separately (pages 3-4 and 14-15),
  and a prime-totient stream with F skipped (page 73). The unsolved sections are the LP2 pages 17-72 (manifest sections 10-25).
* Method: models propose cipher programs, deterministic code scores them (an English oracle with a calibrated null and a final
  Bonferroni check). No result in this document depends on a model's say-so.
* The only real anomaly found: adjacent identical runes are about five times rarer than chance (section 3 below).

## 2. Searches against the real sections (oracle-scored)

| avenue | what was run | result |
| --- | --- | --- |
| Phase 1 baseline (`docs/lp_baseline_run.md`) | Caesar; Vigenere / Beaufort / variant Beaufort and autokey with the 5,000 commonest words plus every key of length <= 2; keyword substitution; columnar widths 2-7; about 46.6k attempts per section | Found 7 of the 10 solved sections with no help (the 3 misses need the F-skip or the totient stream). **Zero final passes and zero near misses on all 18 unsolved sections.** |
| Phase 3 skip resolution | `skip_mode: resolve` (each F literal or encrypted, chosen by a bigram Viterbi search) | Reproduces pages 3-4 and 14-15 with the published keys and page 73 until the transcription corrupts; validates the language and scoring, not key finding |
| Exhaustive and model lanes (Codex, others) | Every key of length <= 4 under the reversed alphabet on sections 11, 19, 21, 25 (19 never finished, 25 failed), plus model-proposed programs | No lead. Coverage of the real sections is unknown until the local ledgers are compared (`lpswarm coverage`) |
| Research packets exp1-exp4 (`packets/`) | Written and validated, **not run**: neighbour/chain feedback (261 ciphers per target), two-shear Hill blocks (33; all shifts 957), progressive keys (4,873), word keys under the reversed alphabet (19,882) | Approved: exp1, exp2. Awaiting review: exp2b, exp3, exp4. Section 6 says these families cannot produce the repeat signature, so a hit is unlikely |

## 3. The repeat shortage (the one anomaly)

| step | finding |
| --- | --- |
| Text count (scream314 transcription, sections of 300+ runes) | 84 doubles in 12,605 pairs (0.67%); about 19% of the frequency expectation; random text 3.4%, solved pages 2.4-2.5% |
| Direct count from the page images (`pageimages doubles`, pages 17-72, independent of any transcription) | 86 in 12,842 pairs (0.67%), two identity tests agreeing on every pair, and the montage of every double inspected by eye. **The shortage is a property of the pages, not of the transcription** |
| Same 86 in both sources | Text over all sections 10-25 gives 86 in 12,941 pairs, the same 86 at the same positions |
| Exact shuffle expectation | 437 expected, ratio 0.20 (z = -16.8); the simpler frequency-squared figure (490) gave 0.18 |
| Where it falls | Across word dots (0.8%), line ends (0.8%) and plain gaps (0.6%); red headings too few to say |
| Per rune (`research_doubles perrune`) | Uniform: chi-square 26.3 on 28 df, p = 0.56; every rune short, none different from the others after Holm. Power: five most frequent runes never doubling is caught 83% of the time, one mid-frequency rune at 3x 34%, at 2x 11% |
| Per page and section | Uniform across 56 pages (p = 0.31) and 16 sections (p = 0.85) |
| Lag profile | Only lag 1 is short (0.20). Lags 2-8 at chance (0.98-1.06) |
| Transcription check | 12,955 of 12,956 transcribed runes agree with the image reading in order; one position differs (page 41 line 8, image AE, text A, unadjudicated); the 75 extra image boxes are margin art |

Reading: a rule on adjacent positions (a non-zero step between neighbours, or never emitting the same symbol twice) fits; anything
tied to specific runes or a wider window does not, with the power limits above.

## 4. Structure diagnostics (`research_structure`, no key guessed)

| avenue | result |
| --- | --- |
| First differences and sums, 29x29 transition table | Differences: only the d = 0 bin is off. Given the observed number of repeats, the non-zero differences are flat (max z 2.72, p 0.155; chi-square p 0.060). Transition table without the diagonal: p 0.34. The 84-vs-430 diagonal deficit is the whole story |
| Homogeneity across sections | One population: frequencies p 0.98, difference histograms p 0.115 |
| Mutual information c[i] vs c[i-k], k = 1..64, and IC of c[i] + r*c[i-k] | Nothing beyond the repeat shortage (repeated with equal pairs excluded). The scan did not recover the key length on the two Vigenere control pages, so it is weak against periodic keys |
| Column IC for repeating-key periods 2..200 (F treated four ways) | No repeating key up to about period 60 on the 1,000+ rune sections, under either alphabet orientation (with many Fs only the F-robust comb reaches that far); the control pages 4 and 8 are recovered, page 4 only through the comb |
| Repeat placement (`repeats`) | The deficit is similar across word, colon and line-end gaps; the position-in-section test is a weak lead at most (chosen after looking at the data) |
| Shared-key test between adjacent section pairs (`research_diagnostics keycancel`, 10-12, 17-18, 24-25, offsets -2..2) | Nothing: maximum -0.013, p = 0.57 |
| Power table (English through known mechanisms, in `diagnostics_structure.md`) | Says which mechanisms each diagnostic can see at each length. Position-keyed streams with a non-repeating key (prime, totient, Fibonacci) leave no pairwise structure, so these diagnostics mostly cannot see them; silence says nothing about those |

## 5. Assumption audit and stream searches (the key family, not the repeat signature)

| avenue | result |
| --- | --- |
| Language-agnostic IC sweep (`research_views agnostic`): 8 sequences x 28 scales x 3,000 offsets x 3 F treatments, plus every packet candidate | No flag on any section. Blind spot: F-skip streams are only reachable through F-free stretches of 60-130 runes, where noise alone reaches language IC |
| Same on first differences and neighbour sums (`--derive diff|sum`), testing a running-sum construction | No flag |
| Binary views (`bytes`): base-29 to bytes, 5-bit packing, zlib/gzip/bzip2/xz, magic numbers, entropy | Nothing; encrypted binary would be undetectable by design |
| Numbers (`numbers`): words and lines as numbers, primality/square/Fibonacci fractions, polynomial or linear recurrence mod 29 | Nothing |
| Out-of-step prime stream (`research_windows`): F-free stretches scored with the English bigram model, then verified on text outside the stretch, over primes, Fibonacci, naturals, squares, triangular, pi and e digits | No flag; best real stage-2 z 3.7 against 3.4 for noise and 32-38 for the planted stream |

## 6. Signature screen: which cipher families can produce what the text looks like (`research_signature`)

The text's measured signature: lag-1 ratio 0.19 (interval 0.15-0.24), lags 2-8 at chance, unigram IC x 29 = 0.999,
first-difference IC x 29 = 1.025 (language 1.6-2.0). English plaintext was put through 58,024 enumerated ciphers: the four packet
families, the other position-keyed sequences, neighbour/chain feedback over every op, lag 1-16, both directions, 1-3 stages, word
reset, before/after the shift and all 29 shifts (25,056), 6,000 random Hill blocks of size 2-4, and every block permutation of
size 2-5.

* **No cipher is a full match, and none passes the plaintext-level sensitivity check.** Progressive keys and word keys never get
  lag 1 below 0.46 (English itself 0.58, random 0.98); Hill blocks not below 0.35.
* Five feedback ciphers (lag-1 neighbour with a word reset) match the lag statistics, but their first differences are
  language-like (IC 1.42-1.63) which the real flat 1.025 contradicts. This was found by running the screen, and the IC conditions
  were then added and reported separately.
* The closest cipher with flat symbols and flat differences reaches lag 1 = 0.55, three times the real ratio.
* Positive control: a random walk whose zero steps are thinned to 20% (not a DSL cipher) reproduces all four numbers (0.20,
  0.99-1.02, 1.00, 1.02). It is a description of the data, not a mechanism: each rune behaves like the previous one plus a nearly
  uniform non-zero step, with the zero step about five times too rare.

## 7. Reading the page images (`pageimages`)

| avenue | result |
| --- | --- |
| Glyph reader (one computer typeface, stroke distance <= 3 px same rune, >= 15 different) | All 75 pages read; labelled from sections 8 and 9 with 100% agreement on pages 14-16; 99.42% of boxes on pages 17-72 have a known shape and the rest are margin art |
| Red text, drop caps, terminators | Red runs are headings or closing lines ended by a dotted red square; the large red drop cap is the first rune of the text |
| Crib test on red headings (every title of the same length, implied key tested as a window of 7 sequence families or a short repeating key) | 36 combinations on the unsolved pages, no hit, 0 false matches in 108 random-plaintext tests; controls recover page 73's prime stream and page 74's constant key |

## 8. Hypotheses by outcome

| hypothesis | status |
| --- | --- |
| Short repeating key (Vigenere family), either orientation, with or without F-skip | Not supported (period scan, baseline); periods beyond about 60 not excluded |
| Constant, progressive, prime, totient, Fibonacci and similar position-keyed streams | Not seen by the IC sweep or the window search; the pairwise diagnostics cannot see these, and the signature screen says they do not produce the repeat shortage |
| Neighbour or chain feedback, Hill blocks, block permutations | Do not reproduce the signature (section 6) |
| Binary, numbers or running-sum constructions | Nothing found |
| Transcription errors causing the shortage | Ruled out (section 3) |
| A rule on adjacent positions (non-zero step, or no repeated symbol) | Fits the data; no cipher construction found that gives it |

## 9. Open leads and not-yet-done work

* **Outguess test** on the pages (the unsolved pages mostly have no outguess data): the owner is running this; nothing here depends on it.
* **A construction outside the cipher language** whose output has the four numbers above. The screen can test any proposed program
  (`screen_full` and `classify` in `research_signature.py`); it is not wired into the swarm loop.
* **Headings of 13, 19 and 50 runes** have no matching title in the crib list and are only tabulated.
* **Per-page key restarts**: the images give page and line structure the text files lack.
* **Not generated**: the second feedback envelope (lag 2 and `next` direction, 2,784 candidates), the false-boundary control, general
  polynomial keys (squares and triangular with a scale and offset are only a subfamily of quadratic keys), keys that are not
  words, autokey keys and transposition combinations.
* **Discrepancies on solved pages** between the manifest and the images, not yet adjudicated: page 73 second rune missing in the
  manifest, page 74 an Y/E difference and an extra E, the tails of pages 3-4, and page 41 line 8 (AE vs A) on the unsolved pages.
* **Packets exp2b, exp3, exp4** still need review before any run.

## 10. Tooling built along the way

The deterministic harness (oracle, ledger, comparison accounting), the cipher-program language with skip resolution, the Opus /
Codex / scripted-proposer swarm with brief refinement, research packets, structure and view diagnostics, the page-image reader,
`research_doubles` and `research_signature`. Page images are never committed (git-ignored; their SHA-256 sums are in
`data/lp_images.sha256`); only counts and positions are published.

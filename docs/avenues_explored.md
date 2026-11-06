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
| Letter frequencies and IC (`research_structure diffs`, first table) | The unsolved sections' IC x 29 is 1.01-1.08, what uniform draws of the same length give (1.01-1.09); the readable sections are 1.70-2.15. Rune frequencies are flat and the same in all 11 sections (homogeneity p 0.98). A simple substitution is therefore out for these sections; anything with language-like letter frequencies is out |
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
| Numbers as text (`numbers`): 2,820 words and 167 lines read as numbers (base 29 both ways round, decimal concatenation of indexes, Gematria prime-value sum, index sum); fractions that are prime, square or Fibonacci against 99 shuffles. The "prime frequency" reading | Max abs z 2.0 over 21 readings, p = 0.63; the control (words that are primes in base 29) is found at max abs z 68. Whether the text is a polynomial in position (finite differences, orders 1-8) or a linear recurrence mod 29 (orders 2 and 3): no flag on any section; planted cubic and recurrence controls are flagged |
| Out-of-step prime stream (`research_windows`): F-free stretches scored with the English bigram model, then verified on text outside the stretch, over primes, Fibonacci, naturals, squares, triangular, pi and e digits | No flag; best real stage-2 z 3.7 against 3.4 for noise and 32-38 for the planted stream |
| Prime-valued shifts (the page 73 mechanism): every place they were tested | (a) IC sweep: `primes` and `prime_totients`, 28 scales, 3,000 offsets, three F treatments, also on differences and sums; (b) window search: primes (including prime-minus-one through the constant and the sign) at offsets 0-6,000 on F-free stretches, then verified outside the stretch; (c) crib test: the key implied by each red heading as a window of the prime sequence, every scale, offsets up to 20,000; (d) signature screen: primes and prime totients, scales 1-28, offsets 0, 7 and 1,000, plain and reversed forms. No flag or hit in any. These are position-keyed streams, which the pairwise diagnostics cannot see; the signature screen shows they also do not produce the repeat shortage. **There is no separate "next prime" or prime-permutation experiment on record in this project; if one was meant, it is not in this list** |

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
| Hidden data in the page images (OutGuess) | Pages 17-72 cannot be vanilla OutGuess output by the header rule (section 11), so a passphrase sweep is not worth running; default-key extraction returns nothing real on them. Other steganography tools are not tested |
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

## 11. Steganography checks on the page images (OutGuess)

* **Default-key extraction** (OutGuess 0.4 from Debian, all 75 files). Control: page 01 returns the 2,899-byte PGP signed message the
  owner got from the Boxentriq web extractor (anchor lines match). Nine pages return real payloads: 00, 01, 02 (2,899 B each, signed
  messages), 03 (31,809 B: signed message "Let the text guide you", a hex-encoded JPEG and a signature), 08 (140 B of text) and 10-13
  (1,234 B each, signed messages). Page 04's 7,524 bytes are random-looking (7.98 bits/byte, 38.6% printable, as random bytes) and its
  header is the 400 ppi kind below, so it is a false positive. Every other page either decodes the same header (`seed 41408, len 58152`,
  60 pages, so not a message; 19 of them return 58,152 random-looking bytes), crashes after printing that header (exit 136, 41 pages) or
  reports "datalen too long" (5 pages, including 05, 15 and 73).
* **Header fingerprint** (from the Uncovering Cicada wiki page "Outguess detection visual analysis", which says it is unfinished): OutGuess
  writes its own JPEG header, JFIF unit 0 with density 1x1, and `-p` sets the JPEG quality (default 75; 100 gives an all-ones quantisation
  table). All nine payload pages have JFIF 1.1, unit 0, 1x1, quality 75 (03, 08, 10, 11, 12) or 100 (00, 01, 02, 13). The other 66 pages,
  including every page 17-72, have unit 1, 400x400 dpi, quality 92, so they cannot be vanilla OutGuess output by that rule. No
  counterexample among the 75 files.
* **Reading:** the header test needs no passphrase, so it also excludes passphrase-keyed OutGuess on the unsolved pages. Caveats: it assumes
  the repo files are unmodified copies (the nine payloads survived, so those at least were not re-encoded; the wiki independently lists
  about 400 ppi for the later originals), the wiki's analysis is exploratory, and other steganography tools are not excluded.
* **Page 05's appended data (explained):** `05.jpg` is three parts: the page JPEG (336,353 bytes), a 360-character text block, and a
  byte-reversed copy of the same JPEG (336,353 bytes; it decodes to exactly the same pixels, and its end marker comes first and its
  start marker last). The text block is the hex encoding of a 5x5 number grid whose rows, columns and both diagonals sum to 1033
  (a prime); the visible page shows the same grid with 13 cells written as rune words. The 13 hidden numbers are the Gematria prime
  sums of those words (SHADOWS 341, AETHEREAL 366, BUFFERS 199, VOID 130, CARNAL 320, OBSCURA 245, FORM 91, MOBIUS 226, ANALOG 320,
  MOURNFUL 199, CABAL 341; all 13 match), so the appended data adds nothing the page does not already encode. An earlier note here
  said 72,700 bytes after the last end marker; that came from taking the last FFD9 in the file, which is inside the reversed copy.
  `10.jpg` is pages 10-13 concatenated (the last three are byte-identical to `11.jpg`, `12.jpg`, `13.jpg`).
* **Page 03's payload contains a small image:** a 587x109 grayscale JPEG (15,188 bytes, 400 dpi header, so not OutGuess output itself;
  default-key extraction returns nothing from it) showing one line of runes with a digit 5 and a digit 3 in it. Read by shape matching
  after scaling 2x: `TH M D EO F M A R  5  U AE NG R NG  3  EA M EO F IO` (18 runes in groups of 8, 5 and 5; the two digits are not
  runes). Shifting or reversing each group, or all 18 together, gives nothing English, but strings that short cannot be tested well.
  Not solved.
* **Not done:** page 08's two-letter groups, and anything on the 18-rune line beyond the shift check above.

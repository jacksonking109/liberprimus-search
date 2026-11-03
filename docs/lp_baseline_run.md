# Brute-force baseline on the Liber Primus sections

Reference run of the Phase 1 baseline (no models) on all imported sections.

```
lpswarm baseline --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --ledger lp.sqlite
```

- Alphabet: Gematria Primus (29 runes). Oracle: English, alpha = 0.01 per section, final
  Bonferroni check over all attempts on each section. Sections over 500 runes are scored on
  their first 500 decrypted runes.
- Search per section: Caesar (29 shifts); Vigenère / Beaufort / variant Beaufort and autokey
  with the 5000 commonest corpus words plus every key of length ≤ 2; keyword substitution;
  columnar widths 2–7 plus word-derived orders. Running key skipped (no key texts supplied).
  About 46.6k attempts per section, 1.16M in total, about 6 minutes on one core.
- 25 sections scored; 3 were skipped because they contain no runes (titles in Latin script,
  and a hex/number block).

## Known-answer check: sections the source lists as solved

| Section | Source's note (claim) | Found by baseline | Final pass (example key) |
| --- | --- | --- | --- |
| Runes - 01.jpg | substitution, reversed Gematria | yes | Beaufort, key [28] → "A WARNING BELIEVE NOTHING FROM THIS BOOK…" |
| 05.jpg | default Gematria | yes | shift 0 → "SOME WISDOM THE PRIMES ARE SACRED…" |
| 03.jpg-04.jpg | key DIVINITY, plaintext F skipped | **no** | needs a "skip F" Vigenère variant; DIVINITY is also not in the top-5000 words |
| 06.jpg-09.jpg/1 | shift 3, reversed Gematria | yes | Beaufort, key TH → "A KOAN A MAN DECIDED TO GO AND STUDY WITH A MASTER…" |
| 09.jpg/2 | shift 3, reversed Gematria | yes | Beaufort, key TH → "AN INSTRUCTION DO FOUR UNREASONABLE THINGS EACH DAY" |
| 10.jpg-13.jpg | default Gematria | yes | shift 0 → "THE LOSS OF DIVINITY THE CIRCUMFERENCE PRACTICES…" |
| 14.jpg-15.jpg | key FIRFUMFERENFE, plaintext F skipped | **no** | needs the "skip F" variant and that key |
| 16.jpg | default Gematria | yes | shift 0 → "AN INSTRUCTION QUESTION ALL THINGS…" |
| 56.jpg - 73.jpg | totient-based stream, F skipped | **no** | stream cipher outside the Phase 1 families |
| 57.jpg - 74.jpg | default Gematria | yes | shift 0 → "PARABLE LIKE THE INSTAR TUNNELING TO THE SURFACE…" |

7 of 10 found, with no other help. The 3 misses use mechanisms the Phase 1 families do not have.
That makes them concrete Phase 3 tests: can a model-driven generator propose those families?

## Unsolved sections

All 18 unsolved sections were searched with zero final passes and zero near misses. Everything
tried is recorded in the ledger as ruled out under `baseline/baseline`. As expected, nothing in
this search space produces English.

## Caveats

- Sections, not pages: the source has no page breaks inside multi-page sections.
- `56.jpg/2` and `56.jpg - 73.jpg` contain corrupted characters (U+FFFD) and an unknown rune
  (ᛂ). These are dropped, which can misalign the text after them.
- Decrypted previews print the alphabet's primary tokens, so ING shows as NG, K as C, V as U,
  Q as CW.

## Update: Phase 3 cipher language (skip resolution)

The two "skip F" sections are expressible in the cipher-program language with
`skip_mode: "resolve"` (each ᚠ may be a literal or an encrypted rune; a Viterbi search picks):

| Section | Spec | Result |
| --- | --- | --- |
| 03.jpg-04.jpg | repeat key [6,19,28,19,20,19,13,3], add, skip F (resolve) | "WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END OF ALL THINGS..." passes the final check at 50k attempts |
| 14.jpg-15.jpg | repeat key [29,19,25,29,28,10,29,11,25,11,20,29,11], add, skip F (resolve) | "A KOAN DURING A LESSON THE MASTER EXPLAINED THE I THE I IS THE VOICE OF THE CIRCUMFERENCE..." passes the final check at 50k attempts |
| 56.jpg - 73.jpg | prime-totient stream, sub, skip F | decodes "...END WITHIN THE DEEP WEB THERE EXISTS A PA..." then loses sync at the corrupted characters |

With "every ᚠ is a literal" (`skip_mode: "all"`) neither section passes. Resolved attempts are
calibrated against nulls decrypted by the same search (measured null FPR 0.0-0.3% at alpha 1%).
The keys come from the source's notes, so this validates the language and the scoring, not a
model's ability to find them: a model may have memorised these published solutions.

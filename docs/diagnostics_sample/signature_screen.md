# Which cipher families can reproduce the repeat signature?

**SYNTHETIC: English plaintext (training split) through the DSL's ciphers; compatibility is necessary, not evidence.**

A match is pre-specified: lag-1 ratio inside the 95% interval of the real ratio, and every lag from 2 to 8 inside 0.85-1.15. Ratios are equal-neighbour counts over the exact shuffle expectation of the same ciphertext.

Real signature (manifest sections 10-25): lag 1 86 doubles against 444 expected, ratio 0.19 (95% interval 0.15-0.24); lags 2-8: 0.99, 0.99, 1.03, 1.08, 1.03, 1.01, 0.98.

Solved plain-substitution text (sections 3, 7, 9, 27) has lag 1 at 0.44 (95% interval 0.29-0.65), below the synthetic English control, so the plaintext level is uncertain. Sensitivity (post hoc, not the pre-specified match): `loose` asks that the cipher lower the plaintext's own lag-1 ratio by a factor in 0.24-0.83 (real interval over the solved-text interval) with lags 2-8 flat.

Real text: unigram IC x 29 = 0.999, first-difference IC x 29 = 1.025 (uniform 1.0, language 1.6-2.0); both must be <= 1.15 for a `full` match.

Controls on 6 English windows of 5000: plaintext lag 1 0.58, lags 2-8 0.72, 0.90, 0.95, 1.01, 0.99, 1.01, 0.96, unigram IC 1.80, first-difference IC 1.12; iid noise lag 1 0.98. Positive control (not a DSL cipher): a random walk whose zero steps are thinned to 20% has lag 1 0.20, lags 2-8 0.99-1.02, unigram IC 1.00, first-difference IC 1.02: full match yes.

| family | candidates | errors | lag-1 ratio min / median / max | lag 1 in real interval | lags 2-8 flat | lag-only match | both ICs ok | full match | loose |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| control: no cipher | 3 | 0 | 0.58 / 0.58 / 0.58 | 0 | 0 | 0 | 0 | **0** | 0 |
| exp1 feedback (neighbour/chain, 8 forms x b) | 261 | 0 | 0.00 / 0.98 / 3.80 | 5 | 157 | 2 | 143 | **0** | 0 |
| exp2b two-shear Hill blocks, all shifts | 957 | 0 | 0.35 / 0.91 / 2.29 | 0 | 811 | 0 | 580 | **0** | 0 |
| exp3 progressive keys | 4873 | 0 | 0.46 / 0.97 / 1.97 | 0 | 3248 | 0 | 4872 | **0** | 0 |
| exp4 word keys under the reversed alphabet | 19882 | 0 | 0.46 / 0.91 / 1.42 | 0 | 1437 | 0 | 7867 | **0** | 0 |
| other position-keyed sequences | 840 | 0 | 0.74 / 0.96 / 1.33 | 0 | 810 | 0 | 834 | **0** | 0 |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | 25056 | 0 | 0.00 / 0.94 / 3.80 | 18 | 14131 | 5 | 13298 | **0** | 0 |
| random Hill blocks, sizes 2-4 (sample, no shift) | 6000 | 0 | 0.56 / 0.98 / 1.47 | 0 | 5650 | 0 | 5613 | **0** | 0 |
| block permutations, sizes 2-5 (all, no shift) | 152 | 0 | 0.58 / 0.75 / 0.90 | 0 | 12 | 0 | 0 | **0** | 0 |

Re-screened on 60 windows (300000 runes): matches first, then the closest lag-flat candidates.

| family | cipher | lag 1 | lags 2-8 min-max | unigram IC | diff IC | lag-only match | full | loose |
| --- | --- | ---: | --- | ---: | ---: | --- | --- | --- |
| exp1 feedback (neighbour/chain, 8 forms x b) | sub; constant 7; neighbor sub lag 1 prev reset word (before the key) | 0.20 | 0.88-1.03 | 1.07 | 1.61 | yes | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 7; neighbor sub lag 1 prev reset word (before the key) | 0.20 | 0.88-1.03 | 1.07 | 1.61 | yes | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 7; neighbor sub lag 1 next reset word (before the key) | 0.21 | 0.95-1.05 | 1.15 | 1.42 | yes | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 7; neighbor rsub lag 1 prev reset word (before the key) | 0.22 | 0.89-1.03 | 1.10 | 1.62 | yes | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 15; neighbor rsub lag 1 prev reset word (before the key) | 0.23 | 0.86-0.99 | 1.07 | 1.63 | yes | no | no |
| exp1 feedback (neighbour/chain, 8 forms x b) | sub; constant 15; neighbor sub lag 1 prev reset word (before the key) | 0.24 | 0.86-0.98 | 1.06 | 1.62 | yes | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 15; neighbor sub lag 1 prev reset word (before the key) | 0.24 | 0.86-0.98 | 1.06 | 1.62 | yes | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 18; neighbor rsub lag 1 next x3 reset word (before the key) | 0.55 | 0.92-1.02 | 1.13 | 1.08 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 19; chain sub lag 1 next x3 reset word (before the key) | 0.57 | 0.86-1.00 | 1.14 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 15; chain rsub lag 1 next x3 reset word (before the key) | 0.58 | 0.91-1.00 | 1.09 | 1.08 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 1; neighbor rsub lag 1 next x3 reset word (before the key) | 0.59 | 0.91-1.00 | 1.12 | 1.08 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 4; neighbor rsub lag 1 next x3 reset word (before the key) | 0.59 | 0.92-1.00 | 1.11 | 1.07 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 17; neighbor rsub lag 1 prev x3 reset word (before the key) | 0.59 | 0.91-1.00 | 1.08 | 1.11 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 15; neighbor rsub lag 1 next x3 reset word (before the key) | 0.60 | 0.91-1.00 | 1.10 | 1.09 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 19; neighbor sub lag 1 next x3 reset word (before the key) | 0.61 | 0.93-1.01 | 1.10 | 1.03 | no | no | no |
| exp1 feedback (neighbour/chain, 8 forms x b) | sub; constant 2; chain sub lag 1 prev reset word (before the key) | 0.62 | 0.93-0.99 | 1.12 | 1.13 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 19; chain sub lag 1 prev x3 reset word (before the key) | 0.62 | 0.88-1.00 | 1.07 | 1.07 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 3; neighbor rsub lag 1 next x3 reset word (before the key) | 0.63 | 0.88-1.01 | 1.13 | 1.07 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 15; neighbor rsub lag 1 prev x3 reset word (before the key) | 0.63 | 0.93-1.09 | 1.09 | 1.13 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 8; neighbor sub lag 1 next x3 reset word (before the key) | 0.63 | 0.92-1.02 | 1.15 | 1.03 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 5; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 1; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 2; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 3; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 4; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 6; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 7; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 8; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 9; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |
| wider feedback mixers (kind x op x lag x dir x times x reset x position x shift) | sub; constant 10; chain sub lag 1 next x3 reset word (after the key) | 0.63 | 0.90-0.99 | 1.12 | 1.05 | no | no | no |

Seconds: 255.1.

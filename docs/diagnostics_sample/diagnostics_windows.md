# Local-window search for an out-of-step prime stream

**EXPLORATORY: a stage-2 flag is a lead for the real oracle, not a result.**

Stage 1: bigram log-likelihood of every decryption of the longest F-free stretches (orientation x scale x constant x offset 0..6000, sequences ['primes']). Stage 2: the best stage-1 candidates decrypted over the first 800 runes with the resolved F-skip and scored on the runes outside the stretch, against 40 random candidates. Lead if z >= 8. 

| section | stretch | stage-1 best per symbol (z vs bulk; shuffled best per symbol) | best stage-2 z | best candidate | flag |
| --- | --- | --- | ---: | --- | --- |
| 10 | 73 runes at 645 | -3.76 (4.4; -3.73) | 1.8 | primes reversed x1 +8 @3082 | no |
| 10 | 66 runes at 511 | -3.52 (4.9; -3.70) | 2.1 | primes reversed x28 +5 @4351 | no |
| 12 | 114 runes at 560 | -3.94 (4.7; -3.95) | 2.5 | primes plain x1 +0 @3885 | no |
| 12 | 73 runes at 279 | -3.81 (4.2; -3.69) | 2.4 | primes plain x1 +7 @1963 | no |
| 12 | 69 runes at 438 | -3.70 (4.4; -3.55) | 2.7 | primes plain x1 +0 @873 | no |
| 13 | 183 runes at 150 | -4.05 (5.3; -4.15) | 2.3 | primes reversed x1 +9 @2257 | no |
| 13 | 63 runes at 86 | -3.66 (4.3; -3.58) | 1.3 | primes plain x1 +14 @3530 | no |
| 14 | 126 runes at 35 | -4.01 (4.6; -3.93) | 2.0 | primes plain x1 +10 @146 | no |
| 14 | 76 runes at 687 | -3.80 (4.3; -3.73) | 2.8 | primes plain x28 +28 @2354 | no |
| 14 | 64 runes at 595 | -3.58 (4.6; -3.59) | 2.8 | primes reversed x28 +20 @4747 | no |
| 16 | 88 runes at 516 | -3.90 (4.3; -3.73) | 2.2 | primes plain x28 +19 @624 | no |
| 16 | 64 runes at 141 | -3.57 (4.7; -3.50) | 2.7 | primes plain x1 +0 @3432 | no |
| 16 | 61 runes at 398 | -3.59 (4.5; -3.51) | 2.8 | primes plain x1 +20 @2665 | no |
| 17 | 91 runes at 437 | -3.82 (4.7; -3.87) | 2.0 | primes reversed x1 +17 @1551 | no |
| 18 | 101 runes at 442 | -3.80 (5.0; -3.76) | 2.0 | primes plain x28 +12 @1173 | no |
| 18 | 93 runes at 594 | -3.79 (4.8; -3.72) | 1.9 | primes reversed x1 +9 @1457 | no |
| 20 | 88 runes at 168 | -3.83 (4.5; -3.77) | 2.7 | primes plain x28 +13 @5382 | no |
| 20 | 88 runes at 555 | -3.87 (4.4; -3.79) | 2.8 | primes plain x1 +28 @1738 | no |
| 20 | 79 runes at 475 | -3.67 (4.8; -3.73) | 3.8 | primes plain x1 +13 @872 | no |
| 22 | 118 runes at 45 | -3.98 (4.5; -3.98) | 1.1 | primes reversed x1 +21 @4789 | no |
| 22 | 64 runes at 338 | -3.57 (4.7; -3.59) | 2.5 | primes plain x1 +8 @2202 | no |
| 24 | 77 runes at 346 | -3.78 (4.4; -3.76) | 4.2 | primes plain x1 +24 @4695 | no |
| 24 | 76 runes at 445 | -3.71 (4.6; -3.75) | 1.9 | primes plain x28 +1 @726 | no |
| 24 | 72 runes at 273 | -3.61 (4.8; -3.70) | 2.3 | primes plain x28 +4 @1137 | no |
| 25 | 129 runes at 66 | -4.00 (4.7; -4.00) | 1.2 | primes plain x1 +28 @2384 | no |
| control: English, prime-minus-one stream, F-skip | 123 runes at 125 | -2.75 (10.1; -3.97) | 35.6 | primes plain x1 +28 @501 | **LEAD** |
| control: English, prime-minus-one stream, F-skip | 84 runes at 584 | -2.67 (8.6; -3.85) | 37.1 | primes plain x1 +28 @501 | **LEAD** |
| control: English, prime-minus-one stream, F-skip | 79 runes at 1 | -2.58 (8.7; -3.75) | 36.8 | primes plain x1 +28 @500 | **LEAD** |
| control: same, plus one extra skipped index at 200 | 131 runes at 125 | -4.03 (4.6; -4.05) | 40.5 | primes plain x1 +28 @501 | **LEAD** |
| control: same, plus one extra skipped index at 200 | 79 runes at 1 | -2.58 (8.7; -3.80) | 32.6 | primes plain x1 +28 @500 | **LEAD** |
| control: uniform noise | 123 runes at 36 | -3.98 (4.7; -3.94) | 3.6 | primes reversed x1 +9 @1197 | no |
| control: uniform noise | 88 runes at 254 | -3.80 (4.6; -3.78) | 3.1 | primes plain x28 +27 @3465 | no |
| control: uniform noise | 88 runes at 435 | -3.71 (5.0; -3.87) | 1.9 | primes reversed x28 +4 @988 | no |

Limits: English bigram model only; one sequence family (primes, which includes prime-minus-one through the constant) unless widened; stretches of 60 or more runes, so a stream broken more often than that is not reachable; the verification window is the first runes of the section.


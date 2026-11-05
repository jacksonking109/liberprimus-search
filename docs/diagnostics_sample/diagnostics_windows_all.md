# Local-window search for an out-of-step prime stream

**EXPLORATORY: a stage-2 flag is a lead for the real oracle, not a result.**

Stage 1: bigram log-likelihood of every decryption of the longest F-free stretches (orientation x scale x constant x offset 0..6000, sequences ['primes', 'fibonacci', 'naturals', 'squares', 'triangular', 'pi_digits', 'e_digits']). Stage 2: the best stage-1 candidates decrypted over the first 800 runes with the resolved F-skip and scored on the runes outside the stretch, against 40 random candidates. Lead if z >= 8. 

| section | stretch | stage-1 best per symbol (z vs bulk; shuffled best per symbol) | best stage-2 z | best candidate | flag |
| --- | --- | --- | ---: | --- | --- |
| 10 | 73 runes at 645 | -3.71 (4.6; -3.64) | 2.7 | pi_digits plain x28 +21 @5023 | no |
| 10 | 66 runes at 511 | -3.47 (5.2; -3.58) | 2.6 | primes reversed x28 +22 @1137 | no |
| 12 | 114 runes at 560 | -3.94 (4.7; -3.84) | 2.5 | primes plain x1 +0 @3885 | no |
| 12 | 73 runes at 279 | -3.80 (4.3; -3.62) | 3.0 | e_digits reversed x28 +15 @3351 | no |
| 12 | 69 runes at 438 | -3.64 (4.5; -3.55) | 2.5 | primes plain x1 +0 @873 | no |
| 13 | 183 runes at 150 | -4.05 (5.2; -4.15) | 2.3 | primes reversed x1 +9 @2257 | no |
| 13 | 63 runes at 86 | -3.66 (4.2; -3.58) | 1.3 | primes plain x1 +14 @3530 | no |
| 14 | 126 runes at 35 | -3.91 (5.2; -3.87) | 1.9 | primes plain x1 +10 @146 | no |
| 14 | 76 runes at 687 | -3.71 (4.6; -3.73) | 2.8 | primes reversed x28 +1 @1394 | no |
| 14 | 64 runes at 595 | -3.58 (4.8; -3.59) | 3.7 | e_digits plain x1 +16 @2017 | no |
| 16 | 88 runes at 516 | -3.71 (5.0; -3.73) | 3.1 | e_digits reversed x1 +14 @2528 | no |
| 16 | 64 runes at 141 | -3.57 (4.8; -3.50) | 2.7 | primes plain x1 +0 @3432 | no |
| 16 | 61 runes at 398 | -3.59 (4.5; -3.51) | 2.9 | e_digits reversed x1 +15 @1933 | no |
| 17 | 91 runes at 437 | -3.77 (4.8; -3.83) | 1.9 | primes plain x1 +16 @993 | no |
| 18 | 101 runes at 442 | -3.80 (5.1; -3.76) | 2.0 | primes plain x28 +12 @1173 | no |
| 18 | 93 runes at 594 | -3.79 (4.9; -3.69) | 3.7 | e_digits plain x28 +26 @40 | no |
| 20 | 88 runes at 168 | -3.78 (4.7; -3.76) | 2.7 | primes plain x28 +13 @5382 | no |
| 20 | 88 runes at 555 | -3.78 (4.6; -3.64) | 1.0 | primes plain x28 +0 @445 | no |
| 20 | 79 runes at 475 | -3.67 (4.9; -3.73) | 2.8 | primes reversed x28 +11 @3834 | no |
| 22 | 118 runes at 45 | -3.91 (4.9; -3.94) | 1.7 | pi_digits reversed x1 +24 @462 | no |
| 22 | 64 runes at 338 | -3.56 (4.7; -3.52) | 2.5 | pi_digits plain x28 +16 @3419 | no |
| 24 | 77 runes at 346 | -3.76 (4.5; -3.65) | 2.1 | primes plain x28 +6 @1319 | no |
| 24 | 76 runes at 445 | -3.71 (4.7; -3.61) | 3.2 | e_digits plain x28 +20 @2722 | no |
| 24 | 72 runes at 273 | -3.61 (4.9; -3.61) | 2.3 | primes plain x28 +4 @1137 | no |
| 25 | 129 runes at 66 | -3.93 (4.9; -4.00) | 1.0 | pi_digits plain x28 +4 @1163 | no |
| control: English, prime-minus-one stream, F-skip | 123 runes at 125 | -2.75 (10.2; -3.97) | 35.6 | primes plain x1 +28 @501 | **LEAD** |
| control: English, prime-minus-one stream, F-skip | 84 runes at 584 | -2.67 (8.7; -3.73) | 37.1 | primes plain x1 +28 @501 | **LEAD** |
| control: English, prime-minus-one stream, F-skip | 79 runes at 1 | -2.58 (8.8; -3.65) | 36.8 | primes plain x1 +28 @500 | **LEAD** |
| control: same, plus one extra skipped index at 200 | 131 runes at 125 | -3.95 (5.0; -4.02) | 38.4 | primes plain x1 +28 @501 | **LEAD** |
| control: same, plus one extra skipped index at 200 | 79 runes at 1 | -2.58 (8.8; -3.69) | 32.6 | primes plain x1 +28 @500 | **LEAD** |
| control: uniform noise | 123 runes at 36 | -3.85 (5.3; -3.94) | 3.4 | primes reversed x1 +9 @1197 | no |
| control: uniform noise | 88 runes at 254 | -3.80 (4.6; -3.75) | 2.0 | e_digits plain x1 +15 @5664 | no |
| control: uniform noise | 88 runes at 435 | -3.69 (5.2; -3.75) | 1.6 | pi_digits plain x1 +15 @5419 | no |

Limits: English bigram model only; one sequence family (primes, which includes prime-minus-one through the constant) unless widened; stretches of 60 or more runes, so a stream broken more often than that is not reachable; the verification window is the first runes of the section.


# Literal readings of "their numbers are the direction"

**EXPLORATORY; no oracle, no models.**

## 1. The prime value of a rune as the key for the next (self-keyed)

Sections of 300+ runes (10, 12, 13, 14, 16, 17, 18, 20, 22, 24, 25); null: the same decryption of each section shuffled (50 times). Flag: IC x 29 >= 1.25 and above the null maximum.

| variant | best IC x 29 | null mean / max | flag |
| --- | ---: | --- | --- |
| p = c - key, key = prime of rune t-1 | 1.033 | 1.021 / 1.055 | no |
| p = c + key, key = prime of rune t-1 | 1.025 | 1.024 / 1.062 | no |
| p = c - key, key = prime of rune t-2 | 1.038 | 1.021 / 1.071 | no |
| p = c + key, key = prime of rune t-2 | 1.026 | 1.021 / 1.072 | no |
| p = c - key, key = prime of rune t-3 | 1.022 | 1.020 / 1.060 | no |
| p = c + key, key = prime of rune t-3 | 1.014 | 1.027 / 1.083 | no |
| p = c - key, key = running sum of primes before t | 1.023 | 1.021 / 1.091 | no |
| p = c + key, key = running sum of primes before t | 1.024 | 1.023 / 1.048 | no |

English enciphered the same way, against the repeat signature (real: lag 1 0.19, lags 2-8 at chance, ICs 1.00 / 1.03):

| variant | lag 1 | lags 2-8 | unigram IC | difference IC | full match |
| --- | ---: | --- | ---: | ---: | --- |
| prime of rune t-1, sign + | 0.75 | 0.94-1.07 | 1.01 | 1.02 | no |
| prime of rune t-1, sign - | 1.23 | 0.97-1.14 | 1.01 | 1.03 | no |
| prime of rune t-2, sign + | 0.96 | 0.83-1.08 | 1.01 | 1.00 | no |
| prime of rune t-2, sign - | 0.98 | 0.96-1.16 | 1.01 | 1.00 | no |
| prime of rune t-3, sign + | 0.98 | 0.80-1.06 | 1.01 | 1.00 | no |
| prime of rune t-3, sign - | 0.98 | 0.91-1.25 | 1.02 | 1.00 | no |
| running sum of primes before t, sign + | 1.09 | 0.89-1.06 | 1.00 | 1.00 | no |
| running sum of primes before t, sign - | 1.00 | 0.97-1.05 | 1.01 | 1.00 | no |

## 2. Prime values as steps through a page (best walk of 30+ runes, English bigram score)

Null: the same search on the page's runes shuffled (20 times). p = share of shuffles whose best walk scores at least as well. A walk stops when it would revisit a position, so short pages often have no walk of 30 runes (score -99 in a shuffle, which lowers the null mean).

| page | runes | best score | null mean / max | p |
| ---: | ---: | ---: | --- | ---: |
| 17 | 262 | -4.474 | -4.555 / -4.152 | 0.476 |
| 18 | 266 | -4.528 | -9.372 / -3.875 | 0.429 |
| 19 | 201 | -5.110 | -4.426 / -3.590 | 0.857 |
| 20 | 217 | -4.662 | -4.528 / -3.852 | 0.714 |
| 21 | 261 | -4.460 | -4.725 / -3.833 | 0.238 |
| 22 | 263 | -4.664 | -4.928 / -4.255 | 0.238 |
| 24 | 208 | -4.816 | -33.081 / -3.879 | 0.238 |
| 25 | 255 | -4.817 | -9.232 / -3.932 | 0.762 |
| 26 | 268 | -4.427 | -4.775 / -4.131 | 0.095 |
| 27 | 263 | -4.427 | -4.575 / -3.837 | 0.333 |
| 28 | 273 | -5.150 | -4.308 / -3.632 | 1.000 |
| 29 | 261 | -4.783 | -4.650 / -4.131 | 0.619 |
| 30 | 272 | -4.409 | -4.439 / -3.564 | 0.429 |
| 31 | 137 | -4.033 | -42.511 / -4.241 | 0.048 |
| 32 | 159 | -4.623 | -42.426 / -4.328 | 0.286 |
| 33 | 267 | -4.396 | -4.697 / -3.945 | 0.238 |
| 34 | 273 | -4.754 | -9.310 / -3.964 | 0.762 |
| 35 | 260 | -4.960 | -14.007 / -3.985 | 0.762 |
| 36 | 271 | -4.401 | -4.496 / -4.001 | 0.286 |
| 37 | 269 | -4.501 | -4.740 / -4.184 | 0.333 |
| 38 | 273 | -4.441 | -4.474 / -3.989 | 0.381 |
| 39 | 131 | -4.514 | -70.780 / -4.191 | 0.095 |
| 40 | 213 | -4.488 | -9.200 / -3.965 | 0.571 |
| 41 | 270 | -4.640 | -4.484 / -3.595 | 0.667 |
| 42 | 273 | -4.968 | -4.333 / -3.795 | 1.000 |
| 43 | 265 | -5.055 | -4.362 / -3.683 | 1.000 |
| 44 | 234 | -4.571 | -13.674 / -3.804 | 0.857 |
| 45 | 269 | -4.897 | -4.572 / -3.704 | 0.905 |
| 46 | 277 | -4.075 | -9.228 / -3.971 | 0.095 |
| 47 | 263 | -4.815 | -4.696 / -3.993 | 0.667 |
| 48 | 269 | -4.802 | -13.899 / -4.070 | 0.810 |
| 51 | 261 | -3.887 | -4.526 / -3.846 | 0.095 |
| 52 | 271 | -4.074 | -4.621 / -4.036 | 0.095 |
| 53 | 238 | -4.408 | -4.715 / -3.985 | 0.143 |
| 54 | 228 | -4.446 | -13.944 / -3.634 | 0.476 |
| 55 | 228 | -4.513 | -9.411 / -3.972 | 0.381 |
| 56 | 240 | -4.312 | -4.378 / -3.873 | 0.476 |
| 57 | 231 | -4.417 | -9.221 / -3.755 | 0.619 |
| 58 | 273 | -3.903 | -4.482 / -4.069 | 0.048 |
| 59 | 272 | -4.336 | -4.572 / -3.989 | 0.286 |
| 60 | 274 | -5.078 | -9.318 / -4.003 | 0.857 |
| 61 | 273 | -4.758 | -4.548 / -3.723 | 0.714 |
| 62 | 270 | -4.344 | -4.592 / -4.031 | 0.286 |
| 63 | 270 | -4.491 | -4.599 / -3.953 | 0.429 |
| 64 | 274 | -4.464 | -4.453 / -3.914 | 0.524 |
| 65 | 271 | -4.686 | -9.446 / -4.035 | 0.476 |
| 68 | 92 | -4.528 | -75.477 / -4.396 | 0.143 |
| 69 | 263 | -4.913 | -4.664 / -4.157 | 0.857 |
| 70 | 179 | -4.458 | -32.991 / -4.284 | 0.238 |
| 71 | 232 | -4.317 | -4.714 / -3.948 | 0.190 |

2 of 50 pages at p <= 0.05 (about 2.5 expected by chance); smallest p 0.048.

## 3. Square pages as grids, against the hint numbers 563, 569, 1136, 1033, 3301, 121, 464

Page 23 (14 x 14): rows [862, 864, 840, 675, 720, 816, 860, 598, 813, 566, 814, 629, 720, 804]; columns [818, 842, 743, 770, 1082, 652, 610, 856, 856, 702, 667, 610, 513, 860]; diagonals [846, 678]; total 10581.
Hits: 3 (3x3 at row 10 col 8: sum 563; 6x6 at row 5 col 1: circumference 1136; 6x6 at row 6 col 5: circumference 1136); the same runes shuffled give 4.3 on average.

Page 49 (11 x 11): rows [563, 617, 287, 540, 743, 513, 577, 579, 603, 537, 486]; columns [569, 429, 641, 669, 518, 611, 463, 690, 378, 578, 499]; diagonals [519, 440]; total 6045.
Hits: 7 (row 1 = 563; column 1 = 569; 3x3 at row 5 col 4: sum 569; 4x4 at row 3 col 6: circumference 464; 5x5 at row 3 col 6: sum 1136; 5x5 at row 4 col 4: circumference 1136; 8x8 at row 3 col 4: circumference 1136); the same runes shuffled give 2.5 on average.


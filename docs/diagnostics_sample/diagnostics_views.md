# Assumption audit: language-agnostic and data views

**EXPLORATORY: fixed readings and sweeps, no language model; a flag is a lead to inspect, not a result.**

## 1. Decrypt, then index of coincidence (any language)

Window: first 600 runes. Families: 8 sequences x 28 scales x 3000 offsets x 3 F treatments; plus every packet candidate that can be evaluated. Flag: IC x 29 >= 1.25 and above the shuffled-ciphertext maximum (2 replicates). Natural language gives about 1.6-2.0. 

| section | best IC | z vs bulk | shuffled max | best candidate | longest F-free stretch: IC (null max, floor) | flag | packets: best IC (null max) |
| ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 10 | 1.225 | 5.2 | 1.235 | primes x27 @45 (F literal, key advances) | 66 runes: 1.933 (1.987, 2.11) | no | 1.061 (1.048) |
| 12 | 1.141 | 6.6 | 1.154 | prime_totients x4 @868 (F literal, key does not advance) | 73 runes: 1.843 (2.174, 2.23) | no | 1.059 (1.056) |
| 13 | 1.186 | 8.2 | 1.175 | e_digits x7 @1331 (F literal, key advances) | 183 runes: 1.303 (1.320, 1.34) | no | 1.107 (1.106) |
| 14 | 1.163 | 6.1 | 1.173 | primes x13 @1643 (F literal, key does not advance) | 126 runes: 1.418 (1.510, 1.61) | no | 1.028 (1.059) |
| 16 | 1.171 | 6.6 | 1.167 | primes x27 @2166 (F literal, key advances) | 84 runes: 1.589 (1.797, 1.90) | no | 1.026 (1.050) |
| 17 | 1.172 | 6.0 | 1.183 | pi_digits x17 @1629 (F literal, key advances) | 91 runes: 1.693 (1.806, 1.86) | no | 1.037 (1.066) |
| 18 | 1.202 | 5.1 | 1.213 | primes x8 @204 (F literal, key advances) | 101 runes: 1.516 (1.688, 1.80) | no | 1.025 (1.054) |
| 20 | 1.135 | 7.5 | 1.133 | prime_totients x12 @1650 (F literal, key advances) | 88 runes: 1.598 (1.712, 1.80) | no | 1.026 (1.062) |
| 22 | 1.215 | 6.4 | 1.197 | primes x11 @130 (F literal, key does not advance) | 118 runes: 1.433 (1.546, 1.58) | no | 1.024 (1.051) |
| 24 | 1.175 | 6.3 | 1.193 | prime_totients x10 @362 (F literal, key advances) | 77 runes: 1.725 (1.992, 2.09) | no | 1.075 (1.056) |
| 25 | 1.204 | 7.5 | 1.205 | prime_totients x13 @629 (F literal, key advances) | 129 runes: 1.359 (1.493, 1.56) | no | 1.127 (1.091) |

Synthetic controls (their answers are known):

| case | best IC | shuffled max | flag | best candidate |
| --- | ---: | ---: | --- | --- |
| English through a totient stream, offset 777 | 1.773 | 1.173 | **FLAG** | primes x1 @777 (F untouched) |
| English through a Fibonacci stream with the F-skip (F literal iff plaintext F; ambiguous as on the real pages) | 1.215 | 1.265 | no | pi_digits x3 @1524 (F literal, key advances) |
| non-English letters (iid, skewed) through a prime stream | 3.358 | 1.170 | **FLAG** | primes x2 @345 (F literal, key advances) |
| iid uniform noise (no cipher) | 1.156 | 1.146 | no | primes x8 @1155 (F literal, key advances) |

Limits: the three F treatments assume each F is literal for every F or for none; the documented F-skip pages need each F resolved separately, so those are only reachable through the longest F-free stretch, and a stretch of 60-120 runes searched over about 700,000 candidates reaches an IC from noise alone that language also reaches (see the null mean and maximum): the check is blind there. A stream that falls out of step partway (a skip at one index) is in the same position.

## 2. Runes as binary data

Readings: base-29 integer to bytes (both digit orders), 5-bit packing, one byte per rune, rune pairs. Hits are valid zlib/gzip/bzip2/xz streams or magic numbers at offsets 0-31 (chance is negligible). The statistics are calibrated as the maximum over all readings x statistics, 99 shuffles.

| section | runes | hits | max |z| | p (max over stats) | top statistic |
| --- | ---: | --- | ---: | ---: | --- |
| 10 | 729 | 0 | 1.9 | 0.640 | one byte per rune: lzma ratio (-1.9) |
| 12 | 693 | 0 | 2.5 | 0.260 | base 29, digits least significant first: entropy (-2.5) |
| 13 | 333 | 0 | 2.0 | 0.350 | base 29, digits least significant first: printable fraction (-2.0) |
| 14 | 1729 | 0 | 1.5 | 0.900 | 5-bit packing: longest printable run (1.5) |
| 16 | 1894 | 0 | 2.0 | 0.520 | 5-bit packing: longest printable run (2.0) |
| 17 | 1021 | 0 | 1.6 | 0.810 | two runes to one byte: printable fraction (-1.6) |
| 18 | 1433 | 0 | 2.1 | 0.420 | two runes to one byte: longest printable run (2.1) |
| 20 | 1468 | 0 | 1.9 | 0.640 | base 29, digits least significant first: entropy (-1.9) |
| 22 | 2474 | 0 | 2.4 | 0.310 | 5-bit packing: printable fraction (2.4) |
| 24 | 534 | 0 | 2.1 | 0.430 | one byte per rune: zlib ratio (2.1) |
| 25 | 308 | 0 | 2.3 | 0.510 | base 29, digits most significant first: lzma ratio (-2.3) |
| 3 (reference) | 157 | 0 | 2.8 | 0.120 | one byte per rune: zlib ratio (-2.8) |
| 7 (reference) | 629 | 0 | 58.0 | 0.010 | two runes to one byte: zlib ratio (-58.0) |
| 9 (reference) | 89 | 0 | 5.1 | 0.010 | base 29, digits most significant first: longest printable run (5.1) |
| 27 (reference) | 94 | 0 | 2.9 | 0.180 | base 29, digits most significant first: longest printable run (2.9) |

Controls:

| case | hits | max |z| | p | top statistic |
| --- | --- | ---: | ---: | --- |
| zlib-compressed text written in base 29 | base 29: valid zlib stream | 2.1 | 0.430 | 5-bit packing: entropy |
| random bytes written in base 29 | none | 2.5 | 0.220 | one byte per rune: lzma ratio |
| uniform random runes | none | 3.2 | 0.100 | two runes to one byte: longest printable run |
| English plaintext runes | none | 15.1 | 0.010 | one byte per rune: zlib ratio |

Limit: encrypted binary data (uniform bytes) is undetectable by these views.

## 3. Numbers as text

2820 words and 167 lines of the unsolved sections read as numbers; fractions that are prime / square / Fibonacci against 99 shuffles (runes permuted, word and line lengths fixed). Max |z| 2.0 over 21 readings, p 0.630.

| reading | observed | shuffle mean | z |
| --- | ---: | ---: | ---: |
| W3 decimal concatenation of indexes: fraction square | 0.0099 | 0.0135 | -2.0 |
| W3 decimal concatenation of indexes: fraction Fibonacci | 0.0089 | 0.0114 | -1.3 |
| W4 sum of Gematria prime values: fraction square | 0.0429 | 0.0383 | +1.2 |
| L2 base 29, least significant first: fraction prime | 0.0000 | 0.0093 | -1.2 |
| W5 sum of indexes: fraction Fibonacci | 0.0507 | 0.0557 | -1.1 |
| W2 base 29, least significant first: fraction Fibonacci | 0.0096 | 0.0113 | -0.9 |

Controls:

| case | max |z| | p |
| --- | ---: | ---: |
| words that are primes written in base 29 | 68.2 | 0.010 |
| words from random runes | 1.4 | 0.860 |

Does the text itself look like a generated number sequence? IC x 29 of the finite differences (orders 1-8) and of the best linear-recurrence residual (orders 2 and 3), flag rule IC >= 1.25 and above the shuffled maximum:

| section | best difference IC | best order-2 IC | best order-3 IC | flag |
| ---: | ---: | ---: | ---: | --- |
| 10 | 1.023 | 1.051 | 1.072 | no |
| 12 | 1.046 | 1.051 | 1.071 | no |
| 13 | 1.054 | 1.082 | 1.120 | no |
| 14 | 1.049 | 1.050 | 1.076 | no |
| 16 | 1.030 | 1.049 | 1.080 | no |
| 17 | 1.017 | 1.042 | 1.068 | no |
| 18 | 1.047 | 1.046 | 1.061 | no |
| 20 | 1.023 | 1.049 | 1.070 | no |
| 22 | 1.013 | 1.048 | 1.063 | no |
| 24 | 1.033 | 1.065 | 1.088 | no |
| 25 | 1.080 | 1.101 | 1.152 | no |

Sequence-fit controls:

| case | best order-2 IC | best order-3 IC | flag |
| --- | ---: | ---: | --- |
| cubic polynomial in position | 2.015 | 29.000 | **FLAG** |
| second-order recurrence (3, 5) | 29.000 | 29.000 | **FLAG** |
| uniform random runes | 1.064 | 1.073 | no |


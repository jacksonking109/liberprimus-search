# Assumption audit: language-agnostic and data views

**EXPLORATORY: fixed readings and sweeps, no language model; a flag is a lead to inspect, not a result.**

**Run on the neighbour sums c[i]+c[i-1] (mod 29) of each section, not on the runes themselves.**

## 1. Decrypt, then index of coincidence (any language)

Window: first 600 runes. Families: 8 sequences x 28 scales x 3000 offsets x 3 F treatments; plus every packet candidate that can be evaluated. Flag: IC x 29 >= 1.25 and above the shuffled-ciphertext maximum (2 replicates). Natural language gives about 1.6-2.0. 

| section | best IC | z vs bulk | shuffled max | best candidate | longest F-free stretch: IC (null max, floor) | flag | packets: best IC (null max) |
| ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 10 | 1.134 | 6.5 | 1.162 | primes x3 @1753 (F literal, key does not advance) | 68 runes: 1.808 (1.935, 2.10) | no | n/a |
| 12 | 1.112 | 7.0 | 1.127 | primes x17 @2199 (F literal, key does not advance) | 120 runes: 1.422 (1.617, 1.68) | no | n/a |
| 13 | 1.195 | 7.2 | 1.195 | primes x9 @617 (F literal, key advances) | 110 runes: 1.461 (1.616, 1.73) | no | n/a |
| 14 | 1.170 | 6.1 | 1.198 | primes x1 @535 (F literal, key advances) | 71 runes: 1.727 (2.031, 2.18) | no | n/a |
| 16 | 1.164 | 6.3 | 1.176 | prime_totients x2 @2123 (F literal, key advances) | 81 runes: 1.647 (1.790, 1.90) | no | n/a |
| 17 | 1.160 | 6.0 | 1.170 | pi_digits x27 @2386 (F literal, key does not advance) | 119 runes: 1.421 (1.524, 1.58) | no | n/a |
| 18 | 1.132 | 7.1 | 1.138 | primes x17 @1344 (F literal, key does not advance) | 118 runes: 1.407 (1.588, 1.63) | no | n/a |
| 20 | 1.152 | 6.4 | 1.153 | prime_totients x3 @1961 (F literal, key does not advance) | 84 runes: 1.714 (1.838, 1.87) | no | n/a |
| 22 | 1.131 | 7.0 | 1.145 | primes x10 @2584 (F literal, key advances) | 138 runes: 1.420 (1.473, 1.54) | no | n/a |
| 24 | 1.153 | 7.4 | 1.159 | primes x4 @2619 (F literal, key advances) | 109 runes: 1.468 (1.601, 1.68) | no | n/a |
| 25 | 1.388 | 6.4 | 1.456 | primes x9 @1251 (F literal, key does not advance) | 62 runes: 1.902 (2.116, 2.28) | no | n/a |

Synthetic controls (their answers are known):

| case | best IC | shuffled max | flag | best candidate |
| --- | ---: | ---: | --- | --- |
| English through a totient stream, offset 777 | 1.773 | 1.173 | **FLAG** | primes x1 @777 (F untouched) |
| English through a Fibonacci stream with the F-skip (F literal iff plaintext F; ambiguous as on the real pages) | 1.215 | 1.265 | no | pi_digits x3 @1524 (F literal, key advances) |
| non-English letters (iid, skewed) through a prime stream | 3.358 | 1.170 | **FLAG** | primes x2 @345 (F literal, key advances) |
| iid uniform noise (no cipher) | 1.156 | 1.146 | no | primes x8 @1155 (F literal, key advances) |

Limits: the three F treatments assume each F is literal for every F or for none; the documented F-skip pages need each F resolved separately, so those are only reachable through the longest F-free stretch, and a stretch of 60-120 runes searched over about 700,000 candidates reaches an IC from noise alone that language also reaches (see the null mean and maximum): the check is blind there. A stream that falls out of step partway (a skip at one index) is in the same position.


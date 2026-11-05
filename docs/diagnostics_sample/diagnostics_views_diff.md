# Assumption audit: language-agnostic and data views

**EXPLORATORY: fixed readings and sweeps, no language model; a flag is a lead to inspect, not a result.**

**Run on the first differences c[i]-c[i-1] (mod 29) of each section, not on the runes themselves.**

## 1. Decrypt, then index of coincidence (any language)

Window: first 600 runes. Families: 8 sequences x 28 scales x 3000 offsets x 3 F treatments; plus every packet candidate that can be evaluated. Flag: IC x 29 >= 1.25 and above the shuffled-ciphertext maximum (2 replicates). Natural language gives about 1.6-2.0. 

| section | best IC | z vs bulk | shuffled max | best candidate | longest F-free stretch: IC (null max, floor) | flag | packets: best IC (null max) |
| ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 10 | 1.083 | 6.4 | 1.100 | e_digits x5 @1959 (F literal, key does not advance) | 248 runes: 1.195 (1.253, 1.30) | no | n/a |
| 12 | 1.100 | 7.7 | 1.117 | pi_digits x26 @2768 (F literal, key advances) | 410 runes: 1.122 (1.151, 1.17) | no | n/a |
| 13 | 1.150 | 6.8 | 1.178 | e_digits x1 @782 (F untouched) | 282 runes: 1.170 (1.210, 1.23) | no | n/a |
| 14 | 1.113 | 8.2 | 1.099 | e_digits x15 @1390 (F literal, key advances) | 165 runes: 1.325 (1.376, 1.44) | no | n/a |
| 16 | 1.082 | 6.1 | 1.088 | triangular x2 @18 (F untouched) | 360 runes: 1.150 (1.155, 1.17) | no | n/a |
| 17 | 1.095 | 6.9 | 1.105 | primes x7 @1929 (F literal, key advances) | 136 runes: 1.409 (1.441, 1.51) | no | n/a |
| 18 | 1.093 | 6.8 | 1.106 | e_digits x3 @1697 (F literal, key does not advance) | 361 runes: 1.135 (1.178, 1.20) | no | n/a |
| 20 | 1.092 | 6.8 | 1.094 | primes x28 @2715 (F literal, key does not advance) | 245 runes: 1.230 (1.261, 1.29) | no | n/a |
| 22 | 1.092 | 7.5 | 1.091 | prime_totients x12 @2109 (F literal, key does not advance) | 276 runes: 1.223 (1.219, 1.24) | no | n/a |
| 24 | 1.108 | 7.6 | 1.097 | prime_totients x12 @843 (F literal, key does not advance) | 273 runes: 1.174 (1.208, 1.23) | no | n/a |
| 25 | 1.196 | 7.4 | 1.176 | e_digits x6 @648 (F literal, key advances) | 135 runes: 1.449 (1.549, 1.61) | no | n/a |

Synthetic controls (their answers are known):

| case | best IC | shuffled max | flag | best candidate |
| --- | ---: | ---: | --- | --- |
| English through a totient stream, offset 777 | 1.773 | 1.173 | **FLAG** | primes x1 @777 (F untouched) |
| English through a Fibonacci stream with the F-skip (F literal iff plaintext F; ambiguous as on the real pages) | 1.215 | 1.265 | no | pi_digits x3 @1524 (F literal, key advances) |
| non-English letters (iid, skewed) through a prime stream | 3.358 | 1.170 | **FLAG** | primes x2 @345 (F literal, key advances) |
| iid uniform noise (no cipher) | 1.156 | 1.146 | no | primes x8 @1155 (F literal, key advances) |

Limits: the three F treatments assume each F is literal for every F or for none; the documented F-skip pages need each F resolved separately, so those are only reachable through the longest F-free stretch, and a stretch of 60-120 runes searched over about 700,000 candidates reaches an IC from noise alone that language also reaches (see the null mean and maximum): the check is blind there. A stream that falls out of step partway (a skip at one index) is in the same position.


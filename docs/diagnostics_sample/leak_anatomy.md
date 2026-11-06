# Leak anatomy: where the adjacent equal runes sit

**EXPLORATORY: tests fixed in advance, but the 86 doubles are one sample; a p-value here is not confirmation.**

86 doubles in 12955 adjacent pairs (12956 runes); null: the same number of doubles at positions drawn uniformly from the valid pairs (2000 replicates, seed 20261106). A family p is the maximum standardised statistic against the same null. Rule fixed in advance: any family p < 0.01 = structured leak; none below 0.05 = looks like random thinning.

**Verdict: looks like random thinning.** Smallest family p 0.115 (Bonferroni over 5 families 0.577).

| family | statistics | family p | largest z |
| --- | ---: | ---: | ---: |
| layout | 9 | 0.456 | 1.50 |
| phase | 597 | 0.371 | 3.91 |
| spacing | 4 | 0.115 | 2.22 |
| context | 5 | 0.763 | 0.62 |
| alphabet | 3 | 0.593 | 0.23 |

## layout

| statistic | observed | null mean | z | p (single) |
| --- | ---: | ---: | ---: | ---: |
| position in line (tenths) | 15.41 | 8.97 | +1.50 | 0.080 |
| position in word, from the start | 5.90 | 5.00 | +0.28 | 0.315 |
| involves a drop cap | 0.17 | 1.07 | -0.27 | 1.000 |
| line of the page (first / last / other) | 1.06 | 1.91 | -0.44 | 0.586 |
| colour (both red / not) | 0.08 | 1.04 | -0.54 | 1.000 |
| gap after the first rune (none / word dot / colon) | 0.76 | 1.99 | -0.55 | 0.779 |
| pair kind (within line / over a line end / over a page end) | 0.41 | 1.93 | -0.62 | 1.000 |
| word length | 2.39 | 5.93 | -1.05 | 0.887 |
| position in word, from the end | 1.62 | 4.90 | -1.07 | 0.905 |

## phase

Best modulus for each index (the maximum over m = 2..200 sets the family p):

| statistic | observed | null mean | z | p (single) |
| --- | ---: | ---: | ---: | ---: |
| per page index, m = 30 | 58.24 | 28.69 | +3.91 | 0.002 |
| global index, m = 43 | 71.95 | 41.52 | +3.42 | 0.002 |
| per section index, m = 149 | 198.84 | 147.21 | +3.09 | 0.003 |

## spacing

| statistic | observed | null mean | z | p (single) |
| --- | ---: | ---: | ---: | ---: |
| minimum gap | 6.00 | 2.31 | +2.22 | 0.114 |
| maximum gap | 712.00 | 742.48 | -0.18 | 1.000 |
| dispersion of gaps (sd / mean) | 0.94 | 0.98 | -0.31 | 0.806 |
| pairs of doubles closer than 20 | 6.00 | 10.03 | -1.47 | 0.183 |

## context

| statistic | observed | null mean | z | p (single) |
| --- | ---: | ---: | ---: | ---: |
| rune after the pair | 32.51 | 27.85 | +0.62 | 0.239 |
| step after the pair | 28.90 | 27.89 | +0.14 | 0.418 |
| step before the pair | 27.64 | 27.76 | -0.02 | 0.477 |
| the repeated rune | 26.61 | 27.59 | -0.13 | 0.518 |
| rune before the pair | 23.91 | 27.94 | -0.55 | 0.694 |

## alphabet

| statistic | observed | null mean | z | p (single) |
| --- | ---: | ---: | ---: | ---: |
| rune index lower / upper half | 1.22 | 0.93 | +0.23 | 0.271 |
| rune index odd / even | 0.07 | 1.04 | -0.65 | 0.817 |
| vowel / consonant | 0.00 | 0.99 | -0.71 | 1.000 |

## What this analysis could have seen

40 simulations with 86 doubles each. Under a random placement a family should reach p < 0.05 about 5% of the time: layout 5%, phase 0%, spacing 8%, context 8%, alphabet 10%.

Planted structures, share of simulations with the matching family p < 0.01:

| planted structure | family | detected |
| --- | --- | ---: |
| phase (20% of doubles on one residue mod 17) | phase | 32% |
| gap (half the doubles across a word dot) | layout | 92% |
| clusters (half the doubles within 30 of ten centres) | spacing | 98% |
| context (80% after a small step) | context | 100% |
| alphabet (80% on vowel runes) | alphabet | 100% |

pair kind (within line / over a line end / over a page end): doubles [82, 4, 0] against expected [82.06, 3.58, 0.36].

gap after the first rune (none / word dot / colon): doubles [61, 20, 1] against expected [64.24, 16.93, 0.82].

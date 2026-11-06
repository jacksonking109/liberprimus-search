# Per-rune, per-unit and per-lag breakdown of the repeat shortage

**EXPLORATORY: units chosen after inspecting the data; a p-value here is not confirmation.** Image and text are the same pages, so they are a consistency check, not two independent samples. Expected counts are exact under a permutation of each unit's known runes among its known positions.

## image, pages 17-72

86 doubles in 12842 pairs (0.67%) over 56 units. Expected under the shuffle: 437 (ratio 0.20); with the simpler frequency-squared expectation 490 (ratio 0.18).

**Uniform across runes?** chi-square 26.3 on 28 df, Monte Carlo p = 0.562 (null 95% point 41.3). **Uniform across units?** chi-square 58.3 on 54 df, p = 0.309.

Power at 86 doubles (share of simulations with p < 0.05): five most frequent runes never double 0.83; only the five most frequent runes double 1.00; one mid-frequency rune at 4x 0.61.

Per rune: `p deficit` is against the shuffle (is this rune short of chance?); `resid` and `Holm p` compare the rune with the pooled rate (is this rune different from the others?).

| rune | doubles | expected | ratio | p deficit | resid vs pooled | Holm p vs pooled |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OE | 4 | 18.5 | 0.22 | <0.001 | +0.2 | 1.000 |
| A | 1 | 17.4 | 0.06 | <0.001 | -1.3 | 1.000 |
| IO | 2 | 16.4 | 0.12 | <0.001 | -0.7 | 1.000 |
| I | 2 | 16.4 | 0.12 | <0.001 | -0.7 | 1.000 |
| X | 6 | 16.2 | 0.37 | 0.005 | +1.6 | 1.000 |
| O | 4 | 16.0 | 0.25 | <0.001 | +0.5 | 1.000 |
| F | 4 | 15.9 | 0.25 | <0.001 | +0.5 | 1.000 |
| L | 3 | 15.9 | 0.19 | <0.001 | -0.1 | 1.000 |
| TH | 4 | 15.9 | 0.25 | <0.001 | +0.5 | 1.000 |
| EA | 3 | 15.9 | 0.19 | <0.001 | -0.1 | 1.000 |
| J | 4 | 15.4 | 0.26 | <0.001 | +0.6 | 1.000 |
| U | 2 | 15.3 | 0.13 | <0.001 | -0.6 | 1.000 |
| N | 4 | 15.3 | 0.26 | <0.001 | +0.6 | 1.000 |
| Y | 2 | 15.2 | 0.13 | 0.001 | -0.6 | 1.000 |
| C | 1 | 15.2 | 0.07 | <0.001 | -1.1 | 1.000 |
| AE | 7 | 15.1 | 0.46 | 0.011 | +2.3 | 1.000 |
| D | 2 | 15.0 | 0.13 | <0.001 | -0.5 | 1.000 |
| NG | 2 | 14.9 | 0.13 | <0.001 | -0.5 | 1.000 |
| P | 1 | 14.7 | 0.07 | <0.001 | -1.1 | 1.000 |
| B | 0 | 14.6 | 0.00 | <0.001 | -1.7 | 1.000 |
| G | 5 | 14.4 | 0.35 | 0.004 | +1.3 | 1.000 |
| E | 4 | 14.4 | 0.28 | 0.001 | +0.7 | 1.000 |
| T | 2 | 14.2 | 0.14 | <0.001 | -0.5 | 1.000 |
| M | 2 | 14.1 | 0.14 | <0.001 | -0.5 | 1.000 |
| S | 3 | 14.0 | 0.21 | <0.001 | +0.1 | 1.000 |
| R | 2 | 13.3 | 0.15 | <0.001 | -0.4 | 1.000 |
| W | 6 | 13.0 | 0.46 | 0.024 | +2.2 | 1.000 |
| H | 2 | 12.8 | 0.16 | <0.001 | -0.3 | 1.000 |
| EO | 2 | 11.9 | 0.17 | <0.001 | -0.2 | 1.000 |

Equal runes at distance k (pairs with both runes known; shuffle null):

| lag | pairs | equal | rate | expected | ratio | z | p deficit |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 12842 | 86 | 0.67% | 437 | 0.20 | -16.8 | <0.001 |
| 2 | 12782 | 428 | 3.35% | 435 | 0.98 | -0.3 | 0.395 |
| 3 | 12724 | 437 | 3.43% | 433 | 1.01 | 0.2 | 0.604 |
| 4 | 12669 | 445 | 3.51% | 431 | 1.03 | 0.7 | 0.753 |
| 5 | 12614 | 456 | 3.62% | 429 | 1.06 | 1.3 | 0.907 |
| 6 | 12559 | 444 | 3.54% | 428 | 1.04 | 0.8 | 0.801 |
| 7 | 12504 | 434 | 3.47% | 426 | 1.02 | 0.4 | 0.677 |
| 8 | 12449 | 427 | 3.43% | 424 | 1.01 | 0.2 | 0.576 |

Units furthest from uniform (standardised residual): 44 (5 vs 1.6, z +2.8), 41 (5 vs 1.8, z +2.4), 36 (5 vs 1.8, z +2.3), 61 (4 vs 1.8, z +1.6), 46 (4 vs 1.8, z +1.6), 22 (0 vs 1.8, z -1.4)

## text, sections 10-25

86 doubles in 12941 pairs (0.66%) over 16 units. Expected under the shuffle: 444 (ratio 0.19); with the simpler frequency-squared expectation 459 (ratio 0.19).

**Uniform across runes?** chi-square 27.2 on 28 df, Monte Carlo p = 0.509 (null 95% point 41.5). **Uniform across units?** chi-square 7.9 on 14 df, p = 0.854.

Power at 86 doubles (share of simulations with p < 0.05): five most frequent runes never double 0.83; only the five most frequent runes double 1.00; one mid-frequency rune at 4x 0.60.

Per rune: `p deficit` is against the shuffle (is this rune short of chance?); `resid` and `Holm p` compare the rune with the pooled rate (is this rune different from the others?).

| rune | doubles | expected | ratio | p deficit | resid vs pooled | Holm p vs pooled |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OE | 4 | 18.2 | 0.22 | <0.001 | +0.3 | 1.000 |
| A | 1 | 17.9 | 0.06 | <0.001 | -1.3 | 1.000 |
| I | 2 | 17.0 | 0.12 | <0.001 | -0.7 | 1.000 |
| IO | 2 | 16.9 | 0.12 | <0.001 | -0.7 | 1.000 |
| F | 4 | 16.5 | 0.24 | <0.001 | +0.4 | 1.000 |
| X | 6 | 16.3 | 0.37 | 0.003 | +1.6 | 1.000 |
| O | 4 | 16.2 | 0.25 | <0.001 | +0.5 | 1.000 |
| L | 3 | 16.0 | 0.19 | <0.001 | -0.1 | 1.000 |
| EA | 3 | 16.0 | 0.19 | <0.001 | -0.1 | 1.000 |
| TH | 4 | 15.8 | 0.25 | <0.001 | +0.5 | 1.000 |
| J | 4 | 15.6 | 0.26 | <0.001 | +0.6 | 1.000 |
| NG | 2 | 15.5 | 0.13 | <0.001 | -0.6 | 1.000 |
| N | 4 | 15.5 | 0.26 | <0.001 | +0.6 | 1.000 |
| U | 2 | 15.5 | 0.13 | <0.001 | -0.6 | 1.000 |
| Y | 2 | 15.3 | 0.13 | <0.001 | -0.6 | 1.000 |
| C | 1 | 15.2 | 0.07 | <0.001 | -1.1 | 1.000 |
| B | 0 | 15.2 | 0.00 | <0.001 | -1.7 | 1.000 |
| AE | 7 | 15.2 | 0.46 | 0.015 | +2.4 | 1.000 |
| P | 1 | 15.0 | 0.07 | <0.001 | -1.1 | 1.000 |
| G | 5 | 14.8 | 0.34 | 0.004 | +1.3 | 1.000 |
| T | 2 | 14.8 | 0.14 | <0.001 | -0.5 | 1.000 |
| E | 4 | 14.8 | 0.27 | 0.002 | +0.7 | 1.000 |
| D | 2 | 14.7 | 0.14 | 0.001 | -0.5 | 1.000 |
| M | 2 | 14.6 | 0.14 | 0.001 | -0.5 | 1.000 |
| S | 3 | 14.3 | 0.21 | 0.001 | +0.1 | 1.000 |
| R | 2 | 13.8 | 0.15 | <0.001 | -0.4 | 1.000 |
| H | 2 | 13.0 | 0.15 | 0.001 | -0.3 | 1.000 |
| W | 6 | 12.6 | 0.48 | 0.033 | +2.3 | 1.000 |
| EO | 2 | 12.3 | 0.16 | <0.001 | -0.2 | 1.000 |

Equal runes at distance k (pairs with both runes known; shuffle null):

| lag | pairs | equal | rate | expected | ratio | z | p deficit |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 12941 | 86 | 0.66% | 444 | 0.19 | -16.9 | <0.001 |
| 2 | 12926 | 440 | 3.40% | 444 | 0.99 | -0.2 | 0.434 |
| 3 | 12911 | 440 | 3.41% | 443 | 0.99 | -0.2 | 0.456 |
| 4 | 12896 | 457 | 3.54% | 443 | 1.03 | 0.7 | 0.765 |
| 5 | 12881 | 476 | 3.70% | 442 | 1.08 | 1.6 | 0.949 |
| 6 | 12866 | 453 | 3.52% | 442 | 1.03 | 0.5 | 0.703 |
| 7 | 12851 | 444 | 3.45% | 441 | 1.01 | 0.1 | 0.548 |
| 8 | 12836 | 434 | 3.38% | 441 | 0.98 | -0.4 | 0.371 |

Units furthest from uniform (standardised residual): 17 (11 vs 6.8, z +1.6), 18 (13 vs 9.5, z +1.1), 13 (1 vs 2.2, z -0.8), 24 (2 vs 3.5, z -0.8), 19 (0 vs 0.6, z -0.7), 14 (9 vs 11.5, z -0.7)

## text, the 300+ rune sections (the 84-double count)

84 doubles in 12605 pairs (0.67%) over 11 units. Expected under the shuffle: 433 (ratio 0.19); with the simpler frequency-squared expectation 444 (ratio 0.19).

**Uniform across runes?** chi-square 25.8 on 28 df, Monte Carlo p = 0.587 (null 95% point 41.5). **Uniform across units?** chi-square 7.2 on 10 df, p = 0.710.

Power at 84 doubles (share of simulations with p < 0.05): five most frequent runes never double 0.81; only the five most frequent runes double 1.00; one mid-frequency rune at 4x 0.59.

Per rune: `p deficit` is against the shuffle (is this rune short of chance?); `resid` and `Holm p` compare the rune with the pooled rate (is this rune different from the others?).

| rune | doubles | expected | ratio | p deficit | resid vs pooled | Holm p vs pooled |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OE | 4 | 17.9 | 0.22 | <0.001 | +0.3 | 1.000 |
| A | 1 | 17.3 | 0.06 | <0.001 | -1.3 | 1.000 |
| I | 2 | 16.5 | 0.12 | <0.001 | -0.7 | 1.000 |
| F | 4 | 16.4 | 0.24 | <0.001 | +0.5 | 1.000 |
| X | 6 | 16.2 | 0.37 | 0.001 | +1.6 | 1.000 |
| O | 4 | 16.2 | 0.25 | 0.002 | +0.5 | 1.000 |
| IO | 2 | 16.1 | 0.12 | <0.001 | -0.6 | 1.000 |
| EA | 3 | 15.6 | 0.19 | 0.002 | -0.0 | 1.000 |
| NG | 2 | 15.4 | 0.13 | <0.001 | -0.6 | 1.000 |
| L | 2 | 15.4 | 0.13 | <0.001 | -0.6 | 1.000 |
| TH | 4 | 15.3 | 0.26 | <0.001 | +0.6 | 1.000 |
| U | 2 | 15.2 | 0.13 | <0.001 | -0.6 | 1.000 |
| J | 4 | 15.1 | 0.26 | 0.001 | +0.6 | 1.000 |
| Y | 2 | 15.0 | 0.13 | <0.001 | -0.5 | 1.000 |
| AE | 7 | 15.0 | 0.47 | 0.015 | +2.4 | 1.000 |
| B | 0 | 14.7 | 0.00 | <0.001 | -1.7 | 1.000 |
| C | 1 | 14.7 | 0.07 | <0.001 | -1.1 | 1.000 |
| P | 1 | 14.7 | 0.07 | <0.001 | -1.1 | 1.000 |
| N | 4 | 14.7 | 0.27 | <0.001 | +0.7 | 1.000 |
| E | 4 | 14.6 | 0.27 | 0.001 | +0.7 | 1.000 |
| G | 5 | 14.6 | 0.34 | 0.005 | +1.3 | 1.000 |
| D | 2 | 14.5 | 0.14 | <0.001 | -0.5 | 1.000 |
| M | 2 | 14.2 | 0.14 | <0.001 | -0.5 | 1.000 |
| T | 2 | 14.1 | 0.14 | <0.001 | -0.4 | 1.000 |
| S | 3 | 13.7 | 0.22 | 0.002 | +0.2 | 1.000 |
| R | 2 | 13.6 | 0.15 | <0.001 | -0.4 | 1.000 |
| H | 2 | 12.8 | 0.16 | <0.001 | -0.3 | 1.000 |
| EO | 2 | 12.1 | 0.16 | <0.001 | -0.2 | 1.000 |
| W | 5 | 11.3 | 0.44 | 0.034 | +1.9 | 1.000 |

Equal runes at distance k (pairs with both runes known; shuffle null):

| lag | pairs | equal | rate | expected | ratio | z | p deficit |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 12605 | 84 | 0.67% | 433 | 0.19 | -17.4 | <0.001 |
| 2 | 12594 | 436 | 3.46% | 433 | 1.01 | 0.1 | 0.578 |
| 3 | 12583 | 429 | 3.41% | 432 | 0.99 | -0.2 | 0.463 |
| 4 | 12572 | 441 | 3.51% | 432 | 1.02 | 0.4 | 0.676 |
| 5 | 12561 | 468 | 3.73% | 432 | 1.08 | 1.8 | 0.965 |
| 6 | 12550 | 438 | 3.49% | 431 | 1.02 | 0.3 | 0.628 |
| 7 | 12539 | 437 | 3.49% | 431 | 1.01 | 0.3 | 0.628 |
| 8 | 12528 | 422 | 3.37% | 430 | 0.98 | -0.4 | 0.334 |

Units furthest from uniform (standardised residual): 17 (11 vs 6.8, z +1.6), 18 (13 vs 9.5, z +1.1), 13 (1 vs 2.2, z -0.8), 24 (2 vs 3.5, z -0.8), 14 (9 vs 11.6, z -0.8), 16 (10 vs 12.7, z -0.7)


# Phase 2 generators: three stateful families against the repeat signature

**SYNTHETIC: English plaintext (training split), 6 windows of 5,000 runes; no oracle, no model, no added leak.** Real text: lag 1 0.19 (95% interval 0.15-0.24), lags 2-8 at chance, unigram IC 1.00, first-difference IC 1.03, step-stream IC x 28 1.001. `invertible` = share of reachable states where all plaintext symbols give different outputs (a machine below 1.00 cannot carry every message). `word-position p` = do the plaintext word positions of the machine's zero steps look like the real doubles' (21 / 47 / 18 initial / internal / final)?

| family | variant | invertible | lag 1 | lags 2-8 | unigram IC | diff IC | step IC x 28 | zeros | verdict | source of zeros | word-position p |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | --- | ---: |
| 1 table walk | cyclic Latin, row (0,j), wrap | 1.00 | 0.69 | 0.67-1.11 | 1.00 | 1.76 | 1.761 | 717 | **no** | plaintext rune 0 (100% of zeros) | 0.0002 |
| 1 table walk | cyclic Latin, row (0,j), reflect | 0.07 | 1.09 | 0.94-1.04 | 1.44 | 1.20 | 1.205 | 1622 | **no** | state / key dependent (no single plaintext rune) | 0.0614 |
| 1 table walk | cyclic Latin, rook, wrap | 0.00 | 0.00 | 0.01-1.35 | 1.00 | 2.53 | 2.440 | 0 | **no** | none (no zero steps) |  |
| 1 table walk | cyclic Latin, rook, reflect | 0.00 | 0.91 | 0.99-1.17 | 1.73 | 1.73 | 1.776 | 1622 | **no** | state / key dependent (no single plaintext rune) | 0.7425 |
| 1 table walk | cyclic Latin, diagonal (j,j), wrap | 1.00 | 0.69 | 0.67-1.11 | 1.00 | 1.76 | 1.761 | 717 | **no** | plaintext rune 0 (100% of zeros) | 0.0002 |
| 1 table walk | cyclic Latin, diagonal (j,j), reflect | 0.00 | 1.01 | 0.96-1.05 | 1.47 | 1.20 | 1.191 | 1531 | **no** | state / key dependent (no single plaintext rune) | 0.0876 |
| 1 table walk | cyclic Latin, near list, wrap | 0.00 | 1.68 | 2.22-4.74 | 1.01 | 4.76 | 5.080 | 1763 | **no** | plaintext rune 5 (63% of zeros) | 0.7059 |
| 1 table walk | cyclic Latin, near list, reflect | 0.00 | 1.87 | 2.34-4.66 | 1.04 | 4.79 | 5.167 | 2020 | **no** | state / key dependent (no single plaintext rune) | 0.5657 |
| 1 table walk | keyed Latin, row (0,j), wrap | 1.00 | 0.69 | 0.67-1.11 | 1.00 | 1.03 | 1.003 | 717 | **no** | plaintext rune 0 (100% of zeros) | 0.0002 |
| 1 table walk | keyed Latin, row (0,j), reflect | 0.07 | 1.09 | 0.94-1.04 | 1.44 | 1.06 | 1.015 | 1622 | **no** | state / key dependent (no single plaintext rune) | 0.0614 |
| 1 table walk | keyed Latin, rook, wrap | 0.00 | 0.00 | 0.50-1.07 | 1.00 | 1.04 | 1.003 | 0 | **no** | none (no zero steps) |  |
| 1 table walk | keyed Latin, rook, reflect | 0.00 | 1.44 | 0.98-1.67 | 1.09 | 1.02 | 1.009 | 1622 | **no** | state / key dependent (no single plaintext rune) | 0.7425 |
| 1 table walk | keyed Latin, diagonal (j,j), wrap | 0.00 | 0.84 | 0.86-1.06 | 1.99 | 1.08 | 1.011 | 1741 | **no** | state / key dependent (no single plaintext rune) | 0.0560 |
| 1 table walk | keyed Latin, diagonal (j,j), reflect | 0.00 | 0.93 | 0.95-1.05 | 1.69 | 1.11 | 1.029 | 1626 | **no** | state / key dependent (no single plaintext rune) | 0.1992 |
| 1 table walk | keyed Latin, near list, wrap | 0.00 | 0.65 | 1.12-2.24 | 1.00 | 1.01 | 1.001 | 674 | **no** | state / key dependent (no single plaintext rune) | 0.2745 |
| 1 table walk | keyed Latin, near list, reflect | 0.00 | 0.77 | 1.23-2.29 | 1.00 | 1.00 | 1.002 | 799 | **no** | state / key dependent (no single plaintext rune) | 0.6357 |
| 1 table walk | random 29x29, row (0,j), wrap | 0.00 | 0.88 | 0.82-1.04 | 1.91 | 1.07 | 1.010 | 1738 | **no** | state / key dependent (no single plaintext rune) | 0.0576 |
| 1 table walk | random 29x29, row (0,j), reflect | 0.00 | 1.08 | 0.96-1.02 | 2.36 | 1.19 | 1.022 | 2643 | **no** | state / key dependent (no single plaintext rune) | 0.3407 |
| 1 table walk | random 29x29, rook, wrap | 0.00 | 0.98 | 0.97-1.16 | 1.01 | 1.00 | 1.001 | 1029 | **no** | state / key dependent (no single plaintext rune) | 0.7319 |
| 1 table walk | random 29x29, rook, reflect | 0.00 | 2.18 | 1.02-1.99 | 1.26 | 1.11 | 1.006 | 2829 | **no** | state / key dependent (no single plaintext rune) | 0.7690 |
| 1 table walk | random 29x29, diagonal (j,j), wrap | 0.00 | 0.80 | 0.85-1.05 | 1.83 | 1.06 | 1.008 | 1524 | **no** | state / key dependent (no single plaintext rune) | 0.0390 |
| 1 table walk | random 29x29, diagonal (j,j), reflect | 0.00 | 0.96 | 0.95-1.04 | 1.80 | 1.08 | 1.017 | 1781 | **no** | state / key dependent (no single plaintext rune) | 0.0552 |
| 1 table walk | random 29x29, near list, wrap | 0.00 | 0.93 | 1.23-2.41 | 1.02 | 1.00 | 1.000 | 981 | **no** | state / key dependent (no single plaintext rune) | 0.6563 |
| 1 table walk | random 29x29, near list, reflect | 0.00 | 1.13 | 1.30-2.37 | 1.02 | 1.00 | 1.002 | 1195 | **no** | state / key dependent (no single plaintext rune) | 0.4045 |
| 1 table walk | page-05 grid 5x5, row (0,j), wrap | 0.00 | 1.11 | 0.97-1.03 | 8.91 | 5.48 | 2.047 | 10188 | **no** | state / key dependent (no single plaintext rune) | 0.7135 |
| 1 table walk | page-05 grid 5x5, row (0,j), reflect | 0.00 | 1.19 | 0.99-1.01 | 9.81 | 6.35 | 2.079 | 12065 | **no** | state / key dependent (no single plaintext rune) | 0.6179 |
| 1 table walk | page-05 grid 5x5, rook, wrap | 0.00 | 3.31 | 1.02-1.93 | 3.03 | 4.17 | 1.567 | 10384 | **no** | state / key dependent (no single plaintext rune) | 0.1938 |
| 1 table walk | page-05 grid 5x5, rook, reflect | 0.00 | 2.44 | 1.05-1.76 | 3.11 | 2.85 | 1.537 | 7852 | **no** | state / key dependent (no single plaintext rune) | 0.2472 |
| 1 table walk | page-05 grid 5x5, diagonal (j,j), wrap | 0.00 | 1.15 | 0.99-1.04 | 7.35 | 4.19 | 2.031 | 8730 | **no** | state / key dependent (no single plaintext rune) | 0.7209 |
| 1 table walk | page-05 grid 5x5, diagonal (j,j), reflect | 0.00 | 1.22 | 0.98-1.02 | 8.95 | 5.79 | 2.383 | 11292 | **no** | state / key dependent (no single plaintext rune) | 0.5921 |
| 1 table walk | page-05 grid 5x5, near list, wrap | 0.00 | 0.61 | 0.96-1.22 | 3.00 | 1.26 | 1.262 | 1903 | **no** | state / key dependent (no single plaintext rune) | 0.4887 |
| 1 table walk | page-05 grid 5x5, near list, reflect | 0.00 | 0.65 | 0.96-1.24 | 3.11 | 1.23 | 1.218 | 2079 | **no** | state / key dependent (no single plaintext rune) | 0.4165 |
| 1 table walk | page-05 grid tiled, row (0,j), wrap | 0.00 | 1.20 | 0.96-1.01 | 8.45 | 5.05 | 1.874 | 10452 | **no** | state / key dependent (no single plaintext rune) | 0.4491 |
| 1 table walk | page-05 grid tiled, row (0,j), reflect | 0.00 | 0.91 | 0.98-1.03 | 8.41 | 4.11 | 1.983 | 7875 | **no** | state / key dependent (no single plaintext rune) | 0.6123 |
| 1 table walk | page-05 grid tiled, rook, wrap | 0.00 | 3.13 | 1.01-1.91 | 2.99 | 3.76 | 1.567 | 9664 | **no** | state / key dependent (no single plaintext rune) | 0.3077 |
| 1 table walk | page-05 grid tiled, rook, reflect | 0.00 | 2.55 | 1.01-1.88 | 2.97 | 2.85 | 1.566 | 7813 | **no** | state / key dependent (no single plaintext rune) | 0.6453 |
| 1 table walk | page-05 grid tiled, diagonal (j,j), wrap | 0.00 | 1.24 | 0.91-1.02 | 5.09 | 2.50 | 1.533 | 6541 | **no** | state / key dependent (no single plaintext rune) | 0.1400 |
| 1 table walk | page-05 grid tiled, diagonal (j,j), reflect | 0.00 | 0.71 | 0.99-1.04 | 7.27 | 3.02 | 1.903 | 5336 | **no** | state / key dependent (no single plaintext rune) | 0.2054 |
| 1 table walk | page-05 grid tiled, near list, wrap | 0.00 | 0.63 | 0.98-1.23 | 2.98 | 1.24 | 1.239 | 1935 | **no** | state / key dependent (no single plaintext rune) | 0.5923 |
| 1 table walk | page-05 grid tiled, near list, reflect | 0.00 | 0.66 | 0.99-1.21 | 3.00 | 1.27 | 1.259 | 2050 | **no** | state / key dependent (no single plaintext rune) | 0.6229 |
| 2 permuting alphabet | emitted rune moves to slot 0 | 1.00 | 0.69 | 0.86-2.01 | 1.01 | 1.00 | 1.000 | 717 | **no** | plaintext rune 0 (100% of zeros) | 0.0002 |
| 2 permuting alphabet | both alphabets, used rune moves to slot 0 | 1.00 | 0.59 | 0.70-1.02 | 1.76 | 1.09 | 1.014 | 1081 | **no** | state / key dependent (no single plaintext rune) | 0.6747 |
| 2 permuting alphabet | emitted rune moves to slot 7 | 1.00 | 0.76 | 0.70-1.58 | 1.01 | 1.00 | 1.000 | 794 | **no** | plaintext rune 7 (100% of zeros) | 0.0002 |
| 2 permuting alphabet | both alphabets, used rune moves to slot 7 | 1.00 | 0.59 | 0.70-1.02 | 1.76 | 1.09 | 1.014 | 1081 | **no** | state / key dependent (no single plaintext rune) | 0.6747 |
| 2 permuting alphabet | emitted rune moves to slot 14 | 1.00 | 0.04 | 0.88-1.37 | 1.01 | 1.03 | 1.000 | 44 | **no** | plaintext rune 14 (100% of zeros) | 0.0002 |
| 2 permuting alphabet | both alphabets, used rune moves to slot 14 | 1.00 | 0.59 | 0.70-1.02 | 1.76 | 1.09 | 1.014 | 1081 | **no** | state / key dependent (no single plaintext rune) | 0.6747 |
| 2 permuting alphabet | emitted rune moves to slot 21 | 1.00 | 0.29 | 0.82-2.27 | 1.01 | 1.02 | 1.000 | 303 | **no** | plaintext rune 21 (100% of zeros) | 0.0002 |
| 2 permuting alphabet | both alphabets, used rune moves to slot 21 | 1.00 | 0.59 | 0.70-1.02 | 1.76 | 1.09 | 1.014 | 1081 | **no** | state / key dependent (no single plaintext rune) | 0.6747 |
| 2 permuting alphabet | emitted rune moves to slot 28 | 1.00 | 0.20 | 0.03-2.08 | 1.00 | 1.02 | 1.000 | 205 | **no** | plaintext rune 28 (100% of zeros) | 0.0002 |
| 2 permuting alphabet | both alphabets, used rune moves to slot 28 | 1.00 | 0.59 | 0.70-1.02 | 1.76 | 1.09 | 1.014 | 1081 | **no** | state / key dependent (no single plaintext rune) | 0.6747 |
| 2 permuting alphabet | emitted rune swaps with the one 1 places on | 1.00 | 1.25 | 0.91-1.10 | 1.06 | 1.00 | 1.001 | 1376 | **no** | state / key dependent (no single plaintext rune) | 0.3951 |
| 2 permuting alphabet | emitted rune swaps with the one 7 places on | 1.00 | 0.45 | 0.74-0.92 | 1.19 | 1.01 | 1.000 | 552 | **no** | state / key dependent (no single plaintext rune) | 0.6505 |
| 2 permuting alphabet | emitted rune swaps with the one 14 places on | 1.00 | 1.45 | 1.08-1.48 | 1.18 | 1.02 | 1.000 | 1764 | **no** | state / key dependent (no single plaintext rune) | 0.0272 |
| 2 permuting alphabet | Chaocipher (both alphabets) | 1.00 | 1.03 | 0.90-1.00 | 1.00 | 1.00 | 1.000 | 1068 | **no** | state / key dependent (no single plaintext rune) | 0.7469 |
| 3 non-zero step | x = 2x mod 29 (primitive root, 1..28); rune 28 skip | 1.00 | 0.00 | 0.95-1.04 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | x = 2x mod 29 (primitive root, 1..28); rune 28 fold | 1.00 | 0.00 | 0.96-1.08 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | x = 2x mod 29 (primitive root, 1..28); rune 0 skip | 1.00 | 0.00 | 0.97-1.05 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | x = 2x mod 29 (primitive root, 1..28); rune 0 fold | 1.00 | 0.00 | 0.96-1.02 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | x = 2x mod 29 (primitive root, 1..28); rune 14 skip | 1.00 | 0.00 | 0.93-1.06 | 1.00 | 1.03 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | x = 2x mod 29 (primitive root, 1..28); rune 14 fold | 1.00 | 0.00 | 0.97-1.07 | 1.00 | 1.03 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | lagged Fibonacci mod 28 (3, 7); rune 28 skip | 1.00 | 0.00 | 0.99-1.04 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | lagged Fibonacci mod 28 (3, 7); rune 28 fold | 1.00 | 0.00 | 0.98-1.11 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | lagged Fibonacci mod 28 (3, 7); rune 0 skip | 1.00 | 0.00 | 0.96-1.06 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | lagged Fibonacci mod 28 (3, 7); rune 0 fold | 1.00 | 0.00 | 0.94-1.03 | 1.00 | 1.03 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | lagged Fibonacci mod 28 (3, 7); rune 14 skip | 1.00 | 0.00 | 0.95-1.05 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | lagged Fibonacci mod 28 (3, 7); rune 14 fold | 1.00 | 0.00 | 0.98-1.06 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | 2x2 matrix power mod 29; rune 28 skip | 1.00 | 0.00 | 0.97-1.06 | 1.00 | 1.05 | 1.003 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | 2x2 matrix power mod 29; rune 28 fold | 1.00 | 0.00 | 0.97-1.09 | 1.00 | 1.05 | 1.004 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | 2x2 matrix power mod 29; rune 0 skip | 1.00 | 0.00 | 0.97-1.07 | 1.00 | 1.05 | 1.004 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | 2x2 matrix power mod 29; rune 0 fold | 1.00 | 0.00 | 0.98-1.07 | 1.00 | 1.05 | 1.004 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | 2x2 matrix power mod 29; rune 14 skip | 1.00 | 0.00 | 0.95-1.06 | 1.00 | 1.06 | 1.003 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | 2x2 matrix power mod 29; rune 14 fold | 1.00 | 0.00 | 0.97-1.07 | 1.00 | 1.05 | 1.003 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | x += p' + 1 (plaintext feedback); rune 28 skip | 1.00 | 0.00 | 0.95-1.16 | 1.00 | 1.04 | 1.000 | 0 | **no** | none (no zero steps) |  |
| 3 non-zero step | x += p' + 1 (plaintext feedback); rune 28 fold | 1.00 | 0.00 | 0.98-1.15 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | x += p' + 1 (plaintext feedback); rune 0 skip | 1.00 | 0.00 | 0.92-1.04 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | x += p' + 1 (plaintext feedback); rune 0 fold | 1.00 | 0.00 | 0.96-1.05 | 1.00 | 1.04 | 1.000 | 0 | **near miss: too few repeats** | none (no zero steps) |  |
| 3 non-zero step | x += p' + 1 (plaintext feedback); rune 14 skip | 1.00 | 0.00 | 0.82-1.04 | 1.00 | 1.04 | 1.000 | 0 | **no** | none (no zero steps) |  |
| 3 non-zero step | x += p' + 1 (plaintext feedback); rune 14 fold | 1.00 | 0.00 | 0.85-1.05 | 1.00 | 1.03 | 1.000 | 0 | **no** | none (no zero steps) |  |

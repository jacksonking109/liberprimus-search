# Adjacent identical glyphs counted directly from the page images

**EXPLORATORY.** A double needs two agreeing tests: the same shape, and a stroke distance of at most 8 px between the two crops. Pairs touching an unknown or unresolved box are excluded. Expected = pairs x sum of squared shape frequencies on the page; the shuffle keeps each page's shapes and positions.

Coverage on the unsolved pages: 99.42% of 13031 glyph boxes have a known shape.

| group | pages | pairs | doubles | rate | expected | ratio | shuffle z | p (deficit) | excluded | test disagreements |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| unsolved pages 17-72 | 56 | 12842 | 86 | 0.67% | 490 | 0.18 | -16.8 | 0.005 | 133 | 0 |
| solved, plain substitution (language level) | 6 | 924 | 22 | 2.38% | 63 | 0.35 | -4.9 | 0.005 | 8 | 0 |
| solved, enciphered | 10 | 1818 | 46 | 2.53% | 104 | 0.44 | -5.1 | 0.005 | 12 | 0 |

For comparison: scream314 text of the unsolved sections 84 doubles in 12,605 pairs (0.67%, ratio 0.19); uniformly random text 3.4%.

Unsolved pages by stratum (doubles / pairs):

| stratum | doubles | pairs |
| --- | ---: | ---: |
| inside a line | 82 | 12362 |
| across a line end | 4 | 480 |
| no separator | 61 | 9685 |
| word dot | 20 | 2553 |
| colon pair | 1 | 124 |
| red heading text | 1 | 197 |
| black body text | 85 | 12645 |

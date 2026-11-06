# Image reader audit

**EXPLORATORY audit; no oracle, no models.** Documented separation of the typeface: same rune <= 3 px from its shape, different runes >= 15 px apart.

## 1. Match margins (every glyph with a known shape)

| set | glyphs | d1 median / max | d2 median / min | d1 > 3 | d2 < 15 | gap (d2 - d1) < 8 | smallest gap |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| all pages | 15781 | 0 / 4 | 387 / 14 | 1 | 100 | 0 | 14 |
| unsolved pages 17-72 | 12943 | 0 / 2 | 384 / 14 | 0 | 65 | 0 | 14 |

Weakest margins (smallest gap between the given shape and the nearest other rune):

| page | line | index | read as | nearest other | d1 | d2 | gap |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| 03 | 3 | 3 | W | TH | 0 | 14 | 14 |
| 04 | 1 | 11 | W | TH | 0 | 14 | 14 |
| 04 | 3 | 9 | W | TH | 0 | 14 | 14 |
| 04 | 3 | 10 | W | TH | 0 | 14 | 14 |
| 04 | 5 | 20 | W | TH | 0 | 14 | 14 |
| 06 | 1 | 5 | W | TH | 0 | 14 | 14 |
| 06 | 6 | 8 | W | TH | 0 | 14 | 14 |
| 06 | 7 | 8 | W | TH | 0 | 14 | 14 |
| 07 | 1 | 3 | W | TH | 0 | 14 | 14 |
| 07 | 1 | 20 | W | TH | 0 | 14 | 14 |
| 07 | 2 | 19 | W | TH | 0 | 14 | 14 |
| 07 | 5 | 9 | W | TH | 0 | 14 | 14 |

## 2. Agreement with the manifest on solved pages

The shapes were labelled from pages 14-16, so those rows are circular; the others are independent.

| pages | image glyphs | text runes | matched | substituted | image only | text only | unknown glyphs | agreement (of text) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 01 | 185 | 184 | 182 | 1 | 2 | 1 | 3 | 98.91% |
| 05 | 81 | 157 | 81 | 0 | 0 | 76 | 0 | 51.59% |
| 03-04 | 489 | 515 | 485 | 0 | 4 | 30 | 4 | 94.17% |
| 06-09 | 762 | 780 | 760 | 2 | 0 | 18 | 0 | 97.44% |
| 10-13 | 754 | 629 | 624 | 1 | 129 | 4 | 4 | 99.21% |
| 73 | 85 | 82 | 81 | 1 | 3 | 0 | 0 | 98.78% |
| 74 | 95 | 94 | 93 | 1 | 1 | 0 | 0 | 98.94% |
| 14-16 (labelling pages: circular) | 408 | 408 | 408 | 0 | 0 | 0 | 0 | 100.00% |

Image glyphs the manifest text does not have (5 or more on a page): 10-13: page 13 124 image glyphs with no text.

## 3. Wrong glyph size: wrong runes, or only unknown ones?

Pages rescaled and re-read with the same shapes, against the normal reading of the same page. `wrong` = a rune read as a different rune; `unknown` = read as no known shape; `structural` = glyphs lost or added.

| page | scale | glyphs | matched | wrong | unknown | structural |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 17 | 0.8 | 0 | 0 | 0 | 0 | 262 |
| 17 | 0.85 | 0 | 0 | 0 | 0 | 262 |
| 17 | 0.9 | 260 | 4 | 0 | 256 | 2 |
| 17 | 0.95 | 262 | 224 | 0 | 38 | 0 |
| 17 | 1.05 | 262 | 211 | 0 | 51 | 0 |
| 17 | 1.1 | 262 | 22 | 0 | 240 | 0 |
| 17 | 1.15 | 177 | 1 | 0 | 176 | 85 |
| 17 | 1.2 | 0 | 0 | 0 | 0 | 262 |
| 33 | 0.8 | 0 | 0 | 0 | 0 | 267 |
| 33 | 0.85 | 0 | 0 | 0 | 0 | 267 |
| 33 | 0.9 | 265 | 1 | 0 | 264 | 2 |
| 33 | 0.95 | 266 | 229 | 0 | 37 | 1 |
| 33 | 1.05 | 266 | 201 | 0 | 65 | 1 |
| 33 | 1.1 | 265 | 30 | 0 | 235 | 2 |
| 33 | 1.15 | 145 | 0 | 0 | 145 | 122 |
| 33 | 1.2 | 0 | 0 | 0 | 0 | 267 |
| 58 | 0.8 | 0 | 0 | 0 | 0 | 277 |
| 58 | 0.85 | 0 | 0 | 0 | 0 | 277 |
| 58 | 0.9 | 270 | 7 | 0 | 263 | 7 |
| 58 | 0.95 | 274 | 238 | 0 | 36 | 3 |
| 58 | 1.05 | 274 | 217 | 0 | 57 | 3 |
| 58 | 1.1 | 274 | 34 | 0 | 239 | 5 |
| 58 | 1.15 | 184 | 4 | 0 | 180 | 93 |
| 58 | 1.2 | 0 | 0 | 0 | 0 | 277 |

Wrong runes across all rescaled reads: 0.

## 4. The short image at many scales (known answer)

| scale | pieces | unknown | wrong | exact |
| ---: | ---: | ---: | ---: | --- |
| 1.4 | 20 | 18 | 0 | no |
| 1.5 | 20 | 18 | 0 | no |
| 1.6 | 20 | 18 | 0 | no |
| 1.7 | 20 | 18 | 0 | no |
| 1.8 | 20 | 18 | 0 | no |
| 1.9 | 20 | 1 | 0 | no |
| 2.0 | 20 | 0 | 0 | yes |
| 2.1 | 20 | 4 | 0 | no |
| 2.2 | 20 | 16 | 0 | no |
| 2.3 | 20 | 18 | 0 | no |
| 2.4 | 20 | 18 | 0 | no |
| 2.5 | 20 | 18 | 0 | no |
| 2.6 | 20 | 18 | 0 | no |
| 2.7 | 20 | 18 | 0 | no |

## 5. Separators against the text's word breaks

Consecutive glyphs on one line, both aligned: 12360. Both mark a break 2675, text only 45, image only 1, neither 9639; agreement 99.63%.

## 6. Positions where the image and the text differ

| page | line | image reads | text has | distance to image reading | distance to text reading | nearest three |
| --- | ---: | --- | --- | ---: | ---: | --- |
| 41 | 8 | AE | A | 0 | 49 | AE 0, A 49, O 89 |

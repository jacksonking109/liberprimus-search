# Red headings read from the page images

**EXPLORATORY.** Red runs are headings or closing lines; the dotted red square ends a red passage (`|`). 29 shapes labelled from pages 14-16 (agreement with the manifest: 14-15 100.0%, 16 100.0%).

## Plain-substitution pages (readable as written)

- page 05: SOMEWISDOM|; CNOWTHIS|
- page 10: THELOSSOFDIUINITY|; CONSUMPTION|
- page 11: PRESERUATION|
- page 12: ADHERENCE|
- page 13: SOMEWISDOM|; NINSTRUCTION|
- page 16: ANINSTRUCTION|; CNOWTHIS|
- page 74: PARABLE|

## Red runs on the unsolved pages (ciphertext runes, as plain Gematria tokens)

| page | length | terminated | ciphertext |
| ---: | ---: | --- | --- |
| 17 | 13 | yes | SHEOGMIOFSYENGC |
| 20 | 16 | yes | LJEOHNGCTHTAEJTXHTUOE |
| 23 | 11 | yes | ATXBMGIOSBXEO |
| 24 | 14 | yes | DOOETTHAECWJXEAGEAM |
| 25 | 12 | no | XIXMUXMCTHPOB |
| 32 | 9 | yes | FULMAEAYOEA |
| 32 | 11 | yes | LUNGNCUBNTFNG |
| 40 | 16 | yes | UAWNGGXDGIBIEOTBIY |
| 44 | 19 | yes | MPYLSOAAEHLEEOIMLLSCP |
| 50 | 10 | yes | DEOXCFIAWHG |
| 50 | 8 | yes | NGTHEOIFCOEEO |
| 57 | 8 | no | FNMYGDAEH |
| 71 | 9 | yes | AMNGDIOTHXIM |

## Crib test

Each heading is tried against every title of the same length (AN INSTRUCTION, SOME WISDOM, KNOW THIS, A WARNING, AN END, A KOAN, PARABLE, THE LOSS OF DIVINITY, CONSUMPTION, PRESERVATION, ADHERENCE, WELCOME). The implied key must be a window of a sequence (7 families x 28 scales x offsets 0..20000) or a short repeating key.

Unsolved headings: 36 combinations tested, 0 hits. Random-plaintext baseline: 0 of 108 false matches.


Known-page controls (pages 73 and 74): 10 hits in 20 combinations:

- page 73 as 'AN END' [c-p]: [('primes', 1, 0)] []
- page 73 as 'AN END' [p-c]: [('primes', 28, 0)] []
- page 73 as 'AN END' [(28-c)-p]: [('pi_digits', 13, 8002), ('pi_digits', 16, 3481), ('e_digits', 16, 19208)] []
- page 73 as 'AN END' [p-(28-c)]: [('pi_digits', 13, 3481), ('pi_digits', 16, 8002), ('e_digits', 13, 19208)] []
- page 73 as 'A KOAN' [c-p]: [('primes', 5, 3750)] []
- page 73 as 'A KOAN' [p-c]: [('primes', 24, 3750)] []
- page 73 as 'A KOAN' [(28-c)-p]: [('primes', 10, 1143), ('primes', 10, 18707)] []
- page 73 as 'A KOAN' [p-(28-c)]: [('primes', 19, 1143), ('primes', 19, 18707)] []
- page 74 as 'PARABLE' [c-p]: [] [1, 2, 3]
- page 74 as 'PARABLE' [p-c]: [] [1, 2, 3]

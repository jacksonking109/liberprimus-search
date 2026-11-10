# What the solving community says, and where our results stand against it

Written 2026-11-10 as step 1 of the reset in `docs/plan_repeat_shortage.md`. **Everything under "Community claims" is second-hand**: the owner read a
Discord solving forum and pasted text or screenshots. We cannot read the forum ourselves (no browser in this environment; automated reading of Discord is
against its terms), so claims are recorded as claims, and only the numbers marked "checked" were tested against our data.

## Community claims (as relayed)

* **Last page (our page 73, "AN END").** Wording: WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO [128 hex characters] ... DUTY OF EVERY PILGRIM
  SEEK OUT THIS PAGE. The digest is 512 bits; its length alone does not say SHA-512, BLAKE-512 or another algorithm. Ideas: search the web by code signatures
  (HTML, CSS) that 3301 would use; or the page is not up and has to be created or self-hosted as in 2014, when "magic squares" were put into input fields;
  counter: a page that hashes to a given digest cannot be constructed unless the Liber Primus gives its exact code.
* **Other threads.** Roman numerals as a lesson in representation ("the same symbols can look completely different once you know the representation");
  3301 is prime and its position in the primes is 464 = 16 x 29, with "either the words or their numbers" as the motto; a research plan whose theme is
  representation ("a thing can be many things, which can be a different thing..."); "epiphany seeks the devoted" from the 2016 hint; 464 words from four solved
  sections arranged into a table; "LP is a quilt" and a reading list; the unreasonable-things passage linked to a music idea ("strange loop").
* **Page 32 alignment** (the 2016 hint and page 32 both show the tree): the hint image is 563 x 569 px, matching page 32's top-row and left-column Gematria
  sums, and the 1,136-byte OutGuess payload matches a 5x5 subgrid circumference of 1,136.
* **Hearsay:** LP2 is based on the Quadrivium plus some mathematics; the 5x5 grid on page 05 (the "box of primes") holds the key, per the people leading the
  research. How it would be used is not known.
* **Common knowledge there:** frequency analysis, n-grams, bigrams, repeated sequences (a table of five repeated 5-6 rune sequences with positions).

## Checked against our data

| claim | result |
| --- | --- |
| page 73 wording | **Confirmed in full.** Our image reading of all 85 glyphs decodes end to end with the prime-totient stream and the F-skip (no sync loss): ANENDWITHINTHEDEEPWEBTHEREEXISTSAPAGETHATHASHESTO / ITISTHEDUTYOFEUERYPILGRIMTOSEECOUTTHISPAGE (U for V, C for K in the rune spelling). The manifest's 82-rune section 26 does not decode (corrupted characters); the images do |
| the hash | **Read from the image** (it is printed as Latin hex between the rune lines): 128 characters in lines of 26, 25, 25, 27, 25, read twice (by eye, and by clustering the 128 character shapes into 16 classes; the two agree). Saved in `data/lp_derived/p73_hash.txt`. Equals **none of 880 digests** (SHA-512, SHA3-512, BLAKE2b-512 and SM3 over 220 inputs: the 75 page images, the OutGuess payloads and the image inside page 03, the manifest section texts, and puzzle phrases such as 3301, DIVINITY, WELCOME and the page's own sentence) |
| page 73's other content | Red heading and drop cap, three rune lines, the hex block, two rune lines, then **five black dots** (each about 67 px across) at (1104, 2447), (873, 2517), (1604, 2686), (921, 2708), (1408, 2747) in the 2400 x 3600 image: not a regular pentagon (pairwise distances 197 to 750 px, 683 and 750 among them) |
| 3301 and 464 | Arithmetic confirmed: 3301 is prime, pi(3301) = 464 = 16 x 29. Word counts of the solved sections in the manifest text (1: 44, 3: 30, 4: 123, 5: 193, 6: 7, 7: 153, 8: 86, 9: 17, 26: 26, 27: 19) have no four that sum to 464 (closest 462, sections 3, 5, 7, 8); inconclusive, because the manifest lacks about 124 runes of page 13 and counts line ends as breaks |
| page 32 alignment | **Reproduced on our transcription** (their "page 32" is our image 49, 121 runes): top row 563, left column 569, a 5x5 circumference of 1,136 with L A W inside. Chance level about 3 in 100,000 for the 563/569 pair (`docs/avenues_explored.md` section 15) |
| repeated-sequence table | All five sequences sit at exactly the claimed positions in our stream; repeats are at chance. One typo in theirs (B-M-R-N-M gap 6,553, not 6,533) |
| the five dots point somewhere in LP2 (relayed; people are comparing them with constellations, paintings and other images, nothing found yet) | Two mechanical overlays, both negative. (1) Laid on each of the 75 pages at their own pixel coordinates, no page has all five on a rune: at most 4 (on 11 pages), hits per page 0/1/2/3/4 = 17/12/25/10/11, about chance. (2) At any shift, the number of placements where all five land on runes, against 142 rotated and reflected copies of the pattern: page 05 is highest (1,161 placements against a null mean of 148, p 0.007 for that page, about 0.5 after trying 75 pages); the rest are unremarkable. A test of the five dots against the cells of page 05's grid was inconclusive (my crude cell segmentation found 20 clusters, not 25, and no fit for any orientation). Not tested: constellations, paintings, non-rune art |
| the page 05 grid as the key | Not as a Hill matrix or repeating key (5,060 variants, nothing); any repeating or linear use also fails the repeat signature. A use with state or a lookup is untested because the use is unknown |

## Where we may add something (we cannot know what they already have)

* An independent, audited image transcription of pages 17-72 (agrees with scream314 at all but one rune; finds the page 13 gap and the page 41 error) and the
  derived table `data/lp_derived/lp2_runes.csv`.
* The anatomy of the **repeat shortage**: adjacent equal runes at 0.19 of chance, only at lag 1, the same in images and text, uniform across runes, pages and
  sections, not tied to position, neighbours or alphabet class (random thinning); no cipher in the program language reproduces it (58,024 screened); a keyed
  multiplicative running sum can, but not with EA as the trigger.
* The hash and the five dots read from page 73's image, and the full page 73 decode.

## Open questions for the forum (for the owner to ask, if they wish)

1. Has anyone hashed the HTML or JavaScript of the known onion pages and the 2014 and 2016 pages with SHA-512, SHA3-512, BLAKE2b and Whirlpool against this digest?
2. What exactly is the 2014 "magic squares into input fields" mechanism, and is page 05's grid (rows, columns and diagonals sum to the prime 1033) the same kind of object?
3. Is the repeat shortage known, and does anyone have a construction (a table lookup without fixed points, a walk on a graph, a rule on adjacent symbols) that gives it?
4. Which hint numbers beyond 563, 569, 1136 and 3301 are established, and for which pages?
5. What do the five dots on page 73 mean, if anything? Which images or patterns have already been compared with them?
6. Onion v2 services have been retired since 2021, so the 2014-era pages cannot be fetched; has anyone kept an archived copy of any of those pages (or the 2016 onion page) that could be hashed against the digest?

## Roles from here

Formalise and test concrete hypotheses from the forum against our data with a calibrated null and report back; stop open-ended sweeps, packet runs and model
spend until a hypothesis calls for them (the Codex and DeepSeek lanes and the signature gate stay built but idle).

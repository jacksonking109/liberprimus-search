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
| added dots on community "page 22" (our image 39) and Orion / Vitruvian Man as candidates for the dot patterns (relayed) | **The dots are in our file**: eight small round dots along the top of the arrow-shaped figure, at (1097, 2342), (1152, 2345), (1296, 2351), (1440, 2263), (1567, 2246), (1683, 2287), (1714, 2359), (1737, 2312) on the 2400 x 3600 image; three on the left are nearly level. Fitting them (rotation, scale, reflection, best assignment) to Orion's eight main stars (J2000 positions from memory, accurate to about 0.01 h) is no better than random 8-point sets (share as good 0.63). Page 73's five dots against the best 5 of those 8 stars: no better than random (0.32). Vitruvian Man not tested (no point set to fit) |
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

## Lead: Blake's "A Poison Tree" and the grey tree page (2026-11-11, from a relayed suggestion)
Question: are the withered tree of Blake's plate (Songs of Experience, 1794), the OutGuess images and a Liber Primus page
near 52-56 connected?

Checked from our own data
* Community page numbers are our image number minus 17, so community pages 52-56 are our images 69-73. Our images 52-56 hold
  runes only and have no tree.
* **Our image 72 (community page 55) is the page with the tree.** It is a pale grey outline of a bare, many-branched tree
  (about 1065 x 1042 px on a 2400 x 3600 page, grey level about 190, edge-traced look with jagged contours), above the black
  cicada. Rune text sits above it. The tree sits between the two black vine borders. No figure lies under it, and no poem text
  surrounds it.
* Header test: image 72 is the same type as the other pages 17-72 (400 dpi, quality 92), so it is not OutGuess output and the
  tree is not a hidden payload of that kind.
* The OutGuess payloads we have are runic text, PGP-signed messages and, on page 03, an inner runic image. None is a tree and
  none is a low-quality picture. The "low-quality OutGuess images" in the suggestion are not in our data, so that comparison
  could not be made here.

Not checked (blocked)
* This environment cannot reach Wikipedia, Wikimedia, the Blake Archive, the Uncovering Cicada wiki or the Substack write-up
  (no DNS). I did not compare against the Blake plate image itself, and the visual similarity is untested. A web search found
  no page tying "A Poison Tree" to Cicada 3301. It found only that Blake appears in other Cicada material (The Marriage of
  Heaven and Hell; a collage of four Blake paintings on the 2012 onion page), and one secondary blog mentioning a bare oak tree
  image in a later release. I did not read it, so treat the oak mention as unverified.

Dead ends so far: no poem text on or near page 72; no figure under the tree; tree is not OutGuess output; no online link found.
What would settle it: (1) the plate image and the OutGuess images from the user's side, side by side with our crop of image 72;
(2) a trace of the tree outline and a shape comparison; (3) whether the poem's runes via Gematria (or its word-sum numbers) relate
to the page's rune text or to the page 49 numbers. Not done: 3 needs a decision on which numbers count.

### Addendum: the lying figure, and a second tree (2026-11-11)
Looked at every page 17-73 as a thumbnail sheet. Pictures that are not borders or text:
* **Image 39 (community page 22, the eight-dot page):** a traced-outline figure of a person lying flat on their back, head to the
  right, legs to the left. It spans the full page width (x 0-2399) at the very bottom (y 3142-3598 of 3600) and is cut by the
  bottom edge. Above it is a black cross-shaped mark, the eight dots and one rune block. It is drawn as a high-contrast edge trace,
  the same traced look as the grey tree.
* **Image 49 (community page 32, the 11 x 11 grid page):** a **second tree**, a dark, heavily blurred bare tree, x 765-1569,
  y 2234-3137, under the 121-rune block. No figure under it.
* **Image 72 (community page 55):** the grey outline tree described above, with no figure.
* Pages 25-30 (community 8-13) have thin bare-tree borders along the margin. Those are decoration, not a lone tree.

Does the figure pair with a tree as the two halves of the poem's ending? On the page evidence, **no pairing on one page**: the
figure (image 39) and each tree (images 49 and 72) are on different pages, 10 and 33 images apart. Nothing in the pictures marks
them as a pair (no shared composition, no text). The figure's page and the page 49 tree page are both pages with designed numbers
and dots, which is a coincidence worth noting but not evidence. The poem's ending (the foe outstretched beneath the tree) would
need the figure placed under a tree, and none of our pages shows that. Untested: the figure against the Blake plate (the plate
cannot be fetched from here), and whether the three pictures are one image split across pages (a quick check would stack the
figure under each tree at matching scale and see if outlines continue; not done).
Dead ends: no text link; no shared page; blurred tree on 49 is not the grey outline tree on 72 (different rendering).

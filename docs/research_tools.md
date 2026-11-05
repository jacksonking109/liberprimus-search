# Research packets and structure diagnostics

Tools for looking at the unsolved sections without guessing a key. None of them calls a model or
the oracle, and none of them changes thresholds, null calibration or budgets.

## Packets (`python -m lpswarm.research_packets --out packets`)

A packet is a fixed list of cipher programs replayed by a scripted proposer through the normal swarm,
so the real oracle, ledger and comparison accounting apply. Each `packets/<name>/packet.md` gives the
exact targets, counts, caps, stop rule and run command. **Nothing in `packets/` has been run**; run
`lpswarm coverage --latest 3` first, then the command in the packet, only after review.

| packet | what it tests | ciphers per target |
| --- | --- | ---: |
| `exp1_feedback` | neighbour / chain feedback, with and without word reset | 261 |
| `exp2_two_shear` | determinant-one 2x2 Hill blocks, b = 0 | 33 |
| `exp2b_all_shifts` | the same with all 29 offsets (separate approval) | 957 |
| `exp3_progressive` | progressive keys `k_t = d * s(o + t)`: `naturals`, `squares`, `triangular` x scale 1..28 x offset 0..28 x sub/beaufort | 4,873 |

For `naturals` the exp3 packet is the complete arithmetic family `k_t = d*t + b` (the offset sweep
covers every b because d is invertible mod 29). `squares` and `triangular` with a scale and offset
are only a subfamily of quadratic keys; a general polynomial key would need a new stream kind.

## Structure diagnostics (`python -m lpswarm.research_structure {diffs,scans,power,all}`)

Deterministic (fixed seeds), bounded (wall-clock cap, partial results marked) and exploratory: the
units were chosen after looking at the data and p-values calibrate a maximum over the inspected
units. The null keeps each section's symbol frequencies and shuffles their order; p-values are exact
Monte Carlo (the observed sample is one of the r+1 exchangeable samples), so the smallest possible p
with 199 shuffles is 0.005.

* `diffs`: histograms of `d = c[i]-c[i-1]` and `s = c[i]+c[i-1]` (mod 29) pooled over the unsolved
  sections of 300+ runes; the same non-zero-d statistics given the observed number of repeats (the
  missing repeats must appear somewhere, so the shuffles are rescaled to the observed non-zero
  total); repeats within words and across word boundaries; the 29x29 transition table (chi-square
  with and without the diagonal, cells with count <= 1); and whether the sections look like one
  population (chi-square of homogeneity, per-section z).
* `scans`: plug-in mutual information between `c[i]` and `c[i-k]`, k = 1..64, and the index of
  coincidence of `c[i] + r*c[i-k]`, r = 1..28, k = 1..16 (448 transforms; scaling relabels residues,
  so r = b/a covers every `a*c[i-k] + b*c[i]`). Run twice: on all pairs, and with equal pairs
  (`c[i] == c[i-k]`) excluded, which removes the known repeat shortage so that what is left is
  dependence beyond it.
* `power`: English plaintext (training split) put through neighbour feedback, chain autokey,
  a progressive key, a prime stream, 2x2 Hill blocks, a length-37 periodic key, plus plaintext and
  iid noise, at several lengths, with every test above run on each. It says what a diagnostic can see.
  A real section that shows nothing is only evidence against the mechanisms its row detects.
  Synthetic data only; no held-out split.

Outputs: `diagnostics_structure.json` and `diagnostics_structure.md` in `--out` (default
`reports/diag`). A reference run on the bundled transcription is in `docs/diagnostics_sample/`.

## Limits

* The power table uses English plaintext. If the true plaintext is another language, abbreviated or
  not language at all, pairwise structure is weaker than the table suggests.
* Position-keyed streams with a non-repeating key (prime, totient, Fibonacci) leave no pairwise
  structure: the power table shows these diagnostics mostly cannot see them. Absence of pairwise
  dependence says nothing for or against those.
* Mutual information is the plug-in estimate (bias about 784 / 2m nats); only z against the shuffle
  null is used for decisions.
* Word breaks are those of the transcription (the bullet separators). Line breaks are not used.

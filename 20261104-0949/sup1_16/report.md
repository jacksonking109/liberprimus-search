# Swarm run

Updated 2026-11-04 12:45:20. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 16 --generators claude-opus --rounds 4 --per-round 6 --report-dir reports\overnight\20261104-0949\sup1_16 --ledger reports\overnight\20261104-0949\sup1_16\ledger.sqlite --brief-file reports\overnight\20261104-0949\sup1_16\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 179 call(s) in the last 5h (cap 550)
- claude-sonnet: 179 call(s) in the last 5h (cap 550)
- claude-supervisor: 179 call(s) in the last 5h (cap 550)
- codex: 81 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:15.jpg/2- - 32.jpg/2-39.jpg | 1894 | 11271 | 23 | 0 |  |

## LP2:15.jpg/2- - 32.jpg/2-39.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus | 24 | 1 | 11271 | 0 | 2 | 0 |

- near_miss (program, by claude-opus, margin -2.37; chance 4.3e+02: noise level (pure noise does this well that often)): `beaufort; sequence primes*3+2 @1392; map reverse; skip [0] (resolve)` 
  `EDOOUNONEXULBTPEOOEDEYLOFTEOTHYCSRGTNJRDYAEFTMPBIORPHNGITHAELJJOINGOEJYINGTHBEDTHTEOXTWRWIURFYO`
- near_miss (program, by claude-opus, margin -2.39; chance 3.9e+02: noise level (pure noise does this well that often)): `add; sequence prime_totients*5+3 @707; skip [27] (resolve)` 
  `GNGPTHEAGDGDNTHJEOOEWFPMJBPLNHFSEATHXFJCMPESTBPSDFDNGIORAERXIOPTNGLTITDOEEOGTHGNGIOTHTHFCDXEJIOGNGCRD`

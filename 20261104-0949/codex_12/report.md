# Swarm run

Updated 2026-11-04 11:40:30. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 12 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\codex_12 --ledger reports\overnight\20261104-0949\codex_12\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 128 call(s) in the last 5h (cap 550)
- claude-sonnet: 128 call(s) in the last 5h (cap 550)
- claude-supervisor: 128 call(s) in the last 5h (cap 550)
- codex: 69 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1 | 693 | 11780 | 20 | 0 | stop_file |

## LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 24 | 0 | 11780 | 0 | 1 | 0 |

- near_miss (program, by codex, margin -2.41; chance 4.8e+02: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @913; skip [0] (resolve)` 
  `MWWEAFEOJTHXUCPTJBDXOHRNNYHEAFBBTHOIYBIYNGEOEHUDAFEAETCGNETEWTHEOEOEOOEAENUIOUSRFXANGYAEEAFSIOHTHJT`

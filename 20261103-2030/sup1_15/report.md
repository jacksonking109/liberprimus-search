# Swarm run

Updated 2026-11-03 22:35:42. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 15 --generators codex,qwen-local,gemma-local --rounds 4 --per-round 4 --report-dir reports\overnight\20261103-2030\sup1_15 --ledger reports\overnight\20261103-2030\sup1_15\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 50 call(s) in the last 5h (cap 120)
- claude-sonnet: 50 call(s) in the last 5h (cap 120)
- claude-supervisor: 50 call(s) in the last 5h (cap 200)
- codex: 22 call(s) in the last 5h (cap 100)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:15.jpg/1 - 32.jpg/1 | 9 | 12380 | 62 | 0 |  |

## LP2:15.jpg/1 - 32.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 0 | 12330 | 0 | 3 | 0 |
| qwen-local | 16 | 0 | 26 | 0 | 0 | 0 |
| gemma-local | 16 | 2 | 24 | 0 | 0 | 0 |

- near_miss (program, by codex, margin -1.31): `sub; sequence pi_digits*1+0 @1894; skip [24] (resolve)` 
  `DAMEALLMA`
- near_miss (program, by codex, margin -1.50): `sub; sequence pi_digits*1+0 @1506; skip [24] (resolve)` 
  `AIOTSAMESA`
- near_miss (program, by codex, margin -1.54): `sub; sequence pi_digits*1+0 @972; skip [24] (resolve)` 
  `YULEAMAST`
- near_miss (program, by codex, margin -1.57): `sub; sequence primes*1+0 @1978; map reverse; skip [0] (resolve)` 
  `WRTHEANGAERY`
- near_miss (program, by codex, margin -1.57): `sub; sequence primes*1+0 @1979; map reverse; skip [0] (resolve)` 
  `FRTHEANGAERY`
- near_miss (program, by codex, margin -1.61): `sub; sequence pi_digits*1+0 @1765; skip [24] (resolve)` 
  `DUMPADDEE`
- near_miss (program, by codex, margin -1.64): `sub; sequence primes*1+0 @802; map reverse; skip [0] (resolve)` 
  `PTHBTWALLI`
- near_miss (program, by codex, margin -1.64): `sub; sequence primes*1+0 @803; map reverse; skip [0] (resolve)` 
  `FTHBTWALLI`
- near_miss (program, by codex, margin -1.67): `sub; sequence pi_digits*1+0 @1818; skip [24] (resolve)` 
  `FNGSTALEMA`
- near_miss (program, by codex, margin -1.74): `sub; sequence pi_digits*1+0 @129; skip [24] (resolve)` 
  `LAESMADELA`

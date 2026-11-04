# Swarm run

Updated 2026-11-04 12:15:43. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 13 --generators claude-opus --rounds 4 --per-round 6 --report-dir reports\overnight\20261104-0949\sup1_13 --ledger reports\overnight\20261104-0949\sup1_13\ledger.sqlite --brief-file reports\overnight\20261104-0949\sup1_13\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 170 call(s) in the last 5h (cap 550)
- claude-sonnet: 170 call(s) in the last 5h (cap 550)
- claude-supervisor: 170 call(s) in the last 5h (cap 550)
- codex: 81 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:6.jpg/2-7.jpg - 23.jpg/2-24.jpg | 333 | 9314 | 23 | 0 |  |

## LP2:6.jpg/2-7.jpg - 23.jpg/2-24.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus | 24 | 0 | 9314 | 0 | 2 | 0 |

- near_miss (program, by claude-opus, margin -0.20; chance 27: noise level (pure noise does this well that often)): `sub; sequence squares*2+3 @5; skip [27] (resolve)` 
  `FEAFTHEAGIOTHTNGDBTIOEOGUHFUNGYXIOIOPFEACCNGCEOEPJNGBIOICGDAEBNPYJHSEOHIYCNEAUNSTHISLCTHGTHXLPLLCWTHIO`
- near_miss (program, by claude-opus, margin -0.20; chance 32: noise level (pure noise does this well that often)): `sub; sequence primes*5+4 @807; map reverse; skip [27] (resolve)` 
  `RJOEHOATHPUOPBROEAPYPNGAEYFAEOHFIBJUGIOUNEOJOEAENGTHCPTHNHUJXOYAEULHARGMOEEPIOXEAFNDOMRAENHAEPAEMEOTEO`
- near_miss (program, by claude-opus, margin -0.22; chance 71: noise level (pure noise does this well that often)): `sub; sequence squares*2+3 @2; skip [27] (resolve)` 
  `PAHOETHNGIOFYXEACTIWPLIXIOUEEOSTCFWNGFATHLMAEXEXTHUGIORFAERNGIJOEDDFLOJCJDRAWTAEXSDHRXANGOWAETHUP`

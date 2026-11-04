# Swarm run

Updated 2026-11-03 23:41:41. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 22 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\codex_22 --ledger reports\overnight\20261103-2310\codex_22\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 129 call(s) in the last 5h (cap 120), paused until 2026-11-04 01:32 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 129 call(s) in the last 5h (cap 550)
- claude-supervisor: 129 call(s) in the last 5h (cap 200)
- codex: 57 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:57.jpg-66.jpg/1 | 2474 | 32546 | 48 | 0 |  |

## LP2:57.jpg-66.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 0 | 32546 | 0 | 2 | 0 |

- near_miss (program, by codex, margin -2.38): `sub; sequence prime_totients*1+0 @1981; skip [0] (resolve)` 
  `FFHOEDOEMFIIWPEXLTPCGJEAIFPFEJSIJTNGOMYWWOEOWLPANFIOUAEEASTSADUXTHFEAMEDOEYUTHIWRLNWGEARUPXWIO`
- near_miss (program, by codex, margin -2.38): `add; sequence e_digits*1+0 @153; skip [28] (resolve)` 
  `CSOEYPYRNIOSBEATEEACAEAEAETHAMTNGOEYHNGTHWAEEOUGGXEAEIDMGOFDSSDJEFBDLJEOAEREAREAJIODTXMYCCMDUTHBEATHW`
- near_miss (program, by codex, margin -2.40): `add; sequence e_digits*1+0 @152; skip [28] (resolve)` 
  `NXAEFGUEATAETTFILCCAEAEAETHAMTNGOEYHNGTHWAEEOUGGXEAEIDMGOFDSSDJEFBDLJEOAEREAREAJIODTXMYCCMDUTHBEATHW`

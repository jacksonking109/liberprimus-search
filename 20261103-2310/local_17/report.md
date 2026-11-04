# Swarm run

Updated 2026-11-03 23:14:52. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 17 --generators qwen-local,gemma-local --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\local_17 --ledger reports\overnight\20261103-2310\local_17\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 77 call(s) in the last 5h (cap 120)
- claude-sonnet: 77 call(s) in the last 5h (cap 550)
- claude-supervisor: 77 call(s) in the last 5h (cap 200)
- codex: 44 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:- - 40.jpg-43.jpg | 1021 | 190 | 81 | 0 |  |

## LP2:- - 40.jpg-43.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen-local | 48 | 0 | 139 | 0 | 0 | 0 |
| gemma-local | 48 | 4 | 51 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

# Swarm run

Updated 2026-11-03 22:44:53. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 16 --generators codex,qwen-local,gemma-local --rounds 4 --per-round 4 --report-dir reports\overnight\20261103-2030\sup1_16 --ledger reports\overnight\20261103-2030\sup1_16\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 63 call(s) in the last 5h (cap 120)
- claude-sonnet: 63 call(s) in the last 5h (cap 120)
- claude-supervisor: 63 call(s) in the last 5h (cap 200)
- codex: 26 call(s) in the last 5h (cap 100)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:15.jpg/2- - 32.jpg/2-39.jpg | 1894 | 19149 | 58 | 0 |  |

## LP2:15.jpg/2- - 32.jpg/2-39.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 0 | 19115 | 0 | 0 | 0 |
| qwen-local | 16 | 1 | 13 | 0 | 0 | 0 |
| gemma-local | 16 | 2 | 21 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

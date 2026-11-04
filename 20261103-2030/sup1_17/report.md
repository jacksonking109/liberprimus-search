# Swarm run

Updated 2026-11-03 22:52:16. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 17 --generators codex,qwen-local,gemma-local --rounds 4 --per-round 4 --report-dir reports\overnight\20261103-2030\sup1_17 --ledger reports\overnight\20261103-2030\sup1_17\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 64 call(s) in the last 5h (cap 120)
- claude-sonnet: 64 call(s) in the last 5h (cap 120)
- claude-supervisor: 64 call(s) in the last 5h (cap 200)
- codex: 30 call(s) in the last 5h (cap 100)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:- - 40.jpg-43.jpg | 1021 | 22165 | 62 | 0 |  |

## LP2:- - 40.jpg-43.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 0 | 22133 | 0 | 0 | 0 |
| qwen-local | 16 | 0 | 17 | 0 | 0 | 0 |
| gemma-local | 16 | 1 | 15 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

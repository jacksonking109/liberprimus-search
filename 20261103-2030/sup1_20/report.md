# Swarm run

Updated 2026-11-03 23:08:30. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 20 --generators codex,qwen-local,gemma-local --rounds 4 --per-round 4 --report-dir reports\overnight\20261103-2030\sup1_20 --ledger reports\overnight\20261103-2030\sup1_20\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 65 call(s) in the last 5h (cap 120)
- claude-sonnet: 65 call(s) in the last 5h (cap 550)
- claude-supervisor: 65 call(s) in the last 5h (cap 200)
- codex: 39 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:50.jpg/2-56.jpg/1 | 1468 | 3940 | 4 | 0 | stop_file |

## LP2:50.jpg/2-56.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 8 | 0 | 3940 | 0 | 0 | 0 |
| qwen-local | 0 | 0 | 0 | 0 | 0 | 0 |
| gemma-local | 0 | 0 | 0 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

# Swarm run

Updated 2026-11-03 22:33:00. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 14 --generators codex,qwen-local,gemma-local --rounds 4 --per-round 4 --report-dir reports\overnight\20261103-2030\sup1_14 --ledger reports\overnight\20261103-2030\sup1_14\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 40 call(s) in the last 5h (cap 120)
- claude-sonnet: 40 call(s) in the last 5h (cap 120)
- claude-supervisor: 40 call(s) in the last 5h (cap 200)
- codex: 18 call(s) in the last 5h (cap 100)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:8.jpg-14.jpg - 25.jpg-31.jpg | 1729 | 2347 | 4 | 0 | stop_file |

## LP2:8.jpg-14.jpg - 25.jpg-31.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 8 | 0 | 2347 | 0 | 0 | 0 |
| qwen-local | 0 | 0 | 0 | 0 | 0 | 0 |
| gemma-local | 0 | 0 | 0 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

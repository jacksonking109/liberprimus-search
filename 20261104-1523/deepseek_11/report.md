# Swarm run

Updated 2026-11-04 17:35:42. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 11 --generators deepseek --rounds 6 --per-round 16 --max-attempts 60000 --report-dir reports\overnight\20261104-1523\deepseek_11 --ledger reports\overnight\20261104-1523\deepseek_11\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0251, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 191 call(s) in the last 5h (cap 550)
- claude-sonnet: 191 call(s) in the last 5h (cap 550)
- claude-supervisor: 191 call(s) in the last 5h (cap 550)
- codex: 85 call(s) in the last 5h (cap 850)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/1 - 3.jpg/1 | 119 | 36628 | 67 | 0 |  |

## LP2:20.jpg/1 - 3.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| deepseek | 96 | 25 | 36628 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

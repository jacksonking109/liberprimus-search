# Swarm run

Updated 2026-11-04 23:17:06. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 12 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-2305\sonnet_12 --ledger reports\overnight\20261104-2305\sonnet_12\ledger.sqlite --strategy-file reports\overnight\20261104-2305\strategy.txt --auto-brief claude-supervisor --brief-context reports\overnight\20261104-2305\sonnet_12\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.1873, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 50 call(s) in the last 5h (cap 180)
- claude-sonnet: 50 call(s) in the last 5h (cap 180)
- claude-supervisor: 50 call(s) in the last 5h (cap 180)
- codex: 55 call(s) in the last 5h (cap 850)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1 | 693 | 60000 | 2 | 0 | max_attempts |

## LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 12 | 6 | 60000 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

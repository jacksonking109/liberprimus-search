# Swarm run

Updated 2026-11-05 01:30:41. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 24 --generators codex --rounds 6 --per-round 12 --max-attempts 300000 --report-dir reports\overnight\20261104-2305\structure_24 --ledger reports\overnight\20261104-2305\structure_24\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\sonnet_24\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\codex_24\ledger.sqlite --strategy-file reports\overnight\20261104-2305\strategy.txt --brief-file reports\overnight\20261104-2305\structure_24\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.2497, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 80 call(s) in the last 5h (cap 180)
- claude-sonnet: 80 call(s) in the last 5h (cap 180)
- claude-supervisor: 80 call(s) in the last 5h (cap 180)
- codex: 53 call(s) in the last 5h (cap 850)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg | 534 | 300000 | 65 | 0 | max_attempts |

## LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 65 | 0 | 300000 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

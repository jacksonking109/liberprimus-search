# Swarm run

Updated 2026-11-05 04:45:24. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 21 --generators codex --rounds 2 --per-round 12 --max-attempts 5000000 --report-dir reports\overnight\20261104-2305\exhaustive_21 --ledger reports\overnight\20261104-2305\exhaustive_21\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\sonnet_21\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\codex_21\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\local_21\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\deepseek_21\ledger.sqlite --strategy-file reports\overnight\20261104-2305\strategy.txt --brief-file reports\overnight\20261104-2305\exhaustive_21\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.3613, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 45 call(s) in the last 5h (cap 180)
- claude-sonnet: 45 call(s) in the last 5h (cap 180)
- claude-supervisor: 45 call(s) in the last 5h (cap 180)
- codex: 12 call(s) in the last 5h (cap 850)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:56.jpg/2 | 121 | 5000000 | 31 | 0 | max_attempts |

## LP2:56.jpg/2

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 0 | 5000000 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

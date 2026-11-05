# Swarm run

Updated 2026-11-04 23:03:56. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 22 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-2300\codex_22 --ledger reports\overnight\20261104-2300\codex_22\ledger.sqlite --strategy-file reports\overnight\20261104-2300\strategy.txt --auto-brief claude-supervisor --brief-context reports\overnight\20261104-2300\codex_22\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.1873, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 30 call(s) in the last 5h (cap 180)
- claude-sonnet: 30 call(s) in the last 5h (cap 180)
- claude-supervisor: 30 call(s) in the last 5h (cap 180)
- codex: 34 call(s) in the last 5h (cap 850)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:57.jpg-66.jpg/1 | 2474 | 6645 | 4 | 0 | stop_file |

## LP2:57.jpg-66.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 1 | 6645 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

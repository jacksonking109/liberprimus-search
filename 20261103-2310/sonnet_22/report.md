# Swarm run

Updated 2026-11-04 02:13:55. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 22 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\sonnet_22 --ledger reports\overnight\20261103-2310\sonnet_22\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261103-2310\sonnet_22\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 172 call(s) in the last 5h (cap 120), paused until 2026-11-04 04:19 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 172 call(s) in the last 5h (cap 550)
- claude-supervisor: 172 call(s) in the last 5h (cap 200)
- codex: 122 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:57.jpg-66.jpg/1 | 2474 | 6592 | 45 | 0 |  |

## LP2:57.jpg-66.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 48 | 3 | 6592 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

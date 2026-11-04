# Swarm run

Updated 2026-11-04 00:02:04. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 13 --generators qwen-local,gemma-local --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\local_13 --ledger reports\overnight\20261103-2310\local_13\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 143 call(s) in the last 5h (cap 120), paused until 2026-11-04 01:41 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 143 call(s) in the last 5h (cap 550)
- claude-supervisor: 143 call(s) in the last 5h (cap 200)
- codex: 76 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:6.jpg/2-7.jpg - 23.jpg/2-24.jpg | 333 | 239 | 86 | 0 |  |

## LP2:6.jpg/2-7.jpg - 23.jpg/2-24.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen-local | 48 | 1 | 99 | 0 | 0 | 0 |
| gemma-local | 48 | 2 | 140 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

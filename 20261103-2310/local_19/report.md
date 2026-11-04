# Swarm run

Updated 2026-11-03 23:36:26. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 19 --generators qwen-local,gemma-local --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\local_19 --ledger reports\overnight\20261103-2310\local_19\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 124 call(s) in the last 5h (cap 120), paused until 2026-11-04 01:31 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 124 call(s) in the last 5h (cap 550)
- claude-supervisor: 124 call(s) in the last 5h (cap 200)
- codex: 57 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:33.jpg - 50.jpg/1 | 91 (short) | 120 | 88 | 0 |  |

## LP2:33.jpg - 50.jpg/1

**Caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution.**

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen-local | 48 | 0 | 41 | 0 | 0 | 0 |
| gemma-local | 48 | 0 | 79 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

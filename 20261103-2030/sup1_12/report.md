# Swarm run

Updated 2026-11-03 22:26:19. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 12 --generators codex,qwen-local,gemma-local --rounds 4 --per-round 4 --report-dir reports\overnight\20261103-2030\sup1_12 --ledger reports\overnight\20261103-2030\sup1_12\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 40 call(s) in the last 5h (cap 40), paused until 2026-11-04 01:27 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 40 call(s) in the last 5h (cap 40), paused until 2026-11-04 01:27 (local cap, raise max_calls_per_window to allow more)
- claude-supervisor: 40 call(s) in the last 5h (cap 40), paused until 2026-11-04 01:27 (local cap, raise max_calls_per_window to allow more)
- codex: 13 call(s) in the last 5h (cap 30)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1 | 693 | 18302 | 61 | 0 |  |

## LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 0 | 18163 | 0 | 0 | 0 |
| qwen-local | 16 | 0 | 115 | 0 | 0 | 0 |
| gemma-local | 16 | 1 | 24 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

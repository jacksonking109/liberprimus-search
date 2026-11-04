# Swarm run

Updated 2026-11-04 02:34:40. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 17 --generators claude-sonnet --rounds 4 --per-round 6 --report-dir reports\overnight\20261103-2310\sup2_17 --ledger reports\overnight\20261103-2310\sup2_17\ledger.sqlite --brief-file reports\overnight\20261103-2310\sup2_17\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 201 call(s) in the last 5h (cap 120), paused until 2026-11-04 04:34 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 201 call(s) in the last 5h (cap 550)
- claude-supervisor: 201 call(s) in the last 5h (cap 200), paused until 2026-11-04 03:34 (local cap, raise max_calls_per_window to allow more)
- codex: 128 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:- - 40.jpg-43.jpg | 1021 | 9019 | 19 | 0 |  |

## LP2:- - 40.jpg-43.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 24 | 5 | 9019 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

# Swarm run

Updated 2026-11-03 22:31:12. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 13 --generators codex,qwen-local,gemma-local --rounds 4 --per-round 4 --report-dir reports\overnight\20261103-2030\sup1_13 --ledger reports\overnight\20261103-2030\sup1_13\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 40 call(s) in the last 5h (cap 40), paused until 2026-11-04 01:27 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 40 call(s) in the last 5h (cap 40), paused until 2026-11-04 01:27 (local cap, raise max_calls_per_window to allow more)
- claude-supervisor: 40 call(s) in the last 5h (cap 40), paused until 2026-11-04 01:27 (local cap, raise max_calls_per_window to allow more)
- codex: 17 call(s) in the last 5h (cap 30)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:6.jpg/2-7.jpg - 23.jpg/2-24.jpg | 333 | 20452 | 62 | 0 |  |

## LP2:6.jpg/2-7.jpg - 23.jpg/2-24.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 0 | 20270 | 0 | 1 | 0 |
| qwen-local | 16 | 0 | 68 | 0 | 0 | 0 |
| gemma-local | 16 | 1 | 114 | 0 | 0 | 0 |

- near_miss (program, by codex, margin -0.27): `sub; sequence e_digits*1+0 @573; skip [28] (resolve)` 
  `SXJHJREJNGCYGEAOERNGLHTJOYDBCSRODJSLFFOTHIOENGAMDIAEYNUOEAENNNGEATHWUMPIPTIONYPRTHLEAWIAELNGLWOE`

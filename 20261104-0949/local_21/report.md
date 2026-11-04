# Swarm run

Updated 2026-11-04 10:31:39. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 21 --generators qwen-local,gemma-local --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\local_21 --ledger reports\overnight\20261104-0949\local_21\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 68 call(s) in the last 5h (cap 550)
- claude-sonnet: 68 call(s) in the last 5h (cap 550)
- claude-supervisor: 68 call(s) in the last 5h (cap 550)
- codex: 28 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:56.jpg/2 | 121 | 152 | 86 | 0 |  |

## LP2:56.jpg/2

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen-local | 48 | 1 | 84 | 0 | 0 | 0 |
| gemma-local | 48 | 4 | 68 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

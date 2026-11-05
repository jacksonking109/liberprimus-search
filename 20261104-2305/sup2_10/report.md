# Swarm run

Updated 2026-11-05 06:35:22. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 10 --generators codex --rounds 4 --per-round 6 --report-dir reports\overnight\20261104-2305\sup2_10 --ledger reports\overnight\20261104-2305\sup2_10\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\sonnet_10\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\codex_10\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\local_10\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\structure_10\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\deepseek_10\ledger.sqlite --strategy-file reports\overnight\20261104-2305\strategy.txt --brief-file reports\overnight\20261104-2305\sup2_10\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.3613, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 26 call(s) in the last 5h (cap 180)
- claude-sonnet: 26 call(s) in the last 5h (cap 180)
- claude-supervisor: 26 call(s) in the last 5h (cap 180)
- codex: 5 call(s) in the last 5h (cap 850)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:17.jpg, 18.jpg, 19.jpg - 0.jpg-2.jpg | 729 | 50000 | 18 | 0 | max_attempts |

## LP2:17.jpg, 18.jpg, 19.jpg - 0.jpg-2.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 0 | 50000 | 0 | 0 | 0 |

No passes or near misses: everything tried is recorded as ruled out.

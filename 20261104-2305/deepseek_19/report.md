# Swarm run

Updated 2026-11-05 02:47:34. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 19 --generators deepseek --rounds 6 --per-round 16 --max-attempts 60000 --report-dir reports\overnight\20261104-2305\deepseek_19 --ledger reports\overnight\20261104-2305\deepseek_19\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\sonnet_19\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\codex_19\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\local_19\ledger.sqlite --peer-ledger reports\overnight\20261104-2305\exhaustive_19\ledger.sqlite --strategy-file reports\overnight\20261104-2305\strategy.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.2906, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 83 call(s) in the last 5h (cap 180)
- claude-sonnet: 83 call(s) in the last 5h (cap 180)
- claude-supervisor: 83 call(s) in the last 5h (cap 180)
- codex: 55 call(s) in the last 5h (cap 850)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:33.jpg - 50.jpg/1 | 91 (short) | 60000 | 69 | 0 | max_attempts |

## LP2:33.jpg - 50.jpg/1

**Caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution.**

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| deepseek | 97 | 22 | 60000 | 0 | 1 | 0 |

- near_miss (program, by deepseek, margin -2.14; chance 7.6e+02: noise level (pure noise does this well that often)): `sub; sequence triangular*1+0 @12; skip [0] (resolve)` 
  `OHAEUNTHIOLUWLWMISNGEAAYEOFTPBOEBGMEAOAESGSLFYTHMOESTALWHXYNGITAJFFGOEEOUTADTHLRAEMIAELTGDPYSCY`
- near_miss (program, by deepseek, margin -2.17; chance 1.1e+03: noise level (pure noise does this well that often)): `sub; sequence triangular*1+0 @13; skip [0] (resolve)` 
  `MDIXFTHIOLUWLWMISNGEAAYEOFTPBOEBGMEAOAESGSLFYTHMOESTALWHXYNGITAJFFGOEEOUTADTHLRAEMIAELTGDPYSCY`

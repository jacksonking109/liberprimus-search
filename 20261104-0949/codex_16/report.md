# Swarm run

Updated 2026-11-04 11:20:48. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 16 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\codex_16 --ledger reports\overnight\20261104-0949\codex_16\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 106 call(s) in the last 5h (cap 550)
- claude-sonnet: 106 call(s) in the last 5h (cap 550)
- claude-supervisor: 106 call(s) in the last 5h (cap 550)
- codex: 54 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:15.jpg/2- - 32.jpg/2-39.jpg | 1894 | 24778 | 48 | 0 |  |

## LP2:15.jpg/2- - 32.jpg/2-39.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 0 | 24778 | 0 | 2 | 0 |

- near_miss (program, by codex, margin -2.37; chance 9.1e+02: noise level (pure noise does this well that often)): `beaufort; sequence pi_digits*1+0 @1055; skip [0] (resolve)` 
  `NFTAEYHEEAOENPYGOECNGDNPOAEAEAETCCEEOBHOENODNDNTHHADBTNGOTHGDIULNGTMEACIOIOOCAEAEYJBOEADCJETFREHLT`
- near_miss (program, by codex, margin -2.37; chance 9.4e+02: noise level (pure noise does this well that often)): `beaufort; sequence pi_digits*1+0 @1056; skip [0] (resolve)` 
  `IWPOERCLFOECSYTHAEUNNIOFPOAEAEAETCCEEOBHOENODNDNTHHADBTNGOTHGDIULNGTMEACIOIOOCAEAEYJBOEADCJETFREHLT`
- near_miss (program, by codex, margin -2.39; chance 9.5e+02: noise level (pure noise does this well that often)): `beaufort; sequence prime_totients*1+0 @554; skip [28] (resolve); reverse text` 
  `THNAEIOPEOTPDDNGGEOYEAEAAEDOEGTHAWEAEANGAEDEAAERAEPLPGPGYHCPHEATHEMDEADJGCEOWDIRTOECNGAHWYREDOCEAHEOHYO`

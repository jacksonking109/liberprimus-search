# Swarm run

Updated 2026-11-04 00:12:12. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 13 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\sonnet_13 --ledger reports\overnight\20261103-2310\sonnet_13\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261103-2310\sonnet_13\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 148 call(s) in the last 5h (cap 120), paused until 2026-11-04 01:44 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 148 call(s) in the last 5h (cap 550)
- claude-supervisor: 148 call(s) in the last 5h (cap 200)
- codex: 82 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:6.jpg/2-7.jpg - 23.jpg/2-24.jpg | 333 | 51522 | 42 | 0 |  |

## LP2:6.jpg/2-7.jpg - 23.jpg/2-24.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 48 | 6 | 51522 | 0 | 3 | 0 |

- near_miss (program, by claude-sonnet, margin -0.31): `sub; sequence prime_totients*1+0 @1880; skip [0] (resolve); columnar [2, 1, 0]` 
  `NPXFMEAEOOTHPTSNGWHICFFBTHEAMOXBIOELGEAFAYMPYBAEGYIONOEDOJNGUCRMREARREMLEARYGANONAPLMHSIOSSWOEAW`
- near_miss (program, by claude-sonnet, margin -0.33): `sub; sequence prime_totients*1+0 @1426; skip [0] (resolve); columnar [1, 2, 0]` 
  `UIBBSAWNGDYWHEOHERAOEGRAEBFUWYIOYCNYMCWGOESALMMAUNGAREEANEAWGGNGJGAANMRHXYGTHTHECCSNXIUTGLNG`
- near_miss (program, by claude-sonnet, margin -0.34): `sub; sequence prime_totients*1+0 @1236; skip [0] (resolve); columnar [2, 0, 1]` 
  `IOYMEAGEOLYNGINWDOEJERAWEYNSNGYASAYEAWRHGOLMOENOWOGWSFENGAEWMINGNGHOTHIOLOMNGIORPWEABIOGGCWPCUTLGO`

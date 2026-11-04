# Swarm run

Updated 2026-11-04 01:27:26. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 12 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\codex_12 --ledger reports\overnight\20261103-2310\codex_12\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 169 call(s) in the last 5h (cap 120), paused until 2026-11-04 03:35 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 169 call(s) in the last 5h (cap 550)
- claude-supervisor: 169 call(s) in the last 5h (cap 200)
- codex: 111 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1 | 693 | 34409 | 48 | 0 |  |

## LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 0 | 34409 | 0 | 3 | 0 |

- near_miss (program, by codex, margin -2.40): `add; sequence e_digits*1+0 @1187; skip [27] (resolve)` 
  `OEIOGLOECIOCWEOHTYTHGGBBINXUAEIOEBAEUNNGDOEXRXNALLMEAWEOUWOJEINTSEXFEABEOIOIORWCAERNGOJTHGLTHCEULHT`
- near_miss (program, by codex, margin -2.40): `beaufort; sequence pi_digits*1+0 @293; skip [27] (resolve)` 
  `LSEANGWMJEOTHRNGGFFIORCNGMUYYPBTSIOHNTHSXTSGDOESTPEWNYHEARFXCAANGAEEANHOEFPGGOUJGPYYWIOLFREUBUD`
- near_miss (program, by codex, margin -2.41): `beaufort; sequence pi_digits*1+0 @294; skip [27] (resolve)` 
  `AEWTHEHAWTYIONGGFFIORCNGMUYYPBTSIOHNTHSXTSGDOESTPEWNYHEARFXCAANGAEEANHOEFPGGOUJGPYYWIOLFREUBUD`
- near_miss (program, by codex, margin -2.41): `add; sequence e_digits*1+0 @1470; skip [0] (resolve)` 
  `MYGMEATTHDXRTOSTLYOCPAETHHHULYDSIOHXMFNGNGEONNTHYOEMUFPRCUNLISSMSPFCSSFOHXRAEFOENJUIMCHBUBHL`

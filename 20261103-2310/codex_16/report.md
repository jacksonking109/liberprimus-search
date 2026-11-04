# Swarm run

Updated 2026-11-04 00:48:24. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 16 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\codex_16 --ledger reports\overnight\20261103-2310\codex_16\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 162 call(s) in the last 5h (cap 120), paused until 2026-11-04 03:34 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 162 call(s) in the last 5h (cap 550)
- claude-supervisor: 162 call(s) in the last 5h (cap 200)
- codex: 93 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:15.jpg/2- - 32.jpg/2-39.jpg | 1894 | 32313 | 47 | 0 |  |

## LP2:15.jpg/2- - 32.jpg/2-39.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 1 | 32313 | 0 | 3 | 0 |

- near_miss (program, by codex, margin -2.36): `sub; sequence pi_digits*1+0 @109; skip [0] (resolve)` 
  `SFEWYEAXNIDBOUUIOXNGWFMUYNWPNEYENGPSEOOEEAOMCAYFRUNIHUTHDGOERXTHPJCFRAETHDUIFOESGEOHEAENWAOEPFNEO`
- near_miss (program, by codex, margin -2.37): `sub; sequence pi_digits*1+0 @110; skip [0] (resolve)` 
  `MIOMUOIOBOIFBOUUIOXNGWFMUYNWPNEYENGPSEOOEEAOMCAYFRUNIHUTHDGOERXTHPJCFRAETHDUIFOESGEOHEAENWAOEPFNEO`
- near_miss (program, by codex, margin -2.37): `sub; sequence pi_digits*1+0 @1308; skip [0, 28] (resolve)` 
  `PUMUAEOEHHJFMNUGDBDIFMEAGNGRHLEALOEIOENMTHCEAUDFUCFIPHUUAEWAAEXGXEOCFOIOYTOWRIOSOGRABINIOAJFEOC`
- near_miss (program, by codex, margin -2.37): `sub; sequence pi_digits*1+0 @277; map reverse; skip [0] (resolve)` 
  `THDEABOEAHINFUELTNGGUPMTHDNGEONEOWFAEOAEWGXALLDTOEOEXJXOSEBYPEAAOTJWBYXDBTHPJLNGIXXSNGEAINNGAOMJN`
- near_miss (program, by codex, margin -2.37): `sub; sequence pi_digits*1+0 @1305; skip [0, 28] (resolve)` 
  `BAXTHCEANFHFEONAEHFOENGRFLEACHIPNLEAJEHOEEODTHOLNNGYFUNEONGYTHFHOEUPTHSHTHFGOEAMCCUNGPWJRYMCIYMXFPH`

# Swarm run

Updated 2026-11-04 01:49:35. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 19 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\sonnet_19 --ledger reports\overnight\20261103-2310\sonnet_19\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261103-2310\sonnet_19\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 149 call(s) in the last 5h (cap 120), paused until 2026-11-04 04:11 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 149 call(s) in the last 5h (cap 550)
- claude-supervisor: 149 call(s) in the last 5h (cap 200)
- codex: 122 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:33.jpg - 50.jpg/1 | 91 (short) | 26509 | 23 | 0 |  |

## LP2:33.jpg - 50.jpg/1

**Caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution.**

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 48 | 24 | 26509 | 0 | 12 | 0 |

- near_miss (program, by claude-sonnet, margin -2.02): `beaufort; sequence pi_digits*1+0 @1340; skip [0] (resolve)` 
  `NAETFFMGTHAEAEHFSTIRPREYOUDONRRHXOEBXIINGMFGNGDIIJNYOEDFJJCSAEOEBEACFTHEOJNGWWFYWNGNIOIEDEOMHJETH`
- near_miss (program, by claude-sonnet, margin -2.04): `sub; sequence prime_totients*1+0 @887; skip [0] (resolve); reverse text` 
  `TONGIIOEONGUIOXAEGRWRPSTABXDXNGAESCSLWAEWAEOEOMFAAGEAFIOIWNCIOXANREANYDXLNSNGTNLLNGOYFWNRAESCYHE`
- near_miss (program, by claude-sonnet, margin -2.05): `beaufort; sequence pi_digits*1+0 @1339; skip [0] (resolve)` 
  `GLDAEFACDUYOEHUSTIRPREYOUDONRRHXOEBXIINGMFGNGDIIJNYOEDFJJCSAEOEBEACFTHEOJNGWWFYWNGNIOIEDEOMHJETH`
- near_miss (program, by claude-sonnet, margin -2.05): `beaufort; sequence pi_digits*1+0 @1338; skip [0] (resolve)` 
  `XBEOUACDUYOEHUSTIRPREYOUDONRRHXOEBXIINGMFGNGDIIJNYOEDFJJCSAEOEBEACFTHEOJNGWWFYWNGNIOIEDEOMHJETH`
- near_miss (program, by claude-sonnet, margin -2.06): `add; sequence prime_totients*1+0 @31; skip [0] (resolve)` 
  `HOWHCNGEOEAGIENENPFEEDSEOCBROOPEBJNUIMLEARTHUSEXBEAYEIONFFOTJWIDTOECCNGCHEARTYOEJXUTHUAPNRUFIO`
- near_miss (program, by claude-sonnet, margin -2.06): `add; sequence primes*1+1 @1937; skip [0] (resolve)` 
  `AENGNFLWTHTHHECAPRXAYGXNGXOENLANINNOTTIPSAEFOHEOSOEEAENGNGXUEAEOOSTTHAUMAEYRONGOENFSXJIOWRIOLTOFCJ`
- near_miss (program, by claude-sonnet, margin -2.06): `beaufort; sequence prime_totients*1+0 @1013; skip [0] (resolve)` 
  `EOGINGUEAAEDLEAANGPDHEOEAEIDNIODCAENGARYSLIPOEWEOWUIAINFLAFDTHMIFYINNPSTHDAEOTHNGMDXGAENGNOEJWDPEAEOA`
- near_miss (program, by claude-sonnet, margin -2.06): `add; sequence prime_totients*1+0 @32; skip [0] (resolve)` 
  `XCBIFNGEOEAGIENENPFEEDSEOCBROOPEBJNUIMLEARTHUSEXBEAYEIONFFOTJWIDTOECCNGCHEARTYOEJXUTHUAPNRUFIO`
- near_miss (program, by claude-sonnet, margin -2.07): `add; sequence prime_totients*1+0 @219; skip [0] (resolve)` 
  `OFLNGUSTHEAETHEOAFANDTHTHWEAAEEAPTHWWMAIODMULTHCURIOYPLEATHJWBOETHYWTHDTTMCIXYYNGOICEJNGNIOTEAFCEANGFTDEW`
- near_miss (program, by claude-sonnet, margin -2.08): `sub; sequence prime_totients*1+0 @593; skip [0] (resolve)` 
  `AEGTHEOEOEAADOONFYOEHEOIOTIOXOUTWELOMCTCDEANGNGBHHEARECYGONGIOUMEANYNGEUXNGNSRXAJWNEEACNMIDAENBRLX`

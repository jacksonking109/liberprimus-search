# Swarm run

Updated 2026-11-04 10:24:51. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 21 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\codex_21 --ledger reports\overnight\20261104-0949\codex_21\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 64 call(s) in the last 5h (cap 550)
- claude-sonnet: 64 call(s) in the last 5h (cap 550)
- claude-supervisor: 64 call(s) in the last 5h (cap 550)
- codex: 24 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:56.jpg/2 | 121 | 26369 | 48 | 0 |  |

## LP2:56.jpg/2

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 0 | 26369 | 0 | 7 | 0 |

- near_miss (program, by codex, margin -0.29; chance 59: noise level (pure noise does this well that often)): `beaufort; sequence squares*1+0 @2; map reverse; skip [2] (resolve)` 
  `OSOITHWCMNGOECOTPOIDHUMOEEAJOGIOINGTHMTHCHLINGSEGNUJEMXTHTUGDPIGOEANGDGSSMRXBMJEOSMSTHGEAWJIPNGSR`
- near_miss (program, by codex, margin -0.30; chance 37: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @1674; skip [2] (resolve)` 
  `IOEAINXGOETEAIOREBEANNXYCUPWEOOELUXTHTMDPSEALGSNGFYGLMPTHISWPBTHRFGHEOIOPOHWPWOEAEJIORWTHOIOJHCOFMY`
- near_miss (program, by codex, margin -0.32; chance 90: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @630; skip [0] (resolve)` 
  `RUCLENGTHOEUNGTHNLSEAAEUAOAEONGNIODXMMEAIPOOESNGFDATNGSDUNGEONCONINWEOTHCUWXHUNGEJLLOERPULUWSBPDIAECI`
- near_miss (program, by codex, margin -0.33; chance 89: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @1675; skip [2] (resolve)` 
  `NGFJRXIMTUXTHOLJGTHHXEAEODPJEODSTHMTHIAEBEOLTHLGSNGFYGLMPTHISWPBTHRFGHEOIOPOHWPWOEAEJIORWTHOIOJHCOFMY`
- near_miss (program, by codex, margin -0.35; chance 62: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @546; skip [0] (resolve); columnar [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` 
  `EARLWMSEOAEBHEATTHEEEOMYIGULFIOMMIORBLEGEOTFPELSWEARGOEBDMARYHETHHAEFPIWAEEOAFRWFCEAONAEHLNIOAEWXNE`
- near_miss (program, by codex, margin -0.35; chance 35: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @1857; skip [0] (resolve); reverse text` 
  `AGAEMTAEITHTWIOIMAWSBUTBAIRJTHEUMTHRNGSWERWEIOAAETHPAIROTHDUTHNGIRSAESEANGDXUAEIOSMTHIOTHRLGEAIOSOOEBIE`
- near_miss (program, by codex, margin -0.35; chance 1.6e+02: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @1670; skip [2] (resolve)` 
  `DAEWHDNOELIOWFEAXPCWPNGIOJOEJCHAESUBEASMEMTUOEFLEOUOESNGNGNIORJJSBEACFNHPAEGITHSHCAEEANAIGDOIOJHCOFMY`
- near_miss (program, by codex, margin -0.35; chance 1.8e+02: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @1047; skip [2] (resolve)` 
  `AOPNTJOEAGJYTHMIWGILGHFJCIESUPTHBBNGSDEADTHDBTHAGSESTHHWRXTTHNYGIPIOWUOIPNAEAEOAEGSANEAJPREAOTM`
- near_miss (program, by codex, margin -0.36; chance 1.9e+02: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @801; skip [2] (resolve)` 
  `MUWGENIOOERPEACEJCOBMCODEOHPOELHJTHBADXDTHLEADMFAEEOANGSTHRWTHEOLTHUUCSBEAINCTHGDUTDIWUGTHWJITHOXA`
- near_miss (program, by codex, margin -0.36; chance 2.1e+02: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @1046; skip [2] (resolve)` 
  `ATHPJMHDMWSFEABTIOIPTOEOYMCGLSUPABBNGSDEADTHDBTHAGSESTHHWRXTTHNYGIPIOWUOIPNAEAEOAEGSANEAJPREAOTM`

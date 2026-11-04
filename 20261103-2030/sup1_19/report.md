# Swarm run

Updated 2026-11-03 23:05:39. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 19 --generators codex,qwen-local,gemma-local --rounds 4 --per-round 4 --report-dir reports\overnight\20261103-2030\sup1_19 --ledger reports\overnight\20261103-2030\sup1_19\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 65 call(s) in the last 5h (cap 120)
- claude-sonnet: 65 call(s) in the last 5h (cap 120)
- claude-supervisor: 65 call(s) in the last 5h (cap 200)
- codex: 38 call(s) in the last 5h (cap 100)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:33.jpg - 50.jpg/1 | 91 | 16512 | 59 | 0 |  |

## LP2:33.jpg - 50.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 1 | 16454 | 0 | 2 | 0 |
| qwen-local | 16 | 3 | 43 | 0 | 0 | 0 |
| gemma-local | 16 | 1 | 15 | 0 | 0 | 0 |

- near_miss (program, by codex, margin -2.04): `sub; sequence primes*1+0 @851; skip [0] (resolve)` 
  `AEAEMIOFXEOEBOOOFATEEROEGTHLGXYETASCEBGWIOMGWAETHOENREALFYIOGAEEOMNGNIOAWLTRNGTEANRMSITALWIONSYCNGHO`
- near_miss (program, by codex, margin -2.07): `sub; sequence primes*1+0 @1605; skip [0] (resolve)` 
  `EOEEOEJPNGBIOSMDFPPPWUDNDNGBAEXMMHADNGOESHFADEASAJXWEEDFAETNMASITEOTDEADXAWJAIOFNGAEXGJBEUBAES`
- near_miss (program, by codex, margin -2.09): `sub; sequence primes*1+0 @1606; skip [0] (resolve)` 
  `RTTHTFPNGBIOSMDFPPPWUDNDNGBAEXMMHADNGOESHFADEASAJXWEEDFAETNMASITEOTDEADXAWJAIOFNGAEXGJBEUBAES`
- near_miss (program, by codex, margin -2.11): `sub; sequence primes*1+0 @1477; skip [0] (resolve); columnar [6, 5, 4, 3, 2, 1, 0]` 
  `SEAIOXOWTHJUDCDULLLAWEAJUJSRTHOEAEMEOIOEACINGFIOLOCMYEATHEYITDOEFEAROSEOUTHMAEPBXDWTUFNGAAEMOEGTUNGFACO`
- near_miss (program, by codex, margin -2.12): `sub; sequence primes*1+0 @1567; skip [0] (resolve)` 
  `EOAOEEOFSMMEOFIOPFULLEORUTHXFHEGIEOEFUIOANEWILTOGYSOICAEMWIOOPCIOANYOAXNTHXOEOETNGSIOIOFHNGGNGBGAX`
- near_miss (program, by codex, margin -2.12): `sub; sequence primes*1+0 @850; skip [0] (resolve)` 
  `FXIOIFOEAAMSNPIATEEROEGTHLGXYETASCEBGWIOMGWAETHOENREALFYIOGAEEOMNGNIOAWLTRNGTEANRMSITALWIONSYCNGHO`
- near_miss (program, by codex, margin -2.12): `sub; sequence primes*1+0 @488; skip [0] (resolve); columnar [6, 5, 4, 3, 2, 1, 0]` 
  `NGCHOEPNGOERTHLTEARAENGPMRFTTHEOGEAOAELLMEAAEEOSYFTNTHEOLFGEATHRBAEMEMARTUROWOEOTLONGYOESEFNIBOEEXYWHUCOE`
- near_miss (program, by codex, margin -2.12): `sub; sequence primes*1+0 @849; skip [0] (resolve)` 
  `GETECOEAAMSNPIATEEROEGTHLGXYETASCEBGWIOMGWAETHOENREALFYIOGAEEOMNGNIOAWLTRNGTEANRMSITALWIONSYCNGHO`
- near_miss (program, by codex, margin -2.12): `sub; sequence primes*1+0 @1544; skip [0] (resolve)` 
  `PAEDAEFEANMAEMMDFORTHRDXAEAEEOGEOYXTJCATHYDLNHUGEAABEADFNHWTHFHYBNGNFOJEAAHIYCWDBSEOOEEAOWNTUXAPTHS`
- near_miss (program, by codex, margin -2.12): `sub; sequence primes*1+0 @773; skip [0] (resolve)` 
  `THEREFOPPFEAEAEFHNGBBNGNDHFHLTHTHLPAREADGULJOESBAEODOEXDXNFMTHWSONGAUOEEALYNGGXTEFJNMNGTHDOUTEANAEM`

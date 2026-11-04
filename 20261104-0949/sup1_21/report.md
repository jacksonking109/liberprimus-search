# Swarm run

Updated 2026-11-04 13:18:11. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 21 --generators claude-opus --rounds 4 --per-round 6 --report-dir reports\overnight\20261104-0949\sup1_21 --ledger reports\overnight\20261104-0949\sup1_21\ledger.sqlite --brief-file reports\overnight\20261104-0949\sup1_21\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 202 call(s) in the last 5h (cap 550)
- claude-sonnet: 202 call(s) in the last 5h (cap 550)
- claude-supervisor: 202 call(s) in the last 5h (cap 550)
- codex: 81 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:56.jpg/2 | 121 | 2652 | 24 | 0 |  |

## LP2:56.jpg/2

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus | 24 | 0 | 2652 | 0 | 3 | 0 |

- near_miss (program, by claude-opus, margin -0.18; chance 3.7: noise level (pure noise does this well that often)): `add; sequence prime_totients*3+5 @101; skip [27] (resolve)` 
  `EXPBTNIOWHDUNGMOEBNGCDAMXJBWEOILRIXEOOEPCAEENHWAEFSUXPIOMHNYSHNGFJAEAEIPOEIGLATHYCWYJTUYJTHIOUTHNGT`
- near_miss (program, by claude-opus, margin -0.22; chance 2.6: noise level (pure noise does this well that often)): `beaufort; sequence prime_totients*2+1 @260; map reverse; skip [27] (resolve)` 
  `EREGALIOLIOJLNWTTYTUBEIOEOOEYGSNAESCCIOGNGWNLIDBTHEATNGOEOEPINCNIFLRXDIOUTHRSEAEANGEENJNGLSPAEGBBNGPG`
- near_miss (program, by claude-opus, margin -0.23; chance 3.4: noise level (pure noise does this well that often)): `beaufort; sequence prime_totients*2+1 @261; map reverse; skip [27] (resolve)` 
  `IOREGALIOLIOJLNWTTYTUBEIOEOOEYGSNAESCCIOGNGWNLIDBTHEATNGOEOEPINCNIFLRXDIOUTHRSEAEANGEENJNGLSPAEGBBNGPG`
- near_miss (program, by claude-opus, margin -0.26; chance 21: noise level (pure noise does this well that often)): `add; sequence prime_totients*3+5 @485; skip [27] (resolve)` 
  `MONGXTHEOAEEADNGTWDYNGAENTEOWHTCADIONGSXEOOEPBLWRIOXTHUEALIEAEIOBAGEOGAETNGGFMIAEUSEAOEMOOEEMIOFOBHOEHSCF`
- near_miss (program, by claude-opus, margin -0.26; chance 7.9: noise level (pure noise does this well that often)): `beaufort; sequence prime_totients*2+1 @437; map reverse; skip [27] (resolve)` 
  `IOHUDEOTIIOXYNMNUUEOXOTHTNGYAREIDIRTHDFHSEAIOBGNGOEJDWJIOOEWGMEAAENUDOASTIOAEUBYWJDEEAIOOEFLAESTAWAE`
- near_miss (program, by claude-opus, margin -0.27; chance 18: noise level (pure noise does this well that often)): `beaufort; sequence primes*3+7 @391; map reverse; skip [7] (resolve)` 
  `DMACNGTHSEWJAWACDRBEOWMIOUWYTHBSDFTXUNGAEJOEPBRNGTWBPESGWNOSHRTHEOLSMIPMSEAIOCGTHIUNHOEAFHNGWWLS`
- near_miss (program, by claude-opus, margin -0.28; chance 27: noise level (pure noise does this well that often)): `beaufort; sequence primes*3+7 @43; map reverse; skip [7] (resolve)` 
  `CAJTRHYGWTJWFSWALOROEBHSEASADAWEALWIOMTYDRXLMILIONCTHOINGNYEAWJAEMIABCPOPHOBMLEARUHOETHIOWWXO`
- near_miss (program, by claude-opus, margin -0.28; chance 26: noise level (pure noise does this well that often)): `beaufort; sequence primes*3+7 @144; map reverse; skip [7] (resolve)` 
  `EAWUJIOTHIOWWCGIHFETGUTHNGOEUPNHEOIJEASUBXDOWRSAEPDYALTHRLOEAEACRFLWNGSBTHBDTHEAYIOOEEOXNBTTHOFBUTWAY`
- near_miss (program, by claude-opus, margin -0.28; chance 28: noise level (pure noise does this well that often)): `beaufort; sequence primes*3+7 @88; map reverse; skip [7] (resolve)` 
  `YIOHPBARWXIWRYWGXNIOEFLOOENAEADJRXEYESMCOMAEARXINGDXSEATTNFYPNGIOBHJJTHSPXRFMXEBLTMRBOTEOW`
- near_miss (program, by claude-opus, margin -0.29; chance 18: noise level (pure noise does this well that often)): `beaufort; sequence prime_totients*2+1 @87; map reverse; skip [27] (resolve)` 
  `IOLNJFTIOEOOEAAEILNGTTHFEPDACJANETWOEOOCNASBLXAOEJEOEOFCUBIBUOEJBRHXIIOXSCJLTIOMTHDILECTSRWTEAJAE`

# Swarm run

Updated 2026-11-04 10:43:13. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 19 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\codex_19 --ledger reports\overnight\20261104-0949\codex_19\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 80 call(s) in the last 5h (cap 550)
- claude-sonnet: 80 call(s) in the last 5h (cap 550)
- claude-supervisor: 80 call(s) in the last 5h (cap 550)
- codex: 36 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:33.jpg - 50.jpg/1 | 91 (short) | 30254 | 47 | 0 |  |

## LP2:33.jpg - 50.jpg/1

**Caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution.**

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 1 | 30254 | 0 | 8 | 0 |

- near_miss (program, by codex, margin -2.00; chance 44: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @1605; skip [0, 7] (resolve)` 
  `EOEEOEJPNGBIOSMDFPPPWUDNDNGBAEXMMHADNGOESHFADEASAJXWEEDFAETNMASITEOTWGFEUNGSSHXXTHTWDIOWONGIW`
- near_miss (program, by codex, margin -2.00; chance 45: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @1607; skip [0, 7] (resolve)` 
  `IOFAEHFWCWIOSMDFPPPWUDNDNGBAEXMMHADNGOESHFADEASAJXWEEDFAETNMASITEOTWGFEUNGSSHXXTHTWDIOWONGIW`
- near_miss (program, by codex, margin -2.02; chance 55: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @1606; skip [0, 7] (resolve)` 
  `RTTHTFPNGBIOSMDFPPPWUDNDNGBAEXMMHADNGOESHFADEASAJXWEEDFAETNMASITEOTWGFEUNGSSHXXTHTWDIOWONGIW`
- near_miss (program, by codex, margin -2.02; chance 27: noise level (pure noise does this well that often)): `add; sequence e_digits*1+0 @669; skip [7] (resolve); reverse text` 
  `FSJUDJYWJUMXTACXUIAEIONEAPABTWOTOEAWEINBSJAINGONEHJOERTHAEJTTHNAEAETHCIOMHEAUWNRTHTURNDRUGAEYNGHTH`
- near_miss (program, by codex, margin -2.06; chance 50: noise level (pure noise does this well that often)): `add; sequence e_digits*1+0 @668; skip [7] (resolve); reverse text` 
  `NGLIULEOEEOJUMXTACXUIAEIONEAPABTWOTOEAWEINBSJAINGONEHJOERTHAEJTTHNAEAETHCIOMHEAUWNRTHTURNDRUGAEYNGHTH`
- near_miss (program, by codex, margin -2.06; chance 1.1e+02: noise level (pure noise does this well that often)): `sub; sequence prime_totients*28+0 @31; skip [0] (resolve)` 
  `HOWHCNGEOEAGIENENPFEEDSEOCBROOPEBJNUIMLEARTHUSEXBEAYEIONFFOTJWIDTOECCNGCHEARTYOEJXUTHUAPNRUFIO`
- near_miss (program, by codex, margin -2.06; chance 1.2e+02: noise level (pure noise does this well that often)): `sub; sequence prime_totients*28+0 @32; skip [0] (resolve)` 
  `XCBIFNGEOEAGIENENPFEEDSEOCBROOPEBJNUIMLEARTHUSEXBEAYEIONFFOTJWIDTOECCNGCHEARTYOEJXUTHUAPNRUFIO`
- near_miss (program, by codex, margin -2.07; chance 63: noise level (pure noise does this well that often)): `add; sequence e_digits*1+0 @673; skip [7] (resolve); reverse text` 
  `EAEOJEASJEAWPWAEWEOAEUMAWOEFHAEBRMHFRLLEAWEWRAWJAINGONEHJOERTHAEJTTHNAEAETHCIOMHEAUWNRTHTURNDRUGAEYNGHTH`
- near_miss (program, by codex, margin -2.07; chance 1.4e+02: noise level (pure noise does this well that often)): `sub; sequence prime_totients*28+0 @219; skip [0] (resolve)` 
  `OFLNGUSTHEAETHEOAFANDTHTHWEAAEEAPTHWWMAIODMULTHCURIOYPLEATHJWBOETHYWTHDTTMCIXYYNGOICEJNGNIOTEAFCEANGFTDEW`
- near_miss (program, by codex, margin -2.07; chance 1.3e+02: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @300; skip [0, 7] (resolve)` 
  `THTTOFFHINYEEMDDDIOPRMDEOHXCEEEAEATIOYSLPEAJYMNGEODTNUDEDTHAEEONBWTHCBNCYOMILCWNTEATHEOWOTEAPPW`

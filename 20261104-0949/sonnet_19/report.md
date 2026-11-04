# Swarm run

Updated 2026-11-04 11:29:25. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 19 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\sonnet_19 --ledger reports\overnight\20261104-0949\sonnet_19\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261104-0949\sonnet_19\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 116 call(s) in the last 5h (cap 550)
- claude-sonnet: 116 call(s) in the last 5h (cap 550)
- claude-supervisor: 116 call(s) in the last 5h (cap 550)
- codex: 57 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:33.jpg - 50.jpg/1 | 91 (short) | 8899 | 22 | 0 |  |

## LP2:33.jpg - 50.jpg/1

**Caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution.**

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 41 | 17 | 8899 | 0 | 3 | 0 |

- near_miss (program, by claude-sonnet, margin -1.96; chance 8: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @636; map reverse; skip [0] (resolve)` 
  `ISNFFTWLBSOLUIDETHFXEOSXFBLLREADFHTCNGLLMNGOEAETLCAEAEIOAJLTAWHICSLIPJYNGTHOFMEANTBYNGAGPBYIOEAEA`
- near_miss (program, by claude-sonnet, margin -1.98; chance 9.6: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @635; map reverse; skip [0] (resolve)` 
  `EONGPECTWLBSOLUIDETHFXEOSXFBLLREADFHTCNGLLMNGOEAETLCAEAEIOAJLTAWHICSLIPJYNGTHOFMEANTBYNGAGPBYIOEAEA`
- near_miss (program, by claude-sonnet, margin -2.04; chance 26: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @637; map reverse; skip [0] (resolve)` 
  `RJLNGFNGOEPNUHFIDETHFXEOSXFBLLREADFHTCNGLLMNGOEAETLCAEAEIOAJLTAWHICSLIPJYNGTHOFMEANTBYNGAGPBYIOEAEA`
- near_miss (program, by claude-sonnet, margin -2.05; chance 30: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @82; map reverse; skip [0] (resolve)` 
  `IMJTSYHDEHDNFWULTHREOEBLEOFUYEOWIEOEWFIOWRIWASDLWONIOEOFDANTTSIOWAGAEJFOEOPAGEFJTNGYCIORJINN`
- near_miss (program, by claude-sonnet, margin -2.06; chance 32: noise level (pure noise does this well that often)): `add; sequence prime_totients*1+0 @31; skip [0] (resolve)` 
  `HOWHCNGEOEAGIENENPFEEDSEOCBROOPEBJNUIMLEARTHUSEXBEAYEIONFFOTJWIDTOECCNGCHEARTYOEJXUTHUAPNRUFIO`
- near_miss (program, by claude-sonnet, margin -2.06; chance 33: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @83; map reverse; skip [0] (resolve)` 
  `HPWIFYHDEHDNFWULTHREOEBLEOFUYEOWIEOEWFIOWRIWASDLWONIOEOFDANTTSIOWAGAEJFOEOPAGEFJTNGYCIORJINN`
- near_miss (program, by claude-sonnet, margin -2.06; chance 35: noise level (pure noise does this well that often)): `add; sequence prime_totients*1+0 @32; skip [0] (resolve)` 
  `XCBIFNGEOEAGIENENPFEEDSEOCBROOPEBJNUIMLEARTHUSEXBEAYEIONFFOTJWIDTOECCNGCHEARTYOEJXUTHUAPNRUFIO`
- near_miss (program, by claude-sonnet, margin -2.07; chance 40: noise level (pure noise does this well that often)): `add; sequence prime_totients*1+0 @219; skip [0] (resolve)` 
  `OFLNGUSTHEAETHEOAFANDTHTHWEAAEEAPTHWWMAIODMULTHCURIOYPLEATHJWBOETHYWTHDTTMCIXYYNGOICEJNGNIOTEAFCEANGFTDEW`
- near_miss (program, by claude-sonnet, margin -2.08; chance 43: noise level (pure noise does this well that often)): `beaufort; sequence prime_totients*1+0 @28; map reverse; skip [0] (resolve)` 
  `TNAELNGREAPLACNGFNGAEIEEDDYNGAEINCDEAFIOBUIMYCHIOEADYADOOYRBGIJYMDOEEOUCBNGEOBXCXUNUNGEOCIONOFAETNHX`
- near_miss (program, by claude-sonnet, margin -2.08; chance 46: noise level (pure noise does this well that often)): `add; sequence prime_totients*1+0 @33; skip [0] (resolve)` 
  `TSMTFIOTCEOEOEAJFNPFEEDSEOCBROOPEBJNUIMLEARTHUSEXBEAYEIONFFOTJWIDTOECCNGCHEARTYOEJXUTHUAPNRUFIO`

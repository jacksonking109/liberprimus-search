# Swarm run

Updated 2026-11-04 09:56:11. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 25 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\codex_25 --ledger reports\overnight\20261104-0949\codex_25\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 15 call(s) in the last 5h (cap 550)
- claude-sonnet: 15 call(s) in the last 5h (cap 550)
- claude-supervisor: 15 call(s) in the last 5h (cap 550)
- codex: 6 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:54.jpg-55.jpg - 71.jpg-72.jpg | 308 | 30269 | 47 | 0 |  |

## LP2:54.jpg-55.jpg - 71.jpg-72.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 0 | 30269 | 0 | 6 | 0 |

- near_miss (program, by codex, margin -0.23; chance 2.6e+02: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @1886; skip [0] (resolve)` 
  `RIHAEDEAOERWCEGHCINGEOOCBPNGOEIOFTNGGHMDIOERLOERTPTHNGFJOFOEWEOOILEOIONHSANGWNGOETHYDAEFIXTFAEPPEOBNGEIPA`
- near_miss (program, by codex, margin -0.25; chance 1.1e+02: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @141; skip [0, 28] (resolve)` 
  `ATEMAEOENHPIOERTARAEOPTLEFACWTHHIOTNOETHDMOESUPRAFANGHOTHRDSRFDODBRTHNGXOEGOIEFTTHWFAREEAWLEAHSF`
- near_miss (program, by codex, margin -0.26; chance 2.4e+02: noise level (pure noise does this well that often)): `sub; sequence primes*2+1 @460; skip [0] (resolve)` 
  `UUCOATTRUCGBUGNGCYMANIOCXSMRTHJSHHIOLEAWBEAOETHIOOAETHWIYCIOOIDOETJEAEHSEONIAEOEOEFCTXNGTLTENGIOOEAEYD`
- near_miss (program, by codex, margin -0.26; chance 1.6e+02: noise level (pure noise does this well that often)): `add; sequence primes*1+0 @954; skip [0] (resolve)` 
  `NGLEAOBDEERETEUAMJEOFEOBDHEOAEEBDOGIOEODAGODFYANGNGLNGXGPEOIOMNGIYBIGTHIDIONGPOGMTHLNGHNPNGREAEOEOOLOXTH`
- near_miss (program, by codex, margin -0.27; chance 1.5e+02: noise level (pure noise does this well that often)): `add; sequence prime_totients*1+0 @191; map reverse; skip [28] (resolve)` 
  `GMIOTHRHHTPJBRHNNGGSAEIOTHDTHCEAEOSYEOONNYXAESIONGEODRMOUMYIWTHATAEACSTHAFIUGYTHAAOEFAEFUCUTIOAMFOEM`
- near_miss (program, by codex, margin -0.27; chance 2.4e+02: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @63; skip [0, 28] (resolve)` 
  `BEOMMIOAHRTIOLHEAEOBXWLTXUAEAPWOYLJLCYPGOEJEAXFEAFLAPTHUTHEASONEATHEAPADEAPSGUPLFNGFTHAYNEEAITOOIEA`
- near_miss (program, by codex, margin -0.28; chance 2.7e+02: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @138; skip [0, 28] (resolve)` 
  `OEINGDAEAIHIOENGWNGAEIOMPPAXEDYRPCHYMJEYEATGSEAEIRUYDOEXTHDOEAJFGIOAEDTEATHUPXWWTTOENGYHYTHOLMWLEAHSF`
- near_miss (program, by codex, margin -0.28; chance 2.4e+02: noise level (pure noise does this well that often)): `add; sequence prime_totients*1+0 @1483; map reverse; skip [28] (resolve)` 
  `ARTLOCUNGRTOCHROERDDONJAEETEOXAEJFFHMNEAOEBWHDTFJBXNGWIEASGGOEACNGHPROFAFYYWXHRNJNEAEAUNGEOXJI`
- near_miss (program, by codex, margin -0.29; chance 3.3e+02: noise level (pure noise does this well that often)): `add; sequence prime_totients*1+0 @1482; map reverse; skip [28] (resolve)` 
  `EOFTHXTEAOECFIOHYAAETHTIOWSYOEASTIDIMCDBMJOEXEAODBIOMOWTHMUIOOESGGOEACNGHPROFAFYYWXHRNJNEAEAUNGEOXJI`
- near_miss (program, by codex, margin -0.30; chance 3.2e+02: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @467; skip [0, 28] (resolve)` 
  `WAEAESSWBOITHAEEAUMNENRHOIEOAEEAYBSROERGXEACDIOWSANYBHAEEANGHOXFHTHPPUIOWRNGLAEOSOETIUNCIHHGOHTIODUTH`

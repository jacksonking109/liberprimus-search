# Swarm run

Updated 2026-11-03 23:15:40. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 25 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\codex_25 --ledger reports\overnight\20261103-2310\codex_25\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 78 call(s) in the last 5h (cap 120)
- claude-sonnet: 78 call(s) in the last 5h (cap 550)
- claude-supervisor: 78 call(s) in the last 5h (cap 200)
- codex: 45 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:54.jpg-55.jpg - 71.jpg-72.jpg | 308 | 29964 | 47 | 0 |  |

## LP2:54.jpg-55.jpg - 71.jpg-72.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 1 | 29964 | 0 | 5 | 0 |

- near_miss (program, by codex, margin -0.23): `sub; sequence primes*1+0 @1886; skip [0] (resolve)` 
  `RIHAEDEAOERWCEGHCINGEOOCBPNGOEIOFTNGGHMDIOERLOERTPTHNGFJOFOEWEOOILEOIONHSANGWNGOETHYDAEFIXTFAEPPEOBNGEIPA`
- near_miss (program, by codex, margin -0.25): `add; sequence primes*1+0 @954; skip [0] (resolve)` 
  `NGLEAOBDEERETEUAMJEOFEOBDHEOAEEBDOGIOEODAGODFYANGNGLNGXGPEOIOMNGIYBIGTHIDIONGPOGMTHLNGHNPNGREAEOEOOLOXTH`
- near_miss (program, by codex, margin -0.27): `sub; sequence pi_digits*1+0 @593; skip [28] (resolve)` 
  `EIBDOEUJHMIODHSOEGOEEOSLTMAEATHNHTHOEGBUAEEONNGXUNTHAEOEENGIJOEIEAJTHOEATHEAJOAEOEWNGGRJPAELCTHUTHNAEEAGJUCPIO`
- near_miss (program, by codex, margin -0.29): `beaufort; sequence prime_totients*1+0 @134; map reverse; skip [28] (resolve)` 
  `THCJIOEOEAPMUPJJRBAEBYIOHNFXEHANGFUGIOTOHUROEOENOAEIOCREGWTFEANFIGLLTAAERAESCEOFTEAFTALCDEATHBRNGFPEA`
- near_miss (program, by codex, margin -0.30): `sub; sequence primes*1+0 @467; skip [0, 28] (resolve)` 
  `WAEAESSWBOITHAEEAUMNENRHOIEOAEEAYBSROERGXEACDIOWSANYBHAEEANGHOXFHTHPPUIOWRNGLAEOSOETIUNCIHHGOHTIODUTH`

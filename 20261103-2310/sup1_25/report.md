# Swarm run

Updated 2026-11-04 02:24:48. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 25 --generators claude-sonnet,codex --rounds 6 --per-round 8 --report-dir reports\overnight\20261103-2310\sup1_25 --ledger reports\overnight\20261103-2310\sup1_25\ledger.sqlite --brief-file reports\overnight\20261103-2310\sup1_25\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 193 call(s) in the last 5h (cap 120), paused until 2026-11-04 04:25 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 193 call(s) in the last 5h (cap 550)
- claude-supervisor: 193 call(s) in the last 5h (cap 200)
- codex: 128 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:54.jpg-55.jpg - 71.jpg-72.jpg | 308 | 5713 | 73 | 0 |  |

## LP2:54.jpg-55.jpg - 71.jpg-72.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 48 | 8 | 2473 | 0 | 3 | 0 |
| codex | 48 | 0 | 3240 | 0 | 4 | 0 |

- near_miss (program, by codex, margin -0.17): `sub; sequence primes*1+0 @1886; skip [0] (resolve)` 
  `RIHAEDEAOERWCEGHCINGEOOCBPNGOEIOFTNGGHMDIOERLOERTPTHNGFJOFOEWEOOILEOIONHSANGWNGOETHYDAEFIXTFAEPPEOBNGEIPA`
- near_miss (program, by claude-sonnet, margin -0.18): `sub; sequence pi_digits*1+0 @593; skip [28] (resolve)` 
  `EIBDOEUJHMIODHSOEGOEEOSLTMAEATHNHTHOEGBUAEEONNGXUNTHAEOEENGIJOEIEAJTHOEATHEAJOAEOEWNGGRJPAELCTHUTHNAEEAGJUCPIO`
- near_miss (program, by claude-sonnet, margin -0.19): `add; sequence primes*1+0 @954; skip [0] (resolve)` 
  `NGLEAOBDEERETEUAMJEOFEOBDHEOAEEBDOGIOEODAGODFYANGNGLNGXGPEOIOMNGIYBIGTHIDIONGPOGMTHLNGHNPNGREAEOEOOLOXTH`
- near_miss (program, by claude-sonnet, margin -0.20): `beaufort; sequence prime_totients*1+0 @134; map reverse; skip [28] (resolve)` 
  `THCJIOEOEAPMUPJJRBAEBYIOHNFXEHANGFUGIOTOHUROEOENOAEIOCREGWTFEANFIGLLTAAERAESCEOFTEAFTALCDEATHBRNGFPEA`
- near_miss (program, by codex, margin -0.23): `sub; sequence primes*1+0 @1888; skip [0, 23] (resolve)` 
  `JNGBDAIHIOYOEDGHCINGEOOCBPNGOEIOFTNGGHMDIOERLOERTPTHNGFJOFOEWEOOILEOIONHSANGWNGDGOGIORIXTFAEPPEOBNGEIPA`
- near_miss (program, by codex, margin -0.24): `sub; sequence primes*1+0 @1888; skip [0, 2] (resolve)` 
  `JNGBLGTHHIOYOETFAERRBGYLPJTHOEIOFTNGGHMDIOERLOERTPTHNGFJOFOETHTFOEYATHROIOUDMLUGOGIORIXTFAEPPEOBNGEIPA`
- near_miss (program, by codex, margin -0.25): `beaufort; sequence prime_totients*1+0 @135; map reverse; skip [0, 28] (resolve)` 
  `INAEHAUDNGCSNGAEHMFTHUFEOFROEEATEAIOGSIROEJXPHEAAMCTHHFREGWTFEANFIGLLTAAERAESCEOFTEAFTALCDEATHBRNGFPEA`
- near_miss (program, by codex, margin -0.25): `sub; sequence primes*1+0 @1884; skip [0, 23] (resolve)` 
  `EOUUXXRIWIONGJLTDDEAOEPBHTHIOMYIEAAPWXHEOUJAENEAUTHLFASSEAPTFOEYATHROIOUDMLUGOGIORIXTFAEPPEOBNGEIPA`
- near_miss (program, by codex, margin -0.25): `sub; sequence primes*1+0 @1884; skip [0, 2] (resolve)` 
  `EOUUXXRIWIONGJLTDDEAOEPBHTHIOMYIEAAPWXHEOUJAENEAUTHLFASSEAPTFOEYATHROIOUDMLUGOGIORIXTFAEPPEOBNGEIPA`
- near_miss (program, by codex, margin -0.27): `sub; sequence primes*1+0 @1885; skip [0, 23] (resolve)` 
  `GEAEOIFIOJEPSUHXBJIOTNJTHBDBTHGOEETYAETHRACACTEFRIOFSSEAPTFOEYATHROIOUDMLUGOGIORIXTFAEPPEOBNGEIPA`

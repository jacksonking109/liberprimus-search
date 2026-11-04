# Swarm run

Updated 2026-11-04 02:11:45. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 21 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\sonnet_21 --ledger reports\overnight\20261103-2310\sonnet_21\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261103-2310\sonnet_21\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 165 call(s) in the last 5h (cap 120), paused until 2026-11-04 04:18 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 165 call(s) in the last 5h (cap 550)
- claude-supervisor: 165 call(s) in the last 5h (cap 200)
- codex: 122 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:56.jpg/2 | 121 | 31565 | 39 | 0 |  |

## LP2:56.jpg/2

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 48 | 9 | 31565 | 0 | 6 | 0 |

- near_miss (program, by claude-sonnet, margin -0.24): `sub; sequence prime_totients*1+0 @1353; map reverse; skip [0] (resolve)` 
  `DEOJYMDOFPNGYTENSHOEDNTPPPFWAERBSAERFTHOEHFSNGUBLIOEOWDGSXEAMGSGDEOIOINGJICSHIPUPIONEONGOEBOASXHEI`
- near_miss (program, by claude-sonnet, margin -0.29): `sub; sequence prime_totients*1+0 @1352; map reverse; skip [0] (resolve)` 
  `AETTHPTIOJGBROAUNGNGEOUTJOIODMEOMIINGGFTGREAXISNGUBLIOEOWDGSXEAMGSGDEOIOINGJICSHIPUPIONEONGOEBOASXHEI`
- near_miss (program, by claude-sonnet, margin -0.32): `sub; sequence prime_totients*1+0 @408; skip [0] (resolve)` 
  `NFAEMDWPGFUNCXOIUDAETHTHENUNGDTBAEEATHCLEONYFOEGBTHAEHCFEMNGMIWMIOUANGAIOCWIOOEDOETHTINGACLCYSOECIOAECN`
- near_miss (program, by claude-sonnet, margin -0.38): `sub; sequence prime_totients*1+0 @403; skip [0] (resolve)` 
  `GUNUWYOECPTYOEREONGXSSMSNGYTJSIYWHSLRAELTHRSWIOSIOLAPALLJROCHAEEOEOPALESTJYJJOEDTHNGGRYEEYBYDNG`
- near_miss (program, by claude-sonnet, margin -0.38): `sub; sequence primes*1+0 @1857; skip [0] (resolve); reverse text` 
  `AGAEMTAEITHTWIOIMAWSBUTBAIRJTHEUMTHRNGSWERWEIOAAETHPAIROTHDUTHNGIRSAESEANGDXUAEIOSMTHIOTHRLGEAIOSOOEBIE`
- near_miss (program, by claude-sonnet, margin -0.38): `sub; sequence prime_totients*1+0 @1098; skip [0] (resolve)` 
  `DLALLFIOAIOSJOEJENIXIOTHXFNGGREAHIPRUOEFYUXTIOPTHISILIODIOGLNGFYRCODONFGWDNNGBAGHHLYEACONGEOFWEA`
- near_miss (program, by claude-sonnet, margin -0.38): `sub; sequence prime_totients*1+0 @353; skip [0] (resolve)` 
  `DAUOELGEOAOGEOGSHEAPIHTTOTBGXATHININCYNGDFDCUHFGJIYFGTHEMIICEATHFOFDTNHOLLENGEACEACUJSJFAAEWO`
- near_miss (program, by claude-sonnet, margin -0.38): `sub; sequence prime_totients*1+0 @862; skip [0] (resolve)` 
  `WREORRJMNGTHAJOTOFEARGIFEOAEBGFEFGTFEAAXPSFSOEXNGWSTCDOEEXXPGISEMOIOCEANGEMIDGHSIOAEBTHIOEOERYCICC`
- near_miss (program, by claude-sonnet, margin -0.39): `sub; sequence pi_digits*1+0 @792; map reverse; skip [0] (resolve)` 
  `ADRNTHEOOEEAEOWDMTHCTNWFBPDTHCPAOLGLWFEAGODFLYCLAIFEAREPEOXWCLEXJJGSWBEOJJEUAJAXIMILWGPMPFAE`
- near_miss (program, by claude-sonnet, margin -0.40): `sub; sequence primes*1+0 @1858; skip [0] (resolve); reverse text` 
  `THDDUGMPWEOCDHSIONJOEFCOEYFNIOFUMTHRNGSWERWEIOAAETHPAIROTHDUTHNGIRSAESEANGDXUAEIOSMTHIOTHRLGEAIOSOOEBIE`

# Swarm run

Updated 2026-11-04 11:40:32. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 21 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\sonnet_21 --ledger reports\overnight\20261104-0949\sonnet_21\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261104-0949\sonnet_21\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 128 call(s) in the last 5h (cap 550)
- claude-sonnet: 128 call(s) in the last 5h (cap 550)
- claude-supervisor: 128 call(s) in the last 5h (cap 550)
- codex: 69 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:56.jpg/2 | 121 | 6575 | 16 | 0 | stop_file |

## LP2:56.jpg/2

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 24 | 6 | 6575 | 0 | 5 | 0 |

- near_miss (program, by claude-sonnet, margin -0.21; chance 13: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @408; skip [0] (resolve)` 
  `NFAEMDWPGFUNCXOIUDAETHTHENUNGDTBAEEATHCLEONYFOEGBTHAEHCFEMNGMIWMIOUANGAIOCWIOOEDOETHTINGACLCYSOECIOAECN`
- near_miss (program, by claude-sonnet, margin -0.26; chance 46: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @403; skip [0] (resolve)` 
  `GUNUWYOECPTYOEREONGXSSMSNGYTJSIYWHSLRAELTHRSWIOSIOLAPALLJROCHAEEOEOPALESTJYJJOEDTHNGGRYEEYBYDNG`
- near_miss (program, by claude-sonnet, margin -0.27; chance 53: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @353; skip [0] (resolve)` 
  `DAUOELGEOAOGEOGSHEAPIHTTOTBGXATHININCYNGDFDCUHFGJIYFGTHEMIICEATHFOFDTNHOLLENGEACEACUJSJFAAEWO`
- near_miss (program, by claude-sonnet, margin -0.30; chance 50: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @862; skip [0] (resolve)` 
  `WREORRJMNGTHAJOTOFEARGIFEOAEBGFEFGTFEAAXPSFSOEXNGWSTCDOEEXXPGISEMOIOCEANGEMIDGHSIOAEBTHIOEOERYCICC`
- near_miss (program, by claude-sonnet, margin -0.31; chance 34: noise level (pure noise does this well that often)): `beaufort; sequence prime_totients*1+0 @564; map reverse; skip [0] (resolve)` 
  `HIOAANWRCMBUPCRTHWAOAEHEAEAAGOEIOXWLTRHXGLUNGNAEPSGNGJGFOECRJLAECPEABULCLGSLENNGJCDHWRUSNGCICOEU`
- near_miss (program, by claude-sonnet, margin -0.32; chance 59: noise level (pure noise does this well that often)): `beaufort; sequence prime_totients*1+0 @82; map reverse; skip [0] (resolve)` 
  `DOMNGHHADITHEACEAFDNEPTHEPNCEOOGIOEOFNGCCPYWFBNPYWAEJLDSREMUIEAEOEOFGAEMINEIOOYAETRMGOEPDOENGIOUHTRT`
- near_miss (program, by claude-sonnet, margin -0.34; chance 37: noise level (pure noise does this well that often)): `add; sequence prime_totients*1+0 @321; skip [0] (resolve)` 
  `BEAJMHEAEYSOHEOTHWJTIOEOUPGHRIOXPCNGNNAYARTFEAYUEUMCEMNNGAHDWNGCOEPUTJTMNAYBIOMNIOROECGOEEAAEEANAJ`
- near_miss (program, by claude-sonnet, margin -0.34; chance 46: noise level (pure noise does this well that often)): `sub; sequence fibonacci*1+0 @4; skip [0] (resolve)` 
  `OEYTHNGEEAEAEGTRGLTTHTHRTHUSEANGPSANGGBYNPOSYFFNOENGTHFPNGLIEEJXXOEUNRPXEFCYBJLWEAOBFEOPEACYFDCICNGAE`
- near_miss (program, by claude-sonnet, margin -0.34; chance 22: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @630; skip [0] (resolve)` 
  `RUCLENGTHOEUNGTHNLSEAAEUAOAEONGNIODXMMEAIPOOESNGFDATNGSDUNGEONCONINWEOTHCUWXHUNGEJLLOERPULUWSBPDIAECI`
- near_miss (program, by claude-sonnet, margin -0.35; chance 46: noise level (pure noise does this well that often)): `add; sequence prime_totients*1+0 @820; skip [0] (resolve)` 
  `SEASMHGEATHTTHYCUGEIOIOGWBXXNEBEGEATRMNGGBHAMJJCNRSYNGJFLMMYDONLOEATYIOCEAGRAPPCNGFBIOOPNGLDFNGR`

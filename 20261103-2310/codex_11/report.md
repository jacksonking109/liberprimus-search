# Swarm run

Updated 2026-11-04 01:31:28. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 11 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\codex_11 --ledger reports\overnight\20261103-2310\codex_11\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 171 call(s) in the last 5h (cap 120), paused until 2026-11-04 03:38 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 171 call(s) in the last 5h (cap 550)
- claude-supervisor: 171 call(s) in the last 5h (cap 200)
- codex: 116 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/1 - 3.jpg/1 | 119 | 31830 | 47 | 0 |  |

## LP2:20.jpg/1 - 3.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 1 | 31830 | 0 | 6 | 0 |

- near_miss (program, by codex, margin -2.25): `sub; sequence primes*1+0 @334; skip [0] (resolve)` 
  `THGCYTHNFIWLOATEEAXOEXUUSDOTHTHCHTHEOWNTESUIRELEOFESJAEGIUTHHNBJOIOSPGNSGAEEANRHIMJEOUGOEPGPIOU`
- near_miss (program, by codex, margin -2.27): `add; sequence pi_digits*1+0 @1201; skip [0] (resolve); reverse text` 
  `AXGNGCAEATPTEHUBYRJLEOCUAEOIODFITHASEAECITSTFEHEOOYEUOEOEDTYSTHEAEODOEIOFOESEXAOEIOOEIWATCBWITHGOLD`
- near_miss (program, by codex, margin -2.30): `add; sequence pi_digits*1+0 @1081; skip [0, 28] (resolve)` 
  `OESNGSDGNDUPABEODIDEXNWTHXTHILYTNREAPOEOEAENORLEAOEIOWFMHLWINGEAIEAYMANTTACUAEURTHOGTHLMIOSUBDOJEAB`
- near_miss (program, by codex, margin -2.32): `sub; sequence primes*1+0 @491; skip [0] (resolve)` 
  `THLBWEAEEOANGYFBYEANANUSUNMUIOIOOEOFXCJYTHEARSEALOEAEOHCTHREOOEUBAYFEOGTHERSNGLFNGEOITCTHBTHSOFEOMTHYBYPE`
- near_miss (program, by codex, margin -2.32): `add; sequence pi_digits*1+0 @1374; skip [0, 28] (resolve)` 
  `YSMJDJCAEYSBDBEHANGPHHOERHXEAEPFRBMEAUEPROTAELREAIOMGNGCTOEFIANGLETEIDCUDACFIONOEXAAESTHXEAREORS`
- near_miss (program, by codex, margin -2.33): `add; sequence pi_digits*1+0 @109; skip [0, 28] (resolve)` 
  `AEEOSIFWCTTHBLNGHAERUMBIGGXFGBFJNOIOTMRUEEUADLMGEATHERECTARROEEAOEEWJSMUTHLFNYEAWOEBNGADFTDOIEAEO`
- near_miss (program, by codex, margin -2.33): `sub; sequence primes*1+0 @62; skip [0] (resolve)` 
  `OMEINTOSLFYEGIETHLILLUJLIOIOEAEOHYJSMOEBYIAECMPCNHUOMIOEOJTLDIOBPHNGBXPMGOETLUAEIOHDMTWHOESEOJFU`
- near_miss (program, by codex, margin -2.33): `add; sequence pi_digits*1+0 @168; skip [0] (resolve); reverse text` 
  `BEUYRAEDBITBIODDTHJOEPXUYJOYFJEEADNGLOEGNJJDEAJEABRAEFMEAMSYIRAEGFNGFFAXPSMNGDIOEOCIOBWENSFGEAMM`
- near_miss (program, by codex, margin -2.33): `add; sequence pi_digits*1+0 @1989; skip [0] (resolve); reverse text` 
  `TPCYEAAEFNGMJEOXONGAEOEOYSCRYJODFRNGHAMIOTFXSEOLOESHPRMNGTHTAAXAEOFANDMYHEAEONXALYIOCHATEOMNETHWFDM`
- near_miss (program, by codex, margin -2.33): `add; sequence pi_digits*1+0 @110; skip [0, 28] (resolve)` 
  `NGXXTDHTHOETHSDXBMNYMMRSTHXAJLDJIFIOTMRUEEUADLMGEATHERECTARROEEAOEEWJSMUTHLFNYEAWOEBNGADFTDOIEAEO`

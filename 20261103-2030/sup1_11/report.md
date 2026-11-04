# Swarm run

Updated 2026-11-03 22:19:20. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 11 --generators codex,qwen-local,gemma-local --rounds 4 --per-round 4 --report-dir reports\overnight\20261103-2030\sup1_11 --ledger reports\overnight\20261103-2030\sup1_11\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 40 call(s) in the last 5h (cap 40), paused until 2026-11-04 01:27 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 40 call(s) in the last 5h (cap 40), paused until 2026-11-04 01:27 (local cap, raise max_calls_per_window to allow more)
- claude-supervisor: 40 call(s) in the last 5h (cap 40), paused until 2026-11-04 01:27 (local cap, raise max_calls_per_window to allow more)
- codex: 9 call(s) in the last 5h (cap 30)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/1 - 3.jpg/1 | 119 | 26343 | 62 | 0 |  |

## LP2:20.jpg/1 - 3.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 32 | 1 | 26184 | 0 | 4 | 0 |
| qwen-local | 16 | 1 | 93 | 0 | 0 | 0 |
| gemma-local | 16 | 0 | 66 | 0 | 0 | 0 |

- near_miss (program, by codex, margin -2.23): `sub; sequence primes*1+0 @1628; skip [0] (resolve); columnar [6, 5, 4, 3, 2, 1, 0]` 
  `BFTMEIAFCSNDTMNWFIOAEAEAOAFYOEOESYCOEJEALEANGHYGEOONAEEUCWDESAEAJYYAAEYNGTHCDMGRPALMORANETHOEAEUOW`
- near_miss (program, by codex, margin -2.25): `sub; sequence primes*1+0 @334; skip [0] (resolve)` 
  `THGCYTHNFIWLOATEEAXOEXUUSDOTHTHCHTHEOWNTESUIRELEOFESJAEGIUTHHNBJOIOSPGNSGAEEANRHIMJEOUGOEPGPIOU`
- near_miss (program, by codex, margin -2.26): `sub; sequence primes*1+0 @740; skip [0, 28] (resolve)` 
  `CMTIMUBBLTHEATRNGTHNGHCNGSAETHJXXJATWIOGHEATNGSTHHHDMEALYEANWRNEAEEAXGEAHHYAEFLCWNNGEOITHMMXOHEWRNDO`
- near_miss (program, by codex, margin -2.29): `sub; sequence primes*1+0 @1362; skip [0] (resolve); columnar [6, 5, 4, 3, 2, 1, 0]` 
  `PFAIOAEOPTDFGHESBCMNNXFUXXJJWTHNPCNEATABWMHFUOFUJGTHHEAGOERIDTHIOSFIOENGMMMSAIDUYTHCDJEPEOPUC`
- near_miss (program, by codex, margin -2.29): `sub; sequence primes*1+0 @1361; skip [0] (resolve); columnar [6, 5, 4, 3, 2, 1, 0]` 
  `AEHAIOAEOPTDFGHESBCMNNXFUXXJJWTHNPCNEATABWMHFUOFUJGTHHEAGOERIDTHIOSFIOENGMMMSAIDUYTHCDJEPEOPUC`
- near_miss (program, by codex, margin -2.31): `sub; sequence primes*1+0 @1360; skip [0] (resolve); columnar [6, 5, 4, 3, 2, 1, 0]` 
  `FLUGWAMLTHOEHAOAEDBTHDSELCYLPBPEBGWHWOEEAHJTHOLCJIOIOHXLRHYIOEFHGNGCIOENGMMMSAIDUYTHCDJEPEOPUC`
- near_miss (program, by codex, margin -2.31): `sub; sequence primes*1+0 @1163; skip [0] (resolve); reverse text` 
  `EASTHEOLJHNUIOOENSOLEPOECANTBWIOFUEOPEANEALFTHAECNTHSFOODRNAEEWYARMRWOEGEATHWMRAERAEFWYTGEAMEARJFYIH`
- near_miss (program, by codex, margin -2.32): `sub; sequence primes*1+0 @491; skip [0] (resolve)` 
  `THLBWEAEEOANGYFBYEANANUSUNMUIOIOOEOFXCJYTHEARSEALOEAEOHCTHREOOEUBAYFEOGTHERSNGLFNGEOITCTHBTHSOFEOMTHYBYPE`
- near_miss (program, by codex, margin -2.32): `sub; sequence primes*1+0 @844; skip [0] (resolve); columnar [6, 5, 4, 3, 2, 1, 0]` 
  `EOODAIOAEYFYBPPNGOEEATWUCRHWOEXNLLSEASWFWYWTTHIBDYASIODUBOIAHLRIHIOFTHEMFFGFCFFCAFOJYAEEOSHEOE`
- near_miss (program, by codex, margin -2.33): `sub; sequence primes*1+0 @62; skip [0] (resolve)` 
  `OMEINTOSLFYEGIETHLILLUJLIOIOEAEOHYJSMOEBYIAECMPCNHUOMIOEOJTLDIOBPHNGBXPMGOETLUAEIOHDMTWHOESEOJFU`

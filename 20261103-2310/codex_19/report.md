# Swarm run

Updated 2026-11-04 00:00:53. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 19 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\codex_19 --ledger reports\overnight\20261103-2310\codex_19\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 142 call(s) in the last 5h (cap 120), paused until 2026-11-04 01:40 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 142 call(s) in the last 5h (cap 550)
- claude-supervisor: 142 call(s) in the last 5h (cap 200)
- codex: 75 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:33.jpg - 50.jpg/1 | 91 (short) | 36256 | 47 | 0 |  |

## LP2:33.jpg - 50.jpg/1

**Caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution.**

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 1 | 36256 | 0 | 8 | 0 |

- near_miss (program, by codex, margin -2.00): `sub; sequence primes*1+0 @1605; skip [0, 7] (resolve)` 
  `EOEEOEJPNGBIOSMDFPPPWUDNDNGBAEXMMHADNGOESHFADEASAJXWEEDFAETNMASITEOTWGFEUNGSSHXXTHTWDIOWONGIW`
- near_miss (program, by codex, margin -2.00): `sub; sequence primes*1+0 @1607; skip [0, 7] (resolve)` 
  `IOFAEHFWCWIOSMDFPPPWUDNDNGBAEXMMHADNGOESHFADEASAJXWEEDFAETNMASITEOTWGFEUNGSSHXXTHTWDIOWONGIW`
- near_miss (program, by codex, margin -2.02): `sub; sequence primes*1+0 @1606; skip [0, 7] (resolve)` 
  `RTTHTFPNGBIOSMDFPPPWUDNDNGBAEXMMHADNGOESHFADEASAJXWEEDFAETNMASITEOTWGFEUNGSSHXXTHTWDIOWONGIW`
- near_miss (program, by codex, margin -2.04): `sub; sequence primes*1+0 @851; skip [0] (resolve)` 
  `AEAEMIOFXEOEBOOOFATEEROEGTHLGXYETASCEBGWIOMGWAETHOENREALFYIOGAEEOMNGNIOAWLTRNGTEANRMSITALWIONSYCNGHO`
- near_miss (program, by codex, margin -2.07): `beaufort; sequence e_digits*1+0 @210; map reverse; skip [7] (resolve); reverse text` 
  `EANGIYDJAWIWDHLEAFERBDTHSCTYESCOAEDAWXNIEWSDOIOCNTBIACIOCNEOOJAEOETHCATNEARWEOUCPROJLUFOULBHEA`
- near_miss (program, by codex, margin -2.07): `sub; sequence primes*1+0 @1605; skip [0] (resolve)` 
  `EOEEOEJPNGBIOSMDFPPPWUDNDNGBAEXMMHADNGOESHFADEASAJXWEEDFAETNMASITEOTDEADXAWJAIOFNGAEXGJBEUBAES`
- near_miss (program, by codex, margin -2.07): `sub; sequence primes*1+0 @300; skip [0, 7] (resolve)` 
  `THTTOFFHINYEEMDDDIOPRMDEOHXCEEEAEATIOYSLPEAJYMNGEODTNUDEDTHAEEONBWTHCBNCYOMILCWNTEATHEOWOTEAPPW`
- near_miss (program, by codex, margin -2.08): `sub; sequence prime_totients*1+0 @593; skip [0] (resolve)` 
  `AEGTHEOEOEAADOONFYOEHEOIOTIOXOUTWELOMCTCDEANGNGBHHEARECYGONGIOUMEANYNGEUXNGNSRXAJWNEEACNMIDAENBRLX`
- near_miss (program, by codex, margin -2.08): `sub; sequence primes*1+0 @710; skip [0, 7] (resolve)` 
  `AWUSGXTOEMSSORETTHGIOERECIXULLNUGWEAIOUAESEOMTHGEAHADYHWHNGSFUNYWACLAWEAIOTEAMWFOBSMMHWFCLCWW`
- near_miss (program, by codex, margin -2.08): `sub; sequence prime_totients*1+0 @594; skip [0] (resolve)` 
  `BFNGDFOEAADOONFYOEHEOIOTIOXOUTWELOMCTCDEANGNGBHHEARECYGONGIOUMEANYNGEUXNGNSRXAJWNEEACNMIDAENBRLX`

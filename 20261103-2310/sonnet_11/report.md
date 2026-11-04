# Swarm run

Updated 2026-11-03 23:43:42. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 11 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\sonnet_11 --ledger reports\overnight\20261103-2310\sonnet_11\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261103-2310\sonnet_11\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 131 call(s) in the last 5h (cap 120), paused until 2026-11-04 01:33 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 131 call(s) in the last 5h (cap 550)
- claude-supervisor: 131 call(s) in the last 5h (cap 200)
- codex: 60 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/1 - 3.jpg/1 | 119 | 56563 | 44 | 0 |  |

## LP2:20.jpg/1 - 3.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 48 | 4 | 56563 | 0 | 20 | 0 |

- near_miss (program, by claude-sonnet, margin -2.22): `sub; sequence prime_totients*1+0 @1400; skip [0] (resolve)` 
  `THEJYHCFTHEANEOGDMIOPIOMGGLHMIGNLRFMAEIOWDOERNGGMPYDLYYNUTHWPXAFNGEOIOIONGYEACBMNGIOCPEAASBLAIOHSRO`
- near_miss (program, by claude-sonnet, margin -2.22): `sub; sequence primes*1+28 @1400; skip [0] (resolve)` 
  `THEJYHCFTHEANEOGDMIOPIOMGGLHMIGNLRFMAEIOWDOERNGGMPYDLYYNUTHWPXAFNGEOIOIONGYEACBMNGIOCPEAASBLAIOHSRO`
- near_miss (program, by claude-sonnet, margin -2.23): `sub; sequence prime_totients*1+0 @1040; skip [0] (resolve); reverse text` 
  `EWJAEDDEOFSGCYJEAEAAIOEAPTHJATHBIFSHJAUCELNGNGJJFPDEANIOXBTHUSCJEROEPYTHOFBRATASCOEOTTHMHBANGYNGENN`
- near_miss (program, by claude-sonnet, margin -2.25): `sub; sequence primes*1+0 @334; skip [0] (resolve)` 
  `THGCYTHNFIWLOATEEAXOEXUUSDOTHTHCHTHEOWNTESUIRELEOFESJAEGIUTHHNBJOIOSPGNSGAEEANRHIMJEOUGOEPGPIOU`
- near_miss (program, by claude-sonnet, margin -2.26): `sub; sequence prime_totients*1+0 @1018; skip [0] (resolve); reverse text` 
  `WMTHTTHEOCAIEAJDIDDIOEADHIOCOERAEGWYSEREXGFYALABOWIDREDRWFCCISINEORWTHSBEOTHHUEAOEIOTTHHYGSTAEHOTHF`
- near_miss (program, by claude-sonnet, margin -2.27): `sub; sequence e_digits*1+0 @1155; map reverse; skip [0] (resolve)` 
  `WBPLTHXAJUXGHPCYYNEOOEBFEOAETNTHTEOLYXOLYJJOEIORTHJNGDYETRMSOLDFORTHTPBUFGNREUDOECIIHPOTCAPAET`
- near_miss (program, by claude-sonnet, margin -2.27): `sub; sequence prime_totients*1+0 @1039; skip [0] (resolve); reverse text` 
  `LJAETHGEOEGDTWIOSCUWTHPMWDOHIOEOBSHJAUCELNGNGJJFPDEANIOXBTHUSCJEROEPYTHOFBRATASCOEOTTHMHBANGYNGENN`
- near_miss (program, by claude-sonnet, margin -2.28): `sub; sequence primes*1+0 @756; skip [0] (resolve); columnar [0, 1, 2, 3, 4, 5, 6]` 
  `PCUPNGOENGMGEAGNGLEANYSEAOENOUSUIEOFPPEOIGEAEABOEGLGEOCOMNGOEGYMNGDSOEYRHEAOOEDEOPGROLOEAUWAXEAFGGEAPYBX`
- near_miss (program, by claude-sonnet, margin -2.28): `sub; sequence pi_digits*1+0 @378; skip [0] (resolve)` 
  `XGIWEYIOSNGCWNWWYNGIEOOFYFLONNGRFFATHBAENGHTHNGSIITEDAIDSOUXIOOPBITIOGGPFNGTXANGYGBJSJNMRMMRAR`
- near_miss (program, by claude-sonnet, margin -2.28): `sub; sequence primes*1+0 @1026; skip [0] (resolve); columnar [0, 1, 2, 3, 4, 5, 6]` 
  `MFJNGHCHIYJTRLUPONYIEHLUEIIFIOFCWASTWIDHDGLTCOETHPTHUAEBWGIPNGOEOOENGGWFHOYNFPMALLMMDEOULFEA`

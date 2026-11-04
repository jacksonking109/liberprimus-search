# Swarm run

Updated 2026-11-03 23:59:41. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 12 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\sonnet_12 --ledger reports\overnight\20261103-2310\sonnet_12\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261103-2310\sonnet_12\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 140 call(s) in the last 5h (cap 120), paused until 2026-11-04 01:35 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 140 call(s) in the last 5h (cap 550)
- claude-supervisor: 140 call(s) in the last 5h (cap 200)
- codex: 73 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1 | 693 | 33572 | 42 | 0 |  |

## LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 48 | 6 | 33572 | 0 | 3 | 0 |

- near_miss (program, by claude-sonnet, margin -2.40): `sub; sequence e_digits*1+0 @16; skip [0] (resolve)` 
  `JLYNBEODEOIODCIOCTHBLAEEARWAYOXEBHNTAEFGJGNDOFMIEOPSDIOLOETHXIOGOCRTHDANCLNGNGUMBANTHUSOJFDGDSIOP`
- near_miss (program, by claude-sonnet, margin -2.41): `sub; sequence prime_totients*1+0 @913; skip [0] (resolve)` 
  `MWWEAFEOJTHXUCPTJBDXOHRNNYHEAFBBTHOIYBIYNGEOEHUDAFEAETCGNETEWTHEOEOEOOEAENUIOUSRFXANGYAEEAFSIOHTHJT`
- near_miss (program, by claude-sonnet, margin -2.41): `sub; sequence primes*1+28 @913; skip [0] (resolve)` 
  `MWWEAFEOJTHXUCPTJBDXOHRNNYHEAFBBTHOIYBIYNGEOEHUDAFEAETCGNETEWTHEOEOEOOEAENUIOUSRFXANGYAEEAFSIOHTHJT`

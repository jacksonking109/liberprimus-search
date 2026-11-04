# Swarm run

Updated 2026-11-04 13:40:08. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 25 --generators claude-opus --rounds 4 --per-round 6 --report-dir reports\overnight\20261104-0949\sup1_25 --ledger reports\overnight\20261104-0949\sup1_25\ledger.sqlite --brief-file reports\overnight\20261104-0949\sup1_25\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 215 call(s) in the last 5h (cap 550)
- claude-sonnet: 215 call(s) in the last 5h (cap 550)
- claude-supervisor: 215 call(s) in the last 5h (cap 550)
- codex: 81 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:54.jpg-55.jpg - 71.jpg-72.jpg | 308 | 6265 | 24 | 0 |  |

## LP2:54.jpg-55.jpg - 71.jpg-72.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus | 24 | 0 | 6265 | 0 | 4 | 0 |

- near_miss (program, by claude-opus, margin -0.20; chance 22: noise level (pure noise does this well that often)): `beaufort; sequence primes*4+7 @295; skip [7] (resolve)` 
  `WLMEOJTHGEAELMJJPWBRTHPAJNACCEAALJIOLPNMEALSWSNGUCGXEROOANGYEAFYGCTHCRSUTTHEEGTNGNREOIORHRCEOD`
- near_miss (program, by claude-opus, margin -0.21; chance 32: noise level (pure noise does this well that often)): `beaufort; sequence primes*4+7 @294; skip [7] (resolve)` 
  `UEOEBHWMINBAFOTHWBRTHPAJNACCEAALJIOLPNMEALSWSNGUCGXEROOANGYEAFYGCTHCRSUTTHEEGTNGNREOIORHRCEOD`
- near_miss (program, by claude-opus, margin -0.22; chance 70: noise level (pure noise does this well that often)): `add; sequence prime_totients*3+2 @414; skip [0, 7] (resolve)` 
  `IBSEOBIJTHEOIOWNGRTUTHFOEOAEENWRSATHJUXUBAIOEMOEETUFMGTMTHTHEAEOOEUAEHIXMALWWIOHEFJIODTHGRSEATNUJSG`
- near_miss (program, by claude-opus, margin -0.23; chance 78: noise level (pure noise does this well that often)): `add; sequence prime_totients*3+2 @411; skip [0, 7] (resolve)` 
  `HNGENAEAEOFIOASGNGXONOEAEURCIEWMANGDOIOOENGLHCNDLIHOETHGEANTTHMPSHMGEUNPAJUBPNGWEOYJIODTHGRSEATNUJSG`
- near_miss (program, by claude-opus, margin -0.23; chance 89: noise level (pure noise does this well that often)): `beaufort; sequence prime_totients*2+3 @440; map reverse; skip [27] (resolve)` 
  `SOEGEAWXLAHJMBLEOCUEOAWEOTNGSEAMANEOSWXOASYSEOUBLIOIOJDPTJGIADEEOYOYAXTAAEOREOEASOEMHISENEEANGSRRR`
- near_miss (program, by claude-opus, margin -0.23; chance 83: noise level (pure noise does this well that often)): `add; sequence prime_totients*3+2 @412; skip [0, 7] (resolve)` 
  `YTWNGNGLRETMTPCYWNOEAEURCIEWMANGDOIOOENGLHCNDLIHOETHGEANTTHMPSHMGEUNPAJUBPNGWEOYJIODTHGRSEATNUJSG`
- near_miss (program, by claude-opus, margin -0.23; chance 68: noise level (pure noise does this well that often)): `beaufort; sequence primes*4+7 @685; skip [7] (resolve)` 
  `IIGLMYBJTAWRCSWTFNAEDNGOEAWDCIOIOTHBFGBLAYJNGNWBEAEEANGPEOJESTWEOOETHDLIOHMYNGWGPOONGIOLCCEOAEMLNGDC`
- near_miss (program, by claude-opus, margin -0.23; chance 78: noise level (pure noise does this well that often)): `beaufort; sequence primes*4+7 @686; skip [7] (resolve)` 
  `CHOEDUFWAEOODPAIWAGRLNGOLJWIOFOEOECEOTXWSJCGOERWAESOWHOLGCOJTHEAAEPGYGOGCWWGPOONGIOLCCEOAEMLNGDC`
- near_miss (program, by claude-opus, margin -0.24; chance 70: noise level (pure noise does this well that often)): `sub; sequence prime_totients*5+1 @478; skip [27] (resolve)` 
  `TIEAHUXTNGLIOUNSDHSMSPNBBIOLWMFEOTHEAINCLEUXHNEARMABTHAEOEUHGIDEOSEAYFHAEBXWYOTDHIOOEOEOFIORNGFCTAW`

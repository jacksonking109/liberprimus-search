# Swarm run

Updated 2026-11-04 13:03:45. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 19 --generators claude-opus --rounds 4 --per-round 6 --report-dir reports\overnight\20261104-0949\sup1_19 --ledger reports\overnight\20261104-0949\sup1_19\ledger.sqlite --brief-file reports\overnight\20261104-0949\sup1_19\brief.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 193 call(s) in the last 5h (cap 550)
- claude-sonnet: 193 call(s) in the last 5h (cap 550)
- claude-supervisor: 193 call(s) in the last 5h (cap 550)
- codex: 81 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:33.jpg - 50.jpg/1 | 91 (short) | 2605 | 23 | 0 |  |

## LP2:33.jpg - 50.jpg/1

**Caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution.**

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-opus | 24 | 1 | 2605 | 0 | 5 | 0 |

- near_miss (program, by claude-opus, margin -2.08; chance 12: noise level (pure noise does this well that often)): `add; sequence primes*5+4 @294; skip [8, 15] (resolve)` 
  `GBFXITHBLHFYEYCBPTHMDSRCIOEOEABNXWSOFEETGAOGHUECNGBNIOPEOAENRNGMNYSACEISTHFEARMWOESYLIHEARNCOE`
- near_miss (program, by claude-opus, margin -2.10; chance 15: noise level (pure noise does this well that often)): `add; sequence primes*5+4 @10; skip [8, 15] (resolve)` 
  `HIOLNGWERYHYDXOEFOESNGSPAIOLTHCLNNCBGXFEAGLFMEMYCOERLHSXPTEARHYEAEROPYMATHFMANTTHDCNESYNGPYD`
- near_miss (program, by claude-opus, margin -2.11; chance 17: noise level (pure noise does this well that often)): `add; sequence primes*5+4 @293; skip [8, 15] (resolve)` 
  `AEAMLNLTFNGFYEYCBPTHMDSRCIOEOEABNXWSOFEETGAOGHUECNGBNIOPEOAENRNGMNYSACEISTHFEARMWOESYLIHEARNCOE`
- near_miss (program, by claude-opus, margin -2.13; chance 15: noise level (pure noise does this well that often)): `sub; sequence squares*1+0 @8; skip [27] (resolve)` 
  `BEUFUSTHXPWWNGIIOSOHIOGTHAEEAHIOTBWIOEOTHAEPEENGJHTNLNRSTUMPETUTNOWTCTHTPYTHYFEOETHTYUPAEUOGTHTHTHO`
- near_miss (program, by claude-opus, margin -2.14; chance 19: noise level (pure noise does this well that often)): `sub; sequence squares*1+0 @7; skip [27] (resolve)` 
  `OGLNGAJFXSJPBTOEEOTHNGEAIOEAYOEIONUNGATTHEOTHAEPEENGJHTNLNRSTUMPETUTNOWTCTHTPYTHYFEOETHTYUPAEUOGTHTHTHO`
- near_miss (program, by claude-opus, margin -2.15; chance 21: noise level (pure noise does this well that often)): `sub; sequence e_digits*3+2 @92; skip [27] (resolve); reverse text` 
  `EODUCAAEPPDOEAOELIOTPEWHERDFOEDWEADIDXPAAENGEAWMAEDLAESRLPPIOLDYFTAETFSGBYWTHWNGTHTHLEODSIORIOTTHTHIOEFH`
- near_miss (program, by claude-opus, margin -2.16; chance 32: noise level (pure noise does this well that often)): `add; sequence primes*5+4 @9; skip [8, 15] (resolve)` 
  `IOYFJTBOTIOYDXOEFOESNGSPAIOLTHCLNNCBGXFEAGLFMEMYCOERLHSXPTEARHYEAEROPYMATHFMANTTHDCNESYNGPYD`
- near_miss (program, by claude-opus, margin -2.17; chance 30: noise level (pure noise does this well that often)): `sub; sequence e_digits*3+2 @93; skip [27] (resolve); reverse text` 
  `OGSCUTHIOOEFWRTLWIOPEWHERDFOEDWEADIDXPAAENGEAWMAEDLAESRLPPIOLDYFTAETFSGBYWTHWNGTHTHLEODSIORIOTTHTHIOEFH`
- near_miss (program, by claude-opus, margin -2.18; chance 43: noise level (pure noise does this well that often)): `add; sequence primes*5+4 @11; skip [8, 15] (resolve)` 
  `NEUEOHMXIOHBRSPUXNAEEOAESAIOLTHCLNNCBGXFEAGLFMEMYCOERLHSXPTEARHYEAEROPYMATHFMANTTHDCNESYNGPYD`
- near_miss (program, by claude-opus, margin -2.19; chance 41: noise level (pure noise does this well that often)): `sub; sequence triangular*2+5 @28; skip [27] (resolve); columnar [6, 5, 4, 3, 2, 1, 0]` 
  `GTHNFTLBEHLFRYAECEODNIOUSOENGPRPOBYEIOIOTHBEMIAOJHTHOECOEDWTHHELEAEDBUMMHHENGUXGADEAAETIOXDJOYEAAGO`

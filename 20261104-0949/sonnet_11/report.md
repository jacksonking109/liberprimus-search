# Swarm run

Updated 2026-11-04 10:18:34. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 11 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\sonnet_11 --ledger reports\overnight\20261104-0949\sonnet_11\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261104-0949\sonnet_11\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 61 call(s) in the last 5h (cap 550)
- claude-sonnet: 61 call(s) in the last 5h (cap 550)
- claude-supervisor: 61 call(s) in the last 5h (cap 550)
- codex: 18 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:20.jpg/1 - 3.jpg/1 | 119 | 35202 | 34 | 0 |  |

## LP2:20.jpg/1 - 3.jpg/1

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 48 | 13 | 35202 | 0 | 11 | 0 |

- near_miss (program, by claude-sonnet, margin -2.22; chance 79: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @1400; skip [0] (resolve)` 
  `THEJYHCFTHEANEOGDMIOPIOMGGLHMIGNLRFMAEIOWDOERNGGMPYDLYYNUTHWPXAFNGEOIOIONGYEACBMNGIOCPEAASBLAIOHSRO`
- near_miss (program, by claude-sonnet, margin -2.23; chance 95: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @1040; skip [0] (resolve); reverse text` 
  `EWJAEDDEOFSGCYJEAEAAIOEAPTHJATHBIFSHJAUCELNGNGJJFPDEANIOXBTHUSCJEROEPYTHOFBRATASCOEOTTHMHBANGYNGENN`
- near_miss (program, by claude-sonnet, margin -2.25; chance 1.5e+02: noise level (pure noise does this well that often)): `sub; sequence primes*1+0 @334; skip [0] (resolve)` 
  `THGCYTHNFIWLOATEEAXOEXUUSDOTHTHCHTHEOWNTESUIRELEOFESJAEGIUTHHNBJOIOSPGNSGAEEANRHIMJEOUGOEPGPIOU`
- near_miss (program, by claude-sonnet, margin -2.26; chance 1.6e+02: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @1018; skip [0] (resolve); reverse text` 
  `WMTHTTHEOCAIEAJDIDDIOEADHIOCOERAEGWYSEREXGFYALABOWIDREDRWFCCISINEORWTHSBEOTHHUEAOEIOTTHHYGSTAEHOTHF`
- near_miss (program, by claude-sonnet, margin -2.27; chance 2.1e+02: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @1039; skip [0] (resolve); reverse text` 
  `LJAETHGEOEGDTWIOSCUWTHPMWDOHIOEOBSHJAUCELNGNGJJFPDEANIOXBTHUSCJEROEPYTHOFBRATASCOEOTTHMHBANGYNGENN`
- near_miss (program, by claude-sonnet, margin -2.28; chance 2.1e+02: noise level (pure noise does this well that often)): `sub; sequence pi_digits*1+0 @378; skip [0] (resolve)` 
  `XGIWEYIOSNGCWNWWYNGIEOOFYFLONNGRFFATHBAENGHTHNGSIITEDAIDSOUXIOOPBITIOGGPFNGTXANGYGBJSJNMRMMRAR`
- near_miss (program, by claude-sonnet, margin -2.29; chance 2.7e+02: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @739; skip [0] (resolve)` 
  `HYNGPAREAOIOWHIOJPWASWYAWNEDNGAFDFWBMYMOERSFPWCNGNGIOFIHCIXPSNUMWEASEENDMMFHXYHGCNGEOLNGOETHTB`
- near_miss (program, by claude-sonnet, margin -2.29; chance 2.8e+02: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @1017; skip [0] (resolve); reverse text` 
  `SFHOEYYJEAEJFREORAETHCXXTHMYGFLPNIEAIYAHOEYALABOWIDREDRWFCCISINEORWTHSBEOTHHUEAOEIOTTHHYGSTAEHOTHF`
- near_miss (program, by claude-sonnet, margin -2.29; chance 2.9e+02: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @1056; skip [0] (resolve)` 
  `SOWCEOCIONOEJEOPEAWAESHGYGBGMGNSOWFOEHJMEGGASHBEOIOLMRAIIOFXOEFLBPEOTHTHHEOFNGJMTHEMTHECSPEOEGMMEALTH`
- near_miss (program, by claude-sonnet, margin -2.30; chance 2.9e+02: noise level (pure noise does this well that often)): `sub; sequence e_digits*1+0 @1814; skip [0] (resolve)` 
  `SWWGEOIOTHPAENPHRNEABJRTHYLOEYNPHGFNGHXNGAJWMMEOPPOEEAETHANANBIOUXLTBTHTHGSNGNGISEATOECNGRTPJDNPOERYTH`

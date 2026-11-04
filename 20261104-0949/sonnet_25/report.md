# Swarm run

Updated 2026-11-04 12:05:26. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 25 --generators claude-sonnet --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261104-0949\sonnet_25 --ledger reports\overnight\20261104-0949\sonnet_25\ledger.sqlite --auto-brief claude-supervisor --brief-context reports\overnight\20261104-0949\sonnet_25\brief_context.txt --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it. A lead's *chance* is how many attempts at least this good pure noise would produce among this target's attempts: about 1 or more is noise level, whatever the margin or section length.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 153 call(s) in the last 5h (cap 550)
- claude-sonnet: 153 call(s) in the last 5h (cap 550)
- claude-supervisor: 153 call(s) in the last 5h (cap 550)
- codex: 81 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:54.jpg-55.jpg - 71.jpg-72.jpg | 308 | 8411 | 41 | 0 |  |

## LP2:54.jpg-55.jpg - 71.jpg-72.jpg

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| claude-sonnet | 48 | 6 | 8411 | 0 | 2 | 0 |

- near_miss (program, by claude-sonnet, margin -0.19; chance 25: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @373; map reverse; skip [0] (resolve)` 
  `GCIAEMEAHHTDBAEPAEPMLNGNGIOPSFJTRUGRJEMYTHSCGENGBXPLYNGANPPXAETHMMIOPEOREOEAUAEHNGWFSOOEIFYEAPUOAJS`
- near_miss (program, by claude-sonnet, margin -0.25; chance 90: noise level (pure noise does this well that often)): `sub; sequence prime_totients*1+0 @208; map reverse; skip [0] (resolve); columnar [0, 1, 2, 3, 4, 5, 6]` 
  `NGIOALPHWDAECXEALULAEFEPCEOCSOENSOENNGTELUMRSADOLXYPECHBLNTWSCEALAPFROHSAJGIONGWNOBWLBEUUDTH`

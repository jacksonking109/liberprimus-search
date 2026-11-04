# Swarm run

Updated 2026-11-03 23:46:02. Command: `lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 21 --generators codex --rounds 6 --per-round 8 --max-attempts 60000 --report-dir reports\overnight\20261103-2310\codex_21 --ledger reports\overnight\20261103-2310\codex_21\ledger.sqlite --models config/models.toml --spend-ledger reports/model_spend.sqlite`

**1 target(s), 0 final pass(es).** A FINAL lead survived the end-of-search check (Bonferroni over every attempt on that target); read the text before trusting it.

Model usage (spend ledger): deepseek $0.0000, qwen-local $0.0000, gemma-local $0.0000, granite $0.0000, claude-opus $0.0000, claude-sonnet $0.0000, claude-supervisor $0.0000, codex $0.0000, dry $0.0000

- claude-opus: 134 call(s) in the last 5h (cap 120), paused until 2026-11-04 01:34 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 134 call(s) in the last 5h (cap 550)
- claude-supervisor: 134 call(s) in the last 5h (cap 200)
- codex: 63 call(s) in the last 5h (cap 750)

| target | symbols | attempts | hypotheses | final passes | stopped |
| --- | ---: | ---: | ---: | ---: | --- |
| LP2:56.jpg/2 | 121 | 40233 | 48 | 0 |  |

## LP2:56.jpg/2

| generator | proposals | invalid | attempts | passes | near misses | model errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| codex | 48 | 0 | 40233 | 0 | 8 | 0 |

- near_miss (program, by codex, margin -0.32): `sub; sequence primes*1+0 @630; skip [0] (resolve)` 
  `RUCLENGTHOEUNGTHNLSEAAEUAOAEONGNIODXMMEAIPOOESNGFDATNGSDUNGEONCONINWEOTHCUWXHUNGEJLLOERPULUWSBPDIAECI`
- near_miss (program, by codex, margin -0.32): `sub; sequence primes*1+0 @234; skip [2] (resolve)` 
  `DYCEAOEOEOUUREXNGXDOESBDIOEOAEBEOEOEIOGTHUSNOAETHMAEULAEBAETJFTHMPIOLBTHEFOURPMGOEDENGHIONFGFTHENSPFLINGB`
- near_miss (program, by codex, margin -0.34): `sub; sequence primes*1+0 @2; skip [2] (resolve)` 
  `OEIORFGAERACHOEOERAGWHILLCERUNTHSDTHGJOYMTHDAECEARAEHWGAGTHAETMLTHTHAEALMYODEDXNGGIMEATUCDDMHUAFTH`
- near_miss (program, by codex, margin -0.34): `sub; sequence primes*1+0 @1869; skip [2] (resolve)` 
  `AIODBNGWJNGNGEARTHSHUIOEAOYEAOTJDMISSTHIPEADLATEMPOEAEGNRFTHJEABXPTHAMAXWEICIOUMOENNECCUTHPRBAWIOAEYR`
- near_miss (program, by codex, margin -0.34): `sub; sequence primes*1+0 @1424; skip [2] (resolve)` 
  `LNGAENSUWTHTHCPPENGCSBIOIODJIWJGBDIMLXHGHIOMOEEMSMOESRNCEWIOEAEOSNGIOARREPGUGETAEONOTHNGGTHTHLJAFF`
- near_miss (program, by codex, margin -0.35): `sub; sequence primes*1+0 @1928; skip [2] (resolve)` 
  `FEYEAMMIISNTMIAETAOEUUWAFAUNGUOETHOITHNGGTHTHRBJXGXEAPFTHPNIOEUTHIMOEOESAUCAEXIFEOFNTOETTHUBWODEXMN`
- near_miss (program, by codex, margin -0.35): `sub; sequence primes*1+0 @1868; skip [0] (resolve)` 
  `YTHHNGIOPMHRUBGBEOAERCCSOBOEIEORTAEIOYIPEADLATEMPOEAEGNRFOOEOENHWTMOFFEFTHAJFEAXEAHNTTXGMTHRRTXGSS`
- near_miss (program, by codex, margin -0.36): `sub; sequence primes*1+0 @1868; skip [2] (resolve)` 
  `YTHHNGIOPMHRUBGBEOAERCCSOBOEIEORTAEIOYIPEADLATEMPOEAEGNRFTHJEABXPTHAMAXWEICIOUMOENNECCUTHPRBAWIOAEYR`
- near_miss (program, by codex, margin -0.36): `sub; sequence primes*1+0 @232; skip [2] (resolve)` 
  `GOJCPUWNGNGOEEAAGYGCRGRGEGAELEAMATNGOIPCGRMAEULAEBAETJFTHMPIOLBTHEFOURPMGOEDENGHIONFGFTHENSPFLINGB`
- near_miss (program, by codex, margin -0.36): `sub; sequence primes*1+0 @1425; skip [2] (resolve)` 
  `XSJCNACMAEAJOEOETHHJSNGCNGTGUNTHJEATHMLXHGHIOMOEEMSMOESRNCEWIOEAEOSNGIOARREPGUGETAEONOTHNGGTHTHLJAFF`

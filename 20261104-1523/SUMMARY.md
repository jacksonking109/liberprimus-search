# Overnight run 20261104-1523

Started 2026-11-04 15:23:11, updated 2026-11-04 15:49:24, status **running**. Jobs: pending 47, running 3, done 11

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 15:23:11 | 2026-11-04 15:37:17 | Claude Code proposers vs the random control |
| sonnet/10 | done | 2026-11-04 15:37:33 | 2026-11-04 15:41:04 | Sonnet, briefed by Opus |
| sonnet/11 | done | 2026-11-04 15:41:06 | 2026-11-04 15:44:37 | Sonnet, briefed by Opus |
| sonnet/12 | done | 2026-11-04 15:44:52 | 2026-11-04 15:49:24 | Sonnet, briefed by Opus |
| sonnet/13 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/14 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/15 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/16 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/17 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/18 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/19 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/20 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/21 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/22 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/24 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/25 | pending |  |  | Sonnet, briefed by Opus |
| codex/25 | done | 2026-11-04 15:23:11 | 2026-11-04 15:35:47 | Codex (exploratory) |
| codex/24 | done | 2026-11-04 15:23:11 | 2026-11-04 15:40:48 | Codex (exploratory) |
| codex/22 | done | 2026-11-04 15:36:02 | 2026-11-04 15:48:59 | Codex (exploratory) |
| codex/21 | done | 2026-11-04 15:41:06 | 2026-11-04 15:47:02 | Codex (exploratory) |
| codex/20 | running | 2026-11-04 15:47:18 |  | Codex (exploratory) |
| codex/19 | running | 2026-11-04 15:49:14 |  | Codex (exploratory) |
| codex/18 | pending |  |  | Codex (exploratory) |
| codex/17 | pending |  |  | Codex (exploratory) |
| codex/16 | pending |  |  | Codex (exploratory) |
| codex/15 | pending |  |  | Codex (exploratory) |
| codex/14 | pending |  |  | Codex (exploratory) |
| codex/13 | pending |  |  | Codex (exploratory) |
| codex/12 | pending |  |  | Codex (exploratory) |
| codex/11 | pending |  |  | Codex (exploratory) |
| codex/10 | pending |  |  | Codex (exploratory) |
| local/17 | done | 2026-11-04 15:23:11 | 2026-11-04 15:31:35 | local models |
| local/18 | done | 2026-11-04 15:31:51 | 2026-11-04 15:41:46 | local models |
| local/16 | done | 2026-11-04 15:42:01 | 2026-11-04 15:47:33 | local models |
| local/19 | running | 2026-11-04 15:47:48 |  | local models |
| local/15 | pending |  |  | local models |
| local/20 | pending |  |  | local models |
| local/14 | pending |  |  | local models |
| local/21 | pending |  |  | local models |
| local/13 | pending |  |  | local models |
| local/22 | pending |  |  | local models |
| local/12 | pending |  |  | local models |
| local/24 | pending |  |  | local models |
| local/11 | pending |  |  | local models |
| local/25 | pending |  |  | local models |
| local/10 | pending |  |  | local models |
| deepseek/10 | pending |  |  | DeepSeek (volume) |
| deepseek/11 | pending |  |  | DeepSeek (volume) |
| deepseek/12 | pending |  |  | DeepSeek (volume) |
| deepseek/13 | pending |  |  | DeepSeek (volume) |
| deepseek/14 | pending |  |  | DeepSeek (volume) |
| deepseek/15 | pending |  |  | DeepSeek (volume) |
| deepseek/16 | pending |  |  | DeepSeek (volume) |
| deepseek/17 | pending |  |  | DeepSeek (volume) |
| deepseek/18 | pending |  |  | DeepSeek (volume) |
| deepseek/19 | pending |  |  | DeepSeek (volume) |
| deepseek/20 | pending |  |  | DeepSeek (volume) |
| deepseek/21 | pending |  |  | DeepSeek (volume) |
| deepseek/22 | pending |  |  | DeepSeek (volume) |
| deepseek/24 | pending |  |  | DeepSeek (volume) |
| deepseek/25 | pending |  |  | DeepSeek (volume) |

## Now running

**codex/20** (since 2026-11-04 15:47:18), latest log lines:
```
  | Brief for LP2:50/2-56/1 (1468 runes, IC 0.995 so flat, doubles 11 vs 50.6 expected)
  | Nothing has been tried on this section yet. The flat IC rules out monoalphabetic and short-period keys being visible directly. The strong doubles deficit means adjacent ciphertext runes are rarely
  | 1. Prime-totient stream, modelled on the solved LP page. Use sequence prime_totients, combine sub, offset_range [0,2000], with skip [0] (F), first skip_mode "all", then "resolve". Repeat with comb
  | 2. Autokey, which suits the doubles deficit. Use source "ciphertext" and source "plaintext", each with combine sub, add and beaufort. Primers: single runes 0..28 (one proposal per value, or batch 
  | 3. Other sequences with offset_range [0,2000]: primes, fibonacci, pi_digits, e_digits, triangular, squares, naturals. Use combine sub and add, scale 1 and add 0 first. Then scale 28 (a negated str
  | 4. Repeat-word keys whose period may be hidden by the flat IC: DIVINITY, CIRCUMFERENCE, FIRFUMFERENFE, PILGRIM, INSTAR, EMERGE, CICADA, PARABLE. Use combine sub and beaufort, map identity and reve
  | 5. Reversal variants. Set reverse_text true together with the best stream families above (prime_totients sub, ciphertext autokey). The section may be written backwards like other LP pages.
  | 6. Columnar transposition. Undo columnar with widths 2..8 using simple orders: identity, reversed, and alternating such as [1,0] or [2,0,1]. Combine each with constant streams 0..28 via sub. Then 
15:47:39 [model] codex (proposer) calling...
15:48:05 [model] codex (proposer) ok 25.9s, tokens in/out 18177/1043, reply 3363 chars, model not reported (pin one with model = "..." in the models config)
```
**codex/19** (since 2026-11-04 15:49:14), latest log lines:
```
===== 2026-11-04 15:49:14 C:\Users\ihazp\liberprimus-search\.venv\Scripts\python.exe -m lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 19 --gen
note: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution
== LP2:33.jpg - 50.jpg/1  (91 symbols)
15:49:16 [model] claude-supervisor (supervisor) calling...
```
**local/19** (since 2026-11-04 15:47:48), latest log lines:
```
15:48:24 [model] gemma-local (proposer) ok 15.4s, tokens in/out 1667/479, reply 1443 chars
round 1 [qwen-local] proposals=8 valid=8 attempts=8 passes=0 near=0 invalid=0
round 1 [gemma-local] proposals=8 valid=8 attempts=58 passes=0 near=0 invalid=0
15:48:35 [model] qwen-local (proposer) calling...
15:48:59 [model] qwen-local (proposer) ok 23.7s, tokens in/out 2040/793, reply 2791 chars
15:48:59 [model] gemma-local (proposer) calling...
15:49:15 [model] gemma-local (proposer) ok 15.7s, tokens in/out 2123/499, reply 1562 chars
round 2 [qwen-local] proposals=8 valid=0 attempts=8 passes=0 near=0 invalid=8
round 2 [gemma-local] proposals=8 valid=6 attempts=64 passes=0 near=0 invalid=2
15:49:15 [model] qwen-local (proposer) calling...
```

## Results so far

- **tier-claude** (done)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.50 (3/6), 36316 attempts, 22 model calls, $0.0000
  - claude-sonnet: recall 0.33 (2/6), 19573 attempts, 23 model calls, $0.0000
- **sonnet/10** (done)
  - LP2:17.jpg, 18.jpg, 19.jpg - 0.jpg-2.jpg: 30378 attempts, 60 hypotheses, **0 final pass(es)**
- **sonnet/11** (done)
  - LP2:20.jpg/1 - 3.jpg/1: 38843 attempts, 53 hypotheses, **0 final pass(es)**
- **sonnet/12** (done)
  - LP2:20.jpg/2-23.jpg/1 - 3.jpg/2-6.jpg/1: 48263 attempts, 52 hypotheses, **0 final pass(es)**
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 57 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 58281 attempts, 88 hypotheses, **0 final pass(es)**
- **codex/22** (done)
  - LP2:57.jpg-66.jpg/1: 42190 attempts, 86 hypotheses, **0 final pass(es)**
- **codex/21** (done)
  - LP2:56.jpg/2: 19586 attempts, 82 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 2063 attempts, 70 hypotheses, **0 final pass(es)**
- **local/18** (done)
  - LP2:- - 44.jpg-49.jpg: 1145 attempts, 75 hypotheses, **0 final pass(es)**
- **local/16** (done)
  - LP2:15.jpg/2- - 32.jpg/2-39.jpg: 1352 attempts, 68 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 45 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 45 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 200 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 200 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 200 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 63 call(s) in the last 5h (cap 750), spent $0.0000

## Events

- 2026-11-04 15:42:01 4 running: codex/22, sonnet/11, codex/21, local/16
- 2026-11-04 15:42:01 sonnet/12 waiting: claude-plan in use by sonnet/11
- 2026-11-04 15:44:37 sonnet/11: done (exit 0, 4 min)
- 2026-11-04 15:44:52 published: 11 file(s) to branch results
- 2026-11-04 15:44:52 sonnet/12: start (uses claude-plan)
- 2026-11-04 15:44:52 4 running: codex/22, codex/21, local/16, sonnet/12
- 2026-11-04 15:46:07 codex/22: running 10 min | 15:43:57 [model] codex (proposer) ok 29.4s, tokens in/out 19200/917, reply 2885 chars, model not reported (pin one with model = "..." in the models config)
- 2026-11-04 15:46:07 codex/21: running 5 min | 15:46:03 [model] codex (proposer) ok 25.5s, tokens in/out 19191/1072, reply 3187 chars, model not reported (pin one with model = "..." in the models config)
- 2026-11-04 15:47:02 codex/21: done (exit 0, 6 min)
- 2026-11-04 15:47:18 published: 12 file(s) to branch results
- 2026-11-04 15:47:18 local/16: running 5 min | 15:47:12 [model] gemma-local (proposer) calling...
- 2026-11-04 15:47:18 codex/20: start (uses codex-plan)
- 2026-11-04 15:47:18 4 running: codex/22, local/16, sonnet/12, codex/20
- 2026-11-04 15:47:18 sonnet/13 waiting: claude-plan in use by sonnet/12
- 2026-11-04 15:47:33 local/16: done (exit 0, 6 min)
- 2026-11-04 15:47:48 published: 13 file(s) to branch results
- 2026-11-04 15:47:48 local/19: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 15:47:48 4 running: codex/22, sonnet/12, codex/20, local/19
- 2026-11-04 15:47:48 sonnet/13 waiting: claude-plan in use by sonnet/12
- 2026-11-04 15:48:59 codex/22: done (exit 0, 13 min)
- 2026-11-04 15:49:14 published: 14 file(s) to branch results
- 2026-11-04 15:49:14 codex/19: start (uses codex-plan)
- 2026-11-04 15:49:14 4 running: sonnet/12, codex/20, local/19, codex/19
- 2026-11-04 15:49:14 sonnet/13 waiting: claude-plan in use by sonnet/12
- 2026-11-04 15:49:24 sonnet/12: done (exit 0, 5 min)

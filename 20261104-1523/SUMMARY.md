# Overnight run 20261104-1523

Started 2026-11-04 15:23:11, updated 2026-11-04 15:54:12, status **running**. Jobs: pending 43, running 3, done 15

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 15:23:11 | 2026-11-04 15:37:17 | Claude Code proposers vs the random control |
| sonnet/10 | done | 2026-11-04 15:37:33 | 2026-11-04 15:41:04 | Sonnet, briefed by Opus |
| sonnet/11 | done | 2026-11-04 15:41:06 | 2026-11-04 15:44:37 | Sonnet, briefed by Opus |
| sonnet/12 | done | 2026-11-04 15:44:52 | 2026-11-04 15:49:24 | Sonnet, briefed by Opus |
| sonnet/13 | done | 2026-11-04 15:49:40 | 2026-11-04 15:51:10 | Sonnet, briefed by Opus |
| sonnet/14 | running | 2026-11-04 15:51:25 |  | Sonnet, briefed by Opus |
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
| codex/19 | done | 2026-11-04 15:49:14 | 2026-11-04 15:54:12 | Codex (exploratory) |
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
| local/19 | done | 2026-11-04 15:47:48 | 2026-11-04 15:52:15 | local models |
| local/15 | done | 2026-11-04 15:52:31 | 2026-11-04 15:52:36 | local models |
| local/20 | running | 2026-11-04 15:52:52 |  | local models |
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

**sonnet/14** (since 2026-11-04 15:51:25), latest log lines:
```
  | 5. Long repeating words. A flat IC is consistent with a long period.
  |    - Words: CIRCUMFERENCE, FIRFUMFERENFE, DIVINITY, LIBERPRIMUS, PARABLE, WISDOM, INSTAR, ENCRYPTION, CONSUMPTION.
  |    - Each with offset_range spanning the word length, all combines, and map reverse.
  |    - Add a variant with skip [0].
  | 6. Transposition followed by keying.
  |    - Undo columnar transpositions of widths 2 to 8, using identity order and reversed order (for example [1,0] and [2,1,0]).
  |    - After each one, apply direction 1 (ciphertext autokey) and direction 3 (prime totients).
  | 7.
15:51:46 [model] claude-sonnet (proposer) calling...
15:51:54 [model] claude-sonnet (proposer) ok 8.2s, tokens in/out 4152/1084, reply 2320 chars
```
**codex/20** (since 2026-11-04 15:47:18), latest log lines:
```
  | 5. Reversal variants. Set reverse_text true together with the best stream families above (prime_totients sub, ciphertext autokey). The section may be written backwards like other LP pages.
  | 6. Columnar transposition. Undo columnar with widths 2..8 using simple orders: identity, reversed, and alternating such as [1,0] or [2,0,1]. Combine each with constant streams 0..28 via sub. Then 
15:47:39 [model] codex (proposer) calling...
15:48:05 [model] codex (proposer) ok 25.9s, tokens in/out 18177/1043, reply 3363 chars, model not reported (pin one with model = "..." in the models config)
round 1 [codex] proposals=16 valid=16 attempts=18031 passes=0 near=0 invalid=0
15:52:37 [model] codex (proposer) calling...
15:52:59 [model] codex (proposer) ok 21.4s, tokens in/out 18526/860, reply 2881 chars, model not reported (pin one with model = "..." in the models config)
round 2 [codex] proposals=16 valid=16 attempts=24152 passes=0 near=0 invalid=0
15:53:03 [model] codex (proposer) calling...
15:53:34 [model] codex (proposer) ok 30.3s, tokens in/out 19210/1332, reply 4249 chars, model not reported (pin one with model = "..." in the models config)
```
**local/20** (since 2026-11-04 15:52:52), latest log lines:
```
== LP2:50.jpg/2-56.jpg/1  (1468 symbols)
15:52:53 [model] qwen-local (proposer) calling...
15:53:15 [model] qwen-local (proposer) ok 21.7s, tokens in/out 2400/699, reply 2478 chars
15:53:15 [model] gemma-local (proposer) calling...
15:53:31 [model] gemma-local (proposer) ok 16.3s, tokens in/out 2454/502, reply 1487 chars
round 1 [qwen-local] proposals=8 valid=5 attempts=5 passes=0 near=0 invalid=3
round 1 [gemma-local] proposals=8 valid=7 attempts=1020 passes=0 near=0 invalid=1
15:53:41 [model] qwen-local (proposer) calling...
15:54:02 [model] qwen-local (proposer) ok 21.5s, tokens in/out 2909/666, reply 2391 chars
15:54:02 [model] gemma-local (proposer) calling...
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
- **sonnet/13** (done)
  - LP2:6.jpg/2-7.jpg - 23.jpg/2-24.jpg: 22 attempts, 10 hypotheses, **0 final pass(es)**
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 57 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 58281 attempts, 88 hypotheses, **0 final pass(es)**
- **codex/22** (done)
  - LP2:57.jpg-66.jpg/1: 42190 attempts, 86 hypotheses, **0 final pass(es)**
- **codex/21** (done)
  - LP2:56.jpg/2: 19586 attempts, 82 hypotheses, **0 final pass(es)**
- **codex/19** (done)
  - LP2:33.jpg - 50.jpg/1: 60000 attempts, 67 hypotheses, **0 final pass(es)**, stopped: max_attempts (caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution)
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 2063 attempts, 70 hypotheses, **0 final pass(es)**
- **local/18** (done)
  - LP2:- - 44.jpg-49.jpg: 1145 attempts, 75 hypotheses, **0 final pass(es)**
- **local/16** (done)
  - LP2:15.jpg/2- - 32.jpg/2-39.jpg: 1352 attempts, 68 hypotheses, **0 final pass(es)**
- **local/19** (done)
  - LP2:33.jpg - 50.jpg/1: 4296 attempts, 67 hypotheses, **0 final pass(es)** (caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution)
- **local/15** (done)
  - skip LP2:15.jpg/1 - 32.jpg/1: only 9 symbols (minimum 20, --min-length); too short to judge

## Model usage

- qwen-local: 47 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 46 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 208 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 208 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 208 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 69 call(s) in the last 5h (cap 750), spent $0.0000

## Events

- 2026-11-04 15:47:48 sonnet/13 waiting: claude-plan in use by sonnet/12
- 2026-11-04 15:48:59 codex/22: done (exit 0, 13 min)
- 2026-11-04 15:49:14 published: 14 file(s) to branch results
- 2026-11-04 15:49:14 codex/19: start (uses codex-plan)
- 2026-11-04 15:49:14 4 running: sonnet/12, codex/20, local/19, codex/19
- 2026-11-04 15:49:14 sonnet/13 waiting: claude-plan in use by sonnet/12
- 2026-11-04 15:49:24 sonnet/12: done (exit 0, 5 min)
- 2026-11-04 15:49:40 published: 15 file(s) to branch results
- 2026-11-04 15:49:40 sonnet/13: start (uses claude-plan)
- 2026-11-04 15:49:40 4 running: codex/20, local/19, codex/19, sonnet/13
- 2026-11-04 15:51:10 sonnet/13: done (exit 0, 2 min)
- 2026-11-04 15:51:25 published: 16 file(s) to branch results
- 2026-11-04 15:51:25 sonnet/14: start (uses claude-plan)
- 2026-11-04 15:51:25 4 running: codex/20, local/19, codex/19, sonnet/14
- 2026-11-04 15:52:15 local/19: done (exit 0, 4 min)
- 2026-11-04 15:52:31 published: 17 file(s) to branch results
- 2026-11-04 15:52:31 local/15: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 15:52:31 4 running: codex/20, codex/19, sonnet/14, local/15
- 2026-11-04 15:52:31 sonnet/15 waiting: claude-plan in use by sonnet/14
- 2026-11-04 15:52:36 codex/20: running 5 min | 15:48:05 [model] codex (proposer) ok 25.9s, tokens in/out 18177/1043, reply 3363 chars, model not reported (pin one with model = "..." in the models config)
- 2026-11-04 15:52:36 local/15: done (exit 0, 0 min)
- 2026-11-04 15:52:51 published: 17 file(s) to branch results
- 2026-11-04 15:52:52 local/20: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 15:52:52 4 running: codex/20, codex/19, sonnet/14, local/20
- 2026-11-04 15:54:12 codex/19: done (exit 0, 5 min)

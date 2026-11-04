# Overnight run 20261104-1523

Started 2026-11-04 15:23:11, updated 2026-11-04 15:47:02, status **running**. Jobs: pending 50, running 3, done 8

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 15:23:11 | 2026-11-04 15:37:17 | Claude Code proposers vs the random control |
| sonnet/10 | done | 2026-11-04 15:37:33 | 2026-11-04 15:41:04 | Sonnet, briefed by Opus |
| sonnet/11 | done | 2026-11-04 15:41:06 | 2026-11-04 15:44:37 | Sonnet, briefed by Opus |
| sonnet/12 | running | 2026-11-04 15:44:52 |  | Sonnet, briefed by Opus |
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
| codex/22 | running | 2026-11-04 15:36:02 |  | Codex (exploratory) |
| codex/21 | done | 2026-11-04 15:41:06 | 2026-11-04 15:47:02 | Codex (exploratory) |
| codex/20 | pending |  |  | Codex (exploratory) |
| codex/19 | pending |  |  | Codex (exploratory) |
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
| local/16 | running | 2026-11-04 15:42:01 |  | local models |
| local/19 | pending |  |  | local models |
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

**sonnet/12** (since 2026-11-04 15:44:52), latest log lines:
```
  | 5. Reversed reading. Set reverse_text true and rerun the best stream families from 1 and 3 (prime_totients and primes, offset_range [0,2000], sub).
  | 6. Transposition combined with substitution. Try columnar orders of width 2 to 7, simple permutations such as [1,0], [2,0,1] and [0,2,1,3]. Combine each with a prime_totients sub stream or an auto
15:45:11 [model] claude-sonnet (proposer) calling...
15:45:19 [model] claude-sonnet (proposer) ok 8.7s, tokens in/out 4195/1080, reply 2381 chars
round 1 [claude-sonnet] proposals=12 valid=4 attempts=4 passes=0 near=0 invalid=8
15:45:29 [model] claude-sonnet (proposer) calling...
15:45:42 [model] claude-sonnet (proposer) ok 12.7s, tokens in/out 5126/1058, reply 2311 chars
round 2 [claude-sonnet] proposals=12 valid=3 attempts=7 passes=0 near=0 invalid=17
15:45:42 [model] claude-sonnet (proposer) calling...
15:45:54 [model] claude-sonnet (proposer) ok 11.8s, tokens in/out 5460/1202, reply 2525 chars
```
**codex/22** (since 2026-11-04 15:36:02), latest log lines:
```
15:42:55 [model] codex (proposer) ok 21.6s, tokens in/out 19527/857, reply 2916 chars, model not reported (pin one with model = "..." in the models config)
round 3 [codex] proposals=16 valid=16 attempts=22129 passes=0 near=0 invalid=0
15:43:00 [model] codex (proposer) calling...
15:43:24 [model] codex (proposer) ok 24.1s, tokens in/out 19683/980, reply 2757 chars, model not reported (pin one with model = "..." in the models config)
round 4 [codex] proposals=16 valid=16 attempts=28222 passes=0 near=0 invalid=0
15:43:28 [model] codex (proposer) calling...
15:43:57 [model] codex (proposer) ok 29.4s, tokens in/out 19200/917, reply 2885 chars, model not reported (pin one with model = "..." in the models config)
round 5 [codex] proposals=16 valid=16 attempts=38178 passes=0 near=0 invalid=0
15:46:12 [model] codex (proposer) calling...
15:46:38 [model] codex (proposer) ok 25.4s, tokens in/out 19298/1081, reply 2972 chars, model not reported (pin one with model = "..." in the models config)
```
**local/16** (since 2026-11-04 15:42:01), latest log lines:
```
15:46:06 [model] gemma-local (proposer) ok 17.3s, tokens in/out 3652/537, reply 1570 chars
round 4 [qwen-local] proposals=8 valid=7 attempts=455 passes=0 near=0 invalid=16
round 4 [gemma-local] proposals=8 valid=7 attempts=91 passes=0 near=0 invalid=6
15:46:06 [model] qwen-local (proposer) calling...
15:46:29 [model] qwen-local (proposer) ok 22.8s, tokens in/out 3899/686, reply 2548 chars
15:46:29 [model] gemma-local (proposer) calling...
15:46:46 [model] gemma-local (proposer) ok 16.9s, tokens in/out 3905/513, reply 1501 chars
round 5 [qwen-local] proposals=8 valid=8 attempts=691 passes=0 near=0 invalid=16
round 5 [gemma-local] proposals=8 valid=6 attempts=302 passes=0 near=0 invalid=8
15:46:46 [model] qwen-local (proposer) calling...
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
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 57 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 58281 attempts, 88 hypotheses, **0 final pass(es)**
- **codex/21** (done)
  - LP2:56.jpg/2: 19586 attempts, 82 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 2063 attempts, 70 hypotheses, **0 final pass(es)**
- **local/18** (done)
  - LP2:- - 44.jpg-49.jpg: 1145 attempts, 75 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 44 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 45 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 201 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 201 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 201 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 66 call(s) in the last 5h (cap 750), spent $0.0000

## Events

- 2026-11-04 15:37:33 sonnet/10: start (uses claude-plan)
- 2026-11-04 15:37:33 4 running: codex/24, local/18, codex/22, sonnet/10
- 2026-11-04 15:38:18 codex/24: running 15 min | 15:37:50 [model] codex (proposer) calling...
- 2026-11-04 15:40:48 codex/24: done (exit 0, 18 min)
- 2026-11-04 15:41:04 published: 8 file(s) to branch results
- 2026-11-04 15:41:04 codex/22: running 5 min | 15:40:21 [model] codex (proposer) ok 25.7s, tokens in/out 18360/1036, reply 2966 chars, model not reported (pin one with model = "..." in the models config)
- 2026-11-04 15:41:04 sonnet/10: done (exit 0, 4 min)
- 2026-11-04 15:41:06 published: 9 file(s) to branch results
- 2026-11-04 15:41:06 sonnet/11: start (uses claude-plan)
- 2026-11-04 15:41:06 3 running: local/18, codex/22, sonnet/11
- 2026-11-04 15:41:06 codex/21: start (uses codex-plan)
- 2026-11-04 15:41:06 4 running: local/18, codex/22, sonnet/11, codex/21
- 2026-11-04 15:41:06 sonnet/12 waiting: claude-plan in use by sonnet/11
- 2026-11-04 15:41:46 local/18: done (exit 0, 10 min)
- 2026-11-04 15:42:01 published: 10 file(s) to branch results
- 2026-11-04 15:42:01 local/16: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 15:42:01 4 running: codex/22, sonnet/11, codex/21, local/16
- 2026-11-04 15:42:01 sonnet/12 waiting: claude-plan in use by sonnet/11
- 2026-11-04 15:44:37 sonnet/11: done (exit 0, 4 min)
- 2026-11-04 15:44:52 published: 11 file(s) to branch results
- 2026-11-04 15:44:52 sonnet/12: start (uses claude-plan)
- 2026-11-04 15:44:52 4 running: codex/22, codex/21, local/16, sonnet/12
- 2026-11-04 15:46:07 codex/22: running 10 min | 15:43:57 [model] codex (proposer) ok 29.4s, tokens in/out 19200/917, reply 2885 chars, model not reported (pin one with model = "..." in the models config)
- 2026-11-04 15:46:07 codex/21: running 5 min | 15:46:03 [model] codex (proposer) ok 25.5s, tokens in/out 19191/1072, reply 3187 chars, model not reported (pin one with model = "..." in the models config)
- 2026-11-04 15:47:02 codex/21: done (exit 0, 6 min)

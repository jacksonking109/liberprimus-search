# Overnight run 20261104-1523

Started 2026-11-04 15:23:11, updated 2026-11-04 15:47:33, status **running**. Jobs: pending 49, running 3, done 9

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
| codex/20 | running | 2026-11-04 15:47:18 |  | Codex (exploratory) |
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
| local/16 | done | 2026-11-04 15:42:01 | 2026-11-04 15:47:33 | local models |
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
15:45:29 [model] claude-sonnet (proposer) calling...
15:45:42 [model] claude-sonnet (proposer) ok 12.7s, tokens in/out 5126/1058, reply 2311 chars
round 2 [claude-sonnet] proposals=12 valid=3 attempts=7 passes=0 near=0 invalid=17
15:45:42 [model] claude-sonnet (proposer) calling...
15:45:54 [model] claude-sonnet (proposer) ok 11.8s, tokens in/out 5460/1202, reply 2525 chars
round 3 [claude-sonnet] proposals=12 valid=12 attempts=16024 passes=0 near=0 invalid=17
15:47:14 [model] claude-sonnet (proposer) calling...
15:47:27 [model] claude-sonnet (proposer) ok 13.0s, tokens in/out 6340/1634, reply 2516 chars
round 4 [claude-sonnet] proposals=12 valid=12 attempts=26128 passes=0 near=0 invalid=17
15:47:32 [model] claude-sonnet (proposer) calling...
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
**codex/20** (since 2026-11-04 15:47:18), latest log lines:
```
===== 2026-11-04 15:47:18 C:\Users\ihazp\liberprimus-search\.venv\Scripts\python.exe -m lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 20 --gen
== LP2:50.jpg/2-56.jpg/1  (1468 symbols)
15:47:19 [model] claude-supervisor (supervisor) calling...
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
- **local/16** (done)
  - LP2:15.jpg/2- - 32.jpg/2-39.jpg: 1352 attempts, 68 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 45 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 45 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 200 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 200 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 200 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 64 call(s) in the last 5h (cap 750), spent $0.0000

## Events

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
- 2026-11-04 15:47:18 published: 12 file(s) to branch results
- 2026-11-04 15:47:18 local/16: running 5 min | 15:47:12 [model] gemma-local (proposer) calling...
- 2026-11-04 15:47:18 codex/20: start (uses codex-plan)
- 2026-11-04 15:47:18 4 running: codex/22, local/16, sonnet/12, codex/20
- 2026-11-04 15:47:18 sonnet/13 waiting: claude-plan in use by sonnet/12
- 2026-11-04 15:47:33 local/16: done (exit 0, 6 min)

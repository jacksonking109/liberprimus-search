# Overnight run 20261104-1523

Started 2026-11-04 15:23:11, updated 2026-11-04 15:35:47, status **running**. Jobs: pending 56, running 3, done 2

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | running | 2026-11-04 15:23:11 |  | Claude Code proposers vs the random control |
| sonnet/10 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/11 | pending |  |  | Sonnet, briefed by Opus |
| sonnet/12 | pending |  |  | Sonnet, briefed by Opus |
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
| codex/24 | running | 2026-11-04 15:23:11 |  | Codex (exploratory) |
| codex/22 | pending |  |  | Codex (exploratory) |
| codex/21 | pending |  |  | Codex (exploratory) |
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
| local/18 | running | 2026-11-04 15:31:51 |  | local models |
| local/16 | pending |  |  | local models |
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

**tier-claude** (since 2026-11-04 15:23:11), latest log lines:
```
15:34:24 [model] claude-sonnet (proposer) calling...
15:34:36 [model] claude-sonnet (proposer) ok 12.0s, tokens in/out 2712/1243, reply 2200 chars
[claude-sonnet] 4/6 L=160 recovered=1 attempts=157 calls=1 usd=0.0000 stopped=pass_found
15:34:49 [model] claude-sonnet (proposer) calling...
15:35:02 [model] claude-sonnet (proposer) ok 12.6s, tokens in/out 2703/1145, reply 2485 chars
15:35:15 [model] claude-sonnet (proposer) calling...
15:35:26 [model] claude-sonnet (proposer) ok 10.5s, tokens in/out 3496/1179, reply 2531 chars
15:35:27 [model] claude-sonnet (proposer) calling...
15:35:36 [model] claude-sonnet (proposer) ok 8.9s, tokens in/out 4283/1144, reply 2492 chars
15:35:37 [model] claude-sonnet (proposer) calling...
```
**codex/24** (since 2026-11-04 15:23:11), latest log lines:
```
15:23:27 [model] codex (proposer) calling...
15:23:52 [model] codex (proposer) ok 24.9s, tokens in/out 18177/1045, reply 3336 chars, model not reported (pin one with model = "..." in the models config)
round 1 [codex] proposals=16 valid=16 attempts=26003 passes=0 near=0 invalid=0
15:28:40 [model] codex (proposer) calling...
15:29:07 [model] codex (proposer) ok 27.3s, tokens in/out 19054/1014, reply 2976 chars, model not reported (pin one with model = "..." in the models config)
round 2 [codex] proposals=16 valid=16 attempts=32113 passes=0 near=0 invalid=0
15:33:14 [model] codex (proposer) calling...
15:33:37 [model] codex (proposer) ok 23.0s, tokens in/out 19716/957, reply 3002 chars, model not reported (pin one with model = "..." in the models config)
round 3 [codex] proposals=16 valid=16 attempts=42152 passes=0 near=0 invalid=0
15:35:32 [model] codex (proposer) calling...
```
**local/18** (since 2026-11-04 15:31:51), latest log lines:
```
15:32:34 [model] gemma-local (proposer) ok 16.4s, tokens in/out 2452/447, reply 1336 chars
round 1 [qwen-local] proposals=8 valid=7 attempts=7 passes=0 near=0 invalid=1
round 1 [gemma-local] proposals=8 valid=7 attempts=57 passes=0 near=0 invalid=1
15:33:23 [model] qwen-local (proposer) calling...
15:33:47 [model] qwen-local (proposer) ok 24.1s, tokens in/out 2843/688, reply 2542 chars
15:33:47 [model] gemma-local (proposer) calling...
15:34:16 [model] gemma-local (proposer) ok 29.1s, tokens in/out 2903/518, reply 1520 chars
round 2 [qwen-local] proposals=8 valid=8 attempts=77 passes=0 near=0 invalid=1
round 2 [gemma-local] proposals=8 valid=6 attempts=66 passes=0 near=0 invalid=3
15:35:37 [model] qwen-local (proposer) calling...
```

## Results so far

- **tier-claude** (running)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.50 (3/6), 36316 attempts, 22 model calls, $0.0000
  - claude-sonnet: recall 0.50 (2/4), 10241 attempts, 13 model calls, $0.0000
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 57 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 2063 attempts, 70 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 44 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 44 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 187 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 187 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 187 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 59 call(s) in the last 5h (cap 750), spent $0.0000

## Events

- 2026-11-04 15:23:11 started
- 2026-11-04 15:23:11 tier-claude: start (uses claude-plan)
- 2026-11-04 15:23:11 codex/25: start (uses codex-plan)
- 2026-11-04 15:23:11 2 running: tier-claude, codex/25
- 2026-11-04 15:23:11 codex/24: start (uses codex-plan)
- 2026-11-04 15:23:11 3 running: tier-claude, codex/25, codex/24
- 2026-11-04 15:23:11 local/17: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 15:23:11 4 running: tier-claude, codex/25, codex/24, local/17
- 2026-11-04 15:23:11 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 15:28:15 tier-claude: running 5 min | 15:27:33 [model] claude-opus (proposer) calling...
- 2026-11-04 15:28:15 codex/25: running 5 min | 15:28:05 [model] codex (proposer) calling...
- 2026-11-04 15:28:15 codex/24: running 5 min | 15:23:52 [model] codex (proposer) ok 24.9s, tokens in/out 18177/1045, reply 3336 chars, model not reported (pin one with model = "..." in the models config)
- 2026-11-04 15:28:15 local/17: running 5 min | 15:28:12 [model] gemma-local (proposer) calling...
- 2026-11-04 15:31:35 local/17: done (exit 0, 8 min)
- 2026-11-04 15:31:51 published: 6 file(s) to branch results
- 2026-11-04 15:31:51 local/18: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 15:31:51 4 running: tier-claude, codex/25, codex/24, local/18
- 2026-11-04 15:31:51 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 15:33:16 tier-claude: running 10 min | 15:33:13 [model] claude-sonnet (proposer) ok 14.9s, tokens in/out 3366/1576, reply 2313 chars
- 2026-11-04 15:33:16 codex/25: running 10 min | 15:31:58 [model] codex (proposer) ok 27.2s, tokens in/out 19980/1090, reply 3277 chars, model not reported (pin one with model = "..." in the models config)
- 2026-11-04 15:33:16 codex/24: running 10 min | 15:33:14 [model] codex (proposer) calling...
- 2026-11-04 15:35:47 codex/25: done (exit 0, 13 min)

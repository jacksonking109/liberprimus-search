# Overnight run 20261103-2310

Started 2026-11-03 23:10:06, updated 2026-11-03 23:21:04, status **running**. Jobs: pending 56, running 2, done 3

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | running | 2026-11-03 23:10:06 |  | Claude Code proposers vs the random control |
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
| codex/25 | done | 2026-11-03 23:10:06 | 2026-11-03 23:15:43 | Codex (exploratory) |
| codex/24 | done | 2026-11-03 23:15:59 | 2026-11-03 23:21:04 | Codex (exploratory) |
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
| local/17 | done | 2026-11-03 23:10:06 | 2026-11-03 23:14:52 | local models |
| local/18 | running | 2026-11-03 23:15:08 |  | local models |
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

**tier-claude** (since 2026-11-03 23:10:06), latest log lines:
```
23:20:08 [model] claude-sonnet (proposer) calling...
23:20:15 [model] claude-sonnet (proposer) ok 6.4s, tokens in/out 4202/772, reply 1722 chars
23:20:16 [model] claude-sonnet (proposer) calling...
23:20:23 [model] claude-sonnet (proposer) ok 7.1s, tokens in/out 4757/815, reply 1754 chars
[claude-sonnet] 2/6 L=80 recovered=0 attempts=6543 calls=5 usd=0.0000
23:20:32 [model] claude-sonnet (proposer) calling...
23:20:46 [model] claude-sonnet (proposer) ok 13.2s, tokens in/out 2456/1576, reply 2079 chars
23:20:46 [model] claude-sonnet (proposer) calling...
23:20:57 [model] claude-sonnet (proposer) ok 11.3s, tokens in/out 3109/1300, reply 1746 chars
23:20:58 [model] claude-sonnet (proposer) calling...
```
**local/18** (since 2026-11-03 23:15:08), latest log lines:
```
23:18:37 [model] qwen-local (proposer) calling...
23:19:01 [model] qwen-local (proposer) ok 23.9s, tokens in/out 3395/618, reply 2103 chars
23:19:01 [model] gemma-local (proposer) calling...
23:19:19 [model] gemma-local (proposer) ok 17.8s, tokens in/out 3471/456, reply 1398 chars
round 5 [qwen-local] proposals=8 valid=8 attempts=87 passes=0 near=0 invalid=0
round 5 [gemma-local] proposals=8 valid=8 attempts=173 passes=0 near=0 invalid=0
23:20:10 [model] qwen-local (proposer) calling...
23:20:32 [model] qwen-local (proposer) ok 21.6s, tokens in/out 3541/565, reply 1799 chars
23:20:32 [model] gemma-local (proposer) calling...
23:20:49 [model] gemma-local (proposer) ok 17.2s, tokens in/out 3622/456, reply 1355 chars
```

## Results so far

- **tier-claude** (running)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 73695 attempts, 23 model calls, $0.0000
  - claude-sonnet: recall 0.00 (0/2), 10228 attempts, 10 model calls, $0.0000
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 29964 attempts, 47 hypotheses, **0 final pass(es)**
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 26431 attempts, 47 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 190 attempts, 81 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 52 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 52 call(s) in the last 5h (cap none), spent $0.0000
- granite: 2 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 101 call(s) in the last 5h (cap 120), spent $0.0000
- claude-sonnet: 101 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 101 call(s) in the last 5h (cap 200), spent $0.0000
- codex: 51 call(s) in the last 5h (cap 750), spent $0.0000
- dry: 2 call(s) in the last 5h (cap none), spent $0.0000

## Events

- 2026-11-03 23:10:06 started
- 2026-11-03 23:10:06 tier-claude: start (uses claude-plan)
- 2026-11-03 23:10:06 codex/25: start (uses codex-plan)
- 2026-11-03 23:10:06 2 running: tier-claude, codex/25
- 2026-11-03 23:10:06 local/17: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-03 23:10:06 3 running: tier-claude, codex/25, local/17
- 2026-11-03 23:10:06 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-03 23:14:52 local/17: done (exit 0, 5 min)
- 2026-11-03 23:15:08 published: 6 file(s) to branch results
- 2026-11-03 23:15:08 local/18: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-03 23:15:08 3 running: tier-claude, codex/25, local/18
- 2026-11-03 23:15:08 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-03 23:15:13 tier-claude: running 5 min | 23:14:42 [model] claude-opus (proposer) calling...
- 2026-11-03 23:15:13 codex/25: running 5 min | 23:14:59 [model] codex (proposer) ok 12.2s, tokens in/out 18433/463, reply 1674 chars
- 2026-11-03 23:15:43 codex/25: done (exit 0, 6 min)
- 2026-11-03 23:15:59 published: 7 file(s) to branch results
- 2026-11-03 23:15:59 codex/24: start (uses codex-plan)
- 2026-11-03 23:15:59 3 running: tier-claude, local/18, codex/24
- 2026-11-03 23:15:59 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-03 23:20:09 local/18: running 5 min | 23:19:19 [model] gemma-local (proposer) ok 17.8s, tokens in/out 3471/456, reply 1398 chars
- 2026-11-03 23:20:14 tier-claude: running 10 min | 23:20:08 [model] claude-sonnet (proposer) calling...
- 2026-11-03 23:20:59 codex/24: running 5 min | 23:20:40 [model] codex (proposer) calling...
- 2026-11-03 23:21:04 codex/24: done (exit 0, 5 min)

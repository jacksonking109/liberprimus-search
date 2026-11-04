# Overnight run 20261104-0949

Started 2026-11-04 09:49:00, updated 2026-11-04 10:02:45, status **running**. Jobs: pending 56, running 2, done 3

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | running | 2026-11-04 09:49:00 |  | Claude Code proposers vs the random control |
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
| codex/25 | done | 2026-11-04 09:49:00 | 2026-11-04 09:56:14 | Codex (exploratory) |
| codex/24 | done | 2026-11-04 09:56:29 | 2026-11-04 10:02:45 | Codex (exploratory) |
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
| local/17 | done | 2026-11-04 09:49:00 | 2026-11-04 09:55:18 | local models |
| local/18 | running | 2026-11-04 09:55:34 |  | local models |
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

**tier-claude** (since 2026-11-04 09:49:00), latest log lines:
```
10:01:10 [model] claude-sonnet (proposer) ok 14.9s, tokens in/out 4032/1484, reply 1760 chars
10:01:11 [model] claude-sonnet (proposer) calling...
10:01:29 [model] claude-sonnet (proposer) ok 18.2s, tokens in/out 4506/1889, reply 1556 chars
[claude-sonnet] 3/6 L=80 recovered=0 attempts=2451 calls=5 usd=0.0000
10:01:40 [model] claude-sonnet (proposer) calling...
10:01:55 [model] claude-sonnet (proposer) ok 15.1s, tokens in/out 2713/1441, reply 1770 chars
[claude-sonnet] 4/6 L=160 recovered=1 attempts=7 calls=1 usd=0.0000 stopped=pass_found
10:02:13 [model] claude-sonnet (proposer) calling...
10:02:20 [model] claude-sonnet (proposer) ok 7.0s, tokens in/out 2704/751, reply 1638 chars
10:02:39 [model] claude-sonnet (proposer) calling...
```
**local/18** (since 2026-11-04 09:55:34), latest log lines:
```
09:59:35 [model] qwen-local (proposer) calling...
09:59:56 [model] qwen-local (proposer) ok 21.7s, tokens in/out 3276/667, reply 2439 chars
09:59:56 [model] gemma-local (proposer) calling...
10:00:12 [model] gemma-local (proposer) ok 15.3s, tokens in/out 3451/443, reply 1333 chars
round 4 [qwen-local] proposals=8 valid=8 attempts=113 passes=0 near=0 invalid=0
round 4 [gemma-local] proposals=8 valid=7 attempts=57 passes=0 near=0 invalid=3
10:01:55 [model] qwen-local (proposer) calling...
10:02:16 [model] qwen-local (proposer) ok 21.5s, tokens in/out 3416/658, reply 2271 chars
10:02:16 [model] gemma-local (proposer) calling...
10:02:31 [model] gemma-local (proposer) ok 14.9s, tokens in/out 3621/418, reply 1257 chars
```

## Results so far

- **tier-claude** (running)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 39128 attempts, 22 model calls, $0.0000
  - claude-sonnet: recall 0.50 (2/4), 5709 attempts, 12 model calls, $0.0000
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 30269 attempts, 47 hypotheses, **0 final pass(es)**
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 22296 attempts, 41 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 298 attempts, 82 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 11 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 11 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 36 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 36 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 36 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 12 call(s) in the last 5h (cap 750), spent $0.0000

## Events

- 2026-11-04 09:49:00 started
- 2026-11-04 09:49:00 tier-claude: start (uses claude-plan)
- 2026-11-04 09:49:00 codex/25: start (uses codex-plan)
- 2026-11-04 09:49:00 2 running: tier-claude, codex/25
- 2026-11-04 09:49:00 local/17: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 09:49:00 3 running: tier-claude, codex/25, local/17
- 2026-11-04 09:49:00 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 09:54:03 tier-claude: running 5 min | 09:53:37 [model] claude-opus (proposer) calling...
- 2026-11-04 09:54:03 codex/25: running 5 min | 09:53:45 [model] codex (proposer) ok 15.9s, tokens in/out 19304/478, reply 1648 chars
- 2026-11-04 09:54:03 local/17: running 5 min | 09:54:01 [model] gemma-local (proposer) calling...
- 2026-11-04 09:55:18 local/17: done (exit 0, 6 min)
- 2026-11-04 09:55:34 published: 6 file(s) to branch results
- 2026-11-04 09:55:34 local/18: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 09:55:34 3 running: tier-claude, codex/25, local/18
- 2026-11-04 09:55:34 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 09:56:14 codex/25: done (exit 0, 7 min)
- 2026-11-04 09:56:29 published: 7 file(s) to branch results
- 2026-11-04 09:56:29 codex/24: start (uses codex-plan)
- 2026-11-04 09:56:30 3 running: tier-claude, local/18, codex/24
- 2026-11-04 09:56:30 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 09:59:05 tier-claude: running 10 min | 09:58:51 [model] claude-sonnet (proposer) calling...
- 2026-11-04 10:00:35 local/18: running 5 min | 10:00:12 [model] gemma-local (proposer) ok 15.3s, tokens in/out 3451/443, reply 1333 chars
- 2026-11-04 10:01:30 codex/24: running 5 min | 10:01:27 [model] codex (proposer) ok 22.4s, tokens in/out 18854/431, reply 1595 chars
- 2026-11-04 10:02:45 codex/24: done (exit 0, 6 min)

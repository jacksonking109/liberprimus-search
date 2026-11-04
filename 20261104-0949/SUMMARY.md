# Overnight run 20261104-0949

Started 2026-11-04 09:49:00, updated 2026-11-04 09:55:18, status **running**. Jobs: pending 58, running 2, done 1

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
| codex/25 | running | 2026-11-04 09:49:00 |  | Codex (exploratory) |
| codex/24 | pending |  |  | Codex (exploratory) |
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
| local/18 | pending |  |  | local models |
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
[claude-opus] 2/6 L=80 recovered=0 attempts=6480 calls=5 usd=0.0000
09:50:49 [model] claude-opus (proposer) calling...
09:51:36 [model] claude-opus (proposer) ok 46.5s, tokens in/out 2393/4314, reply 1389 chars
09:51:36 [model] claude-opus (proposer) calling...
09:52:19 [model] claude-opus (proposer) ok 42.8s, tokens in/out 2777/3100, reply 1320 chars
09:52:19 [model] claude-opus (proposer) calling...
09:53:37 [model] claude-opus (proposer) ok 77.8s, tokens in/out 3116/6112, reply 1527 chars
09:53:37 [model] claude-opus (proposer) calling...
09:54:47 [model] claude-opus (proposer) ok 70.4s, tokens in/out 3433/6540, reply 1627 chars
09:54:49 [model] claude-opus (proposer) calling...
```
**codex/25** (since 2026-11-04 09:49:00), latest log lines:
```
09:51:17 [model] codex (proposer) ok 22.9s, tokens in/out 18040/461, reply 1653 chars
round 2 [codex] proposals=8 valid=8 attempts=10113 passes=0 near=1 invalid=0
09:51:49 [model] codex (proposer) calling...
09:52:04 [model] codex (proposer) ok 14.2s, tokens in/out 18476/402, reply 1516 chars
round 3 [codex] proposals=8 valid=8 attempts=12186 passes=0 near=1 invalid=0
09:52:05 [model] codex (proposer) calling...
09:52:24 [model] codex (proposer) ok 19.4s, tokens in/out 18895/509, reply 1654 chars
round 4 [codex] proposals=8 valid=8 attempts=18210 passes=0 near=3 invalid=0
09:53:29 [model] codex (proposer) calling...
09:53:45 [model] codex (proposer) ok 15.9s, tokens in/out 19304/478, reply 1648 chars
```

## Results so far

- **tier-claude** (running)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.50 (1/2), 6512 attempts, 6 model calls, $0.0000
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 298 attempts, 82 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 6 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 6 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 11 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 11 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 11 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 5 call(s) in the last 5h (cap 750), spent $0.0000

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

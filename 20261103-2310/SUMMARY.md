# Overnight run 20261103-2310

Started 2026-11-03 23:10:06, updated 2026-11-03 23:15:43, status **running**. Jobs: pending 57, running 2, done 2

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
23:13:11 [model] claude-opus (proposer) calling...
23:13:21 [model] claude-opus (proposer) ok 10.4s, tokens in/out 4493/860, reply 1475 chars
[claude-opus] 2/6 L=80 recovered=0 attempts=16160 calls=5 usd=0.0000
23:13:22 [model] claude-opus (proposer) calling...
23:13:45 [model] claude-opus (proposer) ok 23.8s, tokens in/out 2392/1767, reply 1291 chars
23:13:46 [model] claude-opus (proposer) calling...
23:14:42 [model] claude-opus (proposer) ok 56.2s, tokens in/out 2789/4805, reply 1591 chars
23:14:42 [model] claude-opus (proposer) calling...
23:15:30 [model] claude-opus (proposer) ok 48.4s, tokens in/out 3232/3518, reply 1683 chars
23:15:30 [model] claude-opus (proposer) calling...
```
**local/18** (since 2026-11-03 23:15:08), latest log lines:
```
===== 2026-11-03 23:15:08 C:\Users\ihazp\liberprimus-search\.venv\Scripts\python.exe -m lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 18 --gen
== LP2:- - 44.jpg-49.jpg  (1433 symbols)
23:15:10 [model] qwen-local (proposer) calling...
23:15:31 [model] qwen-local (proposer) ok 20.9s, tokens in/out 2329/599, reply 2229 chars
23:15:31 [model] gemma-local (proposer) calling...
```

## Results so far

- **tier-claude** (running)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.00 (0/2), 36160 attempts, 9 model calls, $0.0000
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 29964 attempts, 47 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 190 attempts, 81 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 47 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 46 call(s) in the last 5h (cap none), spent $0.0000
- granite: 2 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 78 call(s) in the last 5h (cap 120), spent $0.0000
- claude-sonnet: 78 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 78 call(s) in the last 5h (cap 200), spent $0.0000
- codex: 45 call(s) in the last 5h (cap 750), spent $0.0000
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

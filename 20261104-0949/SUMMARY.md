# Overnight run 20261104-0949

Started 2026-11-04 09:49:00, updated 2026-11-04 10:05:41, status **running**. Jobs: pending 54, running 2, done 5

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 09:49:00 | 2026-11-04 10:05:41 | Claude Code proposers vs the random control |
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
| codex/22 | running | 2026-11-04 10:03:06 |  | Codex (exploratory) |
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
| local/18 | done | 2026-11-04 09:55:34 | 2026-11-04 10:05:01 | local models |
| local/16 | running | 2026-11-04 10:05:16 |  | local models |
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

**codex/22** (since 2026-11-04 10:03:06), latest log lines:
```
===== 2026-11-04 10:03:06 C:\Users\ihazp\liberprimus-search\.venv\Scripts\python.exe -m lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 22 --gen
== LP2:57.jpg-66.jpg/1  (2474 symbols)
10:03:07 [model] codex (proposer) calling...
10:03:25 [model] codex (proposer) ok 17.8s, tokens in/out 17612/461, reply 1733 chars
```
**local/16** (since 2026-11-04 10:05:16), latest log lines:
```
===== 2026-11-04 10:05:16 C:\Users\ihazp\liberprimus-search\.venv\Scripts\python.exe -m lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 16 --gen
== LP2:15.jpg/2- - 32.jpg/2-39.jpg  (1894 symbols)
10:05:18 [model] qwen-local (proposer) calling...
10:05:37 [model] qwen-local (proposer) ok 18.9s, tokens in/out 2331/587, reply 2005 chars
10:05:37 [model] gemma-local (proposer) calling...
```

## Results so far

- **tier-claude** (done)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 39128 attempts, 22 model calls, $0.0000
  - claude-sonnet: recall 0.33 (2/6), 11672 attempts, 22 model calls, $0.0000
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 30269 attempts, 47 hypotheses, **0 final pass(es)**
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 22296 attempts, 41 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 298 attempts, 82 hypotheses, **0 final pass(es)**
- **local/18** (done)
  - LP2:- - 44.jpg-49.jpg: 217 attempts, 85 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 13 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 12 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 46 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 46 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 46 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 13 call(s) in the last 5h (cap 750), spent $0.0000

## Supervisor notes

- 2026-11-04 10:03:06: 10:03 check: the run is healthy at 3 of 59 jobs done. There are no final passes. Codex near misses on section 25 (primes/e_digits sub, margin about -0.23) are at noise level. The tier-claude benchmark so far: sonnet recall 0.50, opus 0.33, random control 0.00. The queue already covers every section, so no jobs were added.

## Events

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
- 2026-11-04 10:03:00 published: 8 file(s) to branch results
- 2026-11-04 10:03:06 supervisor: note: 10:03 check: the run is healthy at 3 of 59 jobs done. There are no final passes. Codex near misses on section 25 (primes/e_digits sub, margin about -0.23) are at noise level. The tier-claude benchmark so far: sonnet recall 0.50, opus 0.33, random control 0.00. The queue already covers every secti...
- 2026-11-04 10:03:06 codex/22: start (uses codex-plan)
- 2026-11-04 10:03:06 3 running: tier-claude, local/18, codex/22
- 2026-11-04 10:03:06 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 10:04:06 tier-claude: running 15 min | 10:04:05 [model] claude-sonnet (proposer) ok 9.6s, tokens in/out 5066/1088, reply 2344 chars
- 2026-11-04 10:05:01 local/18: done (exit 0, 9 min)
- 2026-11-04 10:05:16 published: 9 file(s) to branch results
- 2026-11-04 10:05:16 local/16: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 10:05:16 3 running: tier-claude, codex/22, local/16
- 2026-11-04 10:05:16 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 10:05:41 tier-claude: done (exit 0, 17 min)

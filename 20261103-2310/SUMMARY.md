# Overnight run 20261103-2310

Started 2026-11-03 23:10:06, updated 2026-11-03 23:32:05, status **running**. Jobs: pending 53, running 2, done 6

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-03 23:10:06 | 2026-11-03 23:27:44 | Claude Code proposers vs the random control |
| sonnet/10 | running | 2026-11-03 23:28:00 |  | Sonnet, briefed by Opus |
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
| codex/22 | running | 2026-11-03 23:21:38 |  | Codex (exploratory) |
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
| local/18 | done | 2026-11-03 23:15:08 | 2026-11-03 23:21:43 | local models |
| local/16 | done | 2026-11-03 23:21:59 | 2026-11-03 23:32:05 | local models |
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

**sonnet/10** (since 2026-11-03 23:28:00), latest log lines:
```
  | 4. Other running sequences. Try primes, pi_digits, e_digits, fibonacci, squares and triangular. Use combine sub and beaufort, offset_range [0, 1999], and scale 1 or -1 (expressed as scale 28). Run
  | 5. Periodic keywords. Use repeat with words "DIVINITY", "FIRFUMFERENFE", "CIRCUMFERENCE", "KOAN", "PRIMES" and "INSTAR". Use combine sub, then beaufort, with skip [0] in resolve mode and offset_ra
  | 6. Reversed reading. Take the best variants from 1 and 3 and add reverse_text true, since the page order is listed as 17-19 then 0-2.
  | 7. Transposition, as a fallback. Undo columnar orders of width 3 to 8, such as [1,0,2] or [2,0,3,1], before applying a ciphertext autokey. Only do this if 1 to 6 produce no near_miss.
  | Do NOT: propose constant streams or short nu
23:28:20 [model] claude-sonnet (proposer) calling...
23:28:27 [model] claude-sonnet (proposer) ok 7.2s, tokens in/out 4201/803, reply 1797 chars
round 1 [claude-sonnet] proposals=8 valid=8 attempts=6017 passes=0 near=0 invalid=0
23:31:37 [model] claude-sonnet (proposer) calling...
23:31:49 [model] claude-sonnet (proposer) ok 11.6s, tokens in/out 4780/1562, reply 2143 chars
```
**codex/22** (since 2026-11-03 23:21:38), latest log lines:
```
23:26:26 [model] codex (proposer) ok 29.1s, tokens in/out 17431/502, reply 1579 chars
round 2 [codex] proposals=8 valid=8 attempts=10262 passes=0 near=0 invalid=0
23:26:31 [model] codex (proposer) calling...
23:26:44 [model] codex (proposer) ok 12.5s, tokens in/out 17249/464, reply 1470 chars
round 3 [codex] proposals=8 valid=8 attempts=14296 passes=0 near=0 invalid=0
23:26:45 [model] codex (proposer) calling...
23:26:58 [model] codex (proposer) ok 12.7s, tokens in/out 18177/448, reply 1645 chars
round 4 [codex] proposals=8 valid=8 attempts=18475 passes=0 near=1 invalid=0
23:30:38 [model] codex (proposer) calling...
23:31:07 [model] codex (proposer) ok 28.9s, tokens in/out 18488/483, reply 1531 chars
```

## Results so far

- **tier-claude** (done)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 73695 attempts, 23 model calls, $0.0000
  - claude-sonnet: recall 0.17 (1/6), 23024 attempts, 26 model calls, $0.0000
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 29964 attempts, 47 hypotheses, **0 final pass(es)**
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 26431 attempts, 47 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 190 attempts, 81 hypotheses, **0 final pass(es)**
- **local/18** (done)
  - LP2:- - 44.jpg-49.jpg: 284 attempts, 91 hypotheses, **0 final pass(es)**
- **local/16** (done)
  - LP2:15.jpg/2- - 32.jpg/2-39.jpg: 211 attempts, 89 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 58 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 58 call(s) in the last 5h (cap none), spent $0.0000
- granite: 2 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 119 call(s) in the last 5h (cap 120), spent $0.0000
- claude-sonnet: 119 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 119 call(s) in the last 5h (cap 200), spent $0.0000
- codex: 56 call(s) in the last 5h (cap 750), spent $0.0000
- dry: 2 call(s) in the last 5h (cap none), spent $0.0000

## Supervisor notes

- 2026-11-03 23:21:38: 23:21 check: run healthy, 2 running, 56 pending, no failures. No FINAL leads yet; best is codex/25 (section 54-55..71-72), with near misses at margins -0.23 to -0.29 (sub/add with a primes stream, pi_digits). Watch claude-opus quota: 101 of 120 calls in the last 5h, so it may hit its cap during tier-claude. No jobs added; the queue already covers every section.

## Events

- 2026-11-03 23:15:59 3 running: tier-claude, local/18, codex/24
- 2026-11-03 23:15:59 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-03 23:20:09 local/18: running 5 min | 23:19:19 [model] gemma-local (proposer) ok 17.8s, tokens in/out 3471/456, reply 1398 chars
- 2026-11-03 23:20:14 tier-claude: running 10 min | 23:20:08 [model] claude-sonnet (proposer) calling...
- 2026-11-03 23:20:59 codex/24: running 5 min | 23:20:40 [model] codex (proposer) calling...
- 2026-11-03 23:21:04 codex/24: done (exit 0, 5 min)
- 2026-11-03 23:21:20 published: 8 file(s) to branch results
- 2026-11-03 23:21:38 supervisor: note: 23:21 check: run healthy, 2 running, 56 pending, no failures. No FINAL leads yet; best is codex/25 (section 54-55..71-72), with near misses at margins -0.23 to -0.29 (sub/add with a primes stream, pi_digits). Watch claude-opus quota: 101 of 120 calls in the last 5h, so it may hit its cap during t...
- 2026-11-03 23:21:38 codex/22: start (uses codex-plan)
- 2026-11-03 23:21:38 3 running: tier-claude, local/18, codex/22
- 2026-11-03 23:21:38 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-03 23:21:43 local/18: done (exit 0, 7 min)
- 2026-11-03 23:21:59 published: 9 file(s) to branch results
- 2026-11-03 23:21:59 local/16: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-03 23:21:59 3 running: tier-claude, codex/22, local/16
- 2026-11-03 23:25:14 tier-claude: running 15 min | 23:25:14 [model] claude-sonnet (proposer) ok 8.2s, tokens in/out 3333/835, reply 1839 chars
- 2026-11-03 23:26:39 codex/22: running 5 min | 23:26:31 [model] codex (proposer) calling...
- 2026-11-03 23:26:59 local/16: running 5 min | 23:26:45 [model] gemma-local (proposer) ok 16.8s, tokens in/out 3440/501, reply 1505 chars
- 2026-11-03 23:27:44 tier-claude: done (exit 0, 18 min)
- 2026-11-03 23:28:00 published: 9 file(s) to branch results
- 2026-11-03 23:28:00 sonnet/10: start (uses claude-plan)
- 2026-11-03 23:28:00 3 running: codex/22, local/16, sonnet/10
- 2026-11-03 23:31:40 codex/22: running 10 min | 23:31:07 [model] codex (proposer) ok 28.9s, tokens in/out 18488/483, reply 1531 chars
- 2026-11-03 23:32:00 local/16: running 10 min | 23:31:46 [model] gemma-local (proposer) calling...
- 2026-11-03 23:32:05 local/16: done (exit 0, 10 min)

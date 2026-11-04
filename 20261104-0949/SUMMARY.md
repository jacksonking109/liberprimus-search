# Overnight run 20261104-0949

Started 2026-11-04 09:49:00, updated 2026-11-04 10:24:54, status **running**. Jobs: pending 46, running 2, done 13

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 09:49:00 | 2026-11-04 10:05:41 | Claude Code proposers vs the random control |
| sonnet/10 | done | 2026-11-04 10:05:57 | 2026-11-04 10:13:38 | Sonnet, briefed by Opus |
| sonnet/11 | done | 2026-11-04 10:14:06 | 2026-11-04 10:18:37 | Sonnet, briefed by Opus |
| sonnet/12 | running | 2026-11-04 10:18:53 |  | Sonnet, briefed by Opus |
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
| codex/22 | done | 2026-11-04 10:03:06 | 2026-11-04 10:21:04 | Codex (exploratory) |
| codex/21 | done | 2026-11-04 10:21:19 | 2026-11-04 10:24:54 | Codex (exploratory) |
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
| local/16 | done | 2026-11-04 10:05:16 | 2026-11-04 10:09:57 | local models |
| local/19 | done | 2026-11-04 10:10:13 | 2026-11-04 10:14:26 | local models |
| local/15 | done | 2026-11-04 10:14:41 | 2026-11-04 10:14:46 | local models |
| local/20 | done | 2026-11-04 10:15:02 | 2026-11-04 10:19:48 | local models |
| local/14 | running | 2026-11-04 10:20:04 |  | local models |
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

**sonnet/12** (since 2026-11-04 10:18:53), latest log lines:
```
  | 3. Autokey with source "ciphertext". Use sub and beaufort. Try primers "DIVINITY", "FIRFUMFERENFE", "CIRCUMFERENCE", "INSTAR", "PARABLE", "WELCOME", and single-symbol primers [0] through [28]. Rea
  | 4. Autokey with source "plaintext". Use the same primers with sub, add and beaufort. Do not use skip_mode "resolve" here, since autokey does not support it. Use skip [0] with mode "all" instead.
  | 5. Long repeat keys. Use words "DIVINITY", "CICADA", "PRIMES", "TOTIENT", "KOAN", "MOBIUS", "LIBERPRIMUS", "THEINSTAR", each with sub and beaufort. Combine with reverse_text true as one variant. R
  | 6. Transposition followed by a sequence. Use columnar orders of width 3 to 7 (identity-like orders and simple reversals), then prime_totients sub with skip [0] resolve. Reason: a hidden layer is p
  | Do NOT repeat: con
10:19:08 [model] claude-sonnet (proposer) calling...
10:19:18 [model] claude-sonnet (proposer) ok 9.5s, tokens in/out 4193/844, reply 1859 chars
round 1 [claude-sonnet] proposals=8 valid=8 attempts=6021 passes=0 near=1 invalid=0
10:22:27 [model] claude-sonnet (proposer) calling...
10:22:38 [model] claude-sonnet (proposer) ok 10.3s, tokens in/out 4857/1049, reply 2409 chars
```
**local/14** (since 2026-11-04 10:20:04), latest log lines:
```
10:20:40 [model] gemma-local (proposer) ok 14.3s, tokens in/out 2391/417, reply 1250 chars
round 1 [qwen-local] proposals=8 valid=8 attempts=71 passes=0 near=0 invalid=0
round 1 [gemma-local] proposals=8 valid=8 attempts=36 passes=0 near=0 invalid=0
10:21:48 [model] qwen-local (proposer) calling...
10:22:09 [model] qwen-local (proposer) ok 20.6s, tokens in/out 2819/635, reply 2126 chars
10:22:09 [model] gemma-local (proposer) calling...
10:22:23 [model] gemma-local (proposer) ok 14.5s, tokens in/out 2828/424, reply 1351 chars
round 2 [qwen-local] proposals=8 valid=8 attempts=128 passes=0 near=0 invalid=0
round 2 [gemma-local] proposals=8 valid=8 attempts=44 passes=0 near=0 invalid=0
10:24:35 [model] qwen-local (proposer) calling...
```

## Results so far

- **tier-claude** (done)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 39128 attempts, 22 model calls, $0.0000
  - claude-sonnet: recall 0.33 (2/6), 11672 attempts, 22 model calls, $0.0000
- **sonnet/10** (done)
  - LP2:17.jpg, 18.jpg, 19.jpg - 0.jpg-2.jpg: 20273 attempts, 37 hypotheses, **0 final pass(es)**
- **sonnet/11** (done)
  - LP2:20.jpg/1 - 3.jpg/1: 35202 attempts, 34 hypotheses, **0 final pass(es)**
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 30269 attempts, 47 hypotheses, **0 final pass(es)**
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 22296 attempts, 41 hypotheses, **0 final pass(es)**
- **codex/22** (done)
  - LP2:57.jpg-66.jpg/1: 28292 attempts, 47 hypotheses, **0 final pass(es)**
- **codex/21** (done)
  - LP2:56.jpg/2: 26369 attempts, 48 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 298 attempts, 82 hypotheses, **0 final pass(es)**
- **local/18** (done)
  - LP2:- - 44.jpg-49.jpg: 217 attempts, 85 hypotheses, **0 final pass(es)**
- **local/16** (done)
  - LP2:15.jpg/2- - 32.jpg/2-39.jpg: 167 attempts, 79 hypotheses, **0 final pass(es)**
- **local/19** (done)
  - LP2:33.jpg - 50.jpg/1: 132 attempts, 87 hypotheses, **0 final pass(es)** (caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution)
- **local/15** (done)
  - skip LP2:15.jpg/1 - 32.jpg/1: only 9 symbols (minimum 20, --min-length); too short to judge
- **local/20** (done)
  - LP2:50.jpg/2-56.jpg/1: 189 attempts, 89 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 32 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 32 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 64 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 64 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 64 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 24 call(s) in the last 5h (cap 750), spent $0.0000

## Supervisor notes

- 2026-11-04 10:03:06: 10:03 check: the run is healthy at 3 of 59 jobs done. There are no final passes. Codex near misses on section 25 (primes/e_digits sub, margin about -0.23) are at noise level. The tier-claude benchmark so far: sonnet recall 0.50, opus 0.33, random control 0.00. The queue already covers every section, so no jobs were added.
- 2026-11-04 10:14:06: 10:14 check: the run is healthy at 7 of 61 jobs done, with 2 running. There are no final passes yet. The tier-claude benchmark has finished: opus recall 0.33 (2/6), sonnet 0.33 (2/6), random control 0.00. This corrects my 10:03 note, which gave sonnet 0.50 from an incomplete count. sonnet/10 on section 10 made 20k attempts and produced 0 final passes and no near misses. The section 25 near misses are still at noise level. The queue covers every section, so I added no jobs.

## Events

- 2026-11-04 10:14:41 published: 12 file(s) to branch results
- 2026-11-04 10:14:41 local/15: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 10:14:41 3 running: codex/22, sonnet/11, local/15
- 2026-11-04 10:14:41 sonnet/12 waiting: claude-plan in use by sonnet/11
- 2026-11-04 10:14:46 local/15: done (exit 0, 0 min)
- 2026-11-04 10:15:02 published: 12 file(s) to branch results
- 2026-11-04 10:15:02 local/20: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 10:15:02 3 running: codex/22, sonnet/11, local/20
- 2026-11-04 10:18:12 codex/22: running 15 min | 10:16:43 [model] codex (proposer) ok 31.0s, tokens in/out 19455/520, reply 1659 chars
- 2026-11-04 10:18:37 sonnet/11: done (exit 0, 5 min)
- 2026-11-04 10:18:53 published: 13 file(s) to branch results
- 2026-11-04 10:18:53 sonnet/12: start (uses claude-plan)
- 2026-11-04 10:18:53 3 running: codex/22, local/20, sonnet/12
- 2026-11-04 10:19:48 local/20: done (exit 0, 5 min)
- 2026-11-04 10:20:03 published: 14 file(s) to branch results
- 2026-11-04 10:20:04 local/14: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 10:20:04 3 running: codex/22, sonnet/12, local/14
- 2026-11-04 10:20:04 sonnet/13 waiting: claude-plan in use by sonnet/12
- 2026-11-04 10:21:04 codex/22: done (exit 0, 18 min)
- 2026-11-04 10:21:19 published: 15 file(s) to branch results
- 2026-11-04 10:21:19 codex/21: start (uses codex-plan)
- 2026-11-04 10:21:19 3 running: sonnet/12, local/14, codex/21
- 2026-11-04 10:21:19 sonnet/13 waiting: claude-plan in use by sonnet/12
- 2026-11-04 10:23:54 sonnet/12: running 5 min | 10:22:38 [model] claude-sonnet (proposer) ok 10.3s, tokens in/out 4857/1049, reply 2409 chars
- 2026-11-04 10:24:54 codex/21: done (exit 0, 4 min)

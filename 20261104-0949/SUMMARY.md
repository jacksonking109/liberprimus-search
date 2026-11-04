# Overnight run 20261104-0949

Started 2026-11-04 09:49:00, updated 2026-11-04 10:14:46, status **running**. Jobs: pending 50, running 2, done 9

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 09:49:00 | 2026-11-04 10:05:41 | Claude Code proposers vs the random control |
| sonnet/10 | done | 2026-11-04 10:05:57 | 2026-11-04 10:13:38 | Sonnet, briefed by Opus |
| sonnet/11 | running | 2026-11-04 10:14:06 |  | Sonnet, briefed by Opus |
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
| local/16 | done | 2026-11-04 10:05:16 | 2026-11-04 10:09:57 | local models |
| local/19 | done | 2026-11-04 10:10:13 | 2026-11-04 10:14:26 | local models |
| local/15 | done | 2026-11-04 10:14:41 | 2026-11-04 10:14:46 | local models |
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

**sonnet/11** (since 2026-11-04 10:14:06), latest log lines:
```
  | 2. Other running sequences. Use primes, pi_digits, e_digits, fibonacci, squares, triangular and naturals. Each takes combine "sub", offset_range [0,2000], once with no skip and once with skip [0].
  | 3. Autokey, since the deficit of doubles fits it. Use source "ciphertext" and source "plaintext". Primers: words DIVINITY, CIRCUMFERENCE, FIRFUMFERENFE, KAON, INSTAR, PARABLE, WISDOM, and single-s
  | 4. Periodic Vigenere with LP-themed words. Use repeat words DIVINITY, FIRFUMFERENFE, CIRCUMFERENCE, KOAN, PRIMES, CICADA, LIBERPRIMUS. Try combine "sub" with map identity and with map "reverse" (A
  | 5. Atbash with a shift. Use map "reverse", constant values 0..28, combine "add". This is one pass only; the flat IC makes it unlikely.
  | 6. Transposition from the factorisation 119 = 7x17. Use columnar orders of identity and reversed form for 7 and 17 columns. Pair them with the prime_totients stream (sub, skip [0], offset_range [0
  | 7. Reversed reading. Use reverse_text true with prime_totients, primes and pi_digits (sub, of
10:14:25 [model] claude-sonnet (proposer) calling...
10:14:35 [model] claude-sonnet (proposer) ok 10.2s, tokens in/out 3588/819, reply 1825 chars
round 1 [claude-sonnet] proposals=8 valid=4 attempts=16 passes=0 near=0 invalid=4
10:14:40 [model] claude-sonnet (proposer) calling...
```
**codex/22** (since 2026-11-04 10:03:06), latest log lines:
```
10:07:44 [model] codex (proposer) ok 15.8s, tokens in/out 18033/458, reply 1616 chars
round 2 [codex] proposals=8 valid=8 attempts=10119 passes=0 near=0 invalid=0
10:07:48 [model] codex (proposer) calling...
10:08:03 [model] codex (proposer) ok 14.9s, tokens in/out 18395/422, reply 1620 chars
round 3 [codex] proposals=8 valid=8 attempts=16153 passes=0 near=0 invalid=0
10:09:24 [model] codex (proposer) calling...
10:09:42 [model] codex (proposer) ok 18.7s, tokens in/out 18812/519, reply 1740 chars
round 4 [codex] proposals=8 valid=8 attempts=20219 passes=0 near=0 invalid=0
10:12:57 [model] codex (proposer) calling...
10:13:22 [model] codex (proposer) ok 25.6s, tokens in/out 19212/520, reply 1688 chars
```

## Results so far

- **tier-claude** (done)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 39128 attempts, 22 model calls, $0.0000
  - claude-sonnet: recall 0.33 (2/6), 11672 attempts, 22 model calls, $0.0000
- **sonnet/10** (done)
  - LP2:17.jpg, 18.jpg, 19.jpg - 0.jpg-2.jpg: 20273 attempts, 37 hypotheses, **0 final pass(es)**
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 30269 attempts, 47 hypotheses, **0 final pass(es)**
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 22296 attempts, 41 hypotheses, **0 final pass(es)**
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

## Model usage

- qwen-local: 24 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 24 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 56 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 56 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 56 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 17 call(s) in the last 5h (cap 750), spent $0.0000

## Supervisor notes

- 2026-11-04 10:03:06: 10:03 check: the run is healthy at 3 of 59 jobs done. There are no final passes. Codex near misses on section 25 (primes/e_digits sub, margin about -0.23) are at noise level. The tier-claude benchmark so far: sonnet recall 0.50, opus 0.33, random control 0.00. The queue already covers every section, so no jobs were added.
- 2026-11-04 10:14:06: 10:14 check: the run is healthy at 7 of 61 jobs done, with 2 running. There are no final passes yet. The tier-claude benchmark has finished: opus recall 0.33 (2/6), sonnet 0.33 (2/6), random control 0.00. This corrects my 10:03 note, which gave sonnet 0.50 from an incomplete count. sonnet/10 on section 10 made 20k attempts and produced 0 final passes and no near misses. The section 25 near misses are still at noise level. The queue covers every section, so I added no jobs.

## Events

- 2026-11-04 10:05:16 3 running: tier-claude, codex/22, local/16
- 2026-11-04 10:05:16 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 10:05:41 tier-claude: done (exit 0, 17 min)
- 2026-11-04 10:05:57 published: 9 file(s) to branch results
- 2026-11-04 10:05:57 sonnet/10: start (uses claude-plan)
- 2026-11-04 10:05:57 3 running: codex/22, local/16, sonnet/10
- 2026-11-04 10:08:07 codex/22: running 5 min | 10:08:03 [model] codex (proposer) ok 14.9s, tokens in/out 18395/422, reply 1620 chars
- 2026-11-04 10:09:57 local/16: done (exit 0, 5 min)
- 2026-11-04 10:10:13 published: 10 file(s) to branch results
- 2026-11-04 10:10:13 local/19: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 10:10:13 3 running: codex/22, sonnet/10, local/19
- 2026-11-04 10:10:13 sonnet/11 waiting: claude-plan in use by sonnet/10
- 2026-11-04 10:10:58 sonnet/10: running 5 min | 10:09:34 [model] claude-sonnet (proposer) ok 15.1s, tokens in/out 6496/1367, reply 2012 chars
- 2026-11-04 10:13:08 codex/22: running 10 min | 10:12:57 [model] codex (proposer) calling...
- 2026-11-04 10:13:38 sonnet/10: done (exit 0, 8 min)
- 2026-11-04 10:13:53 published: 11 file(s) to branch results
- 2026-11-04 10:14:06 supervisor: note: 10:14 check: the run is healthy at 7 of 61 jobs done, with 2 running. There are no final passes yet. The tier-claude benchmark has finished: opus recall 0.33 (2/6), sonnet 0.33 (2/6), random control 0.00. This corrects my 10:03 note, which gave sonnet 0.50 from an incomplete count. sonnet/10 on s...
- 2026-11-04 10:14:06 sonnet/11: start (uses claude-plan)
- 2026-11-04 10:14:06 3 running: codex/22, local/19, sonnet/11
- 2026-11-04 10:14:26 local/19: done (exit 0, 4 min)
- 2026-11-04 10:14:41 published: 12 file(s) to branch results
- 2026-11-04 10:14:41 local/15: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-04 10:14:41 3 running: codex/22, sonnet/11, local/15
- 2026-11-04 10:14:41 sonnet/12 waiting: claude-plan in use by sonnet/11
- 2026-11-04 10:14:46 local/15: done (exit 0, 0 min)

# Overnight run 20261104-1523

Started 2026-11-04 15:23:11, updated 2026-11-04 15:37:17, status **running**. Jobs: pending 55, running 3, done 3

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 15:23:11 | 2026-11-04 15:37:17 | Claude Code proposers vs the random control |
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
| codex/22 | running | 2026-11-04 15:36:02 |  | Codex (exploratory) |
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

**codex/24** (since 2026-11-04 15:23:11), latest log lines:
```
15:23:52 [model] codex (proposer) ok 24.9s, tokens in/out 18177/1045, reply 3336 chars, model not reported (pin one with model = "..." in the models config)
round 1 [codex] proposals=16 valid=16 attempts=26003 passes=0 near=0 invalid=0
15:28:40 [model] codex (proposer) calling...
15:29:07 [model] codex (proposer) ok 27.3s, tokens in/out 19054/1014, reply 2976 chars, model not reported (pin one with model = "..." in the models config)
round 2 [codex] proposals=16 valid=16 attempts=32113 passes=0 near=0 invalid=0
15:33:14 [model] codex (proposer) calling...
15:33:37 [model] codex (proposer) ok 23.0s, tokens in/out 19716/957, reply 3002 chars, model not reported (pin one with model = "..." in the models config)
round 3 [codex] proposals=16 valid=16 attempts=42152 passes=0 near=0 invalid=0
15:35:32 [model] codex (proposer) calling...
15:35:58 [model] codex (proposer) ok 25.6s, tokens in/out 19926/1018, reply 2885 chars, model not reported (pin one with model = "..." in the models config)
```
**codex/22** (since 2026-11-04 15:36:02), latest log lines:
```
  | 1. Prime totients. Use stream sequence prime_totients, combine sub, skip [0] (F) with skip_mode "all", offset_range [0,2000]. This is the method behind the solved LP "phi(prime)" page. Repeat with
  | 2. Ciphertext autokey. Use autokey source ciphertext with primer [0], [1] and short words (DIVINITY, KOAN, INSTAR), each with combine sub, add and beaufort. Ciphertext dependence would explain why
  | 3. Plaintext autokey. Use primers DIVINITY, CIRCUMFERENCE, WISDOM, PRIMES and WELCOME with combine sub, then beaufort, without skips. Autokey streams cannot use resolve.
  | 4. Repeat keys. Use repeat word DIVINITY, then FIRFUMFERENFE, with combine sub, skip [0] and offset_range [0, keylength-1]. Also try map reverse with these keys, since earlier LP pages used Atbash
  | 5. Other sequences. Try primes, pi_digits, e_digits, fibonacci, squares and triangular with scale 1, add 0, combine sub and offset_range [0,2000]. Then repeat the most promising ones with map reve
  | 6. Reversed reading. Set reverse_text true together with the best of directions 1, 2 and 5. Unsolved pages may need to be read back to front.
  | 7. Transposition. Only if directions 1-5 give near misses, add a columnar transposition with orders of width 2-8 (for example [1,0] and [2,0,1]) in front of the prime_totients sub stream with skip
  | Report every near miss with its exact spec, so the next round can vary offset, combine mode and skip around it.
15:36:27 [model] codex (proposer) calling...
15:36:50 [model] codex (proposer) ok 23.1s, tokens in/out 17620/963, reply 2978 chars, model not reported (pin one with model = "..." in the models config)
```
**local/18** (since 2026-11-04 15:31:51), latest log lines:
```
round 2 [gemma-local] proposals=8 valid=6 attempts=66 passes=0 near=0 invalid=3
15:35:37 [model] qwen-local (proposer) calling...
15:36:01 [model] qwen-local (proposer) ok 24.3s, tokens in/out 3269/670, reply 2178 chars
15:36:01 [model] gemma-local (proposer) calling...
15:36:31 [model] gemma-local (proposer) ok 30.4s, tokens in/out 3396/529, reply 1532 chars
round 3 [qwen-local] proposals=8 valid=0 attempts=77 passes=0 near=0 invalid=9
round 3 [gemma-local] proposals=8 valid=8 attempts=206 passes=0 near=0 invalid=3
15:36:31 [model] qwen-local (proposer) calling...
15:36:56 [model] qwen-local (proposer) ok 25.0s, tokens in/out 3801/694, reply 2576 chars
15:36:56 [model] gemma-local (proposer) calling...
```

## Results so far

- **tier-claude** (done)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.50 (3/6), 36316 attempts, 22 model calls, $0.0000
  - claude-sonnet: recall 0.33 (2/6), 19573 attempts, 23 model calls, $0.0000
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 57 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 2063 attempts, 70 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 45 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 44 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 194 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 194 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 194 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 60 call(s) in the last 5h (cap 750), spent $0.0000

## Events

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
- 2026-11-04 15:36:02 published: 7 file(s) to branch results
- 2026-11-04 15:36:02 codex/22: start (uses codex-plan)
- 2026-11-04 15:36:02 4 running: tier-claude, codex/24, local/18, codex/22
- 2026-11-04 15:36:02 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 15:36:52 local/18: running 5 min | 15:36:31 [model] qwen-local (proposer) calling...
- 2026-11-04 15:37:17 tier-claude: done (exit 0, 14 min)

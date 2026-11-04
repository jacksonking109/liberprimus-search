# Overnight run 20261104-1523

Started 2026-11-04 15:23:11, updated 2026-11-04 15:41:46, status **running**. Jobs: pending 52, running 3, done 6

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 15:23:11 | 2026-11-04 15:37:17 | Claude Code proposers vs the random control |
| sonnet/10 | done | 2026-11-04 15:37:33 | 2026-11-04 15:41:04 | Sonnet, briefed by Opus |
| sonnet/11 | running | 2026-11-04 15:41:06 |  | Sonnet, briefed by Opus |
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
| codex/24 | done | 2026-11-04 15:23:11 | 2026-11-04 15:40:48 | Codex (exploratory) |
| codex/22 | running | 2026-11-04 15:36:02 |  | Codex (exploratory) |
| codex/21 | running | 2026-11-04 15:41:06 |  | Codex (exploratory) |
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
| local/18 | done | 2026-11-04 15:31:51 | 2026-11-04 15:41:46 | local models |
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

**sonnet/11** (since 2026-11-04 15:41:06), latest log lines:
```
  | 2. Other number sequences with a start-offset sweep. Use primes, fibonacci, pi_digits, e_digits, squares and triangular, each with offset_range [0,2000]. Try combine sub and beaufort, scale 1 and 
  | 3. Ciphertext autokey. Use autokey source ciphertext with primers [0] through [28] (single symbol), then short words: DIVINITY, CICADA, KOAN, INSTAR, PRIMES, WISDOM, LIBER. Try combine sub and add
  | 4. Plaintext autokey with the same primers, combine sub and beaufort. Skip rules are not allowed with autokey, so leave skip unset.
  | 5. Repeat-word Vigenère from LP vocabulary. Words: DIVINITY, FIRFUMFERENFE, CIRCUMFERENCE, INSTAR, PARABLE, ENLIGHTENMENT, CONSUMPTION, PILGRIM, EMERGENCE, MOBIUS, KOAN, SACRED. Combine sub, add a
  | 6. Columnar transposition. 119 = 7×17, so try columnar orders of width 7 and width 17: identity order, reversed order, and a few keyword-derived orders. Combine each with constant 0, then with pri
  | 7. Run a single constant sweep (values 0–28, sub, map identity and reverse) as a baseline only. Do not expand it.
  | Do NOT repeat:
  | - Plain constant shifts beyond
15:41:35 [model] claude-sonnet (proposer) calling...
15:41:45 [model] claude-sonnet (proposer) ok 10.2s, tokens in/out 3582/1413, reply 2925 chars
```
**codex/22** (since 2026-11-04 15:36:02), latest log lines:
```
  | 4. Repeat keys. Use repeat word DIVINITY, then FIRFUMFERENFE, with combine sub, skip [0] and offset_range [0, keylength-1]. Also try map reverse with these keys, since earlier LP pages used Atbash
  | 5. Other sequences. Try primes, pi_digits, e_digits, fibonacci, squares and triangular with scale 1, add 0, combine sub and offset_range [0,2000]. Then repeat the most promising ones with map reve
  | 6. Reversed reading. Set reverse_text true together with the best of directions 1, 2 and 5. Unsolved pages may need to be read back to front.
  | 7. Transposition. Only if directions 1-5 give near misses, add a columnar transposition with orders of width 2-8 (for example [1,0] and [2,0,1]) in front of the prime_totients sub stream with skip
  | Report every near miss with its exact spec, so the next round can vary offset, combine mode and skip around it.
15:36:27 [model] codex (proposer) calling...
15:36:50 [model] codex (proposer) ok 23.1s, tokens in/out 17620/963, reply 2978 chars, model not reported (pin one with model = "..." in the models config)
round 1 [codex] proposals=16 valid=16 attempts=12019 passes=0 near=0 invalid=0
15:39:56 [model] codex (proposer) calling...
15:40:21 [model] codex (proposer) ok 25.7s, tokens in/out 18360/1036, reply 2966 chars, model not reported (pin one with model = "..." in the models config)
```
**codex/21** (since 2026-11-04 15:41:06), latest log lines:
```
  | 3. Related number sequences. Try "primes" with combine "sub", once with add 0 and once with add -1, over offset_range [0,300] with skip [0] resolve. This covers an off-by-one indexing convention. 
  | 4. Reversed reading. Add reverse_text true to the best two settings from directions 1 to 3. The page may encrypt from the end.
  | 5. Other sequences, as a cheap sweep. Try fibonacci, pi_digits, e_digits, squares and triangular with combine "sub", skip [0] resolve, offset_range [0,500].
  | 6. Autokey. Try a ciphertext-source autokey with primers of length 1 to 3, such as word "F" or "TH". Do not use skip resolve with autokey streams, because the language does not allow it.
  | Do NOT spend proposals on:
  | - constant shifts;
  | - short repeat keys, including Vigenère-style words.
  | The flat IC and the deficit of doubles already argue against periodic keys. Only try a repeat key if a direction above returns a near_miss that suggests one.
  | If everything fails, the section may not be English. It could be the 512-bit hash or other non-text. Report that instea
15:41:31 [model] codex (proposer) calling...
```

## Results so far

- **tier-claude** (done)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.50 (3/6), 36316 attempts, 22 model calls, $0.0000
  - claude-sonnet: recall 0.33 (2/6), 19573 attempts, 23 model calls, $0.0000
- **sonnet/10** (done)
  - LP2:17.jpg, 18.jpg, 19.jpg - 0.jpg-2.jpg: 30378 attempts, 60 hypotheses, **0 final pass(es)**
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 57 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 58281 attempts, 88 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 2063 attempts, 70 hypotheses, **0 final pass(es)**
- **local/18** (done)
  - LP2:- - 44.jpg-49.jpg: 1145 attempts, 75 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 44 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 44 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 197 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 197 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 197 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 60 call(s) in the last 5h (cap 750), spent $0.0000

## Events

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
- 2026-11-04 15:37:33 published: 7 file(s) to branch results
- 2026-11-04 15:37:33 sonnet/10: start (uses claude-plan)
- 2026-11-04 15:37:33 4 running: codex/24, local/18, codex/22, sonnet/10
- 2026-11-04 15:38:18 codex/24: running 15 min | 15:37:50 [model] codex (proposer) calling...
- 2026-11-04 15:40:48 codex/24: done (exit 0, 18 min)
- 2026-11-04 15:41:04 published: 8 file(s) to branch results
- 2026-11-04 15:41:04 codex/22: running 5 min | 15:40:21 [model] codex (proposer) ok 25.7s, tokens in/out 18360/1036, reply 2966 chars, model not reported (pin one with model = "..." in the models config)
- 2026-11-04 15:41:04 sonnet/10: done (exit 0, 4 min)
- 2026-11-04 15:41:06 published: 9 file(s) to branch results
- 2026-11-04 15:41:06 sonnet/11: start (uses claude-plan)
- 2026-11-04 15:41:06 3 running: local/18, codex/22, sonnet/11
- 2026-11-04 15:41:06 codex/21: start (uses codex-plan)
- 2026-11-04 15:41:06 4 running: local/18, codex/22, sonnet/11, codex/21
- 2026-11-04 15:41:06 sonnet/12 waiting: claude-plan in use by sonnet/11
- 2026-11-04 15:41:46 local/18: done (exit 0, 10 min)

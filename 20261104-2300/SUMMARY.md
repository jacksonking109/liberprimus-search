# Overnight run 20261104-2300

Started 2026-11-04 23:00:52, updated 2026-11-04 23:03:47, status **running**. Jobs: pending 57, running 3, done 1

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | running | 2026-11-04 23:00:52 |  | Claude Code proposers vs the random control |
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
| codex/25 | done | 2026-11-04 23:00:52 | 2026-11-04 23:03:47 | Codex (exploratory) |
| codex/24 | running | 2026-11-04 23:00:52 |  | Codex (exploratory) |
| codex/22 | running | 2026-11-04 23:00:52 |  | Codex (exploratory) |
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
| local/17 | pending |  |  | local models |
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

**tier-claude** (since 2026-11-04 23:00:52), latest log lines:
```
23:02:48 [model] claude-sonnet (proposer) calling...
23:03:03 [model] claude-sonnet (proposer) ok 14.9s, tokens in/out 3202/1853, reply 2565 chars
[claude-sonnet] 1/6 L=80 recovered=1 attempts=1966 calls=1 usd=0.0000 stopped=pass_found
23:03:11 [model] claude-sonnet (proposer) calling...
23:03:18 [model] claude-sonnet (proposer) ok 7.5s, tokens in/out 3205/1009, reply 2173 chars
[claude-sonnet] 2/6 L=80 recovered=0 attempts=20000 calls=1 usd=0.0000 stopped=max_attempts
23:03:25 [model] claude-sonnet (proposer) calling...
23:03:39 [model] claude-sonnet (proposer) ok 13.6s, tokens in/out 3201/1804, reply 2257 chars
[claude-sonnet] 3/6 L=80 recovered=0 attempts=20000 calls=1 usd=0.0000 stopped=max_attempts
23:03:46 [model] claude-sonnet (proposer) calling...
```
**codex/24** (since 2026-11-04 23:00:52), latest log lines:
```
  | 3. Exhaustive periodic keys as a baseline. Use "repeat" with exhaustive true and key_length 1, 2, 3 and 4, with combine "sub", then the same with map "reverse". Run each once with no skip and once
  | 4. Other sequence streams. Try primes, fibonacci, pi_digits, e_digits, triangular and squares. Use combine sub and beaufort, offset_range [0,1000], and scale 1, then -1 (28). Run each with and wit
  | 5. Transposition, then a simple key. Use grid with read "columns", "columns_reversed", "diagonal" and "spiral_in", with transpose_range [2,60]. Combine this with a constant shift (each value 0..28
  | 6. Transposition plus prime_totients. Use railfence over transpose_range [2,12], or grid columns over [2,40]. Add prime_totients with combine sub, skip [0], and offset_range [0,100].
  | 7. reverse_text true on directions 1 and 2. Some LP pages read backward.
  | Do NOT: run single word-key guesses without sweeps, or run the add duplic
23:01:08 [model] codex (proposer) calling...
23:01:57 [model] codex (proposer) ok 48.9s, tokens in/out 18171/1850, reply 6302 chars, model not reported (pin one with model = "..." in the models config)
round 1 [codex] proposals=32 valid=32 attempts=3365 passes=0 near=0 invalid=0
stopped: stop_file; final passes: 0
```
**codex/22** (since 2026-11-04 23:00:52), latest log lines:
```
  | 2. Other number streams. Try "sequence" primes, pi_digits, e_digits, fibonacci, squares, triangular and naturals. Use scale 1 and scale 28 (that is, -1), add 0, offset_range [0,2000], combine "sub
  | 3. Short periodic keys. Run exhaustive repeat with key_length 1 to 4, combine "sub", first with map "identity" and then with map "reverse". This covers Caesar, Atbash+shift and Vigenère up to leng
  | 4. Lore keywords. Use repeat words DIVINITY, CIRCUMFERENCE, FIRFUMFERENFE, INSTAR, PARABLE, KOAN, CICADA, WELCOME, PRIMES and EMERGE. Combine with "sub" and "beaufort", each word with offset_range
  | 5. Autokey, which suits the suppressed doubles. Use primers U, F, DIVINITY, INSTAR, KOAN and CIRCUMFERENCE. Try source "ciphertext" and "plaintext" with combine "sub" and "beaufort". Use no skip, 
  | 6. Transposition plus a cheap substitution. Combine grid "columns" or "columns_reversed" with transpose_range [2,170] and a constant stream for values 0 to 28, splitting values across proposals to
  | 7. Reversed reading. Take
23:01:15 [model] codex (proposer) calling...
23:01:59 [model] codex (proposer) ok 43.7s, tokens in/out 18716/1984, reply 6405 chars, model not reported (pin one with model = "..." in the models config)
round 1 [codex] proposals=32 valid=31 attempts=6645 passes=0 near=0 invalid=1
stopped: stop_file; final passes: 0
```

## Results so far

- **tier-claude** (running)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 99091 attempts, 6 model calls, $0.0000
  - claude-sonnet: recall 0.33 (1/3), 41966 attempts, 3 model calls, $0.0000
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 21 hypotheses, **0 final pass(es)**, stopped: max_attempts

## Model usage

- deepseek: 13 call(s) in the last 5h (cap none), spent $0.1873
- claude-opus: 30 call(s) in the last 5h (cap 180), spent $0.0000
- claude-sonnet: 30 call(s) in the last 5h (cap 180), spent $0.0000
- claude-supervisor: 30 call(s) in the last 5h (cap 180), spent $0.0000
- codex: 34 call(s) in the last 5h (cap 850), spent $0.0000

## Supervisor notes

- 2026-11-04 23:01:01: 23:00 check-in: run just started, 61 jobs queued covering sections 10-25 across sonnet/codex/local/deepseek lanes. No results yet; holding off on new jobs and strategy until first rounds report.

## Events

- 2026-11-04 23:00:52 started
- 2026-11-04 23:00:52 tier-claude: start (uses claude-plan)
- 2026-11-04 23:00:52 codex/25: start (uses codex-plan)
- 2026-11-04 23:00:52 2 running: tier-claude, codex/25
- 2026-11-04 23:00:52 codex/24: start (uses codex-plan)
- 2026-11-04 23:00:52 3 running: tier-claude, codex/25, codex/24
- 2026-11-04 23:00:52 codex/22: start (uses codex-plan)
- 2026-11-04 23:00:52 4 running: tier-claude, codex/25, codex/24, codex/22
- 2026-11-04 23:00:52 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 23:01:01 supervisor: note: 23:00 check-in: run just started, 61 jobs queued covering sections 10-25 across sonnet/codex/local/deepseek lanes. No results yet; holding off on new jobs and strategy until first rounds report.
- 2026-11-04 23:03:47 codex/25: done (exit 0, 3 min)

# Overnight run 20261104-1523

Started 2026-11-04 15:23:11, updated 2026-11-04 15:31:35, status **running**. Jobs: pending 57, running 3, done 1

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | running | 2026-11-04 15:23:11 |  | Claude Code proposers vs the random control |
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
| codex/25 | running | 2026-11-04 15:23:11 |  | Codex (exploratory) |
| codex/24 | running | 2026-11-04 15:23:11 |  | Codex (exploratory) |
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
| local/17 | done | 2026-11-04 15:23:11 | 2026-11-04 15:31:35 | local models |
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

**tier-claude** (since 2026-11-04 15:23:11), latest log lines:
```
15:30:28 [model] claude-opus (proposer) ok 10.2s, tokens in/out 4252/800, reply 1659 chars
15:30:29 [model] claude-opus (proposer) calling...
15:30:38 [model] claude-opus (proposer) ok 8.5s, tokens in/out 4814/775, reply 1630 chars
[claude-opus] 6/6 L=160 recovered=0 attempts=11863 calls=5 usd=0.0000
15:31:06 [model] claude-sonnet (proposer) calling...
15:31:16 [model] claude-sonnet (proposer) ok 9.7s, tokens in/out 2458/1005, reply 2231 chars
15:31:16 [model] claude-sonnet (proposer) calling...
15:31:32 [model] claude-sonnet (proposer) ok 15.8s, tokens in/out 3130/1778, reply 2624 chars
[claude-sonnet] 1/6 L=80 recovered=1 attempts=1283 calls=2 usd=0.0000 stopped=pass_found
15:31:32 [model] claude-sonnet (proposer) calling...
```
**codex/25** (since 2026-11-04 15:23:11), latest log lines:
```
  | Do NOT repeat:
  | - constant shifts (Caesar), since the IC rules them out
  | - naturals, s
15:23:28 [model] codex (proposer) calling...
15:23:53 [model] codex (proposer) ok 25.7s, tokens in/out 18203/1064, reply 3442 chars, model not reported (pin one with model = "..." in the models config)
round 1 [codex] proposals=16 valid=16 attempts=26016 passes=0 near=0 invalid=0
15:28:05 [model] codex (proposer) calling...
15:28:36 [model] codex (proposer) ok 31.1s, tokens in/out 19156/1121, reply 3260 chars, model not reported (pin one with model = "..." in the models config)
round 2 [codex] proposals=16 valid=16 attempts=38051 passes=0 near=0 invalid=0
15:31:30 [model] codex (proposer) calling...
```
**codex/24** (since 2026-11-04 15:23:11), latest log lines:
```
  | 3. Other numeric sequences: primes, pi_digits, e_digits, fibonacci, squares, triangular, naturals. Use offset_range [0,1999], scale 1 and also scale -1 (or "map": "reverse"), with skip [0] in reso
  | 4. Reversed text and reversed map. Re-run the best of directions 1 to 3 with reverse_text true, and separately with map "reverse" (the Atbash-like Gematria reversal used on early LP pages). Reason
  | 5. Periodic words from LP vocabulary as a sanity check. Use repeat with the words DIVINITY, FIRFUMFERENFE, CICADA, PRIMUS, INSTAR, CIRCUMFERENCE, KOAN. Use sub and beaufort, with and without skip 
  | 6. Columnar transposition before the key. Try orders of width 2 to 8 (for example [1,0], [2,0,1], [0,2,1,3]), combined with plain constant shifts 0 to 28 under sub. Reason: this checks for a pure 
  | Do NOT: submit constant shifts alone without transposition or map variation (frequencies are flat, so a monoalphabetic shift cannot work). Do not repeat any identical stream/co
15:23:27 [model] codex (proposer) calling...
15:23:52 [model] codex (proposer) ok 24.9s, tokens in/out 18177/1045, reply 3336 chars, model not reported (pin one with model = "..." in the models config)
round 1 [codex] proposals=16 valid=16 attempts=26003 passes=0 near=0 invalid=0
15:28:40 [model] codex (proposer) calling...
15:29:07 [model] codex (proposer) ok 27.3s, tokens in/out 19054/1014, reply 2976 chars, model not reported (pin one with model = "..." in the models config)
```

## Results so far

- **tier-claude** (running)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.50 (3/6), 36316 attempts, 22 model calls, $0.0000
  - claude-sonnet: recall 1.00 (1/1), 1283 attempts, 2 model calls, $0.0000
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 2063 attempts, 70 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 48 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 48 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 174 call(s) in the last 5h (cap 550), spent $0.0000
- claude-sonnet: 174 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 174 call(s) in the last 5h (cap 550), spent $0.0000
- codex: 57 call(s) in the last 5h (cap 750), spent $0.0000

## Events

- 2026-11-04 15:23:11 started
- 2026-11-04 15:23:11 tier-claude: start (uses claude-plan)
- 2026-11-04 15:23:11 codex/25: start (uses codex-plan)
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

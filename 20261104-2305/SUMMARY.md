# Overnight run 20261104-2305

Started 2026-11-04 23:05:16, updated 2026-11-04 23:14:10, status **running**. Jobs: pending 60, running 3, done 9

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 23:05:16 | 2026-11-04 23:09:58 | Claude Code proposers vs the random control |
| sonnet/10 | done | 2026-11-04 23:10:14 | 2026-11-04 23:14:10 | Sonnet, briefed by Opus |
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
| codex/25 | done | 2026-11-04 23:05:16 | 2026-11-04 23:07:19 | Codex (exploratory) |
| codex/24 | done | 2026-11-04 23:05:16 | 2026-11-04 23:07:40 | Codex (exploratory) |
| codex/22 | done | 2026-11-04 23:07:35 | 2026-11-04 23:09:35 | Codex (exploratory) |
| codex/21 | done | 2026-11-04 23:07:55 | 2026-11-04 23:09:51 | Codex (exploratory) |
| codex/20 | done | 2026-11-04 23:09:53 | 2026-11-04 23:12:29 | Codex (exploratory) |
| codex/19 | done | 2026-11-04 23:09:53 | 2026-11-04 23:11:34 | Codex (exploratory) |
| codex/18 | done | 2026-11-04 23:11:49 | 2026-11-04 23:13:50 | Codex (exploratory) |
| codex/17 | running | 2026-11-04 23:12:45 |  | Codex (exploratory) |
| codex/16 | running | 2026-11-04 23:14:05 |  | Codex (exploratory) |
| codex/15 | pending |  |  | Codex (exploratory) |
| codex/14 | pending |  |  | Codex (exploratory) |
| codex/13 | pending |  |  | Codex (exploratory) |
| codex/12 | pending |  |  | Codex (exploratory) |
| codex/11 | pending |  |  | Codex (exploratory) |
| codex/10 | pending |  |  | Codex (exploratory) |
| local/17 | running | 2026-11-04 23:05:16 |  | local models |
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
| structure/10 | pending |  |  | Codex: transposition then substitution |
| structure/12 | pending |  |  | Codex: transposition then substitution |
| structure/13 | pending |  |  | Codex: transposition then substitution |
| structure/14 | pending |  |  | Codex: transposition then substitution |
| structure/17 | pending |  |  | Codex: transposition then substitution |
| structure/18 | pending |  |  | Codex: transposition then substitution |
| structure/24 | pending |  |  | Codex: transposition then substitution |
| exhaustive/11 | pending |  |  | Codex: every periodic key up to length 4 |
| exhaustive/19 | pending |  |  | Codex: every periodic key up to length 4 |
| exhaustive/21 | pending |  |  | Codex: every periodic key up to length 4 |
| exhaustive/25 | pending |  |  | Codex: every periodic key up to length 4 |
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

**codex/17** (since 2026-11-04 23:12:45), latest log lines:
```
brief from codex (1954 chars):
  | 1. Start with repeat streams, exhaustive:true, key_length 1, 2, 3, then 4; combine:"sub", identity map, no skips or transposition. IC 0.995 suggests a flattened alphabet; these sweeps establish wh
  | 2. Prioritize autokey, source:"ciphertext", then source:"plaintext"; try every one-symbol primer [0] through [28], combine:"sub" and "beaufort", no skips. Only 11 adjacent doubles versus 35.2 expe
  | 3. Sweep sequence streams primes and prime_totients, offset_range:[0,1999], scale:1, add:0, combine:"sub" and "beaufort". Use separate proposals for each sequence/mode. Uniform IC supports testing
  | 4. Cover remaining sequence families: fibonacci, naturals, squares, triangular, pi_digits, e_digits; offsets 0..1999, scale:1, add:0, combine:"sub" and "beaufort". Then test scale:-1 with sub for 
  | 5. Test interrupted prime and prime_totient streams with skip:[0], first skip_mode:"all", then "resolve"; sub, offsets 0..1999. Repeat with skip:[28] separately. These are boundary-symbol hypothes
  | 6. Test pure routes using constant value:0, sub: grid reads columns, columns_reversed, boustrophedon_columns, diagonal, spiral_in and spiral_out, widths 2..500; railfence rails 2..64; decimate ste
  | 7. On near_miss, test reverse_text:true and narrow stream/route combinations, keeping expansions <=5000. Nothing has been tried yet. Do not duplicate exhaustive sub with add, equivalent reverse-ma
23:13:14 [model] codex (proposer) calling...
23:13:54 [model] codex (proposer) ok 39.8s, tokens in/out 18711/1809, reply 5626 chars, model not reported (pin one with model = "..." in the models config)
```
**codex/16** (since 2026-11-04 23:14:05), latest log lines:
```
===== 2026-11-04 23:14:05 C:\Users\ihazp\liberprimus-search\.venv\Scripts\python.exe -m lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 16 --gen
== LP2:15.jpg/2- - 32.jpg/2-39.jpg  (1894 symbols)
23:14:07 [model] codex (proposer) calling...
```
**local/17** (since 2026-11-04 23:05:16), latest log lines:
```
===== 2026-11-04 23:05:16 C:\Users\ihazp\liberprimus-search\.venv\Scripts\python.exe -m lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 17 --gen
== LP2:- - 40.jpg-43.jpg  (1021 symbols)
23:05:18 [model] qwen-local (proposer) calling...
23:06:06 [model] qwen-local (proposer) ok 48.2s, tokens in/out 2919/769, reply 2885 chars
23:06:06 [model] gemma-local (proposer) calling...
23:06:40 [model] gemma-local (proposer) ok 33.8s, tokens in/out 3001/510, reply 1666 chars
23:06:40 [model] granite (weighting) calling...
23:07:14 [model] granite (weighting) ok 34.4s, tokens in/out 252/38, reply 69 chars
```

## Results so far

- **tier-claude** (done)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 99088 attempts, 6 model calls, $0.0000
  - claude-sonnet: recall 0.33 (2/6), 118614 attempts, 6 model calls, $0.0000
- **sonnet/10** (done)
  - LP2:17.jpg, 18.jpg, 19.jpg - 0.jpg-2.jpg: 60000 attempts, 14 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 2 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 60000 attempts, 2 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/22** (done)
  - LP2:57.jpg-66.jpg/1: 60000 attempts, 4 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/21** (done)
  - LP2:56.jpg/2: 60000 attempts, 4 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/20** (done)
  - LP2:50.jpg/2-56.jpg/1: 60000 attempts, 40 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/19** (done)
  - LP2:33.jpg - 50.jpg/1: 60000 attempts, 7 hypotheses, **0 final pass(es)**, stopped: max_attempts (caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution)
- **codex/18** (done)
  - LP2:- - 44.jpg-49.jpg: 60000 attempts, 4 hypotheses, **0 final pass(es)**, stopped: max_attempts

## Model usage

- deepseek: 13 call(s) in the last 5h (cap none), spent $0.1873
- qwen-local: 1 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 1 call(s) in the last 5h (cap none), spent $0.0000
- granite: 1 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 46 call(s) in the last 5h (cap 180), spent $0.0000
- claude-sonnet: 46 call(s) in the last 5h (cap 180), spent $0.0000
- claude-supervisor: 46 call(s) in the last 5h (cap 180), spent $0.0000
- codex: 50 call(s) in the last 5h (cap 850), spent $0.0000

## Supervisor notes

- 2026-11-04 23:05:27: 23:05 check-in: run just started, 4 jobs running and 68 pending across sections 10-25 (sonnet, codex, local, structure, exhaustive, deepseek). No results yet, so I added no jobs and set no strategy note. I'll reassess when the first results come in.

## Events

- 2026-11-04 23:09:53 3 running: tier-claude, local/17, codex/20
- 2026-11-04 23:09:53 codex/19: start (uses codex-plan)
- 2026-11-04 23:09:53 4 running: tier-claude, local/17, codex/20, codex/19
- 2026-11-04 23:09:53 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 23:09:58 tier-claude: done (exit 0, 5 min)
- 2026-11-04 23:10:14 published: 9 file(s) to branch results
- 2026-11-04 23:10:14 sonnet/10: start (uses claude-plan)
- 2026-11-04 23:10:14 4 running: local/17, codex/20, codex/19, sonnet/10
- 2026-11-04 23:10:19 local/17: running 5 min | 23:07:14 [model] granite (weighting) ok 34.4s, tokens in/out 252/38, reply 69 chars
- 2026-11-04 23:11:34 codex/19: done (exit 0, 2 min)
- 2026-11-04 23:11:49 published: 10 file(s) to branch results
- 2026-11-04 23:11:49 codex/18: start (uses codex-plan)
- 2026-11-04 23:11:49 4 running: local/17, codex/20, sonnet/10, codex/18
- 2026-11-04 23:11:49 sonnet/11 waiting: claude-plan in use by sonnet/10
- 2026-11-04 23:12:29 codex/20: done (exit 0, 3 min)
- 2026-11-04 23:12:45 published: 11 file(s) to branch results
- 2026-11-04 23:12:45 codex/17: start (uses codex-plan)
- 2026-11-04 23:12:45 4 running: local/17, sonnet/10, codex/18, codex/17
- 2026-11-04 23:12:45 sonnet/11 waiting: claude-plan in use by sonnet/10
- 2026-11-04 23:13:50 codex/18: done (exit 0, 2 min)
- 2026-11-04 23:14:05 published: 12 file(s) to branch results
- 2026-11-04 23:14:05 codex/16: start (uses codex-plan)
- 2026-11-04 23:14:05 4 running: local/17, sonnet/10, codex/17, codex/16
- 2026-11-04 23:14:05 sonnet/11 waiting: claude-plan in use by sonnet/10
- 2026-11-04 23:14:10 sonnet/10: done (exit 0, 4 min)

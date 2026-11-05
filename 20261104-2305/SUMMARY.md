# Overnight run 20261104-2305

Started 2026-11-04 23:05:16, updated 2026-11-04 23:11:34, status **running**. Jobs: pending 63, running 3, done 6

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-04 23:05:16 | 2026-11-04 23:09:58 | Claude Code proposers vs the random control |
| sonnet/10 | running | 2026-11-04 23:10:14 |  | Sonnet, briefed by Opus |
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
| codex/20 | running | 2026-11-04 23:09:53 |  | Codex (exploratory) |
| codex/19 | done | 2026-11-04 23:09:53 | 2026-11-04 23:11:34 | Codex (exploratory) |
| codex/18 | pending |  |  | Codex (exploratory) |
| codex/17 | pending |  |  | Codex (exploratory) |
| codex/16 | pending |  |  | Codex (exploratory) |
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

**sonnet/10** (since 2026-11-04 23:10:14), latest log lines:
```
  | 3. Autokey. Adjacent doubles are 4 against 25 expected. That strong deficit suggests the key depends on neighbouring symbols. Test source "ciphertext" and "plaintext" with primers taken from LP vo
  | 4. Exhaustive periodic keys. Use repeat exhaustive with key_length 1 through 4, combine sub. Run once with map identity and once with map reverse, and once more with skip [F] in mode "all". This c
  | 5. Word keys. Use repeat with the words DIVINITY, FIRFUMFERENFE, CIRCUMFERENCE, LIBERPRIMUS, INSTAR, CONSUMPTION and ENLIGHTENMENT. Give each an offset_range [0,20] and try sub and beaufort with b
  | 6. Transposition plus key, as a lower priority. Use railfence with transpose_range [2,12], and grid with read "columns" and transpose_range [2,40]. Pair each with the prime_totients stream at offs
  | Do NOT:
  | - Try pure
23:10:39 [model] claude-sonnet (proposer) calling...
23:10:53 [model] claude-sonnet (proposer) ok 13.9s, tokens in/out 4937/1148, reply 2486 chars
round 1 [claude-sonnet] proposals=12 valid=4 attempts=24404 passes=0 near=0 invalid=8
23:11:10 [model] claude-sonnet (proposer) calling...
```
**codex/20** (since 2026-11-04 23:09:53), latest log lines:
```
  | 1. Prioritize ciphertext autokey with every one-symbol primer [0] through [28], combine "sub", map "identity", no skips or transposition. Only 11 adjacent doubles versus 50.6 expected suggests fee
  | 2. Test plaintext autokey with all one-symbol primers, combine "sub" and "beaufort", no skips. Then ciphertext autokey with all two-symbol primers (841 proposals per mode). This tests short feedba
  | 3. Run repeat streams with exhaustive:true and key_length 1, 2, 3, 4, combine "sub", no skips or transposition. IC 0.995 disfavors a simple shift but permits periodic encryption. Each exhaustive p
  | 4. Sweep sequence streams primes, prime_totients, fibonacci, naturals, squares, triangular, pi_digits, e_digits; combine "sub" and "beaufort", offset_range [0,1999], scale 1, add 0. Each sequence/
  | 5. For the strongest changing-key families, compare skip [0] with skip_mode "all"; for sequences also test "resolve". F is the zero-index rune, making it a concrete literal candidate. Autokey perm
  | 6. Test ordering changes with constant value 0: grid reads columns, boustrophedon_columns, diagonal and spiral_in, each transpose_range [2,500]; railfence [2,64]; decimate [2,1467]. Pure transposi
23:10:23 [model] codex (proposer) calling...
23:11:06 [model] codex (proposer) ok 42.8s, tokens in/out 18615/1478, reply 5527 chars, model not reported (pin one with model = "..." in the models config)
round 1 [codex] proposals=32 valid=32 attempts=32 passes=0 near=0 invalid=0
23:11:16 [model] codex (proposer) calling...
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
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 2 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 60000 attempts, 2 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/22** (done)
  - LP2:57.jpg-66.jpg/1: 60000 attempts, 4 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/21** (done)
  - LP2:56.jpg/2: 60000 attempts, 4 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/19** (done)
  - LP2:33.jpg - 50.jpg/1: 60000 attempts, 7 hypotheses, **0 final pass(es)**, stopped: max_attempts (caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution)

## Model usage

- deepseek: 13 call(s) in the last 5h (cap none), spent $0.1873
- qwen-local: 1 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 1 call(s) in the last 5h (cap none), spent $0.0000
- granite: 1 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 45 call(s) in the last 5h (cap 180), spent $0.0000
- claude-sonnet: 45 call(s) in the last 5h (cap 180), spent $0.0000
- claude-supervisor: 45 call(s) in the last 5h (cap 180), spent $0.0000
- codex: 45 call(s) in the last 5h (cap 850), spent $0.0000

## Supervisor notes

- 2026-11-04 23:05:27: 23:05 check-in: run just started, 4 jobs running and 68 pending across sections 10-25 (sonnet, codex, local, structure, exhaustive, deepseek). No results yet, so I added no jobs and set no strategy note. I'll reassess when the first results come in.

## Events

- 2026-11-04 23:05:27 supervisor: note: 23:05 check-in: run just started, 4 jobs running and 68 pending across sections 10-25 (sonnet, codex, local, structure, exhaustive, deepseek). No results yet, so I added no jobs and set no strategy note. I'll reassess when the first results come in.
- 2026-11-04 23:07:19 codex/25: done (exit 0, 2 min)
- 2026-11-04 23:07:35 published: 6 file(s) to branch results
- 2026-11-04 23:07:35 codex/22: start (uses codex-plan)
- 2026-11-04 23:07:35 4 running: tier-claude, codex/24, local/17, codex/22
- 2026-11-04 23:07:35 sonnet/10 waiting: claude-plan in use by tier-claude
- 2026-11-04 23:07:40 codex/24: done (exit 0, 2 min)
- 2026-11-04 23:07:55 published: 7 file(s) to branch results
- 2026-11-04 23:07:55 codex/21: start (uses codex-plan)
- 2026-11-04 23:07:55 4 running: tier-claude, local/17, codex/22, codex/21
- 2026-11-04 23:09:35 codex/22: done (exit 0, 2 min)
- 2026-11-04 23:09:51 published: 8 file(s) to branch results
- 2026-11-04 23:09:51 codex/21: done (exit 0, 2 min)
- 2026-11-04 23:09:53 published: 9 file(s) to branch results
- 2026-11-04 23:09:53 codex/20: start (uses codex-plan)
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

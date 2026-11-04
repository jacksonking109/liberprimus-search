# Overnight run 20261103-2310

Started 2026-11-03 23:10:06, updated 2026-11-03 23:46:03, status **running**. Jobs: pending 47, running 2, done 13

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | done | 2026-11-03 23:10:06 | 2026-11-03 23:27:44 | Claude Code proposers vs the random control |
| sonnet/10 | done | 2026-11-03 23:28:00 | 2026-11-03 23:38:10 | Sonnet, briefed by Opus |
| sonnet/11 | done | 2026-11-03 23:38:25 | 2026-11-03 23:43:46 | Sonnet, briefed by Opus |
| sonnet/12 | running | 2026-11-03 23:44:17 |  | Sonnet, briefed by Opus |
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
| codex/22 | done | 2026-11-03 23:21:38 | 2026-11-03 23:41:45 | Codex (exploratory) |
| codex/21 | done | 2026-11-03 23:42:01 | 2026-11-03 23:46:03 | Codex (exploratory) |
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
| local/19 | done | 2026-11-03 23:32:28 | 2026-11-03 23:36:28 | local models |
| local/15 | done | 2026-11-03 23:36:44 | 2026-11-03 23:36:49 | local models |
| local/20 | done | 2026-11-03 23:37:05 | 2026-11-03 23:45:12 | local models |
| local/14 | running | 2026-11-03 23:45:28 |  | local models |
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
| sup1/25 | pending |  |  | added by supervisor. Section 25 has near misses at margin -0.23 to -0.29, an order of magnitude closer than any other se |

## Now running

**sonnet/12** (since 2026-11-03 23:44:17), latest log lines:
```
  | 1. Prime-totient stream, the known LP precedent. Use {"kind":"sequence","name":"prime_totients"} with combine "sub", then repeat with "add", with offset_range [0,1500]. Run each with skip [0] (F) 
  | 2. Autokey, aimed at the doubles deficit. The text has 4 adjacent doubles where 23.9 are expected, which is a strong anti-repeat signal typical of keys tied to the text. Try "autokey" with source 
  | 3. Other sequence keys over long offset ranges. Use primes, pi_digits, e_digits, fibonacci, squares and triangular, each with offset_range [0,1000]. Use combine "sub" and "beaufort", with scale 1 
  | 4. Long repeat words, because the IC is flat. Long periods (more than 10) or running keys could produce the flat IC. Use stream "repeat" with LP-themed words such as "DIVINITY", "CICADA", "PARABLE
  | 5. Transposition plus a simple key. Use transpose columnar with widths 3 to 8: identity orders first, then reversed orders. Combine each with a constant shift 0..28 or the prime_totients stream ab
  | 6. Interrupter variants. Run direction 1 with skip [0], skip [24] (A) and skip [26] (Y), each in "resolve" mode. In LP, F is a known literal interrupter.
  | Do NOT spend proposals on:
  | - short-period Vigenère (periods 1 to 8) without a transposition, because IC 1.0
23:44:33 [model] claude-sonnet (proposer) calling...
23:44:41 [model] claude-sonnet (proposer) ok 7.3s, tokens in/out 4178/882, reply 1981 chars
```
**local/14** (since 2026-11-03 23:45:28), latest log lines:
```
===== 2026-11-03 23:45:28 C:\Users\ihazp\liberprimus-search\.venv\Scripts\python.exe -m lpswarm swarm --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json --sections 14 --gen
== LP2:8.jpg-14.jpg - 25.jpg-31.jpg  (1729 symbols)
23:45:30 [model] qwen-local (proposer) calling...
23:45:48 [model] qwen-local (proposer) ok 18.5s, tokens in/out 2336/550, reply 2023 chars
23:45:48 [model] gemma-local (proposer) calling...
23:46:03 [model] gemma-local (proposer) ok 14.6s, tokens in/out 2391/413, reply 1235 chars
```

## Results so far

- **tier-claude** (done)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 73695 attempts, 23 model calls, $0.0000
  - claude-sonnet: recall 0.17 (1/6), 23024 attempts, 26 model calls, $0.0000
- **sonnet/10** (done)
  - LP2:17.jpg, 18.jpg, 19.jpg - 0.jpg-2.jpg: 36073 attempts, 44 hypotheses, **0 final pass(es)**
- **sonnet/11** (done)
  - LP2:20.jpg/1 - 3.jpg/1: 56563 attempts, 44 hypotheses, **0 final pass(es)**
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 29964 attempts, 47 hypotheses, **0 final pass(es)**
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 26431 attempts, 47 hypotheses, **0 final pass(es)**
- **codex/22** (done)
  - LP2:57.jpg-66.jpg/1: 32546 attempts, 48 hypotheses, **0 final pass(es)**
- **codex/21** (done)
  - LP2:56.jpg/2: 40233 attempts, 48 hypotheses, **0 final pass(es)**
- **local/17** (done)
  - LP2:- - 40.jpg-43.jpg: 190 attempts, 81 hypotheses, **0 final pass(es)**
- **local/18** (done)
  - LP2:- - 44.jpg-49.jpg: 284 attempts, 91 hypotheses, **0 final pass(es)**
- **local/16** (done)
  - LP2:15.jpg/2- - 32.jpg/2-39.jpg: 211 attempts, 89 hypotheses, **0 final pass(es)**
- **local/19** (done)
  - LP2:33.jpg - 50.jpg/1: 120 attempts, 88 hypotheses, **0 final pass(es)** (caution: short section (91 runes): many keys give plausible-looking text this short; treat any lead with extra caution)
- **local/15** (done)
  - skip LP2:15.jpg/1 - 32.jpg/1: only 9 symbols (minimum 20, --min-length); too short to judge
- **local/20** (done)
  - LP2:50.jpg/2-56.jpg/1: 148 attempts, 87 hypotheses, **0 final pass(es)**

## Model usage

- qwen-local: 71 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 71 call(s) in the last 5h (cap none), spent $0.0000
- granite: 2 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 134 call(s) in the last 5h (cap 120), spent $0.0000, paused until 01:34 (local cap, raise max_calls_per_window to allow more)
- claude-sonnet: 134 call(s) in the last 5h (cap 550), spent $0.0000
- claude-supervisor: 134 call(s) in the last 5h (cap 200), spent $0.0000
- codex: 63 call(s) in the last 5h (cap 750), spent $0.0000
- dry: 2 call(s) in the last 5h (cap none), spent $0.0000

## Supervisor notes

- 2026-11-03 23:21:38: 23:21 check: run healthy, 2 running, 56 pending, no failures. No FINAL leads yet; best is codex/25 (section 54-55..71-72), with near misses at margins -0.23 to -0.29 (sub/add with a primes stream, pi_digits). Watch claude-opus quota: 101 of 120 calls in the last 5h, so it may hit its cap during tier-claude. No jobs added; the queue already covers every section.
- 2026-11-03 23:32:28: 23:32 check: run healthy. 2 running (codex/22, sonnet/10), local/16 just finished, no failures. No FINAL leads. The best near misses are still codex/25 (sec 54-55..71-72): sub/add with a primes stream at offsets ~954/1886 and pi_digits @593, margins -0.23 to -0.29. codex/22 reported 1 near miss in round 4. Local-model jobs have low attempt counts (~200-280 per section) compared with codex (~26-30k), so their yield per job is small. claude-opus is at 119/120 calls, so it is effectively capped. Sonnet jobs already cover sections 10-25. No jobs added.
- 2026-11-03 23:44:17: 23:44 check: run healthy. 3 running (codex/21, local/20, sonnet/11 just finished), no failures, no FINAL leads. The best near misses are still on section 25 (54-55..71-72) from codex/25, at margins -0.23 to -0.29 using a primes stream @1886/@954, pi_digits @593 and prime_totients @134. That is far closer than any other section; the next best is about -2.2. I added one focused refinement job on section 25 with claude-sonnet and codex. claude-opus is paused until 01:33 (cap 120). Local jobs still produce few attempts per section.
- 2026-11-03 23:44:17: brief for sup1 (claude-sonnet,codex): Section 25 (LP2:54.jpg-55.jpg - 71.jpg-72.jpg, 308 runes). codex/25 found four near misses, all just under the pass threshold: (1) sub, primes*1+0 @1886, skip [0]; (2) add, primes*1+0 @954, skip [0]; (3) sub, pi_digits*1+0 @593, skip [28]; (4) beaufort, prime_totients*1+0 @134, map reverse, skip [28]. Search the neighbourhood of these programs rather than starting fresh. Things to try: offsets within about ±40 of 1886, 954, 593 and 134. Swap sub/add/beaufort on each stream. Toggle skip [0] vs [28] vs none. Try primes*1+k for small k (the -1 / +57 style shifts used in Cicada page keys), primes mod 29, and prime_totients (phi(p)=p-1) at the same offsets, since primes and prime_totients differ only by 1. Also try reversed text and map reverse on the primes variants. Consider that a word-boundary-aware or per-line restart of the stream may explain why two different primes offsets each come close. Avoid: fresh unrelated streams (e_digits, fibonacci) unless combined with the near-miss settings; and Vigenere with English keywords, which the earlier rounds explored without results. Prefer many small, systematic variations per round over a few wide jumps.

## Events

- 2026-11-03 23:37:05 3 running: codex/22, sonnet/10, local/20
- 2026-11-03 23:38:05 sonnet/10: running 10 min | 23:35:24 [model] claude-sonnet (proposer) ok 18.6s, tokens in/out 6881/1473, reply 1995 chars
- 2026-11-03 23:38:10 sonnet/10: done (exit 0, 10 min)
- 2026-11-03 23:38:25 published: 12 file(s) to branch results
- 2026-11-03 23:38:25 sonnet/11: start (uses claude-plan)
- 2026-11-03 23:38:25 3 running: codex/22, local/20, sonnet/11
- 2026-11-03 23:41:45 codex/22: done (exit 0, 20 min)
- 2026-11-03 23:42:01 published: 13 file(s) to branch results
- 2026-11-03 23:42:01 codex/21: start (uses codex-plan)
- 2026-11-03 23:42:01 3 running: local/20, sonnet/11, codex/21
- 2026-11-03 23:42:01 sonnet/12 waiting: claude-plan in use by sonnet/11
- 2026-11-03 23:42:06 local/20: running 5 min | 23:41:48 [model] gemma-local (proposer) ok 15.0s, tokens in/out 3414/411, reply 1201 chars
- 2026-11-03 23:43:26 sonnet/11: running 5 min | 23:42:47 [model] claude-sonnet (proposer) ok 13.3s, tokens in/out 6800/1711, reply 2262 chars
- 2026-11-03 23:43:46 sonnet/11: done (exit 0, 5 min)
- 2026-11-03 23:44:01 published: 14 file(s) to branch results
- 2026-11-03 23:44:17 supervisor: note: 23:44 check: run healthy. 3 running (codex/21, local/20, sonnet/11 just finished), no failures, no FINAL leads. The best near misses are still on section 25 (54-55..71-72) from codex/25, at margins -0.23 to -0.29 using a primes stream @1886/@954, pi_digits @593 and prime_totients @134. That is fa...
- 2026-11-03 23:44:17 supervisor: added sup1: swarm on 1 section(s) with claude-sonnet,codex; brief: Section 25 (LP2:54.jpg-55.jpg - 71.jpg-72.jpg, 308 runes). codex/25 found four near misses, all just under the pass threshold: (1) sub, primes*1+0 @1886, skip [0]; (2) add, primes*1+0 @954, skip [0]; ...
- 2026-11-03 23:44:17 sonnet/12: start (uses claude-plan)
- 2026-11-03 23:44:17 3 running: local/20, codex/21, sonnet/12
- 2026-11-03 23:45:12 local/20: done (exit 0, 8 min)
- 2026-11-03 23:45:28 published: 15 file(s) to branch results
- 2026-11-03 23:45:28 local/14: start (uses ollama:http://127.0.0.1:11434)
- 2026-11-03 23:45:28 3 running: codex/21, sonnet/12, local/14
- 2026-11-03 23:45:28 sonnet/13 waiting: claude-plan in use by sonnet/12
- 2026-11-03 23:46:03 codex/21: done (exit 0, 4 min)

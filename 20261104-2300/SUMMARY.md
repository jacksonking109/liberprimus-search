# Overnight run 20261104-2300

Started 2026-11-04 23:00:52, updated 2026-11-04 23:04:07, status **stopped**. Jobs: pending 57, done 3, interrupted 1

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | interrupted | 2026-11-04 23:00:52 | 2026-11-04 23:04:07 | STOP file |
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
| codex/24 | done | 2026-11-04 23:00:52 | 2026-11-04 23:04:03 | Codex (exploratory) |
| codex/22 | done | 2026-11-04 23:00:52 | 2026-11-04 23:04:05 | Codex (exploratory) |
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

## Results so far

- **tier-claude** (interrupted)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.33 (2/6), 99091 attempts, 6 model calls, $0.0000
  - claude-sonnet: recall 0.33 (1/3), 41966 attempts, 3 model calls, $0.0000
- **codex/25** (done)
  - LP2:54.jpg-55.jpg - 71.jpg-72.jpg: 60000 attempts, 21 hypotheses, **0 final pass(es)**, stopped: max_attempts
- **codex/24** (done)
  - LP2:51.jpg/2-53.jpg - 68.jpg/2-70.jpg: 3365 attempts, 2 hypotheses, **0 final pass(es)**, stopped: stop_file
- **codex/22** (done)
  - LP2:57.jpg-66.jpg/1: 6645 attempts, 4 hypotheses, **0 final pass(es)**, stopped: stop_file

## Model usage

- deepseek: 13 call(s) in the last 5h (cap none), spent $0.1873
- claude-opus: 31 call(s) in the last 5h (cap 180), spent $0.0000
- claude-sonnet: 31 call(s) in the last 5h (cap 180), spent $0.0000
- claude-supervisor: 31 call(s) in the last 5h (cap 180), spent $0.0000
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
- 2026-11-04 23:04:03 published: 6 file(s) to branch results
- 2026-11-04 23:04:03 codex/24: done (exit 0, 3 min)
- 2026-11-04 23:04:05 published: 8 file(s) to branch results
- 2026-11-04 23:04:05 codex/22: done (exit 0, 3 min)
- 2026-11-04 23:04:07 published: 8 file(s) to branch results
- 2026-11-04 23:04:07 stopping: STOP file
- 2026-11-04 23:04:07 tier-claude: interrupted (exit 1, 3 min)

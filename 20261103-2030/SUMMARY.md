# Overnight run 20261103-2030

Started 2026-11-03 20:30:23, updated 2026-11-03 20:32:42, status **running**. Jobs: pending 15, failed 1

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | failed | 2026-11-03 20:30:23 | 2026-11-03 20:32:42 | Claude Code proposers vs the random control |
| unsolved/10 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/11 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/12 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/13 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/14 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/15 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/16 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/17 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/18 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/19 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/20 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/21 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/22 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/24 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/25 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |

## Results so far

- **tier-claude** (failed)
  - random_program:40: recall 0.00 (0/6), 192 attempts, 0 model calls, $0.0000
  - claude-opus: recall 0.50 (1/2), 11742 attempts, 6 model calls, $0.0000
  - last log lines:
    > 
    > ===== 2026-11-03 20:30:23 C:\Users\ihazp\liberprimus-search\.venv\Scripts\python.exe -m lpswarm tiertest --arms random_program:40,claude-opus,claude-sonnet --le
    > C:\Users\ihazp\liberprimus-search\src\lpswarm\router\router.py:106: UserWarning: model deepseek: max_usd is set but prices are 0, so spend is recorded as $0 and
    >   return cls(load_model_specs(path), ledger=ledger, **kw)
    > lpswarm: error: skip_mode "resolve" needs a language model (lm=bigram table)

## Model usage

- qwen-local: 2 call(s) in the last 5h (cap none), spent $0.0000
- gemma-local: 2 call(s) in the last 5h (cap none), spent $0.0000
- granite: 2 call(s) in the last 5h (cap none), spent $0.0000
- claude-opus: 11 call(s) in the last 5h (cap 40), spent $0.0000
- claude-sonnet: 11 call(s) in the last 5h (cap 40), spent $0.0000
- claude-supervisor: 11 call(s) in the last 5h (cap 40), spent $0.0000
- codex: 1 call(s) in the last 5h (cap 30), spent $0.0000
- dry: 2 call(s) in the last 5h (cap none), spent $0.0000

## Events

- 2026-11-03 20:30:23 started
- 2026-11-03 20:30:23 tier-claude: start
- 2026-11-03 20:32:42 tier-claude: failed (exit 2)

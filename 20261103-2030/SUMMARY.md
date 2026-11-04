# Overnight run 20261103-2030

Started 2026-11-03 20:30:23, updated 2026-11-03 20:35:08, status **running**. Jobs: pending 22, failed 1, blocked 8

| job | status | started | ended | note |
| --- | --- | --- | --- | --- |
| tier-claude | failed | 2026-11-03 20:30:23 | 2026-11-03 20:32:42 | Claude Code proposers vs the random control |
| unsolved/10 | blocked |  | 2026-11-03 20:33:05 | model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_pe |
| unsolved/11 | blocked |  | 2026-11-03 20:33:29 | model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_pe |
| unsolved/12 | blocked |  | 2026-11-03 20:33:49 | model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_pe |
| unsolved/13 | blocked |  | 2026-11-03 20:34:08 | model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_pe |
| unsolved/14 | blocked |  | 2026-11-03 20:34:15 | model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_pe |
| unsolved/15 | blocked |  | 2026-11-03 20:34:34 | model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_pe |
| unsolved/16 | blocked |  | 2026-11-03 20:34:48 | model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_pe |
| unsolved/17 | blocked |  | 2026-11-03 20:35:08 | model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_pe |
| unsolved/18 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/19 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/20 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/21 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/22 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/24 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| unsolved/25 | pending |  |  | Codex (exploratory) + DeepSeek (volume) |
| sup1/10 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/11 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/12 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/13 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/14 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/15 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/16 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/17 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/18 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/19 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/20 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/21 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/22 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/24 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |
| sup1/25 | pending |  |  | added by supervisor. The DeepSeek-based unsolved jobs are blocked by the zero-price config. This covers the same section |

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
- claude-opus: 19 call(s) in the last 5h (cap 40), spent $0.0000
- claude-sonnet: 19 call(s) in the last 5h (cap 40), spent $0.0000
- claude-supervisor: 19 call(s) in the last 5h (cap 40), spent $0.0000
- codex: 1 call(s) in the last 5h (cap 30), spent $0.0000
- dry: 2 call(s) in the last 5h (cap none), spent $0.0000

## Supervisor notes

- 2026-11-03 20:33:05: tier-claude failed at 20:32 with exit 2, a config error: 'skip_mode "resolve" needs a language model (lm=bigram table)'. I did not retry it because it would fail the same way until the tiertest command sets an LM (e.g. a bigram table) or uses a different skip_mode. Partial result before the failure: claude-opus recall 0.50 (1/2) over 11742 attempts; random control 0/6. Also a router warning: deepseek has max_usd set but prices are 0, so spend shows as $0 and the cost cap will not limit it. The 15 unsolved jobs are still pending. If they also use skip_mode resolve they may fail the same way.
- 2026-11-03 20:33:29: unsolved/10 was blocked because deepseek has max_usd set but its prices in config/models.toml are 0. The other 14 pending unsolved jobs also use DeepSeek, so they will likely block the same way. I can't edit the config. To fix this, fill in price_in_per_mtok and price_out_per_mtok for deepseek, then rerun those sections. Meanwhile I queued one replacement job on the unsolved sections using Codex and the local models (no DeepSeek) so the night isn't wasted. tier-claude is still failed: tiertest needs an LM (a bigram table) for skip_mode resolve.

## Events

- 2026-11-03 20:30:23 started
- 2026-11-03 20:30:23 tier-claude: start
- 2026-11-03 20:32:42 tier-claude: failed (exit 2)
- 2026-11-03 20:32:59 published: 5 file(s) to branch results
- 2026-11-03 20:33:05 supervisor: note added
- 2026-11-03 20:33:05 unsolved/10: blocked: model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_per_mtok
- 2026-11-03 20:33:20 published: 5 file(s) to branch results
- 2026-11-03 20:33:29 supervisor: note added
- 2026-11-03 20:33:29 supervisor: added sup1: swarm on 15 section(s) with codex,qwen-local,gemma-local
- 2026-11-03 20:33:29 unsolved/11: blocked: model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_per_mtok
- 2026-11-03 20:33:44 published: 5 file(s) to branch results
- 2026-11-03 20:33:49 unsolved/12: blocked: model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_per_mtok
- 2026-11-03 20:34:04 published: 5 file(s) to branch results
- 2026-11-03 20:34:08 unsolved/13: blocked: model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_per_mtok
- 2026-11-03 20:34:10 published: 5 file(s) to branch results
- 2026-11-03 20:34:15 unsolved/14: blocked: model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_per_mtok
- 2026-11-03 20:34:30 published: 5 file(s) to branch results
- 2026-11-03 20:34:34 unsolved/15: blocked: model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_per_mtok
- 2026-11-03 20:34:44 published: 5 file(s) to branch results
- 2026-11-03 20:34:48 unsolved/16: blocked: model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_per_mtok
- 2026-11-03 20:35:03 published: 5 file(s) to branch results
- 2026-11-03 20:35:08 unsolved/17: blocked: model deepseek: prices are 0 in config/models.toml, so its USD cap cannot work; fill in price_in_per_mtok / price_out_per_mtok

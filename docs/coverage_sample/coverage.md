# Coverage digest

Status: **complete**. Ledgers read: 3, failed or skipped: 0.

This lists what the recorded ledgers show was **tested with the recorded configuration**. It does not say any family is exhausted, counts may overlap across ledgers, and anything marked unknown was not recorded. Definitions are in `coverage.json` (`definitions`).

- searched overnight/<run>/<job>/ledger.sqlite for 2 run folder(s); no other location was searched

## section X

Target `820874ee9ac2`, 240 symbols, alphabet latin26, word breaks not used, transcription version unknown, 3 ledger(s). End-of-search check: 0 candidate(s) rechecked, 0 survived (a candidate with no recheck recorded has no final verdict).

| evaluator (executor version; oracle config unknown) | ledgers | stored rows | lean counted | logical (summed, may overlap) |
| --- | ---: | ---: | ---: | ---: |
| phase1-0.1.0 | 1 | 26 | 0 | 26 |
| phase1-0.1.0 | 2 | 27 | 199 | 226 |

Most-tested hypotheses (3 of 3):

| attempts | proposer | description | completion | where |
| ---: | --- | --- | --- | --- |
| 200 (lean) | sonnet | all 2-keys | incomplete (lean sweep stopped: max_attempts; 200 of at most 676 candidates processed) | 20260101-0000/sonnet_1 |
| 26 | codex | constant shifts | has a recorded pass; whether the enumeration finished is not recorded | 20260101-0000/codex_1 |
| 26 | codex | older run, no manifest | has a recorded pass; whether the enumeration finished is not recorded | 20260102-0000/codex_1 |

Recorded stop reasons (from report.json): codex_1: max_attempts.

Best recorded leads (recorded margin = combined - threshold at scoring time; not a probability):

| verdict | recorded margin | final check | description / ledger |
| --- | ---: | --- | --- |
| pass | +2.016 | not run | attempt 1 in `20260101-0000/codex_1/ledger.sqlite` |
| pass | +2.016 | not run | attempt 1 in `20260102-0000/codex_1/ledger.sqlite` |
| pass | +1.841 | not run | attempt 1 in `20260101-0000/sonnet_1/ledger.sqlite` |

## Limits of this digest

- The oracle configuration (alpha, null samples, near-miss rule) is not recorded in the ledgers: evaluator_config is unknown for every attempt.
- Lean-sweep summaries record a count, a completion flag and the proposal's description, not its spec; the completed subset of an incomplete sweep is unknown.
- Why an unfinished job stopped is recorded only in report.json beside the ledger, when present; invalid proposals never reach a ledger.
- No cross-job or cross-run deduplication exists, so summed totals may overlap.
- Transcription version is not recorded; identity is the target id only.
- History is not rescored: recorded thresholds and margins are shown as they were.

# Model tier test

Held-out synthetic program ciphers, difficulty `medium`, 3 cases per length, seed 0. Swarm arms: 5 rounds x 8 proposals, at most 20000 attempts per case. Runtime 365s.

Recovered = an attempt surviving the final check (Bonferroni over all of the arm's attempts on that case) decrypts to >= 90% of the plaintext. Each arm has its own ledger.

Model spend is logged in `reports/model_spend.sqlite` (kept across runs, so per-model `max_usd` caps are cumulative).

| arm | length | cases | recall | 95% CI | median attempts to solve | attempts | false passes | model calls | tokens in/out | USD |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |
| random_program:40 | 80 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | 160 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | all | 6 | 0.00 | [0.00, 0.39] | - | 192 | 0 | 0 | 0/0 | 0.0000 |
| claude-opus | 80 | 3 | 0.67 | [0.21, 0.94] | 2 | 11821 | 0 | 10 | 34784/27655 | 0.0000 |
| claude-opus | 160 | 3 | 0.33 | [0.06, 0.79] | 1 | 30001 | 0 | 11 | 42633/8773 | 0.0000 |
| claude-opus | all | 6 | 0.50 | [0.19, 0.81] | 1 | 41822 | 0 | 21 | 77417/36428 | 0.0000 |
| claude-sonnet | 80 | 3 | 0.33 | [0.06, 0.79] | 3534 | 10515 | 0 | 15 | 49877/16834 | 0.0000 |
| claude-sonnet | 160 | 3 | 0.33 | [0.06, 0.79] | 1 | 12586 | 0 | 11 | 39740/8208 | 0.0000 |
| claude-sonnet | all | 6 | 0.33 | [0.10, 0.70] | 1768 | 23101 | 0 | 26 | 89617/25042 | 0.0000 |

Per-case rows: `tiertest_cases.csv`. Ledgers: one `<arm>.sqlite` per arm.

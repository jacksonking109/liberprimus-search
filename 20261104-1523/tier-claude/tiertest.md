# Model tier test

Held-out synthetic program ciphers, difficulty `medium`, 3 cases per length, seed 0. Swarm arms: 5 rounds x 8 proposals, at most 20000 attempts per case. Runtime 697s.

Recovered = an attempt surviving the final check (Bonferroni over all of the arm's attempts on that case) decrypts to >= 90% of the plaintext. Each arm has its own ledger.

Model spend is logged in `reports/model_spend.sqlite` (kept across runs, so per-model `max_usd` caps are cumulative).

| arm | length | cases | recall | 95% CI | median attempts to solve | attempts | false passes | model calls | tokens in/out | USD |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |
| random_program:40 | 80 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | 160 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | all | 6 | 0.00 | [0.00, 0.39] | - | 192 | 0 | 0 | 0/0 | 0.0000 |
| claude-opus | 80 | 3 | 0.67 | [0.21, 0.94] | 1460 | 14097 | 0 | 11 | 36354/21503 | 0.0000 |
| claude-opus | 160 | 3 | 0.33 | [0.06, 0.79] | 1 | 22219 | 0 | 11 | 42556/9016 | 0.0000 |
| claude-opus | all | 6 | 0.50 | [0.19, 0.81] | 4 | 36316 | 0 | 22 | 78910/30519 | 0.0000 |
| claude-sonnet | 80 | 3 | 0.33 | [0.06, 0.79] | 648 | 10084 | 0 | 12 | 44876/16667 | 0.0000 |
| claude-sonnet | 160 | 1 | 1.00 | [0.21, 1.00] | 1 | 157 | 0 | 1 | 2712/1243 | 0.0000 |
| claude-sonnet | all | 4 | 0.50 | [0.15, 0.85] | 324 | 10241 | 0 | 13 | 47588/17910 | 0.0000 |

Per-case rows: `tiertest_cases.csv`. Ledgers: one `<arm>.sqlite` per arm.

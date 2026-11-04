# Model tier test

Held-out synthetic program ciphers, difficulty `medium`, 3 cases per length, seed 0. Swarm arms: 5 rounds x 8 proposals, at most 20000 attempts per case. Runtime 1055s.

Recovered = an attempt surviving the final check (Bonferroni over all of the arm's attempts on that case) decrypts to >= 90% of the plaintext. Each arm has its own ledger.

Model spend is logged in `reports/model_spend.sqlite` (kept across runs, so per-model `max_usd` caps are cumulative).

| arm | length | cases | recall | 95% CI | median attempts to solve | attempts | false passes | model calls | tokens in/out | USD |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |
| random_program:40 | 80 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | 160 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | all | 6 | 0.00 | [0.00, 0.39] | - | 192 | 0 | 0 | 0/0 | 0.0000 |
| claude-opus | 80 | 3 | 0.33 | [0.06, 0.79] | 955 | 37134 | 0 | 13 | 42379/22936 | 0.0000 |
| claude-opus | 160 | 3 | 0.33 | [0.06, 0.79] | 1 | 36561 | 0 | 10 | 37909/8249 | 0.0000 |
| claude-opus | all | 6 | 0.33 | [0.10, 0.70] | 478 | 73695 | 0 | 23 | 80288/31185 | 0.0000 |
| claude-sonnet | 80 | 3 | 0.00 | [0.00, 0.56] | - | 13986 | 0 | 15 | 54461/16965 | 0.0000 |
| claude-sonnet | 160 | 3 | 0.33 | [0.06, 0.79] | 1 | 9038 | 0 | 11 | 41316/9833 | 0.0000 |
| claude-sonnet | all | 6 | 0.17 | [0.03, 0.56] | 1 | 23024 | 0 | 26 | 95777/26798 | 0.0000 |

Per-case rows: `tiertest_cases.csv`. Ledgers: one `<arm>.sqlite` per arm.

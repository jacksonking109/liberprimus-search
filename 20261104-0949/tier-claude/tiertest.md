# Model tier test

Held-out synthetic program ciphers, difficulty `medium`, 3 cases per length, seed 0. Swarm arms: 5 rounds x 8 proposals, at most 20000 attempts per case. Runtime 399s.

Recovered = an attempt surviving the final check (Bonferroni over all of the arm's attempts on that case) decrypts to >= 90% of the plaintext. Each arm has its own ledger.

Model spend is logged in `reports/model_spend.sqlite` (kept across runs, so per-model `max_usd` caps are cumulative).

| arm | length | cases | recall | 95% CI | median attempts to solve | attempts | false passes | model calls | tokens in/out | USD |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |
| random_program:40 | 80 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | 160 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | all | 6 | 0.00 | [0.00, 0.39] | - | 192 | 0 | 0 | 0/0 | 0.0000 |
| claude-opus | 80 | 3 | 0.33 | [0.06, 0.79] | 3 | 12738 | 0 | 11 | 39227/28014 | 0.0000 |
| claude-opus | 160 | 1 | 1.00 | [0.21, 1.00] | 1 | 3 | 0 | 1 | 5367/697 | 0.0000 |
| claude-opus | all | 4 | 0.50 | [0.15, 0.85] | 2 | 12741 | 0 | 12 | 44594/28711 | 0.0000 |

Per-case rows: `tiertest_cases.csv`. Ledgers: one `<arm>.sqlite` per arm.

# Model tier test

Held-out synthetic program ciphers, difficulty `medium`, 3 cases per length, seed 0. Swarm arms: 5 rounds x 8 proposals, at most 20000 attempts per case. Runtime 141s.

Recovered = an attempt surviving the final check (Bonferroni over all of the arm's attempts on that case) decrypts to >= 90% of the plaintext. Each arm has its own ledger.

Model spend is logged in `reports/model_spend.sqlite` (kept across runs, so per-model `max_usd` caps are cumulative).

| arm | length | cases | recall | 95% CI | median attempts to solve | attempts | false passes | model calls | tokens in/out | USD |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |
| random_program:40 | 80 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | 160 | 3 | 0.00 | [0.00, 0.56] | - | 96 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | all | 6 | 0.00 | [0.00, 0.39] | - | 192 | 0 | 0 | 0/0 | 0.0000 |
| claude-opus | 80 | 3 | 0.33 | [0.06, 0.79] | 1 | 40796 | 0 | 3 | 9420/3157 | 0.0000 |
| claude-opus | 160 | 2 | 0.50 | [0.09, 0.91] | 1 | 38292 | 0 | 2 | 10243/1738 | 0.0000 |
| claude-opus | all | 5 | 0.40 | [0.12, 0.77] | 1 | 79088 | 0 | 5 | 19663/4895 | 0.0000 |

Per-case rows: `tiertest_cases.csv`. Ledgers: one `<arm>.sqlite` per arm.

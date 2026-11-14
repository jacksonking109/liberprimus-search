# Tier test reference (no models)

Reference run of the non-model arms: the bar a model arm has to clear. Reproduce with:

```
lpswarm tiertest --arms baseline,random_program:40,random_program:2000 --lengths 80,160 --cases 10
```

- `random_program:40` has the same number of proposals as a default model arm (5 rounds x 8): the per-proposal control a model must beat.
- `random_program:2000` and `baseline` show what cheap brute force achieves with far more attempts.
- The cases are random cipher programs. About a third of them fall inside the Phase 1 families (plain word keys, shifts), which is why the baseline recovers some.

Held-out synthetic program ciphers, difficulty `medium`, 10 cases per length, seed 0. Swarm arms: 5 rounds x 8 proposals, at most 20000 attempts per case. Runtime 106s.

Recovered = an attempt surviving the final check (Bonferroni over all of the arm's attempts on that case) decrypts to >= 90% of the plaintext. Each arm has its own ledger.

Model spend is logged in `reports/model_spend.sqlite` (kept across runs, so per-model `max_usd` caps are cumulative).

| arm | length | cases | recall | 95% CI | median attempts to solve | attempts | false passes | model calls | tokens in/out | USD |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: |
| baseline | 80 | 10 | 0.20 | [0.06, 0.51] | 5214 | 242310 | 0 | 0 | 0/0 | 0.0000 |
| baseline | 160 | 10 | 0.40 | [0.17, 0.69] | 694 | 242310 | 0 | 0 | 0/0 | 0.0000 |
| baseline | all | 20 | 0.30 | [0.15, 0.52] | 2878 | 484620 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | 80 | 10 | 0.00 | [0.00, 0.28] | - | 400 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | 160 | 10 | 0.10 | [0.02, 0.40] | 22 | 400 | 0 | 0 | 0/0 | 0.0000 |
| random_program:40 | all | 20 | 0.05 | [0.01, 0.24] | 22 | 800 | 0 | 0 | 0/0 | 0.0000 |
| random_program:2000 | 80 | 10 | 0.10 | [0.02, 0.40] | 189 | 18074 | 0 | 0 | 0/0 | 0.0000 |
| random_program:2000 | 160 | 10 | 0.30 | [0.11, 0.60] | 422 | 16189 | 0 | 0 | 0/0 | 0.0000 |
| random_program:2000 | all | 20 | 0.20 | [0.08, 0.42] | 306 | 34263 | 0 | 0 | 0/0 | 0.0000 |

Per-case rows and ledgers are written to the run's `--out` folder (not committed).

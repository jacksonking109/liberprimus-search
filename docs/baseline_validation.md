# Validation report (Phase 1 baseline)

Alphabet `latin26` (size 26), language `english`, held-out synthetic cases, difficulty `medium`, seed 0. Runtime 38.2s.

Oracle: alpha=0.01 per attempt, multiple-comparison adjustment `bonferroni` (alpha_eff = alpha / attempts so far on the target), n-gram order 4, dict weight 1.0, 3000 null samples per type per length, screen alpha 0.5.

Search space per case: true key hidden among decoys (500 word-derived decoys; full enumeration for caesar; columnar widths 2..6; 2000 running-key offsets).

## Recall and false-positive rate by family and length

Decisions use the **final check**: after the search, every in-run pass is re-scored at alpha / N_total (N_total = all attempts on that target), which is independent of search order. Recall = case recovered (a final pass with >= 90% similarity to the true plaintext). In-run recall uses the running alpha / i triage verdict instead. FPR = final passes with < 50% similarity / all wrong attempts. Partial = final passes at 50-90% similarity (near-solutions; not counted as FP).

| family | length | cases | recall | recall 95% CI | in-run recall | attempts | false passes | FPR | partial |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| caesar | 20 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 130 | 0 | 0.00e+00 | 0 |
| caesar | 40 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 130 | 0 | 0.00e+00 | 0 |
| caesar | 60 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 130 | 0 | 0.00e+00 | 0 |
| caesar | 100 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 130 | 0 | 0.00e+00 | 0 |
| caesar | 200 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 130 | 0 | 0.00e+00 | 0 |
| vigenere | 20 | 5 | 0.60 | [0.23, 0.88] | 0.60 | 7515 | 0 | 0.00e+00 | 0 |
| vigenere | 40 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 7515 | 0 | 0.00e+00 | 0 |
| vigenere | 60 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 7509 | 0 | 0.00e+00 | 0 |
| vigenere | 100 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 7515 | 0 | 0.00e+00 | 0 |
| vigenere | 200 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 7515 | 0 | 0.00e+00 | 0 |
| autokey | 20 | 5 | 0.80 | [0.38, 0.96] | 1.00 | 7512 | 0 | 0.00e+00 | 0 |
| autokey | 40 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 7512 | 0 | 0.00e+00 | 0 |
| autokey | 60 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 7509 | 0 | 0.00e+00 | 0 |
| autokey | 100 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 7515 | 0 | 0.00e+00 | 0 |
| autokey | 200 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 7515 | 0 | 0.00e+00 | 0 |
| running_key | 20 | 5 | 0.00 | [0.00, 0.43] | 0.60 | 10005 | 1 | 1.00e-04 | 0 |
| running_key | 40 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 10005 | 0 | 0.00e+00 | 0 |
| running_key | 60 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 10005 | 0 | 0.00e+00 | 0 |
| running_key | 100 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 10005 | 0 | 0.00e+00 | 0 |
| running_key | 200 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 10005 | 0 | 0.00e+00 | 0 |
| substitution | 20 | 5 | 0.80 | [0.38, 0.96] | 1.00 | 2490 | 0 | 0.00e+00 | 0 |
| substitution | 40 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 2491 | 0 | 0.00e+00 | 0 |
| substitution | 60 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 2497 | 0 | 0.00e+00 | 0 |
| substitution | 100 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 2484 | 0 | 0.00e+00 | 0 |
| substitution | 200 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 2499 | 0 | 0.00e+00 | 1 |
| columnar | 20 | 5 | 0.80 | [0.38, 0.96] | 0.80 | 4360 | 0 | 0.00e+00 | 0 |
| columnar | 40 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 4360 | 0 | 0.00e+00 | 0 |
| columnar | 60 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 4360 | 0 | 0.00e+00 | 0 |
| columnar | 100 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 4360 | 0 | 0.00e+00 | 1 |
| columnar | 200 | 5 | 1.00 | [0.57, 1.00] | 1.00 | 4360 | 0 | 0.00e+00 | 1 |

## Oracle null calibration check

Fresh null samples (different seed from calibration), scored at the unadjusted alpha (attempt_count = 1). Threshold is the max over null types, so the worst type should sit near alpha and the others at or below it.

Stated tolerance: 3 binomial standard errors, counting both the test sample and the calibration sample: tol = 3 * sqrt(alpha(1-alpha)(1/n_test + 1/n_calib)). Pass = every type's FPR <= alpha + tol and |worst-type FPR - alpha| <= tol.

| length | alpha | worst-type FPR | tolerance | within tolerance |
| ---: | ---: | ---: | ---: | --- |
| 20 | 0.01 | 0.0075 | 0.0086 | yes |
| 40 | 0.01 | 0.0150 | 0.0086 | yes |
| 60 | 0.01 | 0.0125 | 0.0086 | yes |
| 100 | 0.01 | 0.0120 | 0.0086 | yes |
| 200 | 0.01 | 0.0040 | 0.0086 | yes |

| length | null type | n | false pos | FPR | 95% CI |
| ---: | --- | ---: | ---: | ---: | --- |
| 20 | shuffled | 2000 | 15 | 0.0075 | [0.0046, 0.0123] |
| 20 | random | 2000 | 0 | 0.0000 | [0.0000, 0.0019] |
| 20 | wrong_key | 2000 | 8 | 0.0040 | [0.0020, 0.0079] |
| 40 | shuffled | 2000 | 30 | 0.0150 | [0.0105, 0.0213] |
| 40 | random | 2000 | 0 | 0.0000 | [0.0000, 0.0019] |
| 40 | wrong_key | 2000 | 12 | 0.0060 | [0.0034, 0.0105] |
| 60 | shuffled | 2000 | 25 | 0.0125 | [0.0085, 0.0184] |
| 60 | random | 2000 | 0 | 0.0000 | [0.0000, 0.0019] |
| 60 | wrong_key | 2000 | 11 | 0.0055 | [0.0031, 0.0098] |
| 100 | shuffled | 2000 | 15 | 0.0075 | [0.0046, 0.0123] |
| 100 | random | 2000 | 0 | 0.0000 | [0.0000, 0.0019] |
| 100 | wrong_key | 2000 | 24 | 0.0120 | [0.0081, 0.0178] |
| 200 | shuffled | 2000 | 4 | 0.0020 | [0.0008, 0.0051] |
| 200 | random | 2000 | 0 | 0.0000 | [0.0000, 0.0019] |
| 200 | wrong_key | 2000 | 8 | 0.0040 | [0.0020, 0.0079] |

**Null calibration overall: PASS.**

## Ledger

`reports/validation.sqlite` (not committed): hypothesis=150, key_candidate=14524, attempt=160068, result=160068, target=150, corpus_item=0, budget_event=0

Files: `validation.csv` (table above), `validation_cases.csv` (per case), `null_fpr.csv`, `validation.json` (everything).

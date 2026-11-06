# Running sums with a multiplicatively keyed step

**EXPLORATORY; no oracle, no models.** See the module docstring for the reasoning.

## Can the family reproduce the repeat signature? (English plaintext, uniform non-zero key, 6 windows of 5000)

| zero rune (the one whose step is zero) | lag 1 | lags 2-8 | unigram IC | first-difference IC | full match |
| --- | ---: | --- | ---: | ---: | --- |
| EA | 0.22 | 0.98-1.07 | 1.00 | 1.02 | yes |
| F | 0.70 | 0.94-1.06 | 1.00 | 1.00 | no |
| N | 1.80 | 0.92-1.00 | 1.00 | 1.02 | no |

## Is the zero step triggered by plaintext EA? (position of the doubles' second runes in words)

86 doubles; second rune word-initial / internal / final / single: {'initial': 21, 'internal': 47, 'final': 18, 'single': 0}.

| compared with | proportions | chi-square | p |
| --- | --- | ---: | ---: |
| EA in English words | {'initial': 0.068, 'internal': 0.895, 'final': 0.038, 'single': 0.0} | 118.6 | 0.0000 |
| all runes of the real text | {'initial': 0.204, 'internal': 0.585, 'final': 0.204, 'single': 0.007} | 1.5 | 0.6638 |

## IC sweep: a[t]^-1 or a[t] times the first difference, 8 sequences x 3000 offsets, first 600 runes

Flag: IC x 29 >= 1.25 and above the maximum of 3 shuffled copies of the section. Language gives about 1.6-2.0; noise about 1.1.

| section | best IC | null max | best sequence / form / offset | flag |
| ---: | ---: | ---: | --- | --- |
| 10 | 1.100 | 1.075 | pi_digits / a^-1 * step / 885 | no |
| 12 | 1.102 | 1.075 | pi_digits / a * step / 2906 | no |
| 13 | 1.200 | 1.132 | pi_digits / a^-1 * step / 2639 | no |
| 14 | 1.095 | 1.067 | e_digits / a * step / 2055 | no |
| 16 | 1.128 | 1.080 | e_digits / a^-1 * step / 1424 | no |
| 17 | 1.074 | 1.085 | primes / a^-1 * step / 2302 | no |
| 18 | 1.088 | 1.081 | prime_totients / a * step / 342 | no |
| 20 | 1.087 | 1.075 | pi_digits / a^-1 * step / 2442 | no |
| 22 | 1.100 | 1.069 | pi_digits / a * step / 513 | no |
| 24 | 1.133 | 1.086 | e_digits / a^-1 * step / 113 | no |
| 25 | 1.192 | 1.153 | e_digits / a * step / 2919 | no |

Controls (3000 runes):

| case | best IC | best sequence / offset | found |
| --- | ---: | --- | --- |
| English through primes x n, offset 777 | 1.772 | primes / 778 | True |
| English through Fibonacci x n, offset 123 | 1.776 | fibonacci / 12 | True |
| iid noise | 1.064 | prime_totients / 934 |  |

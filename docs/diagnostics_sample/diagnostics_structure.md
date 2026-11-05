# Structure diagnostics

**EXPLORATORY: units chosen after inspecting the data; a p-value here is not confirmation.** No models, no oracle, no decryption scoring.

## Differences, bigrams, homogeneity

Sections [10, 12, 13, 14, 16, 17, 18, 20, 22, 24, 25]; 199 shuffles; 12605 bigrams.

| section | runes | IC x29 | if uniform | adjacent equal | expected | within word | across boundary |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 729 | 1.03 | 1.04 | 4 | 26 | 2 | 2 |
| 12 | 693 | 1.04 | 1.04 | 4 | 25 | 2 | 2 |
| 13 | 333 | 1.08 | 1.08 | 1 | 12 | 1 | 0 |
| 14 | 1729 | 1.02 | 1.02 | 9 | 61 | 7 | 2 |
| 16 | 1894 | 1.02 | 1.01 | 10 | 66 | 10 | 0 |
| 17 | 1021 | 1.02 | 1.03 | 11 | 36 | 9 | 2 |
| 18 | 1433 | 1.01 | 1.02 | 13 | 50 | 8 | 5 |
| 20 | 1468 | 1.01 | 1.02 | 11 | 51 | 8 | 3 |
| 22 | 2474 | 1.02 | 1.01 | 16 | 87 | 12 | 4 |
| 24 | 534 | 1.02 | 1.05 | 2 | 19 | 2 | 0 |
| 25 | 308 | 1.07 | 1.09 | 3 | 11 | 1 | 2 |
| 3 | 157 | 1.70 | 1.18 | 7 | 9 | 2 | 5 |
| 7 | 629 | 1.87 | 1.04 | 15 | 41 | 12 | 3 |
| 9 | 89 | 1.97 | 1.31 | 3 | 6 | 2 | 1 |
| 27 | 94 | 2.15 | 1.30 | 1 | 7 | 1 | 0 |

Rows after the unsolved set are readable sections, for comparison only.

Differences d = c[i] - c[i-1] (pooled): max |z| over 58 bins 10.89, p 0.005; given the observed number of repeats: max |z| over the 28 non-zero d 2.72 (p 0.155), chi-square of the non-zero d p 0.060, enrichment of d = +-1, +-2 p 0.230.

| d | observed | shuffle mean | z | z given the repeat count |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 84 | 432.0 | -10.9 |  |
| 1 | 448 | 434.6 | +0.7 | +0.0 |
| 2 | 493 | 434.9 | +2.8 | +2.1 |
| 3 | 434 | 432.8 | +0.1 | -0.5 |
| 4 | 429 | 437.5 | -0.4 | -0.9 |
| 5 | 430 | 433.6 | -0.2 | -0.8 |
| 6 | 417 | 433.0 | -0.8 | -1.3 |
| 7 | 454 | 435.9 | +0.9 | +0.3 |
| 8 | 409 | 435.4 | -1.2 | -1.8 |
| 9 | 497 | 434.2 | +3.5 | +2.7 |
| 10 | 480 | 434.4 | +2.1 | +1.5 |
| 11 | 440 | 435.7 | +0.2 | -0.4 |
| 12 | 433 | 435.1 | -0.1 | -0.7 |
| 13 | 492 | 434.3 | +2.7 | +2.1 |
| 14 | 461 | 435.9 | +1.2 | +0.6 |
| 15 | 460 | 435.1 | +1.2 | +0.6 |
| 16 | 435 | 434.4 | +0.0 | -0.6 |
| 17 | 395 | 433.4 | -1.9 | -2.4 |
| 18 | 425 | 435.2 | -0.5 | -1.1 |
| 19 | 467 | 433.7 | +1.6 | +1.0 |
| 20 | 454 | 436.4 | +0.8 | +0.2 |
| 21 | 455 | 435.4 | +1.0 | +0.3 |
| 22 | 407 | 438.2 | -1.5 | -2.0 |
| 23 | 476 | 432.8 | +2.0 | +1.4 |
| 24 | 457 | 434.9 | +1.1 | +0.5 |
| 25 | 456 | 436.0 | +1.1 | +0.4 |
| 26 | 443 | 431.3 | +0.6 | -0.0 |
| 27 | 455 | 433.6 | +1.1 | +0.4 |
| 28 | 419 | 435.2 | -0.7 | -1.3 |

Repeats (d = 0): within word 62 (shuffle mean 336, z -15.6); across a word boundary 22 (shuffle mean 96, z -8.3).

Transition table 29x29: chi-square vs independence p 0.005; diagonal share of chi-square 0.26; chi-square without the diagonal p 0.340; cells with count <= 1: 4 (0 off the diagonal; shuffle mean 0.01, p 0.005); diagonal 84 vs 430 expected.

Homogeneity across sections: frequencies p 0.980, difference histograms p 0.115. Per-section z (frequency / difference): 10: -1.1/+0.3, 12: +0.3/+0.9, 13: -0.4/+0.5, 14: -0.4/+1.0, 16: -1.0/-0.3, 17: -0.8/-0.5, 18: -1.2/+1.8, 20: -0.8/-0.3, 22: +1.0/+0.1, 24: -1.7/-1.3, 25: -0.6/+2.3.

## Dependence and transform scans

Sections [10, 12, 13, 14, 16, 17, 18, 20, 22, 24, 25]; 199 shuffles.

**Mutual information, per section x lag (1-64)**: 704 units, max z 3.36, p (max over units) 0.290. Top units:

```
{"lag": 4, "observed": -0.031523675383136496, "section": 25, "z": 3.3633752836982937}
{"lag": 61, "observed": -0.18011260947014418, "section": 25, "z": 3.247285548192255}
{"lag": 32, "observed": 0.12919849230331337, "section": 12, "z": 2.607945327713157}
{"lag": 14, "observed": -0.07768766782399417, "section": 25, "z": 2.5069602786059626}
{"lag": 47, "observed": 0.05903952898117895, "section": 16, "z": 2.498397572655527}
```

**Mutual information, sections pooled, per lag**: 64 units, max z 9.06, p (max over units) 0.005. Top units:

```
{"lag": 1, "mutual_information_nats": 0.050494306997932975, "z": 9.057386618504308}
{"lag": 7, "mutual_information_nats": 0.0352925426447272, "z": 2.1641327129171644}
{"lag": 57, "mutual_information_nats": 0.036366977066657896, "z": 1.8965997964689578}
{"lag": 41, "mutual_information_nats": 0.035661134995667296, "z": 1.7348004323440103}
{"lag": 15, "mutual_information_nats": 0.0344443179984777, "z": 1.6267648206304763}
```

**Transform IC, per section x lag x r**: 4928 units, max z 7.07, p (max over units) 0.005. Top units:

```
{"lag": 1, "observed": 1.0360182735369732, "r": 28, "section": 22, "z": 7.071438568755985}
{"lag": 1, "observed": 1.044238683127572, "r": 28, "section": 14, "z": 6.116924916883162}
{"lag": 1, "observed": 1.0405268778765933, "r": 28, "section": 16, "z": 5.718042999712547}
{"lag": 1, "observed": 1.0445901633250299, "r": 28, "section": 20, "z": 4.404346782273513}
{"lag": 8, "observed": 1.0323913774432134, "r": 20, "section": 16, "z": 4.333702872586704}
```

**Transform IC, sections pooled**: 448 units, max z 13.34, p (max over units) 0.005. Top units:

```
{"ic29": 1.0266839075368648, "lag": 1, "r": 28, "z": 13.340437074023198}
{"ic29": 1.0043438135558345, "lag": 11, "r": 28, "z": 3.6136061590986652}
{"ic29": 1.0042741296532804, "lag": 8, "r": 7, "z": 2.9831803210407237}
{"ic29": 1.00397268774146, "lag": 9, "r": 17, "z": 2.9341228481232675}
{"ic29": 1.0040467814642116, "lag": 16, "r": 7, "z": 2.853365254041338}
```

mutual information is the plug-in estimate (nats); z is against the shuffle null; transforms use r = b/a, which covers every a*c[i-k] + b*c[i] up to relabelling

## Dependence and transform scans, equal pairs excluded (what is left once the repeat shortage is removed)

Sections [10, 12, 13, 14, 16, 17, 18, 20, 22, 24, 25]; 199 shuffles.

**Mutual information, per section x lag (1-64)**: 704 units, max z 3.28, p (max over units) 0.345. Top units:

```
{"lag": 4, "observed": 0.005473488857200115, "section": 25, "z": 3.2770156471094234}
{"lag": 31, "observed": -0.022848301351028777, "section": 13, "z": 2.9828564295042463}
{"lag": 61, "observed": -0.1566088736741349, "section": 25, "z": 2.626253950762974}
{"lag": 32, "observed": 0.16380175386437168, "section": 12, "z": 2.4746666763498704}
{"lag": 26, "observed": 0.07285182377818339, "section": 22, "z": 2.2786193179864394}
```

**Mutual information, sections pooled, per lag**: 64 units, max z 2.12, p (max over units) 0.655. Top units:

```
{"lag": 7, "mutual_information_nats": 0.07034529333440018, "z": 2.1221724364687096}
{"lag": 41, "mutual_information_nats": 0.07094450960904608, "z": 1.8561993263872991}
{"lag": 57, "mutual_information_nats": 0.0712921937603787, "z": 1.7849880337430253}
{"lag": 16, "mutual_information_nats": 0.06978592407649875, "z": 1.6281549992665807}
{"lag": 4, "mutual_information_nats": 0.06916556853475728, "z": 1.6218712729915312}
```

**Transform IC, per section x lag x r**: 4928 units, max z 4.09, p (max over units) 0.905. Top units:

```
{"lag": 8, "observed": 1.032558036691929, "r": 20, "section": 16, "z": 4.086198033191312}
{"lag": 9, "observed": 1.0345171173803092, "r": 23, "section": 14, "z": 3.9160472802594435}
{"lag": 16, "observed": 1.0411582274202271, "r": 6, "section": 18, "z": 3.8696054468729333}
{"lag": 6, "observed": 1.1146697998046875, "r": 10, "section": 24, "z": 3.759096030307274}
{"lag": 8, "observed": 1.177106576331697, "r": 17, "section": 13, "z": 3.660454014068271}
```

**Transform IC, sections pooled**: 448 units, max z 3.15, p (max over units) 0.850. Top units:

```
{"ic29": 1.0042206788155479, "lag": 12, "r": 2, "z": 3.1488749357220676}
{"ic29": 1.0042340027589303, "lag": 16, "r": 7, "z": 2.863657263640396}
{"ic29": 1.0042491102662612, "lag": 4, "r": 21, "z": 2.7859662216533247}
{"ic29": 1.004251830347433, "lag": 8, "r": 7, "z": 2.7216723001477825}
{"ic29": 1.0037066880186745, "lag": 16, "r": 10, "z": 2.622754491899533}
```

mutual information is the plug-in estimate (nats); z is against the shuffle null; transforms use r = b/a, which covers every a*c[i-k] + b*c[i] up to relabelling

## What each diagnostic can see (synthetic)

SYNTHETIC: English plaintext (training split) through known mechanisms; says what each diagnostic can see, not what the real sections are. 99 shuffles per case, alpha 0.05; no multiplicity correction across the eight columns.

| mechanism | length | differences: any bin | differences: non-zero d | differences: near-zero d | transitions | dependence (MI) | transform scan | dependence, repeats excluded | transform, repeats excluded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plaintext (no cipher) | 334 | 0.090 | **0.010** | 0.050 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| plaintext (no cipher) | 534 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| plaintext (no cipher) | 1022 | **0.010** | **0.010** | **0.030** | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| plaintext (no cipher) | 1434 | **0.010** | **0.010** | 0.080 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| iid noise | 334 | 0.670 | 0.400 | 0.610 | 0.190 | 0.170 | 0.940 | 0.250 | 0.890 |
| iid noise | 534 | 0.270 | 0.590 | 0.100 | 0.590 | 0.080 | 0.080 | 0.280 | 0.310 |
| iid noise | 1022 | 0.210 | 0.340 | 0.670 | 0.300 | 0.730 | 0.850 | 0.970 | 0.540 |
| iid noise | 1434 | 0.540 | 0.930 | 0.570 | 0.160 | 0.990 | 0.140 | 1.000 | 0.450 |
| neighbour feedback (add) | 334 | **0.010** | 0.440 | 0.650 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| neighbour feedback (add) | 534 | **0.010** | 0.940 | 0.290 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| neighbour feedback (add) | 1022 | **0.010** | 0.260 | 0.990 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| neighbour feedback (add) | 1434 | **0.010** | 0.470 | 0.600 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| chain / plaintext autokey | 334 | 0.330 | 0.580 | 0.200 | **0.010** | 0.100 | 0.570 | **0.020** | 0.200 |
| chain / plaintext autokey | 534 | 0.350 | 0.290 | 0.360 | **0.010** | **0.010** | **0.040** | **0.010** | 0.080 |
| chain / plaintext autokey | 1022 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| chain / plaintext autokey | 1434 | **0.010** | **0.010** | 0.090 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| progressive key (arithmetic) | 334 | 0.070 | **0.010** | 0.870 | **0.020** | 0.130 | **0.020** | 0.100 | **0.020** |
| progressive key (arithmetic) | 534 | **0.010** | **0.010** | 1.000 | **0.030** | **0.010** | **0.010** | **0.010** | **0.010** |
| progressive key (arithmetic) | 1022 | **0.010** | **0.010** | 1.000 | 0.050 | **0.010** | **0.010** | **0.010** | **0.010** |
| progressive key (arithmetic) | 1434 | **0.010** | **0.010** | 1.000 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| prime stream | 334 | 0.440 | 0.360 | 1.000 | 0.850 | 0.450 | 1.000 | 0.700 | 0.990 |
| prime stream | 534 | 0.090 | 0.350 | 0.980 | 0.510 | 0.260 | 0.830 | 0.800 | 0.530 |
| prime stream | 1022 | 0.110 | **0.030** | 0.620 | 0.890 | 0.110 | 0.280 | 0.230 | 0.430 |
| prime stream | 1434 | 0.150 | 0.750 | 0.360 | 0.080 | 0.260 | 0.670 | 0.230 | 0.150 |
| Hill 2x2 blocks | 334 | **0.010** | 0.160 | 0.080 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| Hill 2x2 blocks | 534 | **0.010** | **0.020** | **0.020** | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| Hill 2x2 blocks | 1022 | **0.010** | **0.030** | 0.570 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| Hill 2x2 blocks | 1434 | **0.010** | **0.010** | 0.230 | **0.010** | **0.010** | **0.010** | **0.010** | **0.010** |
| periodic key, length 37 | 334 | 0.130 | 0.600 | 0.680 | 0.560 | 0.660 | 0.270 | 0.360 | 0.270 |
| periodic key, length 37 | 534 | 0.590 | 0.170 | 0.310 | 0.490 | **0.020** | **0.010** | **0.020** | **0.010** |
| periodic key, length 37 | 1022 | 0.380 | 0.090 | 0.730 | **0.010** | 0.060 | 0.470 | 0.060 | 0.570 |
| periodic key, length 37 | 1434 | **0.010** | 0.080 | 0.990 | **0.010** | 0.180 | 0.100 | 0.450 | 0.220 |

Bold = detected at this level. A real section that shows nothing is only evidence against mechanisms the row above detects at its length.


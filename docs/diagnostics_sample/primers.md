# Cicada identifiers as autokey primers and repeating keys

**EXPLORATORY; no models.**

57 distinct key lists from 7 strings (key ID, long ID, 845145127, 3301, CICADA ...), each forward and reversed, x 24 cipher settings = 1368 candidates per section. Score: mean English bigram log-likelihood of the decryption; the null is the best candidate on the section shuffled (40 times).

Planted control (English, autokey, primer 7A35090F / base36): round trip True, best candidate is the planted one: True (score -2.590).

| section | runes | best | null mean | null max | p | best candidate |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | 729 | -4.736 | -4.718 | -4.619 | 0.683 | CICADA3301 / base36 | repeat add map=reverse F=literal |
| 12 | 693 | -4.679 | -4.711 | -4.662 | 0.122 | 845145127 / ascii | repeat beaufort map=reverse F=literal |
| 13 | 333 | -4.629 | -4.583 | -4.460 | 0.878 | 3301 / number | repeat beaufort map=reverse F=literal |
| 14 | 1729 | -4.848 | -4.815 | -4.752 | 0.951 | CICADA3301 / position | repeat beaufort map=reverse F=literal |
| 16 | 1894 | -4.864 | -4.817 | -4.753 | 1.000 | 7A35090F reversed / ascii | repeat sub map=identity F=literal |
| 17 | 1021 | -4.781 | -4.778 | -4.726 | 0.488 | CICADA3301845145127 / ascii | repeat sub map=reverse F=literal |
| 18 | 1433 | -4.812 | -4.803 | -4.741 | 0.683 | 3301 reversed / ascii | autokey beaufort map=identity F=literal |
| 20 | 1468 | -4.819 | -4.806 | -4.713 | 0.683 | 3301 reversed / hex bytes | autokey sub map=reverse F=keyed |
| 22 | 2474 | -4.838 | -4.831 | -4.776 | 0.634 | CICADA3301845145127 / base36 | autokey beaufort map=reverse F=keyed |
| 24 | 534 | -4.701 | -4.687 | -4.631 | 0.659 | 3301 / ascii | autokey beaufort map=reverse F=literal |
| 25 | 308 | -4.548 | -4.579 | -4.472 | 0.244 | 181F01E57A35090F reversed / hex bytes | repeat beaufort map=reverse F=literal |

Sections with the best candidate above every shuffle: 0 of 11 (expected about 0.3 by chance).

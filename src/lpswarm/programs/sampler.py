"""Random cipher-program sampler.

Used for (a) synthetic program ciphers in the tier test, and (b) the non-LLM
`random_program` control generator. A model-driven generator only counts as
useful if it beats both this and the Phase 1 brute force at equal attempt budget.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np

from lpswarm.programs.sequences import SEQUENCES
from lpswarm.programs.spec import COMBINES

# (probability of: skip rule, reverse map, reverse text, columnar transposition)
_EXTRAS = {"easy": (0.0, 0.0, 0.0, 0.0), "medium": (0.3, 0.3, 0.1, 0.1),
           "hard": (0.5, 0.5, 0.2, 0.25)}


def sample_spec(rng: np.random.Generator, n: int, words: Sequence[np.ndarray] | None = None,
                difficulty: str = "medium", length: int | None = None,
                structure: bool = False) -> dict:
    """A raw (uncompiled) spec with integer symbols only. `structure=True` also draws the
    grid / rail-fence / decimation transpositions (off by default so the control's
    reference numbers stay comparable)."""
    p_skip, p_map, p_rev, p_tr = _EXTRAS[difficulty]
    u = rng.random()
    if u < 0.10:
        stream = {"kind": "constant", "value": int(rng.integers(1, n))}
    elif u < 0.50:
        if words and rng.random() < 0.6:
            cand = [w for w in words if 3 <= len(w) <= 9]
            key = [int(x) for x in cand[int(rng.integers(len(cand)))]]
        else:
            key = [int(x) for x in rng.integers(0, n, int(rng.integers(3, 9)))]
        stream = {"kind": "repeat", "key": key}
    elif u < 0.65:
        if words and rng.random() < 0.6:
            cand = [w for w in words if 3 <= len(w) <= 7]
            primer = [int(x) for x in cand[int(rng.integers(len(cand)))]]
        else:
            primer = [int(x) for x in rng.integers(0, n, int(rng.integers(1, 6)))]
        stream = {"kind": "autokey", "primer": primer,
                  "source": "plaintext" if rng.random() < 0.7 else "ciphertext"}
    else:
        names = sorted(SEQUENCES)
        stream = {"kind": "sequence", "name": names[int(rng.integers(len(names)))],
                  "offset": int(rng.integers(0, 50)), "scale": int(rng.choice([1, 1, 1, -1, 2, 3])),
                  "add": int(rng.integers(0, n))}
    spec: dict = {"stream": stream, "combine": COMBINES[int(rng.integers(len(COMBINES)))]}
    if rng.random() < p_map:
        spec["map"] = "reverse"
    if rng.random() < p_skip:
        spec["skip"] = [int(rng.integers(0, n))]
    if rng.random() < p_rev:
        spec["reverse_text"] = True
    if rng.random() < p_tr:
        if structure and rng.random() < 0.6:
            from lpswarm.programs.spec import GRID_READS
            pick = int(rng.integers(3))
            if pick == 0:
                spec["transpose"] = {"grid": {"width": int(rng.integers(2, 40)),
                                              "read": GRID_READS[int(rng.integers(len(GRID_READS)))]}}
            elif pick == 1:
                spec["transpose"] = {"railfence": {"rails": int(rng.integers(2, 9))}}
            else:   # a step coprime to the text length when it is known
                import math
                k = int(rng.integers(2, 60))
                while length and math.gcd(k, length) != 1:
                    k += 1
                spec["transpose"] = {"decimate": {"step": k}}
        else:
            w = int(rng.integers(3, 6))
            if length is None or w <= length:
                spec["transpose"] = {"columnar": [int(x) for x in rng.permutation(w)]}
    return spec

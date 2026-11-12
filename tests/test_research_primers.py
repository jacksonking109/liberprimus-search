import numpy as np

from lpswarm import research_primers as P
from lpswarm.alphabet import get_alphabet
from lpswarm.programs import spec as S
from lpswarm.research_packets import ALPHABET

ALPHA = get_alphabet(ALPHABET)


def test_matches_program_language():
    keys = P.candidate_keys(ALPHA)
    c = np.random.default_rng(0).integers(0, 29, 200)
    for _lab, key in keys[:4]:
        for kind, how, rmap, skip in P.GRID:
            st = {"kind": "autokey", "primer": list(key), "source": "plaintext"} if kind == "autokey" else {"kind": "repeat", "key": list(key)}
            sp = S.compile_spec({"stream": st, "combine": how, "map": "reverse" if rmap else "identity", "skip": [0] if skip else []}, ALPHA)
            assert (np.asarray(S.decrypt(c, sp, 29)) == P.decrypt(c, key, kind, how, rmap, skip)).all()


def test_round_trip_and_key_id_is_a_candidate():
    keys = P.candidate_keys(ALPHA)
    labels = [lab for lab, _ in keys]
    assert "7A35090F / base36" in labels and "181F01E57A35090F / hex bytes" in labels
    p = np.random.default_rng(1).integers(1, 29, 150)   # no F: a literal F in the plaintext need not round trip
    key = keys[0][1]
    for kind, how, rmap, skip in P.GRID:
        if skip:        # literal-F settings only round trip when no other symbol encrypts to F (as in programs.spec)
            continue
        c = P.encrypt(p, key, kind, how, rmap, skip)
        assert (P.decrypt(c, key, kind, how, rmap, skip) == p).all()

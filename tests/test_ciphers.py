import numpy as np
import pytest

from lpswarm.alphabet import Alphabet
from lpswarm.ciphers import REGISTRY, VARIANTS, get_family
from lpswarm.ciphers.families import Substitution
from lpswarm.textgen.corpus import training_text

ALPHABETS = [Alphabet.latin26(), Alphabet.rune_like(29, corpus=training_text()),
             Alphabet.rune_like(33, extra_tokens=["TH", "NG", "EA", "OE", "ST", "IO", "AE"])]


def _rand_pt(rng, n, L):
    return rng.integers(0, n, size=L).astype(np.int16)


@pytest.mark.parametrize("alpha", ALPHABETS, ids=lambda a: a.name)
@pytest.mark.parametrize("name", sorted(REGISTRY))
@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_round_trip(alpha, name, difficulty):
    fam = get_family(name)
    n = alpha.size
    rng = np.random.default_rng(1)
    words = [alpha.encode(w) for w in ["CIPHER", "PRIMUS", "KEY", "DIVINITY", "WITHIN"]]
    for L in (1, 7, 31, 100, 257):
        pt = _rand_pt(rng, n, L)
        if name == "running_key":
            key = _rand_pt(rng, n, L + 50)
            grid = fam.param_grid(L, key, variants=VARIANTS)
        else:
            key = fam.random_key(rng, n, difficulty, words=words, length=L)
            grid = fam.param_grid(L, key)
        for params in grid[:5]:
            ct = fam.encrypt(pt, key, n, **params)
            assert ct.shape == pt.shape
            assert ct.min(initial=0) >= 0 and ct.max(initial=0) < n
            np.testing.assert_array_equal(fam.decrypt(ct, key, n, **params), pt)


@pytest.mark.parametrize("name", ["caesar", "vigenere", "autokey", "columnar"])
def test_enumeration_contains_random_key(name):
    fam = get_family(name)
    n = 26
    rng = np.random.default_rng(3)
    if name == "columnar":
        key = fam.random_key(rng, n, "easy", length=60)
        keys = set(fam.enumerate_keys(n, 60, max_width=5))
        assert fam.enumeration_size(n, 60, max_width=5) == len(keys)
    else:
        key = fam.random_key(rng, n, "easy") if name == "caesar" else (3, 17)
        keys = set(map(lambda k: k if isinstance(k, int) else tuple(k),
                       fam.enumerate_keys(n, 60, max_key_len=2)))
    assert key in keys


def test_known_vectors():
    a = Alphabet.latin26()
    pt = a.encode("ATTACKATDAWN")
    v = get_family("vigenere")
    assert a.decode(v.encrypt(pt, tuple(a.encode("LEMON")), 26)) == "LXFOPVEFRNHR"
    c = get_family("caesar")
    assert a.decode(c.encrypt(a.encode("HELLO"), 3, 26)) == "KHOOR"
    s = Substitution.keyword_perm(a.encode("ZEBRAS"), 26)
    assert a.decode(s[:8]) == "ZEBRASCD"
    col = get_family("columnar")
    key = col.key_from_word(a.encode("ZEBRAS"), 26)
    assert key == (5, 2, 1, 3, 0, 4)
    ct = col.encrypt(a.encode("WEAREDISCOVEREDFLEEATONCE"), key, 26)
    assert a.decode(ct) == "EVLNACDTESEAROFODEECWIREE"


def test_autokey_vector():
    a = Alphabet.latin26()
    ak = get_family("autokey")
    ct = ak.encrypt(a.encode("ATTACKATDAWN"), tuple(a.encode("QUEENLY")), 26)
    assert a.decode(ct) == "QNXEPVYTWTWP"


def test_alphabet_encode_decode():
    a = Alphabet.latin26()
    assert a.decode(a.encode("Hello, World! 123")) == "HELLOWORLD"
    r = Alphabet.rune_like(29, extra_tokens=["TH", "NG", "EA"])
    arr = r.encode("the king eats")
    assert r.decode(arr) == "THEKINGEATS"
    assert len(arr) == 8  # TH E K I NG EA T S
    assert r.encode(r.decode(arr, glyphs=True)).tolist() == arr.tolist()


def test_alphabet_from_json(tmp_path):
    p = tmp_path / "alpha.json"
    p.write_text('{"name": "tiny", "tokens": ["A", "B", "TH"], "glyphs": ["x", "y", "z"],'
                 ' "aliases": {"C": "B"}}', encoding="utf-8")
    a = Alphabet.from_json(p)
    assert a.size == 3
    assert a.decode(a.encode("ACTH")) == "ABTH"
    assert a.decode(a.encode("xyz"), glyphs=True) == "xyz"

import numpy as np

from lpswarm import research_fibpage as F


def _body():
    page = np.repeat([1, 2, 3], 120)
    n = len(page)
    idx = np.arange(n) % 120
    return {"c": np.random.default_rng(0).integers(0, 29, n), "page": page, "page_start": idx == 0, "line_start": idx % 12 == 0, "word_start": idx % 4 == 0}


def test_pisano_period_and_fib():
    assert list(F.FIB14[:8]) == [0, 1, 1, 2, 3, 5, 8, 13]
    a, b = 0, 1
    for _ in range(14):
        a, b = b, (a + b) % 29
    assert (a, b) == (0, 1)


def test_unit_index_restarts_and_skips_literal():
    starts = np.array([1, 0, 0, 1, 0, 0], dtype=bool)
    assert list(F._unit_index(starts, None)) == [0, 1, 2, 0, 1, 2]
    lit = np.array([0, 1, 0, 0, 0, 0], dtype=bool)
    assert list(F._unit_index(starts, lit))[2:] == [1, 0, 1, 2]       # the literal F does not advance the key


def test_encrypt_restart_round_trips_with_decrypt_batch():
    b = _body()
    p = np.random.default_rng(1).integers(0, 29, len(b["c"]))
    c = F.encrypt_restart(p, b, "line", 5, 7)
    idx = F._unit_index(b["line_start"], None)
    key = 7 * F.FIB14[(idx + 5) % 14] % 29
    assert (F.decrypt_batch(c, key[None, :], "sub", False)[0] == p).all()

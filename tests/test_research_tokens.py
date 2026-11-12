import csv

import numpy as np

from lpswarm import research_tokens as T


def test_token_value_range():
    assert T.token_value("00") == 0 and T.token_value("4F") == 263 and T.token_value("1a") == 62 + 36


def test_committed_table_is_well_formed():
    toks = T.load()
    assert len(toks) == 256
    assert all(t[0] in "01234" and t[1] in T.A62 for t in toks)
    assert max(T.token_value(t) for t in toks) <= 263
    rows = list(csv.DictReader(open("data/lp_derived/tokens_66_68.csv", encoding="utf-8")))
    assert {r["page"] for r in rows} == {"66", "67", "68"} and len(rows) == 256


def test_analyse_on_uniform_tokens_is_unflagged():
    rng = np.random.default_rng(3)
    toks = []
    while len(toks) < 256:
        v = int(rng.integers(0, 264))
        toks.append(f"{v // 62}{T.A62[v % 62]}")
    r = T.analyse(toks, table="missing.csv", sims=100)
    assert r["equal_pairs_max_lag1_128"]["p"] > 0.01 and abs(r["distinct"] - r["distinct_expected"]) < 25

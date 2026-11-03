import numpy as np
import pytest

from lpswarm.executor import (EnumeratedKeys, Executor, ExplicitKeys, Target, TextKeys,
                              WordlistKeys)
from lpswarm.ledger import Ledger
from lpswarm.textgen.synth import heldout_cases


def _target(latin, case):
    return Target(latin, case.ciphertext, f"test:{case.case_id}", is_synthetic=True)


def test_provenance_required():
    led = Ledger()
    with pytest.raises(ValueError):
        led.add_hypothesis("caesar", "x", "", "baseline")


def test_executor_finds_caesar_and_dedupes(tmp_path, latin, oracle):
    led = Ledger(tmp_path / "l.sqlite")
    case = heldout_cases(["caesar"], [60], 1, seed=1)[0]
    hyp = led.add_hypothesis("caesar", "shift", "baseline", "baseline")
    ex = Executor(led, oracle, stop_file=None)
    s = ex.run(_target(latin, case), hyp, "caesar", EnumeratedKeys())
    assert s.new_attempts == 26 and s.passes >= 1
    assert np.array_equal(s.hits[0].plaintext_arr, case.plaintext)
    before = led.counts()
    s2 = ex.run(_target(latin, case), hyp, "caesar", EnumeratedKeys())
    assert s2.new_attempts == 0 and s2.skipped == 26
    assert led.counts() == before
    status = led.conn.execute("SELECT status FROM hypothesis WHERE id=?", (hyp,)).fetchone()[0]
    assert status == "lead"
    counts = [r[0] for r in led.conn.execute(
        "SELECT attempt_count_at_scoring FROM result ORDER BY attempt_id")]
    assert counts == list(range(1, 27))
    led.close()
    # Reopen from disk: still no duplicates on a third run.
    led2 = Ledger(tmp_path / "l.sqlite")
    s3 = Executor(led2, oracle, stop_file=None).run(_target(latin, case), hyp, "caesar",
                                                     EnumeratedKeys())
    assert s3.new_attempts == 0 and led2.counts() == before


def test_ruled_out_and_leads(latin, oracle):
    led = Ledger()
    case = heldout_cases(["vigenere"], [80], 1, seed=2)[0]
    tgt = _target(latin, case)
    ex = Executor(led, oracle, stop_file=None)
    h_bad = led.add_hypothesis("caesar", "maybe a shift", "human", "human")
    ex.run(tgt, h_bad, "caesar", EnumeratedKeys())
    h_good = led.add_hypothesis("vigenere", "word keys", "baseline", "baseline")
    s = ex.run(tgt, h_good, "vigenere", ExplicitKeys([case.key, (1, 2, 3)]),
               {"variants": (case.params["variant"],)})
    assert s.passes == 1
    ro = led.ruled_out()
    assert [r["cipher_family"] for r in ro] == ["caesar"] and ro[0]["attempts"] == 26
    leads = led.leads()
    assert len(leads) == 1 and leads[0]["cipher_family"] == "vigenere"


def test_budget_and_kill_switch(tmp_path, latin, oracle):
    led = Ledger()
    case = heldout_cases(["columnar"], [40], 1, seed=3)[0]
    hyp = led.add_hypothesis("columnar", "small widths", "baseline", "baseline")
    s = Executor(led, oracle, stop_file=None, max_attempts=50).run(
        _target(latin, case), hyp, "columnar", EnumeratedKeys(max_width=6))
    assert s.new_attempts == 50 and s.stopped == "max_attempts"
    stop = tmp_path / "STOP"
    stop.write_text("", encoding="utf-8")
    s2 = Executor(led, oracle, stop_file=stop).run(_target(latin, case), hyp, "columnar",
                                                   EnumeratedKeys(max_width=6))
    assert s2.new_attempts == 0 and s2.stopped == "stop_file"
    status = led.conn.execute("SELECT status FROM hypothesis WHERE id=?", (hyp,)).fetchone()[0]
    assert status == "open"


def test_wordlist_and_running_key_sources(latin, oracle):
    led = Ledger()
    case = heldout_cases(["running_key"], [60], 1, seed=4)[0]
    off = case.params["offset"]
    hyp = led.add_hypothesis("running_key", "text", "baseline", "baseline")
    s = Executor(led, oracle, stop_file=None).run(
        _target(latin, case), hyp, "running_key", TextKeys([("t", case.key)]),
        {"offset_lo": max(0, off - 20), "offset_hi": off + 20})
    assert s.passes >= 1 and s.hits[0].params["offset"] == off
    wl = WordlistKeys(["key", "KEY", "secret", "a"], latin, min_len=2)
    from lpswarm.ciphers import get_family
    ks = list(wl.candidates(get_family("vigenere"), 26, 50))
    assert [k.label for k in ks] == ["key", "secret"]
    assert list(wl.candidates(get_family("caesar"), 26, 50)) == []

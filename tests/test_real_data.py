"""Known-answer checks on the imported Liber Primus sections (skipped if the data is absent).

These only use sections whose plaintext is public and that the Phase 1 families
cover. They check the alphabet mapping and the oracle on real ciphertext, not
any claim about unsolved pages.
"""
import json
from pathlib import Path

import pytest

from lpswarm.alphabet import Alphabet
from lpswarm.ciphers import get_family
from lpswarm.oracle import FullOracle, OracleConfig

ROOT = Path(__file__).resolve().parent.parent
ALPHA = ROOT / "data" / "alphabet" / "gematria_primus.json"
MANIFEST = ROOT / "data" / "lp" / "manifest.json"

pytestmark = pytest.mark.skipif(not (ALPHA.exists() and MANIFEST.exists()),
                                reason="Liber Primus data not imported")


@pytest.fixture(scope="module")
def lp():
    a = Alphabet.from_json(ALPHA)
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    secs = {s["label"]: s for s in man["sections"]}

    def ct(label):
        raw = (MANIFEST.parent / secs[label]["file"]).read_text(encoding="utf-8")
        return a.encode(raw, glyphs_only=True)
    return a, ct, FullOracle(a, OracleConfig(null_samples=300))


def test_alphabet_matches_table(lp):
    a, _, _ = lp
    assert a.size == 29
    assert a.tokens[:4] == ("F", "U", "TH", "O") and a.tokens[-1] == "EA"
    d = json.loads(ALPHA.read_text(encoding="utf-8"))
    assert d["values"][:5] == [2, 3, 5, 7, 11] and d["values"][-1] == 109


def test_cleartext_section_reads_as_english(lp):
    a, ct, oracle = lp
    text = a.decode(ct("05.jpg"))
    assert text.startswith("SOMEWISDOMTHEPRIMESARESACRED")
    assert oracle.score(ct("05.jpg"), attempt_count=50_000).passed


def test_reversed_gematria_section(lp):
    a, ct, oracle = lp
    pt = get_family("vigenere").decrypt(ct("Runes - 01.jpg"), (28,), a.size, variant="beaufort")
    assert a.decode(pt).startswith("AWARNNGBELIEUENOTHNG")
    assert oracle.score(pt, attempt_count=50_000).passed


def test_unsolved_sections_do_not_pass_unshifted(lp):
    a, ct, oracle = lp
    for label in ("17.jpg, 18.jpg, 19.jpg - 0.jpg-2.jpg", "57.jpg-66.jpg/1"):
        assert not oracle.score(ct(label), attempt_count=1).passed

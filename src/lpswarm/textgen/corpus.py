"""Bundled text fixtures and word lists.

Split policy (fixed so nothing leaks into held-out validation):
  - training texts: used to train n-gram models, build the word list, build
    null distributions, and generate the *train* synthetic split;
  - held-out text: used only by the validation harness (see textgen.synth).

Users can add more corpora for a language under data/corpora/<language>/*.txt.
"""
from __future__ import annotations

import re
from collections import Counter
from functools import lru_cache
from importlib import resources
from pathlib import Path

FIXTURES = "lpswarm.fixtures"

# language -> (training files, held-out files)
LANGUAGES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "english": (
        ("english_austen_pride.txt", "english_melville_moby.txt", "english_doyle_adventures.txt"),
        ("english_shelley_frankenstein.txt",),
    ),
}

FALLBACK_TEXT = (
    "We the People of the United States, in Order to form a more perfect Union, establish "
    "Justice, insure domestic Tranquility, provide for the common defence, promote the general "
    "Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and "
    "establish this Constitution for the United States of America. "
    "Four score and seven years ago our fathers brought forth on this continent, a new nation, "
    "conceived in Liberty, and dedicated to the proposition that all men are created equal. "
)

_USER_DATA = Path("data") / "corpora"


def _read_fixture(name: str) -> str | None:
    try:
        return resources.files(FIXTURES).joinpath(name).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None


def _user_texts(language: str) -> list[str]:
    d = _USER_DATA / language
    if not d.is_dir():
        return []
    return [p.read_text(encoding="utf-8", errors="replace") for p in sorted(d.glob("*.txt"))]


@lru_cache(maxsize=None)
def training_text(language: str = "english") -> str:
    files = LANGUAGES.get(language, ((), ()))[0]
    parts = [t for t in (_read_fixture(f) for f in files) if t]
    parts += _user_texts(language)
    if not parts:
        if language != "english":
            raise ValueError(f"no training corpus for language {language!r}")
        return FALLBACK_TEXT * 20
    return "\n\n".join(parts)


@lru_cache(maxsize=None)
def _heldout_text(language: str = "english") -> str:
    """Held-out text. Only lpswarm.validation and textgen.synth may call this."""
    files = LANGUAGES.get(language, ((), ()))[1]
    parts = [t for t in (_read_fixture(f) for f in files) if t]
    if not parts:
        raise RuntimeError(f"no held-out corpus for language {language!r}")
    return "\n\n".join(parts)


_WORD_RE = re.compile(r"[A-Za-z]+")


@lru_cache(maxsize=None)
def word_frequencies(language: str = "english") -> tuple[tuple[str, int], ...]:
    c = Counter(w.upper() for w in _WORD_RE.findall(training_text(language)))
    return tuple(c.most_common())


def wordlist(language: str = "english", min_len: int = 1, min_count: int = 2,
             limit: int | None = None) -> list[str]:
    """Words from the training corpus, most frequent first."""
    words = [w for w, c in word_frequencies(language) if c >= min_count and len(w) >= min_len]
    return words[:limit] if limit else words


def load_wordlist_file(path: str | Path) -> list[str]:
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        w = line.strip()
        if w and not w.startswith("#"):
            out.append(w.upper())
    return out

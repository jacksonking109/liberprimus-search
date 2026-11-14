"""Bundled text fixtures and word lists.

Split policy (fixed so nothing leaks into held-out validation):
  - training texts: used to train n-gram models, build the word list, build
    null distributions, and generate the *train* synthetic split;
  - held-out text: used only by the validation harness (see textgen.synth).

Users can add more corpora for a language under <data dir>/corpora/<language>/*.txt,
where <data dir> is $LPSWARM_DATA if set, else ./data relative to the working
directory. Files that overlap the held-out text are refused, so validation
stays honest.
"""
from __future__ import annotations

import os
import re
import warnings
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

def data_dir() -> Path:
    return Path(os.environ.get("LPSWARM_DATA") or "data")


def _read_fixture(name: str) -> str | None:
    try:
        return resources.files(FIXTURES).joinpath(name).read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None


def _user_files(language: str) -> list[Path]:
    d = data_dir() / "corpora" / language
    return sorted(d.glob("*.txt")) if d.is_dir() else []


def _overlaps_heldout(text: str, language: str, probe: int = 200) -> bool:
    try:
        held = _heldout_text(language)
    except RuntimeError:
        return False
    norm = lambda t: re.sub(r"[^A-Z]", "", t.upper())  # noqa: E731
    h = norm(held)
    u = norm(text)
    if len(u) < probe:
        return False
    # Probe a few slices of the user text; any verbatim hit means overlap.
    step = max(1, (len(u) - probe) // 8)
    return any(u[i:i + probe] in h for i in range(0, len(u) - probe + 1, step))


@lru_cache(maxsize=None)
def _user_texts_cached(language: str, key: tuple) -> tuple[tuple[str, str], ...]:
    from lpswarm.textio import read_text
    out = []
    for f in _user_files(language):
        text = read_text(f, errors="replace")
        if _overlaps_heldout(text, language):
            warnings.warn(f"{f}: overlaps the held-out validation text; not used for training")
            continue
        out.append((str(f), text))
    return tuple(out)


def _user_texts(language: str) -> tuple[tuple[str, str], ...]:
    files = _user_files(language)
    key = tuple((str(f), f.stat().st_mtime_ns, f.stat().st_size) for f in files)
    return _user_texts_cached(language, key)


def training_sources(language: str = "english") -> list[str]:
    """Names of everything that went into training_text(language)."""
    files = [f for f in LANGUAGES.get(language, ((), ()))[0] if _read_fixture(f)]
    return [f"fixture:{f}" for f in files] + [name for name, _ in _user_texts(language)]


def training_text(language: str = "english") -> str:
    return _training_text(language, tuple(n for n, _ in _user_texts(language)))


@lru_cache(maxsize=None)
def _training_text(language: str, _user_key: tuple) -> str:
    files = LANGUAGES.get(language, ((), ()))[0]
    parts = [t for t in (_read_fixture(f) for f in files) if t]
    parts += [t for _, t in _user_texts(language)]
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


@lru_cache(maxsize=8)
def _frequencies(text: str) -> tuple[tuple[str, int], ...]:
    c = Counter(w.upper() for w in _WORD_RE.findall(text))
    return tuple(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def word_frequencies(language: str = "english") -> tuple[tuple[str, int], ...]:
    return _frequencies(training_text(language))


def wordlist_from_text(text: str, min_len: int = 1, min_count: int = 2,
                       limit: int | None = None) -> list[str]:
    """Words of `text`, most frequent first (ties alphabetical, so it is deterministic)."""
    words = [w for w, c in _frequencies(text) if c >= min_count and len(w) >= min_len]
    return words[:limit] if limit else words


def wordlist(language: str = "english", min_len: int = 1, min_count: int = 2,
             limit: int | None = None) -> list[str]:
    """Words from the training corpus, most frequent first."""
    return wordlist_from_text(training_text(language), min_len, min_count, limit)


def load_wordlist_file(path: str | Path) -> list[str]:
    from lpswarm.textio import read_text
    out = []
    for line in read_text(path).splitlines():
        w = line.strip()
        if w and not w.startswith("#"):
            out.append(w.upper())
    return out

"""Key-candidate sources. A source turns 'where keys come from' into concrete
keys for a given cipher family."""
from __future__ import annotations

import itertools

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Iterator, Sequence

import numpy as np

from lpswarm.alphabet import Alphabet
from lpswarm.ciphers.base import CipherFamily


@dataclass
class KeyCandidate:
    key: Any
    derivation: str
    label: str = ""                  # human-readable origin, e.g. the source word
    corpus_item_id: int | None = None
    edition_id: str | None = None


class KeySource(ABC):
    name: str = "keysource"

    @abstractmethod
    def candidates(self, family: CipherFamily, n: int, length: int) -> Iterator[KeyCandidate]: ...


class EnumeratedKeys(KeySource):
    """Walk a family's own key space (Caesar shifts, short Vigenere keys, small columnar widths)."""
    name = "enumerate"

    def __init__(self, **limits: Any):
        self.limits = limits

    def candidates(self, family, n, length):
        if not family.enumerable:
            return iter(())
        return (KeyCandidate(k, "enumerate") for k in family.enumerate_keys(n, length, **self.limits))


class WordlistKeys(KeySource):
    """Turn each word into a key via the family's `key_from_word`."""

    def __init__(self, words: Iterable[str], alphabet: Alphabet, name: str = "wordlist",
                 min_len: int = 1, max_len: int | None = None):
        self.name = f"wordlist:{name}"
        self.alphabet = alphabet
        self.words = []
        seen = set()
        for w in words:
            a = alphabet.encode(w)
            if len(a) < min_len or (max_len and len(a) > max_len):
                continue
            ks = alphabet.keystr(a)
            if ks in seen:
                continue
            seen.add(ks)
            self.words.append((w, a))

    def candidates(self, family, n, length):
        if not family.word_keys:
            return
        for w, a in self.words:
            k = family.key_from_word(a, n)
            if k is None:
                continue
            if family.name == "columnar" and len(k) > length:
                continue
            yield KeyCandidate(k, self.name, label=w)


class ExplicitKeys(KeySource):
    """A fixed list of keys (e.g. a synthetic case's true key mixed with decoys)."""

    def __init__(self, keys: Sequence[Any], derivation: str = "explicit",
                 labels: Sequence[str] | None = None, families: Sequence[str] | None = None):
        # Lists stay lists; any other iterable (e.g. a lazy expansion of 700k keys) is
        # kept lazy and can be walked once.
        self.keys = keys if not isinstance(keys, (list, tuple)) else list(keys)
        self.name = derivation
        self.labels = list(labels) if labels else None
        self.families = set(families) if families else None

    def candidates(self, family, n, length):
        if self.families is not None and family.name not in self.families:
            return
        labels = self.labels if self.labels is not None else itertools.repeat("")
        for k, lab in zip(self.keys, labels):
            yield KeyCandidate(k, self.name, label=lab)


class TextKeys(KeySource):
    """Running-key texts. Each text is one key; offsets are enumerated as params."""

    def __init__(self, texts: Sequence[tuple[str, np.ndarray]], name: str = "texts",
                 corpus_item_ids: Sequence[int | None] | None = None):
        self.texts = list(texts)
        self.name = f"text:{name}"
        self.ids = list(corpus_item_ids) if corpus_item_ids else [None] * len(self.texts)

    def candidates(self, family, n, length):
        if family.name != "running_key":
            return
        for (label, arr), cid in zip(self.texts, self.ids):
            if len(arr) >= length:
                yield KeyCandidate(np.asarray(arr, dtype=np.int16), self.name, label=label,
                                   corpus_item_id=cid)


class ChainKeys(KeySource):
    def __init__(self, *sources: KeySource):
        self.sources = sources
        self.name = "+".join(s.name for s in sources)

    def candidates(self, family, n, length):
        for s in self.sources:
            yield from s.candidates(family, n, length)

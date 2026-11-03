"""Alphabet handling. Everything downstream works on integer arrays mod N.

An alphabet is an ordered list of N symbols. Each symbol has:
  - a *token*: its plaintext spelling (one or more letters, e.g. "A" or "TH"),
    used to transliterate ordinary text corpora into the alphabet;
  - a *glyph*: how it is written in ciphertext (defaults to the token).

Encoding does a greedy longest match over tokens, glyphs and aliases
(case-insensitive for tokens), dropping anything that matches nothing.

No real Liber Primus / Gematria Primus table is bundled. Users supply their
own alphabet as JSON (see `Alphabet.from_json`). The `rune_like` factory is a
synthetic stand-in whose extra symbols are chosen from corpus bigram
frequencies, not from any claim about the real puzzle.
"""
from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

LATIN = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
# Unicode runic block, used only as placeholder display glyphs.
_RUNIC_BLOCK = [chr(c) for c in range(0x16A0, 0x16F1)]

DTYPE = np.int16
MAX_SYMBOLS = 30000  # int16 headroom for modular arithmetic done in int32


def _fold(text: str) -> str:
    """Per-character, length-preserving upper case."""
    out = []
    for ch in text:
        u = ch.upper()
        out.append(u if len(u) == 1 else ch)
    return "".join(out)


@dataclass(frozen=True)
class Alphabet:
    name: str
    tokens: tuple[str, ...]
    glyphs: tuple[str, ...] = ()
    aliases: tuple[tuple[str, str], ...] = ()  # (input string, token)
    # exact: glyphs as written (case-sensitive). folded: upper-cased tokens and aliases.
    _exact: dict = field(default=None, compare=False, repr=False, hash=False)  # type: ignore[assignment]
    _folded: dict = field(default=None, compare=False, repr=False, hash=False)  # type: ignore[assignment]
    _maxlen: int = field(default=0, compare=False, repr=False, hash=False)

    def __post_init__(self) -> None:
        if not self.tokens:
            raise ValueError("alphabet must be non-empty")
        if any(not isinstance(t, str) or not t for t in self.tokens):
            raise ValueError(f"alphabet {self.name}: tokens must be non-empty strings")
        tokens = tuple(_fold(t) for t in self.tokens)
        dup = sorted({t for t in tokens if tokens.count(t) > 1})
        if dup:
            raise ValueError(f"alphabet {self.name}: duplicate tokens {dup}")
        object.__setattr__(self, "tokens", tokens)
        glyphs = tuple(self.glyphs) if self.glyphs else tokens
        if len(tokens) > MAX_SYMBOLS:
            raise ValueError(f"alphabet {self.name}: more than {MAX_SYMBOLS} symbols")
        if len(glyphs) != len(tokens):
            raise ValueError(f"alphabet {self.name}: {len(glyphs)} glyphs for {len(tokens)} tokens")
        if any(not isinstance(g, str) or not g for g in glyphs):
            raise ValueError(f"alphabet {self.name}: glyphs must be non-empty strings")
        dupg = sorted({g for g in glyphs if glyphs.count(g) > 1})
        if dupg:
            raise ValueError(f"alphabet {self.name}: duplicate glyphs {dupg}")
        object.__setattr__(self, "glyphs", glyphs)

        def put(d: dict[str, int], key: str, i: int, what: str) -> None:
            if d.get(key, i) != i:
                raise ValueError(f"alphabet {self.name}: {what} {key!r} maps to both symbol "
                                 f"{d[key]} ({self.tokens[d[key]]}) and {i} ({self.tokens[i]})")
            d[key] = i

        exact: dict[str, int] = {}
        for i, g in enumerate(glyphs):
            put(exact, g, i, "glyph")
        folded: dict[str, int] = {}
        for i, t in enumerate(tokens):
            put(folded, t, i, "token")
        idx = {t: i for i, t in enumerate(tokens)}
        for src, tok in self.aliases:
            if not src:
                raise ValueError(f"alphabet {self.name}: empty alias")
            if _fold(tok) not in idx:
                raise ValueError(f"alphabet {self.name}: alias target {tok!r} is not a token")
            put(folded, _fold(src), idx[_fold(tok)], "alias")
        for key, i in exact.items():
            j = folded.get(key)
            if j is not None and j != i:
                raise ValueError(f"alphabet {self.name}: glyph {key!r} of symbol {i} is also the "
                                 f"token/alias of symbol {j}")
        object.__setattr__(self, "_exact", exact)
        object.__setattr__(self, "_folded", folded)
        object.__setattr__(self, "_maxlen", max(len(k) for k in (*exact, *folded)))

    # ------------------------------------------------------------------ basics
    @property
    def size(self) -> int:
        return len(self.tokens)

    def __len__(self) -> int:
        return self.size

    def encode(self, text: str, skipped: list[str] | None = None,
               glyphs_only: bool = False) -> np.ndarray:
        """Greedy longest-match transliteration; unknown characters are dropped.

        With glyphs_only=True only exact glyphs match: use it for ciphertext, so
        Latin notes or hex inside a transcription are not read as symbols.

        At each position the longest match wins; at equal length an exact glyph
        match beats a case-folded token/alias match. Folding is per character and
        length-preserving (characters like 'ß' whose upper case is longer are left
        as they are), so positions never drift.
        """
        up = _fold(text)
        exact = self._exact
        folded = {} if glyphs_only else self._folded
        maxlen = self._maxlen
        out: list[int] = []
        i, n = 0, len(text)
        while i < n:
            for L in range(min(maxlen, n - i), 0, -1):
                v = exact.get(text[i:i + L])
                if v is None:
                    v = folded.get(up[i:i + L])
                if v is not None:
                    out.append(v)
                    i += L
                    break
            else:
                if skipped is not None:
                    skipped.append(text[i])
                i += 1
        return np.asarray(out, dtype=DTYPE)

    def encode_words(self, text: str) -> list[np.ndarray]:
        """Encode each whitespace-separated word separately (empty words dropped)."""
        res = []
        for w in text.split():
            a = self.encode(w)
            if a.size:
                res.append(a)
        return res

    def decode(self, arr: Iterable[int], glyphs: bool = False) -> str:
        table = self.glyphs if glyphs else self.tokens
        return "".join(table[int(x)] for x in arr)

    def keystr(self, arr: Iterable[int]) -> str:
        """Compact one-char-per-symbol string, for hashing and set lookups."""
        return "".join(chr(0x100 + int(x)) for x in arr)

    def to_json(self) -> dict:
        return {"name": self.name, "tokens": list(self.tokens), "glyphs": list(self.glyphs),
                "aliases": {a: t for a, t in self.aliases}}

    # ------------------------------------------------------------- factories
    @classmethod
    def latin26(cls) -> "Alphabet":
        return cls("latin26", LATIN)

    @classmethod
    def from_tokens(cls, name: str, tokens: Sequence[str], glyphs: Sequence[str] = (),
                    aliases: dict[str, str] | None = None) -> "Alphabet":
        return cls(name, tuple(tokens), tuple(glyphs), tuple((aliases or {}).items()))

    @classmethod
    def from_json(cls, path: str | Path) -> "Alphabet":
        """Load a user-supplied alphabet.

        Format: {"name": str, "tokens": [str], "glyphs": [str] (optional),
                 "aliases": {str: token} (optional)}
        """
        from lpswarm.textio import read_text
        try:
            d = json.loads(read_text(path))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: not valid JSON ({exc})") from None
        if not isinstance(d, dict) or "tokens" not in d:
            raise ValueError(f"{path}: alphabet JSON needs a 'tokens' list")
        aliases = d.get("aliases") or {}
        if not isinstance(aliases, dict):
            raise ValueError(f"{path}: 'aliases' must be an object mapping input -> token")
        return cls.from_tokens(d.get("name", Path(path).stem), d["tokens"], d.get("glyphs") or (),
                               aliases)

    @classmethod
    def rune_like(cls, size: int = 29, corpus: str | None = None,
                  extra_tokens: Sequence[str] | None = None) -> "Alphabet":
        """Synthetic rune-style alphabet of configurable size (>= 26).

        Base 26 latin letters plus (size - 26) digraph tokens. Digraphs are
        `extra_tokens` if given, else the most frequent letter bigrams in
        `corpus`. Display glyphs are arbitrary characters from the Unicode
        runic block. This is a test fixture, not the Gematria Primus.
        """
        if size < 26:
            raise ValueError("rune_like requires size >= 26")
        n_extra = size - 26
        if extra_tokens is None:
            extra_tokens = []
            if n_extra:
                if corpus is None:
                    raise ValueError("rune_like needs a corpus or extra_tokens to choose digraphs")
                letters = "".join(ch for ch in corpus.upper() if "A" <= ch <= "Z" or ch.isspace())
                c = Counter()
                for w in letters.split():
                    c.update(w[i:i + 2] for i in range(len(w) - 1))
                extra_tokens = [bg for bg, _ in c.most_common(n_extra)]
        extra_tokens = list(extra_tokens)[:n_extra]
        if len(extra_tokens) != n_extra:
            raise ValueError("not enough extra tokens for requested size")
        tokens = list(LATIN) + [t.upper() for t in extra_tokens]
        # Placeholder glyphs: runic block first, then Unicode private-use characters.
        glyphs = (_RUNIC_BLOCK + [chr(0xE000 + i) for i in range(size)])[:size]
        return cls(f"rune_like{size}", tuple(tokens), tuple(glyphs))


def get_alphabet(spec: str, corpus: str | None = None) -> Alphabet:
    """Resolve 'latin26', 'rune_likeNN', or a path to an alphabet JSON file."""
    if spec == "latin26":
        return Alphabet.latin26()
    p = Path(spec)
    if p.is_file():
        return Alphabet.from_json(p)
    if spec.startswith("rune_like") and spec[len("rune_like"):].isdigit() or spec == "rune_like":
        size = int(spec[len("rune_like"):] or 29)
        if corpus is None:
            from lpswarm.textgen.corpus import training_text
            corpus = training_text()
        return Alphabet.rune_like(size, corpus=corpus)
    raise ValueError(f"unknown alphabet {spec!r}: use latin26, rune_likeNN, or a path to a JSON file")

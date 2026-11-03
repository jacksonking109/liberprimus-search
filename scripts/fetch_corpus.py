"""Dev-time helper: fetch a few public-domain texts and write trimmed fixtures.

Not part of the package and never run by tests or the harness. The package
itself never touches the network; it only reads the files this script writes
(or the small fallback fixture that ships with the repo).

Usage (from repo root):
    python scripts/fetch_corpus.py

Sources are Project Gutenberg texts mirrored by the GITenberg project on
GitHub. Gutenberg boilerplate headers/footers are stripped.
"""
from __future__ import annotations

import re
import sys
import urllib.request
from pathlib import Path

# (output name, url, Gutenberg id, title)
SOURCES = [
    ("english_austen_pride.txt",
     "https://raw.githubusercontent.com/GITenberg/Pride-and-Prejudice_1342/master/1342.txt",
     1342, "Pride and Prejudice, Jane Austen"),
    ("english_melville_moby.txt",
     "https://raw.githubusercontent.com/GITenberg/Moby-Dick--Or-The-Whale_2701/master/2701.txt",
     2701, "Moby Dick, Herman Melville"),
    ("english_shelley_frankenstein.txt",
     "https://raw.githubusercontent.com/GITenberg/Frankenstein_84/master/84.txt",
     84, "Frankenstein, Mary Shelley"),
    ("english_doyle_adventures.txt",
     "https://raw.githubusercontent.com/GITenberg/The-Adventures-of-Sherlock-Holmes_1661/master/1661.txt",
     1661, "The Adventures of Sherlock Holmes, Arthur Conan Doyle"),
]

MAX_BYTES = 450_000  # per text, keeps the committed fixture small

START_RE = re.compile(r"\*\*\*\s*START OF (THE|THIS) PROJECT GUTENBERG.*?\*\*\*", re.I | re.S)
END_RE = re.compile(r"\*\*\*\s*END OF (THE|THIS) PROJECT GUTENBERG", re.I)


def strip_boilerplate(text: str) -> str:
    m = START_RE.search(text)
    if m:
        text = text[m.end():]
    m = END_RE.search(text)
    if m:
        text = text[: m.start()]
    return text.strip()


def main() -> int:
    out_dir = Path(__file__).resolve().parent.parent / "src" / "lpswarm" / "fixtures"
    out_dir.mkdir(parents=True, exist_ok=True)
    ok = []
    failed = []
    for name, url, gid, title in SOURCES:
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                raw = resp.read()
            text = raw.decode("utf-8", errors="replace")
            text = strip_boilerplate(text)
            # keep only printable ascii-ish prose; trim at a paragraph break
            text = text[:MAX_BYTES]
            cut = text.rfind("\n\n")
            if cut > MAX_BYTES // 2:
                text = text[:cut]
            (out_dir / name).write_text(text, encoding="utf-8", newline="\n")
            ok.append((name, url, gid, title, len(text)))
            print(f"ok   {name}: {len(text)} chars")
        except Exception as exc:  # noqa: BLE001 - dev script, report and continue
            failed.append((name, url, str(exc)))
            print(f"FAIL {name}: {exc}", file=sys.stderr)
    lines = ["# Fixture sources", "",
             "Public-domain texts (Project Gutenberg via GITenberg mirrors), boilerplate stripped,",
             f"truncated to at most {MAX_BYTES} characters each. Written by `scripts/fetch_corpus.py`.", ""]
    for name, url, gid, title, n in ok:
        lines.append(f"- `{name}`: {title} (Gutenberg #{gid}), {n} chars. Source: {url}")
    if failed:
        lines += ["", "Failed downloads:"]
        lines += [f"- `{name}`: {url} ({err})" for name, url, err in failed]
    (out_dir / "SOURCES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

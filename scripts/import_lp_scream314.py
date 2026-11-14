"""Dev-time importer: Liber Primus section transcriptions + Gematria Primus alphabet.

Source: https://github.com/scream314/cicada3301 (clone it first; this script only
reads local files, it never touches the network). The source repository has no
licence file; the rune text is Cicada 3301's published material as transcribed
by that project. Everything written here records where it came from.

Usage (from this repo's root):
    git clone --depth 1 https://github.com/scream314/cicada3301 ../cicada3301
    python scripts/import_lp_scream314.py ../cicada3301

Writes:
    data/alphabet/gematria_primus.json   29-symbol alphabet (order, letters, prime values)
    data/lp/sections/NN_<label>.txt      raw <PRE> text of each section, unmodified
    data/lp/manifest.json                one entry per section, with quality flags
    data/lp/SOURCES.md                   provenance

The alphabet comes from the Gematria Primus table image in the source repo
(assets/2013/gematria-primus.jpg): rune order, letter(s) and value. The image
gives rune *pictures*; each is matched to its Unicode Runic character by the
Unicode name of the Anglo-Saxon futhorc letter. That matching is checked
against the cleartext section "05.jpg" (it must read as English) and against
the set of runes that occur in the transcription.

The "Cipher" column of the source is copied into the manifest as `source_note`:
it is the source's claim about how a section was solved, not something this
harness relies on.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

# Gematria Primus, as printed in the table image (rune order = index 0..28).
# (unicode rune, letters as printed, value as printed)
GEMATRIA = [
    ("ᚠ", "F", 2), ("ᚢ", "U", 3), ("ᚦ", "TH", 5), ("ᚩ", "O", 7),
    ("ᚱ", "R", 11), ("ᚳ", "C/K", 13), ("ᚷ", "G", 17), ("ᚹ", "W", 19),
    ("ᚻ", "H", 23), ("ᚾ", "N", 29), ("ᛁ", "I", 31), ("ᛄ", "J", 37),
    ("ᛇ", "EO", 41), ("ᛈ", "P", 43), ("ᛉ", "X", 47), ("ᛋ", "S/Z", 53),
    ("ᛏ", "T", 59), ("ᛒ", "B", 61), ("ᛖ", "E", 67), ("ᛗ", "M", 71),
    ("ᛚ", "L", 73), ("ᛝ", "NG/ING", 79), ("ᛟ", "OE", 83), ("ᛞ", "D", 89),
    ("ᚪ", "A", 97), ("ᚫ", "AE", 101), ("ᚣ", "Y", 103), ("ᛡ", "IA/IO", 107),
    ("ᛠ", "EA", 109),
]

ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
TD_RE = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
PRE_RE = re.compile(r"<PRE>\n?(.*?)</PRE>", re.S)
HEADING_RE = re.compile(r"^# (LP\d)", re.M)


def build_alphabet() -> dict:
    tokens, glyphs, aliases, values, names = [], [], {}, [], []
    for rune, letters, value in GEMATRIA:
        parts = letters.split("/")
        # Primary token: first printed spelling, except NG/ING and IA/IO where the
        # two-letter form is primary and the other is an alias (both as printed).
        primary = parts[0]
        if letters == "IA/IO":
            primary = "IO"
        tokens.append(primary)
        glyphs.append(rune)
        values.append(value)
        names.append(unicodedata.name(rune))
        for alt in parts:
            if alt != primary:
                aliases[alt] = primary
    return {
        "name": "gematria_primus",
        "tokens": tokens,
        "glyphs": glyphs,
        "aliases": aliases,
        "values": values,
        "unicode_names": names,
        "source": "Gematria Primus table image, scream314/cicada3301 assets/2013/gematria-primus.jpg",
        "notes": [
            "Index order and values are as printed in the table.",
            "Letters missing from the table (Q, V) are not mapped; they are dropped when "
            "transliterating English training text. Map them with aliases if you decide to.",
            "Primary tokens: first printed spelling; for NG/ING and IA/IO the alternative is an alias.",
        ],
    }


def slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s[:60] or "section"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    src = Path(argv[1]).resolve()
    md = src / "pages_and_ciphers.md"
    text = md.read_text(encoding="utf-8")
    try:
        commit = subprocess.run(["git", "-C", str(src), "rev-parse", "HEAD"], capture_output=True,
                                text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        commit = "unknown"

    root = Path(__file__).resolve().parent.parent
    alpha = build_alphabet()
    (root / "data" / "alphabet").mkdir(parents=True, exist_ok=True)
    (root / "data" / "alphabet" / "gematria_primus.json").write_text(
        json.dumps(alpha, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    known = set(alpha["glyphs"])

    out = root / "data" / "lp" / "sections"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.txt"):
        old.unlink()

    # Split by LP1 / LP2 headings so each section knows its part.
    parts = [(m.group(1), m.start()) for m in HEADING_RE.finditer(text)]
    manifest = []
    idx = 0
    for pi, (part, start) in enumerate(parts):
        end = parts[pi + 1][1] if pi + 1 < len(parts) else len(text)
        for row in ROW_RE.findall(text[start:end]):
            tds = TD_RE.findall(row)
            if len(tds) < 3:
                continue
            pre = PRE_RE.search(tds[2])
            raw = pre.group(1) if pre else ""
            label = re.sub(r"\s+", " ", tds[0]).strip()
            note = re.sub(r"<[^>]+>", "", re.sub(r"\s+", " ", tds[1])).strip()
            runes = [c for c in raw if 0x16A0 <= ord(c) <= 0x16FF]
            unknown = sorted({c for c in runes if c not in known})
            fname = f"{idx:02d}_{part}_{slug(label)}.txt"
            (out / fname).write_text(raw, encoding="utf-8", newline="\n")
            manifest.append({
                "index": idx,
                "part": part,
                "label": label,
                "file": f"sections/{fname}",
                "source_note": note,
                "runes": len(runes),
                "runes_in_alphabet": sum(1 for c in runes if c in known),
                "unknown_runes": [f"U+{ord(c):04X} {unicodedata.name(c, '?')}" for c in unknown],
                "replacement_chars": raw.count("�"),
                "non_rune_content": bool(re.search(r"[0-9A-Za-z]", raw)),
                "sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
            })
            idx += 1

    lp = root / "data" / "lp"
    (lp / "manifest.json").write_text(json.dumps({
        "source": "https://github.com/scream314/cicada3301",
        "source_file": "pages_and_ciphers.md",
        "source_commit": commit,
        "unit": "section as listed in the source (may span several pages; no page breaks inside)",
        "sections": manifest,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    flagged = [m for m in manifest if m["unknown_runes"] or m["replacement_chars"]]
    (lp / "SOURCES.md").write_text("\n".join([
        "# Liber Primus transcription: provenance",
        "",
        f"- Source: https://github.com/scream314/cicada3301 at commit `{commit}`,",
        "  file `pages_and_ciphers.md` (one `<PRE>` block per section).",
        "- The source repository has no licence file. The rune text is Cicada 3301's published",
        "  Liber Primus as transcribed there. Kept for personal research; check before redistributing.",
        "- Section files are the `<PRE>` contents unmodified (UTF-8, LF line endings).",
        "- `source_note` in `manifest.json` is the source's own description of the cipher; it is a",
        "  claim, not used by the harness.",
        "- Alphabet: `../alphabet/gematria_primus.json`, from the Gematria Primus table image in the",
        "  same repository (order, letters, values as printed; Unicode runes matched by name).",
        "",
        "## Data-quality flags",
        "",
        *(f"- `{m['file']}` ({m['label']}): " +
          ", ".join(filter(None, [
              f"{m['replacement_chars']} corrupted character(s) (U+FFFD)" if m["replacement_chars"] else "",
              f"runes not in the alphabet: {', '.join(m['unknown_runes'])}" if m["unknown_runes"] else "",
          ])) for m in flagged),
        "",
    ]), encoding="utf-8")
    print(f"wrote {len(manifest)} sections, alphabet with {len(alpha['tokens'])} symbols; "
          f"{len(flagged)} section(s) flagged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

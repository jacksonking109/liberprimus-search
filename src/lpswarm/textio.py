"""Reading user-supplied text files robustly (Windows editors often add a BOM or
save as UTF-16 / cp1252)."""
from __future__ import annotations

from pathlib import Path


def read_text(path: str | Path, errors: str = "strict") -> str:
    """Read UTF-8 (with or without BOM) or BOM-marked UTF-16. Anything else raises a
    clear error unless errors='replace'."""
    p = Path(path)
    try:
        raw = p.read_bytes()
    except FileNotFoundError:
        raise FileNotFoundError(f"file not found: {p}") from None
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16", errors=errors)
    try:
        return raw.decode("utf-8-sig", errors=errors)
    except UnicodeDecodeError as exc:
        raise ValueError(f"{p}: not UTF-8 ({exc.reason} at byte {exc.start}); re-save it as "
                         "UTF-8 (in Notepad: Save As > Encoding > UTF-8)") from None

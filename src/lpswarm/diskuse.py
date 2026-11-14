"""Disk space helpers: free space, size of run folders, and pruning old ledgers.

Ledgers dominate: about 1 KB per stored attempt (lean sweeps store far less). Report files
(.md/.csv) are small and are never touched by pruning."""
from __future__ import annotations

import shutil
from pathlib import Path

GB = 1024 ** 3


def free_gb(path: str | Path = ".") -> float:
    p = Path(path)
    while not p.exists() and p != p.parent:
        p = p.parent
    return shutil.disk_usage(p).free / GB


def dir_size(path: Path) -> int:
    total = 0
    for f in Path(path).rglob("*"):
        try:
            if f.is_file():
                total += f.stat().st_size
        except OSError:
            continue
    return total


def run_sizes(base: str | Path = "reports/overnight") -> list[tuple[str, int, int]]:
    """(run folder, total bytes, ledger bytes), oldest first."""
    out = []
    b = Path(base)
    if not b.is_dir():
        return out
    for d in sorted(p for p in b.iterdir() if p.is_dir()):
        led = sum(f.stat().st_size for f in d.rglob("ledger.sqlite*") if f.is_file())
        out.append((d.name, dir_size(d), led))
    return out


def largest_ledgers(base: str | Path = "reports/overnight", n: int = 8) -> list[tuple[Path, int]]:
    files = [(f, f.stat().st_size) for f in Path(base).rglob("ledger.sqlite*") if f.is_file()] \
        if Path(base).is_dir() else []
    return sorted(files, key=lambda t: -t[1])[:n]


def prune_old_ledgers(base: str | Path = "reports/overnight", keep_runs: int = 3,
                      apply: bool = False) -> tuple[int, list[Path]]:
    """Ledger files of every run except the newest `keep_runs`. Returns (bytes, files);
    deletes them only with apply=True. Never touches reports (.md/.csv) or state.json."""
    b = Path(base)
    runs = sorted(p for p in b.iterdir() if p.is_dir()) if b.is_dir() else []
    victims: list[Path] = []
    for d in runs[:-keep_runs] if keep_runs > 0 else runs:
        victims += [f for f in d.rglob("ledger.sqlite*") if f.is_file()]
    total = sum(f.stat().st_size for f in victims)
    if apply:
        for f in victims:
            try:
                f.unlink()
            except OSError:
                pass
    return total, victims

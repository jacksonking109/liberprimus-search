"""Evidence manifest: what a run was evaluated with, recorded so two runs can be compared
without rescoring or guessing.

Written into each ledger (`run_meta`, one row per swarm/baseline invocation) and, for overnight
runs, once into the run folder (`manifest.json`). It holds versions, the development git SHA, the
ACTUAL oracle configuration (after command-line overrides), alphabet / manifest / section hashes,
resource caps and model NAMES. It never holds credentials, prompts, configuration files (only
hashes of them), transcripts or held-out data. If any item cannot be captured it is recorded as
"unknown" with the reason; nothing is filled in from today's defaults for old data.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA = 1
UNKNOWN = "unknown"


def file_sha(path: str | Path | None) -> str | None:
    if not path:
        return None
    p = Path(path)
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    except OSError:
        return None


def git_sha() -> tuple[str, str | None]:
    """(development SHA, error). Read-only `git rev-parse HEAD` in the source tree."""
    try:
        here = Path(__file__).resolve().parent
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(here), capture_output=True,
                           text=True, timeout=5)
        sha = r.stdout.strip()
        if r.returncode == 0 and len(sha) == 40:
            return sha, None
        return UNKNOWN, (r.stderr.strip() or "git rev-parse failed")[:200]
    except (OSError, subprocess.SubprocessError) as exc:
        return UNKNOWN, str(exc)[:200]


def corpus_identity() -> dict:
    """Hash of the bundled language-model texts the oracle's nulls and scorers are built from."""
    d = Path(__file__).resolve().parent / "fixtures"
    files = sorted(p for p in d.glob("*.txt")) if d.is_dir() else []
    h = hashlib.sha256()
    for p in files:
        h.update(p.name.encode() + b"\0" + (file_sha(p) or "").encode())
    return {"fixture_files": len(files), "sha256": h.hexdigest() if files else UNKNOWN}


def section_hashes(manifest_path: str | Path | None) -> dict[str, str]:
    """Recorded sha256 of each manifest section, keyed like a target label ('LP2:<label>')."""
    if not manifest_path or not Path(manifest_path).is_file():
        return {}
    try:
        man = json.loads(Path(manifest_path).read_text(encoding="utf-8-sig"))
        return {f"{s.get('part', '')}:{s['label']}": s.get("sha256") for s in man.get("sections", [])}
    except (OSError, ValueError, KeyError):
        return {}


def _versions() -> dict:
    import lpswarm
    sha, err = git_sha()
    out = {"lpswarm_version": getattr(lpswarm, "__version__", UNKNOWN),
           "executor_version": getattr(lpswarm, "EXECUTOR_VERSION", UNKNOWN),
           "git_sha": sha, "python": sys.version.split()[0], "platform": platform.platform()}
    if err:
        out["git_sha_error"] = err
    return out


def collect(command: str, oracle_cfg: Any, *, alphabet_path: str | None = None,
            manifest_path: str | None = None, targets: list[tuple[str, int]] | None = None,
            caps: dict | None = None, models: dict | None = None) -> dict:
    """Metadata for one invocation. `targets` is [(label, length)]; `caps` plain numbers;
    `models` names only."""
    cfg = dataclasses.asdict(oracle_cfg) if dataclasses.is_dataclass(oracle_cfg) else UNKNOWN
    sec = section_hashes(manifest_path)
    meta: dict[str, Any] = {
        "schema": SCHEMA, "command": command, **_versions(),
        "oracle_config": json.loads(json.dumps(cfg, default=list, sort_keys=True)),
        "corpus": corpus_identity(),
        "alphabet": {"path": alphabet_path, "sha256": file_sha(alphabet_path) or UNKNOWN},
        "manifest": {"path": manifest_path, "sha256": file_sha(manifest_path) or UNKNOWN},
        "targets": [{"label": lab, "length": n, "section_sha256": sec.get(lab, UNKNOWN)}
                    for lab, n in (targets or [])],
        "caps": {k: v for k, v in (caps or {}).items() if isinstance(v, (int, float, str, bool, type(None)))},
        "models": models or {}}
    return meta


def write_run_manifest(run_dir: Path, cfg: Any, config_path: str | None) -> Path:
    """Run-level manifest for an overnight run: versions plus hashes (never contents) of the
    queue and model config files, and the job ids."""
    meta = {"schema": SCHEMA, "kind": "overnight_run", **_versions(),
            "overnight_toml_sha256": file_sha(config_path) or UNKNOWN,
            "models_toml_sha256": file_sha(getattr(cfg, "models", None)) or UNKNOWN,
            "settings": {k: getattr(cfg, k) for k in ("max_parallel", "capacity", "min_free_gb",
                                                       "tick_minutes", "min_checkin_minutes",
                                                       "max_added_jobs", "results_branch", "publish")
                         if hasattr(cfg, k)},
            "supervisor_model": getattr(cfg, "supervisor", None) or None,
            "jobs": [{"id": j.get("id"), "kind": j.get("kind")} for j in getattr(cfg, "jobs", [])],
            "note": "hashes only; no configuration contents, credentials or prompts are stored"}
    path = Path(run_dir) / "manifest.json"
    path.write_text(json.dumps(meta, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
    return path

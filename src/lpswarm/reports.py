"""Report files for swarm and baseline runs (Markdown + JSON), rewritten after every
target so an interrupted run still leaves its results on disk."""
from __future__ import annotations

import json
import time
from pathlib import Path

from lpswarm.ledger import Ledger


def default_report_dir(command: str) -> Path:
    return Path("reports") / f"{command}-{time.strftime('%Y%m%d-%H%M%S')}"


def target_entry(led: Ledger, target_id: str, label: str, symbols: int, *, stopped: str | None = None,
                 stats: dict | None = None, top: int = 10, elapsed_s: float | None = None) -> dict:
    leads = led.leads(target_id, include_near_miss=True, limit=top)
    finals = [r for r in leads if r.get("passed_final")]
    tried = led.tried(target_id)
    return {
        "label": label, "symbols": symbols, "attempts": led.attempt_count(target_id),
        "hypotheses": len(tried), "final_passes": len(finals), "stopped": stopped,
        "elapsed_s": round(elapsed_s, 1) if elapsed_s is not None else None,
        "generators": stats or {},
        "leads": [{"final": bool(r.get("passed_final")), "verdict": r["verdict"],
                   "family": r["cipher_family"], "key": r["key_preview"], "params": r["params_json"],
                   "margin": round(r["combined"] - r["threshold"], 3), "by": r["proposer_model"],
                   "plaintext": r["plaintext_preview"]} for r in leads],
    }


def write_run_report(out_dir: str | Path, title: str, command: str, entries: list[dict],
                     extra_lines: list[str] | None = None) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    data = {"title": title, "command": command, "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "targets": entries}
    (out / "report.json").write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    total_final = sum(e["final_passes"] for e in entries)
    lines = [f"# {title}", "", f"Updated {data['updated']}. Command: `{command}`", "",
             f"**{len(entries)} target(s), {total_final} final pass(es).** A FINAL lead survived "
             "the end-of-search check (Bonferroni over every attempt on that target); read the "
             "text before trusting it.", ""]
    lines += list(extra_lines or [])
    lines += ["| target | symbols | attempts | hypotheses | final passes | stopped |",
              "| --- | ---: | ---: | ---: | ---: | --- |"]
    for e in entries:
        lines.append(f"| {e['label']} | {e['symbols']} | {e['attempts']} | {e['hypotheses']} | "
                     f"{e['final_passes']} | {e['stopped'] or ''} |")
    for e in entries:
        lines += ["", f"## {e['label']}", ""]
        if e["generators"]:
            lines.append("| generator | proposals | invalid | attempts | passes | near misses | model errors |")
            lines.append("| --- | ---: | ---: | ---: | ---: | ---: | ---: |")
            for name, g in e["generators"].items():
                lines.append(f"| {name} | {g.get('proposals', 0)} | {g.get('invalid', 0)} | "
                             f"{g.get('attempts', 0)} | {g.get('passes', 0)} | "
                             f"{g.get('near_misses', 0)} | {g.get('model_errors', 0)} |")
            lines.append("")
        if not e["leads"]:
            lines.append("No passes or near misses: everything tried is recorded as ruled out.")
            continue
        for ld in e["leads"]:
            tag = "**FINAL**" if ld["final"] else ld["verdict"]
            lines.append(f"- {tag} ({ld['family']}, by {ld['by']}, margin {ld['margin']:+.2f}): "
                         f"`{ld['key']}` {ld['params'] if ld['params'] != '{}' else ''}")
            lines.append(f"  `{ld['plaintext']}`")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out / "report.md"

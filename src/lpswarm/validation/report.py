"""CSV + Markdown reports for the validation harness."""
from __future__ import annotations

import csv
import json
from pathlib import Path


def _write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _fmt(x, nd=3):
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def write_reports(result: dict, out_dir: Path) -> dict[str, Path]:
    out_dir = Path(out_dir)
    paths = {
        "csv": out_dir / "validation.csv",
        "cases_csv": out_dir / "validation_cases.csv",
        "null_csv": out_dir / "null_fpr.csv",
        "md": out_dir / "validation.md",
        "json": out_dir / "validation.json",
    }
    _write_csv(paths["csv"], result["table"])
    _write_csv(paths["cases_csv"], result["cases"])
    _write_csv(paths["null_csv"], result["null_check"]["rows"])
    paths["json"].write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")

    vc, oc = result["validation_config"], result["oracle_config"]
    lines = [
        "# Validation report (Phase 1 baseline)",
        "",
        f"Alphabet `{result['alphabet']}` (size {result['alphabet_size']}), language "
        f"`{vc['language']}`, held-out synthetic cases, difficulty `{vc['difficulty']}`, "
        f"seed {vc['seed']}. Word breaks given to the oracle: "
        f"{'yes' if vc.get('word_breaks') else 'no'}. Runtime {result['elapsed_s']:.1f}s.",
        "",
        f"Oracle: alpha={oc['alpha']} per attempt, multiple-comparison adjustment "
        f"`{oc['multiple_comparisons']}` (alpha_eff = alpha / attempts so far on the target), "
        f"n-gram order {oc['order']}, dict weight {oc['dict_weight']}, "
        f"{oc['null_samples']} null samples per type per length, screen alpha {oc['screen_alpha']}.",
        "",
        "Search space per case: true key hidden among decoys "
        f"({vc['decoys']} word-derived decoys; full enumeration for caesar; columnar widths "
        f"2..{vc['columnar_max_width']}; {vc['running_key_offsets']} running-key offsets).",
        "",
        "## Recall and false-positive rate by family and length",
        "",
        "Decisions use the **final check**: after the search, every in-run pass is re-scored at "
        "alpha / N_total (N_total = all attempts on that target), which is independent of search "
        "order. Recall = case recovered (a final pass with >= 90% similarity to the true "
        "plaintext). In-run recall uses the running alpha / i triage verdict instead. "
        "FPR = final passes with < 50% similarity / all wrong attempts. "
        "Partial = final passes at 50-90% similarity (near-solutions; not counted as FP).",
        "",
        "| family | length | cases | recall | recall 95% CI | in-run recall | attempts | false passes | FPR | partial |",
        "| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in result["table"]:
        lines.append(
            f"| {r['family']} | {r['length']} | {r['cases']} | {r['recall']:.2f} | "
            f"[{r['recall_ci_lo']:.2f}, {r['recall_ci_hi']:.2f}] | {r['recall_in_run']:.2f} | "
            f"{r['attempts']} | "
            f"{r['false_passes']} | {r['fpr']:.2e} | {r['partial_passes']} |")
    ns = result["null_check"]
    lines += [
        "",
        "## Oracle null calibration check",
        "",
        "Fresh null samples (different seed from calibration), scored at the unadjusted alpha "
        "(attempt_count = 1). Threshold is the max over null types, so the worst type should sit "
        "near alpha and the others at or below it.",
        "",
        "Stated tolerance: 3 binomial standard errors, counting both the test sample and the "
        "calibration sample: tol = 3 * sqrt(alpha(1-alpha)(1/n_test + 1/n_calib)). "
        "Pass = every type's FPR <= alpha + tol and |worst-type FPR - alpha| <= tol.",
        "",
        "| length | alpha | worst-type FPR | tolerance | within tolerance |",
        "| ---: | ---: | ---: | ---: | --- |",
    ]
    for s in ns["summary"]:
        lines.append(f"| {s['length']} | {s['alpha']} | {s['worst_type_fpr']:.4f} | "
                     f"{s['tolerance']:.4f} | {'yes' if s['within_tolerance'] else 'NO'} |")
    lines += ["", "| length | null type | n | false pos | FPR | 95% CI |",
              "| ---: | --- | ---: | ---: | ---: | --- |"]
    for r in ns["rows"]:
        lines.append(f"| {r['length']} | {r['null_type']} | {r['n']} | {r['false_pos']} | "
                     f"{r['fpr']:.4f} | [{r['ci_lo']:.4f}, {r['ci_hi']:.4f}] |")
    all_ok = all(s["within_tolerance"] for s in ns["summary"])
    lines += [
        "",
        f"**Null calibration overall: {'PASS' if all_ok else 'FAIL'}.**",
        "",
        "## Ledger",
        "",
        f"`{result['ledger_path']}`: " + ", ".join(f"{k}={v}" for k, v in
                                                     result["ledger_counts"].items()),
        "",
        "Files: `validation.csv` (table above), `validation_cases.csv` (per case), "
        "`null_fpr.csv`, `validation.json` (everything).",
        "",
    ]
    paths["md"].write_text("\n".join(lines), encoding="utf-8")
    return paths

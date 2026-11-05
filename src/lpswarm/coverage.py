"""`lpswarm coverage`: a read-only inventory of what the job ledgers record.

It reads ledger files (SQLite, opened read-only), aggregates them per target (section), and
writes `coverage.json` (structured evidence) and `coverage.md` (a digest for people and
planners). It never writes to a ledger, starts jobs, calls models, or publishes anything.

What it can and cannot say is fixed by what the ledgers record. See docs/coverage.md for the
definitions; the main limits, all reported as "unknown" in the output rather than guessed:
  - the oracle configuration (alpha, null samples, near-miss rule...) is not recorded; only
    `executor_version` and, per result, the threshold and alpha actually applied;
  - a lean-sweep summary stores a count, a completion flag and the proposal's description, not
    the proposal's spec or the exact subset completed;
  - why an unfinished run stopped is recorded only in the optional report.json next to the ledger;
  - proposals rejected as invalid never reach a ledger (only report.json counts them).
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any

SCHEMA_ID = "lpswarm-coverage/1"
REQUIRED_TABLES = {"target": {"id", "label", "alphabet", "length", "word_breaks"},
                   "hypothesis": {"id", "cipher_family", "description", "proposer_model",
                                  "proposer_role", "status"},
                   "attempt": {"id", "hypothesis_id", "target_id", "cipher_family",
                               "executor_version", "created_at"},
                   "result": {"attempt_id", "stage", "verdict", "attempt_count_at_scoring",
                              "alpha_eff"}}
UNKNOWN = "unknown"
CHECKPOINT_COLUMNS = {"spec_json", "expansion_version", "text_length", "requested", "cursor",
                      "equivalent", "stop_reason"}
MAX_RECONSTRUCT = 2_000_000
# Only these job arguments are ever copied from an overnight state.json.
SAFE_ARGS = ("--sections", "--max-attempts", "--rounds", "--per-round", "--generators",
             "--lean-threshold", "--timeout")

DEFINITIONS = {
    "stored_rows": "attempts stored one row each in the ledger's attempt table",
    "lean_counted": "attempts that failed inside a lean sweep: counted in sweep_summary, not stored "
                    "individually. A lean sweep's near misses and passes are stored rows",
    "logical_attempts": "stored_rows + lean_counted (the same total the executor uses for its "
                        "end-of-search correction). Not a count of distinct ciphers or decryptions",
    "overlap": "there is no cross-job or cross-run deduplication of attempts, so totals summed over "
               "ledgers may include the same work more than once; 'same description' lists "
               "hypotheses whose description text is identical in several ledgers (a text match, "
               "not proof of identical ciphers)",
    "identity": "a target is identified by its recorded target id (sha256 of alphabet, ciphertext "
                "and word breaks); the transcription version is not recorded",
    "evaluator_group": "ledgers are only totalled together when their recorded executor_version set "
                       "matches; the oracle configuration is unknown for all of them, so groups are "
                       "comparable only in that limited sense",
    "completion": "completed = a finished lean sweep, or a hypothesis recorded as 'ruled_out' (its "
                  "key source ran out); incomplete = a lean sweep stopped early, or a hypothesis "
                  "left 'open' with stored attempts (stopped early, reason not in the ledger); "
                  "interrupted = a hypothesis still marked 'running'. Whether a range was fully "
                  "enumerated is only evidenced by these flags, never inferred from counts",
    "recorded_margin": "combined - threshold, both exactly as recorded when the attempt was scored "
                       "(the threshold depends on the attempt count at that moment). It is not a "
                       "probability, and is not re-scored here",
    "null_percentile": "as recorded: the fraction of the calibration null scores at or below this "
                       "score. It is not the probability that the decryption is wrong",
    "final_check": "pass = an in-run pass or near miss; survivor = it also passed the recorded "
                   "end-of-search check (final_check.passed_final = 1). 'not run' when that table "
                   "has no row for the attempt",
}


# ---------------------------------------------------------------- discovery
def discover(ledgers: list[str] | None, runs_dir: str | None, runs: list[str] | None,
             latest: int | None) -> tuple[list[dict], list[str]]:
    """Ledger files to read, as [{path, run, job}], and notes about how they were found.

    Searched, and nothing else: each explicit --ledger FILE; and, for --runs-dir DIR,
    exactly DIR/<run>/<job>/ledger.sqlite (two levels, not recursive beyond that)."""
    found: list[dict] = []
    notes: list[str] = []
    for p in ledgers or []:
        found.append({"path": Path(p), "run": None, "job": None})
    if runs_dir is not None:
        base = Path(runs_dir)
        if not base.is_dir():
            notes.append(f"runs directory not found: {runs_dir}")
        else:
            run_dirs = sorted(d for d in base.iterdir() if d.is_dir())
            if runs:
                want = set(runs)
                run_dirs = [d for d in run_dirs if d.name in want]
                missing = sorted(want - {d.name for d in run_dirs})
                if missing:
                    notes.append(f"requested runs not found under {runs_dir}: {', '.join(missing)}")
            if latest:
                run_dirs = run_dirs[-latest:]
            for rd in run_dirs:
                for jd in sorted(d for d in rd.iterdir() if d.is_dir()):
                    f = jd / "ledger.sqlite"
                    if f.is_file():
                        found.append({"path": f, "run": rd.name, "job": jd.name})
            notes.append(f"searched {runs_dir}/<run>/<job>/ledger.sqlite for "
                         f"{len(run_dirs)} run folder(s); no other location was searched")
    return found, notes


# ------------------------------------------------------------------ reading
def _connect_ro(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
    con.execute("PRAGMA query_only = ON")
    return con


def _columns(con: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in con.execute(f"PRAGMA table_info({table})")}


def _check_schema(con: sqlite3.Connection) -> tuple[dict, str | None]:
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    missing = [t for t in REQUIRED_TABLES if t not in tables]
    if missing:
        return {}, f"unsupported schema: missing table(s) {', '.join(missing)}"
    cols = {t: _columns(con, t) for t in tables if t in REQUIRED_TABLES
            or t in ("sweep_summary", "final_check", "run_meta")}
    for t, need in REQUIRED_TABLES.items():
        gone = sorted(need - cols[t])
        if gone:
            return {}, f"unsupported schema: table {t} lacks column(s) {', '.join(gone)}"
    return {"has_sweep_summary": "sweep_summary" in tables,
            "has_final_check": "final_check" in tables,
            "has_null_variant": "null_variant" in cols["result"],
            "has_output_hash": "output_hash" in cols["attempt"],
            "has_sweep_complete": "complete" in cols.get("sweep_summary", set()),
            "has_sweep_checkpoint": CHECKPOINT_COLUMNS <= cols.get("sweep_summary", set()),
            "has_run_meta": "run_meta" in tables}, None


def _clean_description(text: str) -> str:
    """The deterministic part of a hypothesis description: the model's free-text rationale
    (after ' | why:') is dropped, so one model's prose never enters another planner's input."""
    return " ".join(str(text).split(" | why:", 1)[0].split())[:240]


def read_ledger(path: Path, top_leads: int, max_hypotheses: int, reconstruct: bool = True) -> dict:
    """Aggregates of one ledger, read inside a single read transaction. Raises
    sqlite3.Error for unreadable / locked / corrupt files."""
    con = _connect_ro(path)
    try:
        con.execute("BEGIN")        # one snapshot: every query below sees the same committed state
        schema, err = _check_schema(con)
        if err:
            return {"status": "unsupported_schema", "error": err}
        targets = {r[0]: {"label": r[1], "alphabet": r[2], "length": r[3], "page_range": r[4],
                          "is_synthetic": bool(r[5]), "word_breaks": r[6]}
                   for r in con.execute("SELECT id, label, alphabet, length, page_range,"
                                        " is_synthetic, word_breaks FROM target")}
        # stored rows per (target, stage, verdict); attempts with no result row are counted apart
        rows: dict[str, dict] = defaultdict(lambda: {"by_stage": defaultdict(int),
                                                     "by_verdict": defaultdict(int),
                                                     "stored": 0, "no_result": 0})
        for tid, stage, verdict, n in con.execute(
                "SELECT a.target_id, r.stage, r.verdict, COUNT(*) FROM attempt a"
                " LEFT JOIN result r ON r.attempt_id=a.id GROUP BY a.target_id, r.stage, r.verdict"):
            d = rows[tid]
            d["stored"] += n
            if stage is None:
                d["no_result"] += n
            else:
                d["by_stage"][stage] += n
                d["by_verdict"][verdict] += n
        # stored rows per (target, hypothesis)
        nv = "r.null_variant" if schema["has_null_variant"] else "NULL"
        hyps: dict[str, dict[int, dict]] = defaultdict(dict)
        for (tid, hid, fam, desc, model, role, status, n, first, last, versions, nears, passes,
             variants) in con.execute(
                "SELECT a.target_id, h.id, h.cipher_family, h.description, h.proposer_model,"
                " h.proposer_role, h.status, COUNT(*), MIN(a.created_at), MAX(a.created_at),"
                " GROUP_CONCAT(DISTINCT a.executor_version),"
                " SUM(r.verdict='near_miss'), SUM(r.verdict='pass'),"
                f" GROUP_CONCAT(DISTINCT {nv})"
                " FROM attempt a JOIN hypothesis h ON h.id=a.hypothesis_id"
                " LEFT JOIN result r ON r.attempt_id=a.id GROUP BY a.target_id, h.id"):
            hyps[tid][hid] = {
                "hypothesis_id": hid, "family": fam, "description": _clean_description(desc),
                "proposer": model, "role": role, "recorded_status": status,
                "stored_rows": n, "stored_near_misses": nears or 0, "stored_passes": passes or 0,
                "first_attempt": first, "last_attempt": last,
                "executor_versions": sorted(v for v in (versions or "").split(",") if v),
                "null_variants": sorted(v for v in (variants or "").split(",") if v),
                "lean": None}
        lean_total: dict[str, dict] = defaultdict(lambda: {"complete": 0, "incomplete": 0,
                                                           "sweeps": 0})
        if schema["has_sweep_summary"]:
            cc = "s.complete" if schema["has_sweep_complete"] else "NULL"
            ck = ("s.spec_json, s.expansion_version, s.text_length, s.requested, s.cursor,"
                  " s.equivalent, s.stop_reason" if schema["has_sweep_checkpoint"]
                  else "NULL, NULL, NULL, NULL, NULL, NULL, NULL")
            for (tid, hid, fam, sid, att, scr, best, comp, desc, model, role, status,
                 *ckv) in con.execute(
                        "SELECT s.target_id, s.hypothesis_id, s.family, s.sweep_id, s.attempts,"
                        f" s.screened, s.best_margin, {cc}, h.description, h.proposer_model,"
                        f" h.proposer_role, h.status, {ck} FROM sweep_summary s"
                        " JOIN hypothesis h ON h.id=s.hypothesis_id"):
                entry = hyps[tid].setdefault(hid, {
                    "hypothesis_id": hid, "family": fam, "description": _clean_description(desc),
                    "proposer": model, "role": role, "recorded_status": status, "stored_rows": 0,
                    "stored_near_misses": 0, "stored_passes": 0, "first_attempt": None,
                    "last_attempt": None, "executor_versions": [], "null_variants": [],
                    "lean": None})
                done = None if comp is None else bool(comp)
                entry["lean"] = {"sweep_id": sid, "counted_attempts": att, "screened_out": scr,
                                 "best_recorded_margin_of_counted": best, "complete": done,
                                 **_checkpoint_fields(ckv, done, reconstruct)}
                lt = lean_total[tid]
                lt["sweeps"] += 1
                key = "complete" if done is True else "incomplete" if done is False \
                    else "unknown_completion"
                lt[key] = lt.get(key, 0) + att
        # leads (bounded per target) and final-check status
        leads: dict[str, list] = {}
        finals: dict[str, dict] = {}
        for tid in targets:
            fj = ("LEFT JOIN final_check f ON f.attempt_id=a.id" if schema["has_final_check"] else "")
            fc = ("f.attempt_id, f.passed_final, f.threshold_final, f.attempt_count_final"
                  if schema["has_final_check"] else "NULL, NULL, NULL, NULL")
            vv = "r.null_variant" if schema["has_null_variant"] else "NULL"
            leads[tid] = [{
                "attempt_id": aid, "hypothesis_id": hid, "family": fam, "verdict": verdict,
                "stage": stage, "combined": comb, "threshold_at_scoring": thr,
                "recorded_margin": (comb - thr) if comb is not None and thr is not None else None,
                "null_percentile": nullp, "attempt_count_at_scoring": cnt, "alpha_eff": alpha,
                "null_variant": variant, "unreachable": bool(unr),
                "plaintext_preview": (prev or "")[:80],
                "final_check": ("not run" if fid is None else
                                {"passed": bool(passed_f), "threshold": thr_f,
                                 "attempt_count": cnt_f})}
                for (aid, hid, fam, verdict, stage, comb, thr, nullp, cnt, alpha, variant, unr,
                     prev, fid, passed_f, thr_f, cnt_f) in con.execute(
                    "SELECT a.id, a.hypothesis_id, a.cipher_family, r.verdict, r.stage, r.combined,"
                    f" r.threshold, r.null_percentile, r.attempt_count_at_scoring, r.alpha_eff, {vv},"
                    f" r.unreachable, r.plaintext_preview, {fc} FROM attempt a"
                    f" JOIN result r ON r.attempt_id=a.id {fj}"
                    " WHERE a.target_id=? AND r.verdict IN ('pass','near_miss')"
                    " ORDER BY (r.combined - r.threshold) DESC, a.id LIMIT ?", (tid, top_leads))]
            if schema["has_final_check"]:
                checked, survivors = con.execute(
                    "SELECT COUNT(*), COALESCE(SUM(f.passed_final), 0) FROM final_check f"
                    " JOIN attempt a ON a.id=f.attempt_id WHERE a.target_id=?", (tid,)).fetchone()
                finals[tid] = {"rechecked": checked, "survivors": int(survivors)}
            else:
                finals[tid] = {"rechecked": UNKNOWN, "survivors": UNKNOWN}
        n_unlinked = con.execute(
            "SELECT COUNT(*) FROM hypothesis h WHERE NOT EXISTS"
            " (SELECT 1 FROM attempt a WHERE a.hypothesis_id=h.id)"
            + (" AND NOT EXISTS (SELECT 1 FROM sweep_summary s WHERE s.hypothesis_id=h.id)"
               if schema["has_sweep_summary"] else "")).fetchone()[0]
        out_targets = []
        for tid, t in sorted(targets.items()):
            hl = sorted(hyps.get(tid, {}).values(), key=lambda h: (-(h["stored_rows"] + (
                (h["lean"] or {}).get("counted_attempts") or 0)), h["hypothesis_id"]))
            r = rows.get(tid, {"by_stage": {}, "by_verdict": {}, "stored": 0, "no_result": 0})
            lt = lean_total.get(tid, {"complete": 0, "incomplete": 0, "sweeps": 0})
            lean_all = sum(v for k, v in lt.items() if k != "sweeps")
            all_versions = sorted({v for h in hl for v in h["executor_versions"]})
            out_targets.append({
                "target_id": tid, **t, "stored_rows": r["stored"],
                "stored_by_stage": dict(sorted(r["by_stage"].items())),
                "stored_by_verdict": dict(sorted(r["by_verdict"].items())),
                "attempts_without_result_row": r["no_result"],
                "lean_counted": lean_all, "lean_sweeps": lt["sweeps"],
                "lean_counted_by_completion": {k: v for k, v in sorted(lt.items()) if k != "sweeps"},
                "logical_attempts": r["stored"] + lean_all,
                "executor_versions": all_versions,
                "hypothesis_count": len(hl),
                "hypotheses": hl[:max_hypotheses],
                "hypotheses_truncated": len(hl) > max_hypotheses,
                "leads": leads.get(tid, []), "final_check_summary": finals.get(tid)})
        return {"status": "ok", "schema": schema, "targets": out_targets,
                "hypotheses_without_attempts": n_unlinked, "run_meta": _read_run_meta(con, schema)}
    finally:
        con.close()


# --------------------------------------------------------------- checkpoints
def _checkpoint_fields(ckv: list, done: bool | None, reconstruct: bool) -> dict:
    """Checkpoint facts of a lean sweep, kept apart: requested (an upper bound), counted attempts
    (elsewhere), the cursor (candidates fully processed, in expansion order), equivalents skipped
    and the stop reason. All `unknown` for rows written before checkpoints existed."""
    spec_json, version, length, requested, cursor, equivalent, stop = ckv
    if spec_json is None or cursor is None:
        return {"checkpoint": UNKNOWN, "completed_prefix": {
            "status": UNKNOWN, "reason": "no checkpoint recorded (older ledger or summary)"}}
    ck = {"requested_upper_bound": requested, "cursor_candidates_processed": cursor,
          "equivalent_skipped": equivalent, "stop_reason": stop or UNKNOWN,
          "text_length": length, "expansion_version": version}
    if done is True:
        prefix = {"status": "complete_by_recorded_flag"}
    elif not reconstruct:
        prefix = {"status": "not_reconstructed", "reason": "--no-reconstruct"}
    else:
        prefix = _completed_prefix(spec_json, version, length, cursor, requested)
    return {"checkpoint": ck, "completed_prefix": prefix}


def _completed_prefix(spec_json: str, version: int, length: int, cursor: int, requested) -> dict:
    """The first `cursor` ciphers of the proposal in expansion order (re-expanded read-only)."""
    from lpswarm.programs.spec import EXPANSION_VERSION, describe, expand_iter
    if version != EXPANSION_VERSION:
        return {"status": UNKNOWN, "reason": f"expansion order version {version} differs from this "
                f"tool's {EXPANSION_VERSION}; the completed subset cannot be reconstructed"}
    bound = int(requested or cursor)
    if bound > MAX_RECONSTRUCT:
        return {"status": "not_reconstructed", "completed": cursor, "requested_upper_bound": bound,
                "reason": f"expansion larger than {MAX_RECONSTRUCT}; counts only"}
    try:
        spec = json.loads(spec_json)
        first = last = nxt = None
        total = 0
        for i, s in enumerate(expand_iter(spec, length)):
            total += 1
            if i == 0:
                first = describe(s)
            if i == cursor - 1:
                last = describe(s)
            if i == cursor:
                nxt = describe(s)
        return {"status": "reconstructed", "completed": cursor, "expanded_total": total,
                "remaining": max(total - cursor, 0), "first_completed": first,
                "last_completed": last, "first_remaining": nxt,
                "note": "the first `completed` ciphers in deterministic expansion order; the "
                        "decryptions themselves are not rescored here"}
    except Exception as exc:  # noqa: BLE001
        return {"status": UNKNOWN, "reason": f"could not re-expand the recorded spec: {str(exc)[:120]}"}


def _read_run_meta(con: sqlite3.Connection, schema: dict) -> list[dict]:
    if not schema.get("has_run_meta"):
        return []
    out = []
    for rid, created, chash, mj in con.execute(
            "SELECT id, created_at, config_hash, meta_json FROM run_meta ORDER BY id"):
        try:
            m = json.loads(mj)
        except ValueError:
            m = None
        if not isinstance(m, dict):
            out.append({"id": rid, "created_at": created, "config_hash": chash, "unreadable": True})
            continue
        out.append({"id": rid, "created_at": created, "config_hash": chash,
                    "command": m.get("command"), "git_sha": m.get("git_sha", UNKNOWN),
                    "lpswarm_version": m.get("lpswarm_version", UNKNOWN),
                    "executor_version": m.get("executor_version", UNKNOWN),
                    "oracle_config": m.get("oracle_config", UNKNOWN),
                    "caps": m.get("caps", {}), "models": m.get("models", {}),
                    "corpus_sha256": (m.get("corpus") or {}).get("sha256", UNKNOWN),
                    "alphabet_sha256": (m.get("alphabet") or {}).get("sha256", UNKNOWN),
                    "capture_error": m.get("meta_error") or m.get("git_sha_error")})
    return out


# ----------------------------------------------------------------- sidecars
def _sidecars(path: Path, job: str | None) -> dict:
    """Optional facts from files next to the ledger: report.json (stop reason and proposal counts
    per target) and the run's state.json (job status and a few allow-listed arguments)."""
    out: dict[str, Any] = {"report": None, "job_state": None}
    rep = path.parent / "report.json"
    if rep.is_file():
        try:
            data = json.loads(rep.read_text(encoding="utf-8"))
            out["report"] = {
                t.get("label"): {"stopped": t.get("stopped") or None,
                                 "generators": {g: {k: v.get(k) for k in
                                                    ("proposals", "invalid", "duplicates",
                                                     "attempts", "model_errors")}
                                                for g, v in (t.get("generators") or {}).items()
                                                if isinstance(v, dict)}}
                for t in data.get("targets", []) if isinstance(t, dict)}
        except (OSError, ValueError):
            out["report"] = "unreadable"
    st = path.parent.parent / "state.json"
    if job and st.is_file():
        try:
            state = json.loads(st.read_text(encoding="utf-8"))
            for j in state.get("jobs", []):
                if re.sub(r"[^A-Za-z0-9_.-]+", "_", str(j.get("id", ""))) == job:
                    args = [str(a) for a in j.get("args", [])]
                    out["job_state"] = {
                        "job_id": j.get("id"), "status": j.get("status"),
                        "returncode": j.get("returncode"), "reason": j.get("reason"),
                        "args": {a: args[i + 1] for i, a in enumerate(args[:-1]) if a in SAFE_ARGS}}
        except (OSError, ValueError):
            out["job_state"] = "unreadable"
    return out


# ----------------------------------------------------------- classification
def completion_of(h: dict) -> str:
    lean = h.get("lean")
    if lean is not None:
        if lean["complete"] is True:
            return "completed (finished lean sweep)"
        if lean["complete"] is False:
            ck = lean.get("checkpoint")
            if isinstance(ck, dict):
                return (f"incomplete (lean sweep stopped: {ck['stop_reason']}; "
                        f"{ck['cursor_candidates_processed']} of at most {ck['requested_upper_bound']} "
                        "candidates processed)")
            return "incomplete (lean sweep stopped before finishing; reason not recorded in the ledger)"
        return "unknown (lean summary without a completion flag)"
    st = h["recorded_status"]
    if st == "ruled_out":
        return "completed (key source ran out, per recorded status)"
    if st == "running":
        return "interrupted (still marked running)"
    if st == "open":
        return ("incomplete (stopped early; reason not recorded in the ledger)" if h["stored_rows"]
                else "no attempts recorded")
    if st == "lead":
        return "has a recorded pass; whether the enumeration finished is not recorded"
    return f"recorded status {st}"


# --------------------------------------------------------------- aggregation
def build(ledger_specs: list[dict], notes: list[str], top_leads: int = 10,
          max_hypotheses: int = 500, version: str = UNKNOWN, reconstruct: bool = True) -> dict:
    sources: list[dict] = []
    per_target: dict[str, dict] = {}
    for spec in ledger_specs:
        p: Path = spec["path"]
        # References are relative (run/job/ledger.sqlite) for runs-dir discovery, as given otherwise.
        ref = (f"{spec['run']}/{spec['job']}/ledger.sqlite" if spec["run"] else
               str(p).replace("\\", "/"))
        src = {"path": ref, "run": spec["run"], "job": spec["job"], "status": None, "error": None}
        sources.append(src)
        if not p.exists():
            src.update(status="missing", error="file does not exist (nothing was created)")
            continue
        if not p.is_file():
            src.update(status="unreadable", error="not a file")
            continue
        src["size_bytes"] = p.stat().st_size
        try:
            data = read_ledger(p, top_leads, max_hypotheses, reconstruct)
        except sqlite3.OperationalError as exc:
            msg = str(exc)
            src.update(status="locked" if "locked" in msg or "busy" in msg else "unreadable",
                       error=msg[:200])
            continue
        except sqlite3.DatabaseError as exc:
            src.update(status="corrupt", error=str(exc)[:200])
            continue
        except OSError as exc:
            src.update(status="unreadable", error=str(exc)[:200])
            continue
        if data["status"] != "ok":
            src.update(status=data["status"], error=data["error"])
            continue
        src["run_meta"] = data["run_meta"] if data["schema"].get("has_run_meta") else UNKNOWN
        src.update(status="ok", schema=data["schema"],
                   hypotheses_without_attempts=data["hypotheses_without_attempts"],
                   snapshot="one read transaction per ledger: committed rows at read time; the "
                            "executor commits every 2000 attempts, so a running job's newest "
                            "attempts may be missing")
        side = _sidecars(p, spec["job"])
        src["sidecars"] = {"report_json": "present" if isinstance(side["report"], dict)
                           else side["report"] or "absent",
                           "state_json_job": side["job_state"] or "absent"}
        for t in data["targets"]:
            entry = per_target.setdefault(t["target_id"], {
                "target_id": t["target_id"], "labels": set(), "alphabet": t["alphabet"],
                "length": t["length"], "page_ranges": set(), "is_synthetic": t["is_synthetic"],
                "word_breaks": t["word_breaks"], "ledgers": []})
            entry["labels"].add(t["label"])
            if t["page_range"]:
                entry["page_ranges"].add(t["page_range"])
            rep = side["report"].get(t["label"]) if isinstance(side["report"], dict) else None
            for h in t["hypotheses"]:
                h["completion"] = completion_of(h)
            entry["ledgers"].append({
                "ledger": src["path"], "run": spec["run"], "job": spec["job"],
                "run_meta": data["run_meta"] if data["schema"].get("has_run_meta") else UNKNOWN,
                "stored_rows": t["stored_rows"], "stored_by_stage": t["stored_by_stage"],
                "stored_by_verdict": t["stored_by_verdict"],
                "attempts_without_result_row": t["attempts_without_result_row"],
                "lean_counted": t["lean_counted"], "lean_sweeps": t["lean_sweeps"],
                "lean_counted_by_completion": t["lean_counted_by_completion"],
                "logical_attempts": t["logical_attempts"],
                "executor_versions": t["executor_versions"],
                "stopped_reason_from_report_json": (rep or {}).get("stopped") or UNKNOWN,
                "proposal_counts_from_report_json": (rep or {}).get("generators") or UNKNOWN,
                "job_state": side["job_state"] or UNKNOWN,
                "hypothesis_count": t["hypothesis_count"],
                "hypotheses": t["hypotheses"], "hypotheses_truncated": t["hypotheses_truncated"],
                "leads": t["leads"], "final_check_summary": t["final_check_summary"]})
    sections = [_section(e) for e in sorted(per_target.values(), key=lambda e: (
        sorted(e["labels"])[0], e["target_id"]))]
    ok = [s for s in sources if s["status"] == "ok"]
    bad = [s for s in sources if s["status"] != "ok"]
    status = ("no_readable_inputs" if not ok else "partial" if bad or any(
        "not found" in n for n in notes) else "complete")
    return {"schema": SCHEMA_ID, "tool": {"name": "lpswarm", "version": version},
            "status": status,
            "inputs": {"discovery_notes": notes,
                       "ledgers": sorted(sources, key=lambda s: s["path"]),
                       "counts": {"read": len(ok), "failed": len(bad)}},
            "definitions": DEFINITIONS, "sections": sections,
            "limitations": [
                "The oracle configuration (alpha, null samples, near-miss rule) is recorded only in "
                "ledgers written after the evidence manifest existed (run_meta); for all others it "
                "is unknown.",
                "Lean-sweep summaries written before checkpoints record a count, a completion flag and "
                "the proposal's description, not its spec; their completed subset is unknown.",
                "Why an unfinished job stopped is recorded only in report.json beside the ledger, "
                "when present; invalid proposals never reach a ledger (their counts and grouped reasons are in "
                "report.json as invalid_reasons).",
                "No cross-job or cross-run deduplication exists, so summed totals may overlap.",
                "Transcription version is not recorded; identity is the target id only.",
                "History is not rescored: recorded thresholds and margins are shown as they were."]}


def _config_key(run_meta) -> str:
    """The recorded oracle-config hash of a ledger: 'unknown' if none was recorded (older ledgers),
    'multiple:...' if the ledger was used with different configurations (per-attempt attribution
    is then unknown)."""
    if not isinstance(run_meta, list) or not run_meta:
        return "unknown (not recorded)"
    hashes = sorted({m.get("config_hash") for m in run_meta if not m.get("unreadable")} - {None})
    unknown_cfg = [m for m in run_meta if m.get("oracle_config") in (None, UNKNOWN)]
    if not hashes or (len(hashes) == 1 and unknown_cfg):
        return "unknown (capture failed)"
    return hashes[0] if len(hashes) == 1 else "multiple:" + ",".join(h[:12] for h in hashes)


def _config_of(run_meta, key: str):
    if key.startswith("multiple"):
        return "multiple configurations recorded in one ledger; per-attempt attribution unknown"
    if key.startswith("unknown"):
        return UNKNOWN
    for m in run_meta:
        if m.get("config_hash") == key:
            return m.get("oracle_config", UNKNOWN)
    return UNKNOWN


def _section(e: dict) -> dict:
    wb = e["word_breaks"]
    try:
        wlist = json.loads(wb) if wb else None
    except ValueError:
        wlist = None
    breaks = ({"present": True, "count": len(wlist),
               "sha256": hashlib.sha256(json.dumps(wlist).encode()).hexdigest()[:16]}
              if isinstance(wlist, list) else {"present": False})
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for led in e["ledgers"]:
        groups[(tuple(led["executor_versions"]) or (UNKNOWN,), _config_key(led["run_meta"]))].append(led)
    evaluator_groups = []
    for (versions, cfg_key), leds in sorted(groups.items()):
        evaluator_groups.append({
            "executor_versions": list(versions), "oracle_config": _config_of(leds[0]["run_meta"], cfg_key),
            "oracle_config_hash": cfg_key if not cfg_key.startswith(("unknown", "multiple")) else UNKNOWN,
            "git_shas": sorted({m.get("git_sha", UNKNOWN) for led in leds
                                for m in (led["run_meta"] if isinstance(led["run_meta"], list) else [])}),
            "ledgers": [led["ledger"] for led in leds],
            "stored_rows": sum(led["stored_rows"] for led in leds),
            "lean_counted": sum(led["lean_counted"] for led in leds),
            "logical_attempts_summed_over_ledgers": sum(led["logical_attempts"] for led in leds),
            "note": "summed over ledgers; may include overlapping work"})
    desc_in: dict[str, set] = defaultdict(set)
    for led in e["ledgers"]:
        for h in led["hypotheses"]:
            desc_in[h["description"]].add(led["ledger"])
    same_desc = [{"description": d, "ledgers": sorted(ls)} for d, ls in sorted(desc_in.items())
                 if len(ls) > 1]
    leads = sorted((dict(lead, ledger=led["ledger"]) for led in e["ledgers"] for lead in led["leads"]),
                   key=lambda x: (-(x["recorded_margin"] if x["recorded_margin"] is not None
                                    else -1e9), x["ledger"], x["attempt_id"]))
    return {"target_id": e["target_id"], "labels": sorted(e["labels"]), "alphabet": e["alphabet"],
            "length": e["length"], "page_ranges": sorted(e["page_ranges"]),
            "is_synthetic": e["is_synthetic"], "word_breaks": breaks,
            "transcription_version": UNKNOWN,
            "ledger_count": len(e["ledgers"]), "evaluator_groups": evaluator_groups,
            "same_description_in_several_ledgers": same_desc,
            "leads_best_first": leads[:20],
            "final_check": {
                "rechecked": sum(led["final_check_summary"]["rechecked"] for led in e["ledgers"]
                                 if isinstance(led["final_check_summary"]["rechecked"], int)),
                "survivors": sum(led["final_check_summary"]["survivors"] for led in e["ledgers"]
                                 if isinstance(led["final_check_summary"]["survivors"], int)),
                "ledgers_without_final_check_table": sum(
                    1 for led in e["ledgers"]
                    if not isinstance(led["final_check_summary"]["rechecked"], int))},
            "sources": sorted(e["ledgers"], key=lambda led: led["ledger"])}


# ------------------------------------------------------------------ outputs
def to_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True, default=str) + "\n"


def to_markdown(report: dict, top_hypotheses: int = 25) -> str:
    L = ["# Coverage digest", "",
         f"Status: **{report['status']}**. Ledgers read: {report['inputs']['counts']['read']}, "
         f"failed or skipped: {report['inputs']['counts']['failed']}.", "",
         "This lists what the recorded ledgers show was **tested with the recorded configuration**. "
         "It does not say any family is exhausted, counts may overlap across ledgers, and anything "
         "marked unknown was not recorded. Definitions are in `coverage.json` (`definitions`).", ""]
    for n in report["inputs"]["discovery_notes"]:
        L.append(f"- {n}")
    bad = [s for s in report["inputs"]["ledgers"] if s["status"] != "ok"]
    if bad:
        L += ["", "## Inputs not read", ""]
        L += [f"- `{s['path']}`: **{s['status']}**: {s['error']}" for s in bad]
    for s in report["sections"]:
        L += ["", f"## {', '.join(s['labels'])}", "",
              f"Target `{s['target_id'][:12]}`, {s['length']} symbols, alphabet {s['alphabet']}, "
              f"word breaks {'recorded (' + str(s['word_breaks']['count']) + ')' if s['word_breaks']['present'] else 'not used'}, "
              f"transcription version unknown, {s['ledger_count']} ledger(s). End-of-search check: "
              f"{s['final_check']['rechecked']} candidate(s) rechecked, "
              f"{s['final_check']['survivors']} survived (a candidate with no recheck recorded "
              f"has no final verdict).", ""]
        L += ["| evaluator (executor version; oracle config hash, or unknown if not recorded) | ledgers | stored rows | lean counted | logical (summed, may overlap) |",
              "| --- | ---: | ---: | ---: | ---: |"]
        for g in s["evaluator_groups"]:
            h = g.get("oracle_config_hash", "unknown")
            cfg = h[:10] if h != "unknown" else ("multiple" if "multiple" in str(g["oracle_config"]) else "unknown")
            L.append(f"| {', '.join(g['executor_versions'])}; config {cfg} | {len(g['ledgers'])} | {g['stored_rows']} "
                     f"| {g['lean_counted']} | {g['logical_attempts_summed_over_ledgers']} |")
        hy = []
        for led in s["sources"]:
            for h in led["hypotheses"]:
                n = h["stored_rows"] + ((h.get("lean") or {}).get("counted_attempts") or 0)
                hy.append((n, led, h))
        hy.sort(key=lambda t: (-t[0], t[1]["ledger"], t[2]["hypothesis_id"]))
        if hy:
            L += ["", f"Most-tested hypotheses ({min(top_hypotheses, len(hy))} of {len(hy)}):", "",
                  "| attempts | proposer | description | completion | where |", "| ---: | --- | --- | --- | --- |"]
            for n, led, h in hy[:top_hypotheses]:
                lean = " (lean)" if h.get("lean") else ""
                where = led["job"] or Path(led["ledger"]).name
                L.append(f"| {n}{lean} | {h['proposer']} | {h['description']} | {h['completion']} "
                         f"| {led['run'] or ''}/{where} |")
        stops = sorted({(led["job"] or led["ledger"], led["stopped_reason_from_report_json"])
                        for led in s["sources"] if led["stopped_reason_from_report_json"] != UNKNOWN})
        if stops:
            L += ["", "Recorded stop reasons (from report.json): " + "; ".join(
                f"{j}: {r}" for j, r in stops) + "."]
        if s["same_description_in_several_ledgers"]:
            L += ["", "Same description recorded in several ledgers (a text match, not proof of "
                  "identical ciphers): " + "; ".join(
                      f"`{d['description'][:70]}` x{len(d['ledgers'])}"
                      for d in s["same_description_in_several_ledgers"][:8]) + "."]
        if s["leads_best_first"]:
            L += ["", "Best recorded leads (recorded margin = combined - threshold at scoring time; "
                  "not a probability):", "",
                  "| verdict | recorded margin | final check | description / ledger |", "| --- | ---: | --- | --- |"]
            for lead in s["leads_best_first"][:8]:
                fc = lead["final_check"]
                fcs = fc if isinstance(fc, str) else ("survived" if fc["passed"] else "did not survive")
                m = lead["recorded_margin"]
                ms = f"{m:+.3f}" if m is not None else "unknown"
                L.append(f"| {lead['verdict']} | {ms} | {fcs} | attempt {lead['attempt_id']} in "
                         f"`{lead['ledger']}` |")
        else:
            L += ["", "No pass or near miss recorded."]
    L += ["", "## Limits of this digest", ""] + [f"- {x}" for x in report["limitations"]]
    return "\n".join(L) + "\n"

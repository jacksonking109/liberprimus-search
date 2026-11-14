"""Evidence manifest (run_meta, manifest.json) and lean-sweep checkpoints, and how coverage reads them."""
import json
import sqlite3
from pathlib import Path

import numpy as np
import pytest

from lpswarm import coverage as C
from lpswarm import runmeta
from lpswarm.ledger import Ledger
from lpswarm.oracle import OracleConfig
from lpswarm.programs import describe, expand_iter, expansion_size
from lpswarm.programs.spec import EXPANSION_VERSION, canonical

from test_coverage import CT, ORACLE, SWEEP, SWEEP_N, TARGET, Executor, ExplicitKeys, cover, only_section, ordinary

TRUE_INDEX = 5 * 26 + 11            # position of the true key [5, 11] in the exhaustive length-2 order
SPEC = {"spec_json": canonical(SWEEP), "expansion_version": EXPANSION_VERSION, "text_length": int(len(CT)),
        "requested": expansion_size(SWEEP)}


def sweep(path, max_attempts=None, lean_spec=SPEC):
    from lpswarm.programs import spec_hash
    with Ledger(path) as led:
        h = led.add_hypothesis("program", "all 2-keys", "sonnet", "proposer")
        s = Executor(led, ORACLE, stop_file=None, max_attempts=max_attempts).run(
            TARGET, h, "program", ExplicitKeys(expand_iter(SWEEP)), lean_id=spec_hash(SWEEP),
            lean_spec=lean_spec)
        led.commit()
    return path, s


def lean_of(path):
    return only_section(cover(path))["sources"][0]["hypotheses"][0]["lean"]


# ---------------------------------------------------------------- checkpoints
@pytest.mark.parametrize("cap", [60, 100, 200, 400])
def test_interrupted_sweep_reconstructs_the_exact_completed_prefix(tmp_path, cap):
    path, summary = sweep(tmp_path / "p.sqlite", max_attempts=cap)
    lean = lean_of(path)
    ck, pre = lean["checkpoint"], lean["completed_prefix"]
    items = [describe(s) for s in expand_iter(SWEEP)]
    cursor = ck["cursor_candidates_processed"]
    assert 0 < cursor < SWEEP_N and ck["stop_reason"] == "max_attempts"
    assert pre["status"] == "reconstructed" and pre["completed"] == cursor
    assert pre["first_completed"] == items[0] and pre["last_completed"] == items[cursor - 1]
    assert pre["first_remaining"] == items[cursor]                          # remainder starts right after
    assert pre["expanded_total"] == SWEEP_N and pre["remaining"] == SWEEP_N - cursor
    assert ck["requested_upper_bound"] == SWEEP_N
    # independent evidence that the prefix is exactly what ran: the true key (position 141) is stored
    # as a pass only if the sweep got past it
    with Ledger(path) as led:
        stored = led.conn.execute("SELECT COUNT(*) FROM attempt").fetchone()[0]
    assert (stored > 0) == (cursor > TRUE_INDEX)
    assert "stopped: max_attempts" in only_section(cover(path))["sources"][0]["hypotheses"][0]["completion"]


def test_a_finished_sweep_has_cursor_equal_to_requested_and_unchanged_accounting(tmp_path):
    path, _ = sweep(tmp_path / "f.sqlite")
    lean = lean_of(path)
    assert lean["complete"] is True and lean["checkpoint"]["stop_reason"] == "exhausted"
    assert lean["checkpoint"]["cursor_candidates_processed"] == lean["checkpoint"]["requested_upper_bound"]
    assert lean["completed_prefix"] == {"status": "complete_by_recorded_flag"}
    with Ledger(path) as led:                                    # logical totals unaffected by checkpoints
        tid = led.conn.execute("SELECT id FROM target").fetchone()[0]
        assert led.attempt_count(tid) == only_section(cover(path))["sources"][0]["logical_attempts"]
    # a re-run of a stopped sweep replaces the checkpoint with the new one
    path2, _ = sweep(tmp_path / "r.sqlite", max_attempts=100)
    sweep(path2)
    again = lean_of(path2)
    assert again["complete"] is True and again["checkpoint"]["cursor_candidates_processed"] == SWEEP_N


def test_missing_or_mismatched_checkpoints_stay_unknown(tmp_path):
    # a summary written without a checkpoint (older code)
    path, _ = sweep(tmp_path / "o.sqlite", max_attempts=100, lean_spec=None)
    lean = lean_of(path)
    assert lean["checkpoint"] == "unknown" and lean["completed_prefix"]["status"] == "unknown"
    assert "no checkpoint recorded" in lean["completed_prefix"]["reason"]
    assert only_section(cover(path))["sources"][0]["hypotheses"][0]["completion"].startswith("incomplete")
    # a checkpoint written under a different expansion order is not reinterpreted
    path2, _ = sweep(tmp_path / "v.sqlite", max_attempts=100, lean_spec={**SPEC, "expansion_version": 99})
    pre = lean_of(path2)["completed_prefix"]
    assert pre["status"] == "unknown" and "differs" in pre["reason"]
    # --no-reconstruct keeps the recorded facts but does not re-expand
    path3, _ = sweep(tmp_path / "n.sqlite", max_attempts=100)
    rep = C.build([{"path": path3, "run": None, "job": None}], [], reconstruct=False)
    lean3 = only_section(rep)["sources"][0]["hypotheses"][0]["lean"]
    assert lean3["completed_prefix"]["status"] == "not_reconstructed" and lean3["checkpoint"]["cursor_candidates_processed"]


def test_old_ledger_without_checkpoint_columns_is_migrated_and_still_reads(tmp_path):
    sweep_old = tmp_path / "x.sqlite"
    # read it as a never-migrated ledger first: unknown, not an error
    with Ledger(sweep_old) as led:
        h = led.add_hypothesis("program", "old sweep", "x", "proposer")
        led.add_target(Alphabet_latin(), CT, "section X", None, True)
        tid = led.conn.execute("SELECT id FROM target").fetchone()[0]
        led.conn.executescript("""DROP TABLE sweep_summary;
            CREATE TABLE sweep_summary (id INTEGER PRIMARY KEY, target_id TEXT NOT NULL,
              hypothesis_id INTEGER NOT NULL, family TEXT NOT NULL, sweep_id TEXT NOT NULL,
              attempts INTEGER NOT NULL, screened INTEGER NOT NULL DEFAULT 0, best_margin REAL,
              complete INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT (datetime('now')),
              UNIQUE (target_id, sweep_id));""")
        led.conn.execute("INSERT INTO sweep_summary (target_id, hypothesis_id, family, sweep_id, attempts,"
                         " complete) VALUES (?, ?, 'program', 's', 500, 0)", (tid, h))
        led.commit()
        # also add one attempt so a section exists
    rep = cover(sweep_old)
    src = rep["inputs"]["ledgers"][0]
    assert src["status"] == "ok" and src["schema"]["has_sweep_checkpoint"] is False
    lean = only_section(rep)["sources"][0]["hypotheses"][0]["lean"]
    assert lean["checkpoint"] == "unknown" and lean["complete"] is False and lean["counted_attempts"] == 500
    # opening it with the current Ledger adds the columns (migration) and the old row stays unknown
    with Ledger(sweep_old) as led:
        cols = {r[1] for r in led.conn.execute("PRAGMA table_info(sweep_summary)")}
    assert C.CHECKPOINT_COLUMNS <= cols


def Alphabet_latin():
    from lpswarm.alphabet import Alphabet
    return Alphabet.latin26()


# --------------------------------------------------------------- evidence manifest
def test_run_meta_is_recorded_and_coverage_separates_configurations(tmp_path):
    a, b = tmp_path / "a.sqlite", tmp_path / "b.sqlite"
    for path, nulls in ((a, 200), (b, 300)):
        ordinary(path)
        with Ledger(path) as led:
            meta = runmeta.collect("swarm", OracleConfig(null_samples=nulls),
                                   alphabet_path="data/alphabet/gematria_primus.json",
                                   manifest_path="data/lp/manifest.json", targets=[("LP2:x", 100)],
                                   caps={"max_attempts": 40, "rounds": 2, "note": None},
                                   models={"generators": ["packet"], "ranker": None})
            led.record_run_meta(meta)
    rep = cover(a, b)
    groups = only_section(rep)["evaluator_groups"]
    assert len(groups) == 2                                    # different oracle configs are never merged
    cfgs = {g["oracle_config"]["null_samples"] for g in groups}
    assert cfgs == {200, 300} and all(len(g["oracle_config_hash"]) == 64 for g in groups)
    assert all(g["git_shas"] for g in groups)
    src = rep["inputs"]["ledgers"][0]
    assert src["run_meta"][0]["command"] == "swarm" and src["run_meta"][0]["lpswarm_version"]
    # a ledger without run_meta is unknown, never given today's defaults
    old = ordinary(tmp_path / "old.sqlite")
    g = only_section(cover(old))["evaluator_groups"][0]
    assert g["oracle_config"] == "unknown" and g["oracle_config_hash"] == "unknown"


def test_one_ledger_used_with_two_configurations_is_flagged_not_attributed(tmp_path):
    p = ordinary(tmp_path / "m.sqlite")
    with Ledger(p) as led:
        for nulls in (200, 300):
            led.record_run_meta(runmeta.collect("swarm", OracleConfig(null_samples=nulls)))
    g = only_section(cover(p))["evaluator_groups"][0]
    assert "attribution unknown" in g["oracle_config"] and g["oracle_config_hash"] == "unknown"


def test_capture_failure_is_explicit_and_never_filled_in(tmp_path, monkeypatch, capsys):
    from lpswarm import cli
    p = ordinary(tmp_path / "f.sqlite")

    def boom(*a, **k):
        raise RuntimeError("could not read the oracle")
    monkeypatch.setattr(runmeta, "collect", boom)

    class Oracle:
        cfg = OracleConfig()
    with Ledger(p) as led:
        cli._record_run_meta(led, "swarm", Oracle(), type("A", (), {})(), [], {}, {})
    assert "could not record run metadata" in capsys.readouterr().err
    g = only_section(cover(p))["evaluator_groups"][0]
    assert g["oracle_config"] == "unknown"                       # not today's OracleConfig()
    meta = only_section(cover(p))["sources"][0]["run_meta"][0]
    assert "could not read the oracle" in meta["capture_error"]


def test_metadata_holds_no_secrets_and_only_hashes_of_config_files(tmp_path):
    secret_cfg = tmp_path / "overnight.toml"
    secret_cfg.write_text('api_key = "SECRET-IN-FILE"\n[overnight]\n', encoding="utf-8")
    from lpswarm.overnight import OvernightConfig
    cfg = OvernightConfig(models=str(secret_cfg), supervisor="claude-supervisor",
                          jobs=[{"id": "codex", "kind": "swarm", "args": ["--api-key", "SECRET-ARG"]}])
    path = runmeta.write_run_manifest(tmp_path, cfg, str(secret_cfg))
    text = path.read_text(encoding="utf-8")
    assert "SECRET-IN-FILE" not in text and "SECRET-ARG" not in text
    data = json.loads(text)
    assert data["overnight_toml_sha256"] == runmeta.file_sha(secret_cfg) and len(data["overnight_toml_sha256"]) == 64
    assert data["jobs"] == [{"id": "codex", "kind": "swarm"}] and data["supervisor_model"] == "claude-supervisor"
    meta = runmeta.collect("swarm", OracleConfig(), caps={"max_attempts": 5})
    blob = json.dumps(meta).lower()
    assert "api_key" not in blob and "password" not in blob and "token" not in blob
    assert meta["oracle_config"]["null_samples"] == 3000 and meta["corpus"]["sha256"] != "unknown"

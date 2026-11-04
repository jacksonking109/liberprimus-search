"""SQLite ledger: hypotheses, key candidates, attempts, results, corpus, budget.

Every attempt is deduplicated on sha256(target, family, canonical params, key
hash). Recording an attempt that already exists is a no-op, so re-running the
same search adds no rows.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from lpswarm.alphabet import Alphabet


def canonical_json(obj: Any) -> str:
    return json.dumps(_canon(obj), sort_keys=True, separators=(",", ":"), default=_default)


def _canon(obj: Any) -> Any:
    """Normalise values so equal params hash equally (1 == 1.0 == np.int64(1))."""
    if isinstance(obj, dict):
        return {str(k): _canon(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_canon(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return [_canon(v) for v in obj.tolist()]
    if isinstance(obj, (bool, np.bool_)):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        f = float(obj)
        return int(f) if f.is_integer() else f
    return obj


def _default(o: Any) -> Any:
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def dedupe_hash(target_id: str, family: str, params: dict, key_hash: str) -> str:
    return hashlib.sha256(canonical_json([target_id, family, params, key_hash]).encode()).hexdigest()


def target_id_for(alphabet: Alphabet, ciphertext: np.ndarray, breaks=None) -> str:
    """Scores with and without word breaks are different experiments, so breaks are
    part of the target's identity (and of every attempt's dedupe hash)."""
    h = hashlib.sha256()
    h.update(canonical_json(alphabet.to_json()).encode())
    h.update(np.asarray(ciphertext, dtype=np.int16).tobytes())
    if breaks:
        h.update(b"breaks:" + canonical_json(sorted(int(b) for b in breaks)).encode())
    return h.hexdigest()


class Ledger:
    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        # timeout: several overnight jobs may write the shared spend ledger at once.
        # check_same_thread=False: the router calls models from worker threads and
        # serialises its ledger use with a lock.
        self.conn = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        schema = resources.files("lpswarm.ledger").joinpath("schema.sql").read_text(encoding="utf-8")
        self._migrate()
        self.conn.executescript(schema)
        self.conn.execute("PRAGMA journal_mode = WAL" if self.path != ":memory:" else "PRAGMA journal_mode = MEMORY")
        self._key_ids: dict[str, int] = {}

    _COLUMNS = {"target": {"word_breaks": "TEXT"},
                "attempt": {"output_hash": "TEXT"},
                "key_candidate": {"value_json": "TEXT"},
                "result": {"unreachable": "INTEGER NOT NULL DEFAULT 0", "word_score": "REAL",
                           "null_variant": "TEXT"}}

    def _migrate(self) -> None:
        """Add columns introduced after a ledger was created (tables are created by the
        schema script; this only extends existing ones)."""
        for table, cols in self._COLUMNS.items():
            have = {r[1] for r in self.conn.execute(f"PRAGMA table_info({table})")}
            if not have:
                continue  # new ledger: the schema creates the table complete
            for col, decl in cols.items():
                if col not in have:
                    self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")
        self.conn.commit()

    def close(self) -> None:
        self.conn.commit()
        self.conn.close()

    def __enter__(self) -> "Ledger":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    @contextmanager
    def transaction(self) -> Iterator[None]:
        try:
            yield
            self.conn.commit()
        except BaseException:
            self.rollback()
            raise

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()
        self._key_ids.clear()  # cached ids may refer to rolled-back rows

    # ---------------------------------------------------------------- records
    def add_corpus_item(self, work: str, author: str | None = None, edition: str | None = None,
                        translation: str | None = None, page_line_structure: str | None = None,
                        source_url: str | None = None, confidence_tag: str = "speculative",
                        ring: int = 3, content_hash: str | None = None) -> int:
        if content_hash:
            row = self.conn.execute("SELECT id FROM corpus_item WHERE content_hash=?",
                                    (content_hash,)).fetchone()
            if row:
                return int(row["id"])
        cur = self.conn.execute(
            "INSERT INTO corpus_item (work, author, edition, translation, page_line_structure,"
            " source_url, confidence_tag, ring, content_hash) VALUES (?,?,?,?,?,?,?,?,?)",
            (work, author, edition, translation, page_line_structure, source_url, confidence_tag,
             ring, content_hash))
        return int(cur.lastrowid)

    def add_target(self, alphabet: Alphabet, ciphertext: np.ndarray, label: str,
                   page_range: str | None = None, is_synthetic: bool = False,
                   breaks=None) -> str:
        tid = target_id_for(alphabet, ciphertext, breaks)
        wb = canonical_json(sorted(int(b) for b in breaks)) if breaks else None
        self.conn.execute(
            "INSERT OR IGNORE INTO target (id, label, alphabet, length, page_range, is_synthetic,"
            " word_breaks) VALUES (?,?,?,?,?,?,?)",
            (tid, label, alphabet.name, int(len(ciphertext)), page_range, int(is_synthetic), wb))
        return tid

    def add_hypothesis(self, cipher_family: str, description: str, proposer_model: str,
                       proposer_role: str, parent_id: int | None = None,
                       status: str = "open") -> int:
        if not proposer_model or not proposer_role:
            raise ValueError("provenance is mandatory: proposer_model and proposer_role")
        cur = self.conn.execute(
            "INSERT INTO hypothesis (cipher_family, description, proposer_model, proposer_role,"
            " parent_id, status) VALUES (?,?,?,?,?,?)",
            (cipher_family, description, proposer_model, proposer_role, parent_id, status))
        return int(cur.lastrowid)

    def find_or_add_hypothesis(self, cipher_family: str, description: str, proposer_model: str,
                               proposer_role: str) -> int:
        row = self.conn.execute(
            "SELECT id FROM hypothesis WHERE cipher_family=? AND description=? AND proposer_model=?"
            " AND proposer_role=? ORDER BY id LIMIT 1",
            (cipher_family, description, proposer_model, proposer_role)).fetchone()
        if row:
            return int(row["id"])
        return self.add_hypothesis(cipher_family, description, proposer_model, proposer_role)

    def set_hypothesis_status(self, hypothesis_id: int, status: str) -> None:
        self.conn.execute("UPDATE hypothesis SET status=? WHERE id=?", (status, hypothesis_id))

    def key_candidate_id(self, value_hash: str, derivation: str, preview: str | None = None,
                         corpus_item_id: int | None = None, edition_id: str | None = None,
                         value_json: str | None = None) -> int:
        ck = (value_hash, derivation)
        kid = self._key_ids.get(ck)
        if kid is not None:
            return kid
        self.conn.execute(
            "INSERT OR IGNORE INTO key_candidate (corpus_item_id, derivation, value_hash,"
            " value_preview, value_json, edition_id) VALUES (?,?,?,?,?,?)",
            (corpus_item_id, derivation, value_hash, preview, value_json, edition_id))
        kid = int(self.conn.execute(
            "SELECT id FROM key_candidate WHERE value_hash=? AND derivation=?",
            (value_hash, derivation)).fetchone()["id"])
        self._key_ids[ck] = kid
        return kid

    def hypothesis_has_pass(self, hypothesis_id: int) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM attempt a JOIN result r ON r.attempt_id=a.id"
            " WHERE a.hypothesis_id=? AND r.passed=1 LIMIT 1", (hypothesis_id,)).fetchone() is not None

    def has_attempt(self, dhash: str) -> bool:
        return self.conn.execute("SELECT 1 FROM attempt WHERE dedupe_hash=?",
                                 (dhash,)).fetchone() is not None

    def prior_verdict(self, dhash: str) -> str | None:
        """Verdict of an already-recorded attempt (None if absent or unscored)."""
        row = self.conn.execute("SELECT r.verdict FROM attempt a JOIN result r ON r.attempt_id=a.id"
                                " WHERE a.dedupe_hash=?", (dhash,)).fetchone()
        return row[0] if row else None

    def prior_output(self, target_id: str, output_hash: str) -> str | None:
        """Verdict of an earlier attempt on this target whose decryption was identical
        (a different key or family that is the same cipher here), or None."""
        row = self.conn.execute("SELECT r.verdict FROM attempt a JOIN result r ON r.attempt_id=a.id"
                                " WHERE a.target_id=? AND a.output_hash=? LIMIT 1",
                                (target_id, output_hash)).fetchone()
        return row[0] if row else None

    def output_hashes(self, target_id: str) -> set[str]:
        return {r[0] for r in self.conn.execute(
            "SELECT output_hash FROM attempt WHERE target_id=? AND output_hash IS NOT NULL",
            (target_id,))}

    def attempt_count(self, target_id: str) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM attempt WHERE target_id=?",
                                     (target_id,)).fetchone()[0])

    def record_attempt(self, *, hypothesis_id: int, key_candidate_id: int, target_id: str,
                       cipher_family: str, params: dict, dedupe: str, executor_version: str,
                       runtime_ms: float | None = None, page_range: str | None = None,
                       cost_usd: float = 0.0, output_hash: str | None = None) -> int | None:
        """Insert an attempt; returns its id, or None if it was already recorded."""
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO attempt (hypothesis_id, key_candidate_id, target_id,"
            " cipher_family, params_json, page_range, executor_version, runtime_ms, cost_usd,"
            " dedupe_hash, output_hash) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (hypothesis_id, key_candidate_id, target_id, cipher_family, canonical_json(params),
             page_range, executor_version, runtime_ms, cost_usd, dedupe, output_hash))
        return int(cur.lastrowid) if cur.rowcount else None

    def record_result(self, attempt_id: int, report: Any, plaintext_preview: str | None = None) -> None:
        r = report
        self.conn.execute(
            "INSERT OR IGNORE INTO result (attempt_id, stage, verdict, ic, ngram_score, dict_score,"
            " lm_loglik, combined, screen_score, threshold, null_percentile, passed,"
            " attempt_count_at_scoring, alpha_eff, unreachable, word_score, null_variant,"
            " plaintext_preview) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (attempt_id, r.stage, r.verdict, r.ic, r.ngram_score, r.dict_score, r.lm_loglik,
             r.combined, r.screen_score, r.threshold, r.null_percentile, int(r.passed),
             r.attempt_count, r.alpha_eff, int(bool(getattr(r, "unreachable", False))),
             getattr(r, "word_score", None), getattr(r, "null_variant", None), plaintext_preview))

    def record_final_check(self, attempt_id: int, attempt_count: int, alpha_eff: float,
                           threshold: float, passed: bool) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO final_check (attempt_id, attempt_count_final, alpha_eff_final,"
            " threshold_final, passed_final) VALUES (?,?,?,?,?)",
            (attempt_id, attempt_count, alpha_eff, threshold, int(passed)))

    def candidates_for_final(self, target_id: str) -> list[dict]:
        """In-run passes and near misses on a target, with their scores."""
        rows = self.conn.execute(
            "SELECT a.id AS attempt_id, r.combined, r.verdict, r.null_variant FROM attempt a"
            " JOIN result r ON r.attempt_id=a.id WHERE a.target_id=? AND r.stage='full'"
            " AND r.verdict IN ('pass','near_miss')", (target_id,)).fetchall()
        return [dict(r) for r in rows]

    def attempt_detail(self, attempt_id: int) -> dict | None:
        row = self.conn.execute(
            "SELECT a.*, k.value_json, k.value_preview, k.derivation FROM attempt a"
            " JOIN key_candidate k ON k.id=a.key_candidate_id WHERE a.id=?", (attempt_id,)).fetchone()
        return dict(row) if row else None

    def target_info(self, target_id: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM target WHERE id=?", (target_id,)).fetchone()
        return dict(row) if row else None

    def add_budget_event(self, vendor: str, model: str, tokens_in: int = 0, tokens_out: int = 0,
                         usd: float = 0.0, task_id: str | None = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO budget_event (vendor, model, tokens_in, tokens_out, usd, task_id)"
            " VALUES (?,?,?,?,?,?)", (vendor, model, tokens_in, tokens_out, usd, task_id))
        return int(cur.lastrowid)

    def add_rate_limit_event(self, model: str, hit_at: float, resume_at: float, source: str,
                             parsed: bool = False, message: str | None = None) -> None:
        self.conn.execute("INSERT INTO rate_limit_event (model, hit_at, resume_at, source, parsed,"
                          " message) VALUES (?,?,?,?,?,?)",
                          (model, hit_at, resume_at, source, int(parsed), (message or "")[:500]))
        self.conn.commit()

    def active_limit(self, model, now: float, include_window: bool = False) -> float | None:
        """Latest resume time for a model (or any of a list of models sharing a quota)
        if it is still in the future. Pauses from the local call cap (source 'window')
        are recorded for history but ignored unless include_window: the router works
        them out live from the call count, so raising the cap takes effect at once."""
        models = [model] if isinstance(model, str) else list(model)
        q = ",".join("?" * len(models))
        extra = "" if include_window else " AND source != 'window'"
        row = self.conn.execute(f"SELECT MAX(resume_at) FROM rate_limit_event WHERE model IN ({q})"
                                + extra, models).fetchone()
        return float(row[0]) if row and row[0] is not None and row[0] > now else None

    def calls_since(self, model, since_epoch: float) -> list[float]:
        """Epoch times of logged calls since `since_epoch` for a model or a list of models
        (a shared plan quota), oldest first."""
        models = [model] if isinstance(model, str) else list(model)
        q = ",".join("?" * len(models))
        rows = self.conn.execute(
            "SELECT CAST(strftime('%s', created_at) AS REAL) FROM budget_event"
            f" WHERE model IN ({q}) AND CAST(strftime('%s', created_at) AS REAL) >= ?"
            " ORDER BY created_at, id", (*models, since_epoch)).fetchall()
        return [float(r[0]) for r in rows]

    # ---------------------------------------------------------------- queries
    def counts(self) -> dict[str, int]:
        return {t: int(self.conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0])
                for t in ("hypothesis", "key_candidate", "attempt", "result", "target",
                          "corpus_item", "budget_event")}

    def ruled_out(self, target_id: str | None = None) -> list[dict]:
        """What has been tried and failed, grouped by target, family and hypothesis."""
        sql = (
            "SELECT a.target_id, t.label, a.cipher_family, h.id AS hypothesis_id, h.description,"
            " h.proposer_model, h.proposer_role, COUNT(*) AS attempts,"
            " SUM(r.verdict='fail') AS fails, SUM(r.verdict='near_miss') AS near_misses,"
            " SUM(r.verdict='pass') AS passes, MAX(r.combined) AS best_combined"
            " FROM attempt a JOIN result r ON r.attempt_id=a.id"
            " JOIN hypothesis h ON h.id=a.hypothesis_id JOIN target t ON t.id=a.target_id"
            + (" WHERE a.target_id=?" if target_id else "") +
            " GROUP BY a.target_id, a.cipher_family, h.id"
            " HAVING SUM(r.passed)=0 ORDER BY t.label, a.cipher_family")
        rows = self.conn.execute(sql, (target_id,) if target_id else ()).fetchall()
        return [dict(r) for r in rows]

    def tried(self, target_id: str) -> list[dict]:
        """Every hypothesis tried on a target with its attempt count (no verdicts)."""
        rows = self.conn.execute(
            "SELECT a.cipher_family, h.description, h.proposer_model, COUNT(*) AS attempts"
            " FROM attempt a JOIN hypothesis h ON h.id=a.hypothesis_id WHERE a.target_id=?"
            " GROUP BY a.cipher_family, h.id ORDER BY h.id", (target_id,)).fetchall()
        return [dict(r) for r in rows]

    def leads(self, target_id: str | None = None, include_near_miss: bool = False,
              limit: int = 50, final_only: bool = False) -> list[dict]:
        """Human queue: passing (optionally near-miss) attempts, best margin first.

        `passed_final` is NULL until final_check has run for the target; with
        final_only=True only attempts that survived it are returned.
        """
        verdicts = ("pass", "near_miss") if include_near_miss else ("pass",)
        q = ",".join("?" * len(verdicts))
        where = [f"r.verdict IN ({q})"]
        args: list = list(verdicts)
        if target_id:
            where.append("a.target_id=?")
            args.append(target_id)
        if final_only:
            where.append("f.passed_final=1")
        sql = ("SELECT a.id AS attempt_id, a.target_id, a.cipher_family, a.params_json,"
               " k.value_preview AS key_preview, k.derivation, r.verdict, r.combined, r.threshold,"
               " r.null_percentile, r.attempt_count_at_scoring, r.plaintext_preview, r.null_variant,"
               " f.passed_final, f.threshold_final, f.attempt_count_final,"
               " h.proposer_model, h.proposer_role"
               " FROM attempt a JOIN result r ON r.attempt_id=a.id"
               " JOIN key_candidate k ON k.id=a.key_candidate_id"
               " JOIN hypothesis h ON h.id=a.hypothesis_id"
               " LEFT JOIN final_check f ON f.attempt_id=a.id"
               " WHERE " + " AND ".join(where) +
               " ORDER BY (r.combined - r.threshold) DESC LIMIT ?")
        args.append(int(limit))
        return [dict(r) for r in self.conn.execute(sql, args).fetchall()]

    def targets(self) -> list[dict]:
        return [dict(r) for r in self.conn.execute("SELECT * FROM target ORDER BY created_at")]

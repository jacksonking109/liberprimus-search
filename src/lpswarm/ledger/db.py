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
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=_default)


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


def target_id_for(alphabet: Alphabet, ciphertext: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(canonical_json(alphabet.to_json()).encode())
    h.update(np.asarray(ciphertext, dtype=np.int16).tobytes())
    return h.hexdigest()


class Ledger:
    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        schema = resources.files("lpswarm.ledger").joinpath("schema.sql").read_text(encoding="utf-8")
        self.conn.executescript(schema)
        self.conn.execute("PRAGMA journal_mode = WAL" if self.path != ":memory:" else "PRAGMA journal_mode = MEMORY")
        self._key_ids: dict[str, int] = {}

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
            self.conn.rollback()
            raise

    def commit(self) -> None:
        self.conn.commit()

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
                   page_range: str | None = None, is_synthetic: bool = False) -> str:
        tid = target_id_for(alphabet, ciphertext)
        self.conn.execute(
            "INSERT OR IGNORE INTO target (id, label, alphabet, length, page_range, is_synthetic)"
            " VALUES (?,?,?,?,?,?)",
            (tid, label, alphabet.name, int(len(ciphertext)), page_range, int(is_synthetic)))
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
                         corpus_item_id: int | None = None, edition_id: str | None = None) -> int:
        kid = self._key_ids.get(value_hash)
        if kid is not None:
            return kid
        self.conn.execute(
            "INSERT OR IGNORE INTO key_candidate (corpus_item_id, derivation, value_hash,"
            " value_preview, edition_id) VALUES (?,?,?,?,?)",
            (corpus_item_id, derivation, value_hash, preview, edition_id))
        kid = int(self.conn.execute("SELECT id FROM key_candidate WHERE value_hash=?",
                                    (value_hash,)).fetchone()["id"])
        self._key_ids[value_hash] = kid
        return kid

    def hypothesis_has_pass(self, hypothesis_id: int) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM attempt a JOIN result r ON r.attempt_id=a.id"
            " WHERE a.hypothesis_id=? AND r.passed=1 LIMIT 1", (hypothesis_id,)).fetchone() is not None

    def has_attempt(self, dhash: str) -> bool:
        return self.conn.execute("SELECT 1 FROM attempt WHERE dedupe_hash=?",
                                 (dhash,)).fetchone() is not None

    def attempt_count(self, target_id: str) -> int:
        return int(self.conn.execute("SELECT COUNT(*) FROM attempt WHERE target_id=?",
                                     (target_id,)).fetchone()[0])

    def record_attempt(self, *, hypothesis_id: int, key_candidate_id: int, target_id: str,
                       cipher_family: str, params: dict, dedupe: str, executor_version: str,
                       runtime_ms: float | None = None, page_range: str | None = None,
                       cost_usd: float = 0.0) -> int | None:
        """Insert an attempt; returns its id, or None if it was already recorded."""
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO attempt (hypothesis_id, key_candidate_id, target_id,"
            " cipher_family, params_json, page_range, executor_version, runtime_ms, cost_usd,"
            " dedupe_hash) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (hypothesis_id, key_candidate_id, target_id, cipher_family, canonical_json(params),
             page_range, executor_version, runtime_ms, cost_usd, dedupe))
        return int(cur.lastrowid) if cur.rowcount else None

    def record_result(self, attempt_id: int, report: Any, plaintext_preview: str | None = None) -> None:
        r = report
        self.conn.execute(
            "INSERT OR IGNORE INTO result (attempt_id, stage, verdict, ic, ngram_score, dict_score,"
            " lm_loglik, combined, screen_score, threshold, null_percentile, passed,"
            " attempt_count_at_scoring, alpha_eff, plaintext_preview)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (attempt_id, r.stage, r.verdict, r.ic, r.ngram_score, r.dict_score, r.lm_loglik,
             r.combined, r.screen_score, r.threshold, r.null_percentile, int(r.passed),
             r.attempt_count, r.alpha_eff, plaintext_preview))

    def add_budget_event(self, vendor: str, model: str, tokens_in: int = 0, tokens_out: int = 0,
                         usd: float = 0.0, task_id: str | None = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO budget_event (vendor, model, tokens_in, tokens_out, usd, task_id)"
            " VALUES (?,?,?,?,?,?)", (vendor, model, tokens_in, tokens_out, usd, task_id))
        return int(cur.lastrowid)

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

    def leads(self, target_id: str | None = None, include_near_miss: bool = False,
              limit: int = 50) -> list[dict]:
        """Human queue: passing (optionally near-miss) attempts, best first."""
        verdicts = ("pass", "near_miss") if include_near_miss else ("pass",)
        q = ",".join("?" * len(verdicts))
        sql = ("SELECT a.id AS attempt_id, a.target_id, a.cipher_family, a.params_json,"
               " k.value_preview AS key_preview, k.derivation, r.verdict, r.combined, r.threshold,"
               " r.null_percentile, r.attempt_count_at_scoring, r.plaintext_preview,"
               " h.proposer_model, h.proposer_role"
               " FROM attempt a JOIN result r ON r.attempt_id=a.id"
               " JOIN key_candidate k ON k.id=a.key_candidate_id"
               " JOIN hypothesis h ON h.id=a.hypothesis_id"
               f" WHERE r.verdict IN ({q})" + (" AND a.target_id=?" if target_id else "") +
               " ORDER BY (r.combined - r.threshold) DESC LIMIT ?")
        args: tuple = verdicts + ((target_id,) if target_id else ()) + (limit,)
        return [dict(r) for r in self.conn.execute(sql, args).fetchall()]

-- lpswarm ledger schema (SQLite). Negative results are first-class data.
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS corpus_item (
    id INTEGER PRIMARY KEY,
    work TEXT NOT NULL,
    author TEXT,
    edition TEXT,
    translation TEXT,
    page_line_structure TEXT,
    source_url TEXT,
    confidence_tag TEXT NOT NULL DEFAULT 'speculative'
        CHECK (confidence_tag IN ('confirmed', 'inferred', 'speculative')),
    ring INTEGER NOT NULL DEFAULT 3 CHECK (ring BETWEEN 0 AND 3),
    content_hash TEXT UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- A ciphertext under attack (real page range or a synthetic case).
CREATE TABLE IF NOT EXISTS target (
    id TEXT PRIMARY KEY,               -- sha256 of alphabet name + ciphertext
    label TEXT NOT NULL,
    alphabet TEXT NOT NULL,
    length INTEGER NOT NULL,
    page_range TEXT,
    is_synthetic INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS hypothesis (
    id INTEGER PRIMARY KEY,
    cipher_family TEXT NOT NULL,
    description TEXT NOT NULL,
    proposer_model TEXT NOT NULL,      -- 'human' / 'baseline' in Phase 1
    proposer_role TEXT NOT NULL,
    parent_id INTEGER REFERENCES hypothesis(id),
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'running', 'ruled_out', 'lead', 'confirmed', 'abandoned')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS key_candidate (
    id INTEGER PRIMARY KEY,
    corpus_item_id INTEGER REFERENCES corpus_item(id),
    derivation TEXT NOT NULL,          -- e.g. 'wordlist:<name>', 'enumerate', 'synthetic'
    value_hash TEXT NOT NULL UNIQUE,
    value_preview TEXT,
    edition_id TEXT
);

CREATE TABLE IF NOT EXISTS attempt (
    id INTEGER PRIMARY KEY,
    hypothesis_id INTEGER NOT NULL REFERENCES hypothesis(id),
    key_candidate_id INTEGER NOT NULL REFERENCES key_candidate(id),
    target_id TEXT NOT NULL REFERENCES target(id),
    cipher_family TEXT NOT NULL,
    params_json TEXT NOT NULL,
    page_range TEXT,
    executor_version TEXT NOT NULL,
    runtime_ms REAL,
    cost_usd REAL NOT NULL DEFAULT 0,
    dedupe_hash TEXT NOT NULL UNIQUE,  -- sha256(target, family, params, key value_hash)
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS attempt_target ON attempt(target_id);
CREATE INDEX IF NOT EXISTS attempt_hyp ON attempt(hypothesis_id);

CREATE TABLE IF NOT EXISTS result (
    attempt_id INTEGER PRIMARY KEY REFERENCES attempt(id),
    stage TEXT NOT NULL,               -- 'screen' or 'full'
    verdict TEXT NOT NULL,             -- 'fail' / 'near_miss' / 'pass'
    ic REAL,
    ngram_score REAL,
    dict_score REAL,
    lm_loglik REAL,
    combined REAL,
    screen_score REAL,
    threshold REAL,
    null_percentile REAL,
    passed INTEGER NOT NULL,
    attempt_count_at_scoring INTEGER NOT NULL,
    alpha_eff REAL NOT NULL,
    plaintext_preview TEXT
);
CREATE INDEX IF NOT EXISTS result_verdict ON result(verdict);

CREATE TABLE IF NOT EXISTS budget_event (
    id INTEGER PRIMARY KEY,
    vendor TEXT NOT NULL,
    model TEXT NOT NULL,
    tokens_in INTEGER NOT NULL DEFAULT 0,
    tokens_out INTEGER NOT NULL DEFAULT 0,
    usd REAL NOT NULL DEFAULT 0,
    task_id TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

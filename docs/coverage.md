# `lpswarm coverage`: what the ledgers record

A read-only inventory of recorded experiments. It reads job ledgers (SQLite) and writes two files:
`coverage.json` (structured evidence) and `coverage.md` (a digest for people and planners). It never
writes to a ledger, starts a job, calls a model or publishes anything.

```powershell
.\.venv\Scripts\lpswarm.exe coverage                       # all runs under reports\overnight
.\.venv\Scripts\lpswarm.exe coverage --latest 1            # newest run only
.\.venv\Scripts\lpswarm.exe coverage --run 20261104-2305   # named run(s)
.\.venv\Scripts\lpswarm.exe coverage --ledger lp.sqlite --ledger other.sqlite --out reports\mine
```

## Inputs

Exactly these are searched, and nothing else (no caches, archives or the results worktree):

- every `--ledger FILE` given (a file; never created if missing);
- with `--runs-dir DIR` (default `reports/overnight` when no `--ledger` is given):
  `DIR/<run>/<job>/ledger.sqlite`, exactly two levels, not recursive. `--run NAME` (repeatable) and
  `--latest N` narrow the run folders. The model-spend ledger has no such path and is never read.

Optional sidecars, used only when present beside a discovered ledger: `report.json` in the job folder
(stop reason and proposal counts per target) and the run's `state.json` (job status, and only these
arguments: `--sections --max-attempts --rounds --per-round --generators --lean-threshold --timeout`).
Nothing else from them, and no prompts, transcripts, keys or config, is copied.

Output goes to `--out` (default `reports/coverage`, git-ignored). `--top-leads` bounds the leads kept per
target and ledger (default 10); `--max-hypotheses` bounds the hypotheses listed per target and ledger
in the JSON (totals always cover all of them).

**Exit codes:** `0` every selected input was read; `3` partial (some input missing, locked, corrupt,
unreadable or unsupported; the files are written and name each failure); `4` nothing readable (files
still written, status `no_readable_inputs`); `2` usage error. Incomplete discovery (a missing runs
folder or an unknown `--run`) also gives status `partial`.

## How a ledger is read

SQLite in read-only mode (`mode=ro`, `PRAGMA query_only`), all queries of one ledger inside **one read
transaction**: a consistent snapshot of what was committed at that moment, WAL included. No journal
mode is changed and nothing is checkpointed or copied, so a running job is not disturbed. Different
ledgers are read at slightly different moments, and the executor commits every 2000 attempts, so a
running job's newest attempts may be missing. Aggregates are SQL `GROUP BY` queries; only the best
leads per target are fetched row by row.

Supported schemas: the current one, and older ledgers that lack `null_variant`, `output_hash`,
`final_check` or `sweep_summary` (then the matching fields say `unknown`). A file missing a required
table or column is reported `unsupported_schema` and is **not** treated as empty coverage.

## Definitions (also in `coverage.json`)

- **stored rows**: attempts stored one row each. **lean counted**: attempts that failed inside a lean
  sweep, counted in `sweep_summary` but not stored. **logical attempts** = stored rows + lean counted,
  the same total the executor uses for its end-of-search correction. It is not a count of distinct
  ciphers or decryptions.
- **identity**: the target id (sha256 of alphabet, ciphertext and word breaks). Transcription version
  is not recorded: `unknown`. Word breaks are shown as present/absent, a count and a short hash.
- **evaluator group**: ledgers are totalled together only if their recorded `executor_version` set
  and recorded oracle configuration are identical. Ledgers written by `swarm`/`baseline` since the
  evidence manifest existed carry the ACTUAL configuration (`run_meta`, below); older ledgers have
  `oracle_config: unknown` and are never labelled with today's settings. A ledger used with two
  different configurations is flagged "per-attempt attribution unknown", not split by guesswork.
- **completion** (evidence only, never inferred from counts):
  `completed` = a finished lean sweep, or a hypothesis recorded `ruled_out` (its key source ran out);
  `incomplete` = a lean sweep stopped early, or a hypothesis left `open` with stored attempts (stopped
  early; the reason is in the ledger only for lean sweeps via the flag, and otherwise only in
  `report.json`); `interrupted` = still marked `running`. A requested range is not an executed range:
  a lean summary holds a count, a flag and the proposal's description, so the completed subset of an
  incomplete sweep is `unknown`.
- **overlap**: there is no cross-job or cross-run deduplication, so totals summed over ledgers may
  contain the same work more than once. "Same description in several ledgers" is a text match, not
  proof of identical ciphers.
- **leads**: stored passes and near misses, best recorded margin first. **recorded margin** =
  combined - threshold, both as recorded at scoring time (the threshold depends on the attempt count
  then). It is not a probability; nothing is re-scored. **null percentile** is as recorded: the share of
  calibration null scores at or below the score, not the probability that a decryption is wrong.
  **final check**: `not run` when no `final_check` row exists; otherwise survived or did not.
  "Survivors" counts only candidates with a recorded recheck that passed.
- Free-text rationales that models attached to proposals (after ` | why:`) are dropped.

## Evidence recorded by new runs (older ledgers: `unknown`)

**Evidence manifest.** Each `swarm`/`baseline` invocation appends a row to the ledger's `run_meta`
table: lpswarm and executor version, development git SHA (`unknown` plus the reason if it cannot be
read), Python/platform, the **actual oracle configuration** after command-line overrides (and its
hash), a hash of the bundled language texts, the alphabet and manifest hashes, the target labels with
their recorded section hashes, resource caps, and the generator/ranker model *names*. No credentials,
prompts, config files, transcripts or held-out data. If capture fails, a row with an explicit
`meta_error` is written and the oracle configuration stays `unknown`; nothing is filled in. An
overnight run also writes `manifest.json` in its run folder: the same facts plus the SHA-256 of
`overnight.toml` and `models.toml` (hashes only, never contents).

**Lean-sweep checkpoints.** A lean summary now also records the proposal's canonical spec, the
expansion-order version, the text length, the requested size (an upper bound), the **cursor**
(candidates fully processed in the deterministic expansion order; the candidate that hit a stop is not
counted), how many of those were skipped as the same decryption, and the stop reason (`exhausted`,
`max_attempts`, `timeout`, `stop_file`, `stop_event`). Coverage reports requested, counted attempts,
cursor, remaining, equivalents skipped and stop reason separately, and for an incomplete sweep
re-expands the spec read-only (`--no-reconstruct` skips this) to name the first and last completed
cipher and the first remaining one. A different expansion version, or a missing checkpoint, stays
`unknown`. **Resume is unchanged:** an unfinished sweep is re-run from the start; the cursor is never
used to skip work, and logical attempt counts and the end-of-search threshold are unaffected.

## Known limitations

1. Ledgers written before the evidence manifest have no oracle configuration (only
   `executor_version`, and per result the threshold and alpha actually applied).
2. Lean summaries written before checkpoints do not store the spec, cursor or stop reason; their
   completed subset is unknown.
3. For hypotheses that are not lean sweeps, why an unfinished job stopped is recorded only in
   `report.json` (when present); invalid proposals never reach a ledger (their counts and grouped
   reasons are in `report.json` as `invalid_reasons`).
4. Hypotheses with no attempts cannot be tied to a target; they are counted per ledger
   (`hypotheses_without_attempts`).
5. No cross-job or cross-run deduplication, so totals may overlap.

## Sample

`docs/coverage_sample/` holds output generated from small synthetic ledgers (built with the helpers in
`tests/test_coverage.py` and `tests/test_evidence.py`): one run with a recorded evidence manifest, one
lean sweep stopped at 200 of 676 candidates (with its reconstructed completed prefix), and an older
ledger with no manifest, so both the recorded and `unknown` cases show. Timestamps and the git SHA are
from when it was generated.

## Follow-ups still open

- **Output-hash memory for lean sweeps:** a second proposal covering the same ciphers as an earlier
  lean sweep is currently counted again (conservative, but slower).
- **Stop reasons for non-lean hypotheses** in the ledger, so they no longer depend on `report.json`.
- **Resume from the cursor:** deliberately not done; it needs its own design so that unknown work is
  never skipped under an assumed checkpoint.
- **Capability matrix / versioned briefs:** the coverage JSON is the input they should read; they
  should cite its `target_id` and `sources[].ledger` references.

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
- **evaluator group**: ledgers are totalled together only if their recorded `executor_version` set is
  identical. The oracle configuration (alpha, null samples, near-miss rule) is **not recorded**, so
  `oracle_config` is `unknown` for everyone; old runs are never labelled with today's settings.
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

## Known limitations

1. The oracle configuration is not recorded (only `executor_version`, and per result the threshold and
   alpha actually applied).
2. A lean summary does not store the proposal's spec or the completed subset.
3. Why an unfinished job stopped is recorded only in `report.json` (when present); invalid proposals
   never reach a ledger.
4. Hypotheses with no attempts cannot be tied to a target; they are counted per ledger
   (`hypotheses_without_attempts`).
5. No cross-job or cross-run deduplication, so totals may overlap.

## Sample

`docs/coverage_sample/` holds output generated from the reproducible fixture in
`tests/test_coverage.py` (`make_runs`: three small synthetic ledgers in two runs, one lean sweep, one
job with a `report.json` and `state.json`). Timestamps in it are from when it was generated.

## Follow-ups (not done here; for items 2-4 of the plan)

- **Evaluator identity in execution:** record the oracle configuration (and `lpswarm` version) once per
  ledger or per run, so groups can be told apart instead of `unknown`.
- **Lean sweeps:** store the proposal's spec JSON and, for stopped sweeps, a checkpoint of the
  completed range, so "requested" versus "completed" is evidence, not `unknown`; and remember a compact
  set of output hashes so repeated coverage of the same ciphers is skipped and counted once.
- **Stop reasons:** write the stop reason (max attempts, timeout, stop file, budget) into the ledger
  per hypothesis, so it no longer depends on `report.json`.
- **Capability matrix / versioned briefs:** the coverage JSON is the input they should read; they
  should cite its `target_id` and `sources[].ledger` references.

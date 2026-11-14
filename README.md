# lpswarm: models propose, code disposes

A multi-model research harness in which language models propose candidate solutions as small JSON
programs, and deterministic, statistically calibrated code decides whether any of them worked. It was
built against a hard, real target: the unsolved pages of the Cicada 3301 *Liber Primus*.

**Status, plainly:** the harness recovers every solved section of the book that its program language
can express, and it has not decrypted any unsolved section. Negative results are recorded as results.

## What it demonstrates

- **Delegation across a hard trust boundary.** Models (Claude Code and Codex through their CLIs, DeepSeek or
  any OpenAI-compatible API, local models through Ollama) only emit proposals in a validated declarative
  language. They never write code, and they never see scores, thresholds or decrypted text: each model gets
  only a coarse verdict (`fail` / `near_miss` / `pass`) for its own proposals.
- **A null-calibrated oracle.** Thresholds come from null distributions at a stated false-positive rate.
  Every attempt on a target is counted: a running `alpha / i` level triages during a search, and a final
  Bonferroni check over every recorded attempt makes the binding decision.
- **A multi-model router.** Roles (proposer, triage, weighting, supervisor), per-model USD caps and
  usage-window pacing, a random-program control arm, and a tier test that compares model arms with brute
  force and random proposals on held-out synthetic targets.
- **A ledger of everything.** SQLite, deduplicated on what was tried, so nothing runs twice and failed
  hypotheses are kept and queryable.
- **Validation before use.** Recall and false-positive rate per cipher family and text length, a null
  false-positive check, and a test suite (`pytest`).

## Beyond ciphers

The pattern is general: a model proposes, a deterministic evaluator scores, a null distribution says what
chance looks like, and every attempt is counted against the error rate. Any problem with those three parts
fits: program synthesis against tests, formula discovery against data with a held-out null, heuristic or
configuration search, or a model proposing statistical tests whose p-values code computes under
multiple-comparison control.

What carries over unchanged and what is cipher-specific:

| Generic | Cipher-specific (replace to port) |
| --- | --- |
| `router/` (adapters, roles, budgets, pacing) | `programs/` (the cipher-program language) |
| `ledger/` (hypotheses, attempts, results, budget events) | `ciphers/`, `baseline/` (cipher families, brute force) |
| `executor/` (enumerate, dedupe, budgets, stop file) | `oracle/` scoring (n-gram language model; the calibration and multiple-comparison logic around it is generic) |
| `swarm/` loop, generators, coarse-verdict feedback | `textgen/` (synthetic plaintext and ciphertext) |
| multiple-comparison bookkeeping, `validation/` harness shape | `alphabet.py` |

To port it, replace the proposal language, the scorer and the null sampler; the rest stays.

## Architecture

| Piece | What it does | Where |
| --- | --- | --- |
| Alphabets | Any symbol set (tokens, glyphs, aliases); nothing about the real rune table is hard-coded | `src/lpswarm/alphabet.py` |
| Cipher families | Caesar, Vigenere / Beaufort / variant Beaufort, autokey, running key, simple substitution, columnar transposition. Each declares its parameter and key space | `src/lpswarm/ciphers/` |
| Synthetic data | Seeded plaintext/ciphertext pairs by family, length, key difficulty, language; held-out split | `src/lpswarm/textgen/` |
| Oracle | IC, n-gram log-likelihood, dictionary coverage, LM slot; thresholds from null distributions at a stated false-positive rate, tightened for multiple comparisons; full and coarse (verdict-only) APIs | `src/lpswarm/oracle/` |
| Ledger | SQLite store of hypotheses, key candidates, attempts, results, corpus items, budget events, deduplicated | `src/lpswarm/ledger/` |
| Executor | Enumerates params x keys, skips anything already in the ledger, scores, records; budgets + kill switch | `src/lpswarm/executor/` |
| Validation | Recall and false-positive rate per family and length, plus a null-calibration check | `src/lpswarm/validation/` |
| Baseline | Non-LLM brute force over every family with word-list keys | `src/lpswarm/baseline/` |
| Program language | Declarative JSON ciphers (key streams, combiners, maps, skips, transpositions) that models write and code interprets | `src/lpswarm/programs/` |
| Router | Model adapters, roles, USD caps, usage-window pacing | `src/lpswarm/router/`, `config/models.example.toml` |
| Swarm | Generators (LLM, random control, ranker), rounds, briefs, coarse feedback | `src/lpswarm/swarm/` |
| Overnight runner | Lanes of swarm and baseline jobs with budgets, resumable | `src/lpswarm/overnight.py`, `config/overnight.example.toml` |

Network code (HTTP imports) exists only in `src/lpswarm/router/adapters.py`, enforced by a test; the
CLI adapters run the Claude Code and Codex command-line tools as subprocesses. API keys come from environment variables named in the config and are never stored. The only
other networked file is the optional dev script `scripts/fetch_corpus.py`.

## Install

Windows, everything at once (venv, Ollama, GPU-pinned models, config, checks):
`powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1`. See the quick start in
`docs/phase3_runbook.md`. `lpswarm doctor` checks an existing setup.

Manual install. Python 3.11+. Windows (PowerShell):

```powershell
cd <this repo>
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

Linux/macOS: same, with `python3 -m venv .venv` and `source .venv/bin/activate`.

If your console shows `?` or errors on rune glyphs, run `chcp 65001` or set
`$env:PYTHONIOENCODING = "utf-8"` first.

## Usage

Every command also works as `python -m lpswarm <command>`.

```powershell
pytest                                   # all tests (~10 s)
lpswarm validate                         # full validation run (~1 min), writes reports/
lpswarm validate --quick                 # small smoke run (~5 s)
lpswarm null-check --lengths 20,40,100   # oracle false-positive rate on fresh nulls
```

Brute-force baseline on a synthetic demo target, then on your own ciphertext:

```powershell
lpswarm baseline --demo vigenere:120 --ledger demo.sqlite
lpswarm baseline --ciphertext data/page.txt --alphabet data/alphabet.json --ledger lp.sqlite `
                 --wordlist data/words.txt --running-key-texts data/keytexts
lpswarm leads --ledger lp.sqlite --near-miss     # human queue
lpswarm ruled-out --ledger lp.sqlite             # negative results
lpswarm encode data/page.txt --alphabet data/alphabet.json   # check how a file is read
```

Re-running the same baseline adds no rows: attempts are deduplicated on
`sha256(target, family, params, key)`.

Stop a long run by creating a file named `STOP` in the working directory
(`New-Item STOP` in PowerShell); delete it to run again. `--max-attempts` and `--timeout` set
per-family budgets.

### Liber Primus data

`data/lp/` holds the 28 sections of the scream314/cicada3301 transcription (one file per
section as that source lists them; multi-page sections have no page breaks inside), with
`manifest.json` (labels, the source's own cipher notes, quality flags) and `SOURCES.md`
(provenance, licence caveat). `data/alphabet/gematria_primus.json` is the Gematria Primus table
(order, letters, prime values), checked against the cleartext section. Re-import with
`python scripts/import_lp_scream314.py <path to a clone of scream314/cicada3301>`.

```powershell
lpswarm baseline --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json `
                 --ledger lp.sqlite                    # every section (~6 min)
lpswarm baseline --manifest data/lp/manifest.json --alphabet data/alphabet/gematria_primus.json `
                 --ledger lp.sqlite --sections 10,22   # just some sections
```

Each section is its own target, so alpha is per section. Ciphertext is read by rune glyphs
only; Latin notes, numbers and hex inside a section are ignored. Sections over 500 runes are
scored on the first 500 decrypted runes (`max_score_length`). Results of the reference run:
`docs/lp_baseline_run.md`.

### Options and config

`--alphabet` takes `latin26` (default), `rune_likeNN` (a synthetic N-symbol rune-style alphabet,
N ≥ 26, whose extra symbols are the commonest corpus digraphs), or a path to an alphabet JSON (see
`data/alphabet/gematria_primus.json` for the format). `--alpha` sets the per-attempt false-positive rate.

Extra training text goes in `data/corpora/english/*.txt` (or under `$LPSWARM_DATA` if set).
Files that overlap the held-out validation book are refused with a warning. Text files may be
UTF-8 with or without a BOM, or UTF-16; anything else gets a clear error.

A TOML file passed with `--config` can set any field of `OracleConfig`
(`src/lpswarm/oracle/oracle.py`), `ValidationConfig` (`src/lpswarm/validation/harness.py`) and
`BaselineConfig` (`src/lpswarm/baseline/bruteforce.py`):

```toml
[oracle]
alpha = 0.005
order = 4
null_samples = 3000

[validation]
lengths = [30, 60, 120]
cases_per_cell = 10
```

## How the oracle decides

For a candidate of length L:

1. **Screen:** bigram log-likelihood must beat the median of the null samples. Most wrong keys
   stop here.
2. **Full score:** `combined = 4-gram log-likelihood per symbol + 1.0 × dictionary coverage`, best
   over configured languages. IC and the optional LM log-likelihood are recorded as evidence but
   do not affect the decision in Phase 1.
3. **Threshold:** for each null type (shuffled good text, uniform random symbols, wrong-key
   decryptions of good text under each family), the upper `alpha_eff` quantile of `combined` at
   exactly length L; the threshold is the max over types. When `alpha_eff` is below what the null
   sample can resolve, the tail is extrapolated with an exponential fit to the top 10% of samples.
   Wrong-key samples that are really near-solutions (equivalent keys such as identity column
   orders of different widths, keyword alphabets sharing their tail; ≥ 50% 4-gram overlap with
   the true plaintext) are redrawn: they are not noise.
4. **In-run verdict (triage):** attempt *i* on a target is scored at `alpha_eff = alpha / i`.
   `pass` if combined ≥ that threshold, `near_miss` if it only beats the unadjusted one, else
   `fail`. The ledger stores every signal, the null percentile, the threshold and
   `attempt_count_at_scoring`.
5. **Final check (the binding decision):** after a search, every in-run pass / near miss is
   re-scored at `alpha / N_total`, where N_total is every attempt recorded on that target
   (Bonferroni over the whole search). This does not depend on the order attempts ran in, and it
   keeps the chance of *any* false pass on a target at or below alpha. Thresholds only rise with N,
   so nothing outside the re-scored set could pass. `lpswarm leads` marks survivors `FINAL`.

   The running `alpha / i` level on its own would not control the error rate (expected false
   passes grow like alpha · ln N). `multiple_comparisons = "spending"` switches the in-run level to
   `alpha / (i(i+1))`, which sums to less than alpha and so is valid by itself, at the cost of
   penalising whatever runs last. If a threshold exceeds the best score any text could reach, the
   result is flagged `unreachable` and the baseline prints a warning: the ciphertext is too short
   for that many attempts.

Generators (Phase 3) only get `CoarseOracle.judge()`, which returns the verdict string and nothing
else. Held-out synthetic data is only reachable from `lpswarm.validation` and the tests.

## Validation baseline

`lpswarm validate` writes `reports/validation.md` (+ CSV/JSON). A copy of the reference run is in
`docs/baseline_validation.md`. Each case hides the true key among decoys and counts:

- **recall:** an attempt that survives the final check reproduces the true plaintext
  (≥ 90 % similarity); *in-run recall* uses the triage verdict instead;
- **FPR:** final passes unrelated to the truth (< 50 % similarity) / all wrong attempts;
- **partial:** final passes at 50–90 % similarity, i.e. near-solutions such as a columnar key
  with two columns swapped. Reported, not counted as false positives.

Reference result (seed 0, 5 cases per cell, ~40 s): recall 1.0 for every family at lengths
40–200; at length 20 recall falls to 0.6–1.0 (running key: 0.0 final, 0.6 in-run) because the
threshold for ~10k attempts approaches the score of real English. One false pass in 160k
attempts over 150 targets, consistent with the per-target alpha = 0.01. Null FPR at the
configured alpha sits between 0.4% and 1.5% across lengths, within the stated tolerance.

## Known limitations

- **Short texts are the hard case.** At length ~20 the n-gram statistics barely separate English
  from noise once the threshold is adjusted for thousands of attempts; recall drops there first.
- **Bonferroni is conservative.** Over millions of attempts it raises the bar a lot. It controls
  the chance of *any* false pass per target, not the false discovery rate. Across many targets
  (e.g. one per LP page) the per-target guarantee does not add up to a global one; set a smaller
  alpha if you search many pages.
- **The final check counts attempts, not distinct decryptions.** Equivalent keys (e.g. periodic
  Vigenère repeats) are separate attempts, which makes it slightly more conservative.
- **Tail extrapolation is a model.** Thresholds below 1/null_samples rely on the exponential tail
  fit; the null check only verifies the empirical part (attempt_count = 1).
- **Calibration is per exact length and in memory.** First scoring at a new length costs about a
  second; nothing is cached on disk.
- **Wrong-key nulls cover only the configured families**, using medium-difficulty keys. A cipher
  family not in that list may have an unrepresented null.
- **Large alphabets lower the n-gram order** automatically (N^order ≤ 20M table entries), with a
  warning; a 29-symbol alphabet keeps order 4.
- **Substitution is only searched through keyword-mixed alphabets.** There is no hill-climbing
  solver for random substitution keys.
- **Running key needs supplied texts**; there is no built-in key-text library yet (Phase 2).
- **English only by default**; other languages need corpora (`data/corpora/<language>/*.txt`).
- **Word breaks are optional.** With breaks (default for transcription targets; `--word-breaks`
  for validation/tier tests) the oracle adds a calibrated word score: the share of symbols in
  dictionary words under the given segmentation. It assumes separators sit at plaintext word
  boundaries (true for every solved section); for transposition hypotheses that assumption may
  not hold. Short-text recall with breaks (8 cases per cell, length 20): Vigenere 0.50 -> 0.88,
  running key 0.25 -> 0.75, substitution 0.75 -> 1.00, columnar 0.62 -> 0.88, null FPR unchanged.
  On the real solved sections every pass margin grows and the 38-rune section 09/2 now passes.
- **The held-out guard prevents accidents; it is not a security boundary.**
- **Skip-literal ambiguity is resolved by search, at a cost.** `skip_mode: "resolve"` lets a
  Viterbi search decide, per occurrence, whether a skip symbol is a literal or an encrypted
  symbol (bigram language model). Because that search optimises for English, those attempts are
  judged against nulls decrypted by the same search (null variant `skipdp:<symbols>`, about 20 s
  to calibrate per target and skip set). Not available with autokey streams.
- **Tier-test budgets are per arm, not per dollar.** Compare recall with the attempts, calls
  and USD columns; `random_program:N` gives attempt-matched controls.
- **Single process.** No multiprocessing, so a big brute force is bounded by one core
  (roughly 10–25k attempts/s on a desktop).

## Phase 3: model tier test

Models propose; code disposes. Generators (LLMs or a random control) propose ciphers in a small
JSON **cipher-program language** (`src/lpswarm/programs/`): key streams (constant, repeating key,
autokey, number sequences such as primes, prime totients, Fibonacci, digits of pi/e),
`sub`/`add`/`beaufort` combination, reversed alphabet map, skip-literal symbols that do not
advance the stream, reversed text and columnar transposition. Code validates and interprets the
programs; the Phase 1 oracle and ledger judge and record them. Models never write code, and they
only see coarse verdicts (`fail`/`near_miss`/`pass`) for their own proposals: no scores,
thresholds or decrypted text.

| Piece | Where |
| --- | --- |
| Cipher-program language, sequences, sampler | `src/lpswarm/programs/` |
| Router + adapters (Ollama, OpenAI-compatible/DeepSeek, Claude Code and Codex on your plan, command, scripted), USD caps, usage-window pacing | `src/lpswarm/router/` |
| Generators (LLM, random control, ranker) and the swarm loop | `src/lpswarm/swarm/` |
| Tier test (baseline vs random vs models on held-out program ciphers) | `src/lpswarm/validation/tiertest.py` |

```powershell
lpswarm swarm --demo program:120 --generators random_program --rounds 3      # no models needed
lpswarm tiertest --arms baseline,random_program:40,random_program:2000 --quick
lpswarm tiertest --models config\models.toml --arms baseline,random_program:40,qwen-local,deepseek
```

Model setup, dry runs and the full experiment: `docs/phase3_runbook.md`. Network access exists
only in `src/lpswarm/router/adapters.py` (enforced by a test); API keys come from environment
variables named in the config and are never stored.

The language expresses the mechanisms of the three solved sections the Phase 1 baseline
missed. With `skip_mode: "resolve"` and the source's keys, 03-04 ("WELCOME WELCOME PILGRIM TO
THE GREAT JOURNEY...") and 14-15 ("A KOAN DURING A LESSON THE MASTER EXPLAINED...") decode end
to end and pass the final check at a 50,000-attempt budget against nulls from the same search
(null FPR 0.0-0.3% at alpha = 1%). 73 still fails, because of transcription corruption.

## Roadmap

2. Corpus census: sourced list of everything Cicada 3301 referenced, with confidence tags,
   editions and expansion rings, and rule-based key-candidate generation.
3. Model tier test (built; run it with your models, see `docs/phase3_runbook.md`).
4. Scale up only if Phase 3 wins.

## Licence

GNU General Public License v3.0 (`LICENSE`). The bundled English texts in `src/lpswarm/fixtures/` are
public-domain books (see `fixtures/SOURCES.md`); the Liber Primus transcription in `data/lp/` is
third-party material with its own provenance notes (`data/lp/SOURCES.md`).

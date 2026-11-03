# lpswarm: Liber Primus research harness (Phase 1)

A test bench for attacking unsolved sections of the Cicada 3301 *Liber Primus*. Hobby /
portfolio proof of concept: a well-documented negative result counts as success.

**Models propose; code disposes.** Every decision about whether a decryption worked is made by
deterministic, null-calibrated code. Phase 1 has no LLM calls at all. It builds the pieces any
later model-driven search is measured against:

| Piece | What it does | Where |
| --- | --- | --- |
| Alphabets | Any symbol set (tokens, glyphs, aliases); nothing about the real rune table is hard-coded | `src/lpswarm/alphabet.py` |
| Cipher families | Caesar, Vigenère / Beaufort / variant Beaufort, autokey, running key, simple substitution, columnar transposition. Each declares its parameter and key space | `src/lpswarm/ciphers/` |
| Synthetic data | Seeded plaintext/ciphertext pairs by family, length, key difficulty, language; held-out split | `src/lpswarm/textgen/` |
| Oracle | IC, n-gram log-likelihood, dictionary coverage, LM slot; thresholds from null distributions at a stated false-positive rate, tightened for multiple comparisons; full and coarse (verdict-only) APIs | `src/lpswarm/oracle/` |
| Ledger | SQLite store of hypotheses, key candidates, attempts, results, corpus items, budget events, deduplicated | `src/lpswarm/ledger/` |
| Executor | Enumerates params × keys, skips anything already in the ledger, scores, records; budgets + kill switch | `src/lpswarm/executor/` |
| Validation | Recall and false-positive rate per family and length, plus a null-calibration check | `src/lpswarm/validation/` |
| Baseline | Non-LLM brute force over every family with word-list keys | `src/lpswarm/baseline/` |
| Router | Interface stub only (Phase 3) | `src/lpswarm/router/`, `config/models.example.toml` |

Nothing in `src/` touches the network or reads credentials. The only networked file is the
optional dev script `scripts/fetch_corpus.py`, which refreshes the bundled corpus.

## Install

Python 3.11+. Windows (PowerShell):

```powershell
cd liberprimus-search
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

### Options and config

`--alphabet` takes `latin26` (default), `rune_likeNN` (a synthetic N-symbol rune-style alphabet,
N ≥ 26, whose extra symbols are the commonest corpus digraphs), or a path to an alphabet JSON (see
`TODO_USER.md`). `--alpha` sets the per-attempt false-positive rate.

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
   exactly length L; the threshold is the max over types. `alpha_eff = alpha / n`, where n is the
   number of attempts recorded against this target, counting this one (Bonferroni). When
   `alpha_eff` is below what the null sample can resolve, the tail is extrapolated with an
   exponential fit to the top 10% of samples.
4. **Verdict:** `pass` if combined ≥ adjusted threshold, `near_miss` if it only beats the
   unadjusted one, else `fail`. The ledger stores every signal, the null percentile, the threshold
   and `attempt_count_at_scoring`.

Generators (Phase 3) only get `CoarseOracle.judge()`, which returns the verdict string and nothing
else. Held-out synthetic data is only reachable from `lpswarm.validation` and the tests.

## Validation baseline

`lpswarm validate` writes `reports/validation.md` (+ CSV/JSON). A copy of the reference run is in
`docs/baseline_validation.md`. Each case hides the true key among decoys and counts:

- **recall:** a passing attempt reproduces the true plaintext (≥ 90 % similarity);
- **FPR:** passing attempts unrelated to the truth (< 50 % similarity) / all wrong attempts;
- **partial:** passing attempts at 50–90 % similarity, i.e. near-solutions such as a columnar key
  with two columns swapped. Reported, not counted as false positives.

## Known limitations

- **Short texts are the hard case.** At length ~20 the n-gram statistics barely separate English
  from noise once the threshold is adjusted for thousands of attempts; recall drops there first.
- **Bonferroni is conservative.** Over millions of attempts it raises the bar a lot. It controls
  the chance of *any* false pass per target, not the false discovery rate.
- **Tail extrapolation is a model.** Thresholds below 1/null_samples rely on the exponential tail
  fit; the null check only verifies the empirical part (attempt_count = 1).
- **Calibration is per exact length and in memory.** First scoring at a new length costs about a
  second; nothing is cached on disk.
- **Wrong-key nulls cover only the configured families**, using medium-difficulty keys. A cipher
  family not in that list may have an unrepresented null.
- **Substitution is only searched through keyword-mixed alphabets.** There is no hill-climbing
  solver for random substitution keys.
- **Running key needs supplied texts**; there is no built-in key-text library yet (Phase 2).
- **English only by default**; other languages need corpora (see `TODO_USER.md`).
- **Word breaks are ignored.** Dictionary coverage segments unspaced text.
- **The held-out guard prevents accidents; it is not a security boundary.**
- **Single process.** No multiprocessing, so a big brute force is bounded by one core
  (roughly 10–25k attempts/s on a desktop).

## Roadmap

2. Corpus census: sourced list of everything Cicada 3301 referenced, with confidence tags,
   editions and expansion rings, and rule-based key-candidate generation.
3. Model tier test: model-driven hypothesis generators behind the router (DeepSeek via API; local
   Qwen/Gemma; Granite tiny for weighting), measured against this Phase 1 baseline.
4. Scale up only if Phase 3 wins.

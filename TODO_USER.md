# TODO for the user

Things only you can supply or decide. Each has a default so work can continue.

## Data you need to supply

- [ ] **Liber Primus ciphertext.** Put page transcriptions in `data/` as UTF-8 text files, one
      file per section/page range. Runes or a transliteration both work as long as the alphabet
      file (next item) covers the characters. Check how a file is read with
      `lpswarm encode data/<file>.txt --alphabet data/alphabet.json`.
- [ ] **Alphabet / rune table.** Nothing about the Gematria Primus is hard-coded. Write
      `data/alphabet.json`:
      ```json
      {"name": "my_runes",
       "tokens": ["F", "U", "TH", "..."],
       "glyphs": ["ᚠ", "ᚢ", "ᚦ", "..."],
       "aliases": {"V": "U"}}
      ```
      `tokens` = plaintext spelling (used to transliterate the English corpus so the n-gram model
      matches the alphabet), `glyphs` = ciphertext symbols, `aliases` = extra spellings that map to
      a token. Order defines the integer value of each symbol (0..N-1); if you believe a different
      numbering matters (e.g. for shift ciphers), that is your call and goes in this file.
- [ ] **Language corpora beyond English.** Defaults: English only, from 4 bundled public-domain
      books (see `src/lpswarm/fixtures/SOURCES.md`). Extra English text goes in
      `data/corpora/english/*.txt` and is added to training automatically. Other languages
      (e.g. Latin, Old English) need a new entry in `LANGUAGES` in
      `src/lpswarm/textgen/corpus.py` plus corpus files; then add them to `OracleConfig.languages`.
- [ ] **Word lists.** Default: the 5000 most frequent words of the training corpus. Supply your own
      with `lpswarm baseline --wordlist path.txt` (one word per line, `#` comments allowed).
- [ ] **Running-key texts.** The baseline skips running key unless you pass
      `--running-key-texts <files or folders>`. Phase 2 (corpus census) is meant to produce these.

## Decisions (defaults in brackets)

- [ ] **Hosted models in Phase 3.** The original spec said "no hosted model APIs". You decided
      DeepSeek goes through its API and everything else is local (Qwen or Gemma as proposers,
      Granite tiny for weighting/triage). Recorded in `config/models.example.toml`; key read from
      `DEEPSEEK_API_KEY` at call time only. Confirm exact model tags and a USD cap.
- [ ] **False-positive rate.** [alpha = 0.01 per attempt, Bonferroni over attempts per target.]
      For a real search over millions of keys you may prefer controlling the false discovery
      rate instead; that would be a new `multiple_comparisons` mode.
- [ ] **Calibration tolerance.** [3 binomial standard errors over test + calibration samples.]
- [ ] **Word breaks.** [Ignored: ciphertexts are scored as unbroken symbol streams and dictionary
      coverage uses segmentation.] If you want word-separator positions from the real pages used
      as a signal, that is a Phase 2 feature.
- [ ] **Validation key spaces.** [True key hidden among 500 word-derived decoys; columnar widths
      2-6; 2000 running-key offsets.] Bigger spaces lower recall at short lengths because the
      Bonferroni threshold rises; that trade-off is the point of the baseline.

## Missing / not done

- Project Gutenberg itself was blocked from the build container; fixtures came from the GITenberg
  GitHub mirror via `scripts/fetch_corpus.py`. Re-run that script to refresh them.

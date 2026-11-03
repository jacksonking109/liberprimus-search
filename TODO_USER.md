# TODO for the user

Things only you can supply or decide. Each has a default so work can continue.

## Data you need to supply

- [x] **Liber Primus ciphertext.** Imported from `github.com/scream314/cicada3301` into
      `data/lp/` (see `data/lp/SOURCES.md`). Open points:
  - [ ] That repo has **no licence file**. Fine for personal research; check before making this
        repo public or redistributing `data/lp/`.
  - [ ] The source groups text into **sections**, not pages; multi-page sections have no page
        breaks. If you want strictly per-page targets, a source with page breaks is needed
        (maybe `github.com/cijhho123/cicada3301`; not reviewed).
  - [ ] Two sections are flagged: `56.jpg/2` and `56.jpg - 73.jpg` contain corrupted characters
        (U+FFFD), and the latter has rune U+16C2 (ᛂ), which is not in the Gematria table. Both are
        dropped, which can misalign everything after them. Correct them from the page images if
        you can.
- [x] **Alphabet / rune table.** `data/alphabet/gematria_primus.json`, from the table image in the
      same repo; checked against the cleartext section 05. Open point:
  - [ ] Q and V are not in the table, so English training text drops them. Solvers often map
        V→U and Q→C(W); add `"V": "U"` etc. to `aliases` if you agree.
- [ ] **Other alphabets (optional).** Nothing about the Gematria Primus is hard-coded in the
      code. To try a different table or ordering, write another JSON like:
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
- [ ] **False-positive rate.** [alpha = 0.01 per target: the final check is Bonferroni over
      every attempt on the target.] If you search many pages, the chance of a false pass
      *somewhere* grows with the number of pages; lower alpha (e.g. 0.01 / number of pages) or
      add a false-discovery-rate mode.
- [ ] **Calibration tolerance.** [3 binomial standard errors over test + calibration samples.]
- [x] **Word breaks.** Used by default for transcription targets (`--no-word-breaks` turns them
      off). Separators: the rune word dot and whitespace, including line ends (checked on the
      solved sections: joining across a line end never forms a dictionary word).
- [ ] **Validation key spaces.** [True key hidden among 500 word-derived decoys; columnar widths
      2-6; 2000 running-key offsets.] Bigger spaces lower recall at short lengths because the
      Bonferroni threshold rises; that trade-off is the point of the baseline.

## Missing / not done

- Project Gutenberg itself was blocked from the build container; fixtures came from the GITenberg
  GitHub mirror via `scripts/fetch_corpus.py`. Re-run that script to refresh them.

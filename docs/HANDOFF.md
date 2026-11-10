# Handoff: state of the work and how to continue it on another machine

Branch `claude/eager-pasteur-l0dsma` of `jacksonking109/liberprimus-search`. Written 2026-11-10 for a fresh Claude Code or Codex session.

## Standing rules
Models propose, code disposes: every claim is tested by deterministic code with a calibrated null. No live model calls, paid runs or packet runs without the
owner's go-ahead. Keys only through environment variables (`api_key_env`); never commit `config/models.toml` or a key. Do not invent facts about the puzzle
(mark guesses "(guess)"); do not compare new answers against known goods. Page images are never committed (`data/lp_images/` is git-ignored; SHA-256 sums are
in `data/lp_images.sha256`).

## Read first (in this order)
1. `docs/avenues_explored.md`: every avenue tried and what came out (sections 1-15).
2. `docs/community_state.md`: what the solving forum says (second-hand) and how it checks against our data; open questions for the forum.
3. `docs/plan_repeat_shortage.md`: the plan (Phases 0-1 done, Phase 2 partial, Phase 3 not run).
4. `config/briefs/lp2_signature.md`: the measured facts of the unsolved sections in 1,750 characters (give this to any model you consult).
5. `docs/research_tools.md`: every tool and its reference output (`docs/diagnostics_sample/`).

## The one anomaly
Adjacent equal runes occur at 0.19 of chance (86 against about 440), only at lag 1; flat letter frequencies and flat differences (IC x 29 = 1.00 and 1.03). The same in the
page images and the text, uniform across runes, pages and sections, not tied to position, phase, neighbours or alphabet class. No cipher in the program language
reproduces it (58,024 screened). A keyed multiplicative running sum can, but not with EA as the trigger (position test). Self-keyed prime readings, page-05-grid
keys, dot overlays and Orion fits: negative. Page 49 (community "page 32") carries designed numbers: 11x11 sums 563 / 569, 5x5 circumference 1136.

## Set up
```
git clone https://github.com/jacksonking109/liberprimus-search.git && cd liberprimus-search
git checkout claude/eager-pasteur-l0dsma
python -m venv .venv && .venv/Scripts/activate        # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -e ".[dev,images]"
python -m pytest -q                                   # about 5-10 minutes, expect 0 failures
python -m lpswarm.pageimages fetch                    # only if you need the images (partial clone of iBotPeaches/cicada_3301)
```
Most analyses need only committed data: `data/lp/` (manifest and sections), `data/lp_derived/lp2_runes.csv` (our image reading of pages 17-72), `data/alphabet/`.

## Reproduce the main results (no model, no keys)
```
python -m lpswarm.research_signature --out reports/diag     # which cipher families can reproduce the repeat signature (about 4 min)
python -m lpswarm.research_leak --out reports/diag          # where the 86 doubles sit (random thinning)
python -m lpswarm.research_doubles all --out reports/diag --cache units.json   # needs the images the first time (3 min), then the cache
python -m lpswarm.research_muldiff --out reports/diag       # multiplicatively keyed running sums
python -m lpswarm.research_literal --out reports/diag       # literal readings of "their numbers are the direction"
python -m lpswarm.reader_audit --out reports/diag           # audit of the image reader (needs images)
```
`reports/` is git-ignored; reference outputs are committed in `docs/diagnostics_sample/`.

## Not in git (regenerate if needed)
Page images (fetch above); OutGuess payloads (Debian `outguess` 0.4, default key: `outguess -r page.jpg out.bin`; nine pages carry real payloads, none of pages 17-72);
`read.pkl`-style caches; `reports/`.

## Idle on purpose
Codex and DeepSeek lanes (`config/overnight.example.toml`, a commented `codex-signature` lane), `--facts-file config/briefs/lp2_signature.md`, and `--signature-gate`
(refuses programs that cannot reproduce the signature; currently refuses every family in the program language, so a lane needs a new construction in the language
first). DeepSeek needs `DEEPSEEK_API_KEY` set locally and prices in `config/models.toml`.

## Suggested use of a second model (bridge)
Give it `config/briefs/lp2_signature.md` and `docs/community_state.md`; ask only for constructions whose output has the signature (flat symbols and steps, repeats
about five times rarer than chance, nothing at lags 2-8), each as a spec that can be enciphered on English and screened (`research_signature.screen_full` and
`classify`). Treat anything it says about puzzle history as unverified. Limit the exchange and the spend.

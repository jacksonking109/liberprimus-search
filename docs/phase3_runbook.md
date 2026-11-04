# Phase 3 runbook (Windows, at home)

The model tier test asks one question: do model-driven generators find ciphers better
than (a) the Phase 1 brute force and (b) random programs from the same cipher language, at
comparable cost? Everything below runs from the repo root in PowerShell, with the venv active.

## Quick start (one command)

In PowerShell (needs git and Python 3.11+; the script installs Ollama with winget if it is missing):

```powershell
git clone -b claude/eager-pasteur-l0dsma https://github.com/jacksonking109/liberprimus-search
cd liberprimus-search
powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1
```

What it does, step by step (each line prints OK / WARN / FAIL; safe to re-run):
1. Finds Python 3.11+, creates `.venv`, installs lpswarm.
2. Installs Ollama if missing, finds your GPUs with `nvidia-smi`, and starts one Ollama server per
   GPU: the biggest card (5060 Ti) on port 11434 for the proposer models, the smallest (2060) on
   11435 for the ranker. Each server only sees its own GPU.
3. Pulls models: the first of `qwen3:14b`, `qwen3:8b` that pulls, plus `gemma3:12b` for the big
   card, and the first of `granite4:tiny-h`, `granite3.3:2b` for the small one. Override with
   `-ProposerModels`, `-ExtraModels`, `-RankerModels`.
4. Writes `config\models.toml` with whatever actually pulled (an existing file is kept; use
   `-Force` to regenerate).
5. Runs the tests, `lpswarm doctor`, and an offline dry run, then prints the next commands.

After a reboot, only this is needed before a run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_ollama.ps1
.\.venv\Scripts\lpswarm.exe doctor
```

`-ExecutionPolicy Bypass` applies to that one PowerShell process only. Use
`.\.venv\Scripts\lpswarm.exe` (no venv activation needed), or activate with
`.\.venv\Scripts\Activate.ps1` if your execution policy allows scripts. Stop the servers with
`scripts\start_ollama.ps1 -Stop`. The Ollama tray app is closed while the pinned servers run;
starting it again takes over port 11434 with both GPUs.

The steps below are the manual equivalent.

## 0. Update and check

```powershell
git pull
pip install -e ".[dev]"
pytest
```

## 1. Models

```powershell
ollama pull qwen3:8b          # or whichever Qwen/Gemma tags you use
ollama pull gemma3:12b
ollama pull <granite tiny tag>
ollama list                   # copy the exact tags
Copy-Item config\models.example.toml config\models.toml
notepad config\models.toml    # set tags, DeepSeek model id and prices, max_usd
$env:DEEPSEEK_API_KEY = "..." # this session only; never put it in the file
```

`config/models.toml` holds no secrets, but keep it local if you'd rather not publish your setup.

## 2. Dry run (no network, no cost)

```powershell
lpswarm tiertest --models config\models.toml --arms dry --quick --out reports\dry
lpswarm swarm --demo program:120 --models config\models.toml --generators dry --rounds 2 --ledger reports\dry\swarm.sqlite
```

## 3. Smoke test each real model

```powershell
lpswarm tiertest --models config\models.toml --arms qwen-local --quick --out reports\smoke-qwen
lpswarm tiertest --models config\models.toml --arms deepseek --quick --max-usd 0.50 --out reports\smoke-deepseek
```

Look at `reports\smoke-*\tiertest_cases.csv`: `model_calls` > 0, and few invalid proposals
(`lpswarm swarm` prints `invalid=` per round). If a local model returns invalid JSON, try
`json_mode = true` or a bigger model.

## 4. The tier test

Same held-out cases for every arm; each arm gets its own ledger in `--out`.

```powershell
lpswarm tiertest --models config\models.toml `
  --arms baseline,random_program:2000,random_program:40,qwen-local,gemma-local,deepseek `
  --lengths 80,160 --cases 10 --rounds 5 --per-round 8 --max-usd 5 --out reports\tier1
```

- Reference numbers for the non-model arms: `docs/tiertest_reference.md` (baseline 30%,
  random_program:40 5%, random_program:2000 20% on 20 cases).
- Model calls are logged in `reports\model_spend.sqlite`, which is never deleted, so each
  model's `max_usd` is a cumulative cap across tier-test runs. Delete that file to reset it.
- `random_program:40` gets the same number of proposals as a model arm (5 rounds × 8) and is
  the fair control per proposal. `random_program:2000` is the control per unit of compute.
- Add `--ranker granite` to have Granite order each round's proposals.
- Read `reports\tier1\tiertest.md`. A model arm "wins" only if its recall clearly beats
  `random_program:40` (non-overlapping CIs, or the same result over several seeds via
  `--seed`) and is reasonable per dollar compared with `baseline` and `random_program:2000`.

## 4b. Claude Code and Codex on your subscription plans

The `claude_code` and `codex` providers run the official CLIs signed in with your own account,
so calls use your plan's included usage, not API billing:

- Only the unmodified CLI is run; lpswarm never reads or stores its login.
- Each call runs in a fresh empty temp folder. Claude Code runs with tools off, Codex in a
  read-only sandbox, so they answer as chat models and cannot touch the repo, ledger or oracle.
- `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `CODEX_API_KEY` are removed from the CLI's
  environment, so a key you have set for other tools never switches these calls to API billing.
- Anthropic's docs say subscription limits assume "ordinary, individual usage"; keep runs small.
  Codex: check OpenAI's current terms for automated `codex exec` use before enabling it.

Usage limits (the 5-hour windows):
- lpswarm counts its own calls per model in a rolling window (`window_hours`, default 5) and
  pauses when `max_calls_per_window` is reached, until the oldest call ages out.
- When the CLI replies that a usage limit was hit, lpswarm records the reset time (from the
  message, or a 30-minute cool-down if none is given) and pauses that model until then.
- While one model is paused, other generators keep working; if all are paused, the run waits
  (create `STOP` to end it). `wait_on_rate_limit = false` in a `[swarm]` config section stops instead.
- Both are stored in the ledger, so they carry over between runs. The real limit is shared with
  your other use of the plan (chat, IDE), which lpswarm cannot see.
- `lpswarm doctor` shows calls in the current window and any active pause per model.

```powershell
claude                 # sign in once (interactive), then exit
.\.venv\Scripts\lpswarm.exe doctor --ping   # one tiny real call per model
.\.venv\Scripts\lpswarm.exe tiertest --models config\models.toml --arms claude-opus,claude-sonnet --cases 3 --out reports\tier-claude
```

With 5 rounds per case, 3 cases at 2 lengths is about 30 calls: inside one 40-call window.

## 4c. Unattended runs

`scripts\overnight.ps1` runs the queue in `config\overnight.toml` with `lpswarm overnight`:
resumable, per-job logs and reports, `SUMMARY.md`, optional Claude Code supervisor (menu actions
only), results pushed to the `results` branch. See START_HERE.md section 7.

## 5. Real sections (optional, after the tier test)

```powershell
lpswarm swarm --manifest data\lp\manifest.json --alphabet data\alphabet\gematria_primus.json `
  --sections 10,22 --models config\models.toml --generators qwen-local,deepseek `
  --rounds 5 --per-round 8 --max-usd 2 --ledger lp.sqlite
lpswarm leads --ledger lp.sqlite --near-miss
```

Caveats:
- Models may have memorised published solutions of the solved sections, so solved sections
  say nothing about a model's skill. Only the synthetic tier test measures that.
- A `FINAL` lead on an unsolved section is a lead, not a solution: read it, and check whether
  the cipher program is simply overfitting a short section.
- Stop any run by creating a file named `STOP` in the working directory.

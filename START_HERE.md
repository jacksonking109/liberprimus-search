# Start here: first run at home (Windows)

Everything you need tonight, in order. Commands are for **PowerShell** on the desktop. Each
command is in its own block so it can be copied on its own.

Machine: RTX 5060 Ti 16 GB (Qwen3 / Gemma3, the "proposers") + RTX 2060 6 GB (Granite, the
"ranker"). Branch: `claude/eager-pasteur-l0dsma`.

---

## 1. Before you start

You need **git** and **Python 3.11 or newer** installed (python.org installer, tick
"Add python.exe to PATH"). Ollama is installed for you if it's missing.

Check:

```powershell
git --version
```

```powershell
py -3 --version
```

---

## 2. Get the code

```powershell
git clone -b claude/eager-pasteur-l0dsma https://github.com/jacksonking109/liberprimus-search
```

```powershell
cd liberprimus-search
```

Already cloned earlier? Update instead:

```powershell
git pull
```

---

## 3. One-command setup

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1
```

It prints `[OK]` / `[WARN]` / `[FAIL]` for each step and is safe to re-run. It:

1. finds Python, creates `.venv`, installs lpswarm;
2. installs Ollama with winget if missing (Windows may ask for permission);
3. detects both GPUs and starts two Ollama servers: 5060 Ti on port 11434, 2060 on port 11435;
4. downloads models (first run is a large download): `qwen3:14b` (or `qwen3:8b`),
   `gemma3:12b`, and `granite4:tiny-h` (or `granite3.3:2b`);
5. writes `config\models.toml` from what actually downloaded (adds Claude Code if `claude` is
   installed; Codex is added switched off);
6. runs the tests, `lpswarm doctor`, and an offline dry run, then prints next commands.

Useful options:

- Regenerate the config: add `-Force`
- Skip the tests (faster re-run): add `-SkipTests`
- Pick models yourself: `-ProposerModels "qwen3:8b" -ExtraModels "gemma3:12b" -RankerModels "granite3.3:2b"`
  (comma-separate several to try in order; `none` skips one, e.g. `-ExtraModels none`)

Notes:

- `-ExecutionPolicy Bypass` only applies to that one PowerShell window.
- You never need to "activate" the venv: always run `.\.venv\Scripts\lpswarm.exe ...`.

---

## 4. Sign in to Claude Code (once)

Only if you want Claude Code as a model. Install it first if it isn't installed (see Anthropic's
Claude Code install page), then run it once, sign in with your Claude account, and exit:

```powershell
claude
```

Codex: leave it off until you've read OpenAI's current terms on automated `codex exec` use with
a ChatGPT plan. To enable later: sign in with `codex login`, then uncomment the `[models.codex]`
block in `config\models.toml`.

---

## 5. Health check

```powershell
.\.venv\Scripts\lpswarm.exe doctor
```

Then one tiny real call per model (uses a sliver of your Claude plan, no cost for local models):

```powershell
.\.venv\Scripts\lpswarm.exe doctor --ping
```

Everything should be `[OK]`. A `[WARN]` about DeepSeek's key is fine if you're not using
DeepSeek yet.

---

## 6. Runs

Results go to the `--out` folder: open `tiertest.md` there. The numbers to beat are in
`docs\tiertest_reference.md` (brute force 30%, random 40 proposals 5%, random 2000 20%).

**A. Local models (free, the main experiment):**

```powershell
.\.venv\Scripts\lpswarm.exe tiertest --models config\models.toml --arms baseline,random_program:40,random_program:2000,qwen-local,gemma-local --ranker granite --lengths 80,160 --cases 10 --out reports\tier1
```

If a model name is missing from your config (for example gemma didn't download), drop it from
`--arms`. Drop `--ranker granite` if Granite didn't download.

**B. Claude Code on your plan (small first run, about 30 calls):**

```powershell
.\.venv\Scripts\lpswarm.exe tiertest --models config\models.toml --arms claude-opus,claude-sonnet --lengths 80,160 --cases 3 --out reports\tier-claude
```

It counts its own calls (250 per 5 hours shared by the Claude models, Opus proposer at most 60, by default) and pauses at that cap or when Claude
reports a usage limit, then carries on after the reset. No deadline, so let it wait.

**C. Real Liber Primus sections (after A looks sane):**

```powershell
.\.venv\Scripts\lpswarm.exe swarm --manifest data\lp\manifest.json --alphabet data\alphabet\gematria_primus.json --sections 10,22 --models config\models.toml --generators qwen-local --rounds 5 --per-round 8 --ledger lp.sqlite
```

```powershell
.\.venv\Scripts\lpswarm.exe leads --ledger lp.sqlite --near-miss
```

A `FINAL` lead is a lead, not a solution: read the decrypted text before getting excited.

**D. DeepSeek (optional, costs money):**

1. In `config\models.toml`, set `price_in_per_mtok` and `price_out_per_mtok` from DeepSeek's
   pricing page (while they're 0, spend is logged as $0 and the cap can't protect you), and the
   model id.
2. Set the key in that PowerShell window only (never put it in a file):

```powershell
$env:DEEPSEEK_API_KEY = "paste-your-key-here"
```

3. Check, then add `deepseek` to `--arms` with a small cap:

```powershell
.\.venv\Scripts\lpswarm.exe doctor --ping
```

```powershell
.\.venv\Scripts\lpswarm.exe tiertest --models config\models.toml --arms deepseek --cases 3 --max-usd 1 --out reports\tier-deepseek
```

---

## 7. Leaving it running (overnight / workday)

One command runs a queue of jobs unattended and writes `SUMMARY.md` as it goes:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\overnight.ps1
```

- The queue is `config\overnight.toml` (created by setup). Default: (1) tier test with Claude Code
  Opus + Sonnet; then the unsolved sections (20+ runes) in three lanes that run side by side,
  each starting on a different section: (2) **Sonnet**, with a brief Opus writes for each section
  from what's been tried there, (3) **Codex**, (4) **qwen/gemma** on the 5060 Ti; (5) DeepSeek,
  refused until it's set up. One sub-job per section. Edit the file to change jobs.
- **Side by side:** jobs on different backends run at the same time (up to `max_parallel = 2`):
  the Claude tier test and a Codex/local swarm run together, while two jobs on the same GPU or
  the same plan wait their turn. Inside a swarm round, Codex and the local models are also asked
  at the same time (qwen and gemma still take turns on the 5060 Ti). `-Serial` runs one job at a
  time.
- **Results:** `reports\overnight\<run>\SUMMARY.md` on the desktop, and on GitHub: branch
  **`results`** of this repo (open it in the GitHub app; only report `.md`/`.csv` files are
  pushed, never ledgers, logs or config). Uses your normal git login on the PC.
- **Supervisor:** `claude-supervisor` (Claude Code Opus, tools off) checks in every 60 min and after
  each job. It can only pick from a menu: write you a note, add a swarm job on chosen sections
  (max 5 per run, max 8 rounds), skip or retry a job, restart Ollama, or stop the run. Its notes
  appear in SUMMARY.md. When it adds a job it can **delegate** to a cheaper model (e.g.
  `claude-sonnet`) with a written brief: what to try on those sections, based on the per-section
  results so far. The brief goes into every generator's prompt for that job and is copied into
  SUMMARY's supervisor notes, so you can see what Opus told Sonnet.
- **Usage limits:** Opus, Sonnet and the supervisor share one Claude quota (250 calls / 5 h by
  default, `max_calls_per_window`), with per-model shares (`model_max_calls_per_window`): Opus
  60, supervisor 100 (check-ins and briefs), Sonnet the rest. Codex has its own (90 / 5 h). At a cap or a usage-limit message the affected models
  pause until the reset and the run keeps going with whatever else it can do. The message says
  which kind it is: `local cap 120/120` is lpswarm's own counter (raise `max_calls_per_window`
  in `config\models.toml` and restart; it takes effect at once), while `usage limit reported by
  the CLI` is the real plan limit.
- **Money:** DeepSeek jobs are refused unless its prices are filled in (so `max_usd` can protect
  you) and `DEEPSEEK_API_KEY` is set. Set the key in the same PowerShell window first, or as a
  user environment variable:

```powershell
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "paste-your-key-here", "User")
```

  (Open a new PowerShell window afterwards so it is picked up.)
- **Crashes and reboots:** a failing job doesn't stop the queue. If the PC restarts, run the same
  command again: it resumes the unfinished run (finished jobs and sections are skipped).
- **Watching it:** the main window shows every running job's log as it happens, each line
  prefixed with the job id, e.g. `[sup1/12] 22:41:05 [model] codex (proposer) calling...`, then
  `... ok 74.2s, tokens ...`, round results, pauses and errors. Also a heartbeat every 5 minutes
  per job, which job is waiting for which backend, and the supervisor's notes and actions.
  `-QuietJobs` keeps only starts, finishes and heartbeats. Each job's `job.log` has the same
  lines. To follow one job from a second window:

```powershell
Get-ChildItem reports\overnight -Recurse -Filter job.log | Sort-Object LastWriteTime | Select-Object -Last 1 | Get-Content -Tail 30 -Wait
```

  Every prompt and reply is saved per job in `transcript.jsonl` (kept on the PC, not pushed).
- **Stop:** create a file named `STOP` in the repo folder (`New-Item STOP`); or pass
  `-Until 08:30` to stop at a time. Delete `STOP` before the next run.

Before leaving it:

1. Settings > System > Power: set "When plugged in, put my device to sleep after" to Never (the
   runner also asks Windows to stay awake, but this is the safe setting).
2. Settings > Windows Update: "Pause updates" for a week, so it doesn't reboot overnight.
3. Run `doctor --ping` once (section 5) and check Claude Code / Codex are signed in.

## 8. Everyday controls

After every reboot, start the GPU-pinned Ollama servers before any run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_ollama.ps1
```

Stop them:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_ollama.ps1 -Stop
```

Stop a running experiment cleanly (from a second PowerShell window in the repo folder):

```powershell
New-Item STOP
```

Delete `STOP` before the next run:

```powershell
Remove-Item STOP
```

See usage windows and pauses for Claude Code / Codex:

```powershell
.\.venv\Scripts\lpswarm.exe doctor
```

---

## 9. If something goes wrong

| Symptom | Fix |
| --- | --- |
| `Python 3.11+ not found` | Install from python.org with "Add to PATH", open a new PowerShell, re-run setup. |
| winget missing / Ollama install fails | Install Ollama from ollama.com/download, open a new PowerShell, re-run setup. |
| `could not pull <tag>` | That tag may not exist: try `-ProposerModels qwen3:8b` or `-RankerModels granite3.3:2b`, or pick one from ollama.com/library. |
| doctor: Ollama `not reachable` | Run `scripts\start_ollama.ps1`; logs in `reports\ollama-11434.log` / `ollama-11435.log`. |
| doctor: model `not pulled` | The tag in `config\models.toml` differs from what downloaded; fix the tag or re-run setup with `-Force`. |
| Ollama tray app reopened and grabbed port 11434 | Re-run `scripts\start_ollama.ps1` (it closes the tray app first). |
| Claude Code ping fails | Run `claude` once and sign in; make sure `claude --version` works in the same window. |
| Lots of `invalid=` in swarm output | The model returns bad JSON: try a bigger model, keep `json_mode = true`. |
| Rune glyphs print as `?` | Cosmetic. Run `chcp 65001` first if you want them. |

When asking for help, paste the output of:

```powershell
.\.venv\Scripts\lpswarm.exe doctor
```

and the `tiertest.md` from the run's `--out` folder (reports are not committed to git).

---

More detail: `docs\phase3_runbook.md` (full runbook), `README.md` (what everything is),
`TODO_USER.md` (open decisions).

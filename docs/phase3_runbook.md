# Phase 3 runbook (Windows, at home)

The model tier test asks one question: do model-driven generators find ciphers better
than (a) the Phase 1 brute force and (b) random programs from the same cipher language, at
comparable cost? Everything below runs from the repo root in PowerShell, with the venv active.

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

- `random_program:40` gets the same number of proposals as a model arm (5 rounds × 8) and is
  the fair control per proposal. `random_program:2000` is the control per unit of compute.
- Add `--ranker granite-tiny` to have Granite order each round's proposals.
- Read `reports\tier1\tiertest.md`. A model arm "wins" only if its recall clearly beats
  `random_program:40` (non-overlapping CIs, or the same result over several seeds via
  `--seed`) and is reasonable per dollar compared with `baseline` and `random_program:2000`.

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

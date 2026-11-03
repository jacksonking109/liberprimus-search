<#
.SYNOPSIS
  One-command setup for lpswarm on Windows: Python venv, Ollama, models pinned to
  GPUs, config\models.toml, tests, health check and a dry run.

.DESCRIPTION
  Safe to re-run: finished steps are skipped or repeated harmlessly. Never asks for,
  reads or stores an API key.

  From the repo root:
      powershell -ExecutionPolicy Bypass -File scripts\setup_windows.ps1

  Options:
      -ProposerModels qwen3:14b,qwen3:8b   first tag that pulls is used (big GPU)
      -ExtraModels gemma3:12b              also pulled for the big GPU ('' to skip)
      -RankerModels granite4:tiny-h,granite3.3:2b   first that pulls (small GPU)
      -Force        rewrite config\models.toml even if it exists
      -SkipTests    skip pytest
      -SkipModels   skip Ollama install, servers and model pulls
#>
[CmdletBinding()]
param(
    [string[]]$ProposerModels = @("qwen3:14b", "qwen3:8b"),
    [string[]]$ExtraModels = @("gemma3:12b"),
    [string[]]$RankerModels = @("granite4:tiny-h", "granite3.3:2b"),
    [switch]$Force,
    [switch]$SkipTests,
    [switch]$SkipModels
)

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$VenvPy = Join-Path $Root ".venv\Scripts\python.exe"
$Lpswarm = Join-Path $Root ".venv\Scripts\lpswarm.exe"
$ModelsToml = Join-Path $Root "config\models.toml"
$GpuFile = Join-Path $Root "config\gpus.json"
$script:Problems = @()

function Write-Step([string]$Status, [string]$Message) {
    $color = @{ "OK" = "Green"; "WARN" = "Yellow"; "FAIL" = "Red"; "...." = "Cyan" }[$Status]
    if (-not $color) { $color = "White" }
    Write-Host ("[{0,-4}] {1}" -f $Status, $Message) -ForegroundColor $color
    if ($Status -eq "FAIL") { $script:Problems += $Message }
}

function Stop-Setup([string]$Message) {
    Write-Step "FAIL" $Message
    Write-Host "`nSetup stopped. Fix the problem above and run the script again." -ForegroundColor Red
    exit 1
}

function Update-PathFromRegistry {
    $machine = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $user = [Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machine;$user"
    $local = Join-Path $env:LOCALAPPDATA "Programs\Ollama"
    if ((Test-Path $local) -and ($env:Path -notlike "*$local*")) { $env:Path = "$env:Path;$local" }
}

# ------------------------------------------------------------------ 1. Python
Write-Host "`n== Python" -ForegroundColor Cyan
$py = $null
$candidates = @(@("py", "-3.13"), @("py", "-3.12"), @("py", "-3.11"), @("py", "-3"), @("python"))
foreach ($c in $candidates) {
    $exe = $c[0]
    if (-not (Get-Command $exe -ErrorAction SilentlyContinue)) { continue }
    $cargs = @()
    if ($c.Count -gt 1) { $cargs = @($c[1]) }
    $out = & $exe @cargs -c "import sys; print(int(sys.version_info >= (3, 11)))" 2>$null
    if ($LASTEXITCODE -eq 0 -and "$out".Trim() -eq "1") { $py = @($exe) + $cargs; break }
}
if (-not $py) { Stop-Setup "Python 3.11+ not found. Install it from https://www.python.org/downloads/ (tick 'Add to PATH') and re-run." }
$pyExe = $py[0]
$pyArgs = @()
if ($py.Count -gt 1) { $pyArgs = $py[1..($py.Count - 1)] }
$ver = & $pyExe @pyArgs -c "import sys; print(sys.version.split()[0])"
Write-Step "OK" "Python $ver ($($py -join ' '))"

# -------------------------------------------------------------- 2. venv + deps
if (-not (Test-Path $VenvPy)) {
    Write-Step "...." "creating .venv"
    & $pyExe @pyArgs -m venv .venv
    if ($LASTEXITCODE -ne 0) { Stop-Setup "could not create .venv" }
}
Write-Step "...." "installing lpswarm and dependencies into .venv (first time takes a minute)"
& $VenvPy -m pip install --quiet --upgrade pip
& $VenvPy -m pip install --quiet -e ".[dev]"
if ($LASTEXITCODE -ne 0) { Stop-Setup "pip install failed (see the messages above)" }
Write-Step "OK" "lpswarm installed in .venv"

# ------------------------------------------------------- 3-6. Ollama and models
$proposerTag = $null
$extraTag = $null
$rankerTag = $null
$rankerPort = 11435
if (-not $SkipModels) {
    Write-Host "`n== Ollama" -ForegroundColor Cyan
    Update-PathFromRegistry
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
            Stop-Setup "Ollama is not installed and winget is unavailable. Install Ollama from https://ollama.com/download and re-run."
        }
        Write-Step "...." "installing Ollama with winget (Windows may ask for permission)"
        & winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements
        Update-PathFromRegistry
        if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
            Stop-Setup "Ollama install did not put 'ollama' on PATH. Open a new PowerShell window and re-run."
        }
    }
    $ollamaVer = & ollama --version 2>$null
    Write-Step "OK" "Ollama: $ollamaVer"

    Write-Host "`n== GPUs and servers" -ForegroundColor Cyan
    & (Join-Path $PSScriptRoot "start_ollama.ps1")
    if ($LASTEXITCODE -ne 0) { Stop-Setup "could not start the Ollama servers (see reports\ollama-*.log)" }
    $plan = $null
    if (Test-Path $GpuFile) { $plan = Get-Content $GpuFile -Raw | ConvertFrom-Json }
    $twoGpus = ($plan -and $plan.proposer -and $plan.ranker)
    if (-not $twoGpus) { $rankerPort = 11434 }

    function Get-FirstModel([string[]]$Tags, [int]$Port, [string]$What) {
        $old = $env:OLLAMA_HOST
        $env:OLLAMA_HOST = "127.0.0.1:$Port"
        try {
            foreach ($t in $Tags) {
                if (-not $t) { continue }
                Write-Step "...." "pulling $t for $What (large download the first time)"
                & ollama pull $t | Out-Host   # keep pull output out of the return value
                if ($LASTEXITCODE -eq 0) { Write-Step "OK" "$What model: $t"; return $t }
                Write-Step "WARN" "could not pull $t"
            }
        } finally {
            if ($null -eq $old) { Remove-Item Env:OLLAMA_HOST -ErrorAction SilentlyContinue }
            else { $env:OLLAMA_HOST = $old }
        }
        return $null
    }

    Write-Host "`n== Models" -ForegroundColor Cyan
    $proposerTag = Get-FirstModel $ProposerModels 11434 "proposer"
    if (-not $proposerTag) { Write-Step "FAIL" "no proposer model could be pulled (tried: $($ProposerModels -join ', '))" }
    $extraTag = Get-FirstModel $ExtraModels 11434 "second proposer"
    $rankerTag = Get-FirstModel $RankerModels $rankerPort "ranker"
    if (-not $rankerTag) { Write-Step "WARN" "no ranker model pulled (tried: $($RankerModels -join ', ')); runs work without --ranker" }
}

# ------------------------------------------------------------ 7. models.toml
Write-Host "`n== Config" -ForegroundColor Cyan
if ((Test-Path $ModelsToml) -and -not $Force) {
    Write-Step "OK" "config\models.toml exists; left unchanged (use -Force to regenerate)"
} else {
    $lines = @(
        "# Generated by scripts\setup_windows.ps1 on $(Get-Date -Format 'yyyy-MM-dd HH:mm'). Edit freely.",
        "# No secrets in this file: API keys come from environment variables (api_key_env).",
        "",
        "[models.deepseek]",
        'provider = "openai_compatible"',
        'endpoint = "https://api.deepseek.com"',
        'model = "deepseek-chat"            # confirm against DeepSeek''s docs',
        'api_key_env = "DEEPSEEK_API_KEY"',
        'roles = ["proposer"]',
        "max_usd = 10.0",
        "price_in_per_mtok = 0.0            # FILL IN from DeepSeek's pricing page",
        "price_out_per_mtok = 0.0           # FILL IN",
        "json_mode = true",
        "timeout = 180",
        ""
    )
    if ($proposerTag) {
        $lines += @("[models.qwen-local]", 'provider = "ollama"', 'endpoint = "http://127.0.0.1:11434"',
            "model = `"$proposerTag`"", 'roles = ["proposer"]', "json_mode = true", "timeout = 600",
            "options = { num_ctx = 16384 }", "")
    }
    if ($extraTag) {
        $lines += @("[models.gemma-local]", 'provider = "ollama"', 'endpoint = "http://127.0.0.1:11434"',
            "model = `"$extraTag`"", 'roles = ["proposer"]', "json_mode = true", "timeout = 600",
            "options = { num_ctx = 16384 }", "")
    }
    if ($rankerTag) {
        $lines += @("[models.granite]", 'provider = "ollama"', "endpoint = `"http://127.0.0.1:$rankerPort`"",
            "model = `"$rankerTag`"", 'roles = ["weighting", "triage"]', "json_mode = true", "timeout = 120",
            "options = { num_ctx = 8192 }", "")
    }
    if (Get-Command claude -ErrorAction SilentlyContinue) {
        $lines += @("# Claude Code on your plan (tools off, temp folder, API keys ignored). Sign in once: claude",
            "[models.claude-code]", 'provider = "claude_code"', 'model = "sonnet"', 'roles = ["proposer"]',
            "max_calls_per_window = 40", "window_hours = 5", "timeout = 600", "")
        Write-Step "OK" "found Claude Code; added model claude-code (40 calls per 5h cap)"
    } else {
        $lines += @("# Claude Code not found when this file was generated. Install it, sign in, then uncomment:",
            "# [models.claude-code]", '# provider = "claude_code"', '# model = "sonnet"', '# roles = ["proposer"]',
            "# max_calls_per_window = 40", "# window_hours = 5", "")
    }
    $lines += @("# Codex on your ChatGPT plan: check OpenAI's terms for automated codex exec use, then uncomment.",
        "# [models.codex]", '# provider = "codex"', '# model = "default"', '# roles = ["proposer"]',
        "# max_calls_per_window = 30", "# window_hours = 5", "# timeout = 600", "")
    $lines += @("[models.dry]", 'provider = "scripted"', 'model = "dry"', 'roles = ["proposer", "weighting"]',
        "replies = ['{`"proposals`": [{`"spec`": {`"stream`": {`"kind`": `"sequence`", `"name`": `"primes`"}, `"combine`": `"sub`"}, `"why`": `"dry run`"}]}']",
        "")
    New-Item -ItemType Directory -Force -Path (Split-Path $ModelsToml) | Out-Null
    [IO.File]::WriteAllText($ModelsToml, ($lines -join "`r`n"), (New-Object System.Text.UTF8Encoding $false))
    Write-Step "OK" "wrote config\models.toml"
}

# ------------------------------------------------------- 8. tests, doctor, dry run
if (-not $SkipTests) {
    Write-Host "`n== Tests (about a minute)" -ForegroundColor Cyan
    & $VenvPy -m pytest -q
    if ($LASTEXITCODE -eq 0) { Write-Step "OK" "all tests passed" } else { Write-Step "FAIL" "some tests failed (see above)" }
}

Write-Host "`n== Health check" -ForegroundColor Cyan
& $Lpswarm doctor --models $ModelsToml
if ($LASTEXITCODE -ne 0) { Write-Step "WARN" "doctor reported problems (see above)" }

Write-Host "`n== Dry run (no network, no cost)" -ForegroundColor Cyan
& $Lpswarm tiertest --models $ModelsToml --arms dry --quick --quiet --out reports\dry --spend-ledger reports\dry\spend.sqlite
if ($LASTEXITCODE -eq 0) { Write-Step "OK" "dry run finished: reports\dry\tiertest.md" } else { Write-Step "FAIL" "dry run failed" }

# ------------------------------------------------------------- 9. next steps
Write-Host "`n== Next steps" -ForegroundColor Cyan
$arms = @("baseline", "random_program:40", "random_program:2000")
if ($proposerTag) { $arms += "qwen-local" }
if ($extraTag) { $arms += "gemma-local" }
$hasClaudeModel = (Test-Path $ModelsToml) -and (Select-String -Path $ModelsToml -Pattern '^\[models\.claude-code\]' -Quiet)
$rankerFlag = ""
if ($rankerTag) { $rankerFlag = " --ranker granite" }
Write-Host @"
After each reboot, start the GPU-pinned Ollama servers:
    powershell -ExecutionPolicy Bypass -File scripts\start_ollama.ps1

Local models only (free):
    .\.venv\Scripts\lpswarm.exe tiertest --models config\models.toml --arms $($arms -join ',')$rankerFlag --lengths 80,160 --cases 10 --out reports\tier1

To add DeepSeek:
  1. Put the prices in config\models.toml (price_in_per_mtok / price_out_per_mtok).
  2. In this PowerShell window:  `$env:DEEPSEEK_API_KEY = "<your key>"
  3. .\.venv\Scripts\lpswarm.exe doctor --ping
  4. Add ,deepseek to --arms and keep --max-usd small for the first run.

More: docs\phase3_runbook.md
"@

if ($hasClaudeModel) {
    Write-Host @"
Claude Code on your plan (paces itself to the call cap; pauses at usage limits).
Sign in once by running: claude    then:
    .\.venv\Scripts\lpswarm.exe tiertest --models config\models.toml --arms claude-code --lengths 80,160 --cases 3 --out reports\tier-claude
"@
}

if ($script:Problems.Count -gt 0) {
    Write-Host "`nFinished with $($script:Problems.Count) problem(s):" -ForegroundColor Yellow
    $script:Problems | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    exit 1
}
Write-Host "`nSetup complete." -ForegroundColor Green
exit 0

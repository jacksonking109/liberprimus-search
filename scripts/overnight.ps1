<#
.SYNOPSIS
  Start (or resume) the unattended job queue in config\overnight.toml.

.DESCRIPTION
  Starts the GPU-pinned Ollama servers, then runs `lpswarm overnight`. Re-running this
  script resumes an unfinished run. Results: reports\overnight\<run>\SUMMARY.md, and the
  `results` branch on GitHub if publish = true in config\overnight.toml.

  Stop cleanly: create a file named STOP in the repo folder (New-Item STOP).

      powershell -ExecutionPolicy Bypass -File scripts\overnight.ps1
      powershell -ExecutionPolicy Bypass -File scripts\overnight.ps1 -Until 08:30
      powershell -ExecutionPolicy Bypass -File scripts\overnight.ps1 -New -NoPublish
      powershell -ExecutionPolicy Bypass -File scripts\overnight.ps1 -RetryFailed
#>
[CmdletBinding()]
param(
    [string]$Until = "",
    [switch]$New,
    [switch]$NoPublish,
    [switch]$NoOllama,
    [switch]$RetryFailed
)

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$Lpswarm = Join-Path $Root ".venv\Scripts\lpswarm.exe"
if (-not (Test-Path $Lpswarm)) {
    Write-Host "lpswarm is not installed yet: run scripts\setup_windows.ps1 first" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path (Join-Path $Root "config\overnight.toml"))) {
    Copy-Item (Join-Path $Root "config\overnight.example.toml") (Join-Path $Root "config\overnight.toml")
    Write-Host "created config\overnight.toml from the example" -ForegroundColor Yellow
}
if (Test-Path (Join-Path $Root "STOP")) {
    Write-Host "A STOP file exists in the repo folder; delete it to run (Remove-Item STOP)." -ForegroundColor Yellow
    exit 1
}
if (-not $NoOllama) {
    & (Join-Path $PSScriptRoot "start_ollama.ps1")
    if ($LASTEXITCODE -ne 0) { Write-Host "Ollama servers did not start; local-model jobs may fail" -ForegroundColor Yellow }
}

$argsList = @("overnight", "--config", "config\overnight.toml")
if ($Until) { $argsList += @("--until", $Until) }
if ($New) { $argsList += "--new" }
if ($NoPublish) { $argsList += "--no-publish" }
if ($RetryFailed) { $argsList += "--retry-failed" }
& $Lpswarm @argsList
exit $LASTEXITCODE

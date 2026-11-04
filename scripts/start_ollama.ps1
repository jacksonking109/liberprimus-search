<#
.SYNOPSIS
  Start one Ollama server per GPU: the big GPU (proposer models) on port 11434,
  the small GPU (ranker model) on port 11435.

.DESCRIPTION
  Each server is pinned to one GPU with CUDA_VISIBLE_DEVICES=<GPU UUID>, set only
  for that server process. Both share the normal model store, so a model pulled
  once is visible to both. The Ollama tray app's own server is stopped first,
  because it would otherwise hold port 11434 and use every GPU.

  GPU choice is saved in config\gpus.json (biggest VRAM = proposer GPU, smallest =
  ranker GPU). It is re-detected automatically when the number of GPUs changes
  (e.g. a second card is installed); delete the file to force it. With one GPU (or
  none) the proposer server runs on 11434 and the ranker server on 11435 runs on the
  CPU, so the models config never changes when a second card goes in.

  Run after every reboot, before lpswarm runs:
      powershell -ExecutionPolicy Bypass -File scripts\start_ollama.ps1
  Stop the servers:
      powershell -ExecutionPolicy Bypass -File scripts\start_ollama.ps1 -Stop
#>
[CmdletBinding()]
param(
    [switch]$Stop,
    [int]$ProposerPort = 11434,
    [int]$RankerPort = 11435
)

$ErrorActionPreference = "Continue"
$Root = Split-Path -Parent $PSScriptRoot
$Reports = Join-Path $Root "reports"
$GpuFile = Join-Path $Root "config\gpus.json"
$PidFile = Join-Path $Reports "ollama.pids"
New-Item -ItemType Directory -Force -Path $Reports | Out-Null

function Write-Step([string]$Status, [string]$Message) {
    $color = @{ "OK" = "Green"; "WARN" = "Yellow"; "FAIL" = "Red"; "...." = "Cyan" }[$Status]
    if (-not $color) { $color = "White" }
    Write-Host ("[{0,-4}] {1}" -f $Status, $Message) -ForegroundColor $color
}

function Test-Ollama([int]$Port) {
    try {
        $wc = New-Object System.Net.WebClient
        $wc.Proxy = $null   # never route localhost through a system proxy
        [void]$wc.DownloadString("http://127.0.0.1:$Port/api/tags")
        return $true
    } catch {
        return $false
    }
}

function Stop-OurServers {
    # The PID file can be stale after a reboot (PIDs reused by other programs), so only
    # stop a recorded PID if it is still an ollama process.
    if (Test-Path $PidFile) {
        foreach ($id in Get-Content $PidFile) {
            if ($id -match '^\d+$') {
                $proc = Get-Process -Id ([int]$id) -ErrorAction SilentlyContinue
                if ($proc -and $proc.ProcessName -like "ollama*") {
                    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                }
            }
        }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
}

function Stop-AllOllama {
    # Tray app first (it restarts its server otherwise), then any remaining servers.
    Get-Process -Name "ollama app" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name "ollama" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
}

function Get-Gpus {
    $smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if (-not $smi) { return @() }
    $lines = & $smi.Source --query-gpu=index,uuid,name,memory.total --format=csv,noheader,nounits
    if ($LASTEXITCODE -ne 0) { return @() }
    $gpus = @()
    foreach ($line in $lines) {
        $parts = $line -split ',\s*'
        if ($parts.Count -ge 4) {
            $gpus += [pscustomobject]@{
                index = [int]$parts[0]; uuid = $parts[1].Trim(); name = $parts[2].Trim()
                memory_mb = [int]$parts[3]
            }
        }
    }
    return $gpus
}

function Get-GpuPlan {
    $gpus = @(Get-Gpus | Sort-Object memory_mb -Descending)
    if (Test-Path $GpuFile) {
        $saved = Get-Content $GpuFile -Raw | ConvertFrom-Json
        $savedCount = [int][bool]$saved.proposer + [int][bool]$saved.ranker
        $nowCount = [Math]::Min($gpus.Count, 2)
        # Keep the saved choice unless the GPU count changed (nvidia-smi failing counts as
        # "unknown", not as zero GPUs).
        if ($gpus.Count -eq 0 -or $savedCount -eq $nowCount) { return $saved }
        Write-Step "...." "number of GPUs changed ($savedCount -> $nowCount); choosing GPUs again"
    }
    $plan = [pscustomobject]@{ proposer = $null; ranker = $null }
    if ($gpus.Count -ge 1) { $plan.proposer = $gpus[0] }
    if ($gpus.Count -ge 2) { $plan.ranker = $gpus[$gpus.Count - 1] }
    New-Item -ItemType Directory -Force -Path (Split-Path $GpuFile) | Out-Null
    $json = $plan | ConvertTo-Json -Depth 3
    [IO.File]::WriteAllText($GpuFile, $json, (New-Object System.Text.UTF8Encoding $false))
    return $plan
}

function Start-OneServer([int]$Port, [string]$Uuid, [switch]$Cpu) {
    $ollama = Get-Command ollama -ErrorAction SilentlyContinue
    if (-not $ollama) { throw "ollama is not on PATH (run scripts\setup_windows.ps1 first)" }
    $oldHost = $env:OLLAMA_HOST
    $oldCuda = $env:CUDA_VISIBLE_DEVICES
    try {
        $env:OLLAMA_HOST = "127.0.0.1:$Port"
        if ($Cpu) { $env:CUDA_VISIBLE_DEVICES = "-1" }      # hide every GPU: CPU only
        elseif ($Uuid) { $env:CUDA_VISIBLE_DEVICES = $Uuid }
        else { Remove-Item Env:CUDA_VISIBLE_DEVICES -ErrorAction SilentlyContinue }
        $log = Join-Path $Reports "ollama-$Port.log"
        if (Test-Ollama $Port) {
            Write-Step "FAIL" "port $Port is already answering (another Ollama server or service?); stop it and re-run"
            return $false
        }
        $p = Start-Process -FilePath $ollama.Source -ArgumentList "serve" -WindowStyle Hidden `
            -RedirectStandardError $log -RedirectStandardOutput "$log.out" -PassThru
        Add-Content -Path $PidFile -Value $p.Id
    } finally {
        if ($null -eq $oldHost) { Remove-Item Env:OLLAMA_HOST -ErrorAction SilentlyContinue }
        else { $env:OLLAMA_HOST = $oldHost }
        if ($null -eq $oldCuda) { Remove-Item Env:CUDA_VISIBLE_DEVICES -ErrorAction SilentlyContinue }
        else { $env:CUDA_VISIBLE_DEVICES = $oldCuda }
    }
    for ($i = 0; $i -lt 60; $i++) {
        if ($p.HasExited) { return $false }   # e.g. failed to bind the port
        if (Test-Ollama $Port) { return $true }
        Start-Sleep -Seconds 1
    }
    return $false
}

if ($Stop) {
    Stop-OurServers
    Stop-AllOllama
    Write-Step "OK" "Ollama servers stopped"
    exit 0
}

$plan = Get-GpuPlan
Stop-OurServers
Stop-AllOllama

if ($plan.proposer -and $plan.ranker) {
    Write-Step "...." ("proposer GPU: {0} ({1} MB) -> port {2}" -f $plan.proposer.name, $plan.proposer.memory_mb, $ProposerPort)
    Write-Step "...." ("ranker GPU:   {0} ({1} MB) -> port {2}" -f $plan.ranker.name, $plan.ranker.memory_mb, $RankerPort)
    $ok1 = Start-OneServer $ProposerPort $plan.proposer.uuid
    $ok2 = Start-OneServer $RankerPort $plan.ranker.uuid
    if ($ok1) { Write-Step "OK" "proposer server on 127.0.0.1:$ProposerPort" } else { Write-Step "FAIL" "proposer server did not start; see reports\ollama-$ProposerPort.log" }
    if ($ok2) { Write-Step "OK" "ranker server on 127.0.0.1:$RankerPort" } else { Write-Step "FAIL" "ranker server did not start; see reports\ollama-$RankerPort.log" }
    if (-not ($ok1 -and $ok2)) { exit 1 }
} else {
    $uuid = $null
    if ($plan.proposer) { $uuid = $plan.proposer.uuid; Write-Step "...." ("single GPU: {0}" -f $plan.proposer.name) }
    else { Write-Step "WARN" "no NVIDIA GPU found (nvidia-smi); Ollama will choose its own device" }
    if (Start-OneServer $ProposerPort $uuid) { Write-Step "OK" "proposer server on 127.0.0.1:$ProposerPort" }
    else { Write-Step "FAIL" "server did not start; see reports\ollama-$ProposerPort.log"; exit 1 }
    # The ranker (a small model) runs on the CPU until a second GPU is installed; then the
    # next run of this script puts port $RankerPort on that GPU instead.
    if (Start-OneServer $RankerPort $null -Cpu) {
        Write-Step "OK" "ranker server on 127.0.0.1:$RankerPort (CPU; moves to a second GPU when one is installed)"
    } else {
        Write-Step "WARN" "ranker server did not start (see reports\ollama-$RankerPort.log); runs still work without --ranker"
    }
}
exit 0

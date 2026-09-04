[CmdletBinding()]
param(
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$venvPath = Join-Path $projectRoot ".venv"
$env:UV_CACHE_DIR = Join-Path $projectRoot ".uv-cache"
$env:UV_PYTHON_INSTALL_DIR = Join-Path $projectRoot ".python"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is required. Install it from https://docs.astral.sh/uv/ and run this script again."
}

if ($Recreate -and (Test-Path -LiteralPath $venvPath)) {
    Remove-Item -LiteralPath $venvPath -Recurse -Force
}

if (-not (Test-Path -LiteralPath $venvPath)) {
    uv venv $venvPath --python 3.11 --python-preference managed --seed
    if ($LASTEXITCODE -ne 0) { throw "Failed to create the virtual environment." }
}

$pythonPath = Join-Path $venvPath "Scripts\python.exe"
$lockPath = Join-Path $projectRoot "requirements-local.lock"
$requirementsPath = if (Test-Path -LiteralPath $lockPath) {
    $lockPath
} else {
    Join-Path $projectRoot "requirements-local.txt"
}

uv pip install --python $pythonPath --requirements $requirementsPath
if ($LASTEXITCODE -ne 0) { throw "Failed to install course dependencies." }
uv pip install --python $pythonPath --editable $projectRoot --no-deps
if ($LASTEXITCODE -ne 0) { throw "Failed to install the local mitdeeplearning package." }

& $pythonPath (Join-Path $projectRoot "scripts\verify-environment.py")
if ($LASTEXITCODE -ne 0) { throw "Environment verification failed." }

Write-Host ""
Write-Host "Environment ready. Start Jupyter with:"
Write-Host "  .\scripts\start-jupyter.ps1"

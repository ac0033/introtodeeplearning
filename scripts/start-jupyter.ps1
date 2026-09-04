$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$jupyterPath = Join-Path $projectRoot ".venv\Scripts\jupyter-lab.exe"

if (-not (Test-Path -LiteralPath $jupyterPath)) {
    throw "Local environment not found. Run .\scripts\setup-local.ps1 first."
}

Set-Location $projectRoot
& $jupyterPath

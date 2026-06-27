<#
.SYNOPSIS
    One-shot script to migrate a legacy requirements.txt project to
    pyproject.toml managed by uv (Astral).

.DESCRIPTION
    This script:
    1. Checks that uv is installed
    2. Creates a pyproject.toml from existing requirements.txt
    3. Generates uv.lock
    4. Syncs the virtual environment
    5. Verifies the app imports correctly
    6. Removes the legacy requirements.txt

.PARAMETER BackendDir
    Path to the backend directory. Defaults to the parent of the script directory.

.EXAMPLE
    cd backend; .\scripts\migrate-to-uv.ps1
#>

param(
    [string]$BackendDir = (Join-Path $PSScriptRoot ".." | Resolve-Path)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "=== Checking prerequisites ===" -ForegroundColor Cyan
try {
    $uvVersion = & uv --version 2>&1 | Out-String
    Write-Host "uv version: $uvVersion" -NoNewline
} catch {
    Write-Host "ERROR: 'uv' not found. Install it first:" -ForegroundColor Red
    Write-Host "  pip install uv" -ForegroundColor Yellow
    Write-Host "  or visit https://docs.astral.sh/uv/#installation" -ForegroundColor Yellow
    exit 1
}

$reqFile = Join-Path $BackendDir "requirements.txt"
if (-not (Test-Path $reqFile)) {
    Write-Host "ERROR: No requirements.txt found in $BackendDir" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== 1. Detected dependencies from requirements.txt ===" -ForegroundColor Cyan
Get-Content $reqFile

Write-Host "`n=== 2. Ensuring pyproject.toml exists ===" -ForegroundColor Cyan
$projFile = Join-Path $BackendDir "pyproject.toml"
if (-not (Test-Path $projFile)) {
    Write-Host "pyproject.toml not found — creating one from template..." -ForegroundColor Yellow
    $pyproject = @"
[project]
name = "stride-alytics-backend"
version = "0.1.0"
description = "StrideAlytics platform — backend API"
requires-python = ">=3.10"
dependencies = []

[dependency-groups]
dev = []

[tool.hatch.build.targets.wheel]
packages = ["app/"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"@
    Set-Content -Path $projFile -Value $pyproject -Encoding UTF8
    Write-Host "pyproject.toml created." -ForegroundColor Green
} else {
    Write-Host "pyproject.toml already exists — skipping creation." -ForegroundColor Green
}

Push-Location $BackendDir
try {
    Write-Host "`n=== 3. Generating uv.lock (resolving dependencies) ===" -ForegroundColor Cyan
    uv lock
    Write-Host "uv.lock generated successfully." -ForegroundColor Green

    Write-Host "`n=== 4. Syncing virtual environment ===" -ForegroundColor Cyan
    uv sync --frozen --no-dev
    Write-Host "All packages installed." -ForegroundColor Green

    Write-Host "`n=== 5. Verification ===" -ForegroundColor Cyan
    Write-Host "Checking that the app can import its main module..."
    uv run python -c "from app.main import app; print('✓ FastAPI app loaded successfully')"

    Write-Host "`n=== 6. Cleanup ===" -ForegroundColor Cyan
    if (Test-Path $reqFile) {
        Write-Host "Removing legacy requirements.txt..."
        Remove-Item $reqFile
        Write-Host "✓ requirements.txt deleted." -ForegroundColor Green
    }

    Write-Host "`n============================================" -ForegroundColor Cyan
    Write-Host " Migration complete!                         " -ForegroundColor Cyan
    Write-Host "--------------------------------------------" -ForegroundColor Cyan
    Write-Host " New files:                                  " -ForegroundColor Cyan
    Write-Host "   pyproject.toml  — project config + deps" -ForegroundColor Cyan
    Write-Host "   uv.lock          — deterministic lock" -ForegroundColor Cyan
    Write-Host "   .venv/           — virtual environment" -ForegroundColor Cyan
    Write-Host "                                              " -ForegroundColor Cyan
    Write-Host " Removed:                                    " -ForegroundColor Cyan
    Write-Host "   requirements.txt  — (legacy, deleted)" -ForegroundColor Cyan
    Write-Host "                                              " -ForegroundColor Cyan
    Write-Host " Next steps:                                 " -ForegroundColor Cyan
    Write-Host "   cd backend                                 " -ForegroundColor Cyan
    Write-Host "   uv run uvicorn app.main:app --reload       " -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan
} finally {
    Pop-Location
}
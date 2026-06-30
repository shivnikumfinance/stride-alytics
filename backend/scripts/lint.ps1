<#
.SYNOPSIS
    Thin wrapper around `uv run lint` — runs ruff check.

.DESCRIPTION
    Forwards any extra args to lint, so `.\scripts\lint.ps1 --fix` works.

.PARAMETER ExtraArgs
    Additional arguments passed to `uv run lint`.

.EXAMPLE
    cd backend; .\scripts\lint.ps1 --fix
#>

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$BackendDir = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $BackendDir

& uv run lint @ExtraArgs
exit $LASTEXITCODE

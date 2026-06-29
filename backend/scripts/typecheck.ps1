<#
.SYNOPSIS
    Thin wrapper around `uv run typecheck` — runs mypy on the application package.

.PARAMETER ExtraArgs
    Additional arguments passed to `uv run typecheck`.

.EXAMPLE
    cd backend; .\scripts\typecheck.ps1
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

& uv run typecheck @ExtraArgs
exit $LASTEXITCODE

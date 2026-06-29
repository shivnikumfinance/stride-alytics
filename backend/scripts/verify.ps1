<#
.SYNOPSIS
    Thin wrapper around `uv run verify` — runs the full backend quality gate.

.DESCRIPTION
    Mirrors the pre-commit hook so editor, CLI, and CI can never disagree.
    Forwards any extra args to verify.

.PARAMETER ExtraArgs
    Additional arguments passed to `uv run verify`.

.EXAMPLE
    cd backend; .\scripts\verify.ps1
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

& uv run verify @ExtraArgs
exit $LASTEXITCODE

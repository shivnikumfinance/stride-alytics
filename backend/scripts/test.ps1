<#
.SYNOPSIS
    Thin wrapper around `uv run test` — runs pytest.

.DESCRIPTION
    Forwards extra args, so `.\scripts\test.ps1 -k greeks -x` works.

.PARAMETER ExtraArgs
    Additional arguments passed to `uv run test` (and thus pytest).

.EXAMPLE
    cd backend; .\scripts\test.ps1
    cd backend; .\scripts\test.ps1 tests\test_services.py -v
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

& uv run test @ExtraArgs
exit $LASTEXITCODE

<#
.SYNOPSIS
    Thin wrapper around `uv run format` — runs black --check (or --write).

.DESCRIPTION
    Default mode is ``black --check`` (CI). Pass ``--write`` to apply
    formatting in place.

.PARAMETER ExtraArgs
    Additional arguments passed to `uv run format`.

.EXAMPLE
    cd backend; .\scripts\format.ps1            # CI check
    cd backend; .\scripts\format.ps1 --write    # apply formatting
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

& uv run format @ExtraArgs
exit $LASTEXITCODE

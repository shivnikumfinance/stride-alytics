<#
.SYNOPSIS
    Apply all database migrations in order.

.DESCRIPTION
    Connects to the database in $env:DATABASE_URL (or the local
    docker-compose default) and runs every migrations/*.sql file in
    lexical order, except *_down.sql.

.EXAMPLE
    .\database\scripts\apply_migrations.ps1
    $env:DATABASE_URL = 'postgresql://postgres:postgres@localhost:5432/stridealytics'
    .\database\scripts\apply_migrations.ps1
#>

[CmdletBinding()]
param(
    [string]$DatabaseUrl = $env:DATABASE_URL
)

$ErrorActionPreference = "Stop"
$ROOT = (Resolve-Path "$PSScriptRoot\..\..\").Path
$migDir = Join-Path $ROOT "database\migrations"

if (-not $DatabaseUrl) {
    $DatabaseUrl = "postgresql://postgres:postgres@localhost:5432/stridealytics"
}

Write-Host "Applying migrations from $migDir to $DatabaseUrl" -ForegroundColor Cyan
Write-Host ""

$files = Get-ChildItem -Path $migDir -Filter "*.sql" |
    Where-Object { $_.Name -notlike "*_down.sql" } |
    Sort-Object Name

foreach ($f in $files) {
    Write-Host "  -> $($f.Name)" -ForegroundColor Yellow
    & psql $DatabaseUrl -v ON_ERROR_STOP=1 -f $f.FullName
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  FAILED at $($f.Name)" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "All migrations applied successfully." -ForegroundColor Green
Write-Host ""
Write-Host "Verifying schema:" -ForegroundColor Cyan
& psql $DatabaseUrl -c "\dt" -c "\dv"

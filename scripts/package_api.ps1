param(
    [string]$Name = "CopperAPI"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
  Write-Host "pyinstaller not found. Please 'pip install pyinstaller'" -ForegroundColor Yellow
  exit 1
}

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root

$entry = "app/api/run_api.py"

pyinstaller `
  --name $Name `
  --noconfirm `
  --onefile `
  $entry

Write-Host "API packaged. Dist at .\dist\$Name.exe" -ForegroundColor Green


param(
    [string]$Name = "CopperUI"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
  Write-Host "pyinstaller not found. Please 'pip install pyinstaller'" -ForegroundColor Yellow
  exit 1
}

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $root

$entry = "app/ui/main.py"

# Include QML assets
$data = @(
  "app/ui/qml;app/ui/qml",
  "app/ui/qtquickcontrols2.conf;app/ui"
)

$addDataArgs = @()
foreach ($d in $data) { $addDataArgs += @('--add-data', $d) }

pyinstaller `
  --name $Name `
  --noconfirm `
  --noconsole `
  --onefile `
  $addDataArgs `
  $entry

Write-Host "UI packaged. Dist at .\dist\$Name.exe" -ForegroundColor Green



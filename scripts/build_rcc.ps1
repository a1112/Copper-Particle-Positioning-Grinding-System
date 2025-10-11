param(
  [string]$QtRcc = $(Get-Command rcc -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Source),
  [string]$UiDir = 'app/ui'
)

function Build-One($qrc){
  if (-not (Test-Path $qrc)) { Write-Warning "Missing $qrc"; return }
  $out = [System.IO.Path]::ChangeExtension($qrc, '.rcc')
  if (-not $QtRcc){ Write-Warning 'rcc not found in PATH'; return }
  if ((-not (Test-Path $out)) -or ((Get-Item $out).LastWriteTime -lt (Get-Item $qrc).LastWriteTime)){
    Write-Host "rcc -binary $qrc -> $out"
    & $QtRcc -binary $qrc -o $out
  } else {
    Write-Host "Up-to-date: $out"
  }
}

Push-Location $UiDir
try {
  Build-One 'qml.qrc'
  Build-One 'resource.qrc'
  Build-One 'src.qrc'
}
finally { Pop-Location }

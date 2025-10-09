$ErrorActionPreference = 'Stop'

function Convert-DocxToLines($path){
  $tmp = Join-Path $env:TEMP ([IO.Path]::GetRandomFileName()); New-Item -ItemType Directory -Path $tmp | Out-Null
  try {
    $zip = Join-Path $tmp 'doc.zip'
    Copy-Item $path $zip
    Expand-Archive -Path $zip -DestinationPath $tmp -Force
    $xmlPath = Join-Path $tmp 'word\document.xml'
    $raw = Get-Content -Raw -Encoding UTF8 $xmlPath
    $paras = [regex]::Split($raw, '</w:p>')
    $lines = New-Object System.Collections.Generic.List[string]
    foreach($p in $paras){
      $sb = New-Object System.Text.StringBuilder
      foreach($m in ([regex]::Matches($p, '<w:t[^>]*>(.*?)</w:t>'))){
        $t = $m.Groups[1].Value
        $t = $t -replace '&lt;','<' -replace '&gt;','>' -replace '&amp;','&' -replace '&quot;','"' -replace '&apos;','''
        [void]$sb.Append($t)
      }
      $txt = ($sb.ToString()).TrimEnd()
      if ($txt -ne '') { [void]$lines.Add($txt) }
    }
    return ,$lines
  }
  finally { if (Test-Path $tmp) { Remove-Item -Recurse -Force $tmp } }
}

function Write-MD($lines,$outPath){
  $dir=[IO.Path]::GetDirectoryName($outPath); if(!(Test-Path $dir)){ New-Item -ItemType Directory -Path $dir | Out-Null }
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [IO.File]::WriteAllLines($outPath,$lines,$utf8NoBom)
}

function HtmlEscape([string]$s){
  return ($s -replace '&','&amp;') -replace '<','&lt;' -replace '>','&gt;'
}

function Write-HTML($lines,$outPath){
  $dir=[IO.Path]::GetDirectoryName($outPath); if(!(Test-Path $dir)){ New-Item -ItemType Directory -Path $dir | Out-Null }
  $html = New-Object System.Collections.Generic.List[string]
  $null = $html.Add('<!DOCTYPE html>')
  $null = $html.Add('<html lang="zh-CN">')
  $null = $html.Add('<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
  $null = $html.Add('<title>瀵煎嚭鏂囨。</title>')
  $null = $html.Add('<style>body{font-family:-apple-system,Segoe UI,Roboto,PingFang SC,\"Microsoft YaHei\",Arial,sans-serif;line-height:1.6;padding:24px;max-width:900px;margin:auto;} p{margin:0.6em 0;} .note{color:#888;font-size:12px}</style>')
  $null = $html.Add('</head><body>')
  foreach($ln in $lines){ $null = $html.Add('<p>' + (HtmlEscape $ln) + '</p>') }
  $null = $html.Add('</body></html>')
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [IO.File]::WriteAllLines($outPath,$html,$utf8NoBom)
}

$docs = Get-ChildItem -File -Path "docs" -Filter *.docx
foreach($f in $docs){
  $lines = Convert-DocxToLines $f.FullName
  $base = [IO.Path]::GetFileNameWithoutExtension($f.Name)
  $outMd = Join-Path "docs/export" ($base + ".md")
  $outHtml = Join-Path "docs/export" ($base + ".html")
  Write-MD $lines $outMd
  Write-HTML $lines $outHtml
  Write-Host ("Exported: {0} -> {1}; {2}" -f $f.Name,$outMd,$outHtml)
}


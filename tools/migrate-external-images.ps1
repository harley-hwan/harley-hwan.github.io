param(
  [string] $PostsDir = (Join-Path $PSScriptRoot "..\_posts"),
  [string] $AssetsDir = (Join-Path $PSScriptRoot "..\assets\img\posts"),
  [switch] $DryRun
)

$ErrorActionPreference = "Stop"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$imagePattern = [regex]'!\[(?<alt>[^\]]*)\]\((?<url>https?://[^\s\)]+)(?<title>\s+("[^"]*"|''[^'']*''))?\)'
$imageExtensions = @(".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")
$headers = @{
  "User-Agent" = "Mozilla/5.0 (compatible; harley-hwan-image-migrator/1.0)"
}

function Get-PostAssetSlug {
  param([System.IO.FileInfo] $File)

  $name = [System.IO.Path]::GetFileNameWithoutExtension($File.Name)
  if ($name -match "^\d{4}-\d{2}-\d{2}-(?<slug>.+)$") {
    return $Matches["slug"]
  }

  return $name
}

function Get-SafeImageName {
  param(
    [string] $Url,
    [int] $Index
  )

  $uri = [Uri] $Url
  $sourceName = [System.IO.Path]::GetFileName($uri.AbsolutePath)
  if ([string]::IsNullOrWhiteSpace($sourceName)) {
    $sourceName = "image"
  }

  $sourceName = [Uri]::UnescapeDataString($sourceName)
  $ext = [System.IO.Path]::GetExtension($sourceName).ToLowerInvariant()
  $base = [System.IO.Path]::GetFileNameWithoutExtension($sourceName)

  if ($imageExtensions -notcontains $ext) {
    $base = $sourceName
    $ext = ".png"
  }

  $base = [regex]::Replace($base, "[^A-Za-z0-9]+", "-").Trim("-").ToLowerInvariant()
  if ([string]::IsNullOrWhiteSpace($base)) {
    $base = "image"
  }
  if ($base.Length -gt 70) {
    $base = $base.Substring(0, 70).Trim("-")
  }

  return ("{0:D3}-{1}{2}" -f $Index, $base, $ext)
}

function Add-Replacement {
  param(
    [System.Collections.Generic.List[object]] $Replacements,
    [System.Text.RegularExpressions.Match] $Match,
    [string] $LocalPath
  )

  $title = $Match.Groups["title"].Value
  $replacement = "![{0}]({1}{2})" -f $Match.Groups["alt"].Value, $LocalPath, $title

  $Replacements.Add([PSCustomObject]@{
      Index = $Match.Index
      Length = $Match.Length
      Value = $replacement
    })
}

$downloadCache = @{}
$failures = New-Object System.Collections.Generic.List[string]
$changedFiles = 0
$downloadedFiles = 0

Get-ChildItem -LiteralPath $PostsDir -File -Filter "*.md" | ForEach-Object {
  $postFile = $_
  $text = [System.IO.File]::ReadAllText($postFile.FullName, [System.Text.Encoding]::UTF8)
  $matches = $imagePattern.Matches($text)
  if ($matches.Count -eq 0) {
    return
  }

  $postSlug = Get-PostAssetSlug $postFile
  $postAssetDir = Join-Path $AssetsDir $postSlug
  $replacements = New-Object System.Collections.Generic.List[object]
  $imageIndex = 0

  foreach ($match in $matches) {
    $url = $match.Groups["url"].Value

    if ($downloadCache.ContainsKey($url)) {
      Add-Replacement $replacements $match $downloadCache[$url]
      continue
    }

    $imageIndex++
    $fileName = Get-SafeImageName $url $imageIndex
    $targetPath = Join-Path $postAssetDir $fileName
    $localPath = "/assets/img/posts/$postSlug/$fileName"

    if (-not $DryRun) {
      New-Item -ItemType Directory -Force -Path $postAssetDir | Out-Null

      try {
        try {
          Invoke-WebRequest -Uri $url -Headers $headers -MaximumRedirection 10 -TimeoutSec 60 -OutFile $targetPath
        } catch {
          $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
          if (-not $curl) {
            throw
          }

          & $curl.Source `
            -L `
            --fail `
            --retry 3 `
            --connect-timeout 20 `
            --max-time 120 `
            -A $headers["User-Agent"] `
            -o $targetPath `
            $url | Out-Null

          if ($LASTEXITCODE -ne 0) {
            throw "curl.exe failed with exit code $LASTEXITCODE"
          }
        }

        if (-not (Test-Path -LiteralPath $targetPath) -or (Get-Item -LiteralPath $targetPath).Length -eq 0) {
          throw "Downloaded file is empty"
        }

        $downloadedFiles++
      } catch {
        if (Test-Path -LiteralPath $targetPath) {
          Remove-Item -LiteralPath $targetPath -Force
        }
        $failures.Add("$($postFile.Name): $url - $($_.Exception.Message)")
        continue
      }
    }

    $downloadCache[$url] = $localPath
    Add-Replacement $replacements $match $localPath
  }

  if ($replacements.Count -gt 0) {
    $newText = $text
    foreach ($replacement in ($replacements | Sort-Object Index -Descending)) {
      $newText = $newText.Remove($replacement.Index, $replacement.Length).Insert($replacement.Index, $replacement.Value)
    }

    if ($newText -cne $text) {
      if (-not $DryRun) {
        [System.IO.File]::WriteAllText($postFile.FullName, $newText, $utf8NoBom)
      }
      $changedFiles++
    }
  }
}

Write-Host "Changed post files: $changedFiles"
Write-Host "Downloaded image files: $downloadedFiles"

if ($failures.Count -gt 0) {
  Write-Host "Failures:"
  $failures | ForEach-Object { Write-Host "  $_" }
  exit 1
}

param(
    [string]$Commit = "HEAD",
    [string]$OutDir = "zips"
)

$ErrorActionPreference = "Stop"

if (!(Test-Path ".git")) {
    throw "Not a git repo (missing .git). Run this from your repo root."
}

$repoName = Split-Path -Leaf (Get-Location)

# Resolve commit hash
$hash = (git rev-parse --short $Commit).Trim()
if ([string]::IsNullOrWhiteSpace($hash)) {
    throw "Could not resolve commit: $Commit"
}

if (!(Test-Path $OutDir)) {
    New-Item -ItemType Directory -Path $OutDir | Out-Null
}

$zipName = "$repoName-$hash.zip"
$zipPath = Join-Path $OutDir $zipName

Write-Host "Creating zip for commit $Commit ($hash) => $zipPath"

git archive --format=zip --output="$zipPath" $Commit

Write-Host "Done."

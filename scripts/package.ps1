$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$OutputDir = Join-Path $ProjectRoot "dist"
$BackupPath = Join-Path $OutputDir "omni-erp-assets.zip"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$env:PYTHONPATH = Join-Path $ProjectRoot "src"
python -m omni_erp check --project-root $ProjectRoot
python -m omni_erp package --project-root $ProjectRoot
python -m omni_erp backup --project-root $ProjectRoot --output $BackupPath

Write-Host "Package ready: $BackupPath"

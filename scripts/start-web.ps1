$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$env:PYTHONPATH = Join-Path $ProjectRoot "src"

python -m omni_erp serve --project-root $ProjectRoot --host 127.0.0.1 --port 8765

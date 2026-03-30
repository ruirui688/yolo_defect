$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

& $pythonExe (Join-Path $projectRoot "scripts\prepare_dataset.py") `
    --raw-dir "D:\data_ljl" `
    --output-dir (Join-Path $projectRoot "dataset")

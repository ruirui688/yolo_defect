$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

& $pythonExe (Join-Path $projectRoot "scripts\train.py") `
    --config (Join-Path $projectRoot "configs\train_config.yaml") `
    --data (Join-Path $projectRoot "dataset\data.yaml")

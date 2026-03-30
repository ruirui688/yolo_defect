#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="${1:-defect-yolo}"

if ! command -v conda >/dev/null 2>&1; then
  echo "conda not found in PATH" >&2
  exit 1
fi

eval "$(conda shell.bash hook)"

if conda env list | awk '{print $1}' | grep -Fxq "${ENV_NAME}"; then
  echo "Conda environment already exists: ${ENV_NAME}"
else
  conda env create -n "${ENV_NAME}" -f "${PROJECT_ROOT}/environment.yml"
fi

conda activate "${ENV_NAME}"

python -m pip install --upgrade pip
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
python -m pip install -r "${PROJECT_ROOT}/requirements.txt"

echo "Environment ready: ${ENV_NAME}"
python "${PROJECT_ROOT}/scripts/verify_env.py"

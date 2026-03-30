#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${1:-${PROJECT_ROOT}/dataset}"
CONFIG_PATH="${2:-${PROJECT_ROOT}/configs/train_config.yaml}"

python "${PROJECT_ROOT}/scripts/train.py" \
  --config "${CONFIG_PATH}" \
  --data "${DATA_DIR}/data.yaml"

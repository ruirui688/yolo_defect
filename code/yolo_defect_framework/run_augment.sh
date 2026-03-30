#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATASET_ROOT="${1:-${PROJECT_ROOT}/dataset}"
CONFIG_PATH="${2:-${PROJECT_ROOT}/configs/augment_config.yaml}"

python "${PROJECT_ROOT}/scripts/augment_train_split.py" \
  --dataset-root "${DATASET_ROOT}" \
  --config "${CONFIG_PATH}"

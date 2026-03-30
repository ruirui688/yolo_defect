#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEIGHTS_PATH="${1:-${PROJECT_ROOT}/runs/detect/runs/defect_yolov8m_1536_detect_all/weights/best.pt}"
DATASET_ROOT="${2:-${PROJECT_ROOT}/dataset}"

python "${PROJECT_ROOT}/scripts/evaluate.py" \
  --weights "${WEIGHTS_PATH}" \
  --dataset-root "${DATASET_ROOT}" \
  --split test \
  --gt-mode source_package \
  --pred-mode max_conf

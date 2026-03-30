#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/../.." && pwd)"
SOURCE_PATH="${1:-}"
OUTPUT_DIR="${2:-${REPO_ROOT}/inference_output}"
WEIGHTS_PATH="${3:-${REPO_ROOT}/artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt}"

if [[ -z "${SOURCE_PATH}" ]]; then
  echo "用法: $0 <图片或目录路径> [输出目录] [模型权重路径]" >&2
  exit 1
fi

python "${PROJECT_ROOT}/scripts/infer_directory.py" \
  --weights "${WEIGHTS_PATH}" \
  --source "${SOURCE_PATH}" \
  --output-dir "${OUTPUT_DIR}"


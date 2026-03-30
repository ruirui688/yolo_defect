#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${PROJECT_ROOT}/../.." && pwd)"
ZIP_PATH="${1:-${REPO_ROOT}/raw_data/NoDefectTempSelect.zip}"
OUTPUT_DIR="${2:-${REPO_ROOT}/output/no_defect_eval/NoDefectTempSelect}"
WEIGHTS_PATH="${3:-${REPO_ROOT}/artifacts/final_model/weights/defect_yolov8m_1536_detect_all_best.pt}"

python "${PROJECT_ROOT}/scripts/evaluate_no_defect_zip.py" \
  --weights "${WEIGHTS_PATH}" \
  --zip-path "${ZIP_PATH}" \
  --output-dir "${OUTPUT_DIR}" \
  --save-fp-images

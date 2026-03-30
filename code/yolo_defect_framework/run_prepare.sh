#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAW_DIR="${1:-/data/defect_raw}"
OUTPUT_DIR="${2:-${PROJECT_ROOT}/dataset}"

python "${PROJECT_ROOT}/scripts/prepare_dataset.py" \
  --raw-dir "${RAW_DIR}" \
  --output-dir "${OUTPUT_DIR}"

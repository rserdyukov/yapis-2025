#!/usr/bin/env bash

set -e

# Detect script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"

if [ $# -lt 1 ]; then
  echo "Usage: $(basename "$0") PATH_TO_FILE"
  exit 1
fi

INPUT_PATH="$1"

if [ ! -d "${VENV_DIR}" ]; then
  echo "Virtual environment not found: ${VENV_DIR}. Run build.sh first"
  exit 1
fi

source "${VENV_DIR}/bin/activate"

python "${SCRIPT_DIR}/compiler.py" "${INPUT_PATH}"



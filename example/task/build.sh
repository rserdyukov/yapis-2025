#!/usr/bin/env bash

set -e

# Detect script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/.venv"
REQ_FILE="${SCRIPT_DIR}/requirements.txt"

# Create .venv if missing and install dependencies
if [ ! -d "${VENV_DIR}" ]; then
    python3 -m venv "${VENV_DIR}"

    source "${VENV_DIR}/bin/activate"
    python -m pip install --upgrade pip
    
    if [ -f "${REQ_FILE}" ]; then
        python -m pip install -r "${REQ_FILE}"
    fi
fi



cd "${SCRIPT_DIR}"
antlr -o gen -no-listener -no-visitor example1.g4
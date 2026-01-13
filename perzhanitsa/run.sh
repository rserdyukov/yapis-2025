#!/bin/bash

# Остановить скрипт при любой ошибке
set -e

# Переходим в директорию скрипта
cd "$(dirname "$0")"

# === FIX WINDOWS ENCODING ===
export PYTHONUTF8=1
export PYTHONIOENCODING=utf-8

echo "=== Python Version Check ==="

check_version() {
    $1 -c "import sys; sys.exit(0 if sys.version_info.major == 3 and sys.version_info.minor == 12 else 1)" 2>/dev/null
}

PYTHON_EXEC=""

# Ищем python 3.12
if check_version "python3.12"; then PYTHON_EXEC="python3.12"
elif check_version "python3"; then PYTHON_EXEC="python3"
elif check_version "python"; then PYTHON_EXEC="python"
elif check_version "py -3.12"; then PYTHON_EXEC="py -3.12"
fi

if [ -z "$PYTHON_EXEC" ]; then
    echo "Error: Python 3.12 is required."
    exit 1
fi

echo "Using Python: $PYTHON_EXEC"

echo -e "\n=== Environment Setup ==="

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_EXEC -m venv .venv
fi

# Активация
if [ -f ".venv/bin/activate" ]; then source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then source .venv/Scripts/activate
else
    echo "Error: Could not activate .venv"
    exit 1
fi

# Установка зависимостей (ТЕПЕРЬ С ВЫВОДОМ В КОНСОЛЬ)
REQ_FILE="compiler/requirements.txt"
if [ -f "$REQ_FILE" ]; then
    echo "Installing requirements..."
    # Убрали > /dev/null, чтобы видеть ошибки
    pip install -r "$REQ_FILE"
else
    echo "Warning: $REQ_FILE not found!"
fi

echo -e "\n=== ANTLR4 Generation ==="

COMPILER_DIR="compiler"
GRAMMAR_FILE="$COMPILER_DIR/VecLang.g4"
OUTPUT_DIR="$COMPILER_DIR/generated"

if [ -f "$GRAMMAR_FILE" ]; then
    echo "Found grammar: $GRAMMAR_FILE"
    mkdir -p "$OUTPUT_DIR"
    if [ ! -f "$OUTPUT_DIR/__init__.py" ]; then
        touch "$OUTPUT_DIR/__init__.py"
    fi
    echo "Generating Python files..."
    antlr4 -Dlanguage=Python3 -visitor -no-listener -o "$OUTPUT_DIR" "$GRAMMAR_FILE"
else
    echo "Error: Grammar file $GRAMMAR_FILE not found!"
    exit 1
fi

echo -e "\n=== Running Tests ==="
python run_tests.py
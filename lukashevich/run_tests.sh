#!/bin/bash

# Убедитесь, что скрипт запускается из корневой директории проекта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo "Running compiler on all example files..."

# Ищем все .txt файлы в директории examples
for file in examples/*.txt; do
    if [ -f "$file" ]; then
        echo "----------------------------------------"
        echo "Compiling $file"
        python compiler/main.py "$file"
        if [ $? -eq 0 ]; then
            echo "Successfully compiled $file"
        else
            echo "Error compiling $file"
        fi
    fi
done

echo "----------------------------------------"
echo "All example files processed."
echo "Generated .il files can be found in the current directory."

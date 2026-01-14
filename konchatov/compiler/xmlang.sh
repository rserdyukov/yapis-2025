#!/bin/bash
# quick_compile.sh - простой скрипт для компиляции

if [ $# -eq 0 ]; then
    echo "Использование: $0 <файл.xmlang>"
    echo "Пример: $0 program.xmlang"
    exit 1
fi

INPUT_FILE="$1"
BASE_NAME="${INPUT_FILE%.*}"
OUTPUT_FILE="${BASE_NAME}.pyc"

echo "Компиляция $INPUT_FILE в $OUTPUT_FILE..."

# Проверяем Python
if ! command -v python &> /dev/null; then
    echo "Ошибка: Python не найден"
    exit 1
fi

# Запускаем компилятор
python compiler.py "$INPUT_FILE" -o "$OUTPUT_FILE"

if [ $? -eq 0 ] && [ -f "$OUTPUT_FILE" ]; then
    echo "Успешно создан: $OUTPUT_FILE"
    echo "Размер файла: $(stat -c%s "$OUTPUT_FILE") байт"
else
    echo "Ошибка компиляции"
    exit 1
fi
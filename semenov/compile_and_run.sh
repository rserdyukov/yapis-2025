#!/usr/bin/env bash
set -e

if [ $# -lt 1 ]; then
    echo "Использование: ./compile_and_run.sh <file.txt> [args...]"
    exit 1
fi

INPUT_FILE="$1"
shift
PROGRAM_ARGS="$@"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPILER_DIR="$SCRIPT_DIR/compiler"

detect_platform() {
    case "$OSTYPE" in
        linux*) echo "linux" ;;
        darwin*) echo "osx" ;;
        msys*|cygwin*|win32*) echo "windows" ;;
        *) echo "linux" ;;
    esac
}

PLATFORM=$(detect_platform)

echo "Генерация IL кода..."

INPUT_FILE_ABS="$(cd "$(dirname "$INPUT_FILE")" && pwd)/$(basename "$INPUT_FILE")"

cd "$COMPILER_DIR"
python main.py "$INPUT_FILE_ABS"
cd "$SCRIPT_DIR"

IL_FILE="${INPUT_FILE_ABS%.txt}.il"
EXE_FILE="${INPUT_FILE_ABS%.txt}.exe"
IL_DIR="$(dirname "$IL_FILE")"

if [ ! -f "$IL_FILE" ]; then
    echo "❌ Ошибка: IL файл не был сгенерирован: $IL_FILE"
    exit 1
fi

echo "✓ IL файл создан: $IL_FILE"

find_ilasm() {
    if command -v ilasm &>/dev/null; then
        command -v ilasm
        return
    fi

    if [ "$PLATFORM" = "windows" ]; then
        if [ -f "C:/Program Files/dotnet/packs/Microsoft.NETCore.ILAsm/8.0.0/tools/ilasm.exe" ]; then
            echo "C:/Program Files/dotnet/packs/Microsoft.NETCore.ILAsm/8.0.0/tools/ilasm.exe"
            return
        fi
        
        if command -v dotnet &>/dev/null; then
            NUGET_PACKAGES=$(dotnet nuget locals global-packages --list 2>/dev/null | grep -i "global-packages" | sed 's/.*global-packages: *//' | tr -d '\r' || echo "$HOME/.nuget/packages")
            NUGET_PACKAGES="${NUGET_PACKAGES:-$HOME/.nuget/packages}"
            
            ILASM_FOUND=$(find "$NUGET_PACKAGES" -type f -name "ilasm.exe" -ipath "*microsoft*netcore*ilasm*" 2>/dev/null | head -1)
            if [ -n "$ILASM_FOUND" ]; then
                echo "$ILASM_FOUND"
                return
            fi
        fi
    else
        if [ -f "/usr/share/dotnet/packs/Microsoft.NETCore.ILAsm/8.0.0/tools/ilasm" ]; then
            echo "/usr/share/dotnet/packs/Microsoft.NETCore.ILAsm/8.0.0/tools/ilasm"
            return
        fi
        
        if command -v dotnet &>/dev/null; then
            NUGET_PACKAGES=$(dotnet nuget locals global-packages --list 2>/dev/null | grep -i "global-packages" | sed 's/.*global-packages: *//' | tr -d '\r' || echo "$HOME/.nuget/packages")
            NUGET_PACKAGES="${NUGET_PACKAGES:-$HOME/.nuget/packages}"
            
            ILASM_FOUND=$(find "$NUGET_PACKAGES" -type f -name "ilasm" -ipath "*microsoft*netcore*ilasm*" 2>/dev/null | head -1)
            if [ -n "$ILASM_FOUND" ]; then
                echo "$ILASM_FOUND"
                return
            fi
        fi
    fi

    echo ""
}

ILASM_SOURCE=$(find_ilasm)

if [ -z "$ILASM_SOURCE" ]; then
    echo "❌ Не удалось найти ilasm для .NET 8.0"
    echo "Попробуйте установить: dotnet tool install -g ilasm"
    echo "Или установите .NET 8.0 SDK"
    exit 1
fi

echo "Найден ilasm: $ILASM_SOURCE"

if [ "$PLATFORM" = "windows" ]; then
    ILASM_LOCAL="$SCRIPT_DIR/ilasm.exe"
else
    ILASM_LOCAL="$SCRIPT_DIR/ilasm"
fi

echo "Копируем ilasm в: $ILASM_LOCAL"
cp "$ILASM_SOURCE" "$ILASM_LOCAL"
chmod +x "$ILASM_LOCAL" 2>/dev/null || true

echo "✓ ilasm скопирован: $ILASM_LOCAL"

echo "Компиляция IL файла..."

cd "$IL_DIR"

IL_FILE_NAME="$(basename "$IL_FILE")"
EXE_FILE_NAME="$(basename "$EXE_FILE")"

cd "$IL_DIR"

if [ "$PLATFORM" = "windows" ]; then
    ILASM_REL=$(python -c "import os; print(os.path.relpath('$ILASM_LOCAL', '$IL_DIR'))" 2>/dev/null || echo "$ILASM_LOCAL")
    
    echo "Запуск: $ILASM_REL /output:$EXE_FILE_NAME $IL_FILE_NAME"
    "$ILASM_REL" "/output:$EXE_FILE_NAME" "$IL_FILE_NAME"
    COMPILE_EXIT_CODE=$?
else
    ILASM_REL=$(python -c "import os; print(os.path.relpath('$ILASM_LOCAL', '$IL_DIR'))" 2>/dev/null || echo "$ILASM_LOCAL")
    "$ILASM_REL" "$IL_FILE_NAME" -output:"$EXE_FILE_NAME" -exe
    COMPILE_EXIT_CODE=$?
fi

if [ -f "$EXE_FILE_NAME" ]; then
    EXE_FILE="$IL_DIR/$EXE_FILE_NAME"
    echo "✓ Исполняемый файл создан: $EXE_FILE"
    if [ $COMPILE_EXIT_CODE -ne 0 ]; then
        echo "⚠️  ilasm завершился с кодом $COMPILE_EXIT_CODE, но .exe файл был создан. Продолжаем..."
        COMPILE_EXIT_CODE=0
    fi
elif [ -f "$EXE_FILE" ]; then
    echo "✓ Исполняемый файл создан: $EXE_FILE"
    if [ $COMPILE_EXIT_CODE -ne 0 ]; then
        echo "⚠️  ilasm завершился с кодом $COMPILE_EXIT_CODE, но .exe файл был создан. Продолжаем..."
        COMPILE_EXIT_CODE=0
    fi
else
    echo "❌ Ошибка: исполняемый файл не был создан"
    echo "Проверяем текущую директорию: $(pwd)"
    echo "Файлы в директории:"
    ls -la *.exe 2>/dev/null || echo "Нет .exe файлов"
    if [ $COMPILE_EXIT_CODE -ne 0 ]; then
        echo "❌ Ошибка компиляции IL файла (код возврата: $COMPILE_EXIT_CODE)"
        exit 1
    else
        echo "❌ ilasm завершился без ошибок, но .exe файл не найден"
        exit 1
    fi
fi

echo "Запуск программы..."

./"$EXE_FILE_NAME" $PROGRAM_ARGS

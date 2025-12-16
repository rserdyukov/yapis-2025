#!/bin/bash

# Остановка скрипта при любой ошибке
set -e

echo "=== 1. Starting Build Process ==="

# Проверка, установлена ли Java (она нужна и для Maven Wrapper, и для запуска)
if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed or not in PATH."
    exit 1
fi

# Заходим в папку проекта
cd compiler

# Даем права на выполнение врапперу (на всякий случай)
chmod +x mvnw

echo "=== 2. Running Maven Build (using Wrapper) ==="
# Используем ./mvnw вместо mvn
./mvnw clean package

# Возвращаемся в корень
cd ..

# Имя JAR файла (как мы настроили в pom.xml)
JAR_NAME="mclc.jar"
SOURCE_JAR="compiler/target/$JAR_NAME"

if [ -f "$SOURCE_JAR" ]; then
    echo "=== 3. Moving JAR to root ==="
    cp "$SOURCE_JAR" .
    echo "Copied $JAR_NAME to root."
else
    echo "Error: JAR file not found at $SOURCE_JAR"
    exit 1
fi

echo "=== 4. Creating launcher script 'mcl' ==="
# Создаем скрипт-обертку
echo '#!/bin/bash' > mcl
echo 'java -jar "$(dirname "$0")/'"$JAR_NAME"'" "$@"' >> mcl
chmod +x mcl

echo "========================================="
echo "BUILD SUCCESSFUL!"
echo "You can now run the compiler using:"
echo "./mcl examples"
echo "========================================="
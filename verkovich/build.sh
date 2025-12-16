#!/bin/bash
set -e

echo "=== 1. Starting Build Process ==="

if ! command -v java &> /dev/null; then
    echo "Error: Java is not installed."
    exit 1
fi

cd compiler
chmod +x mvnw
echo ">> Building JAR..."
./mvnw clean package -DskipTests
cd ..

JAR_NAME="mclc.jar"
SOURCE_JAR="compiler/target/$JAR_NAME"

if [ -f "$SOURCE_JAR" ]; then
    cp "$SOURCE_JAR" .
    echo ">> Copied $JAR_NAME to root."
else
    echo "Error: JAR file not found at $SOURCE_JAR"
    exit 1
fi

echo "=== 2. Setting up Python Environment ==="

VENV_DIR=".venv"

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "Error: Python is not installed."
        exit 1
    fi
fi

if [ ! -d "$VENV_DIR" ]; then
    echo ">> Creating virtual environment in $VENV_DIR..."
    $PYTHON_CMD -m venv $VENV_DIR
else
    echo ">> Virtual environment already exists."
fi


if [ -d "$VENV_DIR/Scripts" ]; then
    PIP_CMD="./$VENV_DIR/Scripts/pip"
    PYTHON_REL_PATH="/.venv/Scripts/python"
else
    PIP_CMD="./$VENV_DIR/bin/pip"
    PYTHON_REL_PATH="/.venv/bin/python"
fi
# --------------------------

echo ">> Installing 'bytecode' library..."
"$PIP_CMD" install bytecode > /dev/null

echo "=== 3. Creating launcher script 'mcl' ==="
echo '#!/bin/bash' > mc
echo 'DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"' >> mcl
echo "PYTHON_EXEC=\"\$DIR$PYTHON_REL_PATH\"" >> mcl
echo 'java -Dpython.exec="$PYTHON_EXEC" -jar "$DIR/'"$JAR_NAME"'" "$@"' >> mcl
chmod +x mcl

echo "========================================="
echo "BUILD SUCCESSFUL!"
echo "Run: ./mcl examples/"
echo "========================================="
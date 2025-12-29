@echo off
echo === 1. Starting Build Process ===

where java >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Java is not installed.
    pause
    exit /b 1
)

cd compiler
echo >> Building JAR...
call mvnw.cmd clean package -DskipTests
if %errorlevel% neq 0 (
    echo Build failed.
    cd ..
    pause
    exit /b 1
)
cd ..

set JAR_NAME=mclc.jar
set SOURCE_JAR=compiler\target\%JAR_NAME%

if exist "%SOURCE_JAR%" (
    copy /Y "%SOURCE_JAR%" . >nul
    echo >> Copied %JAR_NAME% to root.
) else (
    echo Error: JAR not found.
    pause
    exit /b 1
)

echo === 2. Setting up Python Environment ===
set VENV_DIR=.venv

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Python is not installed.
    pause
    exit /b 1
)

if not exist "%VENV_DIR%" (
    echo >> Creating virtual environment...
    python -m venv %VENV_DIR%
) else (
    echo >> Virtual environment exists.
)

echo >> Installing 'bytecode' library...
call %VENV_DIR%\Scripts\pip.exe install bytecode >nul

echo === 3. Creating launcher script 'mcl.bat' ===
echo @echo off > mcl.bat

echo set DIR=%%~dp0 >> mcl.bat
echo set PYTHON_EXEC=%%DIR%%.venv\Scripts\python.exe >> mcl.bat
echo java -Dpython.exec="%%PYTHON_EXEC%%" -jar "%%DIR%%%JAR_NAME%" %%* >> mcl.bat

echo =========================================
echo BUILD SUCCESSFUL!
echo Dependencies installed in .venv/
echo Run: mcl examples\test.mcl
echo =========================================
pause
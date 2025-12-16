@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
    echo Usage: run_compiler.bat source_file.txt
    exit /b 1
)

set SOURCE=%~1
set JASMIN_JAR=jasmin.jar
set OUTPUT_DIR=output
set OUTPUT_J=%OUTPUT_DIR%\%~n1.j
set MAIN_CLASS=StringLang

if not exist %OUTPUT_DIR% mkdir %OUTPUT_DIR%

python code_gen_main.py %SOURCE% %OUTPUT_J%
if errorlevel 1 exit /b 1

java -jar %JASMIN_JAR% -d %OUTPUT_DIR% %OUTPUT_J%
if errorlevel 1 exit /b 1

javac -d %OUTPUT_DIR% StringLangRuntime.java
if errorlevel 1 exit /b 1

java -cp %OUTPUT_DIR% %MAIN_CLASS%

endlocal

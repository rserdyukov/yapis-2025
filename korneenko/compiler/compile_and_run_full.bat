@echo off
REM Полный цикл: компиляция исходника в LLVM IR, затем в exe и запуск
REM Использование: compile_and_run_full.bat <путь_к_исходнику.txt>

if "%~1"=="" (
    echo Использование: compile_and_run_full.bat ^<путь_к_исходнику.txt^>
    echo Пример: compile_and_run_full.bat examples\1_yapis.txt
    exit /b 1
)

set SOURCE_FILE=%~1
set BASE_NAME=%~n1
set LL_FILE=%BASE_NAME%.ll
set EXE_NAME=%BASE_NAME%.exe

REM Проверяем существование исходного файла
if not exist "%SOURCE_FILE%" (
    echo Ошибка: файл "%SOURCE_FILE%" не найден
    exit /b 1
)

echo ========================================
echo КОМПИЛЯЦИЯ ИСХОДНИКА В LLVM IR
echo ========================================
echo.

REM Компилируем исходник в LLVM IR
python main.py "%SOURCE_FILE%"
if %ERRORLEVEL% NEQ 0 (
    echo Ошибка при компиляции в LLVM IR
    exit /b 1
)

if not exist "%LL_FILE%" (
    echo Ошибка: LLVM IR файл "%LL_FILE%" не был создан
    exit /b 1
)

echo [OK] LLVM IR создан: %LL_FILE%
echo.

REM Компилируем LLVM IR в exe
call compile_llvm.bat "%LL_FILE%"
if %ERRORLEVEL% NEQ 0 (
    exit /b 1
)

echo.
echo ========================================
echo ЗАПУСК ПРОГРАММЫ
echo ========================================
echo.

REM Запускаем
call run_llvm_exe.bat "%EXE_NAME%"
set EXIT_CODE=%ERRORLEVEL%

exit /b %EXIT_CODE%


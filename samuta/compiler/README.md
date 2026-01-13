## Требования для запуска
- Java 17
- Gradle (использовать wrapper, который лежит в исходном коде)
- Bash-совместимая среда — Git Bash / WSL / Linux / macOS
- LLVM/Clang — для компиляции program.ll
- MinGW (GCC) — для компиляции runtime.c и линковки (gcc)
  Путь задаётся в скрипте build_and_run.sh в переменной MINGW_PATH.

## Сборка и запуск
Весь процесс сборки и запуска теперь выполняется с помощью одного скрипта.
1. Сделать скрипт исполняемым:
```bash
chmod +x build_and_run.sh
```
2. Запустить скрипт:
```bash
./build_and_run.sh path/to/file.gsl
```
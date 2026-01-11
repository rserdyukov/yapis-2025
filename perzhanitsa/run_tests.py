import os
import subprocess
import sys

# Настройки путей
# Определяем абсолютный путь к папке, где лежит этот скрипт
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Путь к ассемблеру
COMPILER_SCRIPT = os.path.join(BASE_DIR, 'compiler', 'main.py')

# Путь к папке с примерами
EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples')


def main():
    # 1. Проверяем наличие необходимых путей
    if not os.path.exists(COMPILER_SCRIPT):
        print(f"Ошибка: Не найден файл ассемблера по пути: {COMPILER_SCRIPT}")
        return

    if not os.path.exists(EXAMPLES_DIR):
        print(f"Ошибка: Не найдена папка с примерами: {EXAMPLES_DIR}")
        return

    # 2. Получаем список всех .vec файлов
    vec_files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith('.vec')]

    # Сортируем, чтобы запускались по порядку (например, example1, example2...)
    vec_files.sort()

    if not vec_files:
        print("В папке 'example' не найдено файлов с расширением .vec")
        return

    print(f"Найдено {len(vec_files)} тестов. Запуск...\n")

    # 3. Проходим по каждому файлу и запускаем его
    for i, filename in enumerate(vec_files, 1):
        filepath = os.path.join(EXAMPLES_DIR, filename)

        print("=" * 60)
        print(f"TEST #{i}: {filename}")
        print("=" * 60)

        try:
            # Запускаем assembler.py через subprocess
            # input="0\n" передается на случай, если в тесте есть вызов read(), чтобы он не завис
            result = subprocess.run(
                [sys.executable, COMPILER_SCRIPT, filepath],
                capture_output=True,
                text=True,
                encoding='utf-8',
                input="[0,0]\n"
            )

            # Вывод STDOUT (то, что программа пишет в консоль)
            if result.stdout:
                print(result.stdout)

            # Вывод STDERR (ошибки Python, если упал сам компилятор)
            if result.stderr:
                print("--- STDERR ---")
                print(result.stderr)

            # Анализ кода возврата
            if result.returncode == 0:
                print(f"Тест завершен (Exit Code: 0)")
            else:
                # Для тестов с ошибками (Semantic Error) это нормальное поведение
                print(f"Тест завершен с кодом {result.returncode} (Ожидалась ошибка?)")

        except Exception as e:
            print(f" Критическая ошибка при запуске теста: {e}")

        print("\n")

    print("Все тесты выполнены.")


if __name__ == "__main__":
    main()
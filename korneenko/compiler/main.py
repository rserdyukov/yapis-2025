import sys
import os
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from antlr4.tree.Tree import ParseTreeWalker

# --- гарантируем, что Python видит папку gen ---
sys.path.append(os.path.join(os.path.dirname(__file__), "gen"))

from gen.gsl1Lexer import gsl1Lexer
from gen.gsl1Parser import gsl1Parser
from semantic_analyzer import SemanticAnalyzer


# --- Кастомный обработчик ошибок ---
class VerboseErrorListener(ErrorListener):
    """Красивый вывод ошибок парсинга"""

    def __init__(self):
        super(VerboseErrorListener, self).__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error = f"Ошибка в строке {line}, позиция {column}: {msg}"
        self.errors.append(error)
        print(error)


def main(argv):
    if len(argv) < 2:
        print("Использование: python main.py <путь_к_файлу>")
        return

    input_file = argv[1]
    if not os.path.exists(input_file):
        print(f"Файл '{input_file}' не найден.")
        return

    # --- Загружаем исходный код ---
    input_stream = FileStream(input_file, encoding="utf-8")

    # --- Создаём лексер и парсер ---
    lexer = gsl1Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = gsl1Parser(stream)

    # --- Убираем стандартные слушатели ошибок ---
    lexer.removeErrorListeners()
    parser.removeErrorListeners()

    # --- Подключаем наш VerboseErrorListener ---
    error_listener = VerboseErrorListener()
    lexer.addErrorListener(error_listener)
    parser.addErrorListener(error_listener)

    # --- Запускаем парсинг ---
    tree = parser.program()

    # --- Результат синтаксического анализа ---
    if error_listener.errors:
        print("\nСинтаксический анализ завершён с ошибками.")
        return
    else:
        print("Синтаксический анализ успешно завершён, ошибок не обнаружено.")
    
    # --- Запускаем семантический анализ ---
    print("\n=== Семантический анализ ===")
    semantic_analyzer = SemanticAnalyzer()
    walker = ParseTreeWalker()
    walker.walk(semantic_analyzer, tree)
    
    # --- Результат семантического анализа ---
    if semantic_analyzer.errors:
        print(f"\nСемантический анализ завершён с {len(semantic_analyzer.errors)} ошибкой(ами).")
    else:
        print("Семантический анализ успешно завершён, ошибок не обнаружено.")


if __name__ == "__main__":
    main(sys.argv)

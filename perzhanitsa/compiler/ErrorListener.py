import sys
from antlr4 import *
from generated.VecLangParser import VecLangParser
from generated.VecLangLexer import VecLangLexer
from antlr4.error.ErrorListener import ErrorListener
from SemanticAnalyzer import *


class SyntaxError(ErrorListener):
    def __init__(self):
        # 1. Инициализируем список для хранения ошибок
        self.errors = []

    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        token_text = offending_symbol.text if offending_symbol else "<unknown>"
        error_message = f"Line {line} : {token_text} {msg}"
        # 2. Добавляем ошибку в список
        self.errors.append(error_message)


def parse_file(filename):
    input_stream = FileStream(filename, encoding='utf-8')
    lexer = VecLangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = VecLangParser(stream)

    parser.removeErrorListeners()
    parser.addErrorListener(SyntaxError())

    # Получаем дерево разбора
    tree = parser.program()

    # Запускаем семантический анализ
    print("\n" + "=" * 50)
    print("Запуск семантического анализа...")

    analyzer = SemanticAnalyzer()
    analyzer.visit(tree)

    if analyzer.errors:
        print(f"\nОбнаружено {len(analyzer.errors)} семантических ошибок:")
        for error in analyzer.errors:
            print(f"  {error}")
        return False
    else:
        print("\n✓ Семантический анализ пройден успешно!")
        print("✓ Программа корректна!")
        return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Try again")
        sys.exit(1)

    parse_file(sys.argv[1])

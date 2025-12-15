import sys

from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

from SemanticAnalyzer import SemanticAnalyzer
from gen.langLexer import langLexer
from gen.langParser import langParser


class VerboseErrorListener(ErrorListener):
    """Кастомный обработчик ошибок для красивого вывода"""

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

    input_stream = FileStream(input_file, encoding='utf-8')

    lexer = langLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = langParser(stream)

    parser.removeErrorListeners()
    lexer.removeErrorListeners()

    error_listener = VerboseErrorListener()
    parser.addErrorListener(error_listener)
    lexer.addErrorListener(error_listener)

    tree = parser.program()

    analyzer = SemanticAnalyzer()
    errors = analyzer.visit(tree)

    if errors:
        print("\nСемантические ошибки:")
        for e in errors:
            print("  -", e)


if __name__ == "__main__":
    main(sys.argv)

import sys
from antlr4 import CommonTokenStream, FileStream
from antlr4.error.ErrorListener import ErrorListener

from gen.yapis2Lexer import yapis2Lexer
from gen.yapis2Parser import yapis2Parser
from SemanticAnalyzer import SemanticAnalyzer


class VerboseErrorListener(ErrorListener):

    def __init__(self):
        super().__init__()
        self.errors = []
        self.lines_reported = set()
        self.max_errors = 8

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if len(self.errors) >= self.max_errors:
            return
        if line in self.lines_reported:
            return
        self.lines_reported.add(line)
        error = f"Ошибка в строке {line}, позиция {column}: {msg}"
        self.errors.append(error)
        print(error)


def parse_file(path: str):
    input_stream = FileStream(path, encoding="utf-8")

    lexer = yapis2Lexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = yapis2Parser(tokens)

    lexer.removeErrorListeners()
    parser.removeErrorListeners()
    listener = VerboseErrorListener()
    lexer.addErrorListener(listener)
    parser.addErrorListener(listener)

    tree = parser.program()
    return tree, listener.errors


def main(argv):
    if len(argv) < 2:
        print("Использование: python main.py <путь_к_файлу>")
        return

    path = argv[1]
    tree, syntax_errors = parse_file(path)
    if syntax_errors:
        print("\nСинтаксический разбор завершён с ошибками (семантика не выполнялась).")
        return
    else:
        print("Синтаксических ошибок не обнаружено")

    analyzer = SemanticAnalyzer()
    sem_errors = analyzer.visit(tree)

    if sem_errors:
        print("\nСемантические ошибки:")
        for e in sem_errors:
            print("  -", e)
    else:
        print("Семантических ошибок не обнаружено")


if __name__ == "__main__":
    main(sys.argv)


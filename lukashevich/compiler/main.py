from antlr4 import *
from parser_code.ExprLexer import ExprLexer
from parser_code.ExprParser import ExprParser
from antlr4.error.ErrorListener import ErrorListener
import sys
import os


class VerboseErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"Синтаксическая ошибка: строка {line}, позиция {column}: {msg}")


def syntax_analyze(filename: str):
    input_stream = FileStream(filename)
    lexer = ExprLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(VerboseErrorListener())

    token_stream = CommonTokenStream(lexer)
    parser = ExprParser(token_stream)
    parser.removeErrorListeners()
    parser.addErrorListener(VerboseErrorListener())

    tree = parser.program()
    return tree


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Укажите путь к файлу")
        sys.exit(1)
    filepath = sys.argv[1]
    if not os.path.isfile(filepath):
        print(f"Файл не найден: {filepath}")
        sys.exit(1)
    try:
        tree = syntax_analyze(filepath)
        print("OK")
        print(tree.toStringTree(recog=None))
    except SyntaxError as e:
        print(f"ERROR: {e}")

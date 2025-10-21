import sys
from antlr4 import *
from StringLangLexer import StringLangLexer
from StringLangParser import StringLangParser
from antlr4.error.ErrorListener import ErrorListener


class SyntaxErrorPrinter(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        token_text = offendingSymbol.text if offendingSymbol else "<неизвестно>"
        print(f"Ошибка синтаксиса в строке {line}, столбце {column}: неожиданный токен '{token_text}'. {msg}")


def parse_file(filename):
    input_stream = FileStream(filename, encoding='utf-8')
    lexer = StringLangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = StringLangParser(stream)

    parser.removeErrorListeners()
    parser.addErrorListener(SyntaxErrorPrinter())

    parser.program()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Попробуйте заново")
        sys.exit(1)

    parse_file(sys.argv[1])


# python syntax_parser.py D:\yapis-2025\gordeyuk\examples\error_example_1.txt
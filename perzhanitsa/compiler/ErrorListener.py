#Syntax analyzer

import sys
from antlr4 import *
from VecLangParser import VecLangParser
from VecLangLexer import VecLangLexer
from antlr4.error.ErrorListener import ErrorListener


class SyntaxError(ErrorListener):
    def syntaxError(self, recognizer, offending_symbol, line, column, msg, e):
        token_text = offending_symbol.text if offending_symbol else "<unknown>"
        print(f"Syntax error at line {line} and column {column}: {token_text}. {msg}")


def parse_file(filename):
    input_stream = FileStream(filename, encoding='utf-8')
    lexer = VecLangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = VecLangParser(stream)

    parser.removeErrorListeners()
    parser.addErrorListener(SyntaxError())

    parser.program()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Try again")
        sys.exit(1)

    parse_file(sys.argv[1])

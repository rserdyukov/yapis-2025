import sys
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

from gen.example1Parser import example1Parser
from gen.example1Lexer import example1Lexer


class CustomErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"Error {line}:{column} - {msg}")


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = example1Lexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(CustomErrorListener())
    stream = CommonTokenStream(lexer)
    parser = example1Parser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(CustomErrorListener())
    parser.program()
    if len(parser.errors) > 0:
        print("Errors:")
        print(parser.errors)
    print("Names table:")
    print(parser.names)
    print("Codes table:")
    for code in parser.codes:
        print(code)

if __name__ == '__main__':
    main(sys.argv)

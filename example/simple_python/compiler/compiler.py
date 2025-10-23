import sys
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener

from generated.SimplePythonParser import SimplePythonParser
from generated.SimplePythonLexer import SimplePythonLexer


class CustomErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"Error {line}:{column} - {msg}")



def main(argv):
    input_stream = FileStream(argv[1])
    lexer = SimplePythonLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(CustomErrorListener())
    stream = CommonTokenStream(lexer)
    parser = SimplePythonParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(CustomErrorListener())
    parser.program()

if __name__ == '__main__':
    main(sys.argv)
    
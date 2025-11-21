import sys

from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from antlr_generated import GrammarMathPLLexer, GrammarMathPLParser


class MathPLErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_message = f"ERROR on line {line}:{column} -> {msg}"
        self.errors.append(error_message)


def main(argv):
    if len(argv) < 2:
        print("Usage: python main.py <path_to_source_file>")
        sys.exit(1)

    input_file = argv[1]

    try:
        input_stream = FileStream(input_file, encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: File not found at '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    error_listener = MathPLErrorListener()

    lexer = GrammarMathPLLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    stream = CommonTokenStream(lexer)

    parser = GrammarMathPLParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    print(f"Starting syntax check for: {input_file}")

    try:
        tree = parser.program()
    except Exception as e:
        print(f"A critical parsing error occurred: {e}")
        sys.exit(1)

    if error_listener.errors:
        print("\nSyntax check failed. Errors found:")
        for error in error_listener.errors:
            print(error)
        sys.exit(1)
    else:
        print("\nSyntax check successful. No errors found.")
        sys.exit(0)


if __name__ == '__main__':
    main(sys.argv)
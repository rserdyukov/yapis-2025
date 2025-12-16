import sys
from antlr4 import *

from gen.example1Parser import example1Parser
from gen.example1Lexer import example1Lexer


def main(argv):
    input_stream = FileStream(argv[1])
    lexer = example1Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = example1Parser(stream)
    parser.program()
    if len(parser.errors) > 0:
        print("Errors:")
        print(parser.errors)
    print("Names table:")
    print(parser.names)
    print("Consts table:")
    for const in parser.consts:
        print(const)
    print("Codes table:")
    for code in parser.codes:
        print(code)

if __name__ == '__main__':
    main(sys.argv)

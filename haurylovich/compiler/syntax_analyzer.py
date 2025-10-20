from antlr4 import FileStream, CommonTokenStream, InputStream
from SetLangLexer import SetLangLexer
from SetLangParser import SetLangParser
from antlr4.error.ErrorListener import ErrorListener
import sys
import os
class VerboseErrorListener(ErrorListener):
    def __init__(self):
        super(VerboseErrorListener, self).__init__()
        self.errors = []
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxError(f"Syntax error at {line}:{column}: {msg}")

def parse_from_file(file):
    input_stream = FileStream(file, encoding='utf-8')
    lexer = SetLangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = SetLangParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(VerboseErrorListener())
    parser.program()
    tree = parser.program()
    return tree

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Укажите путь к файлу")
        sys.exit(1)
    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Файл не найден: {file_path}")
        sys.exit(1)
    try:
        tree = parse_from_file(file_path)
        print("OK")
        print(tree.toStringTree(recog=None))
    except SyntaxError as e:
        print(f"ERROR: {e}")



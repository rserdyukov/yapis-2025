import sys
import os
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from antlr4.tree.Tree import ParseTreeWalker


sys.path.append(os.path.join(os.path.dirname(__file__), "gen"))

from gen.gsl1Lexer import gsl1Lexer
from gen.gsl1Parser import gsl1Parser
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator


# --- Кастомный обработчик ошибок ---
class VerboseErrorListener(ErrorListener):
    """Красивый вывод ошибок парсинга"""

    def __init__(self):
        super(VerboseErrorListener, self).__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error = f"Error at line {line}, position {column}: {msg}"
        self.errors.append(error)
        print(error)


def main(argv):
    if len(argv) < 2:
        print("Usage: python main.py <file_path>")
        return

    input_file = argv[1]
    if not os.path.exists(input_file):
        print(f"File '{input_file}' not found.")
        return

    # --- Загружаем исходный код ---
    input_stream = FileStream(input_file, encoding="utf-8")

    # --- Создаём лексер и парсер ---
    lexer = gsl1Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = gsl1Parser(stream)

    # --- Убираем стандартные слушатели ошибок ---
    lexer.removeErrorListeners()
    parser.removeErrorListeners()

    # --- Подключаем наш VerboseErrorListener ---
    error_listener = VerboseErrorListener()
    lexer.addErrorListener(error_listener)
    parser.addErrorListener(error_listener)

    # --- Запускаем парсинг ---
    tree = parser.program()

    # --- Результат синтаксического анализа ---
    if error_listener.errors:
        print("\nSyntax analysis completed with errors.")
        return
    else:
        print("Syntax analysis completed successfully, no errors found.")
    
    # --- Запускаем семантический анализ ---
    semantic_analyzer = SemanticAnalyzer()
    walker = ParseTreeWalker()
    walker.walk(semantic_analyzer, tree)
    
    # --- Результат семантического анализа ---
    # Выводим ошибки только если они есть и если они критичны
    # (для некритичных ошибок не выводим, чтобы не засорять вывод)

    # --- Генерация LLVM IR ---
    codegen = CodeGenerator()
    llvm_ir = codegen.generate(tree)

    out_file = os.path.splitext(input_file)[0] + ".ll"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(llvm_ir)


if __name__ == "__main__":
    main(sys.argv)

import sys
from antlr4 import CommonTokenStream, FileStream
from antlr4.error.ErrorListener import ErrorListener

from gen.yapis2Lexer import yapis2Lexer
from gen.yapis2IndentLexer import yapis2IndentLexer
from gen.yapis2Parser import yapis2Parser
from SemanticAnalyzer import SemanticAnalyzer
from Compiler import Compiler


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

    lexer = yapis2IndentLexer(input_stream)
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
        print("Использование: python main.py <путь_к_файлу> [--compile]")
        return

    path = argv[1]
    compile_mode = len(argv) > 2 and argv[2] == "--compile"

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
        if compile_mode:
            print("\nКомпиляция пропущена из-за семантических ошибок.")
        return
    else:
        print("Семантических ошибок не обнаружено")

    if compile_mode:
        print("\nКомпиляция в байт-код JVM...")
        compiler = Compiler()
        compiler.source_file_path = path
        jasmin_code = compiler.visitProgram(tree)

        if jasmin_code is None:
            print("ERROR: visitProgram returned None!")
            return 1

        import os
        base_name = os.path.splitext(os.path.basename(path))[0]
        output_file = f"{base_name}.j"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(jasmin_code)
        print(f"Сгенерирован файл: {output_file}")
        print("\nДля компиляции в .class файл используйте:")
        print(f"  jasmin {output_file}")
        print(f"  java Main")
        return 0


if __name__ == "__main__":
    main(sys.argv)

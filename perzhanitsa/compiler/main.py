# assembler.py
import os
import runpy
import sys
import traceback
import importlib.util
import struct
import time
import marshal
import dis

from antlr4 import *

# === ИМПОРТЫ ВАШИХ МОДУЛЕЙ ===
try:
    from ErrorListener import SyntaxError
    from SemanticAnalyzer import SemanticAnalyzer
    from Runtime import get_env
    from Compiler import CompilerVisitor
except ImportError as e:
    print(f"Ошибка при импорте модулей: {e}")
    sys.exit(1)

# Проверка версии Python
if sys.version_info < (3, 11):
    raise RuntimeError("This assembler requires Python 3.11+")

try:
    from generated.VecLangLexer import VecLangLexer
    from generated.VecLangParser import VecLangParser
except ImportError:
    print("Error: Could not find generated ANTLR4 parser files.")
    sys.exit(1)


def save_to_pyc(code_obj, filename):
    with open(filename, 'wb') as f:
        f.write(importlib.util.MAGIC_NUMBER)
        f.write(struct.pack('<I', 0))
        f.write(struct.pack('<I', int(time.time())))
        f.write(struct.pack('<I', 0))
        marshal.dump(code_obj, f)
    print(f"--- Bytecode saved to {filename} ---")


def run_file(filepath):
    print(f"--- Processing {filepath} ---")

    input_stream = FileStream(filepath, encoding='utf-8')
    lexer = VecLangLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = VecLangParser(stream)

    # 1. SYNTAX
    print("--- Analysis ---")
    parser.removeErrorListeners()
    syntax_listener = SyntaxError()
    parser.addErrorListener(syntax_listener)
    tree = parser.program()

    if syntax_listener.errors:
        for err in syntax_listener.errors: print(err)
        return

    # 2. SEMANTIC
    semantic_analyzer = SemanticAnalyzer()
    semantic_analyzer.visit(tree)
    if semantic_analyzer.errors:
        for err in semantic_analyzer.errors: print(f"Line {err['line']}: {err['msg']}")
        return
    else:
        print("analysis passed.")

    # 3. COMPILATION
    print("--- Compilation ---")
    compiler = CompilerVisitor()
    try:
        code_obj = compiler.compile(tree, filepath)
    except Exception:
        print("\n!!! COMPILATION FAILURE !!!")
        traceback.print_exc()
        return
    # print("\n--- Bytecode Disassembly ---")
    #
    # # 1. Выводит метаданные: имена переменных, константы, размер стека и т.д.
    # dis.show_code(code_obj)
    #
    # print("")
    #
    # # 2. Выводит сами инструкции (opcode, аргументы) в читаемом виде
    # dis.dis(code_obj)
    #
    # print("----------------------------\n")
    abs_filepath = os.path.abspath(filepath)
    source_dir = os.path.dirname(abs_filepath)
    base_filename = os.path.basename(abs_filepath)

    # 2. Определяем имя папки для бинарников (стандартно __pycache__)
    cache_dir = os.path.join(source_dir, "__pycache__")

    # 3. Создаем папку, если её нет
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # 4. Формируем итоговый путь: .../example/__pycache__/example1.vec.pyc
    pyc_filename = os.path.join(cache_dir, base_filename + ".pyc")

    save_to_pyc(code_obj, pyc_filename)

    # 4. EXECUTION
    print(f"\n---  Execution ({pyc_filename}) ---")
    env = get_env()
    try:
        runpy.run_path(pyc_filename, init_globals=env, run_name="__main__")
    except Exception as e:
        traceback.print_exc()
        print(f"Runtime Error: {e}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <source_file.vec>")
    else:
        run_file(sys.argv[1])
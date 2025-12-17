

import sys
import os
import subprocess
from pathlib import Path

try:
    from antlr4 import CommonTokenStream, FileStream
except ImportError:
    print("Модуль antlr4 не найден. Установка...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "antlr4-python3-runtime", "-q"])
        print("✓ Зависимости установлены")
        from antlr4 import CommonTokenStream, FileStream
    except Exception as e:
        print("Установите вручную: pip install antlr4-python3-runtime")
        sys.exit(1)

script_dir = Path(__file__).parent.absolute()

if (script_dir / "Compiler.py").exists():
    compiler_dir = script_dir
    os.chdir(compiler_dir)
    sys.path.insert(0, str(compiler_dir))
    project_root = script_dir.parent
else:
    compiler_dir = script_dir / "compiler"
    if not compiler_dir.exists():
        print("Запустите скрипт из корня проекта или из папки compiler")
        sys.exit(1)
    os.chdir(compiler_dir)
    sys.path.insert(0, str(compiler_dir))
    project_root = script_dir

try:
    from gen.yapis2Lexer import yapis2Lexer
    from gen.yapis2IndentLexer import yapis2IndentLexer
    from gen.yapis2Parser import yapis2Parser
    from SemanticAnalyzer import SemanticAnalyzer
    from Compiler import Compiler
except ImportError as e:
    print("Убедитесь, что вы находитесь в правильной директории")
    sys.exit(1)


def parse_file(path):
    input_stream = FileStream(path, encoding="utf-8")
    lexer = yapis2IndentLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = yapis2Parser(tokens)
    tree = parser.program()
    return tree


def compile_to_jasmin(example_path):
    if not os.path.isabs(example_path):
        full_path = os.path.join(str(project_root), example_path)
        if not os.path.exists(full_path):
            full_path = os.path.abspath(example_path)
            if not os.path.exists(full_path):
                return None, None
    else:
        full_path = example_path
        if not os.path.exists(full_path):
            return None, None
    
    print(f"Компиляция {full_path}...")
    
    tree = parse_file(full_path)
    print("✓ Синтаксических ошибок не обнаружено")
    
    analyzer = SemanticAnalyzer()
    sem_errors = analyzer.visit(tree)
    if sem_errors:
        for e in sem_errors:
            print(f"  - {e}")
        return None, None
    print("✓ Семантических ошибок не обнаружено")
    
    compiler = Compiler()
    compiler.source_file_path = full_path
    jasmin_code = compiler.visitProgram(tree)
    
    if jasmin_code is None:
        return None, None
    
    base_name = os.path.splitext(os.path.basename(full_path))[0]
    output_file = f"{base_name}.j"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(jasmin_code)
    
    print(f"✓ Сгенерирован: {output_file}")
    return output_file, base_name


def compile_jasmin(jasmin_file):
    jasmin_jar = "jasmin.jar"
    
    try:
        subprocess.run(["java", "-version"], capture_output=True, check=True)
    except:
        print("Java не установлена: https://www.java.com/")
        return False
    
    jasmin_files = [jasmin_file]
    type_classes = ["Point.j", "Line.j", "Circle.j", "Polygon.j"]
    for tc in type_classes:
        if os.path.exists(tc):
            jasmin_files.append(tc)
    
    print(f"Компиляция {len(jasmin_files)} файлов...")
    for jf in jasmin_files:
        try:
            result = subprocess.run(["java", "-jar", jasmin_jar, jf], 
                                  check=True, capture_output=True, text=True)
            print(f"✓ {jf} скомпилирован")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.decode() if e.stderr else e.stdout.decode() if e.stdout else 'неизвестная ошибка'
            print(f"Ошибка компиляции {jf}: {error_msg}")
            return False
    
    print("✓ Компиляция завершена")
    return True


def main():
    if len(sys.argv) < 2:
        print("Использование: python run_example.py <путь_к_примеру>")
        print("Пример: python run_example.py examples/1.txt")
        sys.exit(1)
    
    example_path = sys.argv[1]
    
    jasmin_file, _ = compile_to_jasmin(example_path)
    if jasmin_file is None:
        sys.exit(1)
    
    if not compile_jasmin(jasmin_file):
        sys.exit(1)
    
    print("\n" + "="*50)
    print("Запуск программы:")
    print("="*50)
    try:
        subprocess.run(["java", "Main"], check=True)
    except:
        print("Ошибка запуска")
        sys.exit(1)
    print("="*50)


if __name__ == "__main__":
    main()

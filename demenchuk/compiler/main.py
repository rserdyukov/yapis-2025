"""RivScript compiler entry point"""

import sys
import argparse
from pathlib import Path

# Добавляем пути
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / 'generated'))

from antlr4 import InputStream

try:
    from compiler.lexer.rivscript_indent_lexer import RivScriptIndentLexer
    from compiler.parser.rivscript_parser import RivScriptParserWrapper
    from compiler.semantic.analyzer import SemanticAnalyzer
    from compiler.codegen.wat_generator import WATGenerator
    from compiler.errors import ErrorReporter, SourceLocation, CompilerError
    from compiler.listeners import CompilerErrorListener
except ImportError:
    from lexer.rivscript_indent_lexer import RivScriptIndentLexer
    from parser.rivscript_parser import RivScriptParserWrapper
    from semantic.analyzer import SemanticAnalyzer
    from codegen.wat_generator import WATGenerator
    from errors import ErrorReporter, SourceLocation, CompilerError
    from listeners import CompilerErrorListener


def compile_file(
    input_path: str,
    output_path: str = None,
    check_only: bool = False,
    debug: bool = False
) -> bool:
    """
    Компилирует файл RivScript
    
    Args:
        input_path: путь к входному файлу
        output_path: путь к выходному файлу (опционально)
        check_only: только проверить, не генерировать код
        debug: режим отладки
    
    Returns:
        True если компиляция успешна, False если есть ошибки
    """
    input_file = Path(input_path).resolve()
    
    if not input_file.exists():
        print(f"❌ Error: File not found: {input_path}")
        return False
    
    if not input_file.suffix == '.riv':
        print(f"⚠️  Warning: Expected .riv extension, got {input_file.suffix}")
    
    # Читаем файл
    try:
        source_code = input_file.read_text(encoding='utf-8')
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    filename = str(input_file)
    
    reporter = ErrorReporter(source_code, filename)
    
    if debug:
        print(f"📄 Compiling: {filename}")
        print(f"   Size: {len(source_code)} bytes, {len(source_code.splitlines())} lines")
        print()
    
    if debug:
        print("🔤 Stage 1: Lexical analysis...")
    
    try:
        input_stream = InputStream(source_code)
        lexer = RivScriptIndentLexer(input_stream)
        
        error_listener = CompilerErrorListener(reporter)
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        
    except Exception as e:
        if 'Indentation error' in str(e):
            from errors import IndentationError as RivIndentError
            # Парсим номер строки из сообщения
            import re
            match = re.search(r'line (\d+)', str(e))
            line = int(match.group(1)) if match else 1
            location = SourceLocation(line, 0, filename)
            reporter.add_error(RivIndentError(str(e), location))
        else:
            print(f"❌ Lexer error: {e}")
            return False
    
    if reporter.has_errors():
        reporter.print_all()
        return False
    
    if debug:
        print("🌳 Stage 2: Parsing...")
    
    try:
        parser_wrapper = RivScriptParserWrapper(lexer)
        parser = parser_wrapper.parser
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        
        tree = parser_wrapper.parse()
        
    except Exception as e:
        print(f"❌ Parser error: {e}")
        return False
    
    if reporter.has_errors():
        reporter.print_all()
        return False
    
    if debug:
        print("   ✓ Parse tree created")

    if debug:
        print("🔍 Stage 3: Semantic analysis...")
    
    try:
        analyzer = SemanticAnalyzer(filename)
        semantic_errors = analyzer.analyze(tree)
        
        for error in semantic_errors:
            reporter.add_error(error)
            
    except Exception as e:
        print(f"❌ Semantic error: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False
    
    if reporter.has_errors():
        reporter.print_all()
        return False
    
    if debug:
        print("   ✓ No semantic errors")
    
    if check_only:
        print(f"✅ {input_file.name}: No errors found")
        return True
    
    if debug:
        print("⚙️  Stage 4: Code generation...")
    
    try:
        generator = WATGenerator()
        wat_code = generator.generate(tree)
        
    except Exception as e:
        print(f"❌ Code generation error: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return False
    
    # Определяем выходной файл
    if output_path:
        output_file = Path(output_path).resolve()
    else:
        output_file = input_file.with_suffix('.wat')
    
    # Записываем результат
    try:
        output_file.write_text(wat_code, encoding='utf-8')
    except Exception as e:
        print(f"❌ Error writing output: {e}")
        return False
    
    print(f"✅ Compiled: {input_file.name} -> {output_file.name}")
    
    if debug:
        print(f"   Output size: {len(wat_code)} bytes")
    
    return True


def main():
    """Точка входа CLI"""
    parser = argparse.ArgumentParser(
        description='RivScript Compiler - Compiles .riv files to WAT',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compiler/main.py input.riv                    # Compile to input.wat
  python compiler/main.py input.riv -o output.wat     # Compile to specified output
  python compiler/main.py input.riv --check           # Only check for errors
  python compiler/main.py examples/correct/*.riv      # Compile multiple files
        """
    )
    
    parser.add_argument(
        'input_files',
        nargs='+',
        help='Input .riv file(s) to compile'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output .wat file (only valid with single input file)'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Only check for errors, do not generate code'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    
    args = parser.parse_args()
    
    # Проверяем что --output только с одним файлом
    if args.output and len(args.input_files) > 1:
        print("❌ Error: --output can only be used with a single input file")
        sys.exit(1)
    
    # Компилируем файлы
    success_count = 0
    fail_count = 0
    
    for input_file in args.input_files:
        success = compile_file(
            input_file,
            output_path=args.output,
            check_only=args.check,
            debug=args.debug
        )
        
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    # Итог для нескольких файлов
    if len(args.input_files) > 1:
        print()
        print(f"📊 Results: {success_count} succeeded, {fail_count} failed")
    
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == '__main__':
    main()

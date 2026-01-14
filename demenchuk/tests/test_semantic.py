#!/usr/bin/env python3
"""
Тесты семантического анализатора RivScript
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'compiler'))
sys.path.insert(0, str(Path(__file__).parent.parent / 'compiler' / 'generated'))

from antlr4 import InputStream
from compiler.lexer.rivscript_indent_lexer import RivScriptIndentLexer
from compiler.parser.rivscript_parser import RivScriptParserWrapper
from compiler.semantic.analyzer import SemanticAnalyzer


def extract_expected_error(filepath):
    """Извлекает ожидаемую ошибку из комментария"""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if 'жидаемая ошибка' in line or 'xpected error' in line:
                match = re.search(r':\s*(.+)', line)
                if match:
                    return match.group(1).strip()
    return None


def test_semantic(filepath):
    """Тестирует семантику на файле"""
    code = filepath.read_text(encoding='utf-8')
    
    try:
        input_stream = InputStream(code)
        lexer = RivScriptIndentLexer(input_stream)
        parser_wrapper = RivScriptParserWrapper(lexer)
        tree = parser_wrapper.parse()
        
        analyzer = SemanticAnalyzer(str(filepath))
        errors = analyzer.analyze(tree)
        
        if errors:
            err = errors[0]
            return False, f"[{err.error_code}] {err.message}"
        return True, None
        
    except Exception as e:
        return False, f"Exception: {str(e)[:60]}"


def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 70)
    print("SEMANTIC TESTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # Корректные примеры - должны проходить
    print("\n>>> CORRECT (should pass)")
    correct_dir = base_dir / 'examples' / 'correct'
    for f in sorted(correct_dir.glob('*.riv')):
        success, error = test_semantic(f)
        if success:
            print(f"✓ {f.name}")
            passed += 1
        else:
            print(f"✗ {f.name}")
            print(f"    Expected: SUCCESS")
            print(f"    Actual:   {error}")
            failed += 1
    
    # Ошибки семантики - должны выдавать ошибку
    print("\n>>> SEMANTIC ERRORS (should fail)")
    error_dir = base_dir / 'examples' / 'errors' / 'semantic'
    for f in sorted(error_dir.glob('*.riv')):
        expected = extract_expected_error(f)
        success, error = test_semantic(f)
        
        if not success:
            print(f"✓ {f.name}")
            print(f"    Expected: {expected or 'ERROR'}")
            print(f"    Actual:   {error}")
            passed += 1
        else:
            print(f"✗ {f.name}")
            print(f"    Expected: {expected or 'ERROR'}")
            print(f"    Actual:   SUCCESS (no error detected)")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"SEMANTIC: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    sys.exit(0 if main() else 1)

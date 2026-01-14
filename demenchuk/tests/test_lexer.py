#!/usr/bin/env python3
"""
Тесты лексера RivScript
"""

import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'compiler' / 'generated'))

from antlr4 import InputStream
from antlr4.error.ErrorListener import ErrorListener
from compiler.lexer.rivscript_indent_lexer import RivScriptIndentLexer


class LexerErrorCollector(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append(f"L{line}:{column} {msg}")


def extract_expected_error(filepath):
    """Извлекает ожидаемую ошибку из комментария"""
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if 'жидаемая ошибка' in line or 'xpected error' in line:
                match = re.search(r':\s*(.+)', line)
                if match:
                    return match.group(1).strip()
    return None


def test_lexer(filepath):
    """Тестирует лексер на файле"""
    code = filepath.read_text(encoding='utf-8')
    
    try:
        input_stream = InputStream(code)
        lexer = RivScriptIndentLexer(input_stream)
        
        collector = LexerErrorCollector()
        lexer.removeErrorListeners()
        lexer.addErrorListener(collector)
        
        # Получаем все токены
        tokens = lexer.getAllTokens()
        
        if collector.errors:
            return False, collector.errors[0]
        return True, None
        
    except Exception as e:
        return False, str(e)[:80]


def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 70)
    print("LEXER TESTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # Корректные примеры - должны проходить
    print("\n>>> CORRECT (should pass)")
    correct_dir = base_dir / 'examples' / 'correct'
    for f in sorted(correct_dir.glob('*.riv')):
        success, error = test_lexer(f)
        if success:
            print(f"✓ {f.name}")
            passed += 1
        else:
            print(f"✗ {f.name}")
            print(f"    Expected: SUCCESS")
            print(f"    Actual:   ERROR: {error}")
            failed += 1
    
    # Ошибки лексера - должны выдавать ошибку
    print("\n>>> LEXER ERRORS (should fail)")
    error_dir = base_dir / 'examples' / 'errors' / 'lexer'
    for f in sorted(error_dir.glob('*.riv')):
        expected = extract_expected_error(f)
        success, error = test_lexer(f)
        
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
    print(f"LEXER: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    sys.exit(0 if main() else 1)

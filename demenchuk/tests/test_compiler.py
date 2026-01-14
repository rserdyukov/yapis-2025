#!/usr/bin/env python3
"""
Интеграционные тесты компилятора RivScript (полный pipeline)
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from compiler.main import compile_file


def main():
    base_dir = Path(__file__).parent.parent
    
    print("=" * 70)
    print("COMPILER INTEGRATION TESTS")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # Корректные примеры - должны компилироваться
    print("\n>>> CORRECT (should compile)")
    correct_dir = base_dir / 'examples' / 'correct'
    for f in sorted(correct_dir.glob('*.riv')):
        with tempfile.NamedTemporaryFile(suffix='.wat', delete=False) as tmp:
            output_path = tmp.name
        
        success = compile_file(str(f), output_path, check_only=False, debug=False)
        
        # Проверяем что WAT создан
        wat_file = Path(output_path)
        if success and wat_file.exists() and wat_file.stat().st_size > 100:
            print(f"✓ {f.name}")
            print(f"    Compiled to: {wat_file.stat().st_size} bytes")
            passed += 1
        else:
            print(f"✗ {f.name}")
            print(f"    Expected: SUCCESS")
            print(f"    Actual:   FAILED")
            failed += 1
        
        wat_file.unlink(missing_ok=True)
    
    # Все ошибки - должны не компилироваться
    print("\n>>> ALL ERRORS (should fail)")
    for error_type in ['lexer', 'parser', 'semantic']:
        error_dir = base_dir / 'examples' / 'errors' / error_type
        if not error_dir.exists():
            continue
            
        for f in sorted(error_dir.glob('*.riv')):
            success = compile_file(str(f), None, check_only=True, debug=False)
            
            if not success:
                print(f"✓ {f.name} ({error_type})")
                passed += 1
            else:
                print(f"✗ {f.name} ({error_type})")
                print(f"    Expected: ERROR")
                print(f"    Actual:   SUCCESS (no error)")
                failed += 1
    
    print("\n" + "=" * 70)
    print(f"COMPILER: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == '__main__':
    sys.exit(0 if main() else 1)

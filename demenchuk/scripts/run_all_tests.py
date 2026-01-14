#!/usr/bin/env python3
"""Run all compiler tests"""

import sys
import subprocess
from pathlib import Path


class Colors:
    GREEN = '\033[0;32m'
    RED = '\033[0;31m'
    NC = '\033[0m'  # No Color
    
    @staticmethod
    def green(text):
        return f"{Colors.GREEN}{text}{Colors.NC}"
    
    @staticmethod
    def red(text):
        return f"{Colors.RED}{text}{Colors.NC}"


def run_test_suite(name, script_path):
    """Запускает один набор тестов"""
    print(f"Running {name} tests...")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,
            cwd=script_path.parent.parent
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running {name}: {e}")
        return False


def main():
    project_dir = Path(__file__).parent.parent
    tests_dir = project_dir / "tests"
    
    print("=" * 70)
    print("RivScript Compiler - Full Test Suite")
    print("=" * 70)
    print()
    
    total_passed = 0
    total_failed = 0
    
    test_suites = [
        ("LEXER", tests_dir / "test_lexer.py"),
        ("PARSER", tests_dir / "test_parser.py"),
        ("SEMANTIC", tests_dir / "test_semantic.py"),
        ("COMPILER INTEGRATION", tests_dir / "test_compiler.py"),
    ]
    
    for i, (name, path) in enumerate(test_suites, 1):
        print(f"{i}/{len(test_suites)} Running {name} tests...")
        
        if run_test_suite(name, path):
            print(Colors.green(f"✓ {name} tests passed"))
            total_passed += 1
        else:
            print(Colors.red(f"✗ {name} tests failed"))
            total_failed += 1
        
        print()
    
    # Итоговый результат
    print("=" * 70)
    if total_failed == 0:
        print(Colors.green(f"ALL TESTS PASSED ({total_passed}/{len(test_suites)})"))
        sys.exit(0)
    else:
        print(Colors.red(f"SOME TESTS FAILED (passed: {total_passed}, failed: {total_failed})"))
        sys.exit(1)


if __name__ == "__main__":
    main()

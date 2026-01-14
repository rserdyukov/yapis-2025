#!/usr/bin/env python3
"""Generate ANTLR parser from grammar"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    compiler_dir = project_dir / "compiler"
    grammar_file = compiler_dir / "RivScript.g4"
    output_dir = compiler_dir / "generated"
    
    print("=" * 60)
    print("RivScript Parser Generator")
    print("=" * 60)
    print(f"Grammar: {grammar_file}")
    print(f"Output:  {output_dir}")
    print()
    
    if not grammar_file.exists():
        print(f"ERROR: Grammar file not found: {grammar_file}")
        sys.exit(1)
    
    try:
        result = subprocess.run(
            ["antlr4", "-version"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        print("ERROR: antlr4 not found!")
        print()
        print("Install ANTLR4:")
        print("  pip install antlr4-tools")
        print()
        print("Or on macOS:")
        print("  brew install antlr")
        print()
        print("Or on Linux:")
        print("  sudo apt-get install antlr4")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating parser...")
    os.chdir(compiler_dir)
    
    result = subprocess.run([
        "antlr4",
        "-Dlanguage=Python3",
        "-o", "generated",
        "-visitor",
        "RivScript.g4"
    ])
    
    if result.returncode != 0:
        print("ERROR: Parser generation failed!")
        sys.exit(1)
    
    init_file = output_dir / "__init__.py"
    if not init_file.exists():
        init_file.write_text("# Generated ANTLR files\n")
    
    print()
    print("✅ Parser generated successfully!")
    print()
    print("Next steps:")
    print("  python compiler/main.py examples/correct/01_basic_types.riv")
    print()


if __name__ == "__main__":
    main()

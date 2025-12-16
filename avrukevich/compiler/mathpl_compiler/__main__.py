import sys
import argparse

from .pipeline import compile_source


def main():
    parser = argparse.ArgumentParser(description="MathPL Compiler")
    
    parser.add_argument("source_file", help="Path to the source .mpl file")
    
    parser.add_argument(
        "-o", "--output", 
        help="Destination directory for compiled files (default: same as source)",
        default=None
    )
    
    parser.add_argument(
        "--wasm", 
        action="store_true", 
        help="Compile the resulting .wat file to binary .wasm using wat2wasm"
    )

    args = parser.parse_args()

    success = compile_source(
        file_path=args.source_file, 
        output_dir=args.output, 
        to_wasm=args.wasm
    )

    if not success:
        sys.exit(1)
    

if __name__ == '__main__':
    main()
import sys

from .pipeline import compile_source


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m mathpl_compiler <path_to_source_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    if not compile_source(input_file):
        sys.exit(1)
    

if __name__ == '__main__':
    main()

    
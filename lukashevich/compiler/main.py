import sys
import os
from antlr4 import *
from parser_code.ExprLexer import ExprLexer
from parser_code.ExprParser import ExprParser
from semantic_analyzer import SemanticAnalyzer, AnalysisErrorManager


def analyze_file(filepath: str):
    if not os.path.isfile(filepath):
        return [f"Файл не найден: {filepath}"]
    error_manager = AnalysisErrorManager()

    try:
        input_stream = FileStream(filepath, encoding="utf-8")
        lexer = ExprLexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_manager)

        token_stream = CommonTokenStream(lexer)
        parser = ExprParser(token_stream)
        parser.removeErrorListeners()
        parser.addErrorListener(error_manager)

        tree = parser.program()

        if error_manager.has_errors():
            return error_manager.get_errors()

        analyzer = SemanticAnalyzer(error_manager)
        analyzer.analyze(tree)
        if error_manager.has_errors():
            return error_manager.get_errors()
        return []

    except Exception as e:
        return [f"Internal analyzer error: {e}"]


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    filepath = sys.argv[1]

    all_errors = analyze_file(filepath)

    if all_errors:
        for error in all_errors:
            print(f"{error}")
        sys.exit(1)
    else:
        print("Analyze successful")


if __name__ == "__main__":
    main()

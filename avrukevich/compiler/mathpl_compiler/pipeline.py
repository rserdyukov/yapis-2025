from antlr4 import FileStream, CommonTokenStream
from antlr_generated import GrammarMathPLLexer, GrammarMathPLParser

from .analyzer import MathPLSemanticAnalyzer
from .utils import MathPLErrorListener


def compile_source(file_path: str) -> bool:
    try:
        input_stream = FileStream(file_path, encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return False
    except Exception as e:
        print(f"Error: {e} while reading file")
        return False
    
    error_listener = MathPLErrorListener()

    lexer = GrammarMathPLLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    stream = CommonTokenStream(lexer)

    parser = GrammarMathPLParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener) 

    print(f"Starting syntax check for: {file_path}")
    tree = parser.program()
    if error_listener.errors:
        print("Syntax check failed. Errors found:")
        for error in error_listener.errors:
            print(error)
        return False
    print("Syntax check successful. No errors found.")

    print(f"Starting semantic analysis for: {file_path}")
    analyzer = MathPLSemanticAnalyzer(error_listener)
    analyzer.visit(tree)
    if error_listener.errors:
        print("Compilation failed. Errors found:")
        for error in error_listener.errors:
            print(error)
        return False
    print("Semantic analysis was successful. No errors found.")

    return True
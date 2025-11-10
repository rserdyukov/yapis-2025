import sys
from antlr4 import *
from parse_antlr.StringLangLexer import StringLangLexer
from parse_antlr.StringLangParser import StringLangParser
from antlr4.error.ErrorListener import ErrorListener
from antlr4.tree.Tree import ParseTreeWalker
from semantic_analyzer import SemanticAnalyzer
from models import Error, ErrorType

class SyntaxErrorListener(ErrorListener):
    def __init__(self):
        self.errors = []
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        token_text = offendingSymbol.text if offendingSymbol else "<unknown>"
        error = Error(line, column, f"Unexpected token '{token_text}': {msg}", ErrorType.SYNTAX)
        self.errors.append(error)
    
    def get_errors(self):
        return self.errors

def analyze_file(filename: str):
    try:
        input_stream = FileStream(filename, encoding='utf-8')
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    lexer = StringLangLexer(input_stream)
    lexer.removeErrorListeners()
    lexer_error_listener = SyntaxErrorListener()
    lexer.addErrorListener(lexer_error_listener)
    
    stream = CommonTokenStream(lexer)
    
    parser = StringLangParser(stream)
    parser.removeErrorListeners()
    parser_error_listener = SyntaxErrorListener()
    parser.addErrorListener(parser_error_listener)
    
    tree = parser.program()
    
    syntax_errors = lexer_error_listener.get_errors() + parser_error_listener.get_errors()
    
    if syntax_errors:
        print(f"\n=== SYNTAX ERRORS ({filename}) ===")
        for error in sorted(syntax_errors, key=lambda e: (e.line, e.column)):
            print(error)
        return
    
    semantic_analyzer = SemanticAnalyzer()
    walker = ParseTreeWalker()
    walker.walk(semantic_analyzer, tree)
    
    semantic_errors = semantic_analyzer.get_errors()
    
    if semantic_errors:
        print(f"\n=== SEMANTIC ERRORS ({filename}) ===")
        for error in sorted(semantic_errors, key=lambda e: (e.line, e.column)):
            print(error)
    else:
        print(f"\n✓ No errors found ({filename})")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <source_file>")
        sys.exit(1)
    
    analyze_file(sys.argv[1])
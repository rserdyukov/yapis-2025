import sys
from antlr4 import *
from parse_antlr.StringLangLexer import StringLangLexer
from parse_antlr.StringLangParser import StringLangParser
from antlr4.error.ErrorListener import ErrorListener
from antlr4.tree.Tree import ParseTreeWalker
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
from emitter import Emitter
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

def compile_to_jasmin(source_file: str, output_file: str):
    try:
        input_stream = FileStream(source_file, encoding='utf-8')
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
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
        for error in syntax_errors:
            print(error)
        return False
    
    semantic_analyzer = SemanticAnalyzer()
    walker = ParseTreeWalker()
    walker.walk(semantic_analyzer, tree)
    
    if semantic_analyzer.has_errors():
        for error in semantic_analyzer.get_errors():
            print(error)
        return False
    
    print("Syntax and semantic analysis passed")
    
    code_gen = CodeGenerator(semantic_analyzer)
    code_gen.visitProgram(tree)
    
    emitter = Emitter(
        code_gen.instructions,
        code_gen.function_instructions,
        code_gen.function_local_counters,
        semantic_analyzer
    )
    
    jasmin_code = emitter.emit()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(jasmin_code)
    
    print(f"Code generated: {output_file}")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python code_gen_main.py <source.txt> <output.j>")
        sys.exit(1)
    
    source = sys.argv[1]
    output = sys.argv[2]
    
    if compile_to_jasmin(source, output):
        print(f"Compilation successful!")
        sys.exit(0)
    else:
        print("Compilation failed")
        sys.exit(1)
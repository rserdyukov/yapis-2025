# xml_parser.py
from antlr4 import *
from XMLlangLexer import XMLlangLexer
from XMLlangParser import XMLlangParser
from antlr4.error.ErrorListener import ErrorListener
from antlr4.tree.Trees import Trees

class CustomErrorListener(ErrorListener):
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_type = "Error"
        if "token recognition error" in msg:
            error_type = "Lexical"
            if offendingSymbol:
                bad_char = offendingSymbol.text
                msg = f"Unrecognized character: '{bad_char}'"
                
        error_msg = f"{error_type} at line {line}:{column} - {msg}"
        self.errors.append(error_msg)
        
    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        pass
        
    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        pass
        
    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        pass

class XMLParser:
    def __init__(self, input_text):
        self.input_stream = InputStream(input_text)
        self.lexer = XMLlangLexer(self.input_stream)
        self.stream = CommonTokenStream(self.lexer)
        self.parser = XMLlangParser(self.stream)
        self.error_listener = CustomErrorListener()
        
        self.lexer.removeErrorListeners()
        self.parser.removeErrorListeners()
        self.lexer.addErrorListener(self.error_listener)
        self.parser.addErrorListener(self.error_listener)
        
        self.tree = None
        self.syntax_errors = []
        
    def parse(self):
    
        try:
            self.tree = self.parser.start()
            self.syntax_errors = self.error_listener.errors
            
            tokens = list(self.lexer.getAllTokens())
            for token in tokens:
                
                if token.type == self.lexer.ERROR:
                    self.syntax_errors.append(
                        f"Lexical error at line {token.line}:{token.column} - "
                        f"Invalid character: '{token.text}'"
                    )
                    
            return self.tree if not self.has_errors() else None
            
        except Exception as e:
            self.syntax_errors.append(f"Parsing failed: {e}")
            return None
            
    def has_errors(self):
        return len(self.syntax_errors) > 0
        
    def get_errors(self):
        return self.syntax_errors
        
    def get_tree_string(self):
        if self.tree and not self.has_errors():
            return Trees.toStringTree(self.tree, None, self.parser)
        return "No valid tree generated"
        
    def print_tree(self, node=None, indent=0):
        if self.has_errors():
            print("Cannot print tree due to syntax errors")
            return
            
        if node is None:
            node = self.tree
            
        if isinstance(node, ParserRuleContext):
            rule_name = self.parser.ruleNames[node.getRuleIndex()]
            print("  " * indent + f"{rule_name}")
            for child in node.getChildren():
                self.print_tree(child, indent + 1)
        elif isinstance(node, TerminalNode):
            token = node.getSymbol()
            token_name = self.parser.symbolicNames[token.type] \
                if token.type < len(self.parser.symbolicNames) else str(token.type)
            print("  " * indent + f"{token_name}: '{token.text}'")
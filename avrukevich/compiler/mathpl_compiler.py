from enum import Enum, auto
from collections import namedtuple

from antlr4.error.ErrorListener import ErrorListener
from antlr_generated import GrammarMathPLVisitor, GrammarMathPLParser


# --- UTILITY CLASSES AND ENUMS ---

class MathPLErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_message = f"  SYNTAX ERROR on line {line}:{column} -> {msg}"
        self.errors.append(error_message)
"""
Error listener для ANTLR парсера и лексера
"""

from antlr4.error.ErrorListener import ErrorListener
from ..errors import ErrorReporter, SourceLocation, SyntaxError as RivSyntaxError


class CompilerErrorListener(ErrorListener):
    """Собирает ошибки лексера и парсера"""
    
    def __init__(self, reporter: ErrorReporter):
        super().__init__()
        self.reporter = reporter
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        location = SourceLocation(line, column, self.reporter.filename)
        error = RivSyntaxError(msg, location)
        self.reporter.add_error(error)

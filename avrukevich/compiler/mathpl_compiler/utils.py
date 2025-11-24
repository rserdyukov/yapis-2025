from antlr4.error.ErrorListener import ErrorListener


class MathPLErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_message = f"  SYNTAX ERROR on line {line}:{column} -> {msg}"
        self.errors.append(error_message)
    
    def semanticError(self, ctx, msg: str):
        line = ctx.start.line
        column = ctx.start.column
        error_message = (
            f"  SEMANTIC ERROR on line {line}:{column} -> {msg}"
        )
        self.errors.append(error_message)
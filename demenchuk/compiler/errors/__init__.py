"""
Система обработки ошибок компиляции RivScript
"""

from .base import ErrorSeverity, SourceLocation, CompilerError
from .lexer_errors import (
    LexerError,
    InvalidCharacterError,
    UnclosedStringError,
    IndentationError,
    UnclosedCommentError,
)
from .parser_errors import (
    ParserError,
    SyntaxError,
    MissingTokenError,
    UnexpectedTokenError,
)
from .semantic_errors import (
    SemanticError,
    UndefinedVariableError,
    UndefinedFunctionError,
    TypeMismatchError,
    WrongArgCountError,
    ScopeError,
    InvalidCastError,
    RefParamError,
    DuplicateDefinitionError,
)
from .error_reporter import ErrorReporter, format_simple_error

__all__ = [
    'ErrorSeverity',
    'SourceLocation',
    'CompilerError',
    'LexerError',
    'InvalidCharacterError',
    'UnclosedStringError',
    'IndentationError',
    'UnclosedCommentError',
    'ParserError',
    'SyntaxError',
    'MissingTokenError',
    'UnexpectedTokenError',
    'SemanticError',
    'UndefinedVariableError',
    'UndefinedFunctionError',
    'TypeMismatchError',
    'WrongArgCountError',
    'ScopeError',
    'InvalidCastError',
    'RefParamError',
    'DuplicateDefinitionError',
    'ErrorReporter',
    'format_simple_error',
]

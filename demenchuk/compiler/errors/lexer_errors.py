"""
Ошибки лексического анализа (E1xx)
"""

from .base import CompilerError, SourceLocation


class LexerError(CompilerError):
    """Базовый класс лексических ошибок"""
    
    @property
    def error_type(self) -> str:
        return "LexerError"


class InvalidCharacterError(LexerError):
    """Недопустимый символ"""
    
    def __init__(self, char: str, location: SourceLocation):
        super().__init__(
            f"Invalid character '{char}'",
            location,
            hint="Only ASCII letters, digits, and standard operators are allowed"
        )
    
    @property
    def error_code(self) -> str:
        return "E101"


class UnclosedStringError(LexerError):
    """Незакрытая строка"""
    
    def __init__(self, location: SourceLocation):
        super().__init__(
            "Unclosed string literal",
            location,
            hint="Add a closing quote \" at the end of the string"
        )
    
    @property
    def error_code(self) -> str:
        return "E102"


class IndentationError(LexerError):
    """Ошибка отступов"""
    
    def __init__(self, message: str, location: SourceLocation):
        super().__init__(
            message,
            location,
            hint="Use consistent indentation (4 spaces or 1 tab, don't mix)"
        )
    
    @property
    def error_code(self) -> str:
        return "E103"


class UnclosedCommentError(LexerError):
    """Незакрытый комментарий"""
    
    def __init__(self, location: SourceLocation):
        super().__init__(
            "Unclosed multi-line comment",
            location,
            hint="Add '*/' to close the comment"
        )
    
    @property
    def error_code(self) -> str:
        return "E104"

"""
Ошибки синтаксического анализа (E2xx)
"""

from .base import CompilerError, SourceLocation


class ParserError(CompilerError):
    """Базовый класс синтаксических ошибок"""
    
    @property
    def error_type(self) -> str:
        return "ParserError"


class SyntaxError(ParserError):
    """Общая синтаксическая ошибка"""
    
    def __init__(self, message: str, location: SourceLocation, hint: str = None):
        super().__init__(message, location, hint)
    
    @property
    def error_code(self) -> str:
        return "E201"


class MissingTokenError(ParserError):
    """Отсутствующий токен"""
    
    def __init__(self, expected: str, location: SourceLocation):
        super().__init__(
            f"Missing '{expected}'",
            location,
            hint=f"Add '{expected}' here"
        )
    
    @property
    def error_code(self) -> str:
        return "E202"


class UnexpectedTokenError(ParserError):
    """Неожиданный токен"""
    
    def __init__(self, found: str, expected: str, location: SourceLocation):
        super().__init__(
            f"Unexpected '{found}', expected {expected}",
            location
        )
    
    @property
    def error_code(self) -> str:
        return "E203"

"""
Типы ошибок компилятора RivScript
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ErrorSeverity(Enum):
    WARNING = "warning"
    ERROR = "error"
    FATAL = "fatal"


@dataclass
class SourceLocation:
    """Позиция в исходном коде"""
    line: int
    column: int
    file: str = "<unknown>"
    
    def __str__(self):
        return f"{self.file}:{self.line}:{self.column}"


class CompilerError(Exception):
    """Базовый класс для всех ошибок компилятора"""
    
    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        hint: Optional[str] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ):
        self.message = message
        self.location = location
        self.hint = hint
        self.severity = severity
        super().__init__(self.format())
    
    @property
    def error_code(self) -> str:
        return "E000"
    
    @property
    def error_type(self) -> str:
        return "CompilerError"
    
    def format(self) -> str:
        """Форматирует ошибку в читаемый вид"""
        parts = []
        
        # Заголовок с цветом
        severity_prefix = {
            ErrorSeverity.WARNING: "⚠️  warning",
            ErrorSeverity.ERROR: "❌ error",
            ErrorSeverity.FATAL: "💀 fatal"
        }
        
        header = f"{severity_prefix[self.severity]}[{self.error_code}]: {self.message}"
        parts.append(header)
        
        # Позиция
        if self.location:
            parts.append(f"  --> {self.location}")
        
        # Подсказка
        if self.hint:
            parts.append(f"  💡 hint: {self.hint}")
        
        return "\n".join(parts)


# ============================================================================
# LEXER ERRORS (E1xx)
# ============================================================================

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


# ============================================================================
# PARSER ERRORS (E2xx)
# ============================================================================

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


# ============================================================================
# SEMANTIC ERRORS (E3xx)
# ============================================================================

class SemanticError(CompilerError):
    """Базовый класс семантических ошибок"""
    
    @property
    def error_type(self) -> str:
        return "SemanticError"


class UndefinedVariableError(SemanticError):
    """Использование необъявленной переменной"""
    
    def __init__(self, name: str, location: SourceLocation):
        super().__init__(
            f"Undefined variable '{name}'",
            location,
            hint=f"Define '{name}' before using it: {name} = <value>"
        )
        self.name = name
    
    @property
    def error_code(self) -> str:
        return "E301"


class UndefinedFunctionError(SemanticError):
    """Вызов необъявленной функции"""
    
    def __init__(self, name: str, location: SourceLocation):
        super().__init__(
            f"Undefined function '{name}'",
            location,
            hint=f"Define function before calling: def {name}(...):"
        )
        self.name = name
    
    @property
    def error_code(self) -> str:
        return "E302"


class TypeMismatchError(SemanticError):
    """Несовместимость типов"""
    
    def __init__(self, expected: str, got: str, operation: str, location: SourceLocation):
        super().__init__(
            f"Type mismatch: cannot {operation} '{expected}' and '{got}'",
            location,
            hint=f"Use explicit cast: ({expected}) value"
        )
        self.expected = expected
        self.got = got
    
    @property
    def error_code(self) -> str:
        return "E303"


class WrongArgCountError(SemanticError):
    """Неверное количество аргументов"""
    
    def __init__(self, name: str, expected: int, got: int, location: SourceLocation):
        super().__init__(
            f"Function '{name}' expects {expected} argument(s), got {got}",
            location,
            hint=f"Check function signature: def {name}(...)"
        )
        self.name = name
        self.expected = expected
        self.got = got
    
    @property
    def error_code(self) -> str:
        return "E304"


class ScopeError(SemanticError):
    """Ошибка области видимости"""
    
    def __init__(self, name: str, message: str, location: SourceLocation):
        super().__init__(
            f"Scope error for '{name}': {message}",
            location
        )
        self.name = name
    
    @property
    def error_code(self) -> str:
        return "E305"


class InvalidCastError(SemanticError):
    """Недопустимое приведение типа"""
    
    def __init__(self, from_type: str, to_type: str, location: SourceLocation):
        super().__init__(
            f"Cannot cast '{from_type}' to '{to_type}'",
            location,
            hint="Not all type conversions are allowed"
        )
        self.from_type = from_type
        self.to_type = to_type
    
    @property
    def error_code(self) -> str:
        return "E306"


class RefParamError(SemanticError):
    """Ошибка ref-параметра"""
    
    def __init__(self, message: str, location: SourceLocation):
        super().__init__(
            message,
            location,
            hint="ref parameters require a variable, not a literal or expression"
        )
    
    @property
    def error_code(self) -> str:
        return "E307"


class DuplicateDefinitionError(SemanticError):
    """Повторное определение"""
    
    def __init__(self, name: str, kind: str, location: SourceLocation, prev_location: SourceLocation = None):
        hint = None
        if prev_location:
            hint = f"Previously defined at {prev_location}"
        super().__init__(
            f"{kind.capitalize()} '{name}' is already defined",
            location,
            hint
        )
        self.name = name
    
    @property
    def error_code(self) -> str:
        return "E308"

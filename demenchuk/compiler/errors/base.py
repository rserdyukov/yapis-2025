"""
Базовые классы для ошибок компилятора
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
        
        severity_prefix = {
            ErrorSeverity.WARNING: "⚠️  warning",
            ErrorSeverity.ERROR: "❌ error",
            ErrorSeverity.FATAL: "💀 fatal"
        }
        
        header = f"{severity_prefix[self.severity]}[{self.error_code}]: {self.message}"
        parts.append(header)
        
        if self.location:
            parts.append(f"  --> {self.location}")
        
        if self.hint:
            parts.append(f"  💡 hint: {self.hint}")
        
        return "\n".join(parts)

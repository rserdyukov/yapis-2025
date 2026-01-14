"""
Ошибки семантического анализа (E3xx)
"""

from .base import CompilerError, SourceLocation


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
    
    def __init__(self, message: str, location: SourceLocation):
        super().__init__(
            message,
            location,
            hint="Check variable scope and lifetime"
        )
    
    @property
    def error_code(self) -> str:
        return "E305"


class InvalidCastError(SemanticError):
    """Недопустимое приведение типов"""
    
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
    
    def __init__(self, name: str, location: SourceLocation):
        super().__init__(
            f"Duplicate definition of '{name}'",
            location,
            hint=f"'{name}' is already defined in this scope"
        )
        self.name = name
    
    @property
    def error_code(self) -> str:
        return "E308"

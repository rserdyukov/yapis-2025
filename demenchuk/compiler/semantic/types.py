"""
Типы данных и символов RivScript
"""

from enum import Enum


class SymbolKind(Enum):
    VARIABLE = "variable"
    FUNCTION = "function"
    PARAMETER = "parameter"
    BUILTIN = "builtin"


class RivType(Enum):
    """Типы данных RivScript"""
    INT = "int"
    STRING = "string"
    BOOL = "bool"
    ELEMENT = "element"
    LIST = "list"
    TREE = "tree"
    QUEUE = "queue"
    NIL = "nil"
    ANY = "any"  # Для встроенных функций с любым типом
    UNKNOWN = "unknown"  # Тип ещё не определён

from enum import Enum
from typing import Optional, List

class ErrorType(Enum):
    SYNTAX = "SYNTAX"
    SEMANTIC = "SEMANTIC"

class Error:
    def __init__(self, line: int, column: int, message: str, error_type: ErrorType):
        self.line = line
        self.column = column
        self.message = message
        self.error_type = error_type
    
    def __str__(self):
        return f"line {self.line}:{self.column} {self.error_type.value} error: {self.message}"

class Variable:
    def __init__(self, name: str, var_type: str, assigned_type: Optional[str] = None,
                 is_array: bool = False, is_parameter: bool = False, 
                 is_initialized: bool = False):
        self.name = name
        self.var_type = var_type
        self.assigned_type = assigned_type
        self.is_array = is_array
        self.is_parameter = is_parameter
        self.is_initialized = is_initialized

class Function:
    def __init__(self, name: str, return_type: str, parameters: List[Variable]):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters
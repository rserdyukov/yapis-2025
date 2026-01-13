from typing import List
from enum import Enum, auto


class MathPLType:
    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name
    
    def __eq__(self, other):
        if isinstance(other, MathPLType):
            return self.name == other.name
        return False
    
    def __hash__(self):
        return hash(self.name)
    

class PrimitiveType(MathPLType):
    pass


class ArrayType(MathPLType):
    def __init__(self, element_type: MathPLType):
        super().__init__(f"{element_type.name}[]")
        self.element_type = element_type


class FunctionType(MathPLType):
    def __init__(
            self,
            return_type: MathPLType,
            param_types: List[MathPLType]
    ) -> None:
        super().__init__('FUNCTION')
        self.return_type = return_type
        self.param_types = param_types
    
    def __repr__(self) -> str:
        return f"{self.name}(PARAMS({self.param_types})) -> {self.return_type}"


INT = PrimitiveType('INT')
FLOAT = PrimitiveType('FLOAT')
BOOL = PrimitiveType('BOOL')
STRING = PrimitiveType('STRING')
VOID = PrimitiveType('VOID')
UNKNOWN = PrimitiveType('UNKNOWN')


class SymbolCategory(Enum):
    GLOBAL = auto()
    LOCAL = auto()
    PARAMETER = auto()
    FUNCTION = auto()


class Symbol:
    def __init__(
        self,
        name: str,
        symbol_type: MathPLType,
        category: SymbolCategory,
        index: int = 0
    ) -> None:
        self.name = name
        self.type = symbol_type
        self.category = category
        self.index = index
    
    def __repr__(self) -> str:
        return (
            f"<Symbol(name='{self.name}', "
            f"type='{self.type.name}', "
            f"cat='{self.category}', "
            f"idx='{self.index}'"
        )
    

class FunctionSymbol(Symbol):
    def __init__(
        self, 
        name: str,
        return_type: MathPLType,
        param_types: List[MathPLType]
    ) -> None:
        super().__init__(
            name, 
            FunctionType(return_type, param_types), 
            SymbolCategory.FUNCTION
        )
        self.return_type = return_type
        self.param_types = param_types
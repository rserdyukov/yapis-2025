from typing import List


class MathPLType:

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return self.name
    

class PrimitiveType(MathPLType):
    pass


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

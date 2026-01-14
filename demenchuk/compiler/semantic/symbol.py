"""
Класс Symbol для представления символов в таблице
"""

from dataclasses import dataclass, field
from typing import List
from .types import SymbolKind, RivType


@dataclass
class Symbol:
    """Символ в таблице (переменная, функция, параметр)"""
    name: str
    kind: SymbolKind
    type: RivType = RivType.UNKNOWN
    line: int = 0
    column: int = 0
    # Для функций
    params: List['Symbol'] = field(default_factory=list)
    is_ref: bool = False  # Для ref-параметров
    
    def __repr__(self):
        if self.kind == SymbolKind.FUNCTION:
            param_str = ", ".join(p.name for p in self.params)
            return f"Function({self.name}({param_str}) -> {self.type.value})"
        return f"{self.kind.value}({self.name}: {self.type.value})"

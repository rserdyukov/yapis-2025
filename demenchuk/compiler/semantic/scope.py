"""
Класс Scope для управления областями видимости
"""

from typing import Dict, List, Optional
from .symbol import Symbol


class Scope:
    """Область видимости"""
    
    def __init__(self, name: str = "global", parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, Symbol] = {}
        self.children: List['Scope'] = []
        
        if parent:
            parent.children.append(self)
    
    def define(self, symbol: Symbol) -> bool:
        """Добавляет символ в текущую область"""
        if symbol.name in self.symbols:
            return False  # Уже определён
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Ищет символ в текущей области и родительских"""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
    
    def lookup_local(self, name: str) -> Optional[Symbol]:
        """Ищет символ только в текущей области"""
        return self.symbols.get(name)
    
    def __repr__(self):
        return f"Scope({self.name}, {len(self.symbols)} symbols)"

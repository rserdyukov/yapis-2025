"""
Таблица символов для отслеживания переменных и функций
"""

from typing import Dict, List, Optional
from .types import SymbolKind, RivType
from .symbol import Symbol
from .scope import Scope
from .builtins import get_builtin_functions, create_builtin_symbol


class SymbolTable:
    """Таблица символов с поддержкой вложенных областей видимости"""
    
    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        # Для перегрузки функций: имя -> список функций с разным числом параметров
        self.functions: Dict[str, List[Symbol]] = {}
        
        # Регистрируем встроенные функции
        self._register_builtins()
    
    def _register_builtins(self):
        """Регистрирует встроенные функции"""
        for name, params, return_type in get_builtin_functions():
            func = create_builtin_symbol(name, params, return_type)
            self.define_function(func)
    
    def enter_scope(self, name: str = "block"):
        """Входит в новую область видимости"""
        new_scope = Scope(name, self.current_scope)
        self.current_scope = new_scope
    
    def exit_scope(self):
        """Выходит из текущей области видимости"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
    
    def define(self, symbol: Symbol) -> bool:
        """Определяет символ в текущей области"""
        return self.current_scope.define(symbol)
    
    def define_function(self, func: Symbol):
        """Определяет функцию с поддержкой перегрузки"""
        if func.name not in self.functions:
            self.functions[func.name] = []
        
        # Проверяем, нет ли уже функции с таким же количеством параметров
        param_count = len(func.params)
        for existing in self.functions[func.name]:
            if len(existing.params) == param_count:
                return False  # Дублирование
        
        self.functions[func.name].append(func)
        # Также добавляем в глобальную область
        self.global_scope.define(func)
        return True
    
    def lookup(self, name: str) -> Optional[Symbol]:
        """Ищет переменную в текущей области и родительских"""
        return self.current_scope.lookup(name)
    
    def lookup_function(self, name: str, arg_count: int = None) -> Optional[Symbol]:
        """Ищет функцию, опционально с нужным количеством аргументов"""
        if name not in self.functions:
            return None
        
        funcs = self.functions[name]
        
        if arg_count is None:
            return funcs[0] if funcs else None
        
        # Ищем перегрузку с нужным количеством параметров
        for func in funcs:
            if len(func.params) == arg_count:
                return func
        
        return None
    
    def is_defined(self, name: str) -> bool:
        """Проверяет, определён ли символ"""
        return self.lookup(name) is not None
    
    def is_function(self, name: str) -> bool:
        """Проверяет, является ли имя функцией"""
        return name in self.functions

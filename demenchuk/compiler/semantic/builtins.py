"""
Встроенные функции RivScript
"""

from typing import List, Tuple
from .symbol import Symbol
from .types import SymbolKind, RivType


def get_builtin_functions() -> List[Tuple[str, List[Tuple[str, RivType]], RivType]]:
    """
    Возвращает список встроенных функций
    
    Returns:
        List[Tuple[name, params, return_type]]
    """
    return [
        # I/O
        ("read", [], RivType.STRING),
        ("write", [("value", RivType.ANY)], RivType.NIL),
        
        # Element
        ("element", [("value", RivType.ANY)], RivType.ELEMENT),
        ("get_value", [("elem", RivType.ELEMENT)], RivType.ANY),
        ("set_value", [("elem", RivType.ELEMENT), ("value", RivType.ANY)], RivType.ELEMENT),
        
        # List
        ("length", [("lst", RivType.LIST)], RivType.INT),
        ("sort", [("lst", RivType.LIST)], RivType.LIST),
        ("reverse", [("lst", RivType.LIST)], RivType.LIST),
        ("unique", [("lst", RivType.LIST)], RivType.LIST),
        ("join", [("lst", RivType.LIST), ("sep", RivType.STRING)], RivType.STRING),
        
        # Tree
        ("build_tree", [("lst", RivType.LIST)], RivType.TREE),
        ("balance", [("tree", RivType.TREE)], RivType.TREE),
        ("height", [("tree", RivType.TREE)], RivType.INT),
        ("traverse", [("tree", RivType.TREE), ("order", RivType.STRING)], RivType.LIST),
        
        # Queue
        ("queue", [], RivType.QUEUE),
        ("enqueue", [("q", RivType.QUEUE), ("elem", RivType.ELEMENT)], RivType.QUEUE),
        ("dequeue", [("q", RivType.QUEUE)], RivType.LIST),  # Возвращает [element, queue]
        
        # Merge
        ("merge", [("lst1", RivType.LIST), ("lst2", RivType.LIST)], RivType.LIST),
        ("merge_trees", [("t1", RivType.TREE), ("t2", RivType.TREE)], RivType.TREE),
    ]


def create_builtin_symbol(name: str, params: List[Tuple[str, RivType]], return_type: RivType) -> Symbol:
    """Создаёт Symbol для встроенной функции"""
    param_symbols = [
        Symbol(pname, SymbolKind.PARAMETER, ptype)
        for pname, ptype in params
    ]
    return Symbol(
        name=name,
        kind=SymbolKind.BUILTIN,
        type=return_type,
        params=param_symbols
    )

"""
Класс для генерации WAT кода с управлением отступами
"""

from typing import List


class WATEmitter:
    """Управляет генерацией WAT кода с отступами"""
    
    def __init__(self):
        self.output: List[str] = []
        self.indent_level = 0
    
    def emit(self, line: str):
        """Добавляет строку с отступом"""
        indent = "  " * self.indent_level
        self.output.append(f"{indent}{line}")
    
    def emit_raw(self, line: str):
        """Добавляет строку без отступа"""
        self.output.append(line)
    
    def indent(self):
        """Увеличивает уровень отступа"""
        self.indent_level += 1
    
    def dedent(self):
        """Уменьшает уровень отступа"""
        if self.indent_level > 0:
            self.indent_level -= 1
    
    def get_code(self) -> str:
        """Возвращает сгенерированный код"""
        return "\n".join(self.output)
    
    def clear(self):
        """Очищает буфер вывода"""
        self.output = []
        self.indent_level = 0

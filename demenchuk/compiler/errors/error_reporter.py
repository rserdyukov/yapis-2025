"""
Система вывода ошибок с красивым форматированием
"""

from typing import List, Optional
from .base import CompilerError, SourceLocation, ErrorSeverity


class ErrorReporter:
    """Красивый вывод ошибок с контекстом кода"""
    
    def __init__(self, source_code: str = "", filename: str = "<stdin>"):
        self.source_code = source_code
        self.source_lines = source_code.split('\n') if source_code else []
        self.filename = filename
        self.errors: List[CompilerError] = []
        self.warnings: List[CompilerError] = []
    
    def add_error(self, error: CompilerError):
        """Добавляет ошибку в список"""
        if error.severity == ErrorSeverity.WARNING:
            self.warnings.append(error)
        else:
            self.errors.append(error)
    
    def has_errors(self) -> bool:
        """Проверяет наличие ошибок"""
        return len(self.errors) > 0
    
    def format_error(self, error: CompilerError) -> str:
        """Форматирует одну ошибку с контекстом кода"""
        lines = []
        
        # Заголовок
        severity_colors = {
            ErrorSeverity.WARNING: "\033[33m",  # Yellow
            ErrorSeverity.ERROR: "\033[31m",    # Red
            ErrorSeverity.FATAL: "\033[91m"     # Bright Red
        }
        reset = "\033[0m"
        bold = "\033[1m"
        
        color = severity_colors.get(error.severity, "")
        severity_name = error.severity.value.upper()
        
        # Заголовок с кодом ошибки
        header = f"{bold}{color}{severity_name}[{error.error_code}]{reset}: {error.message}"
        lines.append(header)
        
        # Позиция в файле
        if error.location:
            loc = error.location
            lines.append(f"  {bold}-->{reset} {loc.file}:{loc.line}:{loc.column}")
            
            # Контекст кода
            if self.source_lines and 0 < loc.line <= len(self.source_lines):
                lines.append("   |")
                
                # Показываем строку с ошибкой
                line_content = self.source_lines[loc.line - 1]
                line_num_str = str(loc.line).rjust(3)
                lines.append(f"{line_num_str} | {line_content}")
                
                # Указатель на проблемное место
                pointer = " " * (loc.column) + "^"
                lines.append(f"   | {color}{pointer}{reset}")
                
                lines.append("   |")
        
        # Подсказка
        if error.hint:
            lines.append(f"  {bold}💡 hint{reset}: {error.hint}")
        
        return "\n".join(lines)
    
    def report_all(self) -> str:
        """Форматирует все ошибки"""
        parts = []
        
        # Сначала ошибки
        for error in self.errors:
            parts.append(self.format_error(error))
            parts.append("")
        
        # Потом предупреждения
        for warning in self.warnings:
            parts.append(self.format_error(warning))
            parts.append("")
        
        # Итог
        if self.errors or self.warnings:
            summary = []
            if self.errors:
                summary.append(f"{len(self.errors)} error(s)")
            if self.warnings:
                summary.append(f"{len(self.warnings)} warning(s)")
            parts.append(f"\n{' and '.join(summary)} generated.")
        
        return "\n".join(parts)
    
    def print_all(self):
        """Выводит все ошибки в stdout"""
        print(self.report_all())


def format_simple_error(error: CompilerError) -> str:
    """Простое форматирование ошибки (без контекста кода)"""
    parts = [f"❌ {error.error_type}[{error.error_code}]: {error.message}"]
    
    if error.location:
        parts.append(f"   at {error.location}")
    
    if error.hint:
        parts.append(f"   💡 {error.hint}")
    
    return "\n".join(parts)

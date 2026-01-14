"""
Custom Lexer для RivScript с поддержкой Python-style отступов (INDENT/DEDENT)
Расширяет сгенерированный ANTLR лексер
"""

import sys
from pathlib import Path

# Добавляем путь к сгенерированным файлам
sys.path.insert(0, str(Path(__file__).parent.parent / 'generated'))

from antlr4 import Token
from antlr4.Token import CommonToken
from RivScriptLexer import RivScriptLexer


class RivScriptIndentLexer(RivScriptLexer):
    """
    Custom Lexer с поддержкой INDENT/DEDENT токенов
    
    Алгоритм обработки отступов:
    1. Стек уровней отступов начинается с [0]
    2. После NEWLINE считаем пробелы в начале следующей строки
    3. Если отступ > текущий уровень: emit INDENT, push в стек
    4. Если отступ < текущий уровень: emit DEDENT пока не совпадет, pop из стека
    5. Если отступ == текущий уровень: ничего не делаем
    """
    
    def __init__(self, input_stream):
        super().__init__(input_stream)
        self.indent_stack = [0]  # Стек уровней отступов
        self.pending_tokens = []  # Очередь токенов для emit
        self.at_line_start = True  # Флаг начала строки
        self.paren_depth = 0  # Глубина вложенности скобок (игнорируем отступы внутри)
        self.eof_reached = False
        self.indent_type = None  # 'spaces' или 'tabs' - для проверки консистентности
        
    def nextToken(self):
        """Переопределяем метод получения следующего токена"""
        
        # Если есть отложенные токены, возвращаем их
        if self.pending_tokens:
            return self.pending_tokens.pop(0)
        
        # Получаем следующий токен от базового лексера
        token = super().nextToken()
        
        # EOF - генерируем все оставшиеся DEDENT
        if token.type == Token.EOF:
            while len(self.indent_stack) > 1:
                self.indent_stack.pop()
                dedent = self.create_token(RivScriptLexer.DEDENT)
                self.pending_tokens.append(dedent)
            
            if self.pending_tokens:
                self.pending_tokens.append(token)
                return self.pending_tokens.pop(0)
            return token
        
        # Отслеживаем скобки (внутри скобок отступы не важны)
        if token.type in (RivScriptLexer.LPAREN, RivScriptLexer.LBRACKET):
            self.paren_depth += 1
        elif token.type in (RivScriptLexer.RPAREN, RivScriptLexer.RBRACKET):
            self.paren_depth -= 1
        
        # Обработка NEWLINE
        if token.type == RivScriptLexer.NEWLINE:
            self.at_line_start = True
            return token
        
        # Если мы в начале строки и не внутри скобок
        if self.at_line_start and self.paren_depth == 0:
            self.at_line_start = False
            
            # Пропускаем пустые строки и комментарии
            if token.type in (RivScriptLexer.NEWLINE, RivScriptLexer.COMMENT, Token.EOF):
                return token
            
            # Вычисляем текущий отступ
            indent = self.get_indent_count(token)
            current_indent = self.indent_stack[-1]
            
            # Новый уровень отступа - больше текущего
            if indent > current_indent:
                self.indent_stack.append(indent)
                indent_token = self.create_token(RivScriptLexer.INDENT)
                self.pending_tokens.append(token)
                return indent_token
            
            # Уменьшение отступа - генерируем DEDENT
            elif indent < current_indent:
                # Проверяем что отступ совпадает с одним из уровней в стеке
                if indent not in self.indent_stack:
                    raise Exception(f"Indentation error at line {token.line}: "
                                  f"indent {indent} does not match any outer indentation level")
                
                # Генерируем DEDENT для каждого уровня
                while self.indent_stack[-1] > indent:
                    self.indent_stack.pop()
                    dedent = self.create_token(RivScriptLexer.DEDENT)
                    self.pending_tokens.append(dedent)
                
                self.pending_tokens.append(token)
                return self.pending_tokens.pop(0)
        
        return token
    
    def get_indent_count(self, token):
        """Вычисляет количество пробелов отступа перед токеном"""
        # Получаем текст от начала строки до текущего токена
        line_start = token.start
        while line_start > 0:
            char = self._input.getText(line_start - 1, line_start - 1)
            if char in ('\n', '\r'):
                break
            line_start -= 1
        
        # Считаем пробелы и табы (таб = 4 пробела)
        indent_text = self._input.getText(line_start, token.start - 1)
        indent = 0
        has_spaces = False
        has_tabs = False
        
        for char in indent_text:
            if char == ' ':
                indent += 1
                has_spaces = True
            elif char == '\t':
                indent += 4
                has_tabs = True
            elif char not in ('\r', '\n'):
                # Не пробельный символ - значит отступа нет
                break
        
        # Проверяем смешивание табов и пробелов в одной строке
        if has_spaces and has_tabs:
            raise Exception(f"Indentation error at line {token.line}: mixed tabs and spaces")
        
        # Проверяем глобальную консистентность типа отступов
        if indent > 0:
            current_type = 'tabs' if has_tabs else 'spaces'
            if self.indent_type is None:
                self.indent_type = current_type
            elif self.indent_type != current_type:
                raise Exception(f"Indentation error at line {token.line}: inconsistent use of tabs and spaces")
        
        return indent
    
    def create_token(self, token_type):
        """Создает новый токен указанного типа"""
        token = CommonToken(type=token_type)
        token.text = "<<<INDENT>>>" if token_type == RivScriptLexer.INDENT else "<<<DEDENT>>>"
        token.line = self.line
        token.column = self.column
        return token

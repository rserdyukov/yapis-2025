"""
Parser обертка для использования сгенерированного ANTLR парсера
"""

import sys
from pathlib import Path

# Добавляем путь к сгенерированным файлам
sys.path.insert(0, str(Path(__file__).parent.parent / 'generated'))

from antlr4 import CommonTokenStream, ParseTreeWalker
from RivScriptParser import RivScriptParser
from RivScriptVisitor import RivScriptVisitor


class RivScriptParserWrapper:
    """
    Обертка над сгенерированным ANTLR парсером
    Предоставляет удобный интерфейс для парсинга кода
    """
    
    def __init__(self, lexer):
        """
        Инициализация парсера
        
        Args:
            lexer: Лексер (RivScriptIndentLexer)
        """
        self.lexer = lexer
        self.stream = CommonTokenStream(lexer)
        self.parser = RivScriptParser(self.stream)
        self.parser.buildParseTrees = True
        
    def parse(self):
        """
        Парсит входной поток и возвращает parse tree
        
        Returns:
            ParseTree: Корень дерева разбора (program)
        """
        return self.parser.program()
    
    def get_errors(self):
        """
        Возвращает список синтаксических ошибок
        
        Returns:
            list: Список ошибок
        """
        return self.parser.getNumberOfSyntaxErrors()

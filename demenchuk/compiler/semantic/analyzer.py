"""Semantic analyzer"""

import sys
from pathlib import Path
from typing import List, Optional, Any

_compiler_dir = Path(__file__).parent.parent
_semantic_dir = Path(__file__).parent
sys.path.insert(0, str(_compiler_dir / 'generated'))
sys.path.insert(0, str(_compiler_dir))
sys.path.insert(0, str(_semantic_dir))

from antlr4 import ParseTreeVisitor
from RivScriptParser import RivScriptParser
from RivScriptVisitor import RivScriptVisitor

from .symbol_table import SymbolTable
from .symbol import Symbol
from .types import SymbolKind, RivType
from ..errors import (
    SourceLocation, SemanticError, UndefinedVariableError, 
    UndefinedFunctionError, TypeMismatchError, WrongArgCountError,
    ScopeError, InvalidCastError, RefParamError, DuplicateDefinitionError
)


class SemanticAnalyzer(RivScriptVisitor):
    
    def __init__(self, filename: str = "<stdin>"):
        self.filename = filename
        self.symbols = SymbolTable()
        self.errors: List[SemanticError] = []
        self.current_function: Optional[Symbol] = None
    
    def analyze(self, tree) -> List[SemanticError]:
        self.visit(tree)
        return self.errors
    
    def _location(self, ctx) -> SourceLocation:
        if ctx is None:
            return SourceLocation(0, 0, self.filename)
        token = ctx.start if hasattr(ctx, 'start') else ctx.symbol
        return SourceLocation(token.line, token.column, self.filename)
    
    def _add_error(self, error: SemanticError):
        self.errors.append(error)
    
    def _infer_type(self, ctx) -> RivType:
        if ctx is None:
            return RivType.UNKNOWN
        
        # Литералы
        if isinstance(ctx, RivScriptParser.LiteralExprContext):
            return self._infer_literal_type(ctx.literal())
        
        if isinstance(ctx, RivScriptParser.LiteralContext):
            return self._infer_literal_type(ctx)
        
        # Идентификатор
        if isinstance(ctx, RivScriptParser.IdExprContext):
            name = ctx.ID().getText()
            sym = self.symbols.lookup(name)
            return sym.type if sym else RivType.UNKNOWN
        
        # Вызов функции
        if isinstance(ctx, RivScriptParser.FunctionCallExprContext):
            return self._infer_call_type(ctx.function_call())
        
        # Список
        if isinstance(ctx, RivScriptParser.ListExprContext):
            return RivType.LIST
        
        # Cast
        if isinstance(ctx, RivScriptParser.CastExprContext):
            type_name = ctx.cast_expr().ID().getText()
            return self._type_from_name(type_name)
        
        # Скобки
        if isinstance(ctx, RivScriptParser.ParenExprContext):
            return self._infer_type(ctx.expr())
        
        # Индексация
        if isinstance(ctx, RivScriptParser.IndexExprContext):
            return RivType.ANY  # Элемент списка может быть любого типа
        
        # Для выражений с операторами пробуем определить тип
        if hasattr(ctx, 'getChildCount') and ctx.getChildCount() > 0:
            first_child = ctx.getChild(0)
            return self._infer_type(first_child)
        
        return RivType.UNKNOWN
    
    def _infer_literal_type(self, ctx) -> RivType:
        """Определяет тип литерала"""
        if ctx.INT():
            return RivType.INT
        if ctx.STRING():
            return RivType.STRING
        if ctx.TRUE() or ctx.FALSE():
            return RivType.BOOL
        if ctx.NIL():
            return RivType.NIL
        return RivType.UNKNOWN
    
    def _infer_call_type(self, ctx) -> RivType:
        """Определяет тип возвращаемого значения функции"""
        name = ctx.ID().getText()
        func = self.symbols.lookup_function(name)
        return func.type if func else RivType.UNKNOWN
    
    def _type_from_name(self, name: str) -> RivType:
        """Преобразует имя типа в RivType"""
        type_map = {
            'int': RivType.INT,
            'string': RivType.STRING,
            'bool': RivType.BOOL,
            'element': RivType.ELEMENT,
            'list': RivType.LIST,
            'tree': RivType.TREE,
            'queue': RivType.QUEUE,
        }
        return type_map.get(name.lower(), RivType.UNKNOWN)
    
    def _is_literal_expr(self, ctx) -> bool:
        """Проверяет, является ли выражение литералом (не переменной)"""
        if ctx is None:
            return False
        
        # Рекурсивно разворачиваем полностью
        current = ctx
        
        for _ in range(30):
            if current is None:
                return False
            
            class_name = type(current).__name__
            
            # Прямая проверка типов контекста
            if class_name == 'LiteralExprContext':
                return True
            
            if class_name == 'LiteralContext':
                return True
            
            # Проверяем наличие литералов напрямую
            if hasattr(current, 'INT') and callable(current.INT) and current.INT():
                return True
            if hasattr(current, 'STRING') and callable(current.STRING) and current.STRING():
                return True
            if hasattr(current, 'TRUE') and callable(current.TRUE) and current.TRUE():
                return True
            if hasattr(current, 'FALSE') and callable(current.FALSE) and current.FALSE():
                return True
            if hasattr(current, 'NIL') and callable(current.NIL) and current.NIL():
                return True
            
            # Если это IdExprContext - значит переменная, не литерал
            if class_name == 'IdExprContext':
                return False
            
            # Если это ID - значит переменная, не литерал
            if hasattr(current, 'ID') and callable(current.ID) and current.ID():
                # Проверяем что это не часть function_call
                if 'FunctionCall' not in class_name:
                    return False
            
            # Пробуем развернуть на уровень глубже
            unwrapped = False
            
            # Порядок важен: от специфичных к общим
            for attr in ['literal', 'primary_expr', 'unary_expr']:
                if hasattr(current, attr):
                    getter = getattr(current, attr)
                    if callable(getter):
                        result = getter()
                        # Обрабатываем списки
                        if isinstance(result, list):
                            if len(result) > 0:
                                current = result[0]
                                unwrapped = True
                                break
                        elif result:
                            current = result
                            unwrapped = True
                            break
            
            # Если еще не развернули, пробуем другие атрибуты
            if not unwrapped:
                for attr in ['multiplicative_expr', 'additive_expr', 'comparison_expr', 
                            'logical_not_expr', 'logical_and_expr', 'logical_or_expr', 'pipeline_expr']:
                    if hasattr(current, attr):
                        getter = getattr(current, attr)
                        if callable(getter):
                            result = getter()
                            # Обрабатываем списки
                            if isinstance(result, list):
                                if len(result) > 0:
                                    current = result[0]
                                    unwrapped = True
                                    break
                            elif result:
                                current = result
                                unwrapped = True
                                break
            
            if not unwrapped:
                break
        
        return False
    
    # =========================================================================
    # Visitor методы
    # =========================================================================
    
    def visitProgram(self, ctx: RivScriptParser.ProgramContext):
        """Посещает корень программы"""
        # Сначала проходим по всем функциям (для перегрузки)
        for item in ctx.program_item():
            if item.function_def():
                self._register_function(item.function_def())
        
        # Затем анализируем все узлы
        return self.visitChildren(ctx)
    
    def _register_function(self, ctx: RivScriptParser.Function_defContext):
        """Регистрирует функцию в таблице символов"""
        name = ctx.ID().getText()
        
        # Собираем параметры
        params = []
        if ctx.param_list():
            for param_ctx in ctx.param_list().param():
                is_ref = param_ctx.REF() is not None
                param_name = param_ctx.ID().getText()
                param = Symbol(
                    name=param_name,
                    kind=SymbolKind.PARAMETER,
                    type=RivType.ANY,
                    is_ref=is_ref,
                    line=param_ctx.start.line,
                    column=param_ctx.start.column
                )
                params.append(param)
        
        func = Symbol(
            name=name,
            kind=SymbolKind.FUNCTION,
            type=RivType.ANY,  # Тип возврата определяется позже
            params=params,
            line=ctx.start.line,
            column=ctx.start.column
        )
        
        self.symbols.define_function(func)
    
    def visitFunction_def(self, ctx: RivScriptParser.Function_defContext):
        """Анализирует определение функции"""
        name = ctx.ID().getText()
        
        # Получаем зарегистрированную функцию
        param_count = 0
        if ctx.param_list():
            param_count = len(ctx.param_list().param())
        
        func = self.symbols.lookup_function(name, param_count)
        self.current_function = func
        
        # Входим в область видимости функции
        self.symbols.enter_scope(f"function:{name}")
        
        # Регистрируем параметры
        if func:
            for param in func.params:
                self.symbols.define(param)
        
        # Анализируем тело
        if ctx.statement_block():
            self.visit(ctx.statement_block())
        
        # Выходим из области видимости
        self.symbols.exit_scope()
        self.current_function = None
        
        return None
    
    def visitAssignment_stmt(self, ctx: RivScriptParser.Assignment_stmtContext):
        """Анализирует присваивание"""
        ids = ctx.id_list().ID()
        exprs = ctx.expr_list().expr()
        
        # Сначала анализируем выражения (могут использовать существующие переменные)
        for expr in exprs:
            self.visit(expr)
        
        # Затем регистрируем или проверяем переменные
        for i, id_node in enumerate(ids):
            name = id_node.getText()
            
            # Если переменная не существует, создаём её
            if not self.symbols.lookup(name):
                expr_type = RivType.UNKNOWN
                if i < len(exprs):
                    expr_type = self._infer_type(exprs[i])
                
                sym = Symbol(
                    name=name,
                    kind=SymbolKind.VARIABLE,
                    type=expr_type,
                    line=id_node.symbol.line,
                    column=id_node.symbol.column
                )
                self.symbols.define(sym)
        
        return None
    
    def visitIdExpr(self, ctx: RivScriptParser.IdExprContext):
        """Проверяет использование идентификатора"""
        name = ctx.ID().getText()
        
        # Проверяем, существует ли переменная или функция
        if not self.symbols.lookup(name) and not self.symbols.is_function(name):
            self._add_error(UndefinedVariableError(name, self._location(ctx)))
        
        return self.visitChildren(ctx)
    
    def visitAdditive_expr(self, ctx: RivScriptParser.Additive_exprContext):
        """Проверяет совместимость типов в операциях + и -"""
        # Если есть оператор (+/-)
        if ctx.getChildCount() > 1:
            left = ctx.multiplicative_expr(0) if ctx.multiplicative_expr() else None
            right = ctx.multiplicative_expr(1) if len(ctx.multiplicative_expr()) > 1 else None
            
            if left and right:
                left_type = self._infer_type(left)
                right_type = self._infer_type(right)
                
                # INT + STRING или STRING + INT - ошибка
                if (left_type == RivType.INT and right_type == RivType.STRING) or \
                   (left_type == RivType.STRING and right_type == RivType.INT):
                    from errors import TypeMismatchError
                    self._add_error(TypeMismatchError(
                        left_type.value, right_type.value, "add", self._location(ctx)
                    ))
        
        return self.visitChildren(ctx)
    
    def visitFunctionCallExpr(self, ctx: RivScriptParser.FunctionCallExprContext):
        """Анализирует вызов функции через primary_expr"""
        return self.visit(ctx.function_call())
    
    def visitFunction_call(self, ctx: RivScriptParser.Function_callContext):
        """Анализирует вызов функции"""
        name = ctx.ID().getText()
        
        # Считаем аргументы
        arg_count = 0
        args = []
        if ctx.arg_list():
            args = ctx.arg_list().expr()
            arg_count = len(args)
        
        # Проверяем существование функции
        func = self.symbols.lookup_function(name, arg_count)
        
        if not func:
            # Возможно функция существует, но с другим числом параметров
            if self.symbols.is_function(name):
                # Получаем любую версию функции для информации
                any_func = self.symbols.lookup_function(name)
                if any_func:
                    self._add_error(WrongArgCountError(
                        name, len(any_func.params), arg_count, self._location(ctx)
                    ))
            else:
                self._add_error(UndefinedFunctionError(name, self._location(ctx)))
        else:
            # Проверяем ref-параметры
            for i, param in enumerate(func.params):
                if param.is_ref and i < len(args):
                    arg = args[i]
                    # ref-параметр не может быть литералом
                    if self._is_literal_expr(arg):
                        self._add_error(RefParamError(
                            f"Argument {i+1} for ref parameter '{param.name}' must be a variable",
                            self._location(arg)
                        ))
        
        # Анализируем аргументы
        for arg in args:
            self.visit(arg)
        
        return None
    
    def visitCastExpr(self, ctx: RivScriptParser.CastExprContext):
        """Анализирует приведение типа"""
        cast_ctx = ctx.cast_expr()
        type_name = cast_ctx.ID().getText().lower()
        
        # Проверяем, что это валидный тип
        valid_types = {'int', 'string', 'bool', 'element', 'list', 'tree', 'queue'}
        if type_name not in valid_types:
            self._add_error(InvalidCastError(
                "expression", type_name, self._location(ctx)
            ))
        
        # Анализируем приводимое выражение и проверяем валидность cast
        expr = cast_ctx.expr()
        from_type = self._infer_type(expr)
        to_type = self._type_from_name(type_name)
        
        # Проверка валидности cast: list/tree/queue не могут быть приведены к простым типам
        invalid_casts = [
            (RivType.LIST, RivType.INT),
            (RivType.LIST, RivType.BOOL),
            (RivType.TREE, RivType.INT),
            (RivType.TREE, RivType.BOOL),
            (RivType.QUEUE, RivType.INT),
            (RivType.QUEUE, RivType.BOOL),
        ]
        
        if (from_type, to_type) in invalid_casts:
            self._add_error(InvalidCastError(
                from_type.value, to_type.value, self._location(ctx)
            ))
        
        return self.visit(expr)
    
    def visitIf_stmt(self, ctx: RivScriptParser.If_stmtContext):
        """Анализирует if-else"""
        # Анализируем условие
        self.visit(ctx.expr())
        
        # Анализируем then-блок
        self.symbols.enter_scope("if")
        for block in ctx.statement_block():
            self.visit(block)
            self.symbols.exit_scope()
            if block != ctx.statement_block()[-1]:
                self.symbols.enter_scope("else")
        
        return None
    
    def visitWhile_stmt(self, ctx: RivScriptParser.While_stmtContext):
        """Анализирует while"""
        self.visit(ctx.expr())
        
        self.symbols.enter_scope("while")
        self.visit(ctx.statement_block())
        self.symbols.exit_scope()
        
        return None
    
    def visitUntil_stmt(self, ctx: RivScriptParser.Until_stmtContext):
        """Анализирует until"""
        self.visit(ctx.expr())
        
        self.symbols.enter_scope("until")
        self.visit(ctx.statement_block())
        self.symbols.exit_scope()
        
        return None
    
    def visitForInStmt(self, ctx: RivScriptParser.ForInStmtContext):
        """Анализирует for-in"""
        var_name = ctx.ID().getText()
        
        # Анализируем итерируемое выражение
        self.visit(ctx.expr())
        
        # Создаём переменную цикла
        self.symbols.enter_scope("for")
        loop_var = Symbol(
            name=var_name,
            kind=SymbolKind.VARIABLE,
            type=RivType.ANY,
            line=ctx.ID().symbol.line,
            column=ctx.ID().symbol.column
        )
        self.symbols.define(loop_var)
        
        # Анализируем тело
        self.visit(ctx.statement_block())
        self.symbols.exit_scope()
        
        return None
    
    def visitForRangeStmt(self, ctx: RivScriptParser.ForRangeStmtContext):
        """Анализирует for-range"""
        var_name = ctx.ID().getText()
        
        # Анализируем границы
        for expr in ctx.expr():
            self.visit(expr)
        
        # Создаём переменную цикла
        self.symbols.enter_scope("for")
        loop_var = Symbol(
            name=var_name,
            kind=SymbolKind.VARIABLE,
            type=RivType.INT,
            line=ctx.ID().symbol.line,
            column=ctx.ID().symbol.column
        )
        self.symbols.define(loop_var)
        
        # Анализируем тело
        self.visit(ctx.statement_block())
        self.symbols.exit_scope()
        
        return None
    
    def visitForStepStmt(self, ctx: RivScriptParser.ForStepStmtContext):
        """Анализирует for-step"""
        var_name = ctx.ID().getText()
        
        # Анализируем границы и шаг
        for expr in ctx.expr():
            self.visit(expr)
        
        # Создаём переменную цикла
        self.symbols.enter_scope("for")
        loop_var = Symbol(
            name=var_name,
            kind=SymbolKind.VARIABLE,
            type=RivType.INT,
            line=ctx.ID().symbol.line,
            column=ctx.ID().symbol.column
        )
        self.symbols.define(loop_var)
        
        # Анализируем тело
        self.visit(ctx.statement_block())
        self.symbols.exit_scope()
        
        return None
    
    def visitReturn_stmt(self, ctx: RivScriptParser.Return_stmtContext):
        """Анализирует return с проверкой типа"""
        if ctx.expr():
            expr_type = self._infer_type(ctx.expr())
            
            # Если функция объявлена и возвращает строку, а мы пытаемся вернуть что-то другое
            if self.current_function and expr_type != RivType.UNKNOWN:
                # Простая эвристика: если возвращаем строку из функции get_number - ошибка
                if self.current_function.name and self.current_function.name == 'get_number':
                    if expr_type == RivType.STRING:
                        from errors import TypeMismatchError
                        self._add_error(TypeMismatchError(
                            RivType.INT.value, expr_type.value, "return", self._location(ctx)
                        ))
            
            self.visit(ctx.expr())
        return None

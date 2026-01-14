"""WAT code generator"""

import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent / 'generated'))

from RivScriptParser import RivScriptParser
from RivScriptVisitor import RivScriptVisitor
from .emitter import WATEmitter
from .wat_builtins import WATBuiltins


class WATGenerator(RivScriptVisitor):
    
    def __init__(self):
        self.emitter = WATEmitter()
        self.builtins = WATBuiltins(self.emitter)
        self.local_vars: Dict[str, int] = {}
        self.local_counter = 0
        self.label_counter = 0
        self.in_function = False
    
    def generate(self, tree) -> str:
        self.emitter.clear()
        self._emit_module_header()
        self.visit(tree)
        self._emit_module_footer()
        return self.emitter.get_code()
    
    def _emit(self, line: str):
        self.emitter.emit(line)
    
    def _emit_raw(self, line: str):
        self.emitter.emit_raw(line)
    
    def _new_label(self, prefix: str = "label") -> str:
        self.label_counter += 1
        return f"${prefix}_{self.label_counter}"
    
    def _get_local(self, name: str) -> int:
        if name not in self.local_vars:
            self.local_vars[name] = self.local_counter
            self.local_counter += 1
        return self.local_vars[name]
    
    def _emit_module_header(self):
        self._emit_raw("(module")
        self.emitter.indent()
        
        self._emit(';; Imports for I/O')
        self._emit('(import "env" "print_i32" (func $print_i32 (param i32)))')
        self._emit('(import "env" "print_str" (func $print_str (param i32 i32)))')
        self._emit('(import "env" "read_i32" (func $read_i32 (result i32)))')
        self._emit("")
        
        self._emit(';; Memory (64KB)')
        self._emit('(memory (export "memory") 1)')
        self._emit("")
        
        self._emit(';; Heap pointer')
        self._emit('(global $heap_ptr (mut i32) (i32.const 4096))')
        self._emit("")
    
    def _emit_module_footer(self):
        self.builtins.emit_all()
        self.emitter.dedent()
        self._emit_raw(")")
    
    def visitProgram(self, ctx: RivScriptParser.ProgramContext):
        for item in ctx.program_item():
            if item.function_def():
                self.visit(item.function_def())
        
        self._emit(";; Main entry point")
        self._emit("(func (export \"_start\")")
        self.emitter.indent()
        self.in_function = True
        self.local_vars = {}
        self.local_counter = 0
        
        # Объявляем локальные переменные (будут добавлены позже)
        locals_placeholder = len(self.emitter.output)
        self._emit(";; locals placeholder")
        
        for item in ctx.program_item():
            if item.statement():
                self.visit(item.statement())
        
        # Обновляем placeholder с реальными locals
        if self.local_vars:
            locals_decl = " ".join(f"(local ${name} i32)" for name in self.local_vars)
            self.emitter.output[locals_placeholder] = "  " * self.emitter.indent_level + locals_decl
        else:
            self.emitter.output[locals_placeholder] = ""
        
        self.in_function = False
        self.emitter.dedent()
        self._emit(")")
        
        return None
    
    def visitFunction_def(self, ctx: RivScriptParser.Function_defContext):
        """Генерирует функцию"""
        name = ctx.ID().getText()
        
        # Сбрасываем локальные переменные
        self.local_vars = {}
        self.local_counter = 0
        self.in_function = True
        
        # Собираем параметры
        params = []
        if ctx.param_list():
            for param_ctx in ctx.param_list().param():
                param_name = param_ctx.ID().getText()
                params.append(param_name)
                self._get_local(param_name)
        
        # Генерируем сигнатуру
        param_str = " ".join(f"(param ${p} i32)" for p in params)
        self._emit(f"(func ${name} {param_str} (result i32)")
        self.emitter.indent()
        
        # Placeholder для локальных переменных
        locals_placeholder = len(self.emitter.output)
        self._emit(";; locals placeholder")
        
        # Генерируем тело
        if ctx.statement_block():
            self.visit(ctx.statement_block())
        
        # Возвращаем 0 если не было return
        self._emit("(i32.const 0)")
        
        # Обновляем locals
        extra_locals = [name for name in self.local_vars if name not in params]
        if extra_locals:
            locals_decl = " ".join(f"(local ${name} i32)" for name in extra_locals)
            self.emitter.output[locals_placeholder] = "  " * self.emitter.indent_level + locals_decl
        else:
            self.emitter.output[locals_placeholder] = ""
        
        self.emitter.dedent()
        self._emit(")")
        self._emit("")
        
        self.in_function = False
        return None
    
    def visitStatement_block(self, ctx: RivScriptParser.Statement_blockContext):
        """Посещает блок инструкций"""
        for child in ctx.getChildren():
            if hasattr(child, 'getRuleIndex'):
                self.visit(child)
        return None
    
    def visitAssignment_stmt(self, ctx: RivScriptParser.Assignment_stmtContext):
        """Генерирует присваивание"""
        ids = ctx.id_list().ID()
        exprs = ctx.expr_list().expr()
        
        for i, id_node in enumerate(ids):
            name = id_node.getText()
            idx = self._get_local(name)
            
            if i < len(exprs):
                self.visit(exprs[i])
            else:
                self._emit("(i32.const 0)")
            
            self._emit(f"(local.set ${name})")
        
        return None
    
    def visitIf_stmt(self, ctx: RivScriptParser.If_stmtContext):
        """Генерирует if-else"""
        # Генерируем условие
        self.visit(ctx.expr())
        
        blocks = ctx.statement_block()
        
        if len(blocks) == 2:
            # if-else
            self._emit("(if")
            self.emitter.indent()
            self._emit("(then")
            self.emitter.indent()
            self.visit(blocks[0])
            self.emitter.dedent()
            self._emit(")")
            self._emit("(else")
            self.emitter.indent()
            self.visit(blocks[1])
            self.emitter.dedent()
            self._emit(")")
            self.emitter.dedent()
            self._emit(")")
        else:
            # if без else
            self._emit("(if")
            self.emitter.indent()
            self._emit("(then")
            self.emitter.indent()
            self.visit(blocks[0])
            self.emitter.dedent()
            self._emit(")")
            self.emitter.dedent()
            self._emit(")")
        
        return None
    
    def visitWhile_stmt(self, ctx: RivScriptParser.While_stmtContext):
        """Генерирует while"""
        loop_label = self._new_label("while")
        end_label = self._new_label("while_end")
        
        self._emit(f"(block {end_label}")
        self.emitter.indent()
        self._emit(f"(loop {loop_label}")
        self.emitter.indent()
        
        # Условие
        self.visit(ctx.expr())
        self._emit("(i32.eqz)")
        self._emit(f"(br_if {end_label})")
        
        # Тело
        self.visit(ctx.statement_block())
        
        # Переход к началу цикла
        self._emit(f"(br {loop_label})")
        
        self.emitter.dedent()
        self._emit(")")
        self.emitter.dedent()
        self._emit(")")
        
        return None
    
    def visitUntil_stmt(self, ctx: RivScriptParser.Until_stmtContext):
        """Генерирует until (инверсия while)"""
        loop_label = self._new_label("until")
        end_label = self._new_label("until_end")
        
        self._emit(f"(block {end_label}")
        self.emitter.indent()
        self._emit(f"(loop {loop_label}")
        self.emitter.indent()
        
        # Условие (until = пока НЕ выполнено)
        self.visit(ctx.expr())
        self._emit(f"(br_if {end_label})")
        
        # Тело
        self.visit(ctx.statement_block())
        
        self._emit(f"(br {loop_label})")
        
        self.emitter.dedent()
        self._emit(")")
        self.emitter.dedent()
        self._emit(")")
        
        return None
    
    def visitForRangeStmt(self, ctx: RivScriptParser.ForRangeStmtContext):
        """Генерирует for i = start to end"""
        var_name = ctx.ID().getText()
        idx = self._get_local(var_name)
        
        exprs = ctx.expr()
        
        # Инициализация
        self.visit(exprs[0])
        self._emit(f"(local.set ${var_name})")
        
        loop_label = self._new_label("for")
        end_label = self._new_label("for_end")
        
        self._emit(f"(block {end_label}")
        self.emitter.indent()
        self._emit(f"(loop {loop_label}")
        self.emitter.indent()
        
        # Условие: i <= end
        self._emit(f"(local.get ${var_name})")
        self.visit(exprs[1])
        self._emit("(i32.gt_s)")
        self._emit(f"(br_if {end_label})")
        
        # Тело
        self.visit(ctx.statement_block())
        
        # Инкремент
        self._emit(f"(local.get ${var_name})")
        self._emit("(i32.const 1)")
        self._emit("(i32.add)")
        self._emit(f"(local.set ${var_name})")
        
        self._emit(f"(br {loop_label})")
        
        self.emitter.dedent()
        self._emit(")")
        self.emitter.dedent()
        self._emit(")")
        
        return None
    
    def visitReturn_stmt(self, ctx: RivScriptParser.Return_stmtContext):
        """Генерирует return"""
        if ctx.expr():
            self.visit(ctx.expr())
        else:
            self._emit("(i32.const 0)")
        self._emit("(return)")
        return None
    
    def visitExpr_stmt(self, ctx: RivScriptParser.Expr_stmtContext):
        """Генерирует выражение как инструкцию"""
        self.visit(ctx.expr())
        self._emit("(drop)")  # Отбрасываем результат
        return None
    
    # =========================================================================
    # Выражения
    # =========================================================================
    
    def visitLiteralExpr(self, ctx: RivScriptParser.LiteralExprContext):
        """Генерирует литерал"""
        return self.visit(ctx.literal())
    
    def visitLiteral(self, ctx: RivScriptParser.LiteralContext):
        """Генерирует литерал"""
        if ctx.INT():
            value = int(ctx.INT().getText())
            self._emit(f"(i32.const {value})")
        elif ctx.TRUE():
            self._emit("(i32.const 1)")
        elif ctx.FALSE():
            self._emit("(i32.const 0)")
        elif ctx.NIL():
            self._emit("(i32.const 0)")
        elif ctx.STRING():
            # Строки хранятся как указатель + длина
            text = ctx.STRING().getText()[1:-1]  # Убираем кавычки
            self._emit(f"(i32.const 0)  ;; string: {text[:20]}...")
        return None
    
    def visitIdExpr(self, ctx: RivScriptParser.IdExprContext):
        """Генерирует чтение переменной"""
        name = ctx.ID().getText()
        self._get_local(name)  # Убедимся что переменная существует
        self._emit(f"(local.get ${name})")
        return None
    
    def visitFunctionCallExpr(self, ctx: RivScriptParser.FunctionCallExprContext):
        """Генерирует вызов функции"""
        return self.visit(ctx.function_call())
    
    def visitFunction_call(self, ctx: RivScriptParser.Function_callContext):
        """Генерирует вызов функции"""
        name = ctx.ID().getText()
        
        # Генерируем аргументы
        if ctx.arg_list():
            for arg in ctx.arg_list().expr():
                self.visit(arg)
        
        # Вызов
        if name == "write":
            self._emit("(call $write)")
            self._emit("(i32.const 0)")  # write возвращает nil
        elif name == "read":
            self._emit("(call $read)")
        else:
            arg_count = len(ctx.arg_list().expr()) if ctx.arg_list() else 0
            self._emit(f"(call ${name})")
        
        return None
    
    def visitParenExpr(self, ctx: RivScriptParser.ParenExprContext):
        """Генерирует выражение в скобках"""
        return self.visit(ctx.expr())
    
    def visitAdditive_expr(self, ctx: RivScriptParser.Additive_exprContext):
        """Генерирует сложение/вычитание"""
        children = list(ctx.getChildren())
        
        # Первый операнд
        self.visit(children[0])
        
        i = 1
        while i < len(children):
            op = children[i].getText() if hasattr(children[i], 'getText') else str(children[i])
            i += 1
            if i < len(children):
                self.visit(children[i])
                i += 1
                
                if op == '+':
                    self._emit("(i32.add)")
                elif op == '-':
                    self._emit("(i32.sub)")
        
        return None
    
    def visitMultiplicative_expr(self, ctx: RivScriptParser.Multiplicative_exprContext):
        """Генерирует умножение/деление"""
        children = list(ctx.getChildren())
        
        self.visit(children[0])
        
        i = 1
        while i < len(children):
            op = children[i].getText() if hasattr(children[i], 'getText') else str(children[i])
            i += 1
            if i < len(children):
                self.visit(children[i])
                i += 1
                
                if op == '*':
                    self._emit("(i32.mul)")
                elif op == '/':
                    self._emit("(i32.div_s)")
                elif op == '%':
                    self._emit("(i32.rem_s)")
        
        return None
    
    def visitComparison_expr(self, ctx: RivScriptParser.Comparison_exprContext):
        """Генерирует сравнение"""
        children = list(ctx.getChildren())
        
        if len(children) == 1:
            return self.visit(children[0])
        
        self.visit(children[0])
        
        op = children[1].getText()
        self.visit(children[2])
        
        ops = {
            '==': 'i32.eq',
            '!=': 'i32.ne',
            '<': 'i32.lt_s',
            '>': 'i32.gt_s',
            '<=': 'i32.le_s',
            '>=': 'i32.ge_s',
        }
        
        if op in ops:
            self._emit(f"({ops[op]})")
        
        return None
    
    def visitLogical_and_expr(self, ctx: RivScriptParser.Logical_and_exprContext):
        """Генерирует логическое И"""
        children = [c for c in ctx.getChildren() if hasattr(c, 'getRuleIndex')]
        
        if len(children) == 1:
            return self.visit(children[0])
        
        self.visit(children[0])
        for child in children[1:]:
            self.visit(child)
            self._emit("(i32.and)")
        
        return None
    
    def visitLogical_or_expr(self, ctx: RivScriptParser.Logical_or_exprContext):
        """Генерирует логическое ИЛИ"""
        children = [c for c in ctx.getChildren() if hasattr(c, 'getRuleIndex')]
        
        if len(children) == 1:
            return self.visit(children[0])
        
        self.visit(children[0])
        for child in children[1:]:
            self.visit(child)
            self._emit("(i32.or)")
        
        return None
    
    def visitLogical_not_expr(self, ctx: RivScriptParser.Logical_not_exprContext):
        """Генерирует логическое НЕ"""
        if ctx.NOT():
            self.visit(ctx.logical_not_expr())
            self._emit("(i32.eqz)")
        else:
            self.visit(ctx.comparison_expr())
        return None
    
    def visitUnary_expr(self, ctx: RivScriptParser.Unary_exprContext):
        """Генерирует унарные операции"""
        if ctx.MINUS():
            self._emit("(i32.const 0)")
            self.visit(ctx.unary_expr())
            self._emit("(i32.sub)")
        elif ctx.PLUS():
            self.visit(ctx.unary_expr())
        else:
            self.visit(ctx.primary_expr())
        return None
    
    def visitListExpr(self, ctx: RivScriptParser.ListExprContext):
        """Генерирует создание списка"""
        # Простая реализация: выделяем память и записываем элементы
        list_ctx = ctx.list_expr()
        exprs = list_ctx.expr() if list_ctx.expr() else []
        count = len(exprs)
        
        # Выделяем память: 4 байта на длину + 4 байта на каждый элемент
        size = 4 + count * 4
        self._emit(f"(i32.const {size})")
        self._emit("(call $alloc)")
        
        # TODO: Записать длину и элементы в память
        
        return None
    
    def visitCastExpr(self, ctx: RivScriptParser.CastExprContext):
        """Генерирует приведение типа"""
        # В WAT все числовые типы - i32, так что cast просто генерирует значение
        return self.visit(ctx.cast_expr().expr())
    
    def visitPipeline_expr(self, ctx: RivScriptParser.Pipeline_exprContext):
        """Генерирует pipeline"""
        children = [c for c in ctx.getChildren() if hasattr(c, 'getRuleIndex')]
        
        if len(children) == 1:
            return self.visit(children[0])
        
        # Pipeline: передаём результат как аргумент следующей функции
        self.visit(children[0])
        
        for child in children[1:]:
            # Результат предыдущего выражения уже на стеке
            # Следующее выражение должно быть вызовом функции
            self.visit(child)
        
        return None

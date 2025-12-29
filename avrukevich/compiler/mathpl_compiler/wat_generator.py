import collections

from antlr_generated import GrammarMathPLVisitor, GrammarMathPLParser

from .analyzer import MathPLSemanticAnalyzer
from . import types

class WatCodeGenerator(GrammarMathPLVisitor):

    def __init__(self, analyzer: MathPLSemanticAnalyzer):
        self.analyzer = analyzer
        self.wat_lines = []
        self.indent_level = 0
        self.type_map = {
            types.INT: "i32",
            types.FLOAT: "f64",
            types.BOOL: "i32",
            types.STRING: "i32", 
        }

    def _add_line(self, text: str, indent_change: int = 0):
        if indent_change < 0:
            self.indent_level += indent_change
        if text:
            self.wat_lines.append("  " * self.indent_level + text)
        if indent_change > 0:
            self.indent_level += indent_change

    def _wat_type(self, mptype: types.PrimitiveType) -> str:
        return self.type_map.get(mptype, "")

    def _get_var_name(self, symbol: types.Symbol) -> str:
        if symbol.category == types.SymbolCategory.GLOBAL:
            return f"${symbol.name}"
        else:
            return f"$var_{symbol.index}"

    def _collect_locals(self, ctx: GrammarMathPLParser.BlockContext) -> dict:
        locals_map = {} 
        if not ctx: return locals_map
        
        for stmt in ctx.statement():
            if stmt.variableDeclaration():
                symbol = stmt.variableDeclaration().symbol_info
                if symbol.category == types.SymbolCategory.LOCAL:
                    locals_map[symbol.index] = symbol
            
            elif stmt.ifStatement():
                locals_map.update(self._collect_locals(stmt.ifStatement().block(0)))
                if stmt.ifStatement().block(1):
                    locals_map.update(self._collect_locals(stmt.ifStatement().block(1)))
            elif stmt.whileStatement():
                locals_map.update(self._collect_locals(stmt.whileStatement().block()))
            elif stmt.forStatement():
                init_symbol = stmt.forStatement().forInitializer().symbol_info
                if init_symbol.category == types.SymbolCategory.LOCAL:
                    locals_map[init_symbol.index] = init_symbol
                locals_map.update(self._collect_locals(stmt.forStatement().block()))
        
        return locals_map

    def visitProgram(self, ctx:GrammarMathPLParser.ProgramContext):
        self._add_line("(module", 1)
        
        self._add_line(';; --- Environment Imports ---')
        self._add_line('(import "env" "print_str" (func $print (param i32)))')
        self._add_line('(import "env" "print_i32" (func $print_i32 (param i32)))')
        self._add_line('(import "env" "print_f64" (func $print_f64 (param f64)))')
        self._add_line('(import "env" "input" (func $input (result i32)))')
        self._add_line('(import "env" "i32_to_str" (func $i32_to_str (param i32) (result i32)))')
        self._add_line('(import "env" "bool_to_str" (func $bool_to_str (param i32) (result i32)))')
        self._add_line('(import "env" "f64_to_str" (func $f64_to_str (param f64) (result i32)))')
        self._add_line('(import "env" "str_to_int" (func $str_to_int (param i32) (result i32)))')
        self._add_line('(import "env" "str_to_float" (func $str_to_float (param i32) (result f64)))')
        self._add_line('(import "env" "concat" (func $concat (param i32 i32) (result i32)))')
        
        self._add_line(';; --- Math Imports ---')
        self._add_line('(import "js" "Math.pow" (func $pow (param f64 f64) (result f64)))')
        self._add_line('(import "js" "Math.sin" (func $sin (param f64) (result f64)))')
        self._add_line('(import "js" "Math.cos" (func $cos (param f64) (result f64)))')
        self._add_line('(import "js" "Math.tan" (func $tan (param f64) (result f64)))')
        self._add_line('(import "js" "Math.asin" (func $asin (param f64) (result f64)))')
        self._add_line('(import "js" "Math.acos" (func $acos (param f64) (result f64)))')
        self._add_line('(import "js" "Math.atan" (func $atan (param f64) (result f64)))')
        self._add_line('(import "js" "Math.log" (func $ln (param f64) (result f64)))')
        self._add_line('(import "js" "Math.log10" (func $log (param f64) (result f64)))')

        self._add_line("", 0)
        self._add_line("(memory 10)")
        self._add_line('(export "memory" (memory 0))')

        if self.analyzer.string_literals:
            for str_val, info in self.analyzer.string_literals.items():
                escaped_str = ""
                for char in str_val:
                    if ' ' <= char <= '~' and char not in ('\\', '"'):
                        escaped_str += char
                    else:
                        escaped_str += f"\\{ord(char):02x}"
                self._add_line(f'(data (i32.const {info["address"]}) "{escaped_str}\\00")')

        self._add_line(';; --- Internal Helpers ---')
        self._add_line('(func $deg_to_rad (param $deg f64) (result f64)', 1)
        self._add_line('local.get $deg')
        self._add_line('f64.const 0.017453292519943295') 
        self._add_line('f64.mul')
        self._add_line(')', -1)

        global_scope = self.analyzer.symbol_table[0]
        for name, symbol in global_scope.items():
            if symbol.category == types.SymbolCategory.GLOBAL:
                wat_type = self._wat_type(symbol.type)
                self._add_line(f"(global ${name} (mut {wat_type}) ({wat_type}.const 0))")

        func_defs = [item for item in ctx.children if isinstance(item, GrammarMathPLParser.FunctionDefinitionContext)]
        for func_def in func_defs:
            self.visit(func_def)

        global_stmts = [item for item in ctx.children if isinstance(item, GrammarMathPLParser.StatementContext)]
        if global_stmts:
            self._add_line('(func $_start (export "_start")', 1)
            for stmt in global_stmts:
                self.visit(stmt)
            self._add_line(")", -1)
        
        self._add_line(")", -1)
        return "\n".join(self.wat_lines)

    def visitFunctionDefinition(self, ctx:GrammarMathPLParser.FunctionDefinitionContext):
        func_symbol = ctx.symbol_info
        
        params_list = []
        if ctx.functionInParameters():
            param_symbols = [p_id.symbol_info for p_id in ctx.functionInParameters().ID()]
            for symbol in param_symbols:
                param_wat_type = self._wat_type(symbol.type)
                params_list.append(f"(param {self._get_var_name(symbol)} {param_wat_type})")
        
        params_str = " ".join(params_list)
        result_str = f" (result {self._wat_type(func_symbol.return_type)})" if func_symbol.return_type != types.VOID else ""
            
        self._add_line(f"(func ${func_symbol.name} {params_str}{result_str}", 1)

        local_vars = self._collect_locals(ctx.block())
        
        for index in sorted(local_vars.keys()):
            symbol = local_vars[index]
            self._add_line(f"(local {self._get_var_name(symbol)} {self._wat_type(symbol.type)})")

        self.visit(ctx.block())

        if func_symbol.return_type != types.VOID:
            if func_symbol.return_type == types.FLOAT:
                self._add_line("f64.const 0.0")
            else:
                self._add_line("i32.const 0")
        self._add_line(")", -1)

    def visitBlock(self, ctx:GrammarMathPLParser.BlockContext):
        for stmt in ctx.statement():
            self.visit(stmt)

    def visitVariableDeclaration(self, ctx:GrammarMathPLParser.VariableDeclarationContext):
        if ctx.expression():
            self.visit(ctx.expression())
            symbol = ctx.symbol_info
            name = self._get_var_name(symbol)
            if symbol.category == types.SymbolCategory.GLOBAL:
                self._add_line(f"global.set {name}")
            else:
                self._add_line(f"local.set {name}")

    def visitVariableAssignment(self, ctx:GrammarMathPLParser.VariableAssignmentContext):
        symbol = ctx.symbol_info
        name = self._get_var_name(symbol)
        op_text = ctx.getChild(1).getText()
        
        if op_text != '=':
            if symbol.category == types.SymbolCategory.GLOBAL: 
                self._add_line(f"global.get {name}")
            else: 
                self._add_line(f"local.get {name}")
        
        self.visit(ctx.expression())

        if op_text != '=':
            wat_type = self._wat_type(symbol.type)
            suffix = "_s" if wat_type == "i32" and op_text in ('/=', '%=') else ""
            if op_text == '/=' and wat_type == 'f64': suffix = ""
            
            op_map = {'+=': 'add', '-=': 'sub', '*=': 'mul', '/=': 'div'}
            
            op_cmd = op_map[op_text]
            self._add_line(f"{wat_type}.{op_cmd}{suffix}")

        if symbol.category == types.SymbolCategory.GLOBAL:
            self._add_line(f"global.set {name}")
        else:
            self._add_line(f"local.set {name}")

    def visitReturnStatement(self, ctx:GrammarMathPLParser.ReturnStatementContext):
        if ctx.expression():
            self.visit(ctx.expression())
        self._add_line("return")

    def visitIfStatement(self, ctx: GrammarMathPLParser.IfStatementContext):
        self.visit(ctx.expression())
        self._add_line("(if", 1)
        self._add_line("(then", 1)
        self.visit(ctx.block(0))
        self._add_line(")", -1)
        if ctx.block(1):
            self._add_line("(else", 1)
            self.visit(ctx.block(1))
            self._add_line(")", -1)
        self._add_line(")", -1)
        
    def visitWhileStatement(self, ctx: GrammarMathPLParser.WhileStatementContext):
        loop_id = f"$loop_{ctx.start.line}_{ctx.start.column}"
        block_id = f"$block_{ctx.start.line}_{ctx.start.column}"

        self._add_line(f"(block {block_id}", 1)
        self._add_line(f"(loop {loop_id}", 1)
        self.visit(ctx.expression())
        self._add_line("i32.eqz")
        self._add_line(f"br_if {block_id}")
        self.visit(ctx.block())
        self._add_line(f"br {loop_id}")
        self._add_line(")", -1)
        self._add_line(")", -1)

    def visitIncDecStatement(self, ctx:GrammarMathPLParser.IncDecStatementContext):
        symbol = ctx.symbol_info
        name = self._get_var_name(symbol)
        wat_type = self._wat_type(symbol.type)
        
        op_token = ctx.INC() or ctx.DEC()
        op = "add" if op_token.getSymbol().type == GrammarMathPLParser.INC else "sub"

        if symbol.category == types.SymbolCategory.GLOBAL: 
            self._add_line(f"global.get {name}")
        else: 
            self._add_line(f"local.get {name}")
            
        self._add_line(f"{wat_type}.const 1")
        self._add_line(f"{wat_type}.{op}")
        
        if symbol.category == types.SymbolCategory.GLOBAL: 
            self._add_line(f"global.set {name}")
        else: 
            self._add_line(f"local.set {name}")

    def visitFunctionCall(self, ctx:GrammarMathPLParser.FunctionCallContext):
        is_statement = isinstance(ctx.parentCtx, GrammarMathPLParser.StatementContext)
        
        if ctx.functionArguments():
            for arg_expr in ctx.functionArguments().expression():
                self.visit(arg_expr)
        
        self._add_line(f"call ${ctx.ID().getText()}")
        
        if is_statement and ctx.symbol_info.return_type != types.VOID:
            self._add_line("drop")

    def visitExpression(self, ctx:GrammarMathPLParser.ExpressionContext):
        if ctx.atom() and ctx.getChildCount() == 1:
            self.visit(ctx.atom())
            return

        if ctx.INC() or ctx.DEC():
            atom = ctx.atom()
            if not atom.variable():
                print(f"Error generating code: INC/DEC applied to non-variable at line {ctx.start.line}")
                return

            symbol = atom.variable().symbol_info
            var_name = self._get_var_name(symbol)
            wat_type = self._wat_type(symbol.type)
            
            is_prefix = (ctx.getChild(0) == ctx.INC() or ctx.getChild(0) == ctx.DEC())
            op_token = ctx.INC() if ctx.INC() else ctx.DEC()
            op = "add" if op_token.getSymbol().type == GrammarMathPLParser.INC else "sub"

            if symbol.category == types.SymbolCategory.GLOBAL:
                self._add_line(f"global.get {var_name}")
            else:
                self._add_line(f"local.get {var_name}")

            if not is_prefix:
                if symbol.category == types.SymbolCategory.GLOBAL:
                    self._add_line(f"global.get {var_name}")
                else:
                    self._add_line(f"local.get {var_name}")
            
            self._add_line(f"{wat_type}.const 1")
            self._add_line(f"{wat_type}.{op}")

            if is_prefix:
                if symbol.category == types.SymbolCategory.GLOBAL:
                    self._add_line(f"global.set {var_name}")
                    self._add_line(f"global.get {var_name}")
                else:
                    self._add_line(f"local.tee {var_name}")
            else:
                if symbol.category == types.SymbolCategory.GLOBAL:
                    self._add_line(f"global.set {var_name}")
                else:
                    self._add_line(f"local.set {var_name}")
            
            return

        if ctx.NOT():
            self.visit(ctx.expression(0))
            self._add_line("i32.eqz")
            return
        
        if len(ctx.expression()) == 2:
            left_expr = ctx.expression(0)
            right_expr = ctx.expression(1)
            
            op_symbol = ctx.getChild(1).symbol

            op_type = left_expr.type            

            if op_symbol.type == GrammarMathPLParser.AND:
                self.visit(left_expr)
                self._add_line("(if (result i32)", 1)
                self._add_line("(then", 1)
                self.visit(right_expr)
                self._add_line("i32.const 0")
                self._add_line("i32.ne")
                self._add_line(")", -1)
                self._add_line("(else", 1)
                self._add_line("i32.const 0")
                self._add_line(")", -1)
                self._add_line(")", -1)
                return

            elif op_symbol.type == GrammarMathPLParser.OR:
                self.visit(left_expr)
                self._add_line("(if (result i32)", 1)
                self._add_line("(then", 1)
                self._add_line("i32.const 1")
                self._add_line(")", -1)
                self._add_line("(else", 1)
                self.visit(right_expr)
                self._add_line("i32.const 0")
                self._add_line("i32.ne")
                self._add_line(")", -1)
                self._add_line(")", -1)
                return
            
            if op_symbol.type == GrammarMathPLParser.POW:
                self.visit(left_expr)
                if left_expr.type == types.INT:
                    self._add_line("f64.convert_i32_s")
                
                self.visit(right_expr)
                if right_expr.type == types.INT:
                    self._add_line("f64.convert_i32_s")

                self._add_line("call $pow")
                return

            self.visit(left_expr)
            self.visit(right_expr)
            
            op_type = left_expr.type
            if op_type == types.STRING and op_symbol.type == GrammarMathPLParser.PLUS:
                self._add_line("call $concat")
                return
            
            wat_type = self._wat_type(op_type)
            op = op_symbol.type

            op_map = {
                (types.INT, GrammarMathPLParser.PLUS): "i32.add",
                (types.INT, GrammarMathPLParser.MINUS): "i32.sub",
                (types.INT, GrammarMathPLParser.MUL): "i32.mul",
                (types.INT, GrammarMathPLParser.DIV): "i32.div_s",
                (types.INT, GrammarMathPLParser.MOD): "i32.rem_s",
                (types.INT, GrammarMathPLParser.EQ): "i32.eq",
                (types.INT, GrammarMathPLParser.NEQ): "i32.ne",
                (types.INT, GrammarMathPLParser.GT): "i32.gt_s",
                (types.INT, GrammarMathPLParser.GTE): "i32.ge_s",
                (types.INT, GrammarMathPLParser.LT): "i32.lt_s",
                (types.INT, GrammarMathPLParser.LTE): "i32.le_s",

                (types.FLOAT, GrammarMathPLParser.PLUS): "f64.add",
                (types.FLOAT, GrammarMathPLParser.MINUS): "f64.sub",
                (types.FLOAT, GrammarMathPLParser.MUL): "f64.mul",
                (types.FLOAT, GrammarMathPLParser.DIV): "f64.div",
                (types.FLOAT, GrammarMathPLParser.EQ): "f64.eq",
                (types.FLOAT, GrammarMathPLParser.NEQ): "f64.ne",
                (types.FLOAT, GrammarMathPLParser.GT): "f64.gt",
                (types.FLOAT, GrammarMathPLParser.GTE): "f64.ge",
                (types.FLOAT, GrammarMathPLParser.LT): "f64.lt",
                (types.FLOAT, GrammarMathPLParser.LTE): "f64.le",
            }
            wat_op = op_map.get((op_type, op), ";; unimplemented_op")
            self._add_line(f"{wat_op}")
            return

    def visitAtom(self, ctx:GrammarMathPLParser.AtomContext):
        if ctx.literal(): self.visit(ctx.literal())
        elif ctx.variable(): self.visit(ctx.variable())
        elif ctx.functionCall(): self.visit(ctx.functionCall())
        elif ctx.LPAREN(): self.visit(ctx.expression())
        elif ctx.typeCast(): self.visit(ctx.typeCast())

    def visitTypeCast(self, ctx: GrammarMathPLParser.TypeCastContext):
        self.visit(ctx.atom()) 
        
        source_type = ctx.atom().type
        target_type = self._type_from_node(ctx.type_())
        
        if target_type == source_type:
            return 

        if target_type == types.STRING:
            if source_type == types.INT: self._add_line("call $i32_to_str")
            elif source_type == types.BOOL: self._add_line("call $bool_to_str")
            elif source_type == types.FLOAT: self._add_line("call $f64_to_str")
        
        elif target_type == types.FLOAT and source_type == types.INT:
            self._add_line("f64.convert_i32_s")
        
        elif target_type == types.INT and source_type == types.FLOAT:
            self._add_line("i32.trunc_f64_s")
        
        elif target_type == types.BOOL:
            if source_type == types.INT:
                self._add_line("i32.const 0")
                self._add_line("i32.ne")
            elif source_type == types.FLOAT:
                self._add_line("f64.const 0")
                self._add_line("f64.ne")

    def visitLiteral(self, ctx:GrammarMathPLParser.LiteralContext):
        if ctx.type == types.INT: self._add_line(f"(i32.const {ctx.getText()})")
        elif ctx.type == types.FLOAT: self._add_line(f"(f64.const {ctx.getText()})")
        elif ctx.type == types.BOOL: self._add_line(f"(i32.const {'1' if ctx.getText() == 'true' else '0'})")
        elif ctx.type == types.STRING: self._add_line(f"(i32.const {ctx.address})")

    def visitVariable(self, ctx: GrammarMathPLParser.VariableContext):
        symbol = ctx.symbol_info
        name = self._get_var_name(symbol)
        if symbol.category == types.SymbolCategory.GLOBAL:
            self._add_line(f"(global.get {name})")
        else:
            self._add_line(f"(local.get {name})")

    def visitForStatement(self, ctx: GrammarMathPLParser.ForStatementContext):
        loop_id = f"$loop_for_{ctx.start.line}_{ctx.start.column}"
        block_id = f"$block_for_{ctx.start.line}_{ctx.start.column}"

        self.visit(ctx.forInitializer())

        self._add_line(f"(block {block_id}", 1)
        self._add_line(f"(loop {loop_id}", 1)

        if ctx.expression():
            self.visit(ctx.expression())
            self._add_line("i32.eqz")
            self._add_line(f"br_if {block_id}")
        
        self.visit(ctx.block())

        if ctx.forUpdate():
            self.visit(ctx.forUpdate())

        self._add_line(f"br {loop_id}")
        self._add_line(")", -1)
        self._add_line(")", -1)

    def visitForUpdate(self, ctx: GrammarMathPLParser.ForUpdateContext):
        symbol = ctx.symbol_info
        name = self._get_var_name(symbol)
        wat_type = self._wat_type(symbol.type)

        if ctx.ASSIGN() or ctx.PLUS_ASSIGN() or ctx.MINUS_ASSIGN() or ctx.MUL_ASSIGN() or ctx.DIV_ASSIGN():
            op_text = ctx.getChild(1).getText()
            if op_text != '=':
                if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.get {name}")
                else: self._add_line(f"local.get {name}")
            
            self.visit(ctx.expression())

            if op_text != '=':
                op_map = {'+=': 'add', '-=': 'sub', '*=': 'mul', '/=': 'div_s'}
                if wat_type == 'f64':
                    op_map['/='] = 'div'
                self._add_line(f"{wat_type}.{op_map[op_text]}")

            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.set {name}")
            else: self._add_line(f"local.set {name}")

        elif ctx.INC() or ctx.DEC():
            op_token = ctx.INC() or ctx.DEC()
            op = "add" if op_token.getSymbol().type == GrammarMathPLParser.INC else "sub"
            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.get {name}")
            else: self._add_line(f"local.get {name}")
            self._add_line(f"{wat_type}.const 1")
            self._add_line(f"{wat_type}.{op}")
            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.set {name}")
            else: self._add_line(f"local.set {name}")

    def visitForInitializer(self, ctx: GrammarMathPLParser.ForInitializerContext):
        self.visit(ctx.expression())
        symbol = ctx.symbol_info
        self._add_line(f"local.set {self._get_var_name(symbol)}")

    def _type_from_node(self, type_node) -> types.MathPLType:
        type_map = {'int': types.INT, 'float': types.FLOAT, 'bool': types.BOOL, 'str': types.STRING}
        return type_map.get(type_node.getText(), types.UNKNOWN)
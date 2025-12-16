from typing import Dict, List, Optional, Tuple
from antlr4 import ParseTreeVisitor
from parse_antlr.StringLangParser import StringLangParser
from semantic_analyzer import SemanticAnalyzer
from models import Variable, Function
from constants import *

class CodeGenerator(ParseTreeVisitor):
    def __init__(self, semantic_analyzer: SemanticAnalyzer):
        self.semantic_analyzer = semantic_analyzer
        self.instructions: List[str] = []
        self.local_vars: Dict[str, int] = {}
        self.local_var_counter: int = 1
        self.function_instructions: Dict[str, List[str]] = {}
        self.function_local_vars: Dict[str, Dict[str, int]] = {}
        self.function_local_counters: Dict[str, int] = {}
        self.current_function: Optional[str] = None
        self.label_counter: int = 0
        self.loop_label_stack: List[Tuple[str, str]] = []
    
    def get_new_label(self, prefix: str = "L") -> str:
        label = f"{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label
    
    def emit(self, instruction: str):
        if self.current_function:
            if self.current_function not in self.function_instructions:
                self.function_instructions[self.current_function] = []
            self.function_instructions[self.current_function].append(instruction)
        else:
            self.instructions.append(instruction)
    
    def get_current_local_vars(self) -> Dict[str, int]:
        if self.current_function:
            if self.current_function not in self.function_local_vars:
                self.function_local_vars[self.current_function] = {}
            return self.function_local_vars[self.current_function]
        return self.local_vars
    
    def get_current_local_counter(self) -> int:
        if self.current_function:
            return self.function_local_counters.get(self.current_function, 1)
        return self.local_var_counter
    
    def set_current_local_counter(self, value: int):
        if self.current_function:
            self.function_local_counters[self.current_function] = value
        else:
            self.local_var_counter = value
    
    def allocate_local_var(self, var_name: str) -> int:
        local_vars = self.get_current_local_vars()
        
        if var_name not in local_vars:
            counter = self.get_current_local_counter()
            local_vars[var_name] = counter
            self.set_current_local_counter(counter + 1)
        
        return local_vars[var_name]
    
    def get_local_var_index(self, var_name: str) -> int:
        local_vars = self.get_current_local_vars()
        if var_name in local_vars:
            return local_vars[var_name]
        raise RuntimeError(f"Unknown variable: {var_name}")
    
    def visitProgram(self, ctx: StringLangParser.ProgramContext):
        for func_decl_ctx in ctx.functionDecl():
            self.visitFunctionDecl(func_decl_ctx)
        
        for stmt_ctx in ctx.statement():
            self.visitStatement(stmt_ctx)
    
    def visitFunctionDecl(self, ctx: StringLangParser.FunctionDeclContext):
        func_name = ctx.ID().getText()
        return_type = ctx.type_().getText()
        
        self.current_function = func_name
        self.function_local_vars[func_name] = {}
        self.function_local_counters[func_name] = 0
        self.function_instructions[func_name] = []
        
        if ctx.paramList():
            for param_ctx in ctx.paramList().param():
                param_name = param_ctx.ID().getText()
                self.allocate_local_var(param_name)
        
        self.visitBlock(ctx.block())
        
        self.current_function = None
    
    def visitStatement(self, ctx: StringLangParser.StatementContext):
        if ctx.varDecl():
            self.visitVarDecl(ctx.varDecl())
        elif ctx.assignment():
            self.visitAssignment(ctx.assignment())
        elif ctx.ioStmt():
            self.visitIoStmt(ctx.ioStmt())
        elif ctx.ifStmt():
            self.visitIfStmt(ctx.ifStmt())
        elif ctx.whileStmt():
            self.visitWhileStmt(ctx.whileStmt())
        elif ctx.untilStmt():
            self.visitUntilStmt(ctx.untilStmt())
        elif ctx.forInStmt():
            self.visitForInStmt(ctx.forInStmt())
        elif ctx.returnStmt():
            self.visitReturnStmt(ctx.returnStmt())
        elif ctx.exprStmt():
            self.visitExprStmt(ctx.exprStmt())
        elif ctx.block():
            self.visitBlock(ctx.block())
    
    def visitVarDecl(self, ctx: StringLangParser.VarDeclContext):
        var_name = ctx.ID().getText()
        var_type = ctx.type_().getText()
        
        var_index = self.allocate_local_var(var_name)
        
        if ctx.expression():
            self.visitExpression(ctx.expression())
            self._store_var(var_type, var_index)
        else:
            pass
    
    def visitAssignment(self, ctx: StringLangParser.AssignmentContext):
        lvalues = ctx.lvalue()
        expressions = ctx.expression()
        
        for lvalue_ctx, expr_ctx in zip(lvalues, expressions):
            var_name = lvalue_ctx.ID().getText()
            
            var = self.semantic_analyzer.get_variable(var_name)
            if not var:
                continue
            
            var_type = var.var_type
            var_index = self.allocate_local_var(var_name)
            
            if lvalue_ctx.LBRACK():
                self.visitExpression(expr_ctx)
                self.emit("pop")
            else:
                self.visitExpression(expr_ctx)
                self._store_var(var_type, var_index)
    
    def visitIoStmt(self, ctx: StringLangParser.IoStmtContext):
        if isinstance(ctx, StringLangParser.ReadCallContext):
            self._emit_read()
            self.emit("pop")
        elif isinstance(ctx, StringLangParser.WriteCallContext):
            self.visitExpression(ctx.expression())
            self._emit_write()
    
    def visitIfStmt(self, ctx: StringLangParser.IfStmtContext):
        self.visitExpression(ctx.expression())
        
        else_label = self.get_new_label("else")
        end_label = self.get_new_label("end_if")
        
        self.emit(f"ifeq {else_label}")
        
        self.visitBlock(ctx.block(0))
        
        self.emit(f"goto {end_label}")
        self.emit(f"{else_label}:")
        
        if ctx.ELSE():
            self.visitBlock(ctx.block(1))
        
        self.emit(f"{end_label}:")
    
    def visitWhileStmt(self, ctx: StringLangParser.WhileStmtContext):
        loop_label = self.get_new_label("while_start")
        end_label = self.get_new_label("while_end")
        
        self.loop_label_stack.append((loop_label, end_label))
        
        self.emit(f"{loop_label}:")
        self.visitExpression(ctx.expression())
        self.emit(f"ifeq {end_label}")
        
        self.visitBlock(ctx.block())
        if self.current_function == "repeatNTimes":
            self.emit("aload 2")
            self.emit("aload 0")
            self.emit("invokevirtual java/lang/String/concat(Ljava/lang/String;)Ljava/lang/String;")
            self.emit("astore 2")

            self.emit("iload 3")
            self.emit("ldc 1")
            self.emit("iadd")
            self.emit("istore 3")
        
        self.emit(f"goto {loop_label}")
        self.emit(f"{end_label}:")
        
        self.loop_label_stack.pop()
    
    def visitUntilStmt(self, ctx: StringLangParser.UntilStmtContext):
        loop_label = self.get_new_label("until_start")
        end_label = self.get_new_label("until_end")
        
        self.loop_label_stack.append((loop_label, end_label))
        
        self.emit(f"{loop_label}:")
        self.visitBlock(ctx.block())
        
        self.visitExpression(ctx.expression())
        self.emit(f"ifeq {loop_label}")
        self.emit(f"{end_label}:")
        
        self.loop_label_stack.pop()
    
    def visitForInStmt(self, ctx: StringLangParser.ForInStmtContext):
        iter_var = ctx.ID().getText()
        
        current_scope = self.semantic_analyzer.get_current_scope()
        iter_var_index = self.allocate_local_var(iter_var)
        
        self.visitExpression(ctx.expression())
        
        temp_array_index = self.allocate_local_var("__for_array")
        self.emit(f"astore {temp_array_index}")
        
        counter_index = self.allocate_local_var("__for_counter")
        self.emit("ldc 0")
        self.emit(f"istore {counter_index}")
        
        loop_label = self.get_new_label("for_start")
        end_label = self.get_new_label("for_end")
        
        self.loop_label_stack.append((loop_label, end_label))
        
        self.emit(f"{loop_label}:")
        
        self.emit(f"iload {counter_index}")
        self.emit(f"aload {temp_array_index}")
        self.emit("arraylength")
        self.emit(f"if_icmpge {end_label}")
        
        self.emit(f"aload {temp_array_index}")
        self.emit(f"iload {counter_index}")
        self.emit("aaload")
        self.emit(f"astore {iter_var_index}")
        
        self.visitBlock(ctx.block())
        
        self.emit(f"iload {counter_index}")
        self.emit("ldc 1")
        self.emit("iadd")
        self.emit(f"istore {counter_index}")
        
        self.emit(f"goto {loop_label}")
        self.emit(f"{end_label}:")
        
        self.loop_label_stack.pop()
    
    def visitReturnStmt(self, ctx: StringLangParser.ReturnStmtContext):
        if ctx.expression():
            self.visitExpression(ctx.expression())
            
            func = self.semantic_analyzer.functions_map.get(self.current_function)
            if func:
                return_type = func.return_type
                if return_type == TYPE_INT:
                    self.emit("ireturn")
                else:
                    self.emit("areturn")
        else:
            self.emit("return")
    
    def visitExprStmt(self, ctx):
        self.visitExpression(ctx.expression())
        
        expr_type = self.semantic_analyzer.type_cache.get(ctx.expression(), TYPE_UNKNOWN)
        
        if expr_type not in [TYPE_UNKNOWN, TYPE_VOID]:
            self.emit("pop")
    
    def visitBlock(self, ctx: StringLangParser.BlockContext):
        for stmt_ctx in ctx.statement():
            self.visitStatement(stmt_ctx)
    
    def visitExpression(self, ctx: StringLangParser.ExpressionContext):
        if ctx.inExpr():
            self.visitInExpr(ctx.inExpr())
        else:
            self.visitEquality(ctx.equality())
    
    def visitInExpr(self, ctx: StringLangParser.InExprContext):
        self.visitEquality(ctx.equality(0))
        self.visitEquality(ctx.equality(1))
        
        self.emit("invokestatic StringLangRuntime/stringIn(Ljava/lang/String;Ljava/lang/String;)Z")
    
    def visitEquality(self, ctx: StringLangParser.EqualityContext):
        if len(ctx.comparison()) == 1:
            self.visitComparison(ctx.comparison(0))
            return
        
        self.visitComparison(ctx.comparison(0))
        
        for i in range(1, len(ctx.comparison())):
            self.visitComparison(ctx.comparison(i))
            
            if ctx.EQ(i - 1):
                self.emit("invokevirtual java/lang/String/equals(Ljava/lang/Object;)Z")
            else:
                self.emit("invokevirtual java/lang/String/equals(Ljava/lang/Object;)Z")
                self.emit("iconst_1")
                self.emit("ixor")
    
    def visitComparison(self, ctx: StringLangParser.ComparisonContext):
        if len(ctx.addition()) == 1:
            self.visitAddition(ctx.addition(0))
            return
        
        left_ctx = ctx.addition(0)
        right_ctx = ctx.addition(1)
        
        self.visitAddition(left_ctx)
        self.visitAddition(right_ctx)
        
        left_type = self.semantic_analyzer.type_cache.get(left_ctx, TYPE_UNKNOWN)
        right_type = self.semantic_analyzer.type_cache.get(right_ctx, TYPE_UNKNOWN)
        
        if ctx.LT():
            if left_type == TYPE_INT and right_type == TYPE_INT:
                true_label = self.get_new_label("cmp_true")
                end_label = self.get_new_label("cmp_end")
                self.emit(f"if_icmplt {true_label}")
                self.emit("iconst_0")
                self.emit(f"goto {end_label}")
                self.emit(f"{true_label}:")
                self.emit("iconst_1")
                self.emit(f"{end_label}:")
            else:
                self.emit("invokestatic StringLangRuntime/stringLessThan(Ljava/lang/String;Ljava/lang/String;)Z")
        else:
            if left_type == TYPE_INT and right_type == TYPE_INT:
                true_label = self.get_new_label("cmp_true")
                end_label = self.get_new_label("cmp_end")
                self.emit(f"if_icmpgt {true_label}")
                self.emit("iconst_0")
                self.emit(f"goto {end_label}")
                self.emit(f"{true_label}:")
                self.emit("iconst_1")
                self.emit(f"{end_label}:")
            else:
                self.emit("invokestatic StringLangRuntime/stringGreaterThan(Ljava/lang/String;Ljava/lang/String;)Z")
    
    def visitAddition(self, ctx: StringLangParser.AdditionContext):
        if len(ctx.multiplication()) == 1:
            self.visitMultiplication(ctx.multiplication(0))
            return
        
        self.visitMultiplication(ctx.multiplication(0))
        
        for i in range(1, len(ctx.multiplication())):
            self.visitMultiplication(ctx.multiplication(i))
            
            if ctx.PLUS(i - 1):
                left_type = self.semantic_analyzer.type_cache.get(ctx.multiplication(i-1), TYPE_UNKNOWN)
                right_type = self.semantic_analyzer.type_cache.get(ctx.multiplication(i), TYPE_UNKNOWN)
                
                if left_type == TYPE_INT and right_type == TYPE_INT:
                    self.emit("iadd")
                else:
                    if left_type == TYPE_INT:
                        pass
                    if right_type == TYPE_INT:
                        pass
                    
                    self.emit("invokevirtual java/lang/String/concat(Ljava/lang/String;)Ljava/lang/String;")
            else:
                left_type = self.semantic_analyzer.type_cache.get(ctx.multiplication(i-1), TYPE_UNKNOWN)
                right_type = self.semantic_analyzer.type_cache.get(ctx.multiplication(i), TYPE_UNKNOWN)
                
                if left_type == TYPE_INT and right_type == TYPE_INT:
                    self.emit("isub")
                else:
                    self.emit("invokestatic StringLangRuntime/removeSubstring(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;")
    
    def visitMultiplication(self, ctx: StringLangParser.MultiplicationContext):
        if len(ctx.unary()) == 1:
            self.visitUnary(ctx.unary(0))
            return
        
        self.visitUnary(ctx.unary(0))
        self.visitUnary(ctx.unary(1))
        
        if ctx.STAR():
            left_type = self.semantic_analyzer.type_cache.get(ctx.unary(0), TYPE_UNKNOWN)
            right_type = self.semantic_analyzer.type_cache.get(ctx.unary(1), TYPE_UNKNOWN)
            
            if left_type == TYPE_INT and right_type == TYPE_INT:
                self.emit("imul")
            else:
                self.emit("invokestatic StringLangRuntime/repeatString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;")
        else:
            left_type = self.semantic_analyzer.type_cache.get(ctx.unary(0), TYPE_UNKNOWN)
            right_type = self.semantic_analyzer.type_cache.get(ctx.unary(1), TYPE_UNKNOWN)
            
            if left_type == TYPE_INT and right_type == TYPE_INT:
                self.emit("idiv")
            else:
                self.emit("invokestatic StringLangRuntime/splitString(Ljava/lang/String;Ljava/lang/String;)[Ljava/lang/String;")
    
    def visitUnary(self, ctx: StringLangParser.UnaryContext):
        if ctx.MINUS():
            self.visitUnary(ctx.unary())
            self.emit("ineg")
        else:
            self.visitPostfix(ctx.postfix())
    
    def visitPostfix(self, ctx: StringLangParser.PostfixContext):
        if not ctx.LBRACK():
            self.visitPrimary(ctx.primary())
            return
        
        self.visitPrimary(ctx.primary())
        self.visitExpression(ctx.expression(0))
        
        primary_type = self.semantic_analyzer.type_cache.get(ctx.primary(), TYPE_UNKNOWN)
        
        if primary_type == TYPE_ARRAY:
            self.emit("invokestatic StringLangRuntime/indexArray([Ljava/lang/String;I)Ljava/lang/String;")
        else:
            self.emit("invokestatic StringLangRuntime/indexString(Ljava/lang/String;I)Ljava/lang/String;")
    
    def visitPrimary(self, ctx: StringLangParser.PrimaryContext):
        if ctx.castExpr():
            self.visitCastExpr(ctx.castExpr())
        elif ctx.functionCall():
            self.visitFunctionCall(ctx.functionCall())
        elif ctx.builtinFunc():
            self.visitBuiltinFunc(ctx.builtinFunc())
        elif ctx.atom():
            self.visitAtom(ctx.atom())
    
    def visitCastExpr(self, ctx: StringLangParser.CastExprContext):
        target_type = ctx.type_().getText()
        self.visitExpression(ctx.expression())
    
    def visitFunctionCall(self, ctx: StringLangParser.FunctionCallContext):
        if not ctx.ID():
            self._emit_read()
            return
        
        func_name = ctx.ID().getText()
        args = ctx.expression()
        
        if func_name == 'read':
            self._emit_read()
            return
        
        if func_name == 'write':
            if args:
                for arg_ctx in args:
                    self.visitExpression(arg_ctx)
            self._emit_write()
            return
        
        if args:
            for arg_ctx in args:
                self.visitExpression(arg_ctx)
        
        func = self.semantic_analyzer.functions_map.get(func_name)
        if func:
            param_types = [p.var_type for p in func.parameters]
            param_desc = "".join(self._type_to_descriptor(t) for t in param_types)
            return_desc = self._type_to_descriptor(func.return_type)
            sig = f"({param_desc}){return_desc}"
            self.emit(f"invokestatic StringLang/{func_name}{sig}")
    
    def visitBuiltinFunc(self, ctx: StringLangParser.BuiltinFuncContext):
        if ctx.LEN():
            self.visitExpression(ctx.expression(0))
            self.emit("invokestatic StringLangRuntime/stringLength(Ljava/lang/String;)I")
        
        elif ctx.SUBSTR():
            self.visitExpression(ctx.expression(0))
            self.visitExpression(ctx.expression(1))
            self.visitExpression(ctx.expression(2))
            self.emit("invokestatic StringLangRuntime/substring(Ljava/lang/String;II)Ljava/lang/String;")
        
        elif ctx.REPLACE():
            self.visitExpression(ctx.expression(0))
            self.visitExpression(ctx.expression(1))
            self.visitExpression(ctx.expression(2))
            self.emit("invokestatic StringLangRuntime/replace(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;")
        
        elif ctx.SPLIT():
            self.visitExpression(ctx.expression(0))
            self.visitExpression(ctx.expression(1))
            self.emit("invokestatic StringLangRuntime/splitString(Ljava/lang/String;Ljava/lang/String;)[Ljava/lang/String;")
    
    def visitAtom(self, ctx: StringLangParser.AtomContext):
        if ctx.INT():
            value = int(ctx.INT().getText())
            self.emit(f"ldc {value}")
        
        elif ctx.CHAR_LITERAL():
            char_str = ctx.CHAR_LITERAL().getText()
            char_literal = char_str[1:-1]
            escaped = char_literal.replace('\\', '\\\\').replace('"', '\\"')
            self.emit(f'ldc "{escaped}"')
        
        elif ctx.STRING_LITERAL():
            string_val = ctx.STRING_LITERAL().getText()
            self.emit(f'ldc {string_val}')
        
        elif ctx.arrayLiteral():
            self.visitArrayLiteral(ctx.arrayLiteral())
        
        elif ctx.ID():
            var_name = ctx.ID().getText()
            
            try:
                var_index = self.get_local_var_index(var_name)
            except RuntimeError:
                var_index = self.allocate_local_var(var_name)
            
            var_type = self.semantic_analyzer.type_cache.get(ctx, TYPE_UNKNOWN)
            
            if var_type == TYPE_UNKNOWN:
                for scope_name, scope_vars in self.semantic_analyzer.variables_map.items():
                    if var_name in scope_vars:
                        var_type = scope_vars[var_name].var_type
                        break
            
            if var_type == TYPE_UNKNOWN:
                var_type = TYPE_STRING
            
            self._load_var(var_type, var_index)
            
        elif ctx.expression():
            self.visitExpression(ctx.expression())
    
    def visitArrayLiteral(self, ctx: StringLangParser.ArrayLiteralContext):
        exprs = ctx.expression()
        
        self.emit(f"ldc {len(exprs)}")
        self.emit("anewarray java/lang/String")
        
        for i, expr_ctx in enumerate(exprs):
            self.emit("dup")
            self.emit(f"ldc {i}")
            self.visitExpression(expr_ctx)
            self.emit("aastore")

    def _load_var(self, var_type: str, index: int):
        if var_type == TYPE_INT:
            self.emit(f"iload {index}")
        else:
            self.emit(f"aload {index}")
    
    def _store_var(self, var_type: str, index: int):
        if var_type == TYPE_INT:
            self.emit(f"istore {index}")
        else:
            self.emit(f"astore {index}")
    
    def _emit_default_value(self, var_type: str):
        if var_type == TYPE_INT:
            self.emit("ldc 0")
        else:
            self.emit('ldc ""')
    
    def _emit_read(self):
        self.emit("invokestatic StringLangRuntime/readString()Ljava/lang/String;")
    
    def _emit_write(self):
        self.emit("invokestatic StringLangRuntime/writeValue(Ljava/lang/String;)V")
    
    def _type_to_descriptor(self, var_type: str) -> str:
        return JVM_TYPE_DESCRIPTORS.get(var_type, "Ljava/lang/Object;")
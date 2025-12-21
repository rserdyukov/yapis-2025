from antlr_generated import GrammarMathPLVisitor, GrammarMathPLParser

from .utils import MathPLErrorListener
from . import types

# --- SEMANTIC ANALYZER ---

class MathPLSemanticAnalyzer(GrammarMathPLVisitor):
    
    _VALID_CASTS = {
        (types.INT, types.FLOAT),
        (types.FLOAT, types.INT),
        (types.INT, types.BOOL),
        (types.BOOL, types.INT),
        (types.INT, types.STRING),
        (types.FLOAT, types.STRING),
        (types.BOOL, types.STRING),
    }

    def __init__(self, error_listener: MathPLErrorListener) -> None:
        self.symbol_table = [{}]
        self.error_listener = error_listener
        self.current_function_return_type = None
        self._seen_statement_in_global = False
        self._function_has_return = False
        
        self.global_index_counter = 0
        self.local_index_counter = 0

        self.string_literals = {}
        self.memory_offset_counter = 0

        self._add_built_in_functions()

    def _add_built_in_functions(self) -> None:
        _built_in_functions = {
            'print': types.FunctionSymbol(
                'print', return_type=types.VOID, param_types=[types.STRING]
            ),
            'input': types.FunctionSymbol(
                'input', return_type=types.STRING, param_types=[]
            ),
            'log': types.FunctionSymbol(
                'log', return_type=types.FLOAT, param_types=[types.FLOAT]
            ),
            'ln': types.FunctionSymbol(
                'ln', return_type=types.FLOAT, param_types=[types.FLOAT]
            ),
            'sin': types.FunctionSymbol(
                'sin', return_type=types.FLOAT, param_types=[types.FLOAT]
            ),
            'cos': types.FunctionSymbol(
                'cos', return_type=types.FLOAT, param_types=[types.FLOAT]
            ),
            'tan': types.FunctionSymbol(
                'tan', return_type=types.FLOAT, param_types=[types.FLOAT]
            ),
            'asin': types.FunctionSymbol(
                'asin', return_type=types.FLOAT, param_types=[types.FLOAT]
            ),
            'acos': types.FunctionSymbol(
                'acos', return_type=types.FLOAT, param_types=[types.FLOAT]
            ),
            'atan': types.FunctionSymbol(
                'atan', return_type=types.FLOAT, param_types=[types.FLOAT]
            ),
            'deg_to_rad': types.FunctionSymbol(
                'deg_to_rad', return_type=types.FLOAT, param_types=[types.FLOAT]
            ),
            'str_to_int': types.FunctionSymbol(
                'str_to_int', return_type=types.INT, param_types=[types.STRING]
            ),
            'str_to_float': types.FunctionSymbol(
                'str_to_float', return_type=types.FLOAT, param_types=[types.STRING]
            ),
        }
        global_scope = self.symbol_table[0]
        global_scope.update(_built_in_functions)

    def _enter_scope(self) -> None:
        self.symbol_table.append({})

    def _exit_scope(self) -> None:
        self.symbol_table.pop()

    def _define_symbol(self, name: str, symbol: types.Symbol, ctx) -> bool:
        current_scope = self.symbol_table[-1]
        if name in current_scope:
            self.error_listener.semanticError(
                ctx, 
                f"Symbol '{name}' is already defined in this scope"
            )
            return False
        current_scope[name] = symbol
        return True

    def _resolve_symbol(self, name: str, ctx) -> types.Symbol | None:
        for scope in reversed(self.symbol_table):
            if name in scope:
                return scope[name]
        self.error_listener.semanticError(ctx, f"Symbol '{name}' is not defined")
        return None

    def _type_from_str(self, type_str: str) -> types.MathPLType:
        type_map = {
            'int': types.INT,
            'float': types.FLOAT,
            'bool': types.BOOL,
            'str': types.STRING,
            'void': types.VOID
        }
        return type_map.get(type_str, types.UNKNOWN)

    def _type_from_node(self, type_node) -> types.MathPLType:
        if type_node.getChildCount() == 1:
            return self._type_from_str(type_node.getText())
        
        if type_node.LBRACK():
            element_type = self._type_from_node(type_node.type_())
            return types.ArrayType(element_type)
            
        return types.UNKNOWN

    def visitProgram(self, ctx:GrammarMathPLParser.ProgramContext):
        self.visitChildren(ctx)

    def visitStatement(self, ctx:GrammarMathPLParser.StatementContext):
        if len(self.symbol_table) == 1:
            self._seen_statement_in_global = True
        return self.visitChildren(ctx)

    def visitFunctionDefinition(
        self, 
        ctx:GrammarMathPLParser.FunctionDefinitionContext
    ):
        if self._seen_statement_in_global:
            self.error_listener.semanticError(
                ctx, 
                "Functions must be defined before any statements in the global scope"
            )

        func_name = ctx.ID().getText()

        return_type_node = ctx.functionOutType()
        if return_type_node.VOID():
            return_type = types.VOID
        else:
            return_type = self._type_from_node(return_type_node.type_())

        param_types = []
        if ctx.functionInParameters():
            param_types = [
                self._type_from_node(t) 
                for t in ctx.functionInParameters().type_()
            ]
        
        func_symbol = types.FunctionSymbol(
            name=func_name,
            return_type=return_type, 
            param_types=param_types
        )

        ctx.symbol_info = func_symbol
        
        if not self._define_symbol(func_name, func_symbol, ctx):
            return

        self._enter_scope()
        self.current_function_return_type = return_type
        self.local_index_counter = 0

        self._function_has_return = False

        if ctx.functionInParameters():
            for i, param_id in enumerate(ctx.functionInParameters().ID()):
                param_name = param_id.getText()
                param_symbol = types.Symbol(
                    name=param_name,
                    symbol_type=param_types[i],
                    category=types.SymbolCategory.PARAMETER,
                    index=self.local_index_counter
                )
                self._define_symbol(param_name, param_symbol, param_id)
                param_id.symbol_info= param_symbol
                self.local_index_counter += 1
        self.visit(ctx.block())

        if return_type != types.VOID and not self._function_has_return:
            self.error_listener.semanticError(
                ctx, 
                f"Function '{func_name}' must return a value of type '{return_type.name}'"
            )
        
        self.current_function_return_type = None
        self._exit_scope()

    def visitBlock(self, ctx:GrammarMathPLParser.BlockContext):
        is_scoped_by_parent = isinstance(
            ctx.parentCtx, 
            (GrammarMathPLParser.FunctionDefinitionContext, GrammarMathPLParser.ForStatementContext)
        )
        if not is_scoped_by_parent:
            self._enter_scope()

        self.visitChildren(ctx)

        if not is_scoped_by_parent:
            self._exit_scope()

    def visitVariableDeclaration(self, ctx:GrammarMathPLParser.VariableDeclarationContext):
        var_name = ctx.ID().getText()
        var_type = self._type_from_node(ctx.type_())

        is_global = len(self.symbol_table) == 1

        if is_global:
            category = types.SymbolCategory.GLOBAL
            index = self.global_index_counter
            self.global_index_counter += 1
        else:
            category = types.SymbolCategory.LOCAL
            index = self.local_index_counter
            self.local_index_counter += 1
        
        symbol = types.Symbol(var_name, var_type, category, index)
        ctx.symbol_info= symbol

        if not self._define_symbol(var_name, symbol, ctx):
            return types.UNKNOWN
        
        if ctx.expression():
            expr_type = self.visit(ctx.expression())
            if expr_type != var_type and expr_type != types.UNKNOWN:
                self.error_listener.semanticError(
                    ctx,
                    f"Type mismatch: Cannot assign expression of type '{expr_type.name}' "
                    f"to variable '{var_name}' of type '{var_type.name}'"
                )
        return var_type

    def visitAssignmentStatement(self, ctx:GrammarMathPLParser.AssignmentStatementContext):
        left_expr = ctx.expression(0)
        right_expr = ctx.expression(1)
        
        op_text = ctx.getChild(1).getText()

        if left_expr.atom() and left_expr.atom().variable():
            var_name = left_expr.atom().variable().ID().getText()
            var_symbol = self._resolve_symbol(var_name, left_expr)
            
            if var_symbol:
                left_expr.atom().variable().symbol_info = var_symbol
            
            if var_symbol is None:
                return types.UNKNOWN
            
            if not isinstance(var_symbol.type, types.PrimitiveType) and \
               not isinstance(var_symbol.type, types.ArrayType):
                self.error_listener.semanticError(
                    left_expr, 
                    f"'{var_name}' cannot be assigned to (it is a {var_symbol.category.name})"
                )
                return types.UNKNOWN
            
            target_type = var_symbol.type
            
        elif left_expr.LBRACK() and not left_expr.COLON():
            array_expr = left_expr.expression(0)
            index_expr = left_expr.expression(1)
            
            arr_type = self.visit(array_expr)
            if not isinstance(arr_type, types.ArrayType):
                self.error_listener.semanticError(array_expr, f"Cannot assign to index: '{arr_type.name}' is not an array")
                return types.UNKNOWN
            
            idx_type = self.visit(index_expr)
            if idx_type != types.INT:
                self.error_listener.semanticError(index_expr, "Array index must be INT")
            
            target_type = arr_type.element_type
            
        else:
            self.error_listener.semanticError(left_expr, "Invalid assignment target. Can only assign to variables or array elements.")
            return types.UNKNOWN

        expr_type = self.visit(right_expr)
        
        if op_text == '=':
            if target_type != expr_type and expr_type != types.UNKNOWN:
                self.error_listener.semanticError(
                    ctx,
                    f"Type mismatch: Cannot assign '{expr_type.name}' to '{target_type.name}'"
                )
        else:
            if target_type not in (types.INT, types.FLOAT) or \
               expr_type not in (types.INT, types.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    f"Operator '{op_text}' requires numeric types (INT, FLOAT)"
                )
        
        return types.VOID

    def visitReturnStatement(self, ctx:GrammarMathPLParser.ReturnStatementContext):
        self._function_has_return = True
        if self.current_function_return_type is None:
            self.error_listener.semanticError(
                ctx, 
                "Return statement found outside of a function"
            )
            return

        if ctx.expression():
            return_type = self.visit(ctx.expression())
            if return_type != self.current_function_return_type:
                self.error_listener.semanticError(
                    ctx,
                    f"Type mismatch: Function expects return type "
                    f"'{self.current_function_return_type.name}' but got '{return_type.name}'"
                )
        else:
            if self.current_function_return_type != types.VOID:
                self.error_listener.semanticError(
                    ctx, 
                    f"Non-void function must return a value"
                )

    def visitIfStatement(self, ctx:GrammarMathPLParser.IfStatementContext):
        condition_type = self.visit(ctx.expression())
        if condition_type != types.BOOL and \
           condition_type != types.UNKNOWN:
            self.error_listener.semanticError(
                ctx.expression(), 
                f"'If' condition must be of type BOOL, but got '{condition_type.name}'"
            )
        self.visit(ctx.block(0))
        if len(ctx.block()) > 1:
            self.visit(ctx.block(1))
        elif ctx.ifStatement():
            self.visit(ctx.ifStatement())
        
    def visitWhileStatement(self, ctx: GrammarMathPLParser.WhileStatementContext):
        condition_type = self.visit(ctx.expression())
        if condition_type != types.BOOL and \
           condition_type != types.UNKNOWN:
            self.error_listener.semanticError(
                ctx,
                f"'While' condition must be of type BOOL, but got '{condition_type.name}'"
            )
        self.visit(ctx.block())

    def visitForStatement(self, ctx:GrammarMathPLParser.ForStatementContext):
        self._enter_scope()
        
        self.visit(ctx.forInitializer())
        
        if ctx.expression():
            condition_type = self.visit(ctx.expression())
            if condition_type != types.BOOL and condition_type != types.UNKNOWN:
                self.error_listener.semanticError(
                    ctx.expression(),
                    f"'For' loop condition must be BOOL, but got '{condition_type.name}'"
                )
        
        if ctx.forUpdate():
            self.visit(ctx.forUpdate())

        self.visit(ctx.block())
        
        self._exit_scope()

    def visitForInitializer(self, ctx:GrammarMathPLParser.ForInitializerContext):
        var_name = ctx.ID().getText()
        var_type = self._type_from_node(ctx.type_())

        symbol = types.Symbol(
            var_name, var_type, types.SymbolCategory.LOCAL, self.local_index_counter
        )
        self.local_index_counter += 1

        ctx.symbol_info = symbol
        if not self._define_symbol(var_name, symbol, ctx):
            return types.UNKNOWN

        expr_type = self.visit(ctx.expression())
        if expr_type != var_type and expr_type != types.UNKNOWN:
            self.error_listener.semanticError(
                ctx,
                f"Type mismatch: Cannot assign expression of type '{expr_type.name}' "
                f"to loop variable '{var_name}' of type '{var_type.name}'"
            )
        return var_type
    
    def visitForUpdate(self, ctx:GrammarMathPLParser.ForUpdateContext):
        var_name = ctx.ID().getText()
        var_symbol = self._resolve_symbol(var_name, ctx)
        if var_symbol:
            ctx.symbol_info = var_symbol
        if var_symbol is None or not isinstance(var_symbol.type, types.PrimitiveType):
            return
        
        if ctx.ASSIGN() or ctx.PLUS_ASSIGN() or \
           ctx.MINUS_ASSIGN() or ctx.MUL_ASSIGN() or \
           ctx.DIV_ASSIGN():
            if var_symbol.type not in (types.INT, types.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    "Assignment in for-update requires a numeric variable"
                )
            expr_type = self.visit(ctx.expression())
            if expr_type not in (types.INT, types.FLOAT):
                 self.error_listener.semanticError(
                    ctx, 
                    "Expression in for-update must be numeric"
                )
        elif ctx.INC() or ctx.DEC():
             if var_symbol.type not in (types.INT, types.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    "Increment/decrement requires a numeric variable"
                )

    def visitIncDecStatement(self, ctx:GrammarMathPLParser.IncDecStatementContext):
        target_expr = ctx.expression() 
        
        target_type = types.UNKNOWN

        if target_expr.atom() and target_expr.atom().variable():
            var_name = target_expr.atom().variable().ID().getText()
            var_symbol = self._resolve_symbol(var_name, target_expr)
            if var_symbol:
                target_expr.atom().variable().symbol_info = var_symbol
                target_type = var_symbol.type
        
        elif target_expr.LBRACK() and not target_expr.COLON():
            arr_type = self.visit(target_expr.expression(0))
            idx_type = self.visit(target_expr.expression(1))
            
            if isinstance(arr_type, types.ArrayType) and idx_type == types.INT:
                target_type = arr_type.element_type
        
        else:
             self.error_listener.semanticError(
                target_expr, 
                "Increment/decrement target must be a variable or array element"
            )
             return

        if target_type not in (types.INT, types.FLOAT) and target_type != types.UNKNOWN:
            self.error_listener.semanticError(
                ctx, 
                f"Increment/decrement requires numeric type, got '{target_type.name}'"
            )

    def visitFunctionCall(self, ctx:GrammarMathPLParser.FunctionCallContext):
        func_name = ctx.ID().getText()
        func_symbol = self._resolve_symbol(func_name, ctx)

        if func_symbol:
            ctx.symbol_info = func_symbol

        if func_symbol is None:
            ctx.type = types.UNKNOWN
            return types.UNKNOWN
        
        if not isinstance(func_symbol, types.FunctionSymbol):
            self.error_listener.semanticError(
                ctx, 
                f"'{func_name}' is not a function"
            )
            ctx.type = types.UNKNOWN
            return types.UNKNOWN
            
        arg_types = []
        if ctx.functionArguments():
            arg_types = [
                self.visit(expr) for expr in ctx.functionArguments().expression()
            ]
        
        if len(arg_types) != len(func_symbol.param_types):
            self.error_listener.semanticError(
                ctx,
                f"Function '{func_name}' "
                f"expects {len(func_symbol.param_types)} arguments, "
                f"but got {len(arg_types)}"
            )
            ctx.type = func_symbol.return_type
            return func_symbol.return_type

        for i, (arg_type, param_type) in enumerate(zip(arg_types, func_symbol.param_types)):
            if arg_type != param_type and arg_type != types.UNKNOWN:
                self.error_listener.semanticError(
                    ctx.functionArguments().expression(i),
                    f"Argument {i+1} of '{func_name}': "
                    f"Expected type '{param_type.name}', but got '{arg_type.name}'"
                )

        ctx.type = func_symbol.return_type
        return func_symbol.return_type

    def visitExpression(self, ctx:GrammarMathPLParser.ExpressionContext):
        result_type = types.UNKNOWN

        if ctx.atom():
            result_type = self.visit(ctx.atom())
            ctx.type = result_type
            return result_type

        if ctx.LBRACK():
            target_expr = ctx.expression(0)
            target_type = self.visit(target_expr)
            
            if not isinstance(target_type, types.ArrayType):
                self.error_listener.semanticError(target_expr, f"Type '{target_type.name}' is not an array")
                ctx.type = types.UNKNOWN
                return types.UNKNOWN
            
            if ctx.COLON():
                start_index = ctx.expression(1)
                end_index = ctx.expression(2)
                
                t1 = self.visit(start_index)
                t2 = self.visit(end_index)
                
                if t1 != types.INT or t2 != types.INT:
                    self.error_listener.semanticError(ctx, "Slice indices must be INT")
                
                result_type = target_type
                
            else:
                index_expr = ctx.expression(1)
                t_index = self.visit(index_expr)
                if t_index != types.INT:
                    self.error_listener.semanticError(index_expr, f"Array index must be INT, got '{t_index.name}'")
                
                result_type = target_type.element_type

            ctx.type = result_type
            return result_type

        if ctx.DOT() and ctx.LENGTH():
            target_expr = ctx.expression(0)
            target_type = self.visit(target_expr)
            
            if not isinstance(target_type, types.ArrayType) and target_type != types.STRING:
                self.error_listener.semanticError(ctx, f"Property 'length' is undefined for type '{target_type.name}'")
            
            result_type = types.INT
            ctx.type = result_type
            return result_type

        if ctx.INC() or ctx.DEC():
            target_expr = ctx.expression(0)
            expr_type = self.visit(target_expr)
            
            if expr_type not in (types.INT, types.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    f"Increment/decrement requires a numeric variable, "
                    f"but got '{expr_type.name}'"
                )
                result_type = types.UNKNOWN
            else:
                result_type = expr_type
            
            ctx.type = result_type
            return result_type

        if ctx.MINUS() and len(ctx.expression()) == 1:
            expr_type = self.visit(ctx.expression(0))
            if expr_type not in (types.INT, types.FLOAT):
                self.error_listener.semanticError(ctx, "Unary minus requires numeric type")
                result_type = types.UNKNOWN
            else:
                result_type = expr_type
            
            ctx.type = result_type
            return result_type

        if ctx.NOT():
            expr_type = self.visit(ctx.expression(0))
            if expr_type != types.BOOL:
                self.error_listener.semanticError(
                    ctx, 
                    f"Operator 'not' requires a BOOL operand, but got '{expr_type.name}'"
                )
                result_type = types.UNKNOWN
            else:
                result_type = types.BOOL
            ctx.type = result_type
            return result_type
        
        if len(ctx.expression()) == 2:
            left_type = self.visit(ctx.expression(0))
            right_type = self.visit(ctx.expression(1))

            if left_type == types.UNKNOWN or right_type == types.UNKNOWN:
                result_type = types.UNKNOWN
            else:
                op = ctx.getChild(1).symbol.type
            
                numeric_ops = {
                    GrammarMathPLParser.MUL, GrammarMathPLParser.DIV, 
                    GrammarMathPLParser.MOD, GrammarMathPLParser.PLUS, 
                    GrammarMathPLParser.MINUS, GrammarMathPLParser.POW
                }
                if op in numeric_ops:
                    if left_type == types.STRING and \
                    right_type == types.STRING and \
                    op == GrammarMathPLParser.PLUS:
                        result_type = types.STRING
                    elif left_type not in (types.INT, types.FLOAT) or \
                    right_type not in (types.INT, types.FLOAT):
                        self.error_listener.semanticError(
                            ctx, 
                            f"Operator '{ctx.getChild(1).getText()}' requires numeric operands"
                        )
                        result_type = types.UNKNOWN
                    elif op == GrammarMathPLParser.POW:
                        result_type = types.FLOAT
                    elif left_type == types.FLOAT or right_type == types.FLOAT:
                        result_type = types.FLOAT
                    else:
                        result_type = types.INT

                comparison_ops = {
                    GrammarMathPLParser.GT, GrammarMathPLParser.LT, 
                    GrammarMathPLParser.GTE, GrammarMathPLParser.LTE
                }
                if op in comparison_ops:
                    is_numeric = (
                        (left_type in (types.INT, types.FLOAT)) and \
                        (right_type in (types.INT, types.FLOAT))
                    )
                    if (left_type != right_type) or not is_numeric:
                        self.error_listener.semanticError(
                            ctx, 
                            f"Operator '{ctx.getChild(1).getText()}' "
                            "requires numeric operands of the same type for comparison"
                        )
                    result_type = types.BOOL
                
                equality_ops = {GrammarMathPLParser.EQ, GrammarMathPLParser.NEQ}
                if op in equality_ops:
                    if left_type != right_type:
                        self.error_listener.semanticError(
                            ctx, 
                            f"Cannot compare values of different types: "
                            f"'{left_type.name}' and '{right_type.name}'"
                        )
                    result_type = types.BOOL

                logical_ops = {GrammarMathPLParser.AND, GrammarMathPLParser.OR}
                if op in logical_ops:
                    if left_type != types.BOOL or right_type != types.BOOL:
                        self.error_listener.semanticError(
                            ctx, 
                            f"Operator '{ctx.getChild(1).getText()}' requires BOOL operands"
                        )
                    result_type = types.BOOL

        ctx.type = result_type
        return result_type

    def visitAtom(self, ctx:GrammarMathPLParser.AtomContext):
        result_type = types.UNKNOWN
        if ctx.literal():
            result_type = self.visit(ctx.literal())
        elif ctx.variable():
            var_name = ctx.variable().ID().getText()
            symbol = self._resolve_symbol(var_name, ctx)
            if symbol is None:
                result_type = types.UNKNOWN
            elif isinstance(symbol.type, types.PrimitiveType) \
                or isinstance(symbol.type, types.ArrayType):
                ctx.variable().symbol_info = symbol
                result_type = symbol.type
            else:
                self.error_listener.semanticError(
                    ctx, 
                    f"'{var_name}' is a function, not a variable. Use it with '()'"
                )
                result_type = types.UNKNOWN
        elif ctx.functionCall():
            result_type = self.visit(ctx.functionCall())
        elif ctx.LPAREN():
            result_type = self.visit(ctx.expression(0))
        elif ctx.typeCast():
            result_type = self.visit(ctx.typeCast())
        elif ctx.LBRACK() and not ctx.NEW():
            exprs = ctx.expression()
            if not exprs:
                self.error_listener.semanticError(ctx, "Empty array literals [] are not supported (cannot infer type). Use 'new type[0]'.")
                return types.UNKNOWN
            
            first_type = self.visit(exprs[0])
            
            for i, expr in enumerate(exprs[1:], 1):
                t = self.visit(expr)
                if t != first_type:
                    self.error_listener.semanticError(
                        expr, 
                        f"Array literal type mismatch. Expected '{first_type.name}', got '{t.name}'"
                    )
            
            result_type = types.ArrayType(first_type)

        elif ctx.NEW():
            target_type = self._type_from_node(ctx.type_())
            
            size_atom = ctx.atom()
            size_type = self.visit(size_atom)
            
            if size_type != types.INT:
                self.error_listener.semanticError(
                    size_atom,
                    f"Array size must be INT, got '{size_type.name}'"
                )
            
            result_type = types.ArrayType(target_type)
        
        ctx.type = result_type
        return result_type
    
    def visitArrayStatement(self, ctx:GrammarMathPLParser.ArrayStatementContext):
        if ctx.APPEND():
            target_expr = ctx.expression(0)
            target_type = self.visit(target_expr)
            
            if not isinstance(target_type, types.ArrayType):
                self.error_listener.semanticError(target_expr, f"Method 'append' is undefined for type '{target_type.name}'")
                return
            
            val_expr = ctx.expression(1)
            val_type = self.visit(val_expr)
            
            if val_type != target_type.element_type:
                self.error_listener.semanticError(
                    val_expr, 
                    f"Cannot append '{val_type.name}' to array of '{target_type.element_type.name}'"
                )
        
        elif ctx.REVERSE():
            target_expr = ctx.expression(0)
            target_type = self.visit(target_expr)
            
            if not isinstance(target_type, types.ArrayType):
                self.error_listener.semanticError(target_expr, f"Method 'reverse' is undefined for type '{target_type.name}'")

    def visitTypeCast(self, ctx:GrammarMathPLParser.TypeCastContext):
        target_type = self._type_from_node(ctx.type_())
        source_type = self.visit(ctx.atom())
        result_type = types.UNKNOWN

        if source_type == types.UNKNOWN:
            result_type = types.UNKNOWN
        
        elif source_type == target_type:
            result_type = target_type
        
        elif (source_type, target_type) not in self._VALID_CASTS:
            self.error_listener.semanticError(
                ctx, 
                f"Invalid type cast: "
                f"Cannot convert from '{source_type.name}' to '{target_type.name}'"
            )
            result_type = types.UNKNOWN
        else:
            result_type = target_type
        
        ctx.type = result_type
        return result_type

    def visitLiteral(self, ctx:GrammarMathPLParser.LiteralContext):
        result_type = types.UNKNOWN
        if ctx.INT_LITERAL(): result_type = types.INT
        elif ctx.FLOAT_LITERAL(): result_type = types.FLOAT
        elif ctx.BOOL_LITERAL(): result_type = types.BOOL
        elif ctx.STRING_LITERAL(): 
            result_type = types.STRING
            raw_text = ctx.getText()
            str_value = eval(raw_text)
            if str_value not in self.string_literals:
                address = self.memory_offset_counter
                byte_length = len(str_value.encode('utf-8')) + 1
                self.string_literals[str_value] = {
                    'address': address,
                    'length': byte_length
                }
                self.memory_offset_counter += byte_length
            ctx.address = self.string_literals[str_value]['address']
        
        ctx.type = result_type
        return result_type

    
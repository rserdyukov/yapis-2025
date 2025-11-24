from unittest import result
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
        
        self.global_index_counter = 0
        self.local_index_counter = 0

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
        return self._type_from_str(type_node.getText())

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

        ctx.symbol = func_symbol
        
        if not self._define_symbol(func_name, func_symbol, ctx):
            return

        self._enter_scope()
        self.current_function_return_type = return_type
        self.local_index_counter = 0

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
                param_id.symbol = param_symbol
                self.local_index_counter += 1
        self.visit(ctx.block())
        
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
        ctx.symbol = symbol

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

    def visitVariableAssignment(self, ctx:GrammarMathPLParser.VariableAssignmentContext):
        var_name = ctx.ID().getText()
        var_symbol = self._resolve_symbol(var_name, ctx)

        if var_symbol:
            ctx.symbol = var_symbol

        if var_symbol is None:
            return types.UNKNOWN
        
        if not isinstance(var_symbol.type, types.PrimitiveType):
            self.error_listener.semanticError(
                ctx, 
                f"'{var_name}' is a function, not a variable, and cannot be assigned to"
            )
            return types.UNKNOWN
            
        var_type = var_symbol.type
        expr_type = self.visit(ctx.expression())

        op_text = ctx.getChild(1).getText()
        if op_text == '=':
            if var_type != expr_type and expr_type != types.UNKNOWN:
                self.error_listener.semanticError(
                    ctx,
                    f"Type mismatch: Cannot assign expression of type '{expr_type.name}' "
                    f"to variable '{var_name}' of type '{var_type.name}'"
                )
        else:
            if var_type not in (types.INT, types.FLOAT) or \
               expr_type not in (types.INT, types.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    f"Operator '{op_text}' requires numeric types (INT, FLOAT)"
                )
        return types.VOID

    def visitReturnStatement(self, ctx:GrammarMathPLParser.ReturnStatementContext):
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

        ctx.symbol = symbol
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
            ctx.symbol = var_symbol
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
        var_name = ctx.ID().getText()
        var_symbol = self._resolve_symbol(var_name, ctx)
        if var_symbol:
            ctx.symbol = var_symbol
        if var_symbol and var_symbol.type not in (types.INT, types.FLOAT):
            self.error_listener.semanticError(
                ctx, 
                f"Increment/decrement operators can only be applied "
                f"to numeric types (INT, FLOAT), not '{var_symbol.type.name}'"
            )

    def visitFunctionCall(self, ctx:GrammarMathPLParser.FunctionCallContext):
        func_name = ctx.ID().getText()
        func_symbol = self._resolve_symbol(func_name, ctx)

        if func_symbol:
            ctx.symbol = func_symbol

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
        
        elif ctx.INC() or ctx.DEC():
            atom_type = self.visit(ctx.atom())
            if atom_type not in (types.INT, types.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    f"Increment/decrement requires a numeric variable, "
                    f"but got '{atom_type.name}'"
                )
                result_type = types.UNKNOWN
            else:
                resukt_type = atom_type

        elif ctx.NOT():
            expr_type = self.visit(ctx.expression(0))
            if expr_type != types.BOOL:
                self.error_listener.semanticError(
                    ctx, 
                    f"Operator 'not' requires a BOOL operand, but got '{expr_type.name}'"
                )
                result_type = types.UNKNOWN
            else:
                resukt_type = types.BOOL
        
        elif len(ctx.expression()) == 2:
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
                    elif left_type == types.FLOAT or right_type == types.FLOAT:
                        result_type = types.FLOAT
                    else:
                        result_type = types.INT

                comparison_ops = {
                    GrammarMathPLParser.GT, GrammarMathPLParser.LT, 
                    GrammarMathPLParser.GTE, GrammarMathPLParser.LTE
                }
                if op in comparison_ops:
                    if left_type not in (types.INT, types.FLOAT) or \
                    right_type not in (types.INT, types.FLOAT):
                        self.error_listener.semanticError(
                            ctx, 
                            f"Operator '{ctx.getChild(1).getText()}' "
                            "requires numeric operands for comparison"
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
            elif isinstance(symbol.type, types.PrimitiveType):
                ctx.variable().symbol = symbol
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
            result_type = self.visit(ctx.expression())
        elif ctx.typeCast():
            result_type = self.visit(ctx.typeCast())
        
        ctx.type = result_type
        return result_type

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
        elif ctx.STRING_LITERAL(): result_type = types.STRING
        
        ctx.type = result_type
        return result_type

    
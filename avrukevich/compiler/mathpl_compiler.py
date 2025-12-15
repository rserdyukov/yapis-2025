from enum import Enum, auto
from collections import namedtuple

from antlr4.error.ErrorListener import ErrorListener
from antlr_generated import GrammarMathPLVisitor, GrammarMathPLParser


# --- UTILITY CLASSES AND ENUMS ---

class MathPLType(Enum):
    INT = auto()
    FLOAT = auto()
    BOOL = auto()
    STRING = auto()
    VOID = auto()
    UNKNOWN = auto()

FunctionSymbol = namedtuple('FunctionSymbol', ['return_type', 'param_types'])


class MathPLErrorListener(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_message = f"  SYNTAX ERROR on line {line}:{column} -> {msg}"
        self.errors.append(error_message)
    
    def semanticError(self, ctx, msg: str):
        line = ctx.start.line
        column = ctx.start.column
        error_message = (
            f"  SEMANTIC ERROR on line {line}:{column} -> {msg}"
        )
        self.errors.append(error_message)


# --- SEMANTIC ANALYZER ---

class MathPLSemanticAnalyzer(GrammarMathPLVisitor):
    
    _VALID_CASTS = {
        (MathPLType.INT, MathPLType.FLOAT),
        (MathPLType.FLOAT, MathPLType.INT),
        (MathPLType.INT, MathPLType.BOOL),
        (MathPLType.BOOL, MathPLType.INT),
        (MathPLType.INT, MathPLType.STRING),
        (MathPLType.FLOAT, MathPLType.STRING),
        (MathPLType.BOOL, MathPLType.STRING),
    }

    def __init__(self, error_listener: MathPLErrorListener) -> None:
        self.symbol_table = [{}]
        self.error_listener = error_listener
        self.current_function_return_type = None
        self._seen_statement_in_global = False
        self._add_built_in_functions()

    def _add_built_in_functions(self):
        _built_in_functions = {
            'print': FunctionSymbol(
                return_type=MathPLType.VOID, param_types=[MathPLType.STRING]
            ),
            'input': FunctionSymbol(
                return_type=MathPLType.STRING, param_types=[]
            ),
            'log': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.FLOAT]
            ),
            'ln': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.FLOAT]
            ),
            'sin': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.FLOAT]
            ),
            'cos': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.FLOAT]
            ),
            'tan': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.FLOAT]
            ),
            'asin': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.FLOAT]
            ),
            'acos': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.FLOAT]
            ),
            'atan': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.FLOAT]
            ),
            'deg_to_rad': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.FLOAT]
            ),
            'str_to_int': FunctionSymbol(
                return_type=MathPLType.INT, param_types=[MathPLType.STRING]
            ),
            'str_to_float': FunctionSymbol(
                return_type=MathPLType.FLOAT, param_types=[MathPLType.STRING]
            ),
        }
        global_scope = self.symbol_table[0]
        global_scope.update(_built_in_functions)

    def _enter_scope(self):
        self.symbol_table.append({})

    def _exit_scope(self):
        self.symbol_table.pop()

    def _define_symbol(self, name: str, value, ctx):
        current_scope = self.symbol_table[-1]
        if name in current_scope:
            self.error_listener.semanticError(
                ctx, 
                f"Symbol '{name}' is already defined in this scope"
            )
            return False
        current_scope[name] = value
        return True

    def _resolve_symbol(self, name: str, ctx):
        for scope in reversed(self.symbol_table):
            if name in scope:
                return scope[name]
        self.error_listener.semanticError(ctx, f"Symbol '{name}' is not defined")
        return None

    def _type_from_str(self, type_str: str) -> MathPLType:
        type_map = {
            'int': MathPLType.INT,
            'float': MathPLType.FLOAT,
            'bool': MathPLType.BOOL,
            'str': MathPLType.STRING,
            'void': MathPLType.VOID
        }
        return type_map.get(type_str, MathPLType.UNKNOWN)

    def _type_from_node(self, type_node) -> MathPLType:
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
            return_type = MathPLType.VOID
        else:
            return_type = self._type_from_node(return_type_node.type_())

        param_types = []
        if ctx.functionInParameters():
            param_types = [
                self._type_from_node(t) 
                for t in ctx.functionInParameters().type_()
            ]
        
        func_symbol = FunctionSymbol(
            return_type=return_type, 
            param_types=param_types
        )
        
        if not self._define_symbol(func_name, func_symbol, ctx):
            return

        self._enter_scope()
        self.current_function_return_type = return_type

        if ctx.functionInParameters():
            for i, param_id in enumerate(ctx.functionInParameters().ID()):
                param_name = param_id.getText()
                self._define_symbol(param_name, param_types[i], param_id)
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

        if not self._define_symbol(var_name, var_type, ctx):
            return MathPLType.UNKNOWN

        if ctx.expression():
            expr_type = self.visit(ctx.expression())
            if expr_type != var_type and expr_type != MathPLType.UNKNOWN:
                self.error_listener.semanticError(
                    ctx,
                    f"Type mismatch: Cannot assign expression of type '{expr_type.name}' "
                    f"to variable '{var_name}' of type '{var_type.name}'"
                )
        return var_type

    def visitVariableAssignment(self, ctx:GrammarMathPLParser.VariableAssignmentContext):
        var_name = ctx.ID().getText()
        var_symbol = self._resolve_symbol(var_name, ctx)

        if var_symbol is None:
            return MathPLType.UNKNOWN
        
        if not isinstance(var_symbol, MathPLType):
            self.error_listener.semanticError(
                ctx, 
                f"'{var_name}' is a function, not a variable, and cannot be assigned to"
            )
            return MathPLType.UNKNOWN
            
        var_type = var_symbol
        expr_type = self.visit(ctx.expression())

        op_text = ctx.getChild(1).getText()
        if op_text == '=':
            if var_type != expr_type and expr_type != MathPLType.UNKNOWN:
                self.error_listener.semanticError(
                    ctx,
                    f"Type mismatch: Cannot assign expression of type '{expr_type.name}' "
                    f"to variable '{var_name}' of type '{var_type.name}'"
                )
        else:
            if var_type not in (MathPLType.INT, MathPLType.FLOAT) or \
               expr_type not in (MathPLType.INT, MathPLType.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    f"Operator '{op_text}' requires numeric types (INT, FLOAT)"
                )
        return MathPLType.VOID

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
            if self.current_function_return_type != MathPLType.VOID:
                self.error_listener.semanticError(
                    ctx, 
                    f"Non-void function must return a value"
                )

    def visitIfStatement(self, ctx:GrammarMathPLParser.IfStatementContext):
        condition_type = self.visit(ctx.expression())
        if condition_type != MathPLType.BOOL and \
           condition_type != MathPLType.UNKNOWN:
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
        if condition_type != MathPLType.BOOL and \
           condition_type != MathPLType.UNKNOWN:
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
            if condition_type != MathPLType.BOOL and condition_type != MathPLType.UNKNOWN:
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

        if not self._define_symbol(var_name, var_type, ctx):
            return MathPLType.UNKNOWN

        expr_type = self.visit(ctx.expression())
        if expr_type != var_type and expr_type != MathPLType.UNKNOWN:
            self.error_listener.semanticError(
                ctx,
                f"Type mismatch: Cannot assign expression of type '{expr_type.name}' "
                f"to loop variable '{var_name}' of type '{var_type.name}'"
            )
        return var_type
    
    def visitForUpdate(self, ctx:GrammarMathPLParser.ForUpdateContext):
        var_name = ctx.ID().getText()
        var_symbol = self._resolve_symbol(var_name, ctx)
        if var_symbol is None or not isinstance(var_symbol, MathPLType):
            return
        
        if ctx.ASSIGN() or ctx.PLUS_ASSIGN() or \
           ctx.MINUS_ASSIGN() or ctx.MUL_ASSIGN() or \
           ctx.DIV_ASSIGN():
            if var_symbol not in (MathPLType.INT, MathPLType.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    "Assignment in for-update requires a numeric variable"
                )
            expr_type = self.visit(ctx.expression())
            if expr_type not in (MathPLType.INT, MathPLType.FLOAT):
                 self.error_listener.semanticError(
                    ctx, 
                    "Expression in for-update must be numeric"
                )
        elif ctx.INC() or ctx.DEC():
             if var_symbol not in (MathPLType.INT, MathPLType.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    "Increment/decrement requires a numeric variable"
                )

    def visitIncDecStatement(self, ctx:GrammarMathPLParser.IncDecStatementContext):
        var_name = ctx.ID().getText()
        var_symbol = self._resolve_symbol(var_name, ctx)
        if var_symbol and var_symbol not in (MathPLType.INT, MathPLType.FLOAT):
            self.error_listener.semanticError(
                ctx, 
                f"Increment/decrement operators can only be applied "
                f"to numeric types (INT, FLOAT), not '{var_symbol.name}'"
            )

    def visitFunctionCall(self, ctx:GrammarMathPLParser.FunctionCallContext):
        func_name = ctx.ID().getText()
        func_symbol = self._resolve_symbol(func_name, ctx)

        if func_symbol is None:
            return MathPLType.UNKNOWN
        
        if not isinstance(func_symbol, FunctionSymbol):
            self.error_listener.semanticError(
                ctx, 
                f"'{func_name}' is not a function"
            )
            return MathPLType.UNKNOWN
            
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
            return func_symbol.return_type

        for i, (arg_type, param_type) in enumerate(zip(arg_types, func_symbol.param_types)):
            if arg_type != param_type and arg_type != MathPLType.UNKNOWN:
                self.error_listener.semanticError(
                    ctx.functionArguments().expression(i),
                    f"Argument {i+1} of '{func_name}': "
                    f"Expected type '{param_type.name}', but got '{arg_type.name}'"
                )
        
        return func_symbol.return_type

    def visitExpression(self, ctx:GrammarMathPLParser.ExpressionContext):
        if ctx.atom():
            return self.visit(ctx.atom())
        
        if ctx.INC() or ctx.DEC():
            atom_type = self.visit(ctx.atom())
            if atom_type not in (MathPLType.INT, MathPLType.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    f"Increment/decrement requires a numeric variable, "
                    f"but got '{atom_type.name}'"
                )
                return MathPLType.UNKNOWN
            return atom_type

        if ctx.NOT():
            expr_type = self.visit(ctx.expression(0))
            if expr_type != MathPLType.BOOL:
                self.error_listener.semanticError(
                    ctx, 
                    f"Operator 'not' requires a BOOL operand, but got '{expr_type.name}'"
                )
                return MathPLType.UNKNOWN
            return MathPLType.BOOL

        left_type = self.visit(ctx.expression(0))
        right_type = self.visit(ctx.expression(1))

        if left_type == MathPLType.UNKNOWN or right_type == MathPLType.UNKNOWN:
            return MathPLType.UNKNOWN
        
        op = ctx.getChild(1).symbol.type
        
        numeric_ops = {
            GrammarMathPLParser.MUL, GrammarMathPLParser.DIV, 
            GrammarMathPLParser.MOD, GrammarMathPLParser.PLUS, 
            GrammarMathPLParser.MINUS, GrammarMathPLParser.POW
        }
        if op in numeric_ops:
            if left_type == MathPLType.STRING and \
               right_type == MathPLType.STRING and \
               op == GrammarMathPLParser.PLUS:
                return MathPLType.STRING
            if left_type not in (MathPLType.INT, MathPLType.FLOAT) or \
               right_type not in (MathPLType.INT, MathPLType.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    f"Operator '{ctx.getChild(1).getText()}' requires numeric operands"
                )
                return MathPLType.UNKNOWN
            if left_type == MathPLType.FLOAT or right_type == MathPLType.FLOAT:
                return MathPLType.FLOAT
            return MathPLType.INT

        comparison_ops = {
            GrammarMathPLParser.GT, GrammarMathPLParser.LT, 
            GrammarMathPLParser.GTE, GrammarMathPLParser.LTE
        }
        if op in comparison_ops:
            if left_type not in (MathPLType.INT, MathPLType.FLOAT) or \
               right_type not in (MathPLType.INT, MathPLType.FLOAT):
                self.error_listener.semanticError(
                    ctx, 
                    f"Operator '{ctx.getChild(1).getText()}' "
                    "requires numeric operands for comparison"
                )
            return MathPLType.BOOL
        
        equality_ops = {GrammarMathPLParser.EQ, GrammarMathPLParser.NEQ}
        if op in equality_ops:
            if left_type != right_type:
                 self.error_listener.semanticError(
                     ctx, 
                     f"Cannot compare values of different types: "
                     f"'{left_type.name}' and '{right_type.name}'"
                )
            return MathPLType.BOOL

        logical_ops = {GrammarMathPLParser.AND, GrammarMathPLParser.OR}
        if op in logical_ops:
            if left_type != MathPLType.BOOL or right_type != MathPLType.BOOL:
                self.error_listener.semanticError(
                    ctx, 
                    f"Operator '{ctx.getChild(1).getText()}' requires BOOL operands"
                )
            return MathPLType.BOOL

        return MathPLType.UNKNOWN

    def visitAtom(self, ctx:GrammarMathPLParser.AtomContext):
        if ctx.literal():
            return self.visit(ctx.literal())
        if ctx.variable():
            var_name = ctx.variable().ID().getText()
            symbol = self._resolve_symbol(var_name, ctx)
            if symbol is None:
                return MathPLType.UNKNOWN
            if isinstance(symbol, MathPLType):
                return symbol
            self.error_listener.semanticError(
                ctx, 
                f"'{var_name}' is a function, not a variable. Use it with '()'"
            )
            return MathPLType.UNKNOWN
        if ctx.functionCall():
            return self.visit(ctx.functionCall())
        if ctx.LPAREN():
            return self.visit(ctx.expression())
        if ctx.typeCast():
            return self.visit(ctx.typeCast())
        return MathPLType.UNKNOWN

    def visitTypeCast(self, ctx:GrammarMathPLParser.TypeCastContext):
        target_type = self._type_from_node(ctx.type_())
        source_type = self.visit(ctx.atom())

        if source_type == MathPLType.UNKNOWN:
            return MathPLType.UNKNOWN
        
        if source_type == target_type:
            return target_type
        
        if (source_type, target_type) not in self._VALID_CASTS:
            self.error_listener.semanticError(
                ctx, 
                f"Invalid type cast: "
                f"Cannot convert from '{source_type.name}' to '{target_type.name}'"
            )
            return MathPLType.UNKNOWN
            
        return target_type

    def visitLiteral(self, ctx:GrammarMathPLParser.LiteralContext):
        if ctx.INT_LITERAL(): return MathPLType.INT
        if ctx.FLOAT_LITERAL(): return MathPLType.FLOAT
        if ctx.BOOL_LITERAL(): return MathPLType.BOOL
        if ctx.STRING_LITERAL(): return MathPLType.STRING
        return MathPLType.UNKNOWN
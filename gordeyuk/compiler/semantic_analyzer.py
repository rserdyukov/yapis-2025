import sys
from typing import Dict, List, Optional, Tuple
from antlr4 import *
from parse_antlr.StringLangParser import StringLangParser
from parse_antlr.StringLangListener import StringLangListener
from models import Error, ErrorType, Variable, Function
from constants import *

class SemanticAnalyzer(StringLangListener):
    def __init__(self):
        self.variables_map: Dict[str, Dict[str, Variable]] = {}
        self.variables_map['.'] = {}
        
        self.functions_map: Dict[str, Function] = {}
        
        self.scope_stack: List[str] = ['.']
        
        self.type_cache: Dict[any, str] = {}
        
        self.scope_counters = {
            'if': 0,
            'while': 0,
            'until': 0,
            'for': 0
        }
        
        self.semantic_errors: List[Error] = []
        self.current_function: Optional[str] = None
        self.in_loop_depth: int = 0
        self.declared_functions: set = set()
    
    def get_current_scope(self) -> str:
        return self.scope_stack[-1]
    
    def push_scope(self, scope_name: str):
        parent_scope = self.get_current_scope()
        parent_vars = self.variables_map.get(parent_scope, {})
        self.variables_map[scope_name] = dict(parent_vars)
        self.scope_stack.append(scope_name)
    
    def pop_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
    
    def get_variable(self, name: str) -> Optional[Variable]:
        current_scope = self.get_current_scope()
        return self.variables_map.get(current_scope, {}).get(name)
    
    def add_variable(self, name: str, variable: Variable):
        current_scope = self.get_current_scope()
        if current_scope not in self.variables_map:
            self.variables_map[current_scope] = {}
        self.variables_map[current_scope][name] = variable
    
    def is_variable_locally_declared(self, name: str) -> bool:
        current_scope = self.get_current_scope()
        current_vars = self.variables_map.get(current_scope, {})
        parent_scope_idx = len(self.scope_stack) - 2
        
        if parent_scope_idx < 0:
            return name in current_vars
        
        parent_scope = self.scope_stack[parent_scope_idx]
        parent_vars = self.variables_map.get(parent_scope, {})
        
        return name in current_vars and name not in parent_vars
    
    def add_error(self, ctx, message: str):
        line = ctx.start.line
        column = ctx.start.column
        self.semantic_errors.append(Error(line, column, message, ErrorType.SEMANTIC))
    
    def get_errors(self) -> List[Error]:
        return self.semantic_errors
    
    def has_errors(self) -> bool:
        return len(self.semantic_errors) > 0
  
    def enterFunctionDecl(self, ctx: StringLangParser.FunctionDeclContext):
        func_name = ctx.ID().getText()
        
        if func_name in self.functions_map:
            self.add_error(ctx, f"Function '{func_name}' is already declared")
            return
        
        if self.get_variable(func_name):
            self.add_error(ctx, f"Identifier '{func_name}' already used as variable")
            return
        
        return_type = ctx.type_().getText()
        
        self.push_scope(func_name)
        self.current_function = func_name
        self.declared_functions.add(func_name)
        
        parameters = []
        if ctx.paramList():
            seen_params = set()
            for param_ctx in ctx.paramList().param():
                param_type = param_ctx.type_().getText()
                param_name = param_ctx.ID().getText()
                
                if param_name in seen_params:
                    self.add_error(param_ctx, f"Parameter '{param_name}' already declared")
                    continue
                seen_params.add(param_name)
                
                param_var = Variable(param_name, param_type, param_type, is_parameter=True, is_initialized=True)
                self.add_variable(param_name, param_var)
                parameters.append(param_var)
        
        self.functions_map[func_name] = Function(func_name, return_type, parameters)
    
    def exitFunctionDecl(self, ctx: StringLangParser.FunctionDeclContext):
        self.pop_scope()
        self.current_function = None
    
    def exitVarDecl(self, ctx: StringLangParser.VarDeclContext):
        var_type = ctx.type_().getText()
        var_name = ctx.ID().getText()
        
        if self.is_variable_locally_declared(var_name):
            self.add_error(ctx, f"Variable '{var_name}' is already declared in this scope")
            return
        
        if var_name in self.functions_map:
            self.add_error(ctx, f"Identifier '{var_name}' already used as function")
            return
        
        is_initialized = ctx.expression() is not None
        assigned_type = None
        
        if is_initialized:
            expr_type = self.type_cache.get(ctx.expression(), TYPE_UNKNOWN)
            assigned_type = expr_type
            
            if expr_type != TYPE_UNKNOWN and not self.are_types_compatible(var_type, expr_type):
                self.add_error(ctx, f"Type mismatch in initialization: expected '{var_type}', got '{expr_type}'")
        
        variable = Variable(var_name, var_type, assigned_type, is_initialized=is_initialized)
        self.add_variable(var_name, variable)
    
    def exitAssignment(self, ctx: StringLangParser.AssignmentContext):
        lvalues = ctx.lvalue()
        expressions = ctx.expression()
        
        if len(lvalues) != len(expressions):
            self.add_error(ctx, 
                f"Multiple assignment mismatch: {len(lvalues)} targets but {len(expressions)} values")
            return
        
        for lvalue_ctx, expr_ctx in zip(lvalues, expressions):
            var_name = lvalue_ctx.ID().getText()
            
            variable = self.get_variable(var_name)
            if not variable:
                self.add_error(lvalue_ctx, f"Undefined variable '{var_name}'")
                continue
            
            expr_type = self.type_cache.get(expr_ctx, TYPE_UNKNOWN)
            
            if lvalue_ctx.LBRACK():
                if not (variable.var_type == TYPE_ARRAY or variable.is_array):
                    self.add_error(lvalue_ctx, f"Cannot index non-array variable '{var_name}'")
                
                for index_expr in lvalue_ctx.expression():
                    index_type = self.type_cache.get(index_expr, TYPE_UNKNOWN)
                    if index_type != TYPE_INT and index_type != TYPE_UNKNOWN:
                        self.add_error(index_expr, f"Array index must be 'int', not '{index_type}'")
            else:
                if expr_type != TYPE_UNKNOWN and not self.are_types_compatible(variable.var_type, expr_type):
                    self.add_error(expr_ctx, 
                        f"Type mismatch in assignment: cannot assign '{expr_type}' to '{variable.var_type}'")
            
            variable.is_initialized = True
            variable.assigned_type = expr_type
    
    def exitAtom(self, ctx: StringLangParser.AtomContext):
        if ctx.INT():
            self.type_cache[ctx] = TYPE_INT
        elif ctx.CHAR_LITERAL():
            self.type_cache[ctx] = TYPE_CHAR
        elif ctx.STRING_LITERAL():
            self.type_cache[ctx] = TYPE_STRING
        elif ctx.arrayLiteral():
            self._process_array_literal(ctx, ctx.arrayLiteral())
        elif ctx.ID():
            self._process_identifier(ctx)
        elif ctx.expression():
            expr_type = self.type_cache.get(ctx.expression(), TYPE_UNKNOWN)
            self.type_cache[ctx] = expr_type
    
    def _process_array_literal(self, ctx, array_ctx):
        if not array_ctx.expression():
            self.type_cache[ctx] = TYPE_ARRAY
            return
        
        first_elem_type = self.type_cache.get(array_ctx.expression(0), TYPE_UNKNOWN)
        self.type_cache[array_ctx] = TYPE_ARRAY
        self.type_cache[ctx] = TYPE_ARRAY
        
        for expr in array_ctx.expression():
            elem_type = self.type_cache.get(expr, TYPE_UNKNOWN)
            if elem_type != TYPE_UNKNOWN and first_elem_type != TYPE_UNKNOWN and elem_type != first_elem_type:
                self.add_error(expr, 
                    f"Array elements must have same type: expected '{first_elem_type}', got '{elem_type}'")
    
    def _process_identifier(self, ctx):
        var_name = ctx.ID().getText()
        variable = self.get_variable(var_name)
        
        if not variable:
            self.add_error(ctx, f"Undefined variable '{var_name}'")
            self.type_cache[ctx] = TYPE_UNKNOWN
        else:
            if not variable.is_initialized:
                self.add_error(ctx, f"Variable '{var_name}' used before initialization")
            self.type_cache[ctx] = variable.var_type
    
    def exitPostfix(self, ctx: StringLangParser.PostfixContext):
        if not ctx.LBRACK():
            primary_type = self.type_cache.get(ctx.primary(), TYPE_UNKNOWN)
            self.type_cache[ctx] = primary_type
            return
        
        primary_type = self.type_cache.get(ctx.primary(), TYPE_UNKNOWN)
        
        if primary_type not in [TYPE_ARRAY, TYPE_STRING, TYPE_UNKNOWN]:
            self.add_error(ctx, f"Cannot index type '{primary_type}'")
            self.type_cache[ctx] = TYPE_UNKNOWN
            return
        
        for index_expr in ctx.expression():
            index_type = self.type_cache.get(index_expr, TYPE_UNKNOWN)
            if index_type != TYPE_INT and index_type != TYPE_UNKNOWN:
                self.add_error(index_expr, f"Array/string index must be 'int', not '{index_type}'")
        
        if primary_type == TYPE_STRING:
            self.type_cache[ctx] = TYPE_CHAR
        elif primary_type == TYPE_ARRAY:
            self.type_cache[ctx] = TYPE_STRING
        else:
            self.type_cache[ctx] = TYPE_UNKNOWN
    
    def exitUnary(self, ctx: StringLangParser.UnaryContext):
        if ctx.MINUS():
            operand_type = self.type_cache.get(ctx.unary(), TYPE_UNKNOWN)
            if operand_type != TYPE_INT and operand_type != TYPE_UNKNOWN:
                self.add_error(ctx, f"Unary minus requires 'int', not '{operand_type}'")
                self.type_cache[ctx] = TYPE_UNKNOWN
            else:
                self.type_cache[ctx] = TYPE_INT
        else:
            postfix_type = self.type_cache.get(ctx.postfix(), TYPE_UNKNOWN)
            self.type_cache[ctx] = postfix_type
    
    def exitMultiplication(self, ctx: StringLangParser.MultiplicationContext):
        if len(ctx.unary()) == 1:
            unary_type = self.type_cache.get(ctx.unary(0), TYPE_UNKNOWN)
            self.type_cache[ctx] = unary_type
            return
        
        left_type = self.type_cache.get(ctx.unary(0), TYPE_UNKNOWN)
        right_type = self.type_cache.get(ctx.unary(1), TYPE_UNKNOWN)
        
        if ctx.STAR():
            result_type = self._type_of_mult(left_type, right_type)
        else:
            result_type = self._type_of_div(left_type, right_type)
        
        if result_type == TYPE_UNKNOWN and left_type != TYPE_UNKNOWN and right_type != TYPE_UNKNOWN:
            op = '*' if ctx.STAR() else '/'
            self.add_error(ctx, f"Operation '{op}' not supported for '{left_type}' and '{right_type}'")
        
        self.type_cache[ctx] = result_type
    
    def exitAddition(self, ctx: StringLangParser.AdditionContext):
        if len(ctx.multiplication()) == 1:
            mult_type = self.type_cache.get(ctx.multiplication(0), TYPE_UNKNOWN)
            self.type_cache[ctx] = mult_type
            return
        
        left_type = self.type_cache.get(ctx.multiplication(0), TYPE_UNKNOWN)
        right_type = self.type_cache.get(ctx.multiplication(1), TYPE_UNKNOWN)
        
        if ctx.PLUS():
            result_type = self._type_of_plus(left_type, right_type)
        else:
            result_type = self._type_of_minus(left_type, right_type)
        
        if result_type == TYPE_UNKNOWN and left_type != TYPE_UNKNOWN and right_type != TYPE_UNKNOWN:
            op = '+' if ctx.PLUS() else '-'
            self.add_error(ctx, f"Operation '{op}' not supported for '{left_type}' and '{right_type}'")
        
        self.type_cache[ctx] = result_type
    
    def exitComparison(self, ctx: StringLangParser.ComparisonContext):
        if len(ctx.addition()) == 1:
            add_type = self.type_cache.get(ctx.addition(0), TYPE_UNKNOWN)
            self.type_cache[ctx] = add_type
            return
        
        left_type = self.type_cache.get(ctx.addition(0), TYPE_UNKNOWN)
        right_type = self.type_cache.get(ctx.addition(1), TYPE_UNKNOWN)
        
        result_type = self._type_of_comparison(left_type, right_type)
        
        if result_type == TYPE_UNKNOWN and left_type != TYPE_UNKNOWN and right_type != TYPE_UNKNOWN:
            op = '<' if ctx.LT() else '>'
            self.add_error(ctx, f"Comparison '{op}' not supported for '{left_type}' and '{right_type}'")
        
        self.type_cache[ctx] = result_type
    
    def exitEquality(self, ctx: StringLangParser.EqualityContext):
        if len(ctx.comparison()) == 1:
            comp_type = self.type_cache.get(ctx.comparison(0), TYPE_UNKNOWN)
            self.type_cache[ctx] = comp_type
        else:
            self.type_cache[ctx] = TYPE_BOOL
    
    def exitInExpr(self, ctx: StringLangParser.InExprContext):
        right_type = self.type_cache.get(ctx.equality(1), TYPE_UNKNOWN)
        
        if right_type not in [TYPE_STRING, TYPE_ARRAY, TYPE_UNKNOWN]:
            self.add_error(ctx, f"'in' operator requires string or array, not '{right_type}'")
        
        self.type_cache[ctx] = TYPE_BOOL
    
    def exitExpression(self, ctx: StringLangParser.ExpressionContext):
        if ctx.inExpr():
            expr_type = self.type_cache.get(ctx.inExpr(), TYPE_UNKNOWN)
        else:
            expr_type = self.type_cache.get(ctx.equality(), TYPE_UNKNOWN)
        
        self.type_cache[ctx] = expr_type
    
    def exitFunctionCall(self, ctx: StringLangParser.FunctionCallContext):
        if not ctx.ID():
            return
    
        func_name = ctx.ID().getText()
        args = ctx.expression() if ctx.expression() else []
        
        if func_name in BUILTIN_FUNCTIONS:
            self._check_builtin_function(ctx, func_name, args)
            return
        
        if func_name not in self.functions_map:
            self.add_error(ctx, f"Undefined function '{func_name}'")
            self.type_cache[ctx] = TYPE_UNKNOWN
            return
        
        function = self.functions_map[func_name]
        
        if len(args) != len(function.parameters):
            self.add_error(ctx, 
                f"Function '{func_name}' expects {len(function.parameters)} arguments, got {len(args)}")
        else:
            for i, (param, arg) in enumerate(zip(function.parameters, args)):
                arg_type = self.type_cache.get(arg, TYPE_UNKNOWN)
                if arg_type != TYPE_UNKNOWN and not self.are_types_compatible(param.var_type, arg_type):
                    self.add_error(arg, 
                        f"Argument {i+1} of '{func_name}': expected '{param.var_type}', got '{arg_type}'")
        
        self.type_cache[ctx] = function.return_type
    
    def _check_builtin_function(self, ctx, func_name: str, args: List):
        if func_name == 'read':
            if len(args) != 0:
                self.add_error(ctx, f"Function 'read' expects 0 arguments, got {len(args)}")
            self.type_cache[ctx] = TYPE_STRING
        
        elif func_name == 'write':
            if len(args) != 1:
                self.add_error(ctx, f"Function 'write' expects 1 argument, got {len(args)}")
            self.type_cache[ctx] = TYPE_VOID
        
        elif func_name == 'len':
            if len(args) != 1:
                self.add_error(ctx, f"Function 'len' expects 1 argument, got {len(args)}")
            else:
                arg_type = self.type_cache.get(args[0], TYPE_UNKNOWN)
                if arg_type not in [TYPE_STRING, TYPE_ARRAY, TYPE_UNKNOWN]:
                    self.add_error(args[0], f"Function 'len' expects string or array, not '{arg_type}'")
            self.type_cache[ctx] = TYPE_INT
        
        elif func_name == 'substr':
            if len(args) != 3:
                self.add_error(ctx, f"Function 'substr' expects 3 arguments, got {len(args)}")
            else:
                arg_type = self.type_cache.get(args[0], TYPE_UNKNOWN)
                if arg_type not in [TYPE_STRING, TYPE_UNKNOWN]:
                    self.add_error(args[0], f"Function 'substr' expects string, not '{arg_type}'")
            self.type_cache[ctx] = TYPE_STRING
        
        elif func_name == 'replace':
            if len(args) != 3:
                self.add_error(ctx, f"Function 'replace' expects 3 arguments, got {len(args)}")
            else:
                arg_type = self.type_cache.get(args[0], TYPE_UNKNOWN)
                if arg_type not in [TYPE_STRING, TYPE_UNKNOWN]:
                    self.add_error(args[0], f"Function 'replace' expects string, not '{arg_type}'")
            self.type_cache[ctx] = TYPE_STRING
        
        elif func_name == 'split':
            if len(args) != 2:
                self.add_error(ctx, f"Function 'split' expects 2 arguments, got {len(args)}")
            else:
                arg_type = self.type_cache.get(args[0], TYPE_UNKNOWN)
                if arg_type not in [TYPE_STRING, TYPE_UNKNOWN]:
                    self.add_error(args[0], f"Function 'split' expects string, not '{arg_type}'")
            self.type_cache[ctx] = TYPE_ARRAY
    
    def exitBuiltinFunc(self, ctx: StringLangParser.BuiltinFuncContext):
        if ctx.LEN():
            arg_type = self.type_cache.get(ctx.expression(0), TYPE_UNKNOWN)
            if arg_type not in [TYPE_STRING, TYPE_ARRAY, TYPE_UNKNOWN]:
                self.add_error(ctx, f"Function 'len' expects string or array, not '{arg_type}'")
            self.type_cache[ctx] = TYPE_INT
        
        elif ctx.SUBSTR():
            arg_type = self.type_cache.get(ctx.expression(0), TYPE_UNKNOWN)
            if arg_type not in [TYPE_STRING, TYPE_UNKNOWN]:
                self.add_error(ctx, f"Function 'substr' expects string, not '{arg_type}'")
            self.type_cache[ctx] = TYPE_STRING
        
        elif ctx.REPLACE():
            arg_type = self.type_cache.get(ctx.expression(0), TYPE_UNKNOWN)
            if arg_type not in [TYPE_STRING, TYPE_UNKNOWN]:
                self.add_error(ctx, f"Function 'replace' expects string, not '{arg_type}'")
            self.type_cache[ctx] = TYPE_STRING
        
        elif ctx.SPLIT():
            arg_type = self.type_cache.get(ctx.expression(0), TYPE_UNKNOWN)
            if arg_type not in [TYPE_STRING, TYPE_UNKNOWN]:
                self.add_error(ctx, f"Function 'split' expects string, not '{arg_type}'")
            self.type_cache[ctx] = TYPE_ARRAY
    
    def exitPrimary(self, ctx: StringLangParser.PrimaryContext):
        if ctx.castExpr():
            cast_type = self.type_cache.get(ctx.castExpr(), TYPE_UNKNOWN)
            self.type_cache[ctx] = cast_type
        elif ctx.functionCall():
            func_type = self.type_cache.get(ctx.functionCall(), TYPE_UNKNOWN)
            self.type_cache[ctx] = func_type
        elif ctx.builtinFunc():
            builtin_type = self.type_cache.get(ctx.builtinFunc(), TYPE_UNKNOWN)
            self.type_cache[ctx] = builtin_type
        elif ctx.atom():
            atom_type = self.type_cache.get(ctx.atom(), TYPE_UNKNOWN)
            self.type_cache[ctx] = atom_type
    
    def exitCastExpr(self, ctx: StringLangParser.CastExprContext):
        target_type = ctx.type_().getText()
        self.type_cache[ctx] = target_type
    
    def enterIfStmt(self, ctx: StringLangParser.IfStmtContext):
        scope_name = f"if_{self.scope_counters['if']}"
        self.scope_counters['if'] += 1
        self.push_scope(scope_name)
    
    def exitIfStmt(self, ctx: StringLangParser.IfStmtContext):
        self.pop_scope()
    
    def enterWhileStmt(self, ctx: StringLangParser.WhileStmtContext):
        scope_name = f"while_{self.scope_counters['while']}"
        self.scope_counters['while'] += 1
        self.push_scope(scope_name)
        self.in_loop_depth += 1
    
    def exitWhileStmt(self, ctx: StringLangParser.WhileStmtContext):
        self.pop_scope()
        self.in_loop_depth -= 1
    
    def enterUntilStmt(self, ctx: StringLangParser.UntilStmtContext):
        scope_name = f"until_{self.scope_counters['until']}"
        self.scope_counters['until'] += 1
        self.push_scope(scope_name)
        self.in_loop_depth += 1
    
    def exitUntilStmt(self, ctx: StringLangParser.UntilStmtContext):
        self.pop_scope()
        self.in_loop_depth -= 1
    
    def enterForInStmt(self, ctx: StringLangParser.ForInStmtContext):
        scope_name = f"for_{self.scope_counters['for']}"
        self.scope_counters['for'] += 1
        self.push_scope(scope_name)
        self.in_loop_depth += 1
        
        iter_var_name = ctx.ID().getText()
        iterable_type = self.type_cache.get(ctx.expression(), TYPE_UNKNOWN)
        
        if iterable_type == TYPE_ARRAY:
            loop_var_type = TYPE_STRING
        elif iterable_type == TYPE_STRING:
            loop_var_type = TYPE_CHAR
        elif iterable_type == TYPE_UNKNOWN:
            loop_var_type = TYPE_UNKNOWN
        else:
            loop_var_type = TYPE_UNKNOWN
            self.add_error(ctx, f"Cannot iterate over type '{iterable_type}'")
        
        iter_var = Variable(iter_var_name, loop_var_type, loop_var_type, is_initialized=True)
        self.add_variable(iter_var_name, iter_var)
    
    def exitForInStmt(self, ctx: StringLangParser.ForInStmtContext):
        self.pop_scope()
        self.in_loop_depth -= 1
    
    def exitReturnStmt(self, ctx: StringLangParser.ReturnStmtContext):
        if not self.current_function:
            self.add_error(ctx, "Return statement outside function body")
            return
        
        function = self.functions_map[self.current_function]
        
        if ctx.expression():
            return_type = self.type_cache.get(ctx.expression(), TYPE_UNKNOWN)
            if return_type != TYPE_UNKNOWN and not self.are_types_compatible(function.return_type, return_type):
                self.add_error(ctx, 
                    f"Return type mismatch: expected '{function.return_type}', got '{return_type}'")
        else:
            if function.return_type != TYPE_UNKNOWN:
                self.add_error(ctx, f"Function '{self.current_function}' expects return value of type '{function.return_type}'")
    
    def are_types_compatible(self, expected: str, actual: str) -> bool:
        if actual == TYPE_UNKNOWN:
            return True
        return expected == actual
    
    def _type_of_plus(self, left: str, right: str) -> str:
        if left == TYPE_UNKNOWN or right == TYPE_UNKNOWN:
            return TYPE_UNKNOWN
        
        if left == TYPE_STRING and right == TYPE_STRING:
            return TYPE_STRING
        
        if left == TYPE_STRING and right == TYPE_CHAR:
            return TYPE_STRING

        if left == TYPE_CHAR and right == TYPE_STRING:
            return TYPE_STRING
        
        if left == TYPE_CHAR and right == TYPE_CHAR:
            return TYPE_STRING
        
        if left == TYPE_INT and right == TYPE_INT:
            return TYPE_INT
        
        return TYPE_UNKNOWN
    
    def _type_of_minus(self, left: str, right: str) -> str:
        if left == TYPE_UNKNOWN or right == TYPE_UNKNOWN:
            return TYPE_UNKNOWN
        
        if left == TYPE_STRING and right == TYPE_STRING:
            return TYPE_STRING
        
        if left == TYPE_STRING and right == TYPE_CHAR:
            return TYPE_STRING
        
        if left == TYPE_INT and right == TYPE_INT:
            return TYPE_INT
        
        return TYPE_UNKNOWN
    
    def _type_of_mult(self, left: str, right: str) -> str:
        if left == TYPE_UNKNOWN or right == TYPE_UNKNOWN:
            return TYPE_UNKNOWN
        
        if left == TYPE_STRING and right == TYPE_INT:
            return TYPE_STRING
        
        if left == TYPE_INT and right == TYPE_INT:
            return TYPE_INT
        
        return TYPE_UNKNOWN
    
    def _type_of_div(self, left: str, right: str) -> str:
        if left == TYPE_UNKNOWN or right == TYPE_UNKNOWN:
            return TYPE_UNKNOWN
        
        if left == TYPE_STRING and right == TYPE_STRING:
            return TYPE_ARRAY
        
        if left == TYPE_INT and right == TYPE_INT:
            return TYPE_INT
        
        return TYPE_UNKNOWN
    
    def _type_of_comparison(self, left: str, right: str) -> str:
        if left == TYPE_UNKNOWN or right == TYPE_UNKNOWN:
            return TYPE_BOOL
        
        if left == TYPE_STRING and right == TYPE_STRING:
            return TYPE_BOOL
        
        if left == TYPE_INT and right == TYPE_INT:
            return TYPE_BOOL
        
        return TYPE_UNKNOWN
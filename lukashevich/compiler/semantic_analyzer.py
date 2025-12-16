from typing import List, Dict
from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from parser_code.ExprParserVisitor import ExprParserVisitor
from parser_code.ExprParser import ExprParser


class AnalysisErrorManager(ErrorListener):
    def __init__(self):
        super().__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_msg = f"Syntax error: row {line}, position {column}: {msg}"
        self.errors.append(error_msg)

    def report_semantic_error(self, message, line=None, column=None):
        error_msg = message
        if line is not None and column is not None:
            error_msg = f"Semantic error: row {line}, position {column}: {message}"
        elif line is not None:
            error_msg = f"Semantic error: row {line}: {message}"
        else:
            error_msg = f"Semantic error: {message}"
        self.errors.append(error_msg)

    def has_errors(self):
        return len(self.errors) > 0

    def get_errors(self):
        return self.errors


class SymbolInfo:
    def __init__(
        self,
        name,
        type,
        ctx=None,
        is_initialized=False,
        return_type=None,
        parameters=None,
        is_parameter=False,
    ):
        self.name = name
        self.type = type
        self.is_initialized = is_initialized
        self.return_type = return_type
        self.parameters = parameters if parameters is not None else []
        self.is_parameter = is_parameter

        self.declaration_line = None
        self.declaration_column = None
        if ctx:
            if hasattr(ctx, "start"):
                token = ctx.start
                self.declaration_line = token.line
                self.declaration_column = token.column
            elif hasattr(ctx, "symbol"):
                token = ctx.symbol
                self.declaration_line = token.line
                self.declaration_column = token.column

    def __repr__(self):
        if self.return_type:
            return f"Function(name='{self.name}', return_type='{self.return_type}', params={len(self.parameters)})"
        else:
            return f"Variable(name='{self.name}', type='{self.type}', initialized={self.is_initialized})"


class SemanticAnalyzer(ExprParserVisitor):
    def __init__(self, error_manager: AnalysisErrorManager):
        self.error_manager = error_manager

        self.scopes: List[Dict[str, SymbolInfo]] = [{}]

        self.current_function_return_type = None

        self.type_compatibility_rules = {
            ("int", "int", "+"): "int",
            ("int", "int", "-"): "int",
            ("int", "int", "*"): "int",
            ("int", "int", "/"): "int",
            ("float", "float", "+"): "float",
            ("float", "float", "-"): "float",
            ("float", "float", "*"): "float",
            ("float", "float", "/"): "float",
            ("int", "float", "+"): "float",
            ("float", "int", "+"): "float",
            ("int", "float", "-"): "float",
            ("float", "int", "-"): "float",
            ("int", "float", "*"): "float",
            ("float", "int", "*"): "float",
            ("int", "float", "/"): "float",
            ("float", "int", "/"): "float",
            ("string", "string", "+"): "string",
            ("int", "int", "=="): "boolean",
            ("int", "int", ">"): "boolean",
            ("int", "int", "<"): "boolean",
            ("float", "float", "=="): "boolean",
            ("float", "float", ">"): "boolean",
            ("float", "float", "<"): "boolean",
            ("color", "color", "=="): "boolean",
            ("boolean", "boolean", "=="): "boolean",
            ("string", "string", "=="): "boolean",
        }
        self.assignment_rules = {
            "int": {"int"},
            "float": {"float"},
            "color": {"color"},
            "pixel": {"pixel"},
            "image": {"image"},
            "boolean": {"boolean"},
            "string": {"string"},
        }
        self.explicit_cast_rules = {
            ("float", "int"),
            ("int", "float"),
            ("pixel", "color"),
            ("int", "boolean"),
            ("boolean", "int"),
        }

        self._add_built_in_functions()

    def _enter_scope(self):
        self.scopes.append({})

    def _exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise Exception("Cannot exit global scope")

    def _add_symbol(self, name, symbol_info):
        self.scopes[-1][name] = symbol_info

    def _lookup_symbol_local(self, name):
        return self.scopes[-1].get(name, None)

    def _lookup_symbol_chain(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _get_result_type(self, type1, type2, operation):
        return self.type_compatibility_rules.get((type1, type2, operation))

    def _are_types_compatible_for_assignment(self, target_type, source_type):
        if target_type == source_type:
            return True
        allowed_sources = self.assignment_rules.get(target_type, set())
        return source_type in allowed_sources

    def _check_explicit_cast(self, source_type, target_type):
        return (
            source_type,
            target_type,
        ) in self.explicit_cast_rules or source_type == target_type

    def _check_conditional_expression_type(self, expr_type):
        return expr_type == "boolean"

    def _add_built_in_functions(self):
        sqrt_params = [
            SymbolInfo("val", "float", is_parameter=True, is_initialized=True)
        ]
        sqrt_info = SymbolInfo(
            "sqrt", "function", return_type="float", parameters=sqrt_params
        )
        self._add_symbol("sqrt", sqrt_info)

        print_params = [
            SymbolInfo("msg", "string", is_parameter=True, is_initialized=True)
        ]
        print_info = SymbolInfo(
            "print", "function", return_type="void", parameters=print_params
        )
        self._add_symbol("print", print_info)

    def analyze(self, tree):
        self.visit(tree)

    def get_antlr_type_name(self, ctx):
        if isinstance(ctx, ExprParser.TypeContext):
            if ctx.TYPE_INT():
                return "int"
            if ctx.TYPE_COLOR():
                return "color"
            if ctx.TYPE_PIXEL():
                return "pixel"
            if ctx.TYPE_IMAGE():
                return "image"
            if ctx.TYPE_FLOAT():
                return "float"
            if ctx.TYPE_BOOLEAN():
                return "boolean"
            if ctx.TYPE_STRING():
                return "string"
        elif isinstance(ctx, ExprParser.ConstructibleTypeContext):
            if ctx.TYPE_COLOR():
                return "color"
        return "unknown_type"

    def _get_last_id_text_from_atom(self, atom_ctx):
        if atom_ctx.ID():
            return atom_ctx.ID().getText()
        elif atom_ctx.atom() and atom_ctx.DOT():
            return atom_ctx.ID().getText()
        elif atom_ctx.atom() and atom_ctx.LPAREN():
            return self._get_last_id_text_from_atom(atom_ctx.atom())
        return None

    def _get_id_ctx_from_atom(self, atom_ctx):
        if atom_ctx.ID():
            return atom_ctx.ID()
        elif atom_ctx.atom() and atom_ctx.DOT():
            return atom_ctx.ID()
        elif atom_ctx.atom() and atom_ctx.LPAREN():
            return self._get_id_ctx_from_atom(atom_ctx.atom())
        return None

    def visitProgram(self, ctx: ExprParser.ProgramContext):
        return self.visitChildren(ctx)

    def visitFuncDef(self, ctx: ExprParser.FuncDefContext):
        func_name = ctx.ID().getText()

        existing_symbol = self._lookup_symbol_local(func_name)
        if existing_symbol:
            self.error_manager.report_semantic_error(
                f"Function '{func_name}' already initialized (row {existing_symbol.declaration_line}).",
                ctx.start.line,
                ctx.start.column,
            )

        return_type = "void"
        if ctx.type_():
            return_type = self.get_antlr_type_name(ctx.type_())

        parameters = []
        param_names = set()
        if ctx.parameterList():
            for param_ctx in ctx.parameterList().parameter():
                param_type = self.get_antlr_type_name(param_ctx.type_())
                param_name = param_ctx.ID().getText()

                if param_name in param_names:
                    self.error_manager.report_semantic_error(
                        f"Parameter '{param_name}' already inicialized in that function.",
                        param_ctx.start.line,
                        param_ctx.start.column,
                    )
                param_names.add(param_name)
                param_info = SymbolInfo(
                    param_name,
                    param_type,
                    ctx=param_ctx,
                    is_initialized=True,
                    is_parameter=True,
                )
                parameters.append(param_info)

        if not existing_symbol:
            func_info = SymbolInfo(
                func_name,
                "function",
                ctx=ctx,
                return_type=return_type,
                parameters=parameters,
            )
            self._add_symbol(func_name, func_info)

        self._enter_scope()
        self.current_function_return_type = return_type

        for param in parameters:
            if not self._lookup_symbol_local(param.name):
                self._add_symbol(param.name, param)

        self.visit(ctx.block())
        self._exit_scope()
        self.current_function_return_type = None

    def visitVariableDef(self, ctx: ExprParser.VariableDefContext):
        var_name = ctx.ID().getText()
        var_type = self.get_antlr_type_name(ctx.type_())

        if self._lookup_symbol_local(var_name):
            self.error_manager.report_semantic_error(
                f"Variable '{var_name}' already initialized in that scope.",
                ctx.start.line,
                ctx.start.column,
            )

        is_initialized = var_type == "image"

        if ctx.expr():
            expr_type = self.visit(ctx.expr())
            if expr_type != "error_type":
                if not self._are_types_compatible_for_assignment(var_type, expr_type):
                    self.error_manager.report_semantic_error(
                        f"Type mismatch when initializing '{var_name}': expected {var_type}, received {expr_type}.",
                        ctx.expr().start.line,
                        ctx.expr().start.column,
                    )
                else:
                    is_initialized = True

        var_info = SymbolInfo(
            var_name, var_type, ctx=ctx, is_initialized=is_initialized
        )
        self._add_symbol(var_name, var_info)

    def visitAssignment(self, ctx: ExprParser.AssignmentContext):
        var_name = ctx.ID().getText()
        symbol = self._lookup_symbol_chain(var_name)

        if not symbol:
            self.error_manager.report_semantic_error(
                f"Assignment to an undeclared variable '{var_name}'.",
                ctx.ID().symbol.line,
                ctx.ID().symbol.column,
            )
            return

        if symbol.type == "function":
            self.error_manager.report_semantic_error(
                f"Cannot assign a value to a function '{var_name}'.",
                ctx.ID().symbol.line,
                ctx.ID().symbol.column,
            )
            return

        expr_type = self.visit(ctx.expr())
        if expr_type != "error_type":
            if not self._are_types_compatible_for_assignment(symbol.type, expr_type):
                self.error_manager.report_semantic_error(
                    f"Type mismatch when initializing '{var_name}': expected {symbol.type}, recieved {expr_type}.",
                    ctx.expr().start.line,
                    ctx.expr().start.column,
                )
            else:
                symbol.is_initialized = True

    def visitIfStat(self, ctx: ExprParser.IfStatContext):
        expr_type = self.visit(ctx.expr())
        if expr_type != "error_type" and not self._check_conditional_expression_type(
            expr_type
        ):
            self.error_manager.report_semantic_error(
                f"Type mismatch '{expr_type}' in condition. Expected 'boolean'.",
                ctx.expr().start.line,
                ctx.expr().start.column,
            )
        self.visit(ctx.block(0))
        if ctx.block(1):
            self.visit(ctx.block(1))

    def visitForStat(self, ctx: ExprParser.ForStatContext):
        self._enter_scope()
        iter_type = self.get_antlr_type_name(ctx.type_())
        iter_var_name = ctx.ID().getText()
        iter_var_info = SymbolInfo(
            iter_var_name, iter_type, ctx=ctx.ID(), is_initialized=True
        )
        self._add_symbol(iter_var_name, iter_var_info)

        expr_collection_type = self.visit(ctx.expr())

        if expr_collection_type != "error_type":
            if not (expr_collection_type == "image" and iter_type == "pixel"):
                self.error_manager.report_semantic_error(
                    f"Operator 'for' expect 'pixel IN image', recieved '{iter_type} IN {expr_collection_type}'.",
                    ctx.expr().start.line,
                    ctx.expr().start.column,
                )

        self.visit(ctx.block())
        self._exit_scope()

    def visitReturnStat(self, ctx: ExprParser.ReturnStatContext):
        if self.current_function_return_type is None:
            self.error_manager.report_semantic_error(
                "Operator 'return' outside of function.",
                ctx.start.line,
                ctx.start.column,
            )
            return

        expected_type = self.current_function_return_type

        if ctx.expr():
            returned_expr_type = self.visit(ctx.expr())
            if expected_type == "void":
                self.error_manager.report_semantic_error(
                    f"Function 'void' cannot return a value.",
                    ctx.expr().start.line,
                    ctx.expr().start.column,
                )
            elif returned_expr_type != "error_type":
                if not self._are_types_compatible_for_assignment(
                    expected_type, returned_expr_type
                ):
                    self.error_manager.report_semantic_error(
                        f"Type mismatch in 'return': function should return {expected_type}, received {returned_expr_type}.",
                        ctx.expr().start.line,
                        ctx.expr().start.column,
                    )
        else:
            if expected_type != "void":
                self.error_manager.report_semantic_error(
                    f"Function returning '{expected_type}' must return a value.",
                    ctx.start.line,
                    ctx.start.column,
                )

    def visitBlock(self, ctx: ExprParser.BlockContext):
        self._enter_scope()
        self.visitChildren(ctx)
        self._exit_scope()

    def visitCastExpr(self, ctx: ExprParser.CastExprContext):
        if ctx.type_():
            source_type = self.visit(ctx.atom())
            target_type = self.get_antlr_type_name(ctx.type_())

            if source_type != "error_type":
                if not self._check_explicit_cast(source_type, target_type):
                    self.error_manager.report_semantic_error(
                        f"Incorrect explicit type cast: cannot convert '{source_type}' to '{target_type}'.",
                        ctx.type_().start.line,
                        ctx.type_().start.column,
                    )
                    return "error_type"
            return target_type
        return self.visit(ctx.atom())

    def visitAtom(self, ctx: ExprParser.AtomContext):
        if ctx.atom() and ctx.LPAREN():
            left_atom_ctx = ctx.atom()
            func_method_name = self._get_last_id_text_from_atom(left_atom_ctx)
            func_method_id_ctx = self._get_id_ctx_from_atom(left_atom_ctx)

            if not func_method_name or not func_method_id_ctx:
                self.error_manager.report_semantic_error(
                    "Function/method name could not be determined",
                    ctx.start.line,
                    ctx.start.column,
                )
                return "error_type"

            line, col = func_method_id_ctx.symbol.line, func_method_id_ctx.symbol.column
            args_ctx = ctx.argumentList()
            num_args = len(args_ctx.expr()) if args_ctx else 0

            if left_atom_ctx.ID() and not left_atom_ctx.DOT():
                symbol = self._lookup_symbol_chain(func_method_name)
                if not symbol or symbol.type != "function":
                    self.error_manager.report_semantic_error(
                        f"Attempted to call '{func_method_name}', which is not a function.",
                        line,
                        col,
                    )
                    return "error_type"
                return self.check_function_call(symbol, args_ctx, line, col)

            else:
                object_atom_ctx = left_atom_ctx.atom()
                object_type = self.visit(object_atom_ctx)
                if object_type == "error_type":
                    return "error_type"

                if object_type == "pixel":
                    if func_method_name == "get_color":
                        if num_args == 0:
                            return "color"
                        else:
                            self.error_manager.report_semantic_error(
                                f"The 'pixel.get_color' method takes no arguments.",
                                line,
                                col,
                            )
                    elif func_method_name == "set_color":
                        if num_args == 1:
                            arg_type = self.visit(args_ctx.expr(0))
                            if self._are_types_compatible_for_assignment(
                                "color", arg_type
                            ):
                                return "void"
                            else:
                                self.error_manager.report_semantic_error(
                                    f"Method 'pixel.set_color' expects 'color', got '{arg_type}'.",
                                    args_ctx.expr(0).start.line,
                                    args_ctx.expr(0).start.column,
                                )
                        else:
                            self.error_manager.report_semantic_error(
                                f"The 'pixel.set_color' method expects 1 argument.",
                                line,
                                col,
                            )
                    else:
                        self.error_manager.report_semantic_error(
                            f"Unknown method '{func_method_name}' for type 'pixel'.",
                            line,
                            col,
                        )

                elif object_type == "image":
                    if func_method_name == "load":
                        if num_args == 1:
                            arg_type = self.visit(args_ctx.expr(0))
                            if arg_type == "string":
                                return "image"
                            else:
                                self.error_manager.report_semantic_error(
                                    f"Method 'image.load' expects 'string', received '{arg_type}'.",
                                    args_ctx.expr(0).start.line,
                                    args_ctx.expr(0).start.column,
                                )
                        else:
                            self.error_manager.report_semantic_error(
                                f"The 'image.load' method expects 1 argument.",
                                line,
                                col,
                            )
                    elif func_method_name == "save":
                        if num_args == 1:
                            arg_type = self.visit(args_ctx.expr(0))
                            if arg_type == "string":
                                return "void"
                            else:
                                self.error_manager.report_semantic_error(
                                    f"Method 'image.save' expects 'string', received '{arg_type}'.",
                                    args_ctx.expr(0).start.line,
                                    args_ctx.expr(0).start.column,
                                )
                        else:
                            self.error_manager.report_semantic_error(
                                f"The 'image.save' method expects 1 argument.",
                                line,
                                col,
                            )
                    elif func_method_name == "get_pixel":
                        if num_args == 2:
                            arg1_type = self.visit(args_ctx.expr(0))
                            arg2_type = self.visit(args_ctx.expr(1))
                            if arg1_type == "int" and arg2_type == "int":
                                return "pixel"
                            else:
                                self.error_manager.report_semantic_error(
                                    f"Method 'image.get_pixel' expects (int, int), received ({arg1_type}, {arg2_type}).",
                                    line,
                                    col,
                                )
                        else:
                            self.error_manager.report_semantic_error(
                                f"The 'image.get_pixel' method expects 2 arguments.",
                                line,
                                col,
                            )
                    else:
                        self.error_manager.report_semantic_error(
                            f"Unknown method '{func_method_name}' for type 'image'.",
                            line,
                            col,
                        )
                else:
                    self.error_manager.report_semantic_error(
                        f"The type '{object_type}' does not support calling methods.",
                        object_atom_ctx.start.line,
                        object_atom_ctx.start.column,
                    )
                return "error_type"

        elif ctx.atom() and ctx.DOT():
            object_type = self.visit(ctx.atom())
            property_name = ctx.ID().getText()
            line, col = ctx.ID().symbol.line, ctx.ID().symbol.column
            if object_type == "error_type":
                return "error_type"
            if object_type == "color":
                if property_name in ["R", "G", "B"]:
                    return "int"
            elif object_type == "pixel":
                if property_name in ["x", "y"]:
                    return "int"
            elif object_type == "image":
                if property_name in ["width", "height"]:
                    return "int"
            self.error_manager.report_semantic_error(
                f"Unknown property '{property_name}' for type '{object_type}'.",
                line,
                col,
            )
            return "error_type"

        elif ctx.LPAREN() and ctx.expr() and ctx.RPAREN():
            return self.visit(ctx.expr())

        elif ctx.constructibleType():
            constructor_type = self.get_antlr_type_name(ctx.constructibleType())
            args_ctx = ctx.argumentList()
            num_args = len(args_ctx.expr()) if args_ctx else 0
            line, col = ctx.start.line, ctx.start.column
            if constructor_type == "color":
                if num_args == 3:
                    arg_types = [self.visit(arg_expr) for arg_expr in args_ctx.expr()]
                    if all(arg_type == "int" for arg_type in arg_types):
                        return "color"
                    else:
                        self.error_manager.report_semantic_error(
                            f"Constructor 'color' expects (int, int, int), received: {arg_types}.",
                            line,
                            col,
                        )
                else:
                    self.error_manager.report_semantic_error(
                        f"The 'color' constructor expects 3 arguments, received {num_args}.",
                        line,
                        col,
                    )
            else:
                self.error_manager.report_semantic_error(
                    f"Unknown constructor '{constructor_type}'.", line, col
                )
            return "error_type"

        elif ctx.literal():
            if ctx.literal().INT():
                return "int"
            if ctx.literal().FLOAT():
                return "float"
            if ctx.literal().STRING():
                return "string"
            if ctx.literal().TRUE() or ctx.literal().FALSE():
                return "boolean"
            return "unknown_type"

        elif ctx.ID():
            var_name = ctx.ID().getText()
            symbol = self._lookup_symbol_chain(var_name)
            line, col = ctx.ID().symbol.line, ctx.ID().symbol.column

            if not symbol:
                self.error_manager.report_semantic_error(
                    f"Using undeclared variable '{var_name}'.", line, col
                )
                return "error_type"

            if (
                not symbol.is_initialized
                and not symbol.is_parameter
                and symbol.type != "function"
            ):
                is_in_assignment_lhs = False
                parent = ctx.parentCtx
                if (
                    isinstance(parent, ExprParser.AssignmentContext)
                    and parent.ID() == ctx.ID()
                ):
                    is_in_assignment_lhs = True
                if (
                    isinstance(parent, ExprParser.VariableDefContext)
                    and parent.ID() == ctx.ID()
                ):
                    is_in_assignment_lhs = True
                if not is_in_assignment_lhs:
                    self.error_manager.report_semantic_error(
                        f"The variable '{var_name}' is used before initialization.",
                        line,
                        col,
                    )
            return symbol.type

        self.error_manager.report_semantic_error(
            "The expression atom could not be recognized",
            ctx.start.line,
            ctx.start.column,
        )
        return "error_type"

    def check_function_call(
        self,
        func_symbol: SymbolInfo,
        argument_list_ctx: ExprParser.ArgumentListContext,
        line,
        column,
    ):
        expected_params = func_symbol.parameters
        actual_args = argument_list_ctx.expr() if argument_list_ctx else []

        if len(expected_params) != len(actual_args):
            self.error_manager.report_semantic_error(
                f"Function '{func_symbol.name}' expects {len(expected_params)} arguments, received {len(actual_args)}.",
                line,
                column,
            )
            return "error_type"

        has_error = False
        for i, param_info in enumerate(expected_params):
            actual_arg_type = self.visit(actual_args[i])
            if actual_arg_type != "error_type":
                if not self._are_types_compatible_for_assignment(
                    param_info.type, actual_arg_type
                ):
                    self.error_manager.report_semantic_error(
                        f"Type mismatch for argument {i+1} ('{param_info.name}') in '{func_symbol.name}': expected {param_info.type}, received {actual_arg_type}.",
                        actual_args[i].start.line,
                        actual_args[i].start.column,
                    )
                    has_error = True
        return "error_type" if has_error else func_symbol.return_type

    def _handle_binary_expression(self, ctx, child_list_accessor, op_map):
        child_nodes = child_list_accessor()
        left_type = self.visit(child_nodes[0])

        op_index = 0
        for i in range(1, len(child_nodes)):
            if left_type == "error_type":
                return "error_type"
            right_type = self.visit(child_nodes[i])
            if right_type == "error_type":
                return "error_type"

            op_str, op_token_node = None, None
            for text, node_getter in op_map.items():
                node_or_list = node_getter()
                if isinstance(node_or_list, list) and op_index < len(node_or_list):
                    op_token_node = node_or_list[op_index]
                    op_str = text
                    break
                elif (
                    not isinstance(node_or_list, list)
                    and node_or_list
                    and op_index == 0
                ):
                    op_token_node = node_or_list
                    op_str = text
                    break

            if not op_str or not op_token_node:
                self.error_manager.report_semantic_error(
                    f"Operator not found in expression",
                    ctx.start.line,
                    ctx.start.column,
                )
                return "error_type"

            result_type = self._get_result_type(left_type, right_type, op_str)

            if not result_type:
                self.error_manager.report_semantic_error(
                    f"Unsupported operation '{op_str}' between types '{left_type}' and '{right_type}'.",
                    op_token_node.symbol.line,
                    op_token_node.symbol.column,
                )
                return "error_type"
            left_type = result_type
            op_index += 1
        return left_type

    def visitExpr(self, ctx: ExprParser.ExprContext):
        return self.visit(ctx.assignmentExpr())

    def visitAssignmentExpr(self, ctx: ExprParser.AssignmentExprContext):
        if not ctx.ASSIGN():
            return self.visit(ctx.relationalExpr())

        right_type = self.visit(ctx.assignmentExpr())
        left_ctx = ctx.relationalExpr()
        left_type = self.visit(left_ctx)

        if left_type == "error_type" or right_type == "error_type":
            return "error_type"

        is_lvalue = False
        cast_expr_for_lvalue = None
        if (
            isinstance(left_ctx, ExprParser.RelationalExprContext)
            and len(left_ctx.additiveExpr()) == 1
        ):
            add_expr = left_ctx.additiveExpr(0)
            if len(add_expr.multiplicativeExpr()) == 1:
                mult_expr = add_expr.multiplicativeExpr(0)
                if len(mult_expr.castExpr()) == 1:
                    cast_expr = mult_expr.castExpr(0)
                    cast_expr_for_lvalue = cast_expr
                    if not cast_expr.type_() and isinstance(
                        cast_expr.atom(), ExprParser.AtomContext
                    ):
                        atom = cast_expr.atom()
                        if (atom.ID() and not atom.atom()) or (
                            atom.ID() and atom.DOT() and atom.atom()
                        ):
                            is_lvalue = True

        if not is_lvalue:
            self.error_manager.report_semantic_error(
                f"Unable to assign value: left side is not an l-value (variable or property)",
                left_ctx.start.line,
                left_ctx.start.column,
            )
            return "error_type"

        if not self._are_types_compatible_for_assignment(left_type, right_type):
            self.error_manager.report_semantic_error(
                f"Type mismatch when assigning: unable to assign '{right_type}' to '{left_type}'.",
                ctx.ASSIGN().symbol.line,
                ctx.ASSIGN().symbol.column,
            )
            return "error_type"

        if (
            is_lvalue
            and cast_expr_for_lvalue
            and cast_expr_for_lvalue.atom().ID()
            and not cast_expr_for_lvalue.atom().atom()
        ):
            symbol = self._lookup_symbol_chain(
                cast_expr_for_lvalue.atom().ID().getText()
            )
            if symbol:
                symbol.is_initialized = True

        return left_type

    def visitRelationalExpr(self, ctx: ExprParser.RelationalExprContext):
        return self._handle_binary_expression(
            ctx, ctx.additiveExpr, {"==": ctx.EQ_EQ, ">": ctx.GT, "<": ctx.LT}
        )

    def visitAdditiveExpr(self, ctx: ExprParser.AdditiveExprContext):
        return self._handle_binary_expression(
            ctx, ctx.multiplicativeExpr, {"+": ctx.PLUS, "-": ctx.MINUS}
        )

    def visitMultiplicativeExpr(self, ctx: ExprParser.MultiplicativeExprContext):
        return self._handle_binary_expression(
            ctx, ctx.castExpr, {"*": ctx.MULT, "/": ctx.DIV}
        )

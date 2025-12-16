from gen.yapis2Parser import yapis2Parser
from gen.yapis2Visitor import yapis2Visitor


class SemanticAnalyzer(yapis2Visitor):
    BUILTIN_FUNCS = {
        "read":    {"params": [], "ret": "int"},
        "write":   {"params": "varargs", "ret": "void"},
        "point":   {"params": ["int", "int"], "ret": "point"},
        "line":    {"params": ["point", "point"], "ret": "line"},
        "circle":  {"params": ["point", "int"], "ret": "circle"},
        "polygon": {"params": "points_varargs", "ret": "polygon"},
        "distance": {"params": ["point", "point"], "ret": "int"},
        "intersection": {"params": ["line", "line"], "ret": "point"},
        "inside": {"params": ["point", {"one_of": ["circle", "polygon"]}], "ret": "bool"},
    }

    BUILTIN_TYPES = {"int", "point", "line", "circle", "polygon", "bool", "string"}

    def __init__(self):
        super().__init__()
        self.scopes = [{}]
        self.functions = {}
        self.errors = []
        self.current_function = None
        self.current_function_has_return = False

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def current_scope(self):
        return self.scopes[-1]

    def find_var(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def add_error(self, msg, ctx):
        line = ctx.start.line if hasattr(ctx, "start") else "?"
        self.errors.append(f"[строка {line}] {msg}")

    def visitProgram(self, ctx: yapis2Parser.ProgramContext):
        for f in ctx.functionDecl():
            self.register_function(f)

        self.visitChildren(ctx)

        return self.errors

    def register_function(self, ctx: yapis2Parser.FunctionDeclContext):
        name = ctx.IDENTIFIER(0).getText()
        param_types = []
        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                param_types.append(p.type_().getText())
        ret_type = ctx.type_().getText() if hasattr(ctx, "type_") and ctx.type_() else None

        if name in self.functions:
            self.add_error(f"Функция '{name}' уже объявлена (перегрузка запрещена)", ctx)
        else:
            self.functions[name] = (param_types, ret_type, ctx.start.line)

    def visitFunctionDecl(self, ctx: yapis2Parser.FunctionDeclContext):
        name = ctx.IDENTIFIER(0).getText()
        ret_type = ctx.type_().getText() if hasattr(ctx, "type_") and ctx.type_() else None

        param_types = []
        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                param_types.append(p.type_().getText())

        self.current_function = (name, ret_type)
        self.current_function_has_return = False
        self.push_scope()

        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                pname = p.IDENTIFIER().getText()
                ptype = p.type_().getText()
                if pname in self.current_scope():
                    self.add_error(f"Повторное объявление параметра '{pname}'", p)
                self.current_scope()[pname] = ptype

        if ctx.block():
            for stmt in ctx.block().statement():
                self.visit(stmt)

        if ret_type and not self.current_function_has_return:
            self.add_error(f"Функция '{name}' должна возвращать значение типа '{ret_type}'", ctx)

        self.pop_scope()
        self.current_function = None
        return None

    def visitVariableDecl(self, ctx: yapis2Parser.VariableDeclContext):
        # rule: IDENTIFIER '=' expression
        name = ctx.IDENTIFIER().getText()
        if name in self.current_scope():
            self.add_error(f"Переменная '{name}' уже объявлена в текущей области", ctx)
        expr_type = self.infer_type(ctx.expression())
        self.current_scope()[name] = expr_type
        return None

    def visitAssignment(self, ctx: yapis2Parser.AssignmentContext):
        name = ctx.IDENTIFIER().getText()
        target_type = self.find_var(name)
        expr_type = self.infer_type(ctx.expression())
        if target_type is None:
            self.current_scope()[name] = expr_type
        else:
            if target_type and expr_type and target_type != expr_type:
                self.add_error(
                    f"Невозможно присвоить значение типа '{expr_type}' переменной '{name}' типа '{target_type}'",
                    ctx
                )
        return None

    def visitReturnStatement(self, ctx: yapis2Parser.ReturnStatementContext):
        if not self.current_function:
            self.add_error("Оператор return вне функции", ctx)
            return None
        expected_type = self.current_function[1]
        actual_type = self.infer_type(ctx.expression())

        if expected_type is None:
            if actual_type is not None:
                self.add_error(f"Функция '{self.current_function[0]}' не должна возвращать значение", ctx)
        else:
            if actual_type is None:
                self.add_error(f"Функция '{self.current_function[0]}' должна возвращать '{expected_type}', но return пустой", ctx)
            elif actual_type != expected_type:
                self.add_error(
                    f"Функция '{self.current_function[0]}' должна возвращать '{expected_type}', но возвращается '{actual_type}'",
                    ctx
                )
        self.current_function_has_return = True
        return None

    def visitIfStatement(self, ctx: yapis2Parser.IfStatementContext):
        cond_type = self.infer_type(ctx.expression())
        if cond_type and cond_type != "bool":
            self.add_error("Условие if должно быть типа bool", ctx)
        self.push_scope()
        for stmt in ctx.block(0).statement():
            self.visit(stmt)
        self.pop_scope()
        if ctx.block(1):
            self.push_scope()
            for stmt in ctx.block(1).statement():
                self.visit(stmt)
            self.pop_scope()
        return None

    def visitWhileStatement(self, ctx: yapis2Parser.WhileStatementContext):
        cond_type = self.infer_type(ctx.expression())
        if cond_type and cond_type != "bool":
            self.add_error("Условие while должно быть типа bool", ctx)
        self.push_scope()
        for stmt in ctx.block().statement():
            self.visit(stmt)
        self.pop_scope()
        return None

    def visitForStatement(self, ctx: yapis2Parser.ForStatementContext):
        self.push_scope()
        it_name = ctx.IDENTIFIER().getText()
        self.current_scope()[it_name] = "int"
        start_t = self.infer_type(ctx.expression(0))
        end_t = self.infer_type(ctx.expression(1))
        if start_t and start_t != "int":
            self.add_error("Начальное значение for должно быть int", ctx.expression(0))
        if end_t and end_t != "int":
            self.add_error("Конечное значение for должно быть int", ctx.expression(1))
        if ctx.expression(2):
            step_t = self.infer_type(ctx.expression(2))
            if step_t and step_t != "int":
                self.add_error("Шаг for должен быть int", ctx.expression(2))

        for stmt in ctx.block().statement():
            self.visit(stmt)
        self.pop_scope()
        return None

    def visitFunctionCall(self, ctx: yapis2Parser.FunctionCallContext):
        if ctx.IDENTIFIER():
            name = ctx.IDENTIFIER().getText()
        else:
            name = ctx.builtInFunction().getText()

        args = ctx.argumentList().expression() if ctx.argumentList() else []
        arg_types = [self.infer_type(a) for a in args]

        if name in self.BUILTIN_FUNCS:
            self.check_builtin_call(name, arg_types, ctx)
            return None

        if name not in self.functions:
            self.add_error(f"Вызов необъявленной функции '{name}'", ctx)
            return None

        expected_params, _, decl_line = self.functions[name]
        if len(expected_params) != len(arg_types):
            self.add_error(
                f"Функция '{name}' ожидает {len(expected_params)} арг., передано {len(arg_types)}",
                ctx
            )
        else:
            for i, (exp_t, got_t) in enumerate(zip(expected_params, arg_types)):
                if exp_t and got_t and exp_t != got_t:
                    self.add_error(
                        f"Аргумент {i + 1} функции '{name}' должен быть '{exp_t}', получен '{got_t}'",
                        ctx
                    )
        return None

    def check_builtin_call(self, name, arg_types, ctx):
        spec = self.BUILTIN_FUNCS[name]
        params = spec["params"]
        if params == "varargs":
            return
        if params == "points_varargs":
            if len(arg_types) < 3:
                self.add_error("Функция 'polygon' требует >=3 точек", ctx)
                return
            for i, t in enumerate(arg_types):
                if t and t != "point":
                    self.add_error(f"Аргумент {i + 1} функции 'polygon' должен быть 'point'", ctx)
            return
        if len(params) != len(arg_types):
            self.add_error(f"Функция '{name}' ожидает {len(params)} арг., передано {len(arg_types)}", ctx)
            return
        for i, (exp, got) in enumerate(zip(params, arg_types)):
            if isinstance(exp, dict) and "one_of" in exp:
                if got not in exp["one_of"]:
                    self.add_error(
                        f"Аргумент {i + 1} функции '{name}' должен быть одним из {exp['one_of']}, получен '{got}'",
                        ctx
                    )
            else:
                if got and exp != got:
                    self.add_error(
                        f"Аргумент {i + 1} функции '{name}' должен быть '{exp}', получен '{got}'",
                        ctx
                    )

    def visitExpression(self, ctx: yapis2Parser.ExpressionContext):
        self.infer_type(ctx)
        return None

    def infer_type(self, ctx):
        if ctx is None:
            return None

        if isinstance(ctx, yapis2Parser.LiteralExprContext):
            return self.type_of_literal(ctx.literal())
        if isinstance(ctx, yapis2Parser.IdentifierExprContext):
            name = ctx.IDENTIFIER().getText()
            var_t = self.find_var(name)
            if var_t is None:
                self.add_error(f"Использование переменной '{name}' вне области видимости", ctx)
            return var_t
        if isinstance(ctx, yapis2Parser.FunctionCallExprContext):
            return self.type_of_call(ctx.functionCall())
        if isinstance(ctx, yapis2Parser.ParenthesizedExprContext):
            return self.infer_type(ctx.expression())
        if isinstance(ctx, yapis2Parser.CastExprContext):
            target_t = ctx.type_().getText() if hasattr(ctx, "type_") and ctx.type_() else None
            self.infer_type(ctx.expression())
            return target_t
        if isinstance(ctx, yapis2Parser.NotExprContext):
            inner_t = self.infer_type(ctx.expression())
            if inner_t and inner_t != "bool":
                self.add_error("Унарный ! применим только к bool", ctx)
            return "bool"
        if isinstance(ctx, yapis2Parser.MemberAccessExprContext):
            base_t = self.infer_type(ctx.expression())
            return "int"

        if hasattr(ctx, "op"):
            if hasattr(ctx, "expression") and len(ctx.expression()) == 2:
                left_node, right_node = ctx.expression()
                left_t = self.infer_type(left_node)
                right_t = self.infer_type(right_node)
                op_text = ctx.op.text
                if op_text in ("*", "/", "%", "+", "-"):
                    return "int"
                if op_text in ("<", ">", "<=", ">=", "==", "!="):
                    if left_t and right_t and left_t != right_t:
                        self.add_error("Сравнение типов должно быть между одинаковыми типами", ctx)
                    return "bool"
                if op_text in ("&&", "||"):
                    if left_t != "bool" or right_t != "bool":
                        self.add_error("Логические операции требуют операнды bool", ctx)
                    return "bool"

        for child in ctx.getChildren():
            t = self.infer_type(getattr(child, "ctx", child)) if hasattr(child, "ctx") else self.infer_type(child)
            if t:
                return t
        return None

    def type_of_literal(self, lit_ctx):
        if lit_ctx.INT():
            return "int"
        if lit_ctx.STRING():
            return "string"
        return None

    def type_of_call(self, call_ctx: yapis2Parser.FunctionCallContext):
        if call_ctx.IDENTIFIER():
            name = call_ctx.IDENTIFIER().getText()
        else:
            name = call_ctx.builtInFunction().getText()

        args = call_ctx.argumentList().expression() if call_ctx.argumentList() else []
        arg_types = [self.infer_type(a) for a in args]

        if name in self.BUILTIN_FUNCS:
            spec = self.BUILTIN_FUNCS[name]
            if name == "polygon":
                self.check_builtin_call(name, arg_types, call_ctx)
            return spec["ret"]

        if name in self.functions:
            param_types, ret_type, _ = self.functions[name]
            if len(param_types) != len(arg_types):
                self.add_error(f"Функция '{name}' ожидает {len(param_types)} арг., передано {len(arg_types)}", call_ctx)
            else:
                for i, (exp_t, got_t) in enumerate(zip(param_types, arg_types)):
                    if exp_t and got_t and exp_t != got_t:
                        self.add_error(
                            f"Аргумент {i + 1} функции '{name}' должен быть '{exp_t}', получен '{got_t}'",
                            call_ctx
                        )
            return ret_type

        self.add_error(f"Вызов необъявленной функции '{name}'", call_ctx)
        return None


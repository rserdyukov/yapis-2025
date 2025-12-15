from gen.langParser import langParser
from gen.langVisitor import langVisitor


class SemanticAnalyzer(langVisitor):
    BUILTIN_NAMES = {"read", "write", "println", "toInt", "split", "size", "get", "add", "remove",
                     "isEmpty", "set", "element", "bool", "int", "float", "double", "char", "str"}

    def __init__(self):
        self.scopes = [{}]
        self.functions = {}
        self.errors = []
        self.current_function = None

    def current_scope(self):
        return self.scopes[-1]

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        self.scopes.pop()

    def add_error(self, msg, ctx):
        line = ctx.start.line if hasattr(ctx, "start") else "?"
        self.errors.append(f"[строка {line}] {msg}")

    def visitProgram(self, ctx: langParser.ProgramContext):
        for stmt in ctx.statement():
            if isinstance(stmt, langParser.FunctionDefContext):
                self.visit(stmt)
            else:
                break

        for stmt in ctx.statement():
            self.visit(stmt)

        return self.errors

    def visitFunctionDef(self, ctx: langParser.FunctionDefContext):
        func_name = ctx.ID().getText()
        return_type = ctx.type_().getText() if hasattr(ctx, "type_") and ctx.type_() else None
        param_types = []

        if func_name in self.BUILTIN_NAMES:
            self.add_error(f"Использование имени встроенной функции/типа '{func_name}' запрещено", ctx)
            return

        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                param_types.append(p.type_().getText())

        if func_name not in self.functions:
            self.functions[func_name] = []

        for existing_return, existing_params in self.functions[func_name]:
            if existing_params == param_types:
                self.add_error(f"Функция '{func_name}' с такой сигнатурой уже объявлена", ctx)
                return

        self.functions[func_name].append((return_type, param_types))
        self.current_function = (func_name, return_type)

        self.push_scope()
        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                self.current_scope()[p.ID().getText()] = p.type_().getText()

        if ctx.statement():
            for s in ctx.statement():
                self.visit(s)

        if return_type != "void":
            if not self.has_return_stmt(ctx):
                self.add_error(f"Функция '{func_name}' должна возвращать значение типа '{return_type}'", ctx)

        self.pop_scope()
        self.current_function = None
        return None

    def has_return_stmt(self, ctx):
        """Рекурсивно ищет return в теле функции"""
        if ctx is None:
            return False

        from gen.langParser import langParser
        if isinstance(ctx, langParser.SimpleStmtContext):
            if ctx.getText().startswith("return"):
                return True

        if hasattr(ctx, "getChildren"):
            for child in ctx.getChildren():
                if self.has_return_stmt(child):
                    return True

        return False

    def visitVarDecl(self, ctx: langParser.VarDeclContext):
        declared_type = ctx.type_().getText() if hasattr(ctx, "type_") and ctx.type_() else None

        for id_token in ctx.ID():
            name = id_token.getText()

            if name in self.BUILTIN_NAMES:
                self.add_error(f"Использование имени встроенной функции/типа '{name}' запрещено", ctx)
                continue

            if name in self.current_scope():
                self.add_error(f"Переменная '{name}' уже объявлена в текущей области видимости", ctx)
            else:
                self.current_scope()[name] = declared_type

        if ctx.exprList() and declared_type:
            for expr_ctx in ctx.exprList().expr():
                expr_type = self.infer_type(expr_ctx)
                if expr_type and expr_type != declared_type:
                    self.add_error(
                        f"Невозможно присвоить значение типа '{expr_type}' переменной '{name}' типа '{declared_type}'",
                        ctx
                    )
        return None

    def visitAssignment(self, ctx: langParser.AssignmentContext):
        for id_token in ctx.ID():
            name = id_token.getText()
            var_type = self.find_var(name)
            if var_type is None:
                self.current_scope()[name] = None
            else:
                if ctx.exprList():
                    for expr_ctx in ctx.exprList().expr():
                        expr_type = self.infer_type(expr_ctx)
                        if expr_type and var_type and expr_type != var_type:
                            self.add_error(
                                f"Невозможно присвоить значение типа '{expr_type}' переменной '{name}' типа '{var_type}'",
                                ctx
                            )
        return None

    def visitFuncCall(self, ctx: langParser.FuncCallContext):
        func_name = ctx.ID().getText()

        if func_name in self.functions:
            passed_args = ctx.argList().expr() if ctx.argList() else []
            matched = False
            for ret_type, param_types in self.functions[func_name]:
                if len(param_types) == len(passed_args):
                    matched = True
                    break
            if not matched:
                self.add_error(
                    f"Функция '{func_name}' не найдена среди перегрузок с подходящим количеством аргументов",
                    ctx
                )
            for arg in passed_args:
                self.infer_type(arg)
            return None

        elif func_name in self.BUILTIN_NAMES:
            passed_args = ctx.argList().expr() if ctx.argList() else []
            for arg in passed_args:
                # Проверяем видимость переменной в текущей области
                if hasattr(arg, "ID") and arg.ID():
                    var_name = arg.ID().getText()
                    var_type = self.find_var(var_name)
                    if var_type is None:
                        self.add_error(
                            f"Использование переменной '{var_name}' вне области видимости",
                            arg
                        )
                else:
                    self.infer_type(arg)  # рекурсивно проверим вложенные выражения
            return None

        else:
            self.add_error(f"Вызов необъявленной функции '{func_name}'", ctx)
            return None

    def find_var(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def infer_type(self, ctx):
        from gen.langParser import langParser
        if ctx is None:
            return None

        if isinstance(ctx, langParser.FuncCallContext):
            func_name = ctx.ID().getText()
            if func_name in self.functions:
                return self.functions[func_name][0][0]  # возвращаемый тип первого перегруза
            elif func_name in self.BUILTIN_NAMES:
                if func_name == "println":
                    return "void"
                return None
            else:
                self.add_error(f"Вызов необъявленной функции '{func_name}'", ctx)
                return None

        text = ctx.getText()
        if text.isdigit():
            return "int"
        if text.replace(".", "", 1).isdigit():
            return "float"
        if text.startswith('"') and text.endswith('"'):
            return "str"
        if text in {"true", "false"}:
            return "bool"

        if hasattr(ctx, "ID") and ctx.ID() and not isinstance(ctx, langParser.FuncCallContext):
            var_name = ctx.ID().getText()
            var_type = self.find_var(var_name)
            if var_type is None:
                self.add_error(f"Использование переменной '{var_name}' вне области видимости", ctx)
            return var_type

        for child in ctx.getChildren():
            child_type = self.infer_type(child)
            if child_type is not None:
                return child_type

        return None

    def visitIfStmt(self, ctx):
        cond_type = self.infer_type(ctx.expr())
        if cond_type != "bool":
            self.add_error("Условие в if должно быть типа boolean", ctx)
        self.push_scope()
        for stmt in ctx.statement():
            self.visit(stmt)
        self.pop_scope()

    def visitWhileStmt(self, ctx):
        cond_type = self.infer_type(ctx.expr())
        if cond_type != "bool":
            self.add_error("Условие в while должно быть типа boolean", ctx)
        self.push_scope()
        for stmt in ctx.statement():
            self.visit(stmt)
        self.pop_scope()

    def visitForStmt(self, ctx):
        cond_type = self.infer_type(ctx.forCond())
        if cond_type != "bool":
            self.add_error("Условие в for должно быть типа boolean", ctx)
        self.push_scope()
        for stmt in ctx.statement():
            self.visit(stmt)
        self.pop_scope()

    def visitSimpleStmt(self, ctx: langParser.SimpleStmtContext):
        if ctx.getText().startswith("return") and self.current_function:
            expected_type = self.current_function[1]
            ret_expr = ctx.expr() if hasattr(ctx, "expr") else None
            actual_type = self.infer_type(ret_expr)

            if expected_type != "void":
                if ret_expr is None:
                    self.add_error(
                        f"Функция '{self.current_function[0]}' должна возвращать значение типа '{expected_type}', но return пустой",
                        ctx
                    )
                elif actual_type != expected_type:
                    self.add_error(
                        f"Функция '{self.current_function[0]}' должна возвращать тип '{expected_type}', "
                        f"но возвращается '{actual_type}'",
                        ctx
                    )
            elif expected_type == "void" and ret_expr is not None:
                self.add_error(
                    f"Функция '{self.current_function[0]}' объявлена как void, но возвращает значение",
                    ctx
                )

        return self.visitChildren(ctx)

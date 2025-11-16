from gen.langParser import langParser
from gen.langVisitor import langVisitor

class SemanticAnalyzer(langVisitor):
    BUILTIN_NAMES = {
        "read", "write", "println", "toInt", "split", "size", "get", "add", "remove",
        "isEmpty", "set", "element", "bool", "int", "float", "double", "char", "str", "open",
        "getFileNames"
    }

    BUILTIN_FUNCTIONS = {
        "read": ("str", []),
        "println": ("void", ["unknown"]),
        "toInt": ("int", ["str"]),
        "split": ("set", ["str", "str"]),
        "size": ("int", ["unknown"]),
        "isEmpty": ("bool", ["set"]),
        "add": ("void", ["set", "unknown"]),
        "remove": ("void", ["set", "int"]),
        "open": ("str", ["str"]),
        "getFileNames": ("set", ["str"]),
        "get": ("str", ["unknown", "int"])
    }

    def __init__(self):
        self.scopes = [{}]
        self.functions = {name: [sig] for name, sig in self.BUILTIN_FUNCTIONS.items()}
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

    def find_var(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _has_comparison_operator(self, ctx):
        if ctx is None:
            return False
        
        from gen.langParser import langParser
        
        if isinstance(ctx, langParser.ExprContext):
            if ctx.getChildCount() == 3:
                middle_child = ctx.getChild(1)
                
                if hasattr(middle_child, 'getText'):
                    op_text = middle_child.getText().strip()
                    comparison_ops = {"<", ">", "<=", ">=", "==", "!=", "&&", "||"}
                    if op_text in comparison_ops:
                        return True
                
                try:
                    if (ctx.OR() is not None and len(ctx.OR()) > 0) or \
                       (ctx.AND() is not None and len(ctx.AND()) > 0) or \
                       (ctx.EQ() is not None and len(ctx.EQ()) > 0) or \
                       (ctx.NEQ() is not None and len(ctx.NEQ()) > 0) or \
                       (ctx.LT() is not None and len(ctx.LT()) > 0) or \
                       (ctx.LE() is not None and len(ctx.LE()) > 0) or \
                       (ctx.GT() is not None and len(ctx.GT()) > 0) or \
                       (ctx.GE() is not None and len(ctx.GE()) > 0):
                        return True
                except:
                    pass
                
                if hasattr(middle_child, 'symbol') and middle_child.symbol:
                    token_type = middle_child.symbol.type
                    if token_type in {langParser.LE, langParser.GE, langParser.EQ, langParser.NEQ, 
                                      langParser.LT, langParser.GT, langParser.AND, langParser.OR}:
                        return True
                
                for i in [0, 2]:
                    if self._has_comparison_operator(ctx.getChild(i)):
                        return True
        
        if hasattr(ctx, "getChildren"):
            for child in ctx.getChildren():
                if self._has_comparison_operator(child):
                    return True
        
        return False

    def visitProgram(self, ctx: langParser.ProgramContext):
        for stmt in ctx.statement():
            if isinstance(stmt, langParser.FunctionDefContext):
                self.visit(stmt)
        for stmt in ctx.statement():
            self.visit(stmt)
        return self.errors

    def visitFunctionDef(self, ctx: langParser.FunctionDefContext):
        func_name = ctx.ID().getText()
        return_type = ctx.type_().getText() if ctx.type_() else None
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

        for stmt in ctx.statement():
            self.visit(stmt)

        if return_type != "void" and not self.has_return_stmt(ctx):
            self.add_error(f"Функция '{func_name}' должна возвращать значение типа '{return_type}'", ctx)

        self.pop_scope()
        self.current_function = None

    def has_return_stmt(self, ctx):
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
        declared_type = ctx.type_().getText() if ctx.type_() else None
        exprs = ctx.exprList().expr() if ctx.exprList() else []

        for i, id_token in enumerate(ctx.ID()):
            name = id_token.getText()
            if name in self.BUILTIN_NAMES:
                self.add_error(f"Использование имени встроенной функции/типа '{name}' запрещено", ctx)
                continue

            expr_type = self.infer_type(exprs[i]) if i < len(exprs) else None

            if expr_type == "literal_set":
                expr_type = "set"

            final_type = declared_type or expr_type or "unknown"

            if name in self.current_scope():
                self.add_error(f"Переменная '{name}' уже объявлена в текущей области видимости", ctx)
            self.current_scope()[name] = final_type

            if expr_type and expr_type != final_type:
                self.add_error(
                    f"Невозможно присвоить значение типа '{expr_type}' переменной '{name}' типа '{final_type}'",
                    ctx
                )

    def visitAssignment(self, ctx: langParser.AssignmentContext):
        if ctx.type_():
            declared_type = ctx.type_().getText()
            exprs = ctx.exprList().expr() if ctx.exprList() else []
            for i, id_token in enumerate(ctx.ID()):
                name = id_token.getText()
                if name in self.BUILTIN_NAMES:
                    self.add_error(f"Использование имени встроенной функции/типа '{name}' запрещено", ctx)
                    continue
                expr_type = self.infer_type(exprs[i]) if i < len(exprs) else None
                if name in self.current_scope():
                    self.add_error(f"Переменная '{name}' уже объявлена в текущей области видимости", ctx)
                self.current_scope()[name] = declared_type
                if expr_type and expr_type != declared_type:
                    self.add_error(
                        f"Невозможно присвоить значение типа '{expr_type}' переменной '{name}' типа '{declared_type}'",
                        ctx
                    )
        else:
            exprs = ctx.exprList().expr() if ctx.exprList() else []
            
            has_assign_op = ctx.PLUS_ASSIGN() or ctx.MINUS_ASSIGN() or ctx.MUL_ASSIGN() or ctx.DIV_ASSIGN()
            has_inc_dec = ctx.INC() or ctx.DEC()
            
            for i, id_token in enumerate(ctx.ID()):
                name = id_token.getText()
                var_type = self.find_var(name)
                
                if has_inc_dec:
                    if var_type is None:
                        self.add_error(f"Использование переменной '{name}' вне области видимости", ctx)
                elif has_assign_op:
                    expr = ctx.expr() if ctx.expr() else None
                    expr_type = self.infer_type(expr) if expr else None
                    if var_type is None:
                        self.add_error(f"Использование переменной '{name}' вне области видимости", ctx)
                    elif expr_type and var_type and expr_type != var_type:
                        self.add_error(
                            f"Невозможно присвоить значение типа '{expr_type}' переменной '{name}' типа '{var_type}'",
                            ctx
                        )
                else:
                    expr_type = self.infer_type(exprs[i]) if i < len(exprs) else None
                    if var_type is None:
                        if expr_type == "literal_set":
                            expr_type = "set"
                        self.current_scope()[name] = expr_type or "unknown"
                    else:
                        if expr_type and expr_type != var_type:
                            self.add_error(
                                f"Невозможно присвоить значение типа '{expr_type}' переменной '{name}' типа '{var_type}'",
                                ctx
                            )

    def visitFuncCall(self, ctx: langParser.FuncCallContext):
        func_name = ctx.ID().getText()
        args = ctx.argList().expr() if ctx.argList() else []

        if func_name in self.functions:
            matched = any(len(param_types) == len(args) for _, param_types in self.functions[func_name])
            if not matched:
                self.add_error(
                    f"Функция '{func_name}' не найдена среди перегрузок с подходящим количеством аргументов",
                    ctx
                )
            for arg in args:
                self.infer_type(arg)
        elif func_name in self.BUILTIN_NAMES:
            for arg in args:
                self.infer_type(arg)
        else:
            self.add_error(f"Вызов необъявленной функции '{func_name}'", ctx)

    def infer_type(self, ctx):
        if ctx is None:
            return "unknown"

        from gen.langParser import langParser

        if isinstance(ctx, langParser.ExprContext):
            try:
                has_comparison = False
                if ctx.getChildCount() == 3:
                    if (ctx.OR() is not None and len(ctx.OR()) > 0) or \
                       (ctx.AND() is not None and len(ctx.AND()) > 0) or \
                       (ctx.EQ() is not None and len(ctx.EQ()) > 0) or \
                       (ctx.NEQ() is not None and len(ctx.NEQ()) > 0) or \
                       (ctx.LT() is not None and len(ctx.LT()) > 0) or \
                       (ctx.LE() is not None and len(ctx.LE()) > 0) or \
                       (ctx.GT() is not None and len(ctx.GT()) > 0) or \
                       (ctx.GE() is not None and len(ctx.GE()) > 0):
                        has_comparison = True
                    
                    if not has_comparison:
                        middle_child = ctx.getChild(1)
                        if hasattr(middle_child, 'getText'):
                            op_text = middle_child.getText().strip()
                            comparison_ops = {"<", ">", "<=", ">=", "==", "!=", "&&", "||"}
                            if op_text in comparison_ops:
                                has_comparison = True
                    
                    if not has_comparison and hasattr(ctx.getChild(1), 'symbol') and ctx.getChild(1).symbol:
                        token_type = ctx.getChild(1).symbol.type
                        if token_type in {langParser.LE, langParser.GE, langParser.EQ, langParser.NEQ, 
                                          langParser.LT, langParser.GT, langParser.AND, langParser.OR}:
                            has_comparison = True
                
                if has_comparison:
                    if ctx.getChildCount() == 3:
                        left_type = self.infer_type(ctx.getChild(0))
                        right_type = self.infer_type(ctx.getChild(2))
                    return "bool"
            except Exception as e:
                pass

        text = ctx.getText()
        if text == "set[]":
            return "literal_set"

        if isinstance(ctx, langParser.FuncCallContext):
            func_name = ctx.ID().getText()
            if func_name in self.functions:
                return self.functions[func_name][0][0]
            elif func_name in self.BUILTIN_NAMES:
                return self.BUILTIN_FUNCTIONS.get(func_name, ("unknown", []))[0]
            else:
                self.add_error(f"Вызов необъявленной функции '{func_name}'", ctx)
                return "unknown"
        
        if isinstance(ctx, langParser.FuncCallPrimaryContext):
            func_call = ctx.funcCall()
            if func_call:
                func_name = func_call.ID().getText()
                if func_name in self.functions:
                    return self.functions[func_name][0][0]
                elif func_name in self.BUILTIN_NAMES:
                    return self.BUILTIN_FUNCTIONS.get(func_name, ("unknown", []))[0]
                else:
                    return "unknown"

        if text.isdigit():
            return "int"
        if text.replace(".", "", 1).isdigit():
            return "float"
        if text.startswith('"') and text.endswith('"'):
            return "str"
        if text in {"true", "false"}:
            return "bool"

        if isinstance(ctx, langParser.IdWithIndexContext):
            var_name = ctx.ID().getText()
            var_type = self.find_var(var_name)
            if var_type is None:
                self.add_error(f"Использование переменной '{var_name}' вне области видимости", ctx)
                return "unknown"
            if ctx.indexSuffix():
                if var_type == "set":
                    return "unknown"
                return var_type
            return var_type
        
        if hasattr(ctx, "ID") and ctx.ID() and not isinstance(ctx, langParser.FuncCallContext) and not isinstance(ctx, langParser.IdWithIndexContext):
            var_name = ctx.ID().getText()
            var_type = self.find_var(var_name)
            if var_type is None:
                return "unknown"
            return var_type


        if isinstance(ctx, langParser.PrefixExprContext):
            if ctx.NOT():
                return "bool"
            operand_type = self.infer_type(ctx.expr())
            return operand_type

        if isinstance(ctx, langParser.PostfixExprContext):
            operand_type = self.infer_type(ctx.primary())
            return operand_type

        if isinstance(ctx, langParser.ExprContext) and ctx.getChildCount() == 3:
            middle_child = ctx.getChild(1)
            if hasattr(middle_child, 'getText'):
                op_text = middle_child.getText()
                if op_text in {"+", "-", "*", "/", "%"}:
                    left_type = self.infer_type(ctx.getChild(0))
                    right_type = self.infer_type(ctx.getChild(2))
                    
                    if op_text == "+" and (left_type == "str" or right_type == "str"):
                        return "str"
                    
                    if left_type in {"int", "float", "double"} and right_type in {"int", "float", "double"}:
                        if left_type in {"float", "double"} or right_type in {"float", "double"}:
                            return "float" if left_type == "float" or right_type == "float" else "double"
                        return "int"
                    if left_type == "unknown" or right_type == "unknown":
                        return "unknown"
                    return left_type if left_type != "unknown" else right_type

        if hasattr(ctx, "getChildren"):
            for child in ctx.getChildren():
                child_type = self.infer_type(child)
                if child_type != "unknown":
                    return child_type

        return "unknown"

    def visitIfStmt(self, ctx):
        expr_ctx = ctx.expr()
        cond_type = self.infer_type(expr_ctx)
        
        if cond_type != "bool":
            if self._has_comparison_in_expr(expr_ctx):
                cond_type = "bool"
            else:
                self.add_error("Условие в if должно быть типа boolean", ctx)

        self.push_scope()
        for stmt in ctx.statement():
            self.visit(stmt)
        self.pop_scope()

    def visitWhileStmt(self, ctx):
        expr_ctx = ctx.expr()
        cond_type = self.infer_type(expr_ctx)
        
        if cond_type != "bool":
            if self._has_comparison_in_expr(expr_ctx):
                cond_type = "bool"
            else:
                self.add_error("Условие в while должно быть типа boolean", ctx)

        self.push_scope()
        for stmt in ctx.statement():
            self.visit(stmt)
        self.pop_scope()
    
    def _has_comparison_in_expr(self, ctx):
        if ctx is None:
            return False
        
        from gen.langParser import langParser
        
        if isinstance(ctx, langParser.ExprContext):
            if ctx.getChildCount() == 3:
                middle_child = ctx.getChild(1)
                
                if hasattr(middle_child, 'getText'):
                    op_text = middle_child.getText().strip()
                    comparison_ops = {"<", ">", "<=", ">=", "==", "!=", "&&", "||"}
                    if op_text in comparison_ops:
                        return True
                
                try:
                    if (ctx.OR() is not None and len(ctx.OR()) > 0) or \
                       (ctx.AND() is not None and len(ctx.AND()) > 0) or \
                       (ctx.EQ() is not None and len(ctx.EQ()) > 0) or \
                       (ctx.NEQ() is not None and len(ctx.NEQ()) > 0) or \
                       (ctx.LT() is not None and len(ctx.LT()) > 0) or \
                       (ctx.LE() is not None and len(ctx.LE()) > 0) or \
                       (ctx.GT() is not None and len(ctx.GT()) > 0) or \
                       (ctx.GE() is not None and len(ctx.GE()) > 0):
                        return True
                except:
                    pass
                
                try:
                    if hasattr(middle_child, 'symbol') and middle_child.symbol:
                        token_type = middle_child.symbol.type
                        if token_type in {langParser.LE, langParser.GE, langParser.EQ, langParser.NEQ, 
                                          langParser.LT, langParser.GT, langParser.AND, langParser.OR}:
                            return True
                except:
                    pass
                
                if self._has_comparison_in_expr(ctx.getChild(0)) or \
                   self._has_comparison_in_expr(ctx.getChild(2)):
                    return True
        
        if hasattr(ctx, "getChildren"):
            for child in ctx.getChildren():
                if self._has_comparison_in_expr(child):
                    return True
        
        return False

    def visitForStmt(self, ctx):
        self.push_scope()
        
        if ctx.forInit():
            for_init = ctx.forInit()
            declared_type = for_init.type_().getText() if for_init.type_() else None
            ids = for_init.ID()
            
            if len(ids) > 0:
                name = ids[0].getText()
                expr_type = None
                children = list(for_init.getChildren())
                for i in range(len(children)):
                    if i < len(children) - 2:
                        if hasattr(children[i], 'getText') and children[i].getText() == name:
                            if i + 1 < len(children) and hasattr(children[i+1], 'getText') and children[i+1].getText() == '=':
                                if i + 2 < len(children) and isinstance(children[i+2], langParser.ExprContext):
                                    expr_type = self.infer_type(children[i+2])
                                    break
                
                final_type = declared_type or expr_type or "unknown"
                if expr_type == "literal_set":
                    expr_type = "set"
                    final_type = declared_type or "set" or "unknown"
                if name not in self.current_scope():
                    self.current_scope()[name] = final_type
                if expr_type and declared_type and expr_type != declared_type:
                    self.add_error(
                        f"Невозможно присвоить значение типа '{expr_type}' переменной '{name}' типа '{declared_type}'",
                        ctx
                    )
        
        for_cond = ctx.forCond()
        cond_type = self.infer_type(for_cond) if for_cond else "bool"
        
        if cond_type != "bool" and for_cond:
            if self._has_comparison_in_expr(for_cond):
                cond_type = "bool"
            else:
                self.add_error("Условие в for должно быть типа boolean", ctx)
        elif cond_type != "bool" and not for_cond:
            pass

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

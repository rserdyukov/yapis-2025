from gen.langParser import langParser
from gen.langVisitor import langVisitor


class ILCodeGenerator(langVisitor):
    def __init__(self, semantic_analyzer):
        self.analyzer = semantic_analyzer
        self.code = []
        self.locals = {}
        self.local_index = 0
        self.label_counter = 0
        self.current_function = None
        self.current_function_locals = []
        self.function_signatures = {}
        self.temp_var_counter = 0
        self.expr_temp_vars = {}
        self._temp_var_types = {}
        self.global_vars = {}

    def get_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def _has_return_in_stmt(self, ctx):
        if ctx is None:
            return False
        from gen.langParser import langParser
        if isinstance(ctx, langParser.SimpleStmtContext):
            if ctx.getText().startswith("return"):
                return True
        if hasattr(ctx, "getChildren"):
            for child in ctx.getChildren():
                if self._has_return_in_stmt(child):
                    return True
        return False

    def _collect_locals_from_stmt(self, ctx):
        if ctx is None:
            return
        from gen.langParser import langParser

        if isinstance(ctx, langParser.VarDeclContext):
            declared_type = ctx.type_().getText() if ctx.type_() else None
            exprs = ctx.exprList().expr() if ctx.exprList() else []
            for i, id_token in enumerate(ctx.ID()):
                name = id_token.getText()
                var_type = declared_type or self.get_var_type(name) or "unknown"
                if i < len(exprs):
                    expr_type = self.analyzer.infer_type(exprs[i])
                    if expr_type == "literal_set":
                        expr_type = "set"
                    if not declared_type:
                        var_type = expr_type or "unknown"
                self.get_local_index(name, var_type)
        elif isinstance(ctx, langParser.AssignmentContext):
            if ctx.type_():
                declared_type = ctx.type_().getText()
                for id_token in ctx.ID():
                    name = id_token.getText()
                    self.get_local_index(name, declared_type)
            else:
                exprs = ctx.exprList().expr() if ctx.exprList() else []
                for i, id_token in enumerate(ctx.ID()):
                    name = id_token.getText()
                    var_type = self.get_var_type(name)
                    if var_type is None and i < len(exprs):
                        expr_type = self.analyzer.infer_type(exprs[i])
                        if expr_type == "literal_set":
                            expr_type = "set"
                        var_type = expr_type or "unknown"
                    if var_type:
                        self.get_local_index(name, var_type)
        elif isinstance(ctx, langParser.ForStmtContext):
            if ctx.forInit():
                for_init = ctx.forInit()
                declared_type = for_init.type_().getText() if for_init.type_() else None
                ids = for_init.ID()
                
                for i, id_token in enumerate(ids):
                    name = id_token.getText()
                    children = list(for_init.getChildren())
                    expr_idx = -1
                    for j, child in enumerate(children):
                        if hasattr(child, 'getText') and child.getText() == name:
                            if j + 1 < len(children) and hasattr(children[j+1], 'getText') and children[j+1].getText() == '=':
                                if j + 2 < len(children):
                                    expr_idx = j + 2
                                    break
                    
                    if expr_idx >= 0 and isinstance(children[expr_idx], langParser.ExprContext):
                        expr_type = self.analyzer.infer_type(children[expr_idx])
                        var_type = declared_type or expr_type or "int"
                    else:
                        var_type = declared_type or "int"
                    
                    self.get_local_index(name, var_type)

        if hasattr(ctx, "getChildren"):
            for child in ctx.getChildren():
                self._collect_locals_from_stmt(child)

    def _collect_temp_locals_from_stmt(self, ctx):
        if ctx is None:
            return
        from gen.langParser import langParser

        if isinstance(ctx, langParser.ExprContext) and ctx.getChildCount() == 3:
            op = ctx.getChild(1)
            left = ctx.getChild(0)
            right = ctx.getChild(2)

            self._collect_temp_locals_from_stmt(left)
            self._collect_temp_locals_from_stmt(right)
            
            left_type = self.analyzer.infer_type(left)
            right_type = self.analyzer.infer_type(right)

            real_left_type = left_type
            real_right_type = right_type

            if isinstance(right, langParser.IdWithIndexContext):
                var_name = right.ID().getText()
                var_type = self.get_var_type(var_name)
                if var_type:
                    if not right.indexSuffix():
                        real_right_type = var_type
            elif isinstance(right, langParser.FuncCallPrimaryContext):
                func_call = right.funcCall()
                if func_call:
                    func_name = func_call.ID().getText()
                    if func_name in self.function_signatures:
                        args = func_call.argList().expr() if func_call.argList() else []
                        for return_type, param_types, _ in self.function_signatures[func_name]:
                            if len(param_types) == len(args):
                                real_right_type = return_type
                                break
                    else:
                        from SemanticAnalyzer import SemanticAnalyzer
                        if func_name in SemanticAnalyzer.BUILTIN_FUNCTIONS:
                            return_type, _ = SemanticAnalyzer.BUILTIN_FUNCTIONS[func_name]
                            real_right_type = return_type
            elif isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                var_name = right.ID().getText()
                var_type = self.get_var_type(var_name)
                if var_type:
                    real_right_type = var_type

            if isinstance(left, langParser.IdWithIndexContext):
                var_name = left.ID().getText()
                var_type = self.get_var_type(var_name)
                if var_type:
                    if not left.indexSuffix():
                        real_left_type = var_type
            elif isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                var_name = left.ID().getText()
                var_type = self.get_var_type(var_name)
                if var_type:
                    real_left_type = var_type
            
            if (ctx.PLUS() or (hasattr(op, 'getText') and op.getText() == "+")):
                if real_left_type == "str" or real_right_type == "str" or real_left_type == "set" or real_right_type == "set":
                    expr_id = id(ctx)
                    if expr_id not in self.expr_temp_vars:
                        temp_name = f"__temp_concat_{self.temp_var_counter}"
                        self.temp_var_counter += 1
                        temp_type = "object"
                        if real_right_type == "set":
                            temp_type = "set"
                        elif real_right_type == "str":
                            temp_type = "str"
                        self.expr_temp_vars[expr_id] = temp_name
                        if not hasattr(self, '_temp_var_types'):
                            self._temp_var_types = {}
                        self._temp_var_types[temp_name] = real_right_type
                        self.get_local_index(temp_name, temp_type)

        if isinstance(ctx, langParser.FuncCallContext):
            args = ctx.argList().expr() if ctx.argList() else []
            for arg in args:
                self._collect_temp_locals_from_stmt(arg)

        if hasattr(ctx, "getChildren"):
            for child in ctx.getChildren():

                if not isinstance(child, langParser.ExprContext):
                    self._collect_temp_locals_from_stmt(child)

    def get_local_index(self, name, var_type):
        if name in self.locals:
            loc_info = self.locals[name]
            if isinstance(loc_info, tuple) and len(loc_info) == 2 and isinstance(loc_info[0], str) and loc_info[0].startswith("arg_"):
                return loc_info[0]
            return loc_info[0]

        idx = self.local_index
        self.local_index += 1
        il_type = self.type_to_il(var_type)
        self.locals[name] = (idx, il_type)
        self.current_function_locals.append((f"V_{idx}", il_type))
        return idx

    def emit_load_var(self, name, var_type):
        idx_or_arg = self.get_local_index(name, var_type)
        if isinstance(idx_or_arg, str) and idx_or_arg.startswith("arg_"):
            arg_num = int(idx_or_arg.split("_")[1])
            if arg_num <= 3:
                self.emit(f"    ldarg.{arg_num}")
            else:
                self.emit(f"    ldarg {arg_num}")
        else:
            if idx_or_arg <= 3:
                self.emit(f"    ldloc.{idx_or_arg}")
            else:
                self.emit(f"    ldloc V_{idx_or_arg}")

    def emit_store_var(self, name, var_type):
        if name not in self.locals:
            self.get_local_index(name, var_type)
        
        loc_info = self.locals[name]
        if isinstance(loc_info, tuple) and len(loc_info) == 2 and isinstance(loc_info[0], str) and loc_info[0].startswith("arg_"):
            pass
        
        if isinstance(loc_info, tuple) and len(loc_info) == 2:
            if isinstance(loc_info[0], str) and loc_info[0].startswith("arg_"):
                idx = 999
            else:
                idx = loc_info[0]
        else:
            idx = loc_info[0] if isinstance(loc_info, (int, tuple)) else 0
        
        if isinstance(idx, int) and idx <= 3:
            self.emit(f"    stloc.{idx}")
        else:
            if isinstance(idx, str) and idx.startswith("arg_"):
                raise ValueError(f"Cannot store to parameter {name}")
            self.emit(f"    stloc V_{idx}")

    def type_to_il(self, lang_type):
        if lang_type == "int":
            return "int32"
        elif lang_type == "float":
            return "float32"
        elif lang_type == "double":
            return "float64"
        elif lang_type == "bool":
            return "bool"
        elif lang_type == "str":
            return "string"
        elif lang_type == "set":
            return "class [mscorlib]System.Collections.Generic.List`1<object>"
        elif lang_type == "void":
            return "void"
        else:
            return "object"

    def get_var_type(self, name):
        for scope in reversed(self.analyzer.scopes):
            if name in scope:
                return scope[name]
        return None

    def emit(self, line):
        self.code.append(line)

    def emit_method_header(self, name, return_type, param_types, param_names, is_entrypoint=False):
        il_return_type = self.type_to_il(return_type)
        params = []
        for ptype, pname in zip(param_types, param_names):
            il_param_type = self.type_to_il(ptype)
            params.append(f"{il_param_type} {pname}")

        entrypoint = ".entrypoint" if is_entrypoint else ""
        if params:
            sig = f"  .method private static {il_return_type} {name}({', '.join(params)}) cil managed"
        else:
            sig = f"  .method private static {il_return_type} {name}() cil managed"
        
        self.emit(sig)
        self.emit("  {")
        if is_entrypoint:
            self.emit("    .entrypoint")
        if self.current_function_locals:
            local_decls = ", ".join([f"{t} {name}" for name, t in self.current_function_locals])
            self.emit(f"    .locals init ({local_decls})")
        else:
            self.emit("    .locals init ()")

    def emit_method_end(self):
        self.emit("  }")
        self.emit("")

    def visitStatement(self, ctx: langParser.StatementContext):
        if ctx.functionDef():
            return self.visit(ctx.functionDef())
        elif ctx.simpleStmt():
            return self.visit(ctx.simpleStmt())
        return self.visitChildren(ctx)

    def visitProgram(self, ctx: langParser.ProgramContext):
        self.emit(".assembly extern mscorlib {}")
        self.emit(".assembly Program {}")
        self.emit("")
        self.emit(".class private auto ansi beforefieldinit Program")
        self.emit("       extends [mscorlib]System.Object")
        self.emit("{")
        self.emit("")

        self.generate_set_to_string()
        self.generate_builtin_helpers()

        for stmt in ctx.statement():
            func_def = stmt.functionDef()
            if func_def:
                self.collect_function_signature(func_def)
            elif stmt.simpleStmt():
                simple = stmt.simpleStmt()
                if simple.varDecl():
                    var_decl = simple.varDecl()
                    declared_type = var_decl.type_().getText() if var_decl.type_() else None
                    exprs = var_decl.exprList().expr() if var_decl.exprList() else []
                    for i, id_token in enumerate(var_decl.ID()):
                        name = id_token.getText()
                        var_type = declared_type or "unknown"
                        if i < len(exprs):
                            expr_type = self.analyzer.infer_type(exprs[i])
                            if expr_type == "literal_set":
                                expr_type = "set"
                            if not declared_type:
                                var_type = expr_type or "unknown"
                        self.global_vars[name] = (var_type, var_decl)
                elif simple.assignment():
                    assign = simple.assignment()
                    if assign.type_():
                        declared_type = assign.type_().getText()
                        exprs = assign.exprList().expr() if assign.exprList() else []
                        for i, id_token in enumerate(assign.ID()):
                            name = id_token.getText()
                            var_type = declared_type or "unknown"
                            if i < len(exprs):
                                expr_type = self.analyzer.infer_type(exprs[i])
                                if expr_type == "literal_set":
                                    expr_type = "set"
                                if not declared_type:
                                    var_type = expr_type or "unknown"
                            if name not in self.global_vars:
                                self.global_vars[name] = (var_type, assign)
                    else:
                        exprs = assign.exprList().expr() if assign.exprList() else []
                        for i, id_token in enumerate(assign.ID()):
                            name = id_token.getText()
                            var_type = "unknown"
                            if i < len(exprs):
                                expr_type = self.analyzer.infer_type(exprs[i])
                                if expr_type == "literal_set":
                                    expr_type = "set"
                                var_type = expr_type or "unknown"
                            if name not in self.global_vars:
                                self.global_vars[name] = (var_type, assign)

        for stmt in ctx.statement():
            func_def = stmt.functionDef()
            if func_def:
                self.visitFunctionDef(func_def)
            elif stmt.simpleStmt():
                pass

        self.emit("}")
        return "\n".join(self.code)

    def collect_function_signature(self, ctx: langParser.FunctionDefContext):
        func_name = ctx.ID().getText()
        return_type = ctx.type_().getText() if ctx.type_() else "void"
        param_types = []
        param_names = []

        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                param_types.append(p.type_().getText())
                param_names.append(p.ID().getText())

        if func_name not in self.function_signatures:
            self.function_signatures[func_name] = []
        self.function_signatures[func_name].append((return_type, param_types, param_names))

    def visitFunctionDef(self, ctx: langParser.FunctionDefContext):
        func_name = ctx.ID().getText()
        return_type = ctx.type_().getText() if ctx.type_() else "void"
        param_types = []
        param_names = []

        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                param_types.append(p.type_().getText())
                param_names.append(p.ID().getText())

        old_locals = self.locals.copy()
        old_index = self.local_index
        old_temp_counter = self.temp_var_counter
        old_expr_temp_vars = self.expr_temp_vars.copy()
        old_temp_var_types = self._temp_var_types.copy()
        self.locals = {}
        self.local_index = 0
        self.current_function_locals = []
        self.current_function = (func_name, return_type)
        self.temp_var_counter = 0
        self.expr_temp_vars = {}
        self._temp_var_types = {}

        for i, (ptype, pname) in enumerate(zip(param_types, param_names)):
            self.locals[pname] = (f"arg_{i}", ptype)
        self.local_index = 0

        is_entrypoint = (func_name == "main" and return_type == "void")
        method_name = "Main" if is_entrypoint else func_name
        
        if is_entrypoint:
            self.function_signatures["Main"] = self.function_signatures.get(func_name, [])
            if "Main" not in self.function_signatures or not self.function_signatures["Main"]:
                self.function_signatures["Main"] = [(return_type, param_types, param_names)]

        has_return = False
        if ctx.statement():
            for stmt in ctx.statement():
                if self._has_return_in_stmt(stmt):
                    has_return = True
                self._collect_locals_from_stmt(stmt)
                self._collect_temp_locals_from_stmt(stmt)
        
        if is_entrypoint:
            for gvar_name, (gvar_type, _) in self.global_vars.items():
                if gvar_name not in self.locals:
                    self.get_local_index(gvar_name, gvar_type)
        
        self.emit_method_header(method_name, return_type, param_types, param_names, is_entrypoint)
        
        if is_entrypoint:
            for gvar_name, (gvar_type, gvar_ctx) in self.global_vars.items():
                from gen.langParser import langParser
                if isinstance(gvar_ctx, langParser.VarDeclContext):
                    declared_type = gvar_ctx.type_().getText() if gvar_ctx.type_() else None
                    exprs = gvar_ctx.exprList().expr() if gvar_ctx.exprList() else []
                    for i, id_token in enumerate(gvar_ctx.ID()):
                        if id_token.getText() == gvar_name:
                            if i < len(exprs):
                                self.visit(exprs[i])
                                expr_type = self.analyzer.infer_type(exprs[i])
                                if expr_type == "literal_set":
                                    expr_type = "set"
                                self.convert_type(expr_type, gvar_type)
                            else:
                                if gvar_type == "int":
                                    self.emit("    ldc.i4.0")
                                elif gvar_type == "bool":
                                    self.emit("    ldc.i4.0")
                                elif gvar_type == "str":
                                    self.emit("    ldstr \"\"")
                                elif gvar_type == "set":
                                    self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
                                else:
                                    self.emit("    ldnull")
                            self.emit_store_var(gvar_name, gvar_type)
                            break
                elif isinstance(gvar_ctx, langParser.AssignmentContext):
                    if gvar_ctx.type_():
                        declared_type = gvar_ctx.type_().getText()
                        exprs = gvar_ctx.exprList().expr() if gvar_ctx.exprList() else []
                        for i, id_token in enumerate(gvar_ctx.ID()):
                            if id_token.getText() == gvar_name:
                                if i < len(exprs):
                                    self.visit(exprs[i])
                                    expr_type = self.analyzer.infer_type(exprs[i])
                                    if expr_type == "literal_set":
                                        expr_type = "set"
                                    self.convert_type(expr_type, gvar_type)
                                else:
                                    if gvar_type == "int":
                                        self.emit("    ldc.i4.0")
                                    elif gvar_type == "bool":
                                        self.emit("    ldc.i4.0")
                                    elif gvar_type == "str":
                                        self.emit("    ldstr \"\"")
                                    elif gvar_type == "set":
                                        self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
                                    else:
                                        self.emit("    ldnull")
                                self.emit_store_var(gvar_name, gvar_type)
                                break
                    else:
                        exprs = gvar_ctx.exprList().expr() if gvar_ctx.exprList() else []
                        for i, id_token in enumerate(gvar_ctx.ID()):
                            if id_token.getText() == gvar_name:
                                if i < len(exprs):
                                    self.visit(exprs[i])
                                    expr_type = self.analyzer.infer_type(exprs[i])
                                    if expr_type == "literal_set":
                                        expr_type = "set"
                                    self.convert_type(expr_type, gvar_type)
                                else:
                                    if gvar_type == "int":
                                        self.emit("    ldc.i4.0")
                                    elif gvar_type == "bool":
                                        self.emit("    ldc.i4.0")
                                    elif gvar_type == "str":
                                        self.emit("    ldstr \"\"")
                                    elif gvar_type == "set":
                                        self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
                                    else:
                                        self.emit("    ldnull")
                                self.emit_store_var(gvar_name, gvar_type)
                                break
        
        if ctx.statement():
            for stmt in ctx.statement():
                self.visit(stmt)

        if return_type != "void" and not has_return:
            if return_type == "int":
                self.emit("    ldc.i4.0")
                self.emit("    ret")
            elif return_type == "bool":
                self.emit("    ldc.i4.0")
                self.emit("    ret")
            elif return_type == "str":
                self.emit("    ldstr \"\"")
                self.emit("    ret")
            elif return_type == "set":
                self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
                self.emit("    ret")
            else:
                self.emit("    ldnull")
                self.emit("    ret")
        elif return_type == "void" or has_return:
            if not has_return:
                self.emit("    ret")

        self.emit_method_end()

        self.locals = old_locals
        self.local_index = old_index
        self.temp_var_counter = old_temp_counter
        self.expr_temp_vars = old_expr_temp_vars
        self._temp_var_types = old_temp_var_types
        self.current_function = None
        self.current_function_locals = []

    def visitVarDecl(self, ctx: langParser.VarDeclContext):
        declared_type = ctx.type_().getText() if ctx.type_() else None
        exprs = ctx.exprList().expr() if ctx.exprList() else []

        for i, id_token in enumerate(ctx.ID()):
            name = id_token.getText()
            var_type = declared_type or self.get_var_type(name) or "unknown"
            
            if i < len(exprs):
                expr_type = self.analyzer.infer_type(exprs[i])
                if expr_type == "literal_set":
                    expr_type = "set"
                if not declared_type:
                    var_type = expr_type or "unknown"

            if i < len(exprs):
                self.visit(exprs[i])
                self.convert_type(self.analyzer.infer_type(exprs[i]), var_type)
            else:
                if var_type == "int":
                    self.emit("    ldc.i4.0")
                elif var_type == "bool":
                    self.emit("    ldc.i4.0")
                elif var_type == "str":
                    self.emit("    ldstr \"\"")
                elif var_type == "set":
                    self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
                elif var_type == "float" or var_type == "double":
                    self.emit("    ldc.r8 0.0")
                else:
                    self.emit("    ldnull")

            self.get_local_index(name, var_type)
            self.emit_store_var(name, var_type)

    def visitAssignment(self, ctx: langParser.AssignmentContext):
        if ctx.type_():
            declared_type = ctx.type_().getText()
            exprs = ctx.exprList().expr() if ctx.exprList() else []
            
            for i, id_token in enumerate(ctx.ID()):
                name = id_token.getText()
                
                if i < len(exprs):
                    self.visit(exprs[i])
                    expr_type = self.analyzer.infer_type(exprs[i])
                    self.convert_type(expr_type, declared_type)
                else:
                    if declared_type == "int":
                        self.emit("    ldc.i4.0")
                    elif declared_type == "bool":
                        self.emit("    ldc.i4.0")
                    elif declared_type == "str":
                        self.emit("    ldstr \"\"")
                    elif declared_type == "set":
                        self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
                    else:
                        self.emit("    ldnull")

                self.get_local_index(name, declared_type)
                self.emit_store_var(name, declared_type)
        else:
            exprs = ctx.exprList().expr() if ctx.exprList() else []
            
            has_assign_op = ctx.PLUS_ASSIGN() or ctx.MINUS_ASSIGN() or ctx.MUL_ASSIGN() or ctx.DIV_ASSIGN()
            has_inc_dec = ctx.INC() or ctx.DEC()
            
            for i, id_token in enumerate(ctx.ID()):
                name = id_token.getText()
                var_type = self.get_var_type(name)
                
                if has_inc_dec:
                    self.emit_load_var(name, var_type)
                    if ctx.INC():
                        self.emit("    ldc.i4.1")
                        self.emit("    add")
                    elif ctx.DEC():
                        self.emit("    ldc.i4.1")
                        self.emit("    sub")
                    self.emit_store_var(name, var_type)
                elif has_assign_op:
                    self.emit_load_var(name, var_type)
                    
                    if ctx.expr():
                        self.visit(ctx.expr())
                        expr_type = self.analyzer.infer_type(ctx.expr())
                        
                        if ctx.PLUS_ASSIGN():
                            if var_type == "str":
                                self.emit("    call string [mscorlib]System.String::Concat(object, object)")
                            else:
                                self.emit("    add")
                        elif ctx.MINUS_ASSIGN():
                            self.emit("    sub")
                        elif ctx.MUL_ASSIGN():
                            self.emit("    mul")
                        elif ctx.DIV_ASSIGN():
                            self.emit("    div")
                    
                    self.emit_store_var(name, var_type)
                else:
                    if i < len(exprs):
                        expr_type = self.analyzer.infer_type(exprs[i])
                        
                        if var_type is None:
                            if expr_type == "literal_set":
                                expr_type = "set"
                            if expr_type and expr_type != "unknown":
                                var_type = expr_type
                            else:
                                var_type = "unknown"
                        
                        if expr_type and expr_type != "unknown" and var_type == "unknown":
                            var_type = expr_type
                        elif expr_type == "int" and var_type == "unknown":
                            var_type = "int"
                        elif expr_type == "str" and var_type == "unknown":
                            var_type = "str"
                        
                        self.visit(exprs[i])
                        self.convert_type(expr_type, var_type)
                    else:
                        if var_type == "int":
                            self.emit("    ldc.i4.0")
                        elif var_type == "bool":
                            self.emit("    ldc.i4.0")
                        elif var_type == "str":
                            self.emit("    ldstr \"\"")
                        elif var_type == "set":
                            self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
                        else:
                            self.emit("    ldnull")

                    self.get_local_index(name, var_type)
                    self.emit_store_var(name, var_type)

    def convert_type(self, from_type, to_type):
        if from_type == to_type:
            return
        
        if to_type == "set" and from_type != "set":
            il_type = self.type_to_il(from_type)
            if il_type != "object":
                if il_type == "int32":
                    self.emit("    box [mscorlib]System.Int32")
                elif il_type == "bool":
                    self.emit("    box [mscorlib]System.Boolean")
                elif il_type == "string":
                    pass
                else:
                    self.emit(f"    box [{il_type}]")
        
        elif from_type != to_type:
            if from_type == "unknown" and to_type == "int":
                pass
            elif to_type == "int" and (from_type not in ["int", "float", "double", "bool", "str", "set"]):
                if from_type != "int":
                    pass
            elif to_type == "str" and from_type == "set":
                pass
            elif to_type == "int" and from_type == "str":
                pass

    def visitFuncCall(self, ctx: langParser.FuncCallContext):
        func_name = ctx.ID().getText()
        args = ctx.argList().expr() if ctx.argList() else []

        if func_name == "read":
            self.emit("    call string [mscorlib]System.Console::ReadLine()")
        elif func_name == "println":
            if args:
                arg_type = self.analyzer.infer_type(args[0])
                
                is_set_arg = False
                from gen.langParser import langParser
                arg_expr = args[0]
                
                if arg_type == "set" or arg_type == "literal_set":
                    is_set_arg = True
                else:
                    var_name_to_check = None
                    if isinstance(arg_expr, langParser.IdWithIndexContext):
                        var_name_to_check = arg_expr.ID().getText()
                    elif isinstance(arg_expr, langParser.PrimaryContext):
                        if hasattr(arg_expr, "ID") and arg_expr.ID():
                            var_name_to_check = arg_expr.ID().getText()
                        if not var_name_to_check and hasattr(arg_expr, "idWithIndex"):
                            id_with_index = arg_expr.idWithIndex()
                            if id_with_index:
                                var_name_to_check = id_with_index.ID().getText() if id_with_index.ID() else None
                    
                    if var_name_to_check and var_name_to_check in self.locals:
                        _, il_type = self.locals[var_name_to_check]
                        il_type_str = str(il_type)
                        if "List`1<object>" in il_type_str:
                            is_set_arg = True
                    
                    if not is_set_arg and var_name_to_check:
                        var_type = self.get_var_type(var_name_to_check)
                        if var_type == "set":
                            is_set_arg = True
                    
                    if not is_set_arg and isinstance(arg_expr, langParser.FuncCallPrimaryContext):
                        func_call = arg_expr.funcCall()
                        if func_call:
                            call_func_name = func_call.ID().getText()
                            from SemanticAnalyzer import SemanticAnalyzer
                            if call_func_name in SemanticAnalyzer.BUILTIN_FUNCTIONS:
                                return_type, _ = SemanticAnalyzer.BUILTIN_FUNCTIONS[call_func_name]
                                if return_type == "set":
                                    is_set_arg = True
                            elif call_func_name in self.function_signatures:
                                call_args = func_call.argList().expr() if func_call.argList() else []
                                for return_type, param_types, _ in self.function_signatures[call_func_name]:
                                    if len(param_types) == len(call_args) and return_type == "set":
                                        is_set_arg = True
                                        break
                    
                    if not is_set_arg:
                        expr_text = arg_expr.getText().strip() if hasattr(arg_expr, 'getText') else None
                        if expr_text:
                            if expr_text in self.locals:
                                _, il_type = self.locals[expr_text]
                                il_type_str = str(il_type)
                                if "List`1<object>" in il_type_str:
                                    is_set_arg = True
                
                self.visit(args[0])
                
                if not is_set_arg:
                    var_name_after_visit = None
                    if isinstance(arg_expr, langParser.IdWithIndexContext):
                        var_name_after_visit = arg_expr.ID().getText()
                    elif isinstance(arg_expr, langParser.PrimaryContext):
                        if hasattr(arg_expr, "ID") and arg_expr.ID():
                            var_name_after_visit = arg_expr.ID().getText()
                        elif hasattr(arg_expr, "idWithIndex"):
                            id_with_index = arg_expr.idWithIndex()
                            if id_with_index and id_with_index.ID():
                                var_name_after_visit = id_with_index.ID().getText()
                    
                    if var_name_after_visit and var_name_after_visit in self.locals:
                        _, il_type_after = self.locals[var_name_after_visit]
                        il_type_str_after = str(il_type_after)
                        if "List`1<object>" in il_type_str_after:
                            is_set_arg = True
                    
                    if not is_set_arg and hasattr(arg_expr, 'getText'):
                        expr_text = arg_expr.getText().strip()
                        for local_name in self.locals.keys():
                            if local_name == expr_text:
                                _, il_type_final = self.locals[local_name]
                                il_type_str_final = str(il_type_final)
                                if "List`1<object>" in il_type_str_final:
                                    is_set_arg = True
                                    break
                
                if is_set_arg:
                    self.emit("    call string Program::SetToString(class [mscorlib]System.Collections.Generic.List`1<object>)")
                elif arg_type != "str":
                    if arg_type in ["int", "bool", "float", "double"]:
                        if arg_type == "int":
                            self.emit("    box [mscorlib]System.Int32")
                        elif arg_type == "bool":
                            self.emit("    box [mscorlib]System.Boolean")
                        self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
                    elif arg_type == "unknown":
                        from gen.langParser import langParser
                        arg_expr = args[0]
                        var_name_to_check = None
                        
                        if isinstance(arg_expr, langParser.IdWithIndexContext):
                            var_name_to_check = arg_expr.ID().getText()
                        elif isinstance(arg_expr, langParser.PrimaryContext):
                            if hasattr(arg_expr, "ID") and arg_expr.ID():
                                var_name_to_check = arg_expr.ID().getText()
                            elif hasattr(arg_expr, "idWithIndex"):
                                id_with_index = arg_expr.idWithIndex()
                                if id_with_index and id_with_index.ID():
                                    var_name_to_check = id_with_index.ID().getText()
                        
                        if not var_name_to_check and hasattr(arg_expr, 'getText'):
                            expr_text = arg_expr.getText().strip()
                            if expr_text in self.locals:
                                var_name_to_check = expr_text
                        
                        handled = False
                        if var_name_to_check and var_name_to_check in self.locals:
                            _, il_type = self.locals[var_name_to_check]
                            il_type_str = str(il_type)
                            if "List`1<object>" in il_type_str:
                                handled = True
                                self.emit("    call string Program::SetToString(class [mscorlib]System.Collections.Generic.List`1<object>)")
                            elif il_type_str == "string":
                                handled = True
                                self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
                        
                        if not handled:
                            if var_name_to_check and var_name_to_check in self.locals:
                                _, il_type = self.locals[var_name_to_check]
                                il_type_str = str(il_type)
                                if il_type_str == "int32":
                                    self.emit("    box [mscorlib]System.Int32")
                                    self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
                                else:
                                    self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
                            else:
                                self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
            self.emit("    call void [mscorlib]System.Console::WriteLine(string)")
        elif func_name == "toInt":
            if len(args) >= 1:
                self.visit(args[0])
            self.emit("    call int32 [mscorlib]System.Int32::Parse(string)")
        elif func_name == "split":
            if len(args) >= 2:
                self.visit(args[0])
                self.visit(args[1])
                
                self.emit("    call class [mscorlib]System.Collections.Generic.List`1<object> Program::Split(string, string)")
            else:
                pass
        elif func_name == "size":
            if len(args) >= 1:
                arg_type = self.analyzer.infer_type(args[0]) if args else "unknown"
                from gen.langParser import langParser
                arg_expr = args[0] if args else None
                is_string = False
                
                var_name_check = None
                if isinstance(arg_expr, langParser.IdWithIndexContext):
                    var_name_check = arg_expr.ID().getText()
                elif isinstance(arg_expr, langParser.PrimaryContext):
                    if hasattr(arg_expr, "ID") and arg_expr.ID():
                        var_name_check = arg_expr.ID().getText()
                    elif hasattr(arg_expr, "idWithIndex"):
                        id_with_index = arg_expr.idWithIndex()
                        if id_with_index and id_with_index.ID():
                            var_name_check = id_with_index.ID().getText()
                
                if var_name_check:
                    if var_name_check in self.locals:
                        _, il_type = self.locals[var_name_check]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    
                    if not is_string:
                        var_type = self.get_var_type(var_name_check)
                        if var_type == "str":
                            is_string = True
                
                if not is_string and arg_type == "str":
                    is_string = True
                
                if not is_string:
                    if isinstance(arg_expr, langParser.FuncCallPrimaryContext):
                        func_call = arg_expr.funcCall()
                        if func_call:
                            call_func_name = func_call.ID().getText()
                            if call_func_name == "open":
                                is_string = True
                
                if not is_string and hasattr(arg_expr, 'getText'):
                    expr_text = arg_expr.getText().strip()
                    expr_text_clean = expr_text.replace(' ', '').replace('\t', '').replace('\n', '')
                    if expr_text in self.locals:
                        _, il_type = self.locals[expr_text]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    elif expr_text_clean in self.locals:
                        _, il_type = self.locals[expr_text_clean]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    else:
                        for local_name in self.locals.keys():
                            if local_name == expr_text or local_name == expr_text_clean:
                                _, il_type = self.locals[local_name]
                                il_type_str = str(il_type)
                                if il_type_str == "string":
                                    is_string = True
                                    break
                
                self.visit(args[0])
                
                if not is_string and hasattr(arg_expr, 'getText'):
                    expr_text = arg_expr.getText().strip()
                    expr_text_clean = expr_text.replace(' ', '').replace('\t', '').replace('\n', '')
                    if expr_text in self.locals:
                        _, il_type = self.locals[expr_text]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    elif expr_text_clean in self.locals:
                        _, il_type = self.locals[expr_text_clean]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    else:
                        for local_name in self.locals.keys():
                            if local_name == expr_text or local_name == expr_text_clean:
                                _, il_type = self.locals[local_name]
                                il_type_str = str(il_type)
                                if il_type_str == "string":
                                    is_string = True
                                    break
            
            if len(args) >= 1:
                if is_string:
                    self.emit("    callvirt instance int32 [mscorlib]System.String::get_Length()")
                else:
                    self.emit("    callvirt instance int32 class [mscorlib]System.Collections.Generic.List`1<object>::get_Count()")
        elif func_name == "isEmpty":
            if len(args) >= 1:
                self.visit(args[0])
            self.emit("    callvirt instance int32 class [mscorlib]System.Collections.Generic.List`1<object>::get_Count()")
            self.emit("    ldc.i4.0")
            self.emit("    ceq")
        elif func_name == "add":
            if len(args) >= 2:
                self.visit(args[0])
                self.visit(args[1])
                value_type = self.analyzer.infer_type(args[1])
                if value_type == "int":
                    self.emit("    box [mscorlib]System.Int32")
                elif value_type == "bool":
                    self.emit("    box [mscorlib]System.Boolean")
                self.emit("    callvirt instance void class [mscorlib]System.Collections.Generic.List`1<object>::Add(!0)")
        elif func_name == "remove":
            if len(args) >= 2:
                self.visit(args[0])
                self.visit(args[1])
                self.emit("    callvirt instance void class [mscorlib]System.Collections.Generic.List`1<object>::RemoveAt(int32)")
        elif func_name == "get":
            if len(args) >= 2:
                arg_type = self.analyzer.infer_type(args[0]) if args else "unknown"
                from gen.langParser import langParser
                arg_expr = args[0] if args else None
                is_string = False
                
                var_name_check = None
                if isinstance(arg_expr, langParser.IdWithIndexContext):
                    var_name_check = arg_expr.ID().getText()
                elif isinstance(arg_expr, langParser.PrimaryContext):
                    if hasattr(arg_expr, "ID") and arg_expr.ID():
                        var_name_check = arg_expr.ID().getText()
                    elif hasattr(arg_expr, "idWithIndex"):
                        id_with_index = arg_expr.idWithIndex()
                        if id_with_index and id_with_index.ID():
                            var_name_check = id_with_index.ID().getText()
                
                if var_name_check:
                    if var_name_check in self.locals:
                        _, il_type = self.locals[var_name_check]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    
                    if not is_string:
                        var_type = self.get_var_type(var_name_check)
                        if var_type == "str":
                            is_string = True
                
                if not is_string and arg_type == "str":
                    is_string = True
                
                if not is_string:
                    if isinstance(arg_expr, langParser.FuncCallPrimaryContext):
                        func_call = arg_expr.funcCall()
                        if func_call:
                            call_func_name = func_call.ID().getText()
                            if call_func_name == "open":
                                is_string = True
                
                if not is_string and hasattr(arg_expr, 'getText'):
                    expr_text = arg_expr.getText().strip()
                    expr_text_clean = expr_text.replace(' ', '').replace('\t', '').replace('\n', '')
                    if expr_text in self.locals:
                        _, il_type = self.locals[expr_text]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    elif expr_text_clean in self.locals:
                        _, il_type = self.locals[expr_text_clean]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    else:
                        for local_name in self.locals.keys():
                            if local_name == expr_text or local_name == expr_text_clean:
                                _, il_type = self.locals[local_name]
                                il_type_str = str(il_type)
                                if il_type_str == "string":
                                    is_string = True
                                    break
                
                self.visit(args[0])
                self.visit(args[1])
                
                if not is_string and hasattr(arg_expr, 'getText'):
                    expr_text = arg_expr.getText().strip()
                    expr_text_clean = expr_text.replace(' ', '').replace('\t', '').replace('\n', '')
                    if expr_text in self.locals:
                        _, il_type = self.locals[expr_text]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    elif expr_text_clean in self.locals:
                        _, il_type = self.locals[expr_text_clean]
                        il_type_str = str(il_type)
                        if il_type_str == "string":
                            is_string = True
                    else:
                        for local_name in self.locals.keys():
                            if local_name == expr_text or local_name == expr_text_clean:
                                _, il_type = self.locals[local_name]
                                il_type_str = str(il_type)
                                if il_type_str == "string":
                                    is_string = True
                                    break
                
                if is_string:
                    self.emit("    callvirt instance char [mscorlib]System.String::get_Chars(int32)")
                    self.emit("    box [mscorlib]System.Char")
                    self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
                else:
                    self.emit("    callvirt instance !0 class [mscorlib]System.Collections.Generic.List`1<object>::get_Item(int32)")
        elif func_name == "open":
            if len(args) >= 1:
                self.visit(args[0])
            self.emit("    call string [mscorlib]System.IO.File::ReadAllText(string)")
        elif func_name == "getFileNames":
            if len(args) >= 1:
                self.visit(args[0])
            self.emit("    call class [mscorlib]System.Collections.Generic.List`1<object> Program::GetFileNames(string)")
        elif func_name in self.function_signatures:
            arg_count = len(args)
            for return_type, param_types, param_names in self.function_signatures[func_name]:
                if len(param_types) == arg_count:
                    for i, arg in enumerate(args):
                        self.visit(arg)
                        arg_type = self.analyzer.infer_type(arg)
                        param_type = param_types[i]
                        
                        from gen.langParser import langParser
                        var_name_to_check = None
                        if isinstance(arg, langParser.IdWithIndexContext) and not arg.indexSuffix():
                            var_name_to_check = arg.ID().getText()
                        elif isinstance(arg, langParser.PrimaryContext) and hasattr(arg, "ID") and arg.ID():
                            var_name_to_check = arg.ID().getText()
                        
                        if var_name_to_check and var_name_to_check in self.locals:
                            _, il_type = self.locals[var_name_to_check]
                            if str(il_type) == "int32" and param_type == "int" and arg_type == "unknown":
                                pass
                            else:
                                self.convert_type(arg_type, param_type)
                        else:
                            self.convert_type(arg_type, param_type)
                    
                    il_return_type = self.type_to_il(return_type)
                    params = []
                    for ptype in param_types:
                        il_param_type = self.type_to_il(ptype)
                        params.append(il_param_type)
                    
                    call_name = "Main" if func_name == "main" else func_name
                    if params:
                        sig = f"    call {il_return_type} Program::{call_name}({', '.join(params)})"
                    else:
                        sig = f"    call {il_return_type} Program::{call_name}()"
                    self.emit(sig)
                    break
        else:
            self.emit(f"    // Unknown function: {func_name}")

    def visitExpr(self, ctx: langParser.ExprContext):
        if ctx.getChildCount() == 1:
            return self.visitChildren(ctx)
        
        if ctx.getChildCount() == 3:
            left = ctx.getChild(0)
            op = ctx.getChild(1)
            right = ctx.getChild(2)
            
            from gen.langParser import langParser
            is_mod = ctx.MOD() or (hasattr(op, 'getText') and op.getText() == "%")
            is_mul = ctx.MUL() or (hasattr(op, 'getText') and op.getText() == "*")
            is_right_comparison = isinstance(right, langParser.ExprContext) and right.getChildCount() == 3 and \
                                 (right.EQ() or right.NEQ() or right.LT() or right.LE() or right.GT() or right.GE())
            
            if (is_mod or is_mul) and is_right_comparison:
                right_left = right.getChild(0)
                right_op = right.getChild(1)
                right_right = right.getChild(2)
                
                self.visit(left)
                left_type = self.analyzer.infer_type(left)
                
                self.visit(right_left)
                right_left_type = self.analyzer.infer_type(right_left)
                
                if is_mod:
                    if left_type != "int" and left_type not in ["float", "double"]:
                        if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                            left_var_name = left.ID().getText()
                            left_var_type = self.get_var_type(left_var_name)
                            if left_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    if right_left_type != "int" and right_left_type not in ["float", "double"]:
                        if isinstance(right_left, langParser.PrimaryContext) and hasattr(right_left, "ID") and right_left.ID():
                            right_left_var_name = right_left.ID().getText()
                            right_left_var_type = self.get_var_type(right_left_var_name)
                            if right_left_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    self.emit("    rem")
                elif is_mul:
                    if left_type != "int" and left_type not in ["float", "double"]:
                        if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                            left_var_name = left.ID().getText()
                            left_var_type = self.get_var_type(left_var_name)
                            if left_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    if right_left_type != "int" and right_left_type not in ["float", "double"]:
                        if isinstance(right_left, langParser.PrimaryContext) and hasattr(right_left, "ID") and right_left.ID():
                            right_left_var_name = right_left.ID().getText()
                            right_left_var_type = self.get_var_type(right_left_var_name)
                            if right_left_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    self.emit("    mul")
                
                self.visit(right_right)
                right_right_type = self.analyzer.infer_type(right_right)
                
                comparison_op = None
                if right.EQ():
                    comparison_op = "=="
                elif right.NEQ():
                    comparison_op = "!="
                elif right.LT():
                    comparison_op = "<"
                elif right.LE():
                    comparison_op = "<="
                elif right.GT():
                    comparison_op = ">"
                elif right.GE():
                    comparison_op = ">="
                else:
                    if hasattr(right_op, 'getText'):
                        op_text = right_op.getText().strip()
                        if op_text == "==":
                            comparison_op = "=="
                        elif op_text == "!=":
                            comparison_op = "!="
                        elif op_text == "<":
                            comparison_op = "<"
                        elif op_text == "<=":
                            comparison_op = "<="
                        elif op_text == ">":
                            comparison_op = ">"
                        elif op_text == ">=":
                            comparison_op = ">="
                
                if right_right_type != "int" and right_right_type not in ["float", "double"]:
                    if isinstance(right_right, langParser.PrimaryContext) and hasattr(right_right, "ID") and right_right.ID():
                        right_right_var_name = right_right.ID().getText()
                        right_right_var_type = self.get_var_type(right_right_var_name)
                        if right_right_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                            self.emit("    unbox.any [mscorlib]System.Int32")
                    if isinstance(right_right, langParser.PrimaryContext) and hasattr(right_right, "ID") and right_right.ID():
                        right_right_var_name = right_right.ID().getText()
                        if right_right_var_name in self.locals:
                            _, right_right_il_type = self.locals[right_right_var_name]
                            if str(right_right_il_type) == "int32":
                                pass
                            elif str(right_right_il_type) != "int32":
                                if right_right_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                    self.emit("    unbox.any [mscorlib]System.Int32")
                
                left_comp_type = self.analyzer.infer_type(right_left)
                right_comp_type = self.analyzer.infer_type(right_right)
                
                is_left_comp_string = (left_comp_type == "str")
                is_right_comp_string = (right_comp_type == "str")
                
                if isinstance(right_left, langParser.PrimaryContext) and hasattr(right_left, "ID") and right_left.ID():
                    left_comp_var_name = right_left.ID().getText()
                    if left_comp_var_name in self.locals:
                        loc_info = self.locals[left_comp_var_name]
                        if isinstance(loc_info, tuple) and len(loc_info) == 2:
                            first_elem, second_elem = loc_info
                            if isinstance(first_elem, str) and first_elem.startswith("arg_"):
                                if second_elem == "str":
                                    is_left_comp_string = True
                            elif str(second_elem) == "string":
                                is_left_comp_string = True
                
                if isinstance(right_right, langParser.PrimaryContext) and hasattr(right_right, "ID") and right_right.ID():
                    right_comp_var_name = right_right.ID().getText()
                    if right_comp_var_name in self.locals:
                        loc_info = self.locals[right_comp_var_name]
                        if isinstance(loc_info, tuple) and len(loc_info) == 2:
                            first_elem, second_elem = loc_info
                            if isinstance(first_elem, str) and first_elem.startswith("arg_"):
                                if second_elem == "str":
                                    is_right_comp_string = True
                            elif str(second_elem) == "string":
                                is_right_comp_string = True
                
                if comparison_op == "==":
                    if is_left_comp_string and is_right_comp_string:
                        self.emit("    callvirt instance bool [mscorlib]System.String::Equals(string)")
                    else:
                        self.emit("    ceq")
                elif comparison_op == "!=":
                    if is_left_comp_string and is_right_comp_string:
                        self.emit("    callvirt instance bool [mscorlib]System.String::Equals(string)")
                        self.emit("    ldc.i4.0")
                        self.emit("    ceq")
                    else:
                        self.emit("    ceq")
                        self.emit("    ldc.i4.0")
                        self.emit("    ceq")
                elif comparison_op == "<":
                    self.emit("    clt")
                elif comparison_op == "<=":
                    self.emit("    cgt")
                    self.emit("    ldc.i4.0")
                    self.emit("    ceq")
                elif comparison_op == ">":
                    self.emit("    cgt")
                elif comparison_op == ">=":
                    self.emit("    clt")
                    self.emit("    ldc.i4.0")
                    self.emit("    ceq")
                else:
                    self.emit("    ceq")
                
                return
            
            left_var_name_for_pre_check = None
            right_var_name_for_pre_check = None
            from gen.langParser import langParser
            
            if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                left_var_name_for_pre_check = left.ID().getText()
            elif isinstance(left, langParser.IdWithIndexContext) and not left.indexSuffix():
                left_var_name_for_pre_check = left.ID().getText()
            
            if isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                right_var_name_for_pre_check = right.ID().getText()
            elif isinstance(right, langParser.IdWithIndexContext) and not right.indexSuffix():
                right_var_name_for_pre_check = right.ID().getText()
            
            self.visit(left)
            left_type = self.analyzer.infer_type(left)
            
            self.visit(right)
            right_type = self.analyzer.infer_type(right)
            
            if ctx.OR() or op.getText() == "||":
                self.emit("    or")
            elif ctx.AND() or op.getText() == "&&":
                self.emit("    and")
            elif ctx.EQ() or op.getText() == "==":
                from gen.langParser import langParser
                is_left_arithmetic = isinstance(left, langParser.ExprContext) and left.getChildCount() == 3 and \
                                    (left.MUL() or left.DIV() or left.MOD() or left.PLUS() or left.MINUS())
                is_right_arithmetic = isinstance(right, langParser.ExprContext) and right.getChildCount() == 3 and \
                                     (right.MUL() or right.DIV() or right.MOD() or right.PLUS() or right.MINUS())
                
                if is_left_arithmetic:
                    left_type = "int"
                
                if is_right_arithmetic:
                    right_type = "int"
                
                
                left_var_name = left_var_name_for_pre_check
                if not left_var_name:
                    if isinstance(left, langParser.PrimaryContext):
                        if hasattr(left, "ID") and left.ID():
                            left_var_name = left.ID().getText()
                        elif hasattr(left, "idWithIndex") and left.idWithIndex():
                            left_var_name = left.idWithIndex().ID().getText() if left.idWithIndex().ID() else None
                    elif isinstance(left, langParser.IdWithIndexContext):
                        if not left.indexSuffix() or len(left.indexSuffix()) == 0:
                            left_var_name = left.ID().getText()
                
                right_var_name = right_var_name_for_pre_check
                if not right_var_name:
                    if isinstance(right, langParser.PrimaryContext):
                        if hasattr(right, "ID") and right.ID():
                            right_var_name = right.ID().getText()
                        elif hasattr(right, "idWithIndex") and right.idWithIndex():
                            right_var_name = right.idWithIndex().ID().getText() if right.idWithIndex().ID() else None
                    elif isinstance(right, langParser.IdWithIndexContext):
                        if not right.indexSuffix() or len(right.indexSuffix()) == 0:
                            right_var_name = right.ID().getText()
                
                if not left_var_name and hasattr(left, 'getText'):
                    left_text = left.getText().strip()
                    if left_text and left_text.isalnum() and not left_text.isdigit():
                        left_var_name = left_text
                
                if not right_var_name and hasattr(right, 'getText'):
                    right_text = right.getText().strip()
                    if right_text and right_text.isalnum() and not right_text.isdigit():
                        right_var_name = right_text
                
                left_is_str = (left_type == "str")
                right_is_str = (right_type == "str")
                
                if left_var_name:
                    left_var_type = self.get_var_type(left_var_name)
                    if left_var_type == "str":
                        left_is_str = True
                
                if right_var_name:
                    right_var_type = self.get_var_type(right_var_name)
                    if right_var_type == "str":
                        right_is_str = True
                
                if left_var_name and left_var_name in self.locals:
                    loc_info = self.locals[left_var_name]
                    if isinstance(loc_info, tuple) and len(loc_info) == 2:
                        first_elem, second_elem = loc_info
                        if isinstance(first_elem, str) and first_elem.startswith("arg_") and second_elem == "str":
                            left_is_str = True
                        elif str(second_elem) == "string":
                            left_is_str = True
                
                if right_var_name and right_var_name in self.locals:
                    loc_info = self.locals[right_var_name]
                    if isinstance(loc_info, tuple) and len(loc_info) == 2:
                        first_elem, second_elem = loc_info
                        if isinstance(first_elem, str) and first_elem.startswith("arg_") and second_elem == "str":
                            right_is_str = True
                        elif str(second_elem) == "string":
                            right_is_str = True
                
                if isinstance(left, langParser.FuncCallPrimaryContext):
                    func_call = left.funcCall()
                    if func_call:
                        func_name = func_call.ID().getText()
                        from SemanticAnalyzer import SemanticAnalyzer
                        if func_name in SemanticAnalyzer.BUILTIN_FUNCTIONS:
                            return_type, _ = SemanticAnalyzer.BUILTIN_FUNCTIONS[func_name]
                            if return_type == "str":
                                left_is_str = True
                
                if isinstance(right, langParser.FuncCallPrimaryContext):
                    func_call = right.funcCall()
                    if func_call:
                        func_name = func_call.ID().getText()
                        from SemanticAnalyzer import SemanticAnalyzer
                        if func_name in SemanticAnalyzer.BUILTIN_FUNCTIONS:
                            return_type, _ = SemanticAnalyzer.BUILTIN_FUNCTIONS[func_name]
                            if return_type == "str":
                                right_is_str = True
                
                use_string_equals = False
                
                if left_is_str or right_is_str:
                    use_string_equals = True
                elif (left_type == "unknown" and left_var_name) or (right_type == "unknown" and right_var_name):
                    if left_type == "unknown" and left_var_name:
                        left_check_type = self.get_var_type(left_var_name)
                        if left_check_type == "str":
                            use_string_equals = True
                        elif left_var_name in self.locals:
                            loc_info = self.locals[left_var_name]
                            if isinstance(loc_info, tuple) and len(loc_info) == 2:
                                _, second_elem = loc_info
                                if str(second_elem) == "string":
                                    use_string_equals = True
                    
                    if not use_string_equals and right_type == "unknown" and right_var_name:
                        right_check_type = self.get_var_type(right_var_name)
                        if right_check_type == "str":
                            use_string_equals = True
                        elif right_var_name in self.locals:
                            loc_info = self.locals[right_var_name]
                            if isinstance(loc_info, tuple) and len(loc_info) == 2:
                                _, second_elem = loc_info
                                if str(second_elem) == "string":
                                    use_string_equals = True
                
                if use_string_equals:
                    self.emit("    callvirt instance bool [mscorlib]System.String::Equals(string)")
                elif (left_type == "unknown" or right_type == "unknown"):
                    if left_type not in ["int", "float", "double", "bool"] and right_type not in ["int", "float", "double", "bool"]:
                        self.emit("    callvirt instance bool [mscorlib]System.String::Equals(string)")
                    else:
                        self.emit("    ceq")
                elif left_type == "int" and right_type == "int":
                    self.emit("    ceq")
                elif left_type in ["int", "float", "double"] and right_type in ["int", "float", "double"]:
                    self.emit("    ceq")
                elif left_type == "int" or right_type == "int" or is_left_arithmetic or is_right_arithmetic:
                    if left_type != "int" and left_type not in ["float", "double"] and not is_left_arithmetic:
                        if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                            left_var_name = left.ID().getText()
                            left_var_type = self.get_var_type(left_var_name)
                            if left_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    elif right_type != "int" and right_type not in ["float", "double"] and not is_right_arithmetic:
                        if isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                            right_var_name = right.ID().getText()
                            right_var_type = self.get_var_type(right_var_name)
                            if right_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    self.emit("    ceq")
                else:
                    self.emit("    ceq")
            elif ctx.NEQ() or op.getText() == "!=":
                is_left_string_ne = (left_type == "str")
                is_right_string_ne = (right_type == "str")
                
                if not is_left_string_ne and left_var_name_for_pre_check:
                    left_var_type_ne = self.get_var_type(left_var_name_for_pre_check)
                    if left_var_type_ne == "str":
                        is_left_string_ne = True
                    elif left_var_name_for_pre_check in self.locals:
                        loc_info = self.locals[left_var_name_for_pre_check]
                        if isinstance(loc_info, tuple) and len(loc_info) == 2:
                            first_elem, second_elem = loc_info
                            if isinstance(first_elem, str) and first_elem.startswith("arg_") and second_elem == "str":
                                is_left_string_ne = True
                            elif str(second_elem) == "string":
                                is_left_string_ne = True
                
                if not is_right_string_ne and right_var_name_for_pre_check:
                    right_var_type_ne = self.get_var_type(right_var_name_for_pre_check)
                    if right_var_type_ne == "str":
                        is_right_string_ne = True
                    elif right_var_name_for_pre_check in self.locals:
                        loc_info = self.locals[right_var_name_for_pre_check]
                        if isinstance(loc_info, tuple) and len(loc_info) == 2:
                            first_elem, second_elem = loc_info
                            if isinstance(first_elem, str) and first_elem.startswith("arg_") and second_elem == "str":
                                is_right_string_ne = True
                            elif str(second_elem) == "string":
                                is_right_string_ne = True
                
                if is_left_string_ne and is_right_string_ne:
                    self.emit("    callvirt instance bool [mscorlib]System.String::Equals(string)")
                    self.emit("    ldc.i4.0")
                    self.emit("    ceq")
                else:
                    self.emit("    ceq")
                    self.emit("    ldc.i4.0")
                    self.emit("    ceq")
            elif ctx.LT() or op.getText() == "<":
                if (left_type in ["int", "float", "double"] and right_type in ["int", "float", "double"]):
                    self.emit("    clt")
                elif left_type == "int" and right_type not in ["int", "float", "double"]:
                    from gen.langParser import langParser
                    if isinstance(right, langParser.FuncCallPrimaryContext):
                        func_call = right.funcCall()
                        if func_call and func_call.ID().getText() == "size":
                            self.emit("    clt")
                        else:
                            self.emit("    clt")
                    else:
                        if isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                            right_var_name = right.ID().getText()
                            right_var_type = self.get_var_type(right_var_name)
                            if right_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                        self.emit("    clt")
                elif right_type == "int" and left_type not in ["int", "float", "double"]:
                    from gen.langParser import langParser
                    if isinstance(left, langParser.FuncCallPrimaryContext):
                        func_call = left.funcCall()
                        if func_call and func_call.ID().getText() == "size":
                            self.emit("    clt")
                        else:
                            self.emit("    clt")
                    else:
                        if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                            left_var_name = left.ID().getText()
                            left_var_type = self.get_var_type(left_var_name)
                            if left_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                        self.emit("    clt")
                elif left_type in ["int", "float", "double"] or right_type in ["int", "float", "double"]:
                    if left_type not in ["int", "float", "double"]:
                        from gen.langParser import langParser
                        if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                            left_var_name = left.ID().getText()
                            left_var_type = self.get_var_type(left_var_name)
                            if left_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    elif right_type not in ["int", "float", "double"]:
                        from gen.langParser import langParser
                        if isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                            right_var_name = right.ID().getText()
                            right_var_type = self.get_var_type(right_var_name)
                            if right_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    self.emit("    clt")
                else:
                    self.emit("    callvirt instance int32 [mscorlib]System.IComparable::CompareTo(object)")
                    self.emit("    ldc.i4.0")
                    self.emit("    clt")
            elif ctx.LE() or op.getText() == "<=":
                from gen.langParser import langParser
                is_left_arithmetic = isinstance(left, langParser.ExprContext) and left.getChildCount() == 3 and \
                                     (left.MUL() or left.DIV() or left.MOD() or left.PLUS() or left.MINUS())
                is_right_arithmetic = isinstance(right, langParser.ExprContext) and right.getChildCount() == 3 and \
                                      (right.MUL() or right.DIV() or right.MOD() or right.PLUS() or right.MINUS())
                
                if is_left_arithmetic:
                    left_type = "int"
                
                if is_right_arithmetic:
                    right_type = "int"
                
                left_is_int32 = False
                right_is_int32 = False
                
                def check_if_int32(operand, var_name_from_pre_check):
                    if var_name_from_pre_check and var_name_from_pre_check in self.locals:
                        _, il_type = self.locals[var_name_from_pre_check]
                        if str(il_type) == "int32":
                            return True
                    
                    var_name = None
                    if isinstance(operand, langParser.PrimaryContext) and hasattr(operand, "ID") and operand.ID():
                        var_name = operand.ID().getText()
                    elif isinstance(operand, langParser.IdWithIndexContext) and not operand.indexSuffix():
                        var_name = operand.ID().getText()
                    
                    if var_name and var_name in self.locals:
                        _, il_type = self.locals[var_name]
                        if str(il_type) == "int32":
                            return True
                    
                    op_type = self.analyzer.infer_type(operand)
                    if op_type == "int":
                        return True
                    
                    if isinstance(operand, langParser.FuncCallPrimaryContext):
                        func_call = operand.funcCall()
                        if func_call:
                            func_name = func_call.ID().getText()
                            if func_name == "toInt":
                                return True
                    
                    return False
                
                left_is_int32 = check_if_int32(left, left_var_name_for_pre_check)
                right_is_int32 = check_if_int32(right, right_var_name_for_pre_check)
                
                if left_type == "int":
                    left_is_int32 = True
                if right_type == "int":
                    right_is_int32 = True
                if is_left_arithmetic:
                    left_is_int32 = True
                if is_right_arithmetic:
                    right_is_int32 = True
                
                final_left_is_int32 = False
                final_right_is_int32 = False
                
                if left_var_name_for_pre_check and left_var_name_for_pre_check in self.locals:
                    _, left_il_type_final = self.locals[left_var_name_for_pre_check]
                    if str(left_il_type_final) == "int32":
                        final_left_is_int32 = True
                if not final_left_is_int32:
                    left_var_name_final = None
                    if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                        left_var_name_final = left.ID().getText()
                    elif isinstance(left, langParser.IdWithIndexContext) and not left.indexSuffix():
                        left_var_name_final = left.ID().getText()
                    if left_var_name_final and left_var_name_final in self.locals:
                        _, left_il_type_final = self.locals[left_var_name_final]
                        if str(left_il_type_final) == "int32":
                            final_left_is_int32 = True
                
                if right_var_name_for_pre_check and right_var_name_for_pre_check in self.locals:
                    _, right_il_type_final = self.locals[right_var_name_for_pre_check]
                    if str(right_il_type_final) == "int32":
                        final_right_is_int32 = True
                if not final_right_is_int32:
                    right_var_name_final = None
                    if isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                        right_var_name_final = right.ID().getText()
                    elif isinstance(right, langParser.IdWithIndexContext) and not right.indexSuffix():
                        right_var_name_final = right.ID().getText()
                    if right_var_name_final and right_var_name_final in self.locals:
                        _, right_il_type_final = self.locals[right_var_name_final]
                        if str(right_il_type_final) == "int32":
                            final_right_is_int32 = True
                
                left_is_int32 = left_is_int32 or final_left_is_int32
                right_is_int32 = right_is_int32 or final_right_is_int32
                
                use_direct_comparison = False
                
                def check_int32_in_locals(operand, var_name_from_pre_check):
                    if var_name_from_pre_check and var_name_from_pre_check in self.locals:
                        _, il_type = self.locals[var_name_from_pre_check]
                        if str(il_type) == "int32":
                            return True
                    
                    var_name = None
                    if isinstance(operand, langParser.PrimaryContext) and hasattr(operand, "ID") and operand.ID():
                        var_name = operand.ID().getText()
                    elif isinstance(operand, langParser.IdWithIndexContext) and not operand.indexSuffix():
                        var_name = operand.ID().getText()
                    
                    if var_name and var_name in self.locals:
                        _, il_type = self.locals[var_name]
                        if str(il_type) == "int32":
                            return True
                    
                    return False
                
                if check_int32_in_locals(left, left_var_name_for_pre_check):
                    use_direct_comparison = True
                if not use_direct_comparison and check_int32_in_locals(right, right_var_name_for_pre_check):
                    use_direct_comparison = True
                
                if use_direct_comparison or left_is_int32 or right_is_int32 or \
                   (left_type in ["int", "float", "double"] and right_type in ["int", "float", "double"]) or \
                   (left_type == "int" or right_type == "int") or \
                   is_left_arithmetic or is_right_arithmetic:
                    self.emit("    cgt")
                    self.emit("    ldc.i4.0")
                    self.emit("    ceq")
                else:
                    use_direct = False
                    
                    if left_var_name_for_pre_check and left_var_name_for_pre_check in self.locals:
                        _, left_il_type_check = self.locals[left_var_name_for_pre_check]
                        if str(left_il_type_check) == "int32":
                            use_direct = True
                    if not use_direct and right_var_name_for_pre_check and right_var_name_for_pre_check in self.locals:
                        _, right_il_type_check = self.locals[right_var_name_for_pre_check]
                        if str(right_il_type_check) == "int32":
                            use_direct = True
                    
                    if not use_direct:
                        left_var_name_ast = None
                        if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                            left_var_name_ast = left.ID().getText()
                        elif isinstance(left, langParser.IdWithIndexContext) and not left.indexSuffix():
                            left_var_name_ast = left.ID().getText()
                        
                        if left_var_name_ast and left_var_name_ast in self.locals:
                            _, left_il_type_ast = self.locals[left_var_name_ast]
                            if str(left_il_type_ast) == "int32":
                                use_direct = True
                    
                    if not use_direct:
                        right_var_name_ast = None
                        if isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                            right_var_name_ast = right.ID().getText()
                        elif isinstance(right, langParser.IdWithIndexContext) and not right.indexSuffix():
                            right_var_name_ast = right.ID().getText()
                        
                        if right_var_name_ast and right_var_name_ast in self.locals:
                            _, right_il_type_ast = self.locals[right_var_name_ast]
                            if str(right_il_type_ast) == "int32":
                                use_direct = True
                    
                    if use_direct:
                        self.emit("    cgt")
                        self.emit("    ldc.i4.0")
                        self.emit("    ceq")
                    else:
                        final_check_left = False
                        final_check_right = False
                        
                        if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                            left_name_final = left.ID().getText()
                            if left_name_final in self.locals:
                                _, left_il_final = self.locals[left_name_final]
                                if str(left_il_final) == "int32":
                                    final_check_left = True
                        elif isinstance(left, langParser.IdWithIndexContext) and not left.indexSuffix():
                            left_name_final = left.ID().getText()
                            if left_name_final in self.locals:
                                _, left_il_final = self.locals[left_name_final]
                                if str(left_il_final) == "int32":
                                    final_check_left = True
                        
                        if isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                            right_name_final = right.ID().getText()
                            if right_name_final in self.locals:
                                _, right_il_final = self.locals[right_name_final]
                                if str(right_il_final) == "int32":
                                    final_check_right = True
                        elif isinstance(right, langParser.IdWithIndexContext) and not right.indexSuffix():
                            right_name_final = right.ID().getText()
                            if right_name_final in self.locals:
                                _, right_il_final = self.locals[right_name_final]
                                if str(right_il_final) == "int32":
                                    final_check_right = True
                        
                        if final_check_left or final_check_right or left_type == "int" or right_type == "int":
                            self.emit("    cgt")
                            self.emit("    ldc.i4.0")
                            self.emit("    ceq")
                        else:
                            use_compare_to = False
                            
                            left_is_string = (left_type == "str" or 
                                             (isinstance(left, langParser.PrimaryContext) and hasattr(left, "STRING")))
                            right_is_string = (right_type == "str" or 
                                              (isinstance(right, langParser.PrimaryContext) and hasattr(right, "STRING")))
                            
                            if left_is_string and right_is_string:
                                use_compare_to = True
                            
                            if use_compare_to:
                                self.emit("    callvirt instance int32 [mscorlib]System.IComparable::CompareTo(object)")
                                self.emit("    ldc.i4.1")
                                self.emit("    cgt")
                                self.emit("    ldc.i4.0")
                                self.emit("    ceq")
                            else:
                                self.emit("    cgt")
                                self.emit("    ldc.i4.0")
                                self.emit("    ceq")
            elif ctx.GT() or op.getText() == ">":
                if (left_type in ["int", "float", "double"] and right_type in ["int", "float", "double"]) or \
                   (left_type == "int" and right_type == "int"):
                    self.emit("    cgt")
                elif left_type in ["int", "float", "double"] or right_type in ["int", "float", "double"]:
                    self.emit("    cgt")
                else:
                    self.emit("    callvirt instance int32 [mscorlib]System.IComparable::CompareTo(object)")
                    self.emit("    ldc.i4.0")
                    self.emit("    cgt")
            elif ctx.GE() or op.getText() == ">=":
                if (left_type in ["int", "float", "double"] and right_type in ["int", "float", "double"]) or \
                   (left_type == "int" and right_type == "int"):
                    self.emit("    clt")
                    self.emit("    ldc.i4.0")
                    self.emit("    ceq")
                elif left_type in ["int", "float", "double"] or right_type in ["int", "float", "double"]:
                    self.emit("    clt")
                    self.emit("    ldc.i4.0")
                    self.emit("    ceq")
                else:
                    self.emit("    callvirt instance int32 [mscorlib]System.IComparable::CompareTo(object)")
                    self.emit("    ldc.i4.m1")
                    self.emit("    cgt")
                    self.emit("    ldc.i4.0")
                    self.emit("    ceq")
            elif ctx.PLUS() or op.getText() == "+":
                if left_type == "str" or right_type == "str" or left_type == "set" or right_type == "set":
                    
                    if right_type == "unknown":
                        right_type_inferred = self.analyzer.infer_type(right)
                        if right_type_inferred != "unknown":
                            right_type = right_type_inferred
                    if left_type == "unknown":
                        left_type_inferred = self.analyzer.infer_type(left)
                        if left_type_inferred != "unknown":
                            left_type = left_type_inferred
                    
                    from gen.langParser import langParser
                    if right_type == "unknown" or right_type != "set":
                        right_var_name_check = None
                        if isinstance(right, langParser.IdWithIndexContext) and not right.indexSuffix():
                            right_var_name_check = right.ID().getText()
                        elif isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                            right_var_name_check = right.ID().getText()
                        
                        if right_var_name_check and right_var_name_check in self.locals:
                            _, right_il_type_check = self.locals[right_var_name_check]
                            right_il_type_str = str(right_il_type_check)
                            if "List`1<object>" in right_il_type_str:
                                right_type = "set"
                            elif right_il_type_str == "int32" and right_type == "unknown":
                                right_type = "int"
                    
                    if left_type == "unknown" or left_type != "set":
                        left_var_name_check = None
                        if isinstance(left, langParser.IdWithIndexContext) and not left.indexSuffix():
                            left_var_name_check = left.ID().getText()
                        elif isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                            left_var_name_check = left.ID().getText()
                        
                        if left_var_name_check and left_var_name_check in self.locals:
                            _, left_il_type_check = self.locals[left_var_name_check]
                            left_il_type_str = str(left_il_type_check)
                            if "List`1<object>" in left_il_type_str:
                                left_type = "set"
                            elif left_il_type_str == "int32" and left_type == "unknown":
                                left_type = "int"
                    
                    def needs_box_for_tostring(operand, semantic_type):
                        from gen.langParser import langParser
                        
                        if semantic_type == "set":
                            return (False, "set")
                        elif semantic_type == "str":
                            return (False, None)
                        elif semantic_type == "int":
                            return (True, "int32")
                        elif semantic_type == "bool":
                            return (True, "bool")
                        
                        var_name = None
                        if isinstance(operand, langParser.IdWithIndexContext) and not operand.indexSuffix():
                            var_name = operand.ID().getText()
                        elif isinstance(operand, langParser.PrimaryContext) and hasattr(operand, "ID") and operand.ID():
                            var_name = operand.ID().getText()
                        elif isinstance(operand, langParser.ParensExprContext):
                            inner = operand.expr()
                            if isinstance(inner, langParser.IdWithIndexContext) and not inner.indexSuffix():
                                var_name = inner.ID().getText()
                            elif isinstance(inner, langParser.PrimaryContext) and hasattr(inner, "ID") and inner.ID():
                                var_name = inner.ID().getText()
                        
                        if var_name and var_name in self.locals:
                            loc_info = self.locals[var_name]
                            if isinstance(loc_info, tuple) and len(loc_info) == 2:
                                first_elem, second_elem = loc_info
                                if isinstance(first_elem, str) and first_elem.startswith("arg_"):
                                    param_semantic_type = second_elem
                                    if param_semantic_type == "str":
                                        return (False, None)
                                    elif param_semantic_type == "set":
                                        return (False, "set")
                                    elif param_semantic_type == "int":
                                        return (True, "int32")
                                    elif param_semantic_type == "bool":
                                        return (True, "bool")
                                else:
                                    il_type = second_elem
                                    il_type_str = str(il_type)
                                    if il_type_str == "int32":
                                        return (True, "int32")
                                    elif il_type_str == "bool":
                                        return (True, "bool")
                                    elif il_type_str == "string":
                                        return (False, None)
                                    elif "List`1<object>" in il_type_str:
                                        return (False, "set")
                        
                        if var_name:
                            var_type_from_analyzer = self.get_var_type(var_name)
                            if var_type_from_analyzer == "set":
                                return (False, "set")
                            elif var_type_from_analyzer == "int":
                                return (True, "int32")
                            elif var_type_from_analyzer == "bool":
                                return (True, "bool")
                            elif var_type_from_analyzer == "str":
                                return (False, None)
                        
                        if not var_name and hasattr(operand, "getText"):
                            operand_text = operand.getText().strip()
                            for local_var_name, loc_info in self.locals.items():
                                if local_var_name == operand_text:
                                    if isinstance(loc_info, tuple) and len(loc_info) == 2:
                                        first_elem, second_elem = loc_info
                                        if isinstance(first_elem, str) and first_elem.startswith("arg_"):
                                            param_semantic_type = second_elem
                                            if param_semantic_type == "str":
                                                return (False, None)
                                            elif param_semantic_type == "set":
                                                return (False, "set")
                                            elif param_semantic_type == "int":
                                                return (True, "int32")
                                            elif param_semantic_type == "bool":
                                                return (True, "bool")
                                        else:
                                            il_type = second_elem
                                            il_type_str = str(il_type)
                                            if "List`1<object>" in il_type_str:
                                                return (False, "set")
                                            elif il_type_str == "int32":
                                                return (True, "int32")
                                            elif il_type_str == "bool":
                                                return (True, "bool")
                                            elif il_type_str == "string":
                                                return (False, None)
                            
                            if operand_text in [name for name in self.locals.keys()]:
                                var_type_from_text = self.get_var_type(operand_text)
                                if var_type_from_text == "set":
                                    return (False, "set")
                        
                        if isinstance(operand, langParser.FuncCallPrimaryContext):
                            func_call = operand.funcCall()
                            if func_call:
                                func_name = func_call.ID().getText()
                                if func_name in self.function_signatures:
                                    args = func_call.argList().expr() if func_call.argList() else []
                                    for return_type, param_types, _ in self.function_signatures[func_name]:
                                        if len(param_types) == len(args):
                                            if return_type == "set":
                                                return (False, "set")
                                            elif return_type == "str":
                                                return (False, None)
                                            elif return_type == "int":
                                                return (True, "int32")
                                            elif return_type == "bool":
                                                return (True, "bool")
                                else:
                                    from SemanticAnalyzer import SemanticAnalyzer
                                    if func_name in SemanticAnalyzer.BUILTIN_FUNCTIONS:
                                        return_type, _ = SemanticAnalyzer.BUILTIN_FUNCTIONS[func_name]
                                        if return_type == "set":
                                            return (False, "set")
                                        elif return_type == "str":
                                            return (False, None)
                                        elif return_type == "int":
                                            return (True, "int32")
                        
                        if semantic_type == "unknown":
                            inferred = self.analyzer.infer_type(operand)
                            if inferred == "int":
                                return (True, "int32")
                            elif inferred == "bool":
                                return (True, "bool")
                            elif inferred == "str":
                                return (False, None)
                            elif inferred == "set":
                                return (False, "set")
                            
                            if var_name:
                                var_type_unknown = self.get_var_type(var_name)
                                if var_type_unknown == "set":
                                    return (False, "set")
                                elif var_type_unknown == "int":
                                    return (True, "int32")
                                elif var_type_unknown == "bool":
                                    return (True, "bool")
                                elif var_type_unknown == "str":
                                    return (False, None)
                        
                        final_inferred = self.analyzer.infer_type(operand)
                        if final_inferred == "set":
                            return (False, "set")
                        elif final_inferred == "str":
                            return (False, None)
                        
                        return (True, "int32")
                    
                    right_needs_box, right_box_type = needs_box_for_tostring(right, right_type)
                    
                    if right_box_type == "set":
                        self.emit("    call string Program::SetToString(class [mscorlib]System.Collections.Generic.List`1<object>)")
                    elif right_needs_box:
                        if right_box_type == "int32":
                            self.emit("    box [mscorlib]System.Int32")
                        elif right_box_type == "bool":
                            self.emit("    box [mscorlib]System.Boolean")
                        self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
                    elif right_type != "str":
                        self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
                    
                    left_needs_box, left_box_type = needs_box_for_tostring(left, left_type)
                    
                    if left_box_type == "set":
                        self.emit("    call string Program::SetToString(class [mscorlib]System.Collections.Generic.List`1<object>)")
                    elif left_needs_box:
                        if left_box_type == "int32":
                            self.emit("    box [mscorlib]System.Int32")
                        elif left_box_type == "bool":
                            self.emit("    box [mscorlib]System.Boolean")
                        self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
                    elif left_type != "str":
                        self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
                    
                    self.emit("    call string [mscorlib]System.String::Concat(string, string)")
                else:
                    self.emit("    add")
            elif ctx.MINUS() or op.getText() == "-":
                self.emit("    sub")
            elif ctx.MUL() or op.getText() == "*":
                from gen.langParser import langParser
                is_right_comparison = isinstance(right, langParser.ExprContext) and right.getChildCount() == 3 and \
                                     (right.EQ() or right.NEQ() or right.LT() or right.LE() or right.GT() or right.GE() or right.AND() or right.OR())
                
                if True:
                    if left_type != "int" and left_type not in ["float", "double"]:
                        if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                            left_var_name = left.ID().getText()
                            left_var_type = self.get_var_type(left_var_name)
                            if left_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    elif right_type != "int" and right_type not in ["float", "double"]:
                        if isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                            right_var_name = right.ID().getText()
                            right_var_type = self.get_var_type(right_var_name)
                            if right_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                    self.emit("    mul")
            elif ctx.DIV() or op.getText() == "/":
                self.emit("    div")
            elif ctx.MOD() or op.getText() == "%":
                if left_type != "int" and left_type not in ["float", "double"]:
                    if isinstance(left, langParser.PrimaryContext) and hasattr(left, "ID") and left.ID():
                        left_var_name = left.ID().getText()
                        left_var_type = self.get_var_type(left_var_name)
                        if left_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                            self.emit("    unbox.any [mscorlib]System.Int32")
                elif right_type != "int" and right_type not in ["float", "double"]:
                    if isinstance(right, langParser.PrimaryContext) and hasattr(right, "ID") and right.ID():
                        right_var_name = right.ID().getText()
                        right_var_type = self.get_var_type(right_var_name)
                        if right_var_type not in ["int", "float", "double", "bool", "str", "set"]:
                            self.emit("    unbox.any [mscorlib]System.Int32")
                self.emit("    rem")
        else:
            return self.visitChildren(ctx)

    def visitPrefixExpr(self, ctx: langParser.PrefixExprContext):
        if ctx.NOT():
            self.visit(ctx.expr())
            self.emit("    ldc.i4.0")
            self.emit("    ceq")
        elif ctx.INC():
            expr = ctx.expr()
            if isinstance(expr, langParser.PrimaryContext):
                if hasattr(expr, "ID") and expr.ID():
                    name = expr.ID().getText()
                    var_type = self.get_var_type(name)
                    self.emit_load_var(name, var_type)
                    self.emit("    ldc.i4.1")
                    self.emit("    add")
                    self.emit("    dup")
                    self.emit_store_var(name, var_type)
        elif ctx.DEC():
            expr = ctx.expr()
            if isinstance(expr, langParser.PrimaryContext):
                if hasattr(expr, "ID") and expr.ID():
                    name = expr.ID().getText()
                    var_type = self.get_var_type(name)
                    self.emit_load_var(name, var_type)
                    self.emit("    ldc.i4.1")
                    self.emit("    sub")
                    self.emit("    dup")
                    self.emit_store_var(name, var_type)

    def visitPostfixExpr(self, ctx: langParser.PostfixExprContext):
        primary = ctx.primary()
        if hasattr(primary, "ID") and primary.ID():
            name = primary.ID().getText()
            var_type = self.get_var_type(name)
            idx = self.get_local_index(name, var_type)
            
            if ctx.INC():
                self.emit_load_var(name, var_type)
                self.emit("    dup")
                self.emit("    ldc.i4.1")
                self.emit("    add")
                self.emit_store_var(name, var_type)
            elif ctx.DEC():
                self.emit_load_var(name, var_type)
                self.emit("    dup")
                self.emit("    ldc.i4.1")
                self.emit("    sub")
                self.emit_store_var(name, var_type)

    def visitLiteralPrimary(self, ctx: langParser.LiteralPrimaryContext):
        return self.visit(ctx.literal())

    def visitLiteral(self, ctx: langParser.LiteralContext):
        text = ctx.getText()
        if ctx.INT():
            self.emit(f"    ldc.i4 {text}")
        elif ctx.FLOAT():
            self.emit(f"    ldc.r8 {text}")
        elif ctx.STRING():
            str_val = text[1:-1].replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
            self.emit(f'    ldstr "{str_val}"')
        elif ctx.BOOLEAN():
            if text == "true":
                self.emit("    ldc.i4.1")
            else:
                self.emit("    ldc.i4.0")

    def visitSetLiteralPrimary(self, ctx: langParser.SetLiteralPrimaryContext):
        set_literal = ctx.setLiteral()
        self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
        
        if set_literal.exprList():
            for expr in set_literal.exprList().expr():
                self.emit("    dup")
                self.visit(expr)
                expr_type = self.analyzer.infer_type(expr)
                if expr_type == "int":
                    self.emit("    box [mscorlib]System.Int32")
                elif expr_type == "bool":
                    self.emit("    box [mscorlib]System.Boolean")
                self.emit("    callvirt instance void class [mscorlib]System.Collections.Generic.List`1<object>::Add(!0)")

    def visitIdWithIndex(self, ctx: langParser.IdWithIndexContext):
        name = ctx.ID().getText()
        var_type = self.get_var_type(name)
        self.emit_load_var(name, var_type)
        
        if ctx.indexSuffix():
            is_string_var = False
            if name in self.locals:
                _, il_type = self.locals[name]
                il_type_str = str(il_type)
                if il_type_str == "string":
                    is_string_var = True
            
            if not is_string_var:
                var_type_from_analyzer = self.get_var_type(name)
                if var_type_from_analyzer == "str":
                    is_string_var = True
            
            if not is_string_var:
                for local_name in self.locals.keys():
                    if local_name == name:
                        _, il_type_check = self.locals[local_name]
                        il_type_str_check = str(il_type_check)
                        if il_type_str_check == "string":
                            is_string_var = True
                            break
            
            for index_suffix in ctx.indexSuffix():
                self.visit(index_suffix.expr())
                index_type = self.analyzer.infer_type(index_suffix.expr())
                if index_type != "int":
                    from gen.langParser import langParser
                    if isinstance(index_suffix.expr(), langParser.PrimaryContext):
                        if hasattr(index_suffix.expr(), "ID") and index_suffix.expr().ID():
                            idx_var_name = index_suffix.expr().ID().getText()
                            idx_var_type = self.get_var_type(idx_var_name)
                            if idx_var_type != "int" and idx_var_type not in ["float", "double", "bool", "str", "set"]:
                                self.emit("    unbox.any [mscorlib]System.Int32")
                
                if is_string_var:
                    self.emit("    callvirt instance char [mscorlib]System.String::get_Chars(int32)")
                else:
                    self.emit("    callvirt instance !0 class [mscorlib]System.Collections.Generic.List`1<object>::get_Item(int32)")

    def visitFuncCallPrimary(self, ctx: langParser.FuncCallPrimaryContext):
        return self.visit(ctx.funcCall())

    def visitParensExpr(self, ctx: langParser.ParensExprContext):
        return self.visit(ctx.expr())

    def visitCastExpr(self, ctx: langParser.CastExprContext):
        self.visit(ctx.expr())
        cast_type = ctx.type_().getText()

    def visitIfStmt(self, ctx: langParser.IfStmtContext):
        self.visit(ctx.expr())
        else_label = self.get_label()
        end_label = self.get_label()
        
        has_else = False
        children_text = [c.getText() for c in ctx.getChildren() if hasattr(c, 'getText')]
        if 'else' in children_text:
            has_else = True
        
        if has_else:
            self.emit(f"    brfalse {else_label}")
        else:
            self.emit(f"    brfalse {end_label}")
        
        if ctx.statement():
            for stmt in ctx.statement():
                self.visit(stmt)
        
        self.emit(f"    br {end_label}")
        
        if has_else:
            self.emit(f"  {else_label}:")
            found_else = False
            for child in ctx.getChildren():
                if found_else:
                    if isinstance(child, langParser.SimpleStmtContext):
                        self.visit(child)
                    elif hasattr(child, 'statement'):
                        for stmt in child.statement():
                            self.visit(stmt)
                elif hasattr(child, 'getText') and child.getText() == 'else':
                    found_else = True
        
        self.emit(f"  {end_label}:")

    def visitWhileStmt(self, ctx: langParser.WhileStmtContext):
        check_label = self.get_label()
        body_label = self.get_label()
        end_label = self.get_label()
        
        self.emit(f"    br {check_label}")
        self.emit(f"  {body_label}:")
        
        if ctx.statement():
            for stmt in ctx.statement():
                self.visit(stmt)
        
        self.emit(f"  {check_label}:")
        self.visit(ctx.expr())
        self.emit(f"    brtrue {body_label}")
        self.emit(f"  {end_label}:")

    def visitForStmt(self, ctx: langParser.ForStmtContext):
        if ctx.forInit():
            self.visit(ctx.forInit())
        
        check_label = self.get_label()
        body_label = self.get_label()
        iter_label = self.get_label()
        end_label = self.get_label()
        
        self.emit(f"    br {check_label}")
        self.emit(f"  {body_label}:")
        
        if ctx.statement():
            for stmt in ctx.statement():
                self.visit(stmt)
        
        self.emit(f"  {iter_label}:")
        if ctx.forIter():
            self.visit(ctx.forIter())
        
        self.emit(f"  {check_label}:")
        if ctx.forCond():
            self.visit(ctx.forCond())
            self.emit(f"    brtrue {body_label}")
        else:
            self.emit(f"    br {body_label}")
        
        self.emit(f"  {end_label}:")

    def visitForInit(self, ctx: langParser.ForInitContext):
        declared_type = ctx.type_().getText() if ctx.type_() else None
        ids = ctx.ID()
        
        for i, id_token in enumerate(ids):
            name = id_token.getText()
            children = list(ctx.getChildren())
            expr_idx = -1
            for j, child in enumerate(children):
                if hasattr(child, 'getText') and child.getText() == name:
                    if j + 1 < len(children) and hasattr(children[j+1], 'getText') and children[j+1].getText() == '=':
                        if j + 2 < len(children):
                            expr_idx = j + 2
                            break
            
            if expr_idx >= 0 and isinstance(children[expr_idx], langParser.ExprContext):
                self.visit(children[expr_idx])
                expr_type = self.analyzer.infer_type(children[expr_idx])
                var_type = declared_type or expr_type or "int"
                self.convert_type(expr_type, var_type)
            else:
                var_type = declared_type or "int"
                if var_type == "int":
                    self.emit("    ldc.i4.0")
                elif var_type == "bool":
                    self.emit("    ldc.i4.0")
                else:
                    self.emit("    ldnull")
            
            self.get_local_index(name, var_type)
            self.emit_store_var(name, var_type)

    def visitForIter(self, ctx: langParser.ForIterContext):
        if ctx.ID():
            name = ctx.ID().getText()
            var_type = self.get_var_type(name)
            idx = self.get_local_index(name, var_type)
            
            if ctx.INC():
                self.emit_load_var(name, var_type)
                self.emit("    ldc.i4.1")
                self.emit("    add")
                self.emit_store_var(name, var_type)
            elif ctx.DEC():
                self.emit_load_var(name, var_type)
                self.emit("    ldc.i4.1")
                self.emit("    sub")
                self.emit_store_var(name, var_type)
            elif ctx.expr():
                self.visit(ctx.expr())
                expr_type = self.analyzer.infer_type(ctx.expr())
                self.convert_type(expr_type, var_type)
                self.emit_store_var(name, var_type)

    def visitSimpleStmt(self, ctx: langParser.SimpleStmtContext):
        if ctx.getText().startswith("return"):
            if ctx.expr():
                self.visit(ctx.expr())
                if self.current_function:
                    func_name, return_type = self.current_function
                    if return_type == "int":
                        expr_type = self.analyzer.infer_type(ctx.expr())
                        if expr_type != "int":
                            from gen.langParser import langParser
                            if isinstance(ctx.expr(), langParser.IdWithIndexContext):
                                var_name = ctx.expr().ID().getText()
                                var_type = self.get_var_type(var_name)
                                if var_type == "set":
                                    self.emit("    unbox.any [mscorlib]System.Int32")
                            elif isinstance(ctx.expr(), langParser.PrimaryContext):
                                if hasattr(ctx.expr(), "ID") and ctx.expr().ID():
                                    var_name = ctx.expr().ID().getText()
                                    var_type = self.get_var_type(var_name)
                                    if var_type != "int" and var_type not in ["float", "double", "bool", "str", "set"]:
                                        if var_type is None or var_type == "unknown":
                                            pass
            self.emit("    ret")
        else:
            return self.visitChildren(ctx)

    def generate_set_to_string(self):
        self.emit("  .method private static string SetToString(class [mscorlib]System.Collections.Generic.List`1<object> set) cil managed")
        self.emit("  {")
        self.emit("    .locals init (string V_0, int32 V_1, string V_2, object V_3)")
        self.emit('    ldstr "["')
        self.emit("    stloc V_2")
        self.emit("    ldc.i4.0")
        self.emit("    stloc V_1")
        self.emit("    br L_set_loop_check")
        self.emit("    L_set_loop:")
        self.emit("    ldloc V_1")
        self.emit("    ldc.i4.0")
        self.emit("    ble L_set_skip_comma")
        self.emit("    ldloc V_2")
        self.emit('    ldstr ", "')
        self.emit("    call string [mscorlib]System.String::Concat(string, string)")
        self.emit("    stloc V_2")
        self.emit("    L_set_skip_comma:")
        self.emit("    ldarg.0")
        self.emit("    ldloc V_1")
        self.emit("    callvirt instance !0 class [mscorlib]System.Collections.Generic.List`1<object>::get_Item(int32)")
        self.emit("    stloc V_3")
        self.emit("    ldloc V_2")
        self.emit("    ldloc V_3")
        self.emit("    callvirt instance string [mscorlib]System.Object::ToString()")
        self.emit("    call string [mscorlib]System.String::Concat(string, string)")
        self.emit("    stloc V_2")
        self.emit("    ldloc V_1")
        self.emit("    ldc.i4.1")
        self.emit("    add")
        self.emit("    stloc V_1")
        self.emit("    L_set_loop_check:")
        self.emit("    ldloc V_1")
        self.emit("    ldarg.0")
        self.emit("    callvirt instance int32 class [mscorlib]System.Collections.Generic.List`1<object>::get_Count()")
        self.emit("    blt L_set_loop")
        self.emit("    ldloc V_2")
        self.emit('    ldstr "]"')
        self.emit("    call string [mscorlib]System.String::Concat(string, string)")
        self.emit("    stloc V_2")
        self.emit("    ldloc V_2")
        self.emit("    ret")
        self.emit("  }")
        self.emit("")

    def generate_builtin_helpers(self):
        self.emit("  .method private static class [mscorlib]System.Collections.Generic.List`1<object> Split(string str, string delimiter) cil managed")
        self.emit("  {")
        self.emit("    .locals init (class [mscorlib]System.Collections.Generic.List`1<object> V_0, string[] V_1, int32 V_2)")
        self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
        self.emit("    stloc V_0")
        self.emit("    ldarg.0")
        self.emit("    ldc.i4.1")
        self.emit("    newarr string")
        self.emit("    dup")
        self.emit("    ldc.i4.0")
        self.emit("    ldarg.1")
        self.emit("    stelem.ref")
        self.emit("    ldc.i4.0")
        self.emit("    callvirt instance string[] [mscorlib]System.String::Split(string[], valuetype [mscorlib]System.StringSplitOptions)")
        self.emit("    stloc V_1")
        self.emit("    ldc.i4.0")
        self.emit("    stloc V_2")
        self.emit("    br L_split_check")
        self.emit("    L_split_loop:")
        self.emit("    ldloc V_0")
        self.emit("    ldloc V_1")
        self.emit("    ldloc V_2")
        self.emit("    ldelem.ref")
        self.emit("    callvirt instance void class [mscorlib]System.Collections.Generic.List`1<object>::Add(!0)")
        self.emit("    ldloc V_2")
        self.emit("    ldc.i4.1")
        self.emit("    add")
        self.emit("    stloc V_2")
        self.emit("    L_split_check:")
        self.emit("    ldloc V_2")
        self.emit("    ldloc V_1")
        self.emit("    ldlen")
        self.emit("    conv.i4")
        self.emit("    blt L_split_loop")
        self.emit("    ldloc V_0")
        self.emit("    ret")
        self.emit("  }")
        self.emit("")
        self.emit("  .method private static class [mscorlib]System.Collections.Generic.List`1<object> GetFileNames(string path) cil managed")
        self.emit("  {")
        self.emit("    .locals init (class [mscorlib]System.Collections.Generic.List`1<object> V_0, string[] V_1, int32 V_2)")
        self.emit("    newobj instance void class [mscorlib]System.Collections.Generic.List`1<object>::.ctor()")
        self.emit("    stloc V_0")
        self.emit("    ldarg.0")
        self.emit("    call string[] [mscorlib]System.IO.Directory::GetFiles(string)")
        self.emit("    stloc V_1")
        self.emit("    ldc.i4.0")
        self.emit("    stloc V_2")
        self.emit("    br L_getfiles_check")
        self.emit("    L_getfiles_loop:")
        self.emit("    ldloc V_0")
        self.emit("    ldloc V_1")
        self.emit("    ldloc V_2")
        self.emit("    ldelem.ref")
        self.emit("    callvirt instance void class [mscorlib]System.Collections.Generic.List`1<object>::Add(!0)")
        self.emit("    ldloc V_2")
        self.emit("    ldc.i4.1")
        self.emit("    add")
        self.emit("    stloc V_2")
        self.emit("    L_getfiles_check:")
        self.emit("    ldloc V_2")
        self.emit("    ldloc V_1")
        self.emit("    ldlen")
        self.emit("    conv.i4")
        self.emit("    blt L_getfiles_loop")
        self.emit("    ldloc V_0")
        self.emit("    ret")
        self.emit("  }")
        self.emit("")

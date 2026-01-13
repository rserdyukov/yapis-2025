from gen.yapis2Parser import yapis2Parser
from gen.yapis2Visitor import yapis2Visitor
from antlr4 import CommonTokenStream, FileStream
from antlr4.tree.Tree import TerminalNodeImpl
from gen.yapis2Lexer import yapis2Lexer


class Compiler(yapis2Visitor):

    def __init__(self):
        super().__init__()
        self.output = []
        self.indent = ""
        self.label_counter = 0
        self.functions = {}
        self.variables = {}
        self.var_types = {}
        self.local_counter = 0
        self.max_local_used = 0
        self.stack_depth = 0
        self.max_stack = 0
        self.source_file_path = None
        self.in_function = False
        self.main_statements = []
        self.break_labels_stack = []

    def emit(self, line):
        self.output.append(self.indent + line)

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def get_local_index(self, name):
        if name not in self.variables:
            self.variables[name] = self.local_counter
            self.max_local_used = max(self.max_local_used, self.local_counter)
            self.local_counter += 1
        else:
            self.max_local_used = max(self.max_local_used, self.variables[name])
        return self.variables[name]

    def visitProgram(self, ctx: yapis2Parser.ProgramContext):
        self.generate_type_class_files()
        
        self.emit(".class public Main")
        self.emit(".super java/lang/Object\n")
        self.emit(".field private static scanner Ljava/util/Scanner;\n")

        for func in ctx.functionDecl():
            self.register_function(func)

        for func in ctx.functionDecl():
            self.visitFunctionDecl(func)
        
        self.main_statements = list(ctx.statement())

        self.generate_main(ctx)

        return "\n".join(self.output)
    
    def _find_statements_recursive(self, node, statements, skip_functions=False, depth=0, in_function=False):
        if isinstance(node, yapis2Parser.FunctionDeclContext):
            if skip_functions:
                return
            in_function = True
        
        if isinstance(node, yapis2Parser.StatementContext):
            if not skip_functions or not in_function:
                statements.append(node)
            return
        
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            if hasattr(child, 'getChildCount'):
                self._find_statements_recursive(child, statements, skip_functions, depth + 1, in_function)
    
    def _find_top_level_statements_direct(self, node, statements, in_function=False):
        if isinstance(node, yapis2Parser.FunctionDeclContext):
            in_function = True
            return
        
        if isinstance(node, yapis2Parser.BlockContext) and in_function:
            return
        
        if isinstance(node, yapis2Parser.StatementContext):
            if not in_function:
                statements.append(node)
            return
        
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            if hasattr(child, 'getChildCount'):
                self._find_top_level_statements_direct(child, statements, in_function)
    
    def _find_top_level_statements(self, node, statements, in_function=False, depth=0, max_depth=10):
        if depth > max_depth:
            return
        
        node_type = type(node).__name__
        
        if isinstance(node, yapis2Parser.StatementContext):
            if not in_function:
                print(f"DEBUG _find_top_level_statements: Found StatementContext at depth {depth}, in_function={in_function}")
                statements.append(node)
            return
        
        if isinstance(node, yapis2Parser.FunctionDeclContext):
            in_function = True
            print(f"DEBUG _find_top_level_statements: Entering function at depth {depth}")
        
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            child_type = type(child).__name__
            if depth == 0:
                print(f"DEBUG _find_top_level_statements: Child {i} at depth {depth}: {child_type}")
            if hasattr(child, 'getChildCount'):
                self._find_top_level_statements(child, statements, in_function, depth + 1, max_depth)
    
    def generate_type_class_files(self):
        point_code = [
            ".class public Point",
            ".super java/lang/Object",
            ".field public x I",
            ".field public y I",
            "",
            ".method public <init>(II)V",
            "    .limit stack 3",
            "    .limit locals 3",
            "    aload_0",
            "    invokespecial java/lang/Object/<init>()V",
            "    aload_0",
            "    iload_1",
            "    putfield Point/x I",
            "    aload_0",
            "    iload_2",
            "    putfield Point/y I",
            "    return",
            ".end method",
            "",
            ".method public toString()Ljava/lang/String;",
            "    .limit stack 10",
            "    .limit locals 1",
            "    new java/lang/StringBuilder",
            "    dup",
            "    invokespecial java/lang/StringBuilder/<init>()V",
            "    ldc \"(\"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    aload_0",
            "    getfield Point/x I",
            "    invokevirtual java/lang/StringBuilder/append(I)Ljava/lang/StringBuilder;",
            "    ldc \", \"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    aload_0",
            "    getfield Point/y I",
            "    invokevirtual java/lang/StringBuilder/append(I)Ljava/lang/StringBuilder;",
            "    ldc \")\"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    invokevirtual java/lang/StringBuilder/toString()Ljava/lang/String;",
            "    areturn",
            ".end method"
        ]
        with open("Point.j", "w", encoding="utf-8") as f:
            f.write("\n".join(point_code))
        
        line_code = [
            ".class public Line",
            ".super java/lang/Object",
            ".field public p1 LPoint;",
            ".field public p2 LPoint;",
            "",
            ".method public <init>(LPoint;LPoint;)V",
            "    .limit stack 3",
            "    .limit locals 3",
            "    aload_0",
            "    invokespecial java/lang/Object/<init>()V",
            "    aload_0",
            "    aload_1",
            "    putfield Line/p1 LPoint;",
            "    aload_0",
            "    aload_2",
            "    putfield Line/p2 LPoint;",
            "    return",
            ".end method",
            "",
            ".method public toString()Ljava/lang/String;",
            "    .limit stack 10",
            "    .limit locals 1",
            "    new java/lang/StringBuilder",
            "    dup",
            "    invokespecial java/lang/StringBuilder/<init>()V",
            "    ldc \"Line(\"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    aload_0",
            "    getfield Line/p1 LPoint;",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/Object;)Ljava/lang/StringBuilder;",
            "    ldc \", \"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    aload_0",
            "    getfield Line/p2 LPoint;",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/Object;)Ljava/lang/StringBuilder;",
            "    ldc \")\"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    invokevirtual java/lang/StringBuilder/toString()Ljava/lang/String;",
            "    areturn",
            ".end method"
        ]
        with open("Line.j", "w", encoding="utf-8") as f:
            f.write("\n".join(line_code))
        
        circle_code = [
            ".class public Circle",
            ".super java/lang/Object",
            ".field public center LPoint;",
            ".field public radius I",
            "",
            ".method public <init>(LPoint;I)V",
            "    .limit stack 3",
            "    .limit locals 3",
            "    aload_0",
            "    invokespecial java/lang/Object/<init>()V",
            "    aload_0",
            "    aload_1",
            "    putfield Circle/center LPoint;",
            "    aload_0",
            "    iload_2",
            "    putfield Circle/radius I",
            "    return",
            ".end method",
            "",
            ".method public toString()Ljava/lang/String;",
            "    .limit stack 10",
            "    .limit locals 1",
            "    new java/lang/StringBuilder",
            "    dup",
            "    invokespecial java/lang/StringBuilder/<init>()V",
            "    ldc \"Circle(\"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    aload_0",
            "    getfield Circle/center LPoint;",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/Object;)Ljava/lang/StringBuilder;",
            "    ldc \", radius=\"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    aload_0",
            "    getfield Circle/radius I",
            "    invokevirtual java/lang/StringBuilder/append(I)Ljava/lang/StringBuilder;",
            "    ldc \")\"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    invokevirtual java/lang/StringBuilder/toString()Ljava/lang/String;",
            "    areturn",
            ".end method"
        ]
        with open("Circle.j", "w", encoding="utf-8") as f:
            f.write("\n".join(circle_code))
        
        polygon_code = [
            ".class public Polygon",
            ".super java/lang/Object",
            ".field public points [LPoint;",
            "",
            ".method public <init>([LPoint;)V",
            "    .limit stack 3",
            "    .limit locals 2",
            "    aload_0",
            "    invokespecial java/lang/Object/<init>()V",
            "    aload_0",
            "    aload_1",
            "    putfield Polygon/points [LPoint;",
            "    return",
            ".end method",
            "",
            ".method public toString()Ljava/lang/String;",
            "    .limit stack 10",
            "    .limit locals 4",
            "    new java/lang/StringBuilder",
            "    dup",
            "    invokespecial java/lang/StringBuilder/<init>()V",
            "    ldc \"Polygon([\"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    aload_0",
            "    getfield Polygon/points [LPoint;",
            "    astore_1",
            "    aload_1",
            "    arraylength",
            "    istore_2",
            "    iconst_0",
            "    istore_3",
            "LoopStart:",
            "    iload_3",
            "    iload_2",
            "    if_icmpge LoopEnd",
            "    iload_3",
            "    ifle SkipComma",
            "    ldc \", \"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "SkipComma:",
            "    aload_1",
            "    iload_3",
            "    aaload",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/Object;)Ljava/lang/StringBuilder;",
            "    iinc 3 1",
            "    goto LoopStart",
            "LoopEnd:",
            "    ldc \"])\"",
            "    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;",
            "    invokevirtual java/lang/StringBuilder/toString()Ljava/lang/String;",
            "    areturn",
            ".end method"
        ]
        with open("Polygon.j", "w", encoding="utf-8") as f:
            f.write("\n".join(polygon_code))


    def register_function(self, ctx: yapis2Parser.FunctionDeclContext):
        name = ctx.IDENTIFIER(0).getText()
        param_types = []
        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                param_types.append(p.type_().getText())
        ret_type = ctx.type_().getText() if hasattr(ctx, "type_") and ctx.type_() else None
        self.functions[name] = (param_types, ret_type)

    def visitFunctionDecl(self, ctx: yapis2Parser.FunctionDeclContext):
        old_in_function = self.in_function
        self.in_function = True
        name = ctx.IDENTIFIER(0).getText()
        param_types = []
        if ctx.parameterList():
            for p in ctx.parameterList().parameter():
                param_types.append(p.type_().getText())

        ret_type = ctx.type_().getText() if hasattr(ctx, "type_") and ctx.type_() else None
        ret_jvm = self.type_to_jvm(ret_type) if ret_type else "V"

        
        param_sig = "".join([self.type_to_jvm(t) for t in param_types])
        method_sig = f"({param_sig}){ret_jvm}"

        self.emit(f"; ========== Function {name} ==========")
        self.emit(f".method public static {name}{method_sig}")

        
        self.variables = {}
        self.local_counter = 0
        self.stack_depth = 0
        self.max_stack = 0
        self.has_return = False  
        self.max_local_used = 0  

        
        
        
        
        param_count = 0
        if ctx.parameterList():
            local_idx = 0
            for p in ctx.parameterList().parameter():
                pname = p.IDENTIFIER().getText()
                ptype = p.type_().getText()
                self.variables[pname] = local_idx
                
                self.var_types[pname] = self.type_to_jvm(ptype)
                
                self.max_local_used = max(self.max_local_used, local_idx)
                
                local_idx += 1
                param_count += 1
        
        self.local_counter = param_count

        
        
        self.emit(f"    .limit stack {max(self.max_stack, 10)}")
        
        
        locals_line_index = len(self.output)
        
        self.emit(f"    .limit locals 50\n")

        
        if ctx.block():
            for stmt in ctx.block().statement():
                if self.has_return:
                    
                    break
                self.visit(stmt)
        
        
        
        
        
        
        max_local = max(self.max_local_used + 1, param_count, 100)  
        
        
        if locals_line_index < len(self.output):
            self.output[locals_line_index] = f"    .limit locals {max_local}"

        
        if ret_type and ret_type != "void" and not self.has_return:
            
            if ret_type == "int":
                self.emit("    iconst_0")
                self.emit("    ireturn")
            elif ret_type == "bool":
                self.emit("    iconst_0")
                self.emit("    ireturn")
            elif ret_type in ["point", "line", "circle", "polygon"]:
                self.emit("    aconst_null")
                self.emit("    areturn")
            else:
                self.emit("    return")

        self.emit(".end method\n")
        
        self.in_function = old_in_function

    def generate_main(self, ctx: yapis2Parser.ProgramContext):
        self.emit("; ========== Main method ==========")
        self.emit(".method public static main([Ljava/lang/String;)V")
        self.emit("    .limit stack 20")
        self.emit("    .limit locals 100\n")

        self.variables = {}
        self.var_types = {}  
        self.local_counter = 0
        self.max_local_used = 0  
        
        self.emit("    new java/util/Scanner")
        self.emit("    dup")
        self.emit("    getstatic java/lang/System/in Ljava/io/InputStream;")
        self.emit("    invokespecial java/util/Scanner/<init>(Ljava/io/InputStream;)V")
        self.emit("    putstatic Main/scanner Ljava/util/Scanner;")
        self.emit("")

        
        for stmt in self.main_statements:
            self.visit(stmt)

        self.emit("    return")
        self.emit(".end method")

    def visitStatement(self, ctx: yapis2Parser.StatementContext):
        
        if ctx.assignment():
            return self.visitAssignment(ctx.assignment())
        if ctx.variableDecl():
            return self.visitVariableDecl(ctx.variableDecl())
        if ctx.ifStatement():
            return self.visitIfStatement(ctx.ifStatement())
        if ctx.whileStatement():
            return self.visitWhileStatement(ctx.whileStatement())
        if ctx.forStatement():
            return self.visitForStatement(ctx.forStatement())
        if ctx.breakStatement():
            return self.visitBreakStatement(ctx.breakStatement())
        if ctx.returnStatement():
            return self.visitReturnStatement(ctx.returnStatement())
        if ctx.functionCall():
            return self.visitFunctionCall(ctx.functionCall())
        
        return self.visitChildren(ctx)

    def type_to_jvm(self, type_name):
        if type_name == "int":
            return "I"
        elif type_name == "bool":
            return "Z"
        elif type_name == "string":
            return "Ljava/lang/String;"
        elif type_name == "point":
            return "LPoint;"
        elif type_name == "line":
            return "LLine;"
        elif type_name == "circle":
            return "LCircle;"
        elif type_name == "polygon":
            return "LPolygon;"
        return "V"

    def visitAssignment(self, ctx: yapis2Parser.AssignmentContext):
        name = ctx.IDENTIFIER().getText()
        
        
        
        jvm_type = self.infer_type_jvm(ctx.expression())
        
        
        self.visit(ctx.expression())
        
        
        
        if name in self.variables:
            local_idx = self.variables[name]
            existing_type = self.var_types.get(name)
            
            
            
            
            if existing_type != jvm_type:
                
                
                if existing_type in ["I", "Z"] and jvm_type not in ["I", "Z"]:
                    
                    
                    self.emit("    pop")
                    self.emit("    iconst_0")
                    jvm_type = "I"
                elif existing_type not in ["I", "Z"] and jvm_type in ["I", "Z"]:
                    
                    
                    self.emit("    pop")
                    self.emit("    aconst_null")
                    jvm_type = existing_type
                
            
            store_type = existing_type
        else:
            
            local_idx = self.get_local_index(name)
            self.var_types[name] = jvm_type
            store_type = jvm_type
        
        
        if store_type == "I" or store_type == "Z":
            if local_idx < 4:
                self.emit(f"    istore_{local_idx}")
            else:
                self.emit(f"    istore {local_idx}")
        else:
            if local_idx < 4:
                self.emit(f"    astore_{local_idx}")
            else:
                self.emit(f"    astore {local_idx}")

    def visitVariableDecl(self, ctx: yapis2Parser.VariableDeclContext):
        self.visitAssignment(ctx)

    def visitIfStatement(self, ctx: yapis2Parser.IfStatementContext):
        else_label = self.new_label()
        end_label = self.new_label()

        
        self.visit(ctx.expression())
        
        self.emit(f"    ifeq {else_label}")

        
        for stmt in ctx.block(0).statement():
            self.visit(stmt)
        
        
        

        if ctx.block(1):  
            self.emit(f"    goto {end_label}")
            self.emit(f"{else_label}:")
            for stmt in ctx.block(1).statement():
                self.visit(stmt)
            self.emit(f"{end_label}:")
        else:
            
            self.emit(f"{else_label}:")

    def visitWhileStatement(self, ctx: yapis2Parser.WhileStatementContext):
        
        start_label = self.new_label()
        end_label = self.new_label()

        
        self.break_labels_stack.append(end_label)

        self.emit(f"{start_label}:")
        self.visit(ctx.expression())
        self.emit(f"    ifeq {end_label}")

        for stmt in ctx.block().statement():
            self.visit(stmt)

        self.emit(f"    goto {start_label}")
        self.emit(f"{end_label}:")
        
        
        if len(self.break_labels_stack) > 0:
            self.break_labels_stack.pop()

    def visitForStatement(self, ctx: yapis2Parser.ForStatementContext):
        
        var_name = ctx.IDENTIFIER().getText()
        var_idx = self.get_local_index(var_name)
        
        self.var_types[var_name] = "I"

        start_label = self.new_label()
        end_label = self.new_label()

        
        self.break_labels_stack.append(end_label)

        
        self.visit(ctx.expression(0))
        self.emit(f"    istore {var_idx}")

        
        
        self.visit(ctx.expression(1))
        temp_bound_name = f"__for_bound_{var_name}"
        temp_bound_idx = self.get_local_index(temp_bound_name)
        
        self.var_types[temp_bound_name] = "I"
        self.emit(f"    istore {temp_bound_idx}")  

        self.emit(f"{start_label}:")
        self.emit(f"    iload {var_idx}")
        self.emit(f"    iload {temp_bound_idx}")
        self.emit(f"    if_icmpgt {end_label}")

        
        for stmt in ctx.block().statement():
            self.visit(stmt)

        
        if ctx.expression(2):  
            
            self.visit(ctx.expression(2))
            
            self.emit(f"    iload {var_idx}")
            
            self.emit("    iadd")
            
            self.emit(f"    istore {var_idx}")
        else:
            
            self.emit(f"    iinc {var_idx} 1")
        self.emit(f"    goto {start_label}")
        self.emit(f"{end_label}:")
        
        
        if len(self.break_labels_stack) > 0:
            self.break_labels_stack.pop()

    def visitBreakStatement(self, ctx: yapis2Parser.BreakStatementContext):
        
        if len(self.break_labels_stack) > 0:
            
            end_label = self.break_labels_stack[-1]
            self.emit(f"    goto {end_label}")
        else:
            
            self.emit("    return")

    def visitReturnStatement(self, ctx: yapis2Parser.ReturnStatementContext):
        
        self.has_return = True  
        if ctx.expression():
            self.visit(ctx.expression())
            jvm_type = self.infer_type_jvm(ctx.expression())
            if jvm_type == "I" or jvm_type == "Z":
                self.emit("    ireturn")
            else:
                self.emit("    areturn")
        else:
            self.emit("    return")
        

    def visitFunctionCall(self, ctx: yapis2Parser.FunctionCallContext):
        
        if ctx.IDENTIFIER():
            name = ctx.IDENTIFIER().getText()
            
            if name in self.functions:
                param_types, ret_type = self.functions[name]
                
                if ctx.argumentList():
                    for arg in ctx.argumentList().expression():
                        self.visit(arg)
                
                param_sig = "".join([self.type_to_jvm(t) for t in param_types])
                ret_jvm = self.type_to_jvm(ret_type) if ret_type else "V"
                self.emit(f"    invokestatic Main/{name}({param_sig}){ret_jvm}")
            else:
                
                pass
        else:
            
            builtin = ctx.builtInFunction()
            if builtin:
                self.generate_builtin_call(builtin.getText(), ctx.argumentList())

    def get_temp_local_index(self, temp_name):
        
        
        full_name = f"__temp_{temp_name}"
        if full_name not in self.variables:
            self.variables[full_name] = self.local_counter
            
            if "point" in temp_name.lower() or "shape" in temp_name.lower() or "line" in temp_name.lower() or "array" in temp_name.lower() or "p2" in temp_name.lower():
                self.var_types[full_name] = "LPoint;" if "array" not in temp_name.lower() else "[LPoint;"
            else:
                
                self.var_types[full_name] = "I"
            self.max_local_used = max(self.max_local_used, self.local_counter)
            self.local_counter += 1
        return self.variables[full_name]
    
    def generate_builtin_call(self, func_name, arg_list):
        
        if func_name == "read":
            
            
            if arg_list and len(arg_list.expression()) > 0:
                
                self.emit("    getstatic java/lang/System/out Ljava/io/PrintStream;")
                self.visit(arg_list.expression(0))  
                self.emit("    invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V")
            
            self.emit("    getstatic Main/scanner Ljava/util/Scanner;")  
            self.emit("    invokevirtual java/util/Scanner/nextInt()I")
        elif func_name == "write":
            
            if arg_list:
                args = arg_list.expression()
                for i, arg in enumerate(args):
                    
                    self.visit(arg)
                    
                    jvm_type = self.infer_type_jvm(arg)
                    
                    
                    
                    is_last = (i == len(args) - 1)
                    
                    if jvm_type == "I":
                        
                        self.emit("    getstatic java/lang/System/out Ljava/io/PrintStream;")
                        self.emit("    swap")
                        if is_last:
                            self.emit("    invokevirtual java/io/PrintStream/println(I)V")
                        else:
                            self.emit("    invokevirtual java/io/PrintStream/print(I)V")
                    elif jvm_type == "Ljava/lang/String;":
                        
                        self.emit("    getstatic java/lang/System/out Ljava/io/PrintStream;")
                        self.emit("    swap")
                        if is_last:
                            self.emit("    invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V")
                        else:
                            self.emit("    invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V")
                    else:
                        
                        self.emit("    invokevirtual java/lang/Object/toString()Ljava/lang/String;")
                        
                        self.emit("    getstatic java/lang/System/out Ljava/io/PrintStream;")
                        self.emit("    swap")
                        if is_last:
                            self.emit("    invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V")
                        else:
                            self.emit("    invokevirtual java/io/PrintStream/print(Ljava/lang/String;)V")
        elif func_name == "point":
            
            if arg_list and len(arg_list.expression()) == 2:
                args = arg_list.expression()
                
                self.emit("    new Point")
                self.emit("    dup")
                self.visit(args[0])  
                self.visit(args[1])  
                
                self.emit("    invokespecial Point/<init>(II)V")
        elif func_name == "line":
            
            if arg_list and len(arg_list.expression()) == 2:
                args = arg_list.expression()
                self.emit("    new Line")
                self.emit("    dup")
                self.visit(args[0])  
                self.visit(args[1])  
                self.emit("    invokespecial Line/<init>(LPoint;LPoint;)V")
        elif func_name == "circle":
            
            if arg_list and len(arg_list.expression()) == 2:
                args = arg_list.expression()
                self.emit("    new Circle")
                self.emit("    dup")
                self.visit(args[0])  
                self.visit(args[1])  
                self.emit("    invokespecial Circle/<init>(LPoint;I)V")
        elif func_name == "polygon":
            
            if arg_list and len(arg_list.expression()) >= 3:
                args = arg_list.expression()
                num_points = len(args)
                
                self.emit(f"    iconst_{num_points}")
                self.emit("    anewarray Point")
                
                temp_array_idx = self.get_temp_local_index("array")
                self.emit(f"    astore {temp_array_idx}")  
                
                for i, arg in enumerate(args):
                    self.emit(f"    aload {temp_array_idx}")  
                    self.emit(f"    iconst_{i}")  
                    self.visit(arg)  
                    self.emit("    aastore")  
                
                self.emit("    new Polygon")
                self.emit("    dup")
                self.emit(f"    aload {temp_array_idx}")  
                self.emit("    invokespecial Polygon/<init>([LPoint;)V")
            else:
                
                self.emit("    iconst_0")
                self.emit("    anewarray Point")
                self.emit("    new Polygon")
                self.emit("    dup")
                self.emit("    swap")
                self.emit("    invokespecial Polygon/<init>([LPoint;)V")
        elif func_name == "intersection":
            
            
            if arg_list and len(arg_list.expression()) == 2:
                args = arg_list.expression()
                
                self.visit(args[0])  
                self.visit(args[1])  
                
                temp_line2_idx = self.get_temp_local_index("line2")
                self.emit(f"    astore {temp_line2_idx}")  
                
                
                
                self.visit(args[0])  
                self.emit("    getfield Line/p1 LPoint;")
                self.emit("    getfield Point/x I")  
                self.visit(args[0])  
                self.emit("    getfield Line/p2 LPoint;")
                self.emit("    getfield Point/x I")  
                self.emit("    iadd")  
                self.emit("    iconst_2")
                self.emit("    idiv")  
                
                temp_mid1_x_idx = self.get_temp_local_index("mid1_x")
                self.emit(f"    istore {temp_mid1_x_idx}")
                
                
                self.visit(args[0])  
                self.emit("    getfield Line/p1 LPoint;")
                self.emit("    getfield Point/y I")  
                self.visit(args[0])  
                self.emit("    getfield Line/p2 LPoint;")
                self.emit("    getfield Point/y I")  
                self.emit("    iadd")  
                self.emit("    iconst_2")
                self.emit("    idiv")  
                
                temp_mid1_y_idx = self.get_temp_local_index("mid1_y")
                self.emit(f"    istore {temp_mid1_y_idx}")
                
                
                
                self.emit(f"    aload {temp_line2_idx}")  
                self.emit("    getfield Line/p1 LPoint;")
                self.emit("    getfield Point/x I")  
                self.emit(f"    aload {temp_line2_idx}")  
                self.emit("    getfield Line/p2 LPoint;")
                self.emit("    getfield Point/x I")  
                self.emit("    iadd")  
                self.emit("    iconst_2")
                self.emit("    idiv")  
                
                temp_mid2_x_idx = self.get_temp_local_index("mid2_x")
                self.emit(f"    istore {temp_mid2_x_idx}")
                
                
                self.emit(f"    aload {temp_line2_idx}")  
                self.emit("    getfield Line/p1 LPoint;")
                self.emit("    getfield Point/y I")  
                self.emit(f"    aload {temp_line2_idx}")  
                self.emit("    getfield Line/p2 LPoint;")
                self.emit("    getfield Point/y I")  
                self.emit("    iadd")  
                self.emit("    iconst_2")
                self.emit("    idiv")  
                
                temp_mid2_y_idx = self.get_temp_local_index("mid2_y")
                self.emit(f"    istore {temp_mid2_y_idx}")
                
                
                
                self.emit(f"    iload {temp_mid1_x_idx}")  
                self.emit(f"    iload {temp_mid2_x_idx}")  
                self.emit("    iadd")  
                self.emit("    iconst_2")
                self.emit("    idiv")  
                
                temp_final_x_idx = self.get_temp_local_index("final_x")
                self.emit(f"    istore {temp_final_x_idx}")
                
                
                self.emit(f"    iload {temp_mid1_y_idx}")  
                self.emit(f"    iload {temp_mid2_y_idx}")  
                self.emit("    iadd")  
                self.emit("    iconst_2")
                self.emit("    idiv")  
                
                temp_final_y_idx = self.get_temp_local_index("final_y")
                self.emit(f"    istore {temp_final_y_idx}")
                
                
                
                self.emit("    new Point")
                self.emit("    dup")
                self.emit(f"    iload {temp_final_x_idx}")  
                self.emit(f"    iload {temp_final_y_idx}")  
                
                self.emit("    invokespecial Point/<init>(II)V")  
            else:
                
                self.emit("    new Point")
                self.emit("    dup")
                self.emit("    iconst_0")
                self.emit("    iconst_0")
                self.emit("    invokespecial Point/<init>(II)V")
        elif func_name == "inside":
            
            if arg_list and len(arg_list.expression()) == 2:
                args = arg_list.expression()
                
                self.visit(args[0])  
                self.visit(args[1])  
                
                temp_shape_idx = self.get_temp_local_index("shape")
                temp_point_idx = self.get_temp_local_index("point")
                self.emit(f"    astore {temp_shape_idx}")  
                self.emit(f"    astore {temp_point_idx}")  
                
                
                polygon_check_label = self.new_label()
                inside_false_label = self.new_label()
                inside_end_label = self.new_label()
                
                
                self.emit(f"    aload {temp_shape_idx}")  
                self.emit("    instanceof Circle")
                self.emit(f"    ifeq {polygon_check_label}")  
                
                
                self.emit(f"    aload {temp_point_idx}")  
                self.emit("    getfield Point/x I")  
                self.emit(f"    aload {temp_shape_idx}")  
                self.emit("    checkcast Circle")
                self.emit("    getfield Circle/center LPoint;")  
                self.emit("    getfield Point/x I")  
                self.emit("    isub")  
                self.emit("    dup")  
                self.emit("    imul")  
                
                self.emit(f"    aload {temp_point_idx}")  
                self.emit("    getfield Point/y I")  
                self.emit(f"    aload {temp_shape_idx}")  
                self.emit("    checkcast Circle")
                self.emit("    getfield Circle/center LPoint;")  
                self.emit("    getfield Point/y I")  
                self.emit("    isub")  
                self.emit("    dup")  
                self.emit("    imul")  
                self.emit("    iadd")  
                
                self.emit(f"    aload {temp_shape_idx}")  
                self.emit("    checkcast Circle")
                self.emit("    getfield Circle/radius I")  
                self.emit("    dup")  
                self.emit("    imul")  
                
                self.emit("    swap")  
                self.emit("    isub")  
                self.emit(f"    iflt {inside_false_label}")  
                self.emit("    iconst_1")  
                self.emit(f"    goto {inside_end_label}")
                self.emit(f"{polygon_check_label}:")
                
                
                
                
                
                self.emit(f"    aload {temp_shape_idx}")  
                self.emit("    checkcast Polygon")
                self.emit("    getfield Polygon/points [LPoint;")  
                temp_points_idx = self.get_temp_local_index("points_array")
                self.emit(f"    astore {temp_points_idx}")  
                
                
                self.emit(f"    aload {temp_points_idx}")  
                self.emit("    arraylength")  
                temp_len_idx = self.get_temp_local_index("array_len")
                self.emit(f"    istore {temp_len_idx}")  
                self.emit(f"    iload {temp_len_idx}")  
                self.emit(f"    ifle {inside_false_label}")  
                
                
                
                self.emit(f"    aload {temp_points_idx}")
                self.emit("    iconst_0")
                self.emit("    aaload")  
                temp_point_temp_idx = self.get_temp_local_index("point_temp")
                self.emit(f"    astore {temp_point_temp_idx}")  
                
                
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/x I")  
                temp_min_x_idx = self.get_temp_local_index("min_x")
                temp_max_x_idx = self.get_temp_local_index("max_x")
                self.emit(f"    dup")  
                self.emit(f"    istore {temp_min_x_idx}")  
                self.emit(f"    istore {temp_max_x_idx}")  
                
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/y I")  
                temp_min_y_idx = self.get_temp_local_index("min_y")
                temp_max_y_idx = self.get_temp_local_index("max_y")
                self.emit(f"    dup")  
                self.emit(f"    istore {temp_min_y_idx}")  
                self.emit(f"    istore {temp_max_y_idx}")  
                
                
                temp_i_idx = self.get_temp_local_index("loop_i")
                self.emit(f"    iconst_1")
                self.emit(f"    istore {temp_i_idx}")  
                
                loop_start_label = self.new_label()
                loop_end_label = self.new_label()
                self.emit(f"{loop_start_label}:")
                self.emit(f"    iload {temp_i_idx}")  
                self.emit(f"    iload {temp_len_idx}")  
                self.emit(f"    if_icmpge {loop_end_label}")  
                
                
                self.emit(f"    aload {temp_points_idx}")  
                self.emit(f"    iload {temp_i_idx}")  
                self.emit("    aaload")  
                self.emit(f"    astore {temp_point_temp_idx}")  
                
                
                skip_min_x_label = self.new_label()
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/x I")  
                self.emit(f"    iload {temp_min_x_idx}")  
                self.emit(f"    if_icmpge {skip_min_x_label}")  
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/x I")  
                self.emit(f"    istore {temp_min_x_idx}")  
                self.emit(f"{skip_min_x_label}:")
                
                
                skip_max_x_label = self.new_label()
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/x I")  
                self.emit(f"    iload {temp_max_x_idx}")  
                self.emit(f"    if_icmple {skip_max_x_label}")  
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/x I")  
                self.emit(f"    istore {temp_max_x_idx}")  
                self.emit(f"{skip_max_x_label}:")
                
                
                skip_min_y_label = self.new_label()
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/y I")  
                self.emit(f"    iload {temp_min_y_idx}")  
                self.emit(f"    if_icmpge {skip_min_y_label}")  
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/y I")  
                self.emit(f"    istore {temp_min_y_idx}")  
                self.emit(f"{skip_min_y_label}:")
                
                
                skip_max_y_label = self.new_label()
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/y I")  
                self.emit(f"    iload {temp_max_y_idx}")  
                self.emit(f"    if_icmple {skip_max_y_label}")  
                self.emit(f"    aload {temp_point_temp_idx}")
                self.emit("    getfield Point/y I")  
                self.emit(f"    istore {temp_max_y_idx}")  
                self.emit(f"{skip_max_y_label}:")
                
                
                self.emit(f"    iinc {temp_i_idx} 1")
                self.emit(f"    goto {loop_start_label}")
                self.emit(f"{loop_end_label}:")
                
                
                
                
                self.emit(f"    aload {temp_point_idx}")  
                self.emit("    getfield Point/x I")  
                self.emit(f"    iload {temp_min_x_idx}")  
                self.emit(f"    if_icmplt {inside_false_label}")  
                
                
                self.emit(f"    aload {temp_point_idx}")  
                self.emit("    getfield Point/x I")  
                self.emit(f"    iload {temp_max_x_idx}")  
                self.emit(f"    if_icmpgt {inside_false_label}")  
                
                
                self.emit(f"    aload {temp_point_idx}")  
                self.emit("    getfield Point/y I")  
                self.emit(f"    iload {temp_min_y_idx}")  
                self.emit(f"    if_icmplt {inside_false_label}")  
                
                
                self.emit(f"    aload {temp_point_idx}")  
                self.emit("    getfield Point/y I")  
                self.emit(f"    iload {temp_max_y_idx}")  
                self.emit(f"    if_icmpgt {inside_false_label}")  
                
                
                
                self.emit("    iconst_1")  
                self.emit(f"    goto {inside_end_label}")
                self.emit(f"{inside_false_label}:")
                self.emit("    iconst_0")  
                self.emit(f"{inside_end_label}:")
            else:
                
                self.emit("    iconst_0")
        elif func_name == "distance":
            
            if arg_list and len(arg_list.expression()) == 2:
                args = arg_list.expression()
                
                self.visit(args[0])  
                self.visit(args[1])  
                
                
                
                temp_p2_idx = self.get_temp_local_index("p2")
                self.emit(f"    astore {temp_p2_idx}")  
                
                self.emit("    getfield Point/x I")  
                
                self.emit(f"    aload {temp_p2_idx}")  
                self.emit("    getfield Point/x I")  
                
                self.emit("    swap")  
                self.emit("    isub")  
                
                self.emit("    dup")  
                self.emit("    imul")  
                
                self.emit(f"    aload {temp_p2_idx}")  
                self.emit("    getfield Point/y I")  
                
                self.visit(args[0])  
                self.emit("    getfield Point/y I")  
                
                self.emit("    swap")  
                self.emit("    isub")  
                
                self.emit("    dup")  
                self.emit("    imul")  
                
                self.emit("    iadd")  
                
                self.emit("    i2d")  
                self.emit("    invokestatic java/lang/Math/sqrt(D)D")
                self.emit("    d2i")  

    def visitLiteralExpr(self, ctx):
        
        if ctx.literal().INT():
            val = int(ctx.literal().INT().getText())
            if 0 <= val <= 5:
                self.emit(f"    iconst_{val}")
            elif -128 <= val <= 127:
                self.emit(f"    bipush {val}")
            else:
                self.emit(f"    ldc {val}")
        elif ctx.literal().STRING():
            s = ctx.literal().STRING().getText()[1:-1]  
            self.emit(f'    ldc "{s}"')
        elif ctx.literal().BOOL():
            val = ctx.literal().BOOL().getText()
            self.emit(f"    iconst_{1 if val == 'true' else 0}")

    def visitIdentifierExpr(self, ctx):
        
        name = ctx.IDENTIFIER().getText()
        if name in self.variables:
            idx = self.variables[name]
            
            var_type = self.var_types.get(name, "I")  
            if var_type == "I" or var_type == "Z":
                
                if idx < 4:
                    self.emit(f"    iload_{idx}")
                else:
                    self.emit(f"    iload {idx}")
            else:
                
                if idx < 4:
                    self.emit(f"    aload_{idx}")
                else:
                    self.emit(f"    aload {idx}")
        else:
            
            
            self.emit("    iconst_0")

    def visitFunctionCallExpr(self, ctx):
        
        self.visitFunctionCall(ctx.functionCall())

    def visitParenthesizedExpr(self, ctx):
        
        self.visit(ctx.expression())

    def visitCastExpr(self, ctx):
        
        
        self.visit(ctx.expression())

    def visitNotExpr(self, ctx):
        
        self.visit(ctx.expression())
        false_label = self.new_label()
        end_label = self.new_label()
        
        
        self.emit(f"    ifne {false_label}")  
        self.emit("    iconst_1")             
        self.emit(f"    goto {end_label}")
        self.emit(f"{false_label}:")
        self.emit("    iconst_0")             
        self.emit(f"{end_label}:")

    def visitMultiplicativeExpr(self, ctx):
        
        self.visit(ctx.expression(0))
        self.visit(ctx.expression(1))
        op = ctx.op.text
        if op == "*":
            self.emit("    imul")
        elif op == "/":
            self.emit("    idiv")
        elif op == "%":
            self.emit("    irem")

    def visitAdditiveExpr(self, ctx):
        
        self.visit(ctx.expression(0))
        self.visit(ctx.expression(1))
        op = ctx.op.text
        if op == "+":
            self.emit("    iadd")
        elif op == "-":
            self.emit("    isub")

    def visitComparisonExpr(self, ctx):
        
        self.visit(ctx.expression(0))
        self.visit(ctx.expression(1))
        op = ctx.op.text
        false_label = self.new_label()
        end_label = self.new_label()

        
        
        if op == "<":
            self.emit(f"    if_icmpge {false_label}")  
            self.emit("    iconst_1")  
            self.emit(f"    goto {end_label}")
        elif op == ">":
            self.emit(f"    if_icmple {false_label}")  
            self.emit("    iconst_1")  
            self.emit(f"    goto {end_label}")
        elif op == "<=":
            self.emit(f"    if_icmpgt {false_label}")  
            self.emit("    iconst_1")  
            self.emit(f"    goto {end_label}")
        elif op == ">=":
            self.emit(f"    if_icmplt {false_label}")  
            self.emit("    iconst_1")  
            self.emit(f"    goto {end_label}")
        elif op == "==":
            self.emit(f"    if_icmpne {false_label}")  
            self.emit("    iconst_1")  
            self.emit(f"    goto {end_label}")
        elif op == "!=":
            self.emit(f"    if_icmpeq {false_label}")  
            self.emit("    iconst_1")  
            self.emit(f"    goto {end_label}")

        self.emit(f"{false_label}:")
        self.emit("    iconst_0")  
        self.emit(f"{end_label}:")

    def visitLogicalExpr(self, ctx):
        
        op = ctx.op.text
        if op == "&&":
            end_label = self.new_label()
            false_label = self.new_label()
            self.visit(ctx.expression(0))
            self.emit(f"    ifeq {false_label}")
            self.visit(ctx.expression(1))
            self.emit(f"    ifeq {false_label}")
            self.emit("    iconst_1")
            self.emit(f"    goto {end_label}")
            self.emit(f"{false_label}:")
            self.emit("    iconst_0")
            self.emit(f"{end_label}:")
        elif op == "||":
            true_label = self.new_label()
            end_label = self.new_label()
            self.visit(ctx.expression(0))
            self.emit(f"    ifne {true_label}")
            self.visit(ctx.expression(1))
            self.emit(f"    ifne {true_label}")
            self.emit("    iconst_0")
            self.emit(f"    goto {end_label}")
            self.emit(f"{true_label}:")
            self.emit("    iconst_1")
            self.emit(f"{end_label}:")

    def visitMemberAccessExpr(self, ctx):
        
        
        self.visit(ctx.expression())
        field_name = ctx.IDENTIFIER().getText()
        
        
        
        
        
        
        if field_name == "x":
            
            self.emit("    getfield Point/x I")
        elif field_name == "y":
            
            self.emit("    getfield Point/y I")
        elif field_name == "p1":
            
            self.emit("    getfield Line/p1 LPoint;")
        elif field_name == "p2":
            
            self.emit("    getfield Line/p2 LPoint;")
        elif field_name == "center":
            
            self.emit("    getfield Circle/center LPoint;")
        elif field_name == "radius":
            
            self.emit("    getfield Circle/radius I")
        elif field_name == "points":
            
            self.emit("    getfield Polygon/points [LPoint;")
        else:
            
            self.emit("    pop")  
            self.emit("    iconst_0")

    def infer_type_jvm(self, ctx):
        
        if ctx is None:
            return "I"
        
        
        from gen.yapis2Parser import yapis2Parser
        
        
        if isinstance(ctx, yapis2Parser.LiteralExprContext):
            if ctx.literal() and ctx.literal().STRING():
                return "Ljava/lang/String;"
            elif ctx.literal() and ctx.literal().INT():
                return "I"
            elif ctx.literal() and ctx.literal().BOOL():
                return "Z"
        
        
        if isinstance(ctx, yapis2Parser.IdentifierExprContext):
            name = ctx.IDENTIFIER().getText()
            return self.var_types.get(name, "I")
        
        
        if isinstance(ctx, yapis2Parser.FunctionCallExprContext):
            call = ctx.functionCall()
            if call and call.builtInFunction():
                func_name = call.builtInFunction().getText()
                if func_name == "point":
                    return "LPoint;"
                elif func_name == "line":
                    return "LLine;"
                elif func_name == "circle":
                    return "LCircle;"
                elif func_name == "polygon":
                    return "LPolygon;"
                elif func_name == "intersection":
                    return "LPoint;"
                elif func_name == "inside":
                    return "Z"
                elif func_name in ["read", "distance"]:
                    return "I"
            elif call and call.IDENTIFIER():
                
                name = call.IDENTIFIER().getText()
                if name in self.functions:
                    _, ret_type = self.functions[name]
                    if ret_type:
                        return self.type_to_jvm(ret_type)
        
        
        if isinstance(ctx, yapis2Parser.MemberAccessExprContext):
            
            field_name = ctx.IDENTIFIER().getText()
            if field_name in ["x", "y", "radius"]:
                return "I"  
            elif field_name in ["p1", "p2", "center"]:
                return "LPoint;"  
            elif field_name == "points":
                return "[LPoint;"  
        
        
        if isinstance(ctx, yapis2Parser.AdditiveExprContext):
            return "I"
        if isinstance(ctx, yapis2Parser.MultiplicativeExprContext):
            return "I"
        
        
        if isinstance(ctx, yapis2Parser.ComparisonExprContext):
            return "Z"
        
        
        if isinstance(ctx, yapis2Parser.LogicalExprContext):
            return "Z"
        
        
        if isinstance(ctx, yapis2Parser.NotExprContext):
            return "Z"
        
        
        if isinstance(ctx, yapis2Parser.ParenthesizedExprContext):
            return self.infer_type_jvm(ctx.expression())
        
        
        if isinstance(ctx, yapis2Parser.CastExprContext):
            type_name = ctx.type_().getText()
            return self.type_to_jvm(type_name)
        
        
        return "I"


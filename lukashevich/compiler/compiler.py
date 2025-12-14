from antlr4 import *
from parser_code.ExprParserVisitor import ExprParserVisitor
from parser_code.ExprParser import ExprParser


class Compiler(ExprParserVisitor):
    def __init__(self):
        self.methods_code = []
        self.current_il = []
        self.locals_map = {}
        self.local_index = 0
        self.args_map = {}
        self.function_return_types = {}
        self.function_arg_types = {}
        self.current_ret_type = "void"
        self.label_counter = 0
        self.temp_int_index = 0
        self.op_map_il = {
            "+": "add",
            "-": "sub",
            "*": "mul",
            "/": "div",
            ">": "cgt",
            "<": "clt",
        }

    def get_il_code(self):
        header = """
.assembly extern mscorlib {}
.assembly extern ImageLangRuntime {}
.assembly ImageLangApp {}
.module ImageLangApp.exe

.class public auto ansi Program extends [mscorlib]System.Object
{
"""
        methods = "\n".join(self.methods_code)
        footer = "}"
        return f"{header}\n{methods}\n{footer}"

    def _new_label(self):
        self.label_counter += 1
        return f"IL_{self.label_counter:04x}"

    def _get_var_index(self, var_name):
        if var_name not in self.locals_map:
            self.locals_map[var_name] = self.local_index
            self.local_index += 1
        return self.locals_map[var_name]

    def _next_temp_int(self):
        idx = self.temp_int_index
        self.temp_int_index += 1
        return idx

    def _emit_unbox_float(self):
        self.current_il.append("unbox.any [mscorlib]System.Double")

    def _emit_box_float(self):
        self.current_il.append("box [mscorlib]System.Double")

    def _map_type(self, type_str):
        if type_str == "int":
            return "int32"
        if type_str == "float":
            return "float64"
        if type_str == "string":
            return "string"
        if type_str == "image":
            return "class [ImageLangRuntime]ImageLang.SysImage"
        if type_str == "color":
            return "class [ImageLangRuntime]ImageLang.SysColor"
        if type_str == "pixel":
            return "class [ImageLangRuntime]ImageLang.SysPixel"
        return "object"

    # --- Visitor Methods ---

    def visitProgram(self, ctx: ExprParser.ProgramContext):
        for child in ctx.getChildren():
            if isinstance(child, ExprParser.FuncDefContext):
                f_name = child.ID().getText()
                ret_type = "void"
                if child.type_():
                    ret_type = self._map_type(child.type_().getText())
                self.function_return_types[f_name] = ret_type

                arg_types = []
                params_ctx = None
                if hasattr(child, "parameterList") and child.parameterList():
                    params_ctx = child.parameterList().parameter()
                elif hasattr(child, "paramList") and child.paramList():
                    params_ctx = child.paramList().param()

                if params_ctx:
                    for param in params_ctx:
                        arg_types.append(self._map_type(param.type_().getText()))

                self.function_arg_types[f_name] = arg_types

        return self.visitChildren(ctx)

    def visitFuncDef(self, ctx: ExprParser.FuncDefContext):
        func_name = ctx.ID().getText()
        self.current_il = []
        self.locals_map = {}
        self.local_index = 0
        self.args_map = {}
        self.temp_int_index = 0

        il_args = []

        params = []
        if hasattr(ctx, "parameterList") and ctx.parameterList():
            params = ctx.parameterList().parameter()
        elif hasattr(ctx, "paramList") and ctx.paramList():
            params = ctx.paramList().param()

        for i, param in enumerate(params):
            p_type = self._map_type(param.type_().getText())
            p_name = param.ID().getText()
            il_args.append(f"{p_type} {p_name}")
            self.args_map[p_name] = {"index": i, "type": p_type}

        args_str = ", ".join(il_args)

        ret_type = "void"
        if ctx.type_():
            ret_type = self._map_type(ctx.type_().getText())

        self.current_ret_type = ret_type

        method_header = f".method static {ret_type} {func_name}({args_str}) cil managed"

        self.visit(ctx.block())

        objs = ", ".join([f"object V_{i}" for i in range(100)])
        ints = ", ".join([f"int32 L_{i}" for i in range(20)])
        locals_decl = f".locals init ({objs}, {ints})"

        body_code = "\n        ".join(self.current_il)

        if ret_type == "void" and (
            not self.current_il or "ret" not in self.current_il[-1]
        ):
            body_code += "\n        ret"

        entry_point_directive = ""
        if func_name == "main":
            entry_point_directive = ".entrypoint"

        full_method = f"""
    {method_header}
    {{
        {entry_point_directive}
        .maxstack 32
        {locals_decl}
        
        {body_code}
    }}
        """
        self.methods_code.append(full_method)

    def visitReturnStat(self, ctx: ExprParser.ReturnStatContext):
        if ctx.expr():
            self.visit(ctx.expr())
            if self.current_ret_type == "int32":
                self._emit_unbox_float()
                self.current_il.append("conv.i4")
            elif self.current_ret_type == "float64":
                self._emit_unbox_float()

        self.current_il.append("ret")

    def visitBlock(self, ctx: ExprParser.BlockContext):
        for stat in ctx.stat():
            if stat.returnStat():
                self.visit(stat.returnStat())
                continue

            if stat.expr():
                self.visit(stat.expr())
                if self.current_il:
                    last_instr = self.current_il[-1]
                    push_instrs = [
                        "box",
                        "call",
                        "newobj",
                        "ldloc",
                        "ldstr",
                        "ldarg",
                        "ldnull",
                        "ldc",
                    ]

                    should_pop = False
                    for instr in push_instrs:
                        if last_instr.startswith(instr):
                            should_pop = True
                            break

                    if " void " in last_instr:
                        should_pop = False

                    if should_pop:
                        self.current_il.append("pop")
            else:
                self.visit(stat)

    def visitVariableDef(self, ctx: ExprParser.VariableDefContext):
        var_name = ctx.ID().getText()
        idx = self._get_var_index(var_name)
        if ctx.expr():
            self.visit(ctx.expr())
            self.current_il.append(f"stloc V_{idx}")

    def visitAssignment(self, ctx: ExprParser.AssignmentContext):
        var_name = ctx.ID().getText()
        idx = self._get_var_index(var_name)
        self.visit(ctx.expr())
        self.current_il.append(f"stloc V_{idx}")

    def _get_left_atom(self, ctx):
        if hasattr(ctx, "atom") and ctx.atom():
            return ctx.atom()
        if hasattr(ctx, "castExpr") and ctx.castExpr():
            return self._get_left_atom(ctx.castExpr())
        if hasattr(ctx, "multiplicativeExpr") and ctx.multiplicativeExpr():
            return self._get_left_atom(ctx.multiplicativeExpr())
        if hasattr(ctx, "additiveExpr") and ctx.additiveExpr():
            return self._get_left_atom(ctx.additiveExpr())
        if hasattr(ctx, "relationalExpr") and ctx.relationalExpr():
            if len(ctx.children) == 1:
                return self._get_left_atom(ctx.children[0])
        return None

    def visitAssignmentExpr(self, ctx: ExprParser.AssignmentExprContext):
        if ctx.ASSIGN():
            left = ctx.relationalExpr()

            is_property_set = False
            prop_obj = None
            prop_name = None

            curr = left
            valid_structure = True
            while not isinstance(curr, ExprParser.AtomContext):
                if hasattr(curr, "children") and len(curr.children) == 1:
                    curr = curr.children[0]
                elif hasattr(curr, "atom"):
                    curr = curr.atom()
                else:
                    valid_structure = False
                    break

            if valid_structure and isinstance(curr, ExprParser.AtomContext):
                if curr.DOT():
                    is_property_set = True
                    prop_obj = curr.atom()
                    prop_name = curr.ID().getText()

            if is_property_set:
                self.visit(prop_obj)

                class_type = ""
                field_type = "int32"

                if prop_name in ["R", "G", "B"]:
                    class_type = "[ImageLangRuntime]ImageLang.SysColor"
                elif prop_name in ["x", "y"]:
                    class_type = "[ImageLangRuntime]ImageLang.SysPixel"

                self.current_il.append(f"castclass class {class_type}")
                self.visit(ctx.assignmentExpr())
                self._emit_unbox_float()
                self.current_il.append("conv.i4")
                self.current_il.append(f"stfld {field_type} {class_type}::{prop_name}")
                self.current_il.append("ldnull")

            else:
                var_name = left.getText()
                idx = self._get_var_index(var_name)
                self.visit(ctx.assignmentExpr())
                self.current_il.append(f"stloc V_{idx}")
                self.current_il.append(f"ldloc V_{idx}")

        else:
            self.visit(ctx.relationalExpr())

    def visitIfStat(self, ctx: ExprParser.IfStatContext):
        else_label = self._new_label()
        end_label = self._new_label()

        self.visit(ctx.expr())
        self._emit_unbox_float()
        self.current_il.append("ldc.r8 0.0")
        self.current_il.append("ceq")
        self.current_il.append(f"brtrue {else_label}")

        self.visit(ctx.block(0))
        self.current_il.append(f"br {end_label}")

        self.current_il.append(f"{else_label}: nop")
        if ctx.block(1):
            self.visit(ctx.block(1))
        self.current_il.append(f"{end_label}: nop")

    def visitForStat(self, ctx: ExprParser.ForStatContext):
        pixel_var_name = ctx.ID().getText()
        pixel_idx = self._get_var_index(pixel_var_name)

        self.visit(ctx.expr())
        self.current_il.append("castclass [ImageLangRuntime]ImageLang.SysImage")

        img_tmp_idx = self.local_index
        self.local_index += 1
        self.current_il.append(f"stloc V_{img_tmp_idx}")

        x_idx = self._next_temp_int()
        y_idx = self._next_temp_int()
        w_idx = self._next_temp_int()
        h_idx = self._next_temp_int()

        self.current_il.append(f"ldloc V_{img_tmp_idx}")
        self.current_il.append(
            "callvirt instance int32 [ImageLangRuntime]ImageLang.SysImage::get_Width()"
        )
        self.current_il.append(f"stloc L_{w_idx}")

        self.current_il.append(f"ldloc V_{img_tmp_idx}")
        self.current_il.append(
            "callvirt instance int32 [ImageLangRuntime]ImageLang.SysImage::get_Height()"
        )
        self.current_il.append(f"stloc L_{h_idx}")

        self.current_il.append("ldc.i4.0")
        self.current_il.append(f"stloc L_{y_idx}")
        lbl_y_start = self._new_label()
        lbl_y_end = self._new_label()
        self.current_il.append(f"{lbl_y_start}: nop")
        self.current_il.append(f"ldloc L_{y_idx}")
        self.current_il.append(f"ldloc L_{h_idx}")
        self.current_il.append(f"bge {lbl_y_end}")

        self.current_il.append("ldc.i4.0")
        self.current_il.append(f"stloc L_{x_idx}")
        lbl_x_start = self._new_label()
        lbl_x_end = self._new_label()
        self.current_il.append(f"{lbl_x_start}: nop")
        self.current_il.append(f"ldloc L_{x_idx}")
        self.current_il.append(f"ldloc L_{w_idx}")
        self.current_il.append(f"bge {lbl_x_end}")

        self.current_il.append(f"ldloc L_{x_idx}")
        self.current_il.append(f"ldloc L_{y_idx}")
        self.current_il.append(f"ldloc V_{img_tmp_idx}")
        self.current_il.append("castclass [ImageLangRuntime]ImageLang.SysImage")
        self.current_il.append(
            "newobj instance void [ImageLangRuntime]ImageLang.SysPixel::.ctor(int32, int32, class [ImageLangRuntime]ImageLang.SysImage)"
        )
        self.current_il.append(f"stloc V_{pixel_idx}")

        self.visit(ctx.block())

        self.current_il.append(f"ldloc L_{x_idx}")
        self.current_il.append("ldc.i4.1")
        self.current_il.append("add")
        self.current_il.append(f"stloc L_{x_idx}")
        self.current_il.append(f"br {lbl_x_start}")
        self.current_il.append(f"{lbl_x_end}: nop")
        self.current_il.append(f"ldloc L_{y_idx}")
        self.current_il.append("ldc.i4.1")
        self.current_il.append("add")
        self.current_il.append(f"stloc L_{y_idx}")
        self.current_il.append(f"br {lbl_y_start}")
        self.current_il.append(f"{lbl_y_end}: nop")

    def visitAtom(self, ctx: ExprParser.AtomContext):
        if ctx.literal():
            if ctx.literal().INT() or ctx.literal().FLOAT():
                self.current_il.append(f"ldc.r8 {ctx.literal().getText()}")
                self._emit_box_float()
            elif ctx.literal().STRING():
                self.current_il.append(f"ldstr {ctx.literal().STRING().getText()}")
            return

        if ctx.LPAREN() and ctx.expr() and not ctx.atom():
            self.visit(ctx.expr())
            return

        if ctx.ID() and not ctx.DOT() and not ctx.LPAREN() and not ctx.atom():
            var_name = ctx.ID().getText()
            if var_name in self.args_map:
                arg_info = self.args_map[var_name]
                idx = arg_info["index"]
                arg_type = arg_info["type"]

                self.current_il.append(f"ldarg {idx}")

                if arg_type == "int32":
                    self.current_il.append("conv.r8")
                    self._emit_box_float()
                elif arg_type == "float64":
                    self._emit_box_float()
            else:
                idx = self._get_var_index(var_name)
                self.current_il.append(f"ldloc V_{idx}")
            return

        if ctx.constructibleType():
            args = ctx.argumentList().expr()
            for arg in args:
                self.visit(arg)
                self._emit_unbox_float()
                self.current_il.append("conv.i4")
            self.current_il.append(
                "newobj instance void [ImageLangRuntime]ImageLang.SysColor::.ctor(int32, int32, int32)"
            )
            return

        if ctx.atom() and ctx.DOT():
            member_name = ctx.ID().getText()
            self.visit(ctx.atom())

            if member_name in ["R", "G", "B"]:
                self.current_il.append("castclass [ImageLangRuntime]ImageLang.SysColor")
                self.current_il.append(
                    f"ldfld int32 [ImageLangRuntime]ImageLang.SysColor::{member_name}"
                )
                self.current_il.append("conv.r8")
                self._emit_box_float()
            elif member_name in ["width", "height"]:
                self.current_il.append("castclass [ImageLangRuntime]ImageLang.SysImage")
                prop = "get_Width" if member_name == "width" else "get_Height"
                self.current_il.append(
                    f"callvirt instance int32 [ImageLangRuntime]ImageLang.SysImage::{prop}()"
                )
                self.current_il.append("conv.r8")
                self._emit_box_float()
            elif member_name in ["x", "y"]:
                self.current_il.append("castclass [ImageLangRuntime]ImageLang.SysPixel")
                self.current_il.append(
                    f"ldfld int32 [ImageLangRuntime]ImageLang.SysPixel::{member_name}"
                )
                self.current_il.append("conv.r8")
                self._emit_box_float()
            return

        if ctx.atom() and ctx.LPAREN():
            child_atom = ctx.atom()
            if child_atom.DOT():
                method_name = child_atom.ID().getText()

                # SPECIAL HANDLING for get_pixel(x, y)
                if method_name == "get_pixel":
                    # Stack goal: x(int), y(int), image(obj) -> newobj SysPixel

                    # 1. Visit args (x, y)
                    self.visit(ctx.argumentList().expr(0))  # x (Boxed Double)
                    self._emit_unbox_float()
                    self.current_il.append("conv.i4")

                    self.visit(ctx.argumentList().expr(1))  # y (Boxed Double)
                    self._emit_unbox_float()
                    self.current_il.append("conv.i4")

                    # 2. Visit object (image)
                    self.visit(child_atom.atom())
                    self.current_il.append(
                        "castclass [ImageLangRuntime]ImageLang.SysImage"
                    )

                    # 3. Call constructor
                    self.current_il.append(
                        "newobj instance void [ImageLangRuntime]ImageLang.SysPixel::.ctor(int32, int32, class [ImageLangRuntime]ImageLang.SysImage)"
                    )
                    return

                # Standard method handling
                self.visit(child_atom.atom())  # Object

                if method_name == "save":
                    self.current_il.append(
                        "castclass [ImageLangRuntime]ImageLang.SysImage"
                    )
                    self.visit(ctx.argumentList().expr(0))
                    self.current_il.append(
                        "callvirt instance void [ImageLangRuntime]ImageLang.SysImage::Save(string)"
                    )
                elif method_name == "set_color":
                    self.current_il.append(
                        "castclass [ImageLangRuntime]ImageLang.SysPixel"
                    )
                    self.visit(ctx.argumentList().expr(0))
                    self.current_il.append(
                        "castclass [ImageLangRuntime]ImageLang.SysColor"
                    )
                    self.current_il.append(
                        "callvirt instance void [ImageLangRuntime]ImageLang.SysPixel::SetColor(class [ImageLangRuntime]ImageLang.SysColor)"
                    )
                elif method_name == "get_color":
                    self.current_il.append(
                        "castclass [ImageLangRuntime]ImageLang.SysPixel"
                    )
                    self.current_il.append(
                        "callvirt instance class [ImageLangRuntime]ImageLang.SysColor [ImageLangRuntime]ImageLang.SysPixel::GetColor()"
                    )

            else:
                func_name = child_atom.getText()
                if func_name == "print":
                    self.visit(ctx.argumentList().expr(0))
                    self.current_il.append(
                        "call void [ImageLangRuntime]ImageLang.StdLib::Print(object)"
                    )
                elif func_name == "load":
                    self.visit(ctx.argumentList().expr(0))
                    self.current_il.append(
                        "call class [ImageLangRuntime]ImageLang.SysImage [ImageLangRuntime]ImageLang.StdLib::Load(string)"
                    )
                elif func_name == "sqrt":
                    self.visit(ctx.argumentList().expr(0))
                    self._emit_unbox_float()
                    self.current_il.append(
                        "call float64 [mscorlib]System.Math::Sqrt(float64)"
                    )
                    self._emit_box_float()

                elif func_name in self.function_return_types:
                    arg_types = self.function_arg_types[func_name]
                    if ctx.argumentList():
                        for i, arg in enumerate(ctx.argumentList().expr()):
                            self.visit(arg)
                            expected_type = arg_types[i]
                            if expected_type != "object":
                                if expected_type == "int32":
                                    self._emit_unbox_float()
                                    self.current_il.append("conv.i4")
                                elif expected_type == "float64":
                                    self._emit_unbox_float()
                                else:
                                    self.current_il.append(f"castclass {expected_type}")

                    ret_type = self.function_return_types[func_name]
                    sig_args = ", ".join(arg_types)
                    sig = f"({sig_args})"
                    self.current_il.append(f"call {ret_type} Program::{func_name}{sig}")

                    if ret_type == "int32" or ret_type == "float64":
                        self.current_il.append("conv.r8")
                        self._emit_box_float()
            return

    def visitAdditiveExpr(self, ctx: ExprParser.AdditiveExprContext):
        return self._handle_binary_op(ctx, ctx.multiplicativeExpr)

    def visitMultiplicativeExpr(self, ctx: ExprParser.MultiplicativeExprContext):
        return self._handle_binary_op(ctx, ctx.castExpr)

    def visitRelationalExpr(self, ctx: ExprParser.RelationalExprContext):
        return self._handle_binary_op(ctx, ctx.additiveExpr)

    def visitCastExpr(self, ctx: ExprParser.CastExprContext):
        self.visit(ctx.atom())
        if ctx.type_():
            target = ctx.type_().getText()
            if target == "int":
                self._emit_unbox_float()
                self.current_il.append("conv.i4")
                self.current_il.append("conv.r8")
                self._emit_box_float()
            elif target == "float":
                pass

    def _handle_binary_op(self, ctx, child_getter):
        children = child_getter()
        op_tokens = [
            c.getText()
            for c in ctx.getChildren()
            if c.getText() in self.op_map_il or c.getText() == "=="
        ]

        if not op_tokens:
            self.visit(children[0])
            return

        self.visit(children[0])
        if len(op_tokens) > 0 and op_tokens[0] != "==":
            self._emit_unbox_float()

        for i in range(1, len(children)):
            op = op_tokens[i - 1]
            if op == "==":
                self.visit(children[i])
                self.current_il.append(
                    "call bool [ImageLangRuntime]ImageLang.StdLib::Eq(object, object)"
                )
                self.current_il.append("conv.r8")
            else:
                self.visit(children[i])
                self._emit_unbox_float()
                self.current_il.append(self.op_map_il[op])
                if op in [">", "<"]:
                    self.current_il.append("conv.r8")

        self._emit_box_float()

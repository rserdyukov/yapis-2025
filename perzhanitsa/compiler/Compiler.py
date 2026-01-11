# Compiler.py
import dis
import sys
from antlr4 import *
from antlr4.tree.Tree import TerminalNode
from bytecode import Bytecode, Instr, Label, CompilerFlags, UNSET, Compare

# Импортируем BUILTINS, чтобы знать, когда использовать LOAD_GLOBAL
from Runtime import BUILTINS

try:
    from generated.VecLangParser import VecLangParser
    from generated.VecLangVisitor import VecLangVisitor
except ImportError:
    print("Error: Could not find generated ANTLR4 parser files.")
    sys.exit(1)

# ==========================================
# CONSTANTS & UTILS
# ==========================================

def _get_op(name):
    for i, op in enumerate(dis._nb_ops):
        if op[1] == name: return i
    return -1

NB_ADD = _get_op('+')
NB_AND = _get_op('&')
NB_FLOOR_DIVIDE = _get_op('//')
NB_LSHIFT = _get_op('<<')
NB_MATRIX_MULTIPLY = _get_op('@')
NB_MULTIPLY = _get_op('*')
NB_REMAINDER = _get_op('%')
NB_OR = _get_op('|')
NB_POWER = _get_op('**')
NB_SUBTRACT = _get_op('-')
NB_TRUE_DIVIDE = _get_op('/')
NB_XOR = _get_op('^')

CMP_OP_MAP = {
    '==': Compare.EQ, '!=': Compare.NE, '<': Compare.LT,
    '<=': Compare.LE, '>': Compare.GT, '>=': Compare.GE,
}

def dump_bytecode(bc: Bytecode, context_name="unknown"):
    print(f"\n{'=' * 20} DEBUG: BYTECODE DUMP FOR [{context_name}] {'=' * 20}")
    try:
        for idx, instr in enumerate(list(bc)):
            if isinstance(instr, Label):
                print(f"{idx:03}  Label()")
            else:
                arg = str(instr.arg) if instr.arg is not UNSET else ""
                print(f"{idx:03}  {instr.name:<25} {arg}")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"Error dumping bytecode: {e}")


# ==========================================
# COMPILER VISITOR
# ==========================================

class CompilerVisitor(VecLangVisitor):
    def __init__(self):
        self.scopes = [{'type': 'module', 'vars': {}}]
        self.bc = None
        self.current_function_locals = []

    def safe_visit(self, node):
        if node is not None: self.visit(node)

    def current_scope(self):
        return self.scopes[-1]

    def is_function_scope(self):
        return self.current_scope()['type'] == 'func'

    def is_ref(self, name):
        for scope in reversed(self.scopes):
            if name in scope['vars']: return scope['vars'][name]
        return False

    def mark_variable(self, name, is_ref=False):
        self.current_scope()['vars'][name] = is_ref

    def emit_load_variable(self, name):
        if name in BUILTINS or name == "__name__":
            if self.is_function_scope():
                self.bc.append(Instr("LOAD_GLOBAL", (False, name)))
            else:
                self.bc.append(Instr("LOAD_NAME", name))
        elif self.is_function_scope():
            if name in self.current_function_locals:
                self.bc.append(Instr("LOAD_FAST", name))
            else:
                self.bc.append(Instr("LOAD_GLOBAL", (False, name)))
        else:
            self.bc.append(Instr("LOAD_NAME", name))

    def emit_load_for_call(self, name):
        self.bc.append(Instr("PUSH_NULL"))
        self.emit_load_variable(name)

    def emit_store(self, name):
        if self.is_function_scope():
            if name not in self.current_function_locals:
                self.current_function_locals.append(name)
                self.bc.varnames = list(self.current_function_locals)
            self.bc.append(Instr("STORE_FAST", name))
        else:
            self.bc.append(Instr("STORE_NAME", name))

    def compile(self, tree, filename="<string>"):
        self.bc = Bytecode()
        self.bc.filename = filename
        self.bc.append(Instr("RESUME", 0))
        self.safe_visit(tree)
        self.bc.append(Instr("LOAD_CONST", None))
        self.bc.append(Instr("RETURN_VALUE"))
        return self.bc.to_code()

    # --- AST Visitors ---
    def visitProgram(self, ctx):
        for child in ctx.children:
            if isinstance(child, (VecLangParser.StatementContext, VecLangParser.FunctionDeclContext)): self.visit(child)

    def visitStatement(self, ctx):
        return self.visitChildren(ctx)

    def visitCompound_statement(self, ctx):
        return self.visitChildren(ctx)

    def visitSimple_statement(self, ctx):
        if ctx.assign_statement():
            self.visit(ctx.assign_statement())
        elif ctx.call_func():
            self.visit(ctx.call_func())
            self.bc.append(Instr("POP_TOP"))
        elif ctx.printStatement():
            self.visit(ctx.printStatement())
        elif ctx.writeStatement():
            self.visit(ctx.writeStatement())
        elif ctx.raiseStatement():
            self.visit(ctx.raiseStatement())
        elif ctx.expression():
            self.visit(ctx.expression())
            self.bc.append(Instr("POP_TOP"))

        # Добавьте этот метод в класс CompilerVisitor (например, после visitIfStatement)

    def visitSwitchStatement(self, ctx):
        end_label = Label()

        # ВАЖНО: Получаем ВСЕ выражения из конструкции switch
        # ctx.expression() возвращает список [switch_expr, case_expr_1, case_expr_2, ...]
        all_exprs = ctx.expression()

        # 1. Вычисляем выражение switch (самый первый элемент списка)
        switch_cond = all_exprs[0]
        self.safe_visit(switch_cond)

        # Получаем токены CASE и списки инструкций
        cases = ctx.CASE()
        statement_lists = ctx.statement_list()

        # Выражения для case начинаются со 2-го элемента (индекс 1)
        case_expr_values = all_exprs[1:]

        # Проходим по всем case
        for i in range(len(cases)):
            next_case_label = Label()

            # 2. Дублируем значение switch на стеке
            self.bc.append(Instr("COPY", 1))

            # 3. Вычисляем значение текущего case
            # Берем выражение из подготовленного среза
            self.safe_visit(case_expr_values[i])

            # 4. Сравниваем (EQ)
            self.bc.append(Instr("COMPARE_OP", Compare.EQ))

            # 5. Если False, прыгаем к следующему case
            self.bc.append(Instr("POP_JUMP_IF_FALSE", next_case_label))

            # --- Ветка MATCH (Совпадение) ---
            self.bc.append(Instr("POP_TOP"))  # Удаляем SwitchVal

            # Выполняем тело case
            self.safe_visit(statement_lists[i])

            # Выход из switch
            self.bc.append(Instr("JUMP_FORWARD", end_label))

            # --- Метка следующего case ---
            self.bc.append(next_case_label)

        # Обработка DEFAULT
        # Если дошли сюда, на стеке все еще лежит SwitchVal. Удаляем его.
        self.bc.append(Instr("POP_TOP"))

        if ctx.DEFAULT():
            # Default блок всегда последний в списке statement_list
            self.safe_visit(statement_lists[-1])

        # Метка выхода из switch
        self.bc.append(end_label)

    def visitAssign_statement(self, ctx):
        var_name = ctx.ID().getText()
        is_decl_ref = ctx.REF() is not None
        already_ref = self.is_ref(var_name)
        if is_decl_ref:
            if already_ref:
                self.safe_visit(ctx.expression())
                self.emit_load_variable(var_name)
                self.bc.append(Instr("STORE_ATTR", "value"))
            else:
                self.emit_load_for_call("Ref")
                self.safe_visit(ctx.expression())
                self.bc.append(Instr("CALL", 1))
                self.emit_store(var_name)
                self.mark_variable(var_name, is_ref=True)
        elif already_ref:
            self.safe_visit(ctx.expression())
            self.emit_load_variable(var_name)
            self.bc.append(Instr("STORE_ATTR", "value"))
        else:
            self.safe_visit(ctx.expression())
            self.emit_store(var_name)
            self.mark_variable(var_name, is_ref=False)

    def visitPrintStatement(self, ctx):
        self.emit_load_for_call("print")
        self.safe_visit(ctx.expression())
        self.bc.append(Instr("CALL", 1))
        self.bc.append(Instr("POP_TOP"))

    def visitWriteStatement(self, ctx):
        self.visitPrintStatement(ctx)

    def visitRaiseStatement(self, ctx):
        self.emit_load_variable(ctx.ID().getText())
        self.bc.append(Instr("RAISE_VARARGS", 1))

    def visitIfStatement(self, ctx):
        lbl_else, lbl_end = Label(), Label()
        self.safe_visit(ctx.expression())
        self.bc.append(Instr("POP_JUMP_IF_FALSE", lbl_else))
        self.safe_visit(ctx.statement_list(0))
        self.bc.append(Instr("JUMP_FORWARD", lbl_end))
        self.bc.append(lbl_else)
        if ctx.ELSE(): self.safe_visit(ctx.statement_list(1))
        self.bc.append(lbl_end)

    def visitWhileStatement(self, ctx):
        lbl_start, lbl_end = Label(), Label()
        self.bc.append(lbl_start)
        self.safe_visit(ctx.expression())
        self.bc.append(Instr("POP_JUMP_IF_FALSE", lbl_end))
        self.safe_visit(ctx.statement_list())
        self.bc.append(Instr("JUMP_BACKWARD", lbl_start))
        self.bc.append(lbl_end)

    def visitForStatement(self, ctx):
        iter_name = ctx.ID().getText()
        self.safe_visit(ctx.expression())
        self.bc.append(Instr("GET_ITER"))
        lbl_start, lbl_end = Label(), Label()
        self.bc.append(lbl_start)
        self.bc.append(Instr("FOR_ITER", lbl_end))
        self.emit_store(iter_name)
        self.mark_variable(iter_name, False)
        self.safe_visit(ctx.statement_list())
        self.bc.append(Instr("JUMP_BACKWARD", lbl_start))
        self.bc.append(lbl_end)

    def visitFunctionDecl(self, ctx):
        func_name = ctx.ID().getText()
        parent_bc = self.bc

        self.bc = Bytecode()
        self.bc.name = func_name
        self.bc.filename = parent_bc.filename
        self.current_function_locals = []
        self.bc.varnames = []
        self.bc.argcount = 0
        self.bc.flags = CompilerFlags.OPTIMIZED | CompilerFlags.NEWLOCALS | CompilerFlags.NOFREE
        self.scopes.append({'type': 'func', 'vars': {}})

        if ctx.parameterList():
            children = ctx.parameterList().children
            count = len(children)
            i = 0
            while i < count:
                child = children[i]
                if isinstance(child, TerminalNode):
                    t = child.getSymbol().type
                    if t == VecLangParser.COMMA:
                        i += 1; continue
                    is_ref = False
                    if t == VecLangParser.REF:
                        is_ref = True; i += 1
                    if i < count:
                        node = children[i]
                        if isinstance(node, TerminalNode) and node.getSymbol().type == VecLangParser.ID:
                            pname = node.getText()
                            self.current_function_locals.append(pname)
                            self.bc.argcount += 1
                            self.mark_variable(pname, is_ref=is_ref)
                i += 1

        self.bc.varnames = list(self.current_function_locals)
        self.bc.append(Instr("RESUME", 0))

        for idx in range(self.bc.argcount):
            arg_name = self.bc.varnames[idx]
            self.bc.append(Instr("LOAD_FAST", arg_name))
            self.bc.append(Instr("POP_TOP"))

        self.safe_visit(ctx.statement_list())
        self.bc.append(Instr("LOAD_CONST", None))
        self.bc.append(Instr("RETURN_VALUE"))

        try:
            func_code = self.bc.to_code()
        except Exception as e:
            print(f"FATAL ERROR compiling function '{func_name}': {e}")
            dump_bytecode(self.bc, func_name)
            raise

        self.scopes.pop()
        self.bc = parent_bc
        self.current_function_locals = []

        self.bc.append(Instr("LOAD_CONST", func_code))
        self.bc.append(Instr("MAKE_FUNCTION", 0))
        self.emit_store(func_name)

    def visitCall_func(self, ctx):
        self.emit_load_for_call(ctx.ID().getText())
        self.processArguments(ctx.args_list())

    def visitLiteral(self, ctx):
        txt = ctx.getText()
        if ctx.INT(): self.bc.append(Instr("LOAD_CONST", int(txt)))
        elif ctx.FLOAT(): self.bc.append(Instr("LOAD_CONST", float(txt)))
        elif ctx.STRING(): self.bc.append(Instr("LOAD_CONST", txt.strip('"')))
        elif ctx.TRUE(): self.bc.append(Instr("LOAD_CONST", True))
        elif ctx.FALSE(): self.bc.append(Instr("LOAD_CONST", False))
        elif ctx.vectorLiteral(): self.visitVectorLiteral(ctx.vectorLiteral())
        elif ctx.matrixLiteral(): self.visitMatrixLiteral(ctx.matrixLiteral())

    def visitVectorLiteral(self, ctx):
        self.emit_load_for_call("vector")
        exprs = ctx.expression()
        for e in exprs: self.safe_visit(e)
        self.bc.append(Instr("CALL", len(exprs)))

    def visitMatrixLiteral(self, ctx):
        self.emit_load_for_call("matrix")
        rows = ctx.row()
        if rows:
            for r in rows:
                exprs = r.expression()
                for e in exprs: self.safe_visit(e)
                self.bc.append(Instr("BUILD_LIST", len(exprs)))
            self.bc.append(Instr("BUILD_LIST", len(rows)))
        else:
            exprs = ctx.expression()
            for e in exprs: self.safe_visit(e)
            self.bc.append(Instr("BUILD_LIST", len(exprs)))
        self.bc.append(Instr("CALL", 1))

    def visitAdditiveExpr(self, ctx):
        if len(ctx.children) == 1: self.safe_visit(ctx.children[0]); return
        self.safe_visit(ctx.children[0])
        for i in range(1, len(ctx.children), 2):
            op = ctx.children[i].getText()
            self.safe_visit(ctx.children[i + 1])
            self.bc.append(Instr("BINARY_OP", NB_ADD if op == '+' else NB_SUBTRACT))

    def visitMultiplicativeExpr(self, ctx):
        if len(ctx.children) == 1: self.safe_visit(ctx.children[0]); return
        self.safe_visit(ctx.children[0])
        for i in range(1, len(ctx.children), 2):
            op = ctx.children[i].getText()
            self.safe_visit(ctx.children[i + 1])
            code = NB_MULTIPLY if op == '*' else NB_TRUE_DIVIDE if op == '/' else NB_REMAINDER
            self.bc.append(Instr("BINARY_OP", code))

    def visitUnaryExpr(self, ctx):
        if ctx.PIPE():
            self.emit_load_for_call("_rt_norm")
            self.safe_visit(ctx.expression())
            self.bc.append(Instr("CALL", 1))
        elif ctx.getChildCount() > 1:
            op = ctx.getChild(0).getText()
            self.safe_visit(ctx.unaryExpr())
            self.bc.append(Instr("UNARY_NEGATIVE" if op == '-' else "UNARY_POSITIVE"))
        else:
            self.safe_visit(ctx.postfixExpr())

    def visitPostfixExpr(self, ctx):
        self.safe_visit(ctx.primary())
        idx = 1
        count = ctx.getChildCount()
        while idx < count:
            child = ctx.getChild(idx)
            if isinstance(child, TerminalNode):
                t = child.getSymbol().type
                if t == VecLangParser.DOT:
                    attr = ctx.getChild(idx + 1).getText()
                    self.bc.append(Instr("LOAD_ATTR", (False, attr)))
                    idx += 2
                elif t == VecLangParser.OPEN_BRACKET:
                    self.safe_visit(ctx.getChild(idx + 1))
                    self.bc.append(Instr("BINARY_SUBSCR"))
                    idx += 3
                elif t == VecLangParser.OPEN_PAREN:
                    self.bc.append(Instr("PUSH_NULL"))
                    self.bc.append(Instr("SWAP", 2))
                    next_node = ctx.getChild(idx + 1)
                    if isinstance(next_node, TerminalNode) and next_node.getSymbol().type == VecLangParser.CLOSE_PAREN:
                        self.bc.append(Instr("CALL", 0))
                        idx += 2
                    else:
                        self.processArguments(next_node)
                        idx += 3
                else:
                    idx += 1
            else:
                idx += 1

    def processArguments(self, arg_list_ctx):
        if arg_list_ctx is None:
            self.bc.append(Instr("CALL", 0))
            return

        kw = []
        cnt = 0
        if hasattr(arg_list_ctx, 'argument'):
            args = arg_list_ctx.argument()
            if not isinstance(args, list): args = [args]

            for arg in args:
                if arg.ASSIGN():
                    kw.append(arg.ID().getText())
                    self.safe_visit(arg.expression())
                else:
                    self.safe_visit(arg.expression())
                    cnt += 1
        elif hasattr(arg_list_ctx, 'expression'):
            exprs = arg_list_ctx.expression()
            if not isinstance(exprs, list): exprs = [exprs]
            for e in exprs:
                self.safe_visit(e)
                cnt += 1

        if kw:
            self.bc.append(Instr("KW_NAMES", tuple(kw)))
        self.bc.append(Instr("CALL", cnt + len(kw)))

    def visitPrimary(self, ctx):
        if ctx.MATRIX() or (ctx.start.text == 'matrix'):
            self.visitKeywordCtor("matrix", ctx.argumentList())
            return
        if ctx.VECTOR() or (ctx.start.text == 'vector'):
            self.visitKeywordCtor("vector", ctx.argumentList())
            return

        # Добавлено для read() как выражения
        if ctx.READ():
            self.emit_load_for_call("read")
            self.bc.append(Instr("CALL", 0))
            return

        if ctx.ID():
            self.emit_load_variable(ctx.ID().getText())
        elif ctx.OPEN_PAREN():
            self.safe_visit(ctx.expression())
        elif ctx.literal():
            self.safe_visit(ctx.literal())
        elif ctx.call_func():
            self.safe_visit(ctx.call_func())

    def visitKeywordCtor(self, name, args_ctx):
        self.emit_load_for_call(name)
        self.processArguments(args_ctx)

    def visitLogicalExpr(self, ctx):
        if len(ctx.children) == 1: self.safe_visit(ctx.children[0]); return
        self.safe_visit(ctx.children[0])
        for i in range(1, len(ctx.children), 2):
            op = ctx.children[i].getText()
            self.safe_visit(ctx.children[i + 1])
            code = NB_AND if op == 'and' else NB_OR
            self.bc.append(Instr("BINARY_OP", code))

    def visitEqualityExpr(self, ctx):
        if len(ctx.children) == 1: self.safe_visit(ctx.children[0]); return
        self.safe_visit(ctx.children[0])
        for i in range(1, len(ctx.children), 2):
            self.safe_visit(ctx.children[i + 1])
            self.bc.append(Instr("COMPARE_OP", CMP_OP_MAP.get(ctx.children[i].getText(), Compare.EQ)))

    def visitRelationalExpr(self, ctx):
        if len(ctx.children) == 1: self.safe_visit(ctx.children[0]); return
        self.safe_visit(ctx.children[0])
        for i in range(1, len(ctx.children), 2):
            self.safe_visit(ctx.children[i + 1])
            self.bc.append(Instr("COMPARE_OP", CMP_OP_MAP.get(ctx.children[i].getText(), Compare.LT)))
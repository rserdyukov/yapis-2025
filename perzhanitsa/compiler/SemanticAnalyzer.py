from antlr4 import *
from generated.VecLangParser import VecLangParser
from generated.VecLangLexer import VecLangLexer
from antlr4.tree.Tree import TerminalNodeImpl
from enum import Enum
from antlr4 import ParseTreeVisitor


# =========================================================
# SYMBOLS & SCOPES
# =========================================================

class SymbolType(Enum):
    VARIABLE = "VARIABLE"
    FUNCTION = "FUNCTION"
    PARAMETER = "PARAMETER"


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.symbols = {}

    def add(self, name, sym_type, data_type, is_ref=False, line=None):
        self.symbols[name] = {
            "sym_type": sym_type,
            "data_type": data_type,
            "is_ref": is_ref,
            "line": line
        }

    def lookup(self, name):
        scope = self
        while scope:
            if name in scope.symbols:
                return scope.symbols[name]
            scope = scope.parent
        return None


# =========================================================
# SEMANTIC ANALYZER
# =========================================================

class SemanticAnalyzer(ParseTreeVisitor):
    def __init__(self):
        super().__init__()
        self.global_scope = Scope()
        self.current_scope = self.global_scope
        self.functions = {}
        self.errors = []

        # --- Registration of built-in functions ---

        # len(obj) -> int
        self.functions["len"] = {
            "params": [{"name": "arg1", "type": "auto", "is_ref": False}],
            "return": "int"
        }

        # range(limit) -> vector (sequence of numbers)
        self.functions["range"] = {
            "params": [{"name": "limit", "type": "int", "is_ref": False}],
            "return": "vector"
        }

        # print(val) -> void (accepts auto)
        self.functions["print"] = {
            "params": [{"name": "value", "type": "auto", "is_ref": False}],
            "return": "void"
        }

        # Register function names in the global scope
        for fname in self.functions:
            self.global_scope.add(fname, SymbolType.FUNCTION, "function", line=0)

        # --------------------------------------

    # -----------------------------------------------------
    # UTILS
    # -----------------------------------------------------

    def error(self, msg, line):
        self.errors.append({'line': line, 'msg': msg})

    def enter_scope(self):
        self.current_scope = Scope(self.current_scope)

    def exit_scope(self):
        self.current_scope = self.current_scope.parent

    # -----------------------------------------------------
    # TYPE CHECKING
    # -----------------------------------------------------

    def compatible(self, t1, t2, op):
        numeric = ["int", "float"]
        containers = ["vector", "matrix"]

        # Allow auto, as the type might not be inferred yet
        if t1 == "auto" or t2 == "auto": return True

        # Logical operations require bool or int
        if op in ["and", "or"]:
            return (t1 in ["bool", "int", "auto"]) and (t2 in ["bool", "int", "auto"])

        if t1 == t2: return True
        if t1 in numeric and t2 in numeric: return True

        # Fixed comparison: op is a string, not a list
        if op == "*":
            if t1 == "vector" and t2 == "vector": return True
            if t1 == "matrix" and t2 == "matrix": return True
            if t1 in numeric and t2 in containers: return True
            if t2 in numeric and t1 in containers: return True

            # !!! ADDED: Allow Matrix * Vector and Vector * Matrix multiplication !!!
            if (t1 == "matrix" and t2 == "vector") or (t1 == "vector" and t2 == "matrix"):
                return True

        if op in ["+", "-"]:
            if t1 == "vector" and t2 in ["vector",
                                         "matrix"]: return True  # Logic might depend on your math rules
            if t1 == "matrix" and t2 == "matrix": return True
            # Allow vector addition/subtraction
            if t1 == "vector" and t2 == "vector": return True
            # You might want to forbid Scalar + Vector, but if not:
            if t1 in containers and t2 in numeric: return True

        return False

    # -----------------------------------------------------
    # PROGRAM & FUNCTIONS
    # -----------------------------------------------------

    def visitProgram(self, ctx):
        for child in ctx.children:
            if isinstance(child, VecLangParser.FunctionDeclContext):
                self.visit(child)
        for child in ctx.children:
            if not isinstance(child, VecLangParser.FunctionDeclContext):
                self.visit(child)

    def visitFunctionDecl(self, ctx):
        name = ctx.ID().getText()
        params = []
        if ctx.parameterList():
            ref_count = len(ctx.parameterList().REF())
            ids = ctx.parameterList().ID()
            for i, pid in enumerate(ids):
                pname = pid.getText()
                params.append({
                    "name": pname,
                    "type": "auto",  # Could make type inference logic from name more complex
                    "is_ref": i < ref_count
                })

        self.functions[name] = {"params": params, "return": "auto"}
        self.enter_scope()
        for p in params:
            self.current_scope.add(p["name"], SymbolType.PARAMETER, p["type"], p["is_ref"], ctx.start.line)
        self.visit(ctx.statement_list())
        self.exit_scope()

    # -----------------------------------------------------
    # STATEMENTS
    # -----------------------------------------------------

    def visitAssign_statement(self, ctx):
        name = ctx.ID().getText()
        expr_type = self.visit(ctx.expression())
        sym = self.current_scope.lookup(name)
        if sym:
            sym["data_type"] = expr_type
        else:
            self.current_scope.add(name, SymbolType.VARIABLE, expr_type, ctx.REF() is not None, ctx.start.line)
        return expr_type

    def visitIfStatement(self, ctx):
        cond = self.visit(ctx.expression())
        # Allow int in condition (like in C/Python)
        if cond not in ["bool", "auto", "int"]:
            self.error(f"If condition must be boolean or int, got: {cond}", ctx.start.line)
        self.visit(ctx.statement_list(0))
        if ctx.ELSE():
            self.visit(ctx.statement_list(1))

        # -----------------------------------------------------
        # LOGICAL & RELATIONAL EXPRESSIONS
        # -----------------------------------------------------

    def visitLogicalExpr(self, ctx):
            # Handle AND, OR
            left = self.visit(ctx.equalityExpr(0))

            # If there are operators (e.g., a or b)
            for i in range(1, len(ctx.equalityExpr())):
                right = self.visit(ctx.equalityExpr(i))
                # Logical operators require bool (or int, like in C)
                # Simplified: require operands to be castable to bool
                if left not in ["bool", "int", "auto"] or right not in ["bool", "int", "auto"]:
                    self.error(f"Logical operations require bool/int, got: {left} and {right}", ctx.start.line)

                # Result of logical operation is always bool
                left = "bool"

            return left

    def visitEqualityExpr(self, ctx):
            # Handle ==, !=
            left = self.visit(ctx.relationalExpr(0))

            for i in range(1, len(ctx.relationalExpr())):
                right = self.visit(ctx.relationalExpr(i))
                op = ctx.getChild(i * 2 - 1).getText()

                if not self.compatible(left, right, op):
                    self.error(f"Incompatible types for comparison: {left} and {right}", ctx.start.line)

                # !!! IMPORTANT: Comparison result is always bool !!!
                left = "bool"

            return left

    def visitRelationalExpr(self, ctx):
            # Handle <, >, <=, >=
            left = self.visit(ctx.additiveExpr(0))

            for i in range(1, len(ctx.additiveExpr())):
                right = self.visit(ctx.additiveExpr(i))
                op = ctx.getChild(i * 2 - 1).getText()

                # Usually only numbers can be compared for greater/less
                numeric = ["int", "float", "auto"]
                if (left not in numeric or right not in numeric) and (left != right):
                    self.error(f"Invalid comparison {left} {op} {right}", ctx.start.line)

                # Comparison result is always bool
                left = "bool"

            return left

    # --- ADDED METHOD FOR FOR LOOP ---
    def visitForStatement(self, ctx):
        # Syntax: for ID in expression : statement_list

        iter_var_name = ctx.ID().getText()

        # 1. Check what we iterate over (range(3) returns 'vector')
        iterable_type = self.visit(ctx.expression())

        if iterable_type not in ["vector", "matrix","int" ,"auto"]:
            self.error(f"Cannot iterate over type '{iterable_type}'", ctx.start.line)

        # 2. Register loop variable (i) in current scope
        # range usually gives int, but vector might contain float. Set auto or int.
        # To not block print(i), assume int.
        self.current_scope.add(iter_var_name, SymbolType.VARIABLE, "int", is_ref=False, line=ctx.start.line)

        # 3. Check loop body
        self.visit(ctx.statement_list())

    # ------------------------------------
    def visitAdditiveExpr(self, ctx):
        # Visit left operand (multiplicativeExpr)
        left = self.visit(ctx.multiplicativeExpr(0))

        # Iterate through all right operands
        for i in range(1, len(ctx.multiplicativeExpr())):
            right = self.visit(ctx.multiplicativeExpr(i))
            # Get operator (+ or -)
            op = ctx.getChild(i * 2 - 1).getText()

            # Check compatibility
            if not self.compatible(left, right, op):
                self.error(f"Incompatible types {left} {op} {right}", ctx.start.line)

            # Result type inference logic for + and -
            if left == "string" and right == "string" and op == "+":
                left = "string"
            elif left == "vector" and right == "vector":
                left = "vector"
            elif left == "matrix" and right == "matrix":
                left = "matrix"
            elif left in ["int", "float"] and right in ["int", "float"]:
                # Simple logic: if float exists, result is float
                left = "float" if "float" in [left, right] else "int"
            else:
                # If types differ but are compatible (e.g. auto), keep auto or left type
                left = "auto" if "auto" in [left, right] else left

        return left

    def visitMultiplicativeExpr(self, ctx):
        left = self.visit(ctx.unaryExpr(0))
        for i in range(1, len(ctx.unaryExpr())):
            right = self.visit(ctx.unaryExpr(i))
            op = ctx.getChild(i * 2 - 1).getText()

            if not self.compatible(left, right, op):
                self.error(f"Incompatible types {left} {op} {right}", ctx.start.line)

            # Result type logic
            if op == "*":
                if left == "vector" and right == "vector":
                    left = "float"  # Dot product
                elif (left == "matrix" and right == "vector") or (left == "vector" and right == "matrix"):
                    # Matrix multiplication by vector yields vector
                    left = "vector"
                elif left == "matrix" and right == "matrix":
                    left = "matrix"
                elif "matrix" in [left, right]:
                    # Scalar * Matrix = Matrix
                    left = "matrix"
                elif "vector" in [left, right]:
                    # Scalar * Vector = Vector
                    left = "vector"
                else:
                    # int * int, float * float, etc.
                    left = "float" if "float" in [left, right] else "int"

            elif op == "/":
                # Division always returns type of left operand (Vector / 2 -> Vector)
                # Or float if dividing numbers
                if left in ["vector", "matrix"]:
                    pass  # type remains the same
                else:
                    left = "float"  # 5 / 2 -> float

            elif op == "%":
                left = "int"

        return left

    def visitUnaryExpr(self, ctx):
        if ctx.PIPE():
            self.visit(ctx.expression())
            return "float"
        return self.visitChildren(ctx)

    def visitPrimary(self, ctx):
        if ctx.ID():
            name = ctx.ID().getText()
            if name == "__name__": return "string"
            sym = self.current_scope.lookup(name)
            if not sym:
                self.error(f"Undeclared variable: {name}", ctx.start.line)
                return "auto"
            return sym["data_type"]
        if ctx.literal(): return self.visit(ctx.literal())
        if ctx.call_func(): return self.visit(ctx.call_func())
        return "auto"

    def visitCall_func(self, ctx):
        name = ctx.ID().getText()
        if name in ["matrix", "vector"]: return name

        args = []
        if ctx.args_list():
            args = ctx.args_list().expression()

        # Check built-in functions
        if name not in self.functions:
            self.error(f"Function '{name}' is not declared", ctx.start.line)
            return "auto"

        fn = self.functions[name]

        # For print, we could make an exception on arg count,
        # but in current implementation range and print are strictly defined in __init__.
        # If print is called with 1 argument, check will pass.

        if len(args) != len(fn["params"]):
            self.error(f"Function '{name}' expects {len(fn['params'])} arguments", ctx.start.line)

        for i, arg in enumerate(args):
            if i >= len(fn["params"]): break
            at = self.visit(arg)
            pt = fn["params"][i]["type"]
            if not self.compatible(at, pt, "="):
                self.error(f"Invalid argument type {i + 1} for function {name}: expected {pt}, got {at}", ctx.start.line)

        return fn["return"]

    def visitLiteral(self, ctx):
        if ctx.STRING(): return "string"
        if ctx.INT(): return "int"
        if ctx.FLOAT(): return "float"
        if ctx.TRUE() or ctx.FALSE(): return "bool"
        if ctx.vectorLiteral(): return "vector"
        if ctx.matrixLiteral(): return "matrix"
        return "auto"

    def visitChildren(self, ctx):
        result = "auto"
        for c in ctx.children or []:
            if not isinstance(c, TerminalNodeImpl):
                result = self.visit(c)
        return result
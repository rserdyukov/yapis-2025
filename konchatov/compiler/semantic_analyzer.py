# semantic_analyzer.py
from antlr4 import *
from XMLlangLexer import XMLlangLexer
from XMLlangParser import XMLlangParser
from xml_parser import XMLParser

class SemanticError(Exception):
    def __init__(self, msg, line=None, column=None):
        self.msg = msg
        self.line = line
        self.column = column
        super().__init__(f"Semantic Error at line {line}:{column}: {msg}" if line and column else f"Semantic Error: {msg}")

class Symbol:
    def __init__(self, name, type, is_func=False, params=None, return_type=None, is_prototype=False, line=None, column=None):
        self.name = name
        self.type = type
        self.is_func = is_func
        self.params = params if params else []
        self.return_type = return_type
        self.is_prototype = is_prototype
        self.line = line
        self.column = column

    def __repr__(self):
        if self.is_func:
            params_str = ", ".join([f"{name}:{type}" for name, type in self.params])
            prototype = " (prototype)" if self.is_prototype else ""
            return f"Symbol({self.name}({params_str}) -> {self.return_type}{prototype})"
        else:
            return f"Symbol({self.name}: {self.type})"

class FunctionOverload:
    def __init__(self, name):
        self.name = name
        self.overloads = []
        self.prototypes = []
        
    def add_overload(self, func_symbol):
        if func_symbol.is_prototype:
            for existing in self.prototypes:
                if self._signatures_equal(existing.params, func_symbol.params):
                    return
            self.prototypes.append(func_symbol)
        else:
            for existing in self.overloads:
                if self._signatures_equal(existing.params, func_symbol.params):
                    raise SemanticError(
                        f"Function '{self.name}' with same signature already declared",
                        func_symbol.line, func_symbol.column
                    )
            self.overloads.append(func_symbol)
        
    def find_best_match(self, arg_types):
        best_match = None
        best_score = -1
        
        all_overloads = self.overloads + self.prototypes
        
        for overload in all_overloads:
            if len(overload.params) != len(arg_types):
                continue
                
            score = 0
            compatible = True
            
            for i, (param_type, arg_type) in enumerate(zip([p[1] for p in overload.params], arg_types)):
                if arg_type == "unknown":
                    score += 1
                elif param_type == arg_type:
                    score += 2
                elif self._types_compatible(param_type, arg_type):
                    score += 1
                else:
                    compatible = False
                    break
                    
            if compatible and score > best_score:
                best_score = score
                best_match = overload
                
        return best_match
        
    def _signatures_equal(self, params1, params2):
        if len(params1) != len(params2):
            return False
            
        for (name1, type1), (name2, type2) in zip(params1, params2):
            if type1 != type2:
                return False
        return True
        
    def _types_compatible(self, expected, actual):
        if expected == actual:
            return True
        if (expected == 'float' and actual == 'int'):
            return True
        return False
        
    def check_implementations(self):
        errors = []
        for prototype in self.prototypes:
            found = False
            for impl in self.overloads:
                if self._signatures_equal(prototype.params, impl.params):
                    if prototype.return_type != impl.return_type:
                        errors.append(
                            f"Function '{self.name}' implementation return type mismatch: "
                            f"prototype returns {prototype.return_type}, "
                            f"implementation returns {impl.return_type}"
                        )
                    found = True
                    break
            if not found and self.overloads:
                params_str = ", ".join([p[1] for p in prototype.params])
                errors.append(
                    f"Function '{self.name}' prototype ({params_str}) has no implementation"
                )
        return errors

class Scope:
    def __init__(self, parent=None, name="global"):
        self.parent = parent
        self.symbols = {}
        self.function_overloads = {}
        self.children = []
        self.name = name
        
    def add_symbol(self, symbol):
        if not symbol.is_func and symbol.name in self.symbols:
            # Проверяем, не объявлена ли переменная в той же самой функции
            # (разные функции могут иметь переменные с одинаковыми именами)
            if self.is_same_function_scope():
                raise SemanticError(
                    f"Symbol '{symbol.name}' already declared in this scope", 
                    symbol.line, symbol.column
                )
            
        if symbol.is_func:
            if symbol.name in self.function_overloads:
                self.function_overloads[symbol.name].add_overload(symbol)
            else:
                overload = FunctionOverload(symbol.name)
                overload.add_overload(symbol)
                self.function_overloads[symbol.name] = overload
        else:
            self.symbols[symbol.name] = symbol
    
    def is_same_function_scope(self):
        """Проверяет, находимся ли мы в той же самой функции"""
        if self.parent and self.parent.name.startswith("function_"):
            return True
        return False
        
    def lookup(self, name, current_only=False):
        if name in self.symbols:
            return self.symbols[name]
            
        if name in self.function_overloads:
            overload = self.function_overloads[name]
            if overload.overloads:
                return overload.overloads[0]
            elif overload.prototypes:
                return overload.prototypes[0]
            
        if not current_only and self.parent:
            return self.parent.lookup(name)
        return None
        
    def lookup_function_best_match(self, name, arg_types):
        if name in self.function_overloads:
            return self.function_overloads[name].find_best_match(arg_types)
            
        if self.parent:
            return self.parent.lookup_function_best_match(name, arg_types)
        return None
        
    def check_function_implementations(self):
        errors = []
        for name, overload in self.function_overloads.items():
            errors.extend(overload.check_implementations())
        return errors
        
    def create_child(self, name="child"):
        child = Scope(self, name)
        self.children.append(child)
        return child

class SemanticAnalyzer:
    def __init__(self):
        self.current_scope = Scope(name="global")
        self.errors = []
        self.warnings = []
        self.in_loop = False
        self.in_switch = False
        self.case_constants = []
        self.current_function = None
        self.visited_nodes = set()
        
    def analyze(self, tree):
        try:
            # Первый проход: объявление функций
            self.first_pass_declarations(tree)
            # Второй проход: проверка использования
            self.second_pass_validation(tree)
            
            implementation_errors = self.current_scope.check_function_implementations()
            self.errors.extend(implementation_errors)
            
        except SemanticError as e:
            self.errors.append(str(e))
        return self.errors
    
    def first_pass_declarations(self, node):
        """Первый проход: объявление всех функций"""
        if node is None:
            return
            
        class_name = type(node).__name__
        method_name = 'first_pass_' + class_name
        visitor = getattr(self, method_name, self.first_pass_generic)
        visitor(node)
    
    def first_pass_generic(self, node):
        if hasattr(node, 'children'):
            for child in node.children:
                if child is not None:
                    self.first_pass_declarations(child)
    
    def first_pass_DefContext(self, ctx):
        # Объявляем функцию в глобальной области видимости
        type_list = ctx.type_()
        typevoid = ctx.TYPEVOID()
        
        if type_list:
            if isinstance(type_list, list):
                return_type = type_list[0].getText() if len(type_list) > 0 else "void"
            else:
                return_type = type_list.getText()
        elif typevoid:
            return_type = "void"
        else:
            return_type = "unknown"
        
        id_node = ctx.ID()
        if isinstance(id_node, list):
            func_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            func_name = id_node.getText() if id_node else "unknown"
        
        params = []
        param_type_nodes = ctx.type_()
        param_id_nodes = ctx.ID()
        
        if param_type_nodes and param_id_nodes:
            if not isinstance(param_id_nodes, list):
                param_id_nodes = [param_id_nodes]
            if not isinstance(param_type_nodes, list):
                param_type_nodes = [param_type_nodes]
            
            if len(param_id_nodes) > 0:
                param_ids = param_id_nodes[1:] if len(param_id_nodes) > 1 else []
                
                for i in range(len(param_ids)):
                    param_name = param_ids[i].getText() if i < len(param_ids) else f"param_{i}"
                    param_type_idx = i + 1
                    if param_type_idx < len(param_type_nodes):
                        param_type = param_type_nodes[param_type_idx].getText()
                    else:
                        param_type = "unknown"
                    params.append((param_name, param_type))
        
        func_symbol = Symbol(
            func_name, 
            'function', 
            is_func=True, 
            params=params, 
            return_type=return_type,
            is_prototype=False,
            line=ctx.start.line if ctx.start else None,
            column=ctx.start.column if ctx.start else None
        )
        
        try:
            self.current_scope.add_symbol(func_symbol)
        except SemanticError as e:
            self.errors.append(str(e))
        
        self.first_pass_generic(ctx)
    
    def first_pass_DefDeclContext(self, ctx):
        type_list = ctx.type_()
        typevoid = ctx.TYPEVOID()
        
        if type_list:
            if isinstance(type_list, list):
                return_type = type_list[0].getText() if len(type_list) > 0 else "void"
            else:
                return_type = type_list.getText()
        elif typevoid:
            return_type = "void"
        else:
            return_type = "unknown"
        
        id_node = ctx.ID()
        if isinstance(id_node, list):
            func_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            func_name = id_node.getText() if id_node else "unknown"
        
        params = []
        param_type_nodes = ctx.type_()
        if param_type_nodes:
            if isinstance(param_type_nodes, list):
                for i in range(1, len(param_type_nodes)):
                    param_type = param_type_nodes[i].getText()
                    params.append((f"param_{i}", param_type))
        
        func_symbol = Symbol(
            func_name, 
            'function', 
            is_func=True,
            params=params, 
            return_type=return_type,
            is_prototype=True,
            line=ctx.start.line if ctx.start else None,
            column=ctx.start.column if ctx.start else None
        )
        
        try:
            self.current_scope.add_symbol(func_symbol)
        except SemanticError as e:
            pass
        
        self.first_pass_generic(ctx)
    
    def second_pass_validation(self, node):
        """Второй проход: проверка использования символов"""
        if node is None:
            return
            
        class_name = type(node).__name__
        method_name = 'visit_' + class_name
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)
        
    def generic_visit(self, node):
        if hasattr(node, 'children'):
            for child in node.children:
                if child is not None:
                    self.second_pass_validation(child)
        return None
        
    def visit_DefContext(self, ctx):
        # Входим в область видимости функции
        id_node = ctx.ID()
        if isinstance(id_node, list):
            func_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            func_name = id_node.getText() if id_node else "unknown"
        
        old_function = self.current_function
        self.current_function = func_name
        
        # Создаем новую область видимости для функции
        func_scope = self.current_scope.create_child(name=f"function_{func_name}")
        old_scope = self.current_scope
        self.current_scope = func_scope
        
        # Добавляем параметры функции в ее область видимости
        type_list = ctx.type_()
        param_id_nodes = ctx.ID()
        
        if type_list and param_id_nodes:
            if not isinstance(param_id_nodes, list):
                param_id_nodes = [param_id_nodes]
            if not isinstance(type_list, list):
                type_list = [type_list]
            
            if len(param_id_nodes) > 0:
                param_ids = param_id_nodes[1:] if len(param_id_nodes) > 1 else []
                
                for i in range(len(param_ids)):
                    param_name = param_ids[i].getText() if i < len(param_ids) else f"param_{i}"
                    param_type_idx = i + 1
                    if param_type_idx < len(type_list):
                        param_type = type_list[param_type_idx].getText()
                    else:
                        param_type = "unknown"
                    
                    param_symbol = Symbol(param_name, param_type)
                    try:
                        self.current_scope.add_symbol(param_symbol)
                    except SemanticError as e:
                        self.errors.append(str(e))
        
        # Обрабатываем тело функции
        if ctx.body():
            self.second_pass_validation(ctx.body())
        
        # Возвращаемся к предыдущей области видимости
        self.current_scope = old_scope
        self.current_function = old_function
        
        return None
        
    def visit_AssignmentContext(self, ctx):
        type_list = ctx.typeList()
        op_list = ctx.opList()
        
        if type_list:
            # Объявляем переменные в текущей области видимости
            self.declare_variables_from_typelist(type_list)
        
        if type_list and op_list:
            # Проверка множественного присваивания
            ids = self.get_ids_from_type_list(type_list)
            values_count = self.count_values_in_op_list(op_list)
            
            if len(ids) != values_count and values_count > 1:
                line = ctx.start.line if ctx.start else None
                column = ctx.start.column if ctx.start else None
                self.errors.append(
                    f"Semantic Error at line {line}:{column}: "
                    f"Mismatch in multiple assignment. "
                    f"Expected {len(ids)} values, got {values_count}"
                )
            
            # Проверка типов
            type_nodes = type_list.type_()
            var_type = None
            if type_nodes:
                if isinstance(type_nodes, list):
                    var_type = type_nodes[0].getText() if len(type_nodes) > 0 else None
                else:
                    var_type = type_nodes.getText()
            
            if var_type:
                # Получаем типы значений
                value_types = self.get_expression_types(op_list)
                
                for i, (var_name, value_type) in enumerate(zip(ids, value_types)):
                    if value_type and not self.check_type_conversion(value_type, var_type):
                        line = ctx.start.line if ctx.start else None
                        column = ctx.start.column if ctx.start else None
                        self.errors.append(
                            f"Semantic Error at line {line}:{column}: "
                            f"Cannot assign {value_type} to {var_type}"
                        )
    
        return self.generic_visit(ctx)
    
    def declare_variables_from_typelist(self, type_list_ctx):
        """Добавляет переменные из TypeList в таблицу символов"""
        type_nodes = type_list_ctx.type_()
        var_type = None
        
        if type_nodes:
            if isinstance(type_nodes, list):
                var_type = type_nodes[0].getText() if len(type_nodes) > 0 else None
            else:
                var_type = type_nodes.getText()
        
        id_nodes = type_list_ctx.ID()
        if not isinstance(id_nodes, list):
            id_nodes = [id_nodes] if id_nodes else []
            
        for id_node in id_nodes:
            var_name = id_node.getText()
            if var_type:
                var_symbol = Symbol(
                    var_name, 
                    var_type,
                    line=id_node.symbol.line if hasattr(id_node, 'symbol') else None,
                    column=id_node.symbol.column if hasattr(id_node, 'symbol') else None
                )
                try:
                    self.current_scope.add_symbol(var_symbol)
                except SemanticError as e:
                    self.errors.append(str(e))
    
    def get_expression_types(self, op_list_ctx):
        """Получает типы всех значений в opList"""
        types = []
        
        if hasattr(op_list_ctx, 'getChildCount'):
            # Проверяем наличие XPath-подобных выражений
            for i in range(op_list_ctx.getChildCount()):
                child = op_list_ctx.getChild(i)
                child_text = child.getText() if hasattr(child, 'getText') else str(child)
                
                # Если выражение содержит XPath (содержит '/', '[' или ']')
                if '/' in child_text or '[' in child_text or ']' in child_text:
                    types.append('list')
                    continue
        
        if op_list_ctx.val():
            for val in op_list_ctx.val():
                val_type = self.get_val_type(val)
                # Проверяем XPath в val
                if hasattr(val, 'getText'):
                    val_text = val.getText()
                    if '/' in val_text or '[' in val_text or ']' in val_text:
                        types.append('list')
                    else:
                        types.append(val_type)
                else:
                    types.append(val_type)
        
        if op_list_ctx.assFunc():
            for ass_func in op_list_ctx.assFunc():
                func_type = self.get_assfunc_type(ass_func)
                types.append(func_type)
        
        if op_list_ctx.INT():
            for _ in op_list_ctx.INT():
                types.append('int')
        
        if op_list_ctx.FLOAT():
            for _ in op_list_ctx.FLOAT():
                types.append('float')
        
        if op_list_ctx.STRING():
            for _ in op_list_ctx.STRING():
                types.append('string')
        
        if op_list_ctx.BOOL():
            for _ in op_list_ctx.BOOL():
                types.append('bool')
        
        if op_list_ctx.list_():
            for _ in op_list_ctx.list_():
                types.append('list')
        
        if op_list_ctx.PASS():
            types.append('string')
        
        return types
    
    def get_val_type(self, val_ctx):
        """Получает тип значения"""
        if val_ctx.ID():
            var_name = val_ctx.ID().getText()
            symbol = self.current_scope.lookup(var_name)
            if symbol:
                return symbol.type
            else:
                # Проверяем XPath выражение
                val_text = val_ctx.getText()
                if '/' in val_text or '[' in val_text or ']' in val_text:
                    return 'list'
                # Это может быть вызов функции
                return "unknown"
        elif val_ctx.defCall():
            return self.get_defcall_type(val_ctx.defCall())
        
        # Проверяем, содержит ли val XPath выражение
        val_text = val_ctx.getText() if hasattr(val_ctx, 'getText') else str(val_ctx)
        if '/' in val_text or '[' in val_text or ']' in val_text:
            return 'list'
        
        return "unknown"
    
    def get_defcall_type(self, defcall_ctx):
        """Получает тип возвращаемого значения функции"""
        if defcall_ctx.ID():
            func_name = defcall_ctx.ID().getText()
            
            # Специальные встроенные функции
            if func_name == 'load':
                return 'document'
            elif func_name == 'read':
                return 'string'
            elif func_name == 'create':
                # Определяем тип создаваемого объекта
                if defcall_ctx.defCall():  # Рекурсивный вызов
                    return 'unknown'
                return 'unknown'
            
            # Определяем типы аргументов
            arg_types = []
            
            if defcall_ctx.val():
                for val in defcall_ctx.val():
                    arg_types.append(self.get_val_type(val))
            
            if defcall_ctx.INT():
                for _ in defcall_ctx.INT():
                    arg_types.append('int')
            
            if defcall_ctx.FLOAT():
                for _ in defcall_ctx.FLOAT():
                    arg_types.append('float')
            
            if defcall_ctx.STRING():
                for _ in defcall_ctx.STRING():
                    arg_types.append('string')
            
            if defcall_ctx.BOOL():
                for _ in defcall_ctx.BOOL():
                    arg_types.append('bool')
            
            if defcall_ctx.list_():
                for _ in defcall_ctx.list_():
                    arg_types.append('list')
            
            # Ищем подходящую перегрузку
            func_symbol = self.current_scope.lookup_function_best_match(func_name, arg_types)
            if func_symbol:
                return func_symbol.return_type
        
        return "unknown"
    
    def get_assfunc_type(self, ass_func):
        """Определяет тип результата функции присваивания"""
        # Для упрощения возвращаем наиболее вероятный тип
        if hasattr(ass_func, 'getText'):
            return 'string'
        if hasattr(ass_func, 'getName'):
            return 'string'
        if hasattr(ass_func, 'getValue'):
            return 'string'
        if hasattr(ass_func, 'getAttribute'):
            return 'string'
        if hasattr(ass_func, 'defCall'):
            return self.get_defcall_type(ass_func.defCall())
        
        return "unknown"
        
    def visit_DefCallContext(self, ctx):
        id_node = ctx.ID()
        if isinstance(id_node, list):
            func_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            func_name = id_node.getText() if id_node else "unknown"
        
        arg_types = []
        
        if ctx.val():
            for val in ctx.val():
                arg_types.append(self.get_val_type(val))
        
        if ctx.INT():
            for _ in ctx.INT():
                arg_types.append('int')
        
        if ctx.FLOAT():
            for _ in ctx.FLOAT():
                arg_types.append('float')
        
        if ctx.STRING():
            for _ in ctx.STRING():
                arg_types.append('string')
        
        if ctx.BOOL():
            for _ in ctx.BOOL():
                arg_types.append('bool')
        
        if ctx.list_():
            for _ in ctx.list_():
                arg_types.append('list')
        
        func_symbol = self.current_scope.lookup_function_best_match(func_name, arg_types)
        
        if not func_symbol:
            line = ctx.start.line if ctx.start else None
            column = ctx.start.column if ctx.start else None
            
            overloads = self.current_scope.function_overloads.get(func_name, None)
            if overloads:
                all_overloads = overloads.overloads + overloads.prototypes
                if all_overloads:
                    available = []
                    for f in all_overloads:
                        params_str = ", ".join([p[1] for p in f.params])
                        available.append(f"({params_str}) -> {f.return_type}")
                    
                    available_str = "; ".join(available)
                    self.errors.append(
                        f"Semantic Error at line {line}:{column}: "
                        f"No matching overload for function '{func_name}' with arguments ({', '.join(arg_types)}). "
                        f"Available: {available_str}"
                    )
                else:
                    self.errors.append(
                        f"Semantic Error at line {line}:{column}: "
                        f"Function '{func_name}' is not declared"
                    )
            else:
                self.errors.append(
                    f"Semantic Error at line {line}:{column}: "
                    f"Function '{func_name}' is not declared"
                )
        else:
            if len(func_symbol.params) != len(arg_types):
                line = ctx.start.line if ctx.start else None
                column = ctx.start.column if ctx.start else None
                self.errors.append(
                    f"Semantic Error at line {line}:{column}: "
                    f"Function '{func_name}' expects "
                    f"{len(func_symbol.params)} arguments, got {len(arg_types)}"
                )
            else:
                # Проверяем типы аргументов
                for i, ((param_name, param_type), arg_type) in enumerate(zip(func_symbol.params, arg_types)):
                    if arg_type != "unknown" and not self.check_type_compatibility(param_type, arg_type):
                        line = ctx.start.line if ctx.start else None
                        column = ctx.start.column if ctx.start else None
                        self.errors.append(
                            f"Semantic Error at line {line}:{column}: "
                            f"Argument {i+1} of function '{func_name}' expects {param_type}, got {arg_type}"
                        )
        
        return self.generic_visit(ctx)
        
    def visit_WhileconContext(self, ctx):
        old_in_loop = self.in_loop
        self.in_loop = True
        
        if ctx.condition():
            condition_text = ctx.condition().getText()
            if condition_text.strip() == 'True':
                line = ctx.start.line if ctx.start else None
                column = ctx.start.column if ctx.start else None
                self.warnings.append(
                    f"Warning at line {line}:{column}: "
                    f"while condition is always True - possible infinite loop"
                )
                
        self.generic_visit(ctx)
        self.in_loop = old_in_loop
        return None
        
    def visit_ForconContext(self, ctx):
        id_nodes = ctx.ID()
        if id_nodes:
            if isinstance(id_nodes, list):
                if len(id_nodes) >= 2:
                    iter_var = id_nodes[0].getText()
                    collection = id_nodes[1].getText()
                    
                    coll_symbol = self.current_scope.lookup(collection)
                    if coll_symbol:
                        if coll_symbol.type not in ['list', 'int']:
                            line = ctx.start.line if ctx.start else None
                            column = ctx.start.column if ctx.start else None
                            self.errors.append(
                                f"Semantic Error at line {line}:{column}: "
                                f"for loop requires list or int type, "
                                f"got {coll_symbol.type}"
                            )
            
        old_in_loop = self.in_loop
        self.in_loop = True
        self.generic_visit(ctx)
        self.in_loop = old_in_loop
        return None
        
    def visit_SwitchconContext(self, ctx):
        old_in_switch = self.in_switch
        old_case_constants = self.case_constants
        self.in_switch = True
        self.case_constants = []
                    
        # Проверяем дублирование констант в case
        switch_var = ctx.ID().getText() if ctx.ID() else None
        
        result = self.generic_visit(ctx)
        
        self.in_switch = old_in_switch
        self.case_constants = old_case_constants
        return result
        
    def visit_CreateContext(self, ctx):
        return self.generic_visit(ctx)
        
    def visit_EditContext(self, ctx):
        id_node = ctx.ID()
        if isinstance(id_node, list):
            var_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            var_name = id_node.getText() if id_node else "unknown"
            
        var_symbol = self.current_scope.lookup(var_name)
        
        if var_symbol:
            edit_type = None
            if ctx.docEdit():
                edit_type = 'document'
            elif ctx.nodeEdite():
                edit_type = 'node'
            elif ctx.attributeEdit():
                edit_type = 'attribute'
                
            if edit_type and var_symbol.type != edit_type:
                line = ctx.start.line if ctx.start else None
                column = ctx.start.column if ctx.start else None
                self.errors.append(
                    f"Semantic Error at line {line}:{column}: "
                    f"Cannot edit {edit_type} on variable "
                    f"of type {var_symbol.type}"
                )
                
        return self.generic_visit(ctx)
        
    def visit_GetAttributeContext(self, ctx):
        id_node = ctx.ID()
        if isinstance(id_node, list):
            var_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            var_name = id_node.getText() if id_node else "unknown"
            
        var_symbol = self.current_scope.lookup(var_name)
        
        if var_symbol and var_symbol.type != 'node':
            line = ctx.start.line if ctx.start else None
            column = ctx.start.column if ctx.start else None
            self.errors.append(
                f"Semantic Error at line {line}:{column}: "
                f"getAttribute can only be used on node, "
                f"got {var_symbol.type}"
            )
            
        return self.generic_visit(ctx)
        
    def visit_AddAttributeContext(self, ctx):
        id_node = ctx.ID()
        if isinstance(id_node, list):
            var_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            var_name = id_node.getText() if id_node else "unknown"
            
        var_symbol = self.current_scope.lookup(var_name)
        
        if var_symbol and var_symbol.type != 'node':
            line = ctx.start.line if ctx.start else None
            column = ctx.start.column if ctx.start else None
            self.errors.append(
                f"Semantic Error at line {line}:{column}: "
                f"addAttribute can only be used on node, "
                f"got {var_symbol.type}"
            )
            
        return self.generic_visit(ctx)
        
    def visit_AppendContext(self, ctx):
        id_node = ctx.ID()
        if isinstance(id_node, list):
            var_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            var_name = id_node.getText() if id_node else "unknown"
            
        var_symbol = self.current_scope.lookup(var_name)
        
        if var_symbol and var_symbol.type not in ['node', 'document']:
            line = ctx.start.line if ctx.start else None
            column = ctx.start.column if ctx.start else None
            self.errors.append(
                f"Semantic Error at line {line}:{column}: "
                f"appendTo can only be used on node or document, "
                f"got {var_symbol.type}"
            )
            
        return self.generic_visit(ctx)
        
    def visit_GetNodeTextContext(self, ctx):
        id_node = ctx.ID()
        if isinstance(id_node, list):
            var_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            var_name = id_node.getText() if id_node else "unknown"
            
        var_symbol = self.current_scope.lookup(var_name)
        
        if var_symbol and var_symbol.type != 'node':
            line = ctx.start.line if ctx.start else None
            column = ctx.start.column if ctx.start else None
            self.errors.append(
                f"Semantic Error at line {line}:{column}: "
                f"getText can only be used on node, "
                f"got {var_symbol.type}"
            )
            
        return self.generic_visit(ctx)
        
    def visit_GetNameContext(self, ctx):
        id_node = ctx.ID()
        if isinstance(id_node, list):
            var_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            var_name = id_node.getText() if id_node else "unknown"
            
        var_symbol = self.current_scope.lookup(var_name)
        
        if var_symbol and var_symbol.type not in ['node', 'attribute']:
            line = ctx.start.line if ctx.start else None
            column = ctx.start.column if ctx.start else None
            self.errors.append(
                f"Semantic Error at line {line}:{column}: "
                f"getName can only be used on node or attribute, "
                f"got {var_symbol.type}"
            )
            
        return self.generic_visit(ctx)
        
    def visit_GetValueContext(self, ctx):
        id_node = ctx.ID()
        if isinstance(id_node, list):
            var_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            var_name = id_node.getText() if id_node else "unknown"
            
        var_symbol = self.current_scope.lookup(var_name)
        
        if var_symbol and var_symbol.type != 'attribute':
            line = ctx.start.line if ctx.start else None
            column = ctx.start.column if ctx.start else None
            self.errors.append(
                f"Semantic Error at line {line}:{column}: "
                f"getValue can only be used on attribute, "
                f"got {var_symbol.type}"
            )
            
        return self.generic_visit(ctx)
        
    def visit_XmldeleteContext(self, ctx):
        id_node = ctx.ID()
        if isinstance(id_node, list):
            var_name = id_node[0].getText() if id_node and len(id_node) > 0 else "unknown"
        else:
            var_name = id_node.getText() if id_node else "unknown"
            
        var_symbol = self.current_scope.lookup(var_name)
        
        if var_symbol and var_symbol.type not in ['document', 'node', 'attribute']:
            line = ctx.start.line if ctx.start else None
            column = ctx.start.column if ctx.start else None
            self.errors.append(
                f"Semantic Error at line {line}:{column}: "
                f"delete can only be used on XML types "
                f"(document, node, attribute), got {var_symbol.type}"
            )
            
        return None
        
    def visit_ReturnValContext(self, ctx):
        return self.generic_visit(ctx)
        
    def visit_BreakContext(self, ctx):
        if not self.in_loop and not self.in_switch:
            line = ctx.start.line if ctx.start else None
            column = ctx.start.column if ctx.start else None
            self.errors.append(
                f"Semantic Error at line {line}:{column}: "
                f"break statement outside of loop or switch"
            )
            
        return None
        
    def visit_ValContext(self, ctx):
        if ctx.ID():
            var_name = ctx.ID().getText()
            symbol = self.current_scope.lookup(var_name)
            if not symbol:
                line = ctx.start.line if ctx.start else None
                column = ctx.start.column if ctx.start else None
                self.errors.append(
                    f"Semantic Error at line {line}:{column}: "
                    f"Variable '{var_name}' is not declared"
                )
        
        return self.generic_visit(ctx)
        
    def visit_BodyContext(self, ctx):
        if ctx.LF():
            old_scope = self.current_scope
            self.current_scope = self.current_scope.create_child(name="block")
            
            result = self.generic_visit(ctx)
            
            self.current_scope = old_scope
            return result
        else:
            return self.generic_visit(ctx)
        
    def get_ids_from_type_list(self, type_list_ctx):
        ids = []
        if type_list_ctx:
            id_nodes = type_list_ctx.ID()
            if not isinstance(id_nodes, list):
                id_nodes = [id_nodes] if id_nodes else []
                
            for id_node in id_nodes:
                ids.append(id_node.getText())
        return ids
        
    def count_values_in_op_list(self, op_list_ctx):
        count = 0
        if op_list_ctx:
            count_methods = [
                ('val', lambda: len(op_list_ctx.val())),
                ('assFunc', lambda: len(op_list_ctx.assFunc())),
                ('INT', lambda: len(op_list_ctx.INT())),
                ('STRING', lambda: len(op_list_ctx.STRING())),
                ('FLOAT', lambda: len(op_list_ctx.FLOAT())),
                ('BOOL', lambda: len(op_list_ctx.BOOL())),
                ('list_', lambda: len(op_list_ctx.list_())),
            ]
            
            for attr_name, count_func in count_methods:
                if hasattr(op_list_ctx, attr_name):
                    try:
                        count += count_func()
                    except:
                        pass
                        
            if hasattr(op_list_ctx, 'PASS') and op_list_ctx.PASS():
                count += 1
                
        return count

    def check_type_compatibility(self, expected, actual):
        if expected == actual:
            return True
            
        allowed_conversions = {
            ('int', 'float'): True,
            ('float', 'int'): True,
        }
        
        return allowed_conversions.get((actual, expected), False)
    
    def check_type_conversion(self, from_type, to_type):
        """Проверяет возможность преобразования типа"""
        if from_type == to_type:
            return True
            
        # Разрешаем преобразование list в list
        if from_type == 'list' and to_type == 'list':
            return True
            
        # Разрешаем преобразование document <-> node
        if (from_type == 'document' and to_type == 'node') or \
           (from_type == 'node' and to_type == 'document'):
            return True
            
        # Разрешаем преобразование string <-> node
        if (from_type == 'string' and to_type == 'node') or \
           (from_type == 'node' and to_type == 'string'):
            return True
            
        # Разрешаем преобразование string <-> document
        if (from_type == 'string' and to_type == 'document') or \
           (from_type == 'document' and to_type == 'string'):
            return True
            
        # Запрещаем преобразования между XML типами и остальными базовыми типами
        # Запрещаем node в int, float, list, attribute и наоборот
        if from_type == 'node' and to_type in ['int', 'float', 'list', 'attribute']:
            return False
        if to_type == 'node' and from_type in ['int', 'float', 'list', 'attribute']:
            return False
        
        # Запрещаем document в int, float, list, attribute и наоборот
        if from_type == 'document' and to_type in ['int', 'float', 'list', 'attribute']:
            return False
        if to_type == 'document' and from_type in ['int', 'float', 'list', 'attribute']:
            return False
        
        # Запрещаем list в любой другой тип (кроме list)
        if from_type == 'list' and to_type != 'list':
            return False
            
        # Запрещаем attribute в int, float, list и наоборот
        if from_type == 'attribute' and to_type in ['int', 'float', 'list']:
            return False
        if to_type == 'attribute' and from_type in ['int', 'float', 'list']:
            return False
        
        # Разрешаем некоторые преобразования между базовыми типами
        allowed_conversions = {
            ('int', 'float'): True,
            ('float', 'int'): True,
        }
        
        return allowed_conversions.get((from_type, to_type), False)

if __name__ == "__main__":
    test_code = """
    node func A()
node func A(string)

node func A(){
	document doc = load("D\:work\b.xml")
	node r = doc
	return r
}

node func A(string pass){
	document doc = load(pass)
	node r = doc
	return r
}

string pass1 = "D\:work\a.xml"
string one, string two = A(), A(pass1)
if one == two {
	read("Roots has one name:" one)
	string pass2 = "D\:work\.xml"}
else {
	read('This is the end')
	return}

document doc1, document doc2 = load(pass1), load(pass2)
node r1 = doc1
node r2 = doc2
node nr = r1 + r2
document ndoc = create.document(root = nr file = "new.xml")
ndoc.save()


    """
    
    print("Testing semantic analyzer with your example...")
    
    parser = XMLParser(test_code)
    tree = parser.parse()
    
    if tree and not parser.has_errors():
        print("Parsing successful!")
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(tree)
        
        if errors:
            print("\nSemantic errors found:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("\nNo semantic errors found")
            
        if analyzer.warnings:
            print("\nWarnings:")
            for warning in analyzer.warnings:
                print(f"  - {warning}")
    else:
        print("\nSyntax errors found:")
        for error in parser.get_errors():
            print(f"  - {error}")
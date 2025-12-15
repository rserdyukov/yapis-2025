"""
Семантический анализатор для языка GSL1
Проверяет типы, области видимости, использование переменных и функций
"""

from antlr4 import *
from gen.gsl1Parser import gsl1Parser
from gen.gsl1Listener import gsl1Listener


class Symbol:
    """Символ в таблице символов"""
    def __init__(self, name, symbol_type, line, is_function=False, params=None, return_type=None):
        self.name = name
        self.type = symbol_type  # 'int', 'str', 'float', 'table', 'column', 'list', etc.
        self.line = line
        self.is_function = is_function
        self.params = params or []  # [(name, type), ...]
        self.return_type = return_type

    def __repr__(self):
        if self.is_function:
            params_str = ', '.join([f"{p[0]}: {p[1]}" for p in self.params])
            return f"func {self.name}({params_str}) -> {self.return_type}"
        return f"{self.name}: {self.type}"


class SemanticAnalyzer(gsl1Listener):
    """Семантический анализатор"""
    
    # Допустимые типы в системе
    VALID_TYPES = {'int', 'float', 'str', 'bool', 'table', 'column', 'row', 'void', 'list'}
    
    # Допустимые типы в системе
    VALID_TYPES = {'int', 'float', 'str', 'bool', 'table', 'column', 'row', 'void', 'list'}
    
    def __init__(self):
        self.errors = []
        self.symbol_table = {}  # {name: Symbol}
        self.scope_stack = [{}]  # Стек областей видимости
        self.current_function = None
        self.line_number = 0
        self.initialized_vars = set()  # Инициализированные переменные
        self.function_returns = {}  # {function_name: has_return}
        self.switch_has_default = {}  # {switch_line: has_default}
        self.initialized_vars = set()  # Инициализированные переменные
        self.function_returns = {}  # {function_name: has_return}
        self.switch_has_default = {}  # {switch_line: has_default}
        
    def error(self, line, message):
        """Добавить ошибку"""
        error_msg = f"Семантическая ошибка в строке {line}: {message}"
        self.errors.append(error_msg)
        print(error_msg)
    
    def get_line(self, ctx):
        """Получить номер строки из контекста"""
        if ctx and ctx.start:
            return ctx.start.line
        return self.line_number
    
    def resolve_type(self, type_ctx):
        """Разрешить тип из контекста"""
        if not type_ctx:
            return None
        # type: ID | ID '[' type ']'
        if type_ctx.getChildCount() == 1:
            return type_ctx.ID().getText()
        elif type_ctx.getChildCount() == 3:  # ID '[' type ']'
            base_type = type_ctx.ID().getText()
            inner_type_ctx = type_ctx.type_(0)
            inner_type = self.resolve_type(inner_type_ctx)
            return f"{base_type}[{inner_type}]"
        return None
    
    def check_type_validity(self, type_name, line):
        """Проверить, является ли тип допустимым"""
        if not type_name:
            return True
        # Извлекаем базовый тип (без параметров)
        base_type = type_name.split('[')[0].strip()
        if base_type not in self.VALID_TYPES:
            self.error(line, f"Тип '{base_type}' не объявлен в системе типов языка")
            return False
        return True
    
    def check_type_compatibility(self, var_type, expr_type, line, context=""):
        """Проверить совместимость типов"""
        if not var_type or var_type == 'unknown':
            return True  # Не можем проверить
        
        # Базовые типы должны совпадать
        var_base = var_type.split('[')[0].strip()
        expr_base = expr_type.split('[')[0].strip() if expr_type else 'unknown'
        
        # Допустимые неявные преобразования
        conversions = {
            ('int', 'float'): True,  # int -> float
            ('float', 'int'): False,  # float -> int (требует явного преобразования)
        }
        
        if var_base == expr_base:
            return True
        
        # Проверяем допустимые преобразования
        if (expr_base, var_base) in conversions:
            if conversions[(expr_base, var_base)]:
                return True
        
        # Для специальных типов строгая проверка
        if var_base in ['table', 'column', 'row']:
            if expr_base != var_base:
                self.error(line, f"{context}Несовместимые типы: ожидается '{var_type}', получено '{expr_type}'")
                return False
        
        # Для остальных типов - строгая проверка
        if expr_base != 'unknown' and var_base != expr_base:
            self.error(line, f"{context}Присваивание значения типа '{expr_type}' переменной типа '{var_type}'")
            return False
        
        return True
    
    def infer_expression_type(self, ctx):
        """Вывести тип выражения (упрощённая версия)"""
        if not ctx:
            return 'unknown'
        
        # Литералы
        if hasattr(ctx, 'literal') and ctx.literal():
            lit = ctx.literal()
            if lit.INT():
                return 'int'
            elif lit.FLOAT():
                return 'float'
            elif lit.STRING():
                return 'str'
            elif lit.getText() in ['true', 'false']:
                return 'bool'
        
        # Идентификатор
        if hasattr(ctx, 'ID') and ctx.ID():
            symbol = self.lookup_symbol(ctx.ID().getText())
            if symbol:
                return symbol.type
            return 'unknown'
        
        # Вызов функции
        if ctx.getChildCount() >= 3:
            first = ctx.getChild(0)
            if isinstance(first, gsl1Parser.ExpressionContext):
                if first.getChildCount() == 1 and first.ID():
                    func_name = first.ID().getText()
                    func_symbol = self.lookup_symbol(func_name)
                    if func_symbol and func_symbol.is_function:
                        return func_symbol.return_type or 'void'
        
        return 'unknown'
    
    def lookup_symbol(self, name):
        """Найти символ в текущей области видимости и выше"""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return None
    
    def add_symbol(self, name, symbol):
        """Добавить символ в текущую область видимости"""
        if name in self.scope_stack[-1]:
            self.error(symbol.line, f"Переменная '{name}' уже объявлена")
        self.scope_stack[-1][name] = symbol
    
    # === Обработка объявлений ===
    
    def enterTableDeclaration(self, ctx: gsl1Parser.TableDeclarationContext):
        """Обработка объявления таблицы"""
        table_name = ctx.ID().getText()
        line = self.get_line(ctx)
        symbol = Symbol(table_name, 'table', line)
        self.add_symbol(table_name, symbol)
    
    def enterTypedAssignment(self, ctx: gsl1Parser.TypedAssignmentContext):
        """Обработка объявления с типом"""
        var_name = ctx.ID().getText()
        type_ctx = ctx.type_()
        var_type = self.resolve_type(type_ctx)
        line = self.get_line(ctx)
        
        # Проверяем валидность типа
        self.check_type_validity(var_type, line)
        
        symbol = Symbol(var_name, var_type, line)
        self.add_symbol(var_name, symbol)
        
        # Проверяем совместимость типов при присваивании
        expr_ctx = ctx.expression()
        if expr_ctx:
            expr_type = self.infer_expression_type(expr_ctx)
            self.check_type_compatibility(var_type, expr_type, line)
        
        # Отмечаем переменную как инициализированную
        self.initialized_vars.add(var_name)
    
    def enterFunctionDef(self, ctx: gsl1Parser.FunctionDefContext):
        """Обработка определения функции"""
        func_name = ctx.ID().getText()
        line = self.get_line(ctx)
        
        # Получаем параметры
        params = []
        params_ctx = ctx.parameters()
        if params_ctx:
            param_list = params_ctx.parameter()
            if param_list:
                for param_ctx in param_list:
                    param_name = param_ctx.ID().getText()
                    param_type = self.resolve_type(param_ctx.type_())
                    # Проверяем валидность типа параметра
                    self.check_type_validity(param_type, line)
                    params.append((param_name, param_type))
        
        # Получаем возвращаемый тип (после '->')
        return_type = None
        type_ctx = ctx.type_()
        if type_ctx:
            return_type = self.resolve_type(type_ctx)
            # Проверяем валидность типа возврата
            self.check_type_validity(return_type, line)
        
        # Создаем символ функции
        func_symbol = Symbol(func_name, 'function', line, is_function=True, 
                            params=params, return_type=return_type)
        
        # Проверяем переопределение
        existing = self.lookup_symbol(func_name)
        if existing and existing.is_function:
            # Проверяем перегрузку (разные сигнатуры)
            if existing.params == params:
                self.error(line, f"Функция '{func_name}' с такими параметрами уже определена")
            # Иначе это перегрузка - разрешена
        else:
            self.add_symbol(func_name, func_symbol)
        
        # Входим в область видимости функции
        self.scope_stack.append({})
        self.current_function = func_symbol
        self.function_returns[func_name] = False  # Инициализируем флаг возврата
        
        # Добавляем параметры в область видимости функции
        for param_name, param_type in params:
            param_symbol = Symbol(param_name, param_type, line)
            self.scope_stack[-1][param_name] = param_symbol
            self.initialized_vars.add(param_name)  # Параметры считаются инициализированными
    
    def exitFunctionDef(self, ctx: gsl1Parser.FunctionDefContext):
        """Выход из области видимости функции"""
        if self.current_function:
            func_name = self.current_function.name
            # Проверяем, должна ли функция возвращать значение
            if self.current_function.return_type and self.current_function.return_type != 'void':
                if not self.function_returns.get(func_name, False):
                    self.error(self.get_line(ctx), 
                             f"Подпрограмма '{func_name}' должна возвращать значение типа '{self.current_function.return_type}', но оператор return отсутствует")
        
        if self.scope_stack:
            self.scope_stack.pop()
        self.current_function = None
    
    # === Обработка присваиваний ===
    
    def enterSingleAssignment(self, ctx: gsl1Parser.SingleAssignmentContext):
        """Обработка простого присваивания"""
        var_name = ctx.ID().getText()
        symbol = self.lookup_symbol(var_name)
        line = self.get_line(ctx)
        
        if not symbol:
            # Автоматическое объявление переменной (если не в функции)
            if self.current_function is None:
                symbol = Symbol(var_name, 'unknown', line)
                self.add_symbol(var_name, symbol)
            else:
                self.error(line, f"Использование необъявленной переменной '{var_name}'")
        else:
            # Проверяем совместимость типов
            expr_ctx = ctx.expression()
            if expr_ctx and symbol.type != 'unknown':
                expr_type = self.infer_expression_type(expr_ctx)
                self.check_type_compatibility(symbol.type, expr_type, line)
        
        # Отмечаем переменную как инициализированную
        self.initialized_vars.add(var_name)
    
    def enterMemberAssignment(self, ctx: gsl1Parser.MemberAssignmentContext):
        """Обработка присваивания члену объекта"""
        obj_name = ctx.ID(0).getText()
        member_name = ctx.ID(1).getText()
        
        obj_symbol = self.lookup_symbol(obj_name)
        if not obj_symbol:
            self.error(self.get_line(ctx), f"Использование необъявленной переменной '{obj_name}'")
        elif obj_symbol.type != 'table':
            self.error(self.get_line(ctx), 
                      f"Обращение к члену '{member_name}' недопустимо для типа '{obj_symbol.type}'")
    
    # === Обработка выражений ===
    
    def enterExpression(self, ctx: gsl1Parser.ExpressionContext):
        """Обработка выражений"""
        line = self.get_line(ctx)
        
        # Проверяем, является ли это идентификатором
        if ctx.getChildCount() == 1 and ctx.ID():
            var_name = ctx.ID().getText()
            symbol = self.lookup_symbol(var_name)
            if not symbol:
                self.error(line, f"Использование необъявленной переменной '{var_name}'")
            else:
                # Проверяем инициализацию переменной
                if var_name not in self.initialized_vars:
                    # Проверяем, не является ли это параметром функции
                    if not (self.current_function and var_name in [p[0] for p in self.current_function.params]):
                        self.error(line, f"Попытка обращения к неинициализированной переменной '{var_name}'")
        
        # Проверяем деление на ноль
        if ctx.getChildCount() == 3:
            op = ctx.getChild(1)
            if hasattr(op, 'getText') and op.getText() == '/':
                right_expr = ctx.getChild(2)
                if isinstance(right_expr, gsl1Parser.ExpressionContext):
                    # Упрощённая проверка: если это литерал 0
                    if right_expr.getChildCount() == 1:
                        if right_expr.literal() and right_expr.literal().INT():
                            if right_expr.literal().INT().getText() == '0':
                                self.error(line, "Семантическая ошибка: деление на ноль")
        
        # Проверяем, является ли это вызовом функции
        # Вызов функции имеет вид: expression '(' ... ')'
        if ctx.getChildCount() >= 3:
            first_child = ctx.getChild(0)
            if isinstance(first_child, gsl1Parser.ExpressionContext):
                # Проверяем, является ли первое выражение идентификатором
                if first_child.getChildCount() == 1 and first_child.ID():
                    func_name = first_child.ID().getText()
                    func_symbol = self.lookup_symbol(func_name)
                    
                    if not func_symbol:
                        self.error(line, f"Вызов необъявленной функции '{func_name}'")
                    elif not func_symbol.is_function:
                        self.error(line, f"'{func_name}' не является функцией")
                    else:
                        # Проверяем количество аргументов
                        arg_count = len(ctx.expression()) - 1
                        param_count = len(func_symbol.params)
                        if arg_count != param_count:
                            self.error(line, 
                                     f"Неверное количество аргументов для '{func_name}': "
                                     f"ожидается {param_count}, получено {arg_count}")
                        else:
                            # Проверяем типы аргументов
                            for i in range(param_count):
                                arg_expr = ctx.expression(i + 1)  # +1 потому что первый - функция
                                param_type = func_symbol.params[i][1]
                                arg_type = self.infer_expression_type(arg_expr)
                                self.check_type_compatibility(param_type, arg_type, line,
                                                            f"Тип аргумента {i+1} функции '{func_name}': ")
    
    def enterReturnStatement(self, ctx: gsl1Parser.ReturnStatementContext):
        """Обработка return"""
        if self.current_function is None:
            self.error(self.get_line(ctx), "return вне функции")
        else:
            # Отмечаем, что функция имеет return
            self.function_returns[self.current_function.name] = True
            
            # Проверяем тип возвращаемого значения
            if ctx.expression():
                expr_type = self.infer_expression_type(ctx.expression())
                expected_type = self.current_function.return_type
                if expected_type and expected_type != 'void':
                    self.check_type_compatibility(expected_type, expr_type, self.get_line(ctx), 
                                                "Неверный тип возвращаемого значения: ")
    
    # === Обработка операций с таблицами ===
    
    def enterDataInsert(self, ctx: gsl1Parser.DataInsertContext):
        """Обработка вставки данных"""
        table_name = ctx.ID().getText()
        symbol = self.lookup_symbol(table_name)
        
        if not symbol:
            self.error(self.get_line(ctx), f"Использование необъявленной таблицы '{table_name}'")
        elif symbol.type != 'table':
            self.error(self.get_line(ctx), 
                      f"Операция '+=' применима только к таблицам, а '{table_name}' имеет тип '{symbol.type}'")
    
    def enterDataDelete(self, ctx: gsl1Parser.DataDeleteContext):
        """Обработка удаления данных"""
        table_name = ctx.ID().getText()
        symbol = self.lookup_symbol(table_name)
        
        if not symbol:
            self.error(self.get_line(ctx), f"Использование необъявленной таблицы '{table_name}'")
        elif symbol.type != 'table':
            self.error(self.get_line(ctx), 
                      f"Операция '-=' применима только к таблицам, а '{table_name}' имеет тип '{symbol.type}'")
    
    def enterForLoop(self, ctx: gsl1Parser.ForLoopContext):
        """Обработка цикла for"""
        var_name = ctx.ID().getText()
        # Переменная цикла добавляется в область видимости
        line = self.get_line(ctx)
        loop_var = Symbol(var_name, 'unknown', line)
        self.scope_stack.append({})
        self.scope_stack[-1][var_name] = loop_var
    
    def exitForLoop(self, ctx: gsl1Parser.ForLoopContext):
        """Выход из области видимости цикла"""
        if self.scope_stack:
            self.scope_stack.pop()
    
    def enterIfStatement(self, ctx: gsl1Parser.IfStatementContext):
        """Обработка if"""
        # Входим в область видимости if (если нужно)
        self.scope_stack.append({})
    
    def exitIfStatement(self, ctx: gsl1Parser.IfStatementContext):
        """Выход из области видимости if"""
        if self.scope_stack:
            self.scope_stack.pop()
    
    def enterSwitchStatement(self, ctx: gsl1Parser.SwitchStatementContext):
        """Обработка switch"""
        line = self.get_line(ctx)
        self.switch_has_default[line] = False
    
    def enterDefaultClause(self, ctx: gsl1Parser.DefaultClauseContext):
        """Обработка default в switch"""
        # Находим родительский switch
        parent = ctx.parentCtx
        while parent and not isinstance(parent, gsl1Parser.SwitchStatementContext):
            parent = parent.parentCtx
        if parent:
            switch_line = self.get_line(parent)
            self.switch_has_default[switch_line] = True
    
    def exitSwitchStatement(self, ctx: gsl1Parser.SwitchStatementContext):
        """Выход из switch - проверяем наличие default"""
        line = self.get_line(ctx)
        if not self.switch_has_default.get(line, False):
            self.error(line, "Отсутствие ветви по умолчанию (default) при обязательности для неучтённых случаев")


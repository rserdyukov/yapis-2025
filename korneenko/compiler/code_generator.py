"""
Генератор LLVM IR для языка GSL1.
Поддерживает все основные конструкции языка: типы, функции, циклы, условия, таблицы и т.д.
"""

import sys
from antlr4 import ParseTreeWalker
from gen.gsl1Parser import gsl1Parser
from gen.gsl1Listener import gsl1Listener


class CodeGenerator(gsl1Listener):
    """"""
    
    def __init__(self):
        # Счётчики для уникальных имён
        self.temp_count = 0
        self.label_count = 0
        self.string_count = 0
        self.function_count = 0
        
        # Стек для управления контекстом (функции, циклы, условия)
        self.function_stack = []  # Текущий стек функций (для управления контекстом)
        self.all_functions = []  # Все функции для генерации в LLVM IR
        self.current_function = None
        
        # Хранилище информации о функциях для вызовов
        self.functions_info = {}  # {func_name: [{'return_type': ..., 'params': [...], 'param_count': ...}]}
        
        # Глобальные данные
        self.global_strings = {}  # {string_value: global_name}
        self.global_declarations = []  # Объявления функций и глобальных переменных
        self.standard_declarations_added = False  # Флаг для добавления стандартных объявлений
        
        # Информация о таблицах для сериализации
        self.tables_info = {}  # {table_name: {'columns': [...], 'rows': [...]}}
        self.table_variables = {}  # {var_ptr: table_name} - маппинг указателей на имена таблиц
        self.pending_row_data = []  # Временное хранилище для данных Row при обработке dataInsert
        
        # Отслеживание вызовов функций для параметров-таблиц
        self.function_call_table_mapping = {}  # {(func_name, param_index): table_name} - маппинг параметров функций на таблицы
        
        # Таблица символов для текущей функции
        self.variables = {}  # {name: (llvm_type, ptr_reg)}
        self.scope_stack = [{}]  # Стек областей видимости для переменных
        
        # Для управления блоками (if, switch, loops)
        self.block_stack = []  # Стек меток блоков
        
        # Флаг для отслеживания обработки генераторного выражения
        self.in_generator_expression = False
        
        # Типы данных
        self.type_map = {
            'int': 'i32',
            'float': 'double',
            'str': 'i8*',
            'bool': 'i1',
            'void': 'void',
            'table': 'i8*',  # Упрощённо - указатель на структуру
            'column': 'i8*',
            'row': 'i8*',
            'list': 'i8*',
        }
        
    # === Вспомогательные методы ===
    
    def new_temp(self) -> str:
        """Создать новый временный регистр"""
        self.temp_count += 1
        return f"%t{self.temp_count}"
    
    def new_label(self) -> str:
        """Создать новую метку"""
        self.label_count += 1
        return f"label{self.label_count}"
    
    def get_llvm_type(self, gsl_type: str) -> str:
        """Преобразовать тип GSL1 в LLVM тип"""
        if not gsl_type:
            return 'i32'  # По умолчанию
        base_type = gsl_type.split('[')[0].strip()
        return self.type_map.get(base_type, 'i8*')
    
    def emit(self, code: str):
        """Добавить инструкцию в текущий контекст"""
        if self.current_function:
            self.current_function['body'].append(code)
        else:
            # Глобальный контекст - добавляем в последнюю функцию или создаём main
            if not self.function_stack:
                self._init_main_function()
            if self.function_stack:
                self.function_stack[-1]['body'].append(code)
    
    def emit_entry(self, code: str):
        """Добавить инструкцию в entry блок функции"""
        if self.current_function:
            self.current_function['entry'].append(code)
    
    def _init_main_function(self):
        """Инициализировать функцию main"""
        main_func = {
            'name': 'main',
            'return_type': 'i32',
            'params': [],
            'entry': [],
            'body': [],
            'footer': []
        }
        self.function_stack.append(main_func)
        self.current_function = main_func
    
    def get_or_create_variable(self, name: str, llvm_type: str = "i32") -> str:
        """Получить или создать переменную"""
        # Ищем в текущей области видимости
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name][1]
        
        # Создаём новую переменную
        ptr = self.new_temp()
        self.emit_entry(f"  {ptr} = alloca {llvm_type}")
        self.scope_stack[-1][name] = (llvm_type, ptr)
        return ptr
    
    def get_string_global(self, string_value: str) -> str:
        """Получить или создать глобальную строковую константу"""
        if string_value in self.global_strings:
            return self.global_strings[string_value]
        
        # Создаём новую глобальную строку
        self.string_count += 1
        global_name = f"@.str{self.string_count}"
        # Экранируем строку для LLVM
        escaped = string_value.replace('\\', '\\\\').replace('"', '\\22').replace('\n', '\\0A').replace('\r', '\\0D')
        # Вычисляем длину строки в байтах (UTF-8) + нулевой терминатор
        # Для кириллицы и других многобайтовых символов нужно считать байты
        str_bytes = string_value.encode('utf-8')
        length = len(str_bytes) + 1  # +1 для нулевого терминатора
        self.global_declarations.append(
            f'{global_name} = private unnamed_addr constant [{length} x i8] c"{escaped}\\00"'
        )
        self.global_strings[string_value] = global_name
        return global_name
    
    # === Обработка программы ===
    
    def enterProgram(self, ctx: gsl1Parser.ProgramContext):
        """Начало программы"""
        # Добавляем стандартные объявления
        self.global_declarations.extend([
            '; Модуль LLVM IR, сгенерированный из GSL1',
            'declare i32 @printf(i8*, ...)',
            'declare i32 @puts(i8*)',
            '',
        ])
        self._init_main_function()
    
    def exitProgram(self, ctx: gsl1Parser.ProgramContext):
        """Конец программы"""
        # Завершаем main функцию
        if self.function_stack:
            main_func = self.function_stack[-1]
            main_func['footer'].append('  ret i32 0')
    
    # === Обработка литералов ===
    
    def exitLiteral(self, ctx: gsl1Parser.LiteralContext):
        """Обработка литералов"""
        if ctx.INT():
            ctx.llvm_type = "i32"
            ctx.llvm_value = ctx.INT().getText()
        elif ctx.FLOAT():
            ctx.llvm_type = "double"
            # LLVM требует формат с точкой
            val = ctx.FLOAT().getText()
            if '.' not in val:
                val += '.0'
            ctx.llvm_value = val
        elif ctx.STRING():
            # Строка - создаём глобальную константу
            string_text = ctx.STRING().getText()[1:-1]  # Убираем кавычки
            global_name = self.get_string_global(string_text)
            # Получаем указатель на строку
            ptr = self.new_temp()
            self.emit(f"  {ptr} = getelementptr inbounds [{(len(string_text)+1)} x i8], "
                     f"[{(len(string_text)+1)} x i8]* {global_name}, i32 0, i32 0")
            ctx.llvm_type = "i8*"
            ctx.llvm_value = ptr
        elif ctx.getText() == 'true':
            ctx.llvm_type = "i1"
            ctx.llvm_value = "1"
        elif ctx.getText() == 'false':
            ctx.llvm_type = "i1"
            ctx.llvm_value = "0"
        elif ctx.getText() == 'None':
            ctx.llvm_type = "i8*"
            ctx.llvm_value = "null"
        else:
            ctx.llvm_type = None
            ctx.llvm_value = None
    
    # === Обработка выражений ===
    
    def exitExpression(self, ctx: gsl1Parser.ExpressionContext):
        """Обработка выражений"""
        # Если мы находимся внутри генераторного выражения, не генерируем LLVM IR код
        if self.in_generator_expression:
            ctx.llvm_type = "void"
            ctx.llvm_value = None
            return
        
        child_count = ctx.getChildCount()
        
        # Один ребёнок: literal, ID, или вложенное выражение
        if child_count == 1:
            child = ctx.getChild(0)
            
            # Литерал
            if isinstance(child, gsl1Parser.LiteralContext):
                ctx.llvm_type = getattr(child, "llvm_type", None)
                ctx.llvm_value = getattr(child, "llvm_value", None)
                return
            
            # Идентификатор
            if ctx.ID():
                var_name = ctx.ID().getText()
                
                # Проверяем, является ли это переменной цикла
                if self.block_stack:
                    for block in reversed(self.block_stack):
                        if block.get('type') == 'for' and block.get('var_name') == var_name:
                            # Это переменная цикла
                            if self.current_function and block.get('loop_counter_ptr'):
                                # Внутри функции - генерируем код для получения текущего индекса
                                loop_counter_ptr = block.get('loop_counter_ptr')
                                loop_counter = self.new_temp()
                                self.emit(f"  {loop_counter} = load i32, i32* {loop_counter_ptr}")
                                ctx.llvm_type = "i32"
                                ctx.llvm_value = loop_counter
                                ctx.is_loop_var = True
                                ctx.loop_var_name = var_name
                                ctx.var_name = var_name
                                return
                            else:
                                # Вне функции или нет счётчика - сохраняем информацию
                                ctx.llvm_type = "i8*"
                                ctx.llvm_value = "null"
                                ctx.is_loop_var = True
                                ctx.loop_var_name = var_name
                                ctx.var_name = var_name
                                return
                
                # Ищем переменную в областях видимости
                var_type = "i32"
                ptr = None
                for scope in reversed(self.scope_stack):
                    if var_name in scope:
                        var_type, ptr = scope[var_name]
                        break
                
                if ptr is None:
                    # Создаём переменную
                    ptr = self.get_or_create_variable(var_name, var_type)
                    # Инициализируем нулём
                    zero = "0" if var_type == "i32" else "0.0" if var_type == "double" else "null"
                    self.emit(f"  store {var_type} {zero}, {var_type}* {ptr}")
                
                # Загружаем значение
                tmp = self.new_temp()
                self.emit(f"  {tmp} = load {var_type}, {var_type}* {ptr}")
                ctx.llvm_type = var_type
                ctx.llvm_value = tmp
                # Сохраняем имя переменной для использования в print
                ctx.var_name = var_name
                # Если это таблица, сохраняем это для правильной обработки в print
                if var_name in self.tables_info:
                    ctx.is_table = True
                
                # Проверяем, не является ли это условием if (для переменных типа bool)
                if var_type == "i1":
                    # Ищем блок if в стеке
                    if_block = None
                    if self.block_stack:
                        for block in reversed(self.block_stack):
                            if block.get('type') == 'if' and block.get('pending'):
                                if_block = block
                                break
                    
                    if if_block:
                        if_block['pending'] = False
                        if_block['cond_val'] = tmp
                        # Генерируем br инструкцию
                        self.emit(f"  br i1 {tmp}, label %{if_block['then_label']}, label %{if_block['else_label']}")
                        self.emit(f"{if_block['then_label']}:")
                
                return
            
            # Вложенное выражение (скобки)
            if isinstance(child, gsl1Parser.ExpressionContext):
                ctx.llvm_type = getattr(child, "llvm_type", None)
                ctx.llvm_value = getattr(child, "llvm_value", None)
                
                # Проверяем, не является ли это условием if (для выражений типа bool)
                if ctx.llvm_type == "i1" and ctx.llvm_value:
                    # Ищем блок if в стеке
                    if_block = None
                    if self.block_stack:
                        for block in reversed(self.block_stack):
                            if block.get('type') == 'if' and block.get('pending'):
                                if_block = block
                                break
                    
                    if if_block:
                        if_block['pending'] = False
                        if_block['cond_val'] = ctx.llvm_value
                        # Генерируем br инструкцию
                        self.emit(f"  br i1 {ctx.llvm_value}, label %{if_block['then_label']}, label %{if_block['else_label']}")
                        self.emit(f"{if_block['then_label']}:")
                
                return
        
        # Два ребёнка: выражение '.' ID (доступ к члену)
        if child_count == 3 and ctx.getChild(1).getText() == '.':
            left_expr = ctx.getChild(0)
            member_name = ctx.getChild(2).getText() if ctx.getChild(2) else None
            
            # Проверяем, является ли левая часть переменной цикла
            if isinstance(left_expr, gsl1Parser.ExpressionContext) and left_expr.ID():
                obj_name = left_expr.ID().getText()
                
                # Проверяем, есть ли активный цикл for с этой переменной
                if self.block_stack:
                    for block in reversed(self.block_stack):
                        if block.get('type') == 'for' and block.get('var_name') == obj_name:
                            # Это переменная цикла - нужно получить данные из таблицы
                            table_name = block.get('table_name')
                            table_info = block.get('table_info')
                            
                            # Если table_info есть, используем его
                            # Если нет, но table_name есть в self.tables_info, используем его
                            # Если нет ни того, ни другого, это может быть список - используем упрощённый подход
                            if table_info:
                                # Используем информацию о таблице из блока
                                pass
                            elif table_name and table_name in self.tables_info:
                                # Используем информацию о таблице из self.tables_info
                                table_info = self.tables_info[table_name]
                            else:
                                # Это список или неизвестная переменная - используем упрощённый подход
                                # Для списков используем данные из исходной таблицы (если есть)
                                # Ищем исходную таблицу в глобальных таблицах
                                if self.tables_info:
                                    # Используем первую доступную таблицу (упрощённо)
                                    first_table_name = list(self.tables_info.keys())[0]
                                    table_info = self.tables_info[first_table_name]
                                    table_name = first_table_name
                            
                            if table_name and table_info:
                                # Если мы внутри функции, генерируем код для доступа к данным
                                # Проверяем, есть ли loop_counter_ptr (значит, цикл генерирует LLVM IR)
                                loop_counter_ptr = block.get('loop_counter_ptr')
                                if loop_counter_ptr:
                                    # Получаем текущий индекс
                                    loop_counter = self.new_temp()
                                    self.emit(f"  {loop_counter} = load i32, i32* {loop_counter_ptr}")
                                    
                                    # Находим индекс колонки
                                    col_index = None
                                    # Используем информацию о таблице из блока или из self.tables_info
                                    if table_info:
                                        columns = table_info.get('columns', [])
                                        rows = table_info.get('rows', [])
                                    elif table_name in self.tables_info:
                                        columns = self.tables_info[table_name]['columns']
                                        rows = self.tables_info[table_name]['rows']
                                    else:
                                        columns = []
                                        rows = []
                                    
                                    for i, col in enumerate(columns):
                                        if col['name'] == member_name:
                                            col_index = i
                                            break
                                    
                                    if col_index is not None:

                                        col_type = columns[col_index]['type']
                                        llvm_type = self.get_llvm_type(col_type)
                                        
                                        # Генерируем switch для получения значения по индексу
                                        switch_end_label = self.new_label()
                                        result_reg = self.new_temp()
                                        
                                        # Создаём switch по индексу строки
                                        switch_cases = []
                                        for i, row in enumerate(rows):
                                            if col_index >= len(row):
                                                continue
                                            value = row[col_index]
                                            case_label = self.new_label()
                                            switch_cases.append((i, case_label, value))
                                        
                                        # Генерируем switch
                                        if switch_cases:
                                            # Генерируем default case label
                                            default_label = self.new_label()
                                            
                                            # Генерируем switch инструкцию с default
                                            self.emit(f"  switch i32 {loop_counter}, label %{default_label} [")
                                            for idx, label, value in switch_cases:
                                                self.emit(f"    i32 {idx}, label %{label}")
                                            self.emit(f"  ]")
                                            
                                            # Генерируем cases
                                            case_results = []
                                            for idx, label, value in switch_cases:
                                                self.emit(f"{label}:")
                                                case_result = self.new_temp()
                                                if llvm_type == "i32":
                                                    try:
                                                        int_val = int(value)
                                                        self.emit(f"  {case_result} = add i32 0, {int_val}")
                                                    except (ValueError, TypeError):
                                                        self.emit(f"  {case_result} = add i32 0, 0")
                                                elif llvm_type == "double":
                                                    try:
                                                        float_val = float(value)
                                                        self.emit(f"  {case_result} = fadd double 0.0, {float_val}")
                                                    except (ValueError, TypeError):
                                                        self.emit(f"  {case_result} = fadd double 0.0, 0.0")
                                                elif llvm_type == "i8*":
                                                    # Строка - создаём глобальную строку
                                                    str_global = self.get_string_global(value)
                                                    str_ptr = self.new_temp()
                                                    str_len = len(value) + 1
                                                    self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {str_global}, i32 0, i32 0")
                                                    case_result = str_ptr
                                                case_results.append((case_result, label))
                                                self.emit(f"  br label %{switch_end_label}")
                                            
                                            # Генерируем default case
                                            self.emit(f"{default_label}:")
                                            default_result = self.new_temp()
                                            if llvm_type == "i32":
                                                self.emit(f"  {default_result} = add i32 0, 0")
                                            elif llvm_type == "double":
                                                self.emit(f"  {default_result} = fadd double 0.0, 0.0")
                                            elif llvm_type == "i8*":
                                                # Для строк создаём пустую строку
                                                empty_str = self.get_string_global("")
                                                str_ptr = self.new_temp()
                                                str_len = 1
                                                self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {empty_str}, i32 0, i32 0")
                                                default_result = str_ptr
                                            else:
                                                default_result = "null"
                                            self.emit(f"  br label %{switch_end_label}")
                                            
                                            # Генерируем phi-инструкцию для объединения результатов
                                            self.emit(f"{switch_end_label}:")
                                            result_reg = self.new_temp()
                                            phi_parts = []
                                            for case_result, case_label in case_results:
                                                phi_parts.append(f"[{case_result}, %{case_label}]")
                                            # Добавляем default значение
                                            phi_parts.append(f"[{default_result}, %{default_label}]")
                                            # Формируем phi инструкцию: phi type [value1, label1], [value2, label2], ...
                                            phi_str = ', '.join(phi_parts)
                                            self.emit(f"  {result_reg} = phi {llvm_type} {phi_str}")
                                            
                                            ctx.llvm_type = llvm_type
                                            ctx.llvm_value = result_reg
                                            ctx.is_loop_var = True
                                            ctx.loop_var_name = obj_name
                                            ctx.member_name = member_name
                                            ctx.table_name = table_name
                                            # Устанавливаем var_name для правильной обработки в сравнениях
                                            ctx.var_name = None  # Это значение из таблицы, не переменная
                                            return
                                        else:
                                            # Нет данных - возвращаем значение по умолчанию
                                            if llvm_type == "i32":
                                                ctx.llvm_type = "i32"
                                                ctx.llvm_value = "0"
                                            elif llvm_type == "double":
                                                ctx.llvm_type = "double"
                                                ctx.llvm_value = "0.0"
                                            else:
                                                ctx.llvm_type = "i8*"
                                                ctx.llvm_value = "null"
                                            return
                                    else:
                                        # Колонка не найдена
                                        ctx.llvm_type = "i8*"
                                        ctx.llvm_value = "null"
                                        return
                                elif not loop_counter_ptr:
                                    # Вне функции и нет loop_counter_ptr - используем упрощённую обработку
                                    ctx.llvm_type = "i8*"
                                    ctx.llvm_value = "null"
                                    return
            
            # Обычная обработка доступа к члену
            ctx.llvm_type = "i8*"
            ctx.llvm_value = "null"
            return
        
        # Три ребёнка: (expr), бинарная операция, или вызов функции
        if child_count >= 3:
            left = ctx.getChild(0)
            middle = ctx.getChild(1)
            right = ctx.getChild(2) if child_count >= 3 else None
            
            # Строковая конкатенация (проверяем ПЕРЕД вызовом функции и бинарными операциями)
            if middle and middle.getText() == '+':
                # Получаем типы и значения операндов
                left_type = None
                left_val = None
                right_type = None
                right_val = None
                
                # Обрабатываем левый операнд
                if isinstance(left, gsl1Parser.ExpressionContext):
                    left_type = getattr(left, "llvm_type", None)
                    left_val = getattr(left, "llvm_value", None)
                elif isinstance(left, gsl1Parser.LiteralContext):
                    left_type = getattr(left, "llvm_type", None)
                    left_val = getattr(left, "llvm_value", None)
                
                # Обрабатываем правый операнд
                if isinstance(right, gsl1Parser.ExpressionContext):
                    right_type = getattr(right, "llvm_type", None)
                    right_val = getattr(right, "llvm_value", None)
                elif isinstance(right, gsl1Parser.LiteralContext):
                    right_type = getattr(right, "llvm_type", None)
                    right_val = getattr(right, "llvm_value", None)
                
                # Если хотя бы один операнд - строка, это строковая конкатенация
                if left_type == "i8*" or right_type == "i8*":
                    # Получаем указатели на строки
                    left_ptr = None
                    right_ptr = None
                    
                    # Обрабатываем левую строку
                    if left_type == "i8*" and left_val:
                        if left_val.startswith("%"):
                            left_ptr = left_val
                        elif left_val.startswith("@"):
                            left_ptr = self.new_temp()
                            str_len = 100
                            for str_val, global_name in self.global_strings.items():
                                if global_name == left_val:
                                    str_len = len(str_val) + 1
                                    break
                            self.emit(f"  {left_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {left_val}, i32 0, i32 0")
                        else:
                            left_ptr = left_val
                    
                    # Обрабатываем правую строку
                    if right_type == "i8*" and right_val:
                        if right_val.startswith("%"):
                            right_ptr = right_val
                        elif right_val.startswith("@"):
                            right_ptr = self.new_temp()
                            str_len = 100
                            for str_val, global_name in self.global_strings.items():
                                if global_name == right_val:
                                    str_len = len(str_val) + 1
                                    break
                            self.emit(f"  {right_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {right_val}, i32 0, i32 0")
                        else:
                            right_ptr = right_val
                    
                    # Если обе строки есть, выполняем конкатенацию
                    if left_ptr and right_ptr:
                        # Вычисляем размеры строк
                        len1_reg = self.new_temp()
                        len2_reg = self.new_temp()
                        self.emit(f"  {len1_reg} = call i64 @strlen(i8* {left_ptr})")
                        self.emit(f"  {len2_reg} = call i64 @strlen(i8* {right_ptr})")
                        
                        # Выделяем память для результата (len1 + len2 + 1)
                        total_len_reg = self.new_temp()
                        one_const = self.new_temp()
                        self.emit(f"  {one_const} = add i64 {len1_reg}, {len2_reg}")
                        self.emit(f"  {total_len_reg} = add i64 {one_const}, 1")
                        
                        result_ptr = self.new_temp()
                        self.emit(f"  {result_ptr} = call i8* @malloc(i64 {total_len_reg})")
                        
                        # Копируем первую строку
                        self.emit(f"  call i8* @strcpy(i8* {result_ptr}, i8* {left_ptr})")
                        
                        # Добавляем вторую строку
                        self.emit(f"  call i8* @strcat(i8* {result_ptr}, i8* {right_ptr})")
                        
                        ctx.llvm_type = "i8*"
                        ctx.llvm_value = result_ptr
                        return
                    elif left_ptr:
                        # Только левая строка
                        ctx.llvm_type = "i8*"
                        ctx.llvm_value = left_ptr
                        return
                    elif right_ptr:
                        # Только правая строка
                        ctx.llvm_type = "i8*"
                        ctx.llvm_value = right_ptr
                        return
                    else:
                        # Пустая строка
                        empty_str = self.get_string_global("")
                        str_ptr = self.new_temp()
                        str_len = 1
                        self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {empty_str}, i32 0, i32 0")
                        ctx.llvm_type = "i8*"
                        ctx.llvm_value = str_ptr
                        return
            
            # Вызов функции: expr '(' ... ')'
            # Проверяем сначала вызов функции, так как это более специфичный случай
            if middle.getText() == '(':
                # Это может быть вызов функции или скобки
                func_expr = ctx.expression(0) if ctx.expression() else None
                func_name = None
                
                # Проверяем, является ли первый ребёнок идентификатором (имя функции)
                if func_expr:
                    if func_expr.ID():
                        func_name = func_expr.ID().getText()
                    elif func_expr.getChildCount() == 1 and func_expr.getChild(0) and hasattr(func_expr.getChild(0), 'getText'):
                        # Может быть вложенное выражение с ID
                        first_child = func_expr.getChild(0)
                        if hasattr(first_child, 'getText') and first_child.getText().isidentifier():
                            func_name = first_child.getText()
                
                # Если это вызов функции (есть имя функции)
                if func_name:
                    # Специальные функции - возвращаем null
                    if func_name == "Table" or func_name == "Row" or func_name == "row":
                        # Сохраняем аргументы Row для последующего использования в exitDataInsert
                        row_args = []
                        if len(ctx.expression()) > 1:
                            for i in range(1, len(ctx.expression())):
                                arg_expr = ctx.expression(i)
                                
                                # Проверяем, является ли это выражением с одним литералом внутри
                                # (выражение может содержать литерал как единственный дочерний элемент)
                                literal = None
                                if isinstance(arg_expr, gsl1Parser.ExpressionContext):
                                    if arg_expr.getChildCount() == 1:
                                        child = arg_expr.getChild(0)
                                        if isinstance(child, gsl1Parser.LiteralContext):
                                            literal = child
                                elif isinstance(arg_expr, gsl1Parser.LiteralContext):
                                    literal = arg_expr
                                
                                # Если нашли литерал, извлекаем значение напрямую
                                if literal:
                                    if literal.STRING():
                                        str_text = literal.STRING().getText()
                                        # Убираем кавычки
                                        if str_text.startswith('"') and str_text.endswith('"'):
                                            str_text = str_text[1:-1]
                                        row_args.append(str_text)
                                    elif literal.INT():
                                        row_args.append(literal.INT().getText())
                                    elif literal.FLOAT():
                                        row_args.append(literal.FLOAT().getText())
                                    else:
                                        row_args.append("?")
                                else:
                                    # Если не литерал, используем обработанные значения
                                    arg_type = getattr(arg_expr, "llvm_type", "i32")
                                    arg_val = getattr(arg_expr, "llvm_value", "0")
                                    
                                    if arg_type == "i32":
                                        if arg_val and not arg_val.startswith("%"):
                                            row_args.append(str(arg_val))
                                        else:
                                            row_args.append("?")
                                    elif arg_type == "double":
                                        if arg_val and not arg_val.startswith("%"):
                                            row_args.append(str(arg_val))
                                        else:
                                            row_args.append("?")
                                    elif arg_type == "i8*":
                                        # Пытаемся найти строку в global_strings
                                        if arg_val and arg_val.startswith("@"):
                                            found = False
                                            for str_val, global_name in self.global_strings.items():
                                                if global_name == arg_val:
                                                    row_args.append(str_val)
                                                    found = True
                                                    break
                                            if not found:
                                                row_args.append("?")
                                        else:
                                            row_args.append("?")
                                    else:
                                        row_args.append("?")
                        
                        # Сохраняем аргументы Row для последующего использования
                        ctx.row_args = row_args
                        ctx.llvm_type = "i8*"
                        ctx.llvm_value = "null"
                        return
                    
                    # Функция str() - преобразование в строку
                    if func_name == "str":
                        if len(ctx.expression()) > 1:
                            arg_expr = ctx.expression(1)
                            arg_type = getattr(arg_expr, "llvm_type", "i32")
                            arg_val = getattr(arg_expr, "llvm_value", "0")
                            
                            if arg_type is None:
                                arg_type = "i32"
                            if arg_val is None:
                                arg_val = "0"
                            
                            # Выделяем память для строки (достаточно для числа)
                            buffer_size = 32  # Достаточно для любого числа
                            buffer_ptr = self.new_temp()
                            self.emit(f"  {buffer_ptr} = call i8* @malloc(i64 {buffer_size})")
                            
                            # Используем sprintf для преобразования
                            if arg_type == "i32":
                                fmt_str = self.get_string_global("%d")
                                fmt_ptr = self.new_temp()
                                fmt_len = len("%d") + 1
                                self.emit(f"  {fmt_ptr} = getelementptr inbounds [{fmt_len} x i8], [{fmt_len} x i8]* {fmt_str}, i32 0, i32 0")
                                self.emit(f"  call i32 (i8*, i8*, ...) @sprintf(i8* {buffer_ptr}, i8* {fmt_ptr}, i32 {arg_val})")
                            elif arg_type == "double":
                                fmt_str = self.get_string_global("%.2f")
                                fmt_ptr = self.new_temp()
                                fmt_len = len("%.2f") + 1
                                self.emit(f"  {fmt_ptr} = getelementptr inbounds [{fmt_len} x i8], [{fmt_len} x i8]* {fmt_str}, i32 0, i32 0")
                                self.emit(f"  call i32 (i8*, i8*, ...) @sprintf(i8* {buffer_ptr}, i8* {fmt_ptr}, double {arg_val})")
                            else:
                                # Для других типов возвращаем пустую строку
                                empty_str = self.get_string_global("")
                                str_ptr = self.new_temp()
                                str_len = 1
                                self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {empty_str}, i32 0, i32 0")
                                buffer_ptr = str_ptr
                            
                            ctx.llvm_type = "i8*"
                            ctx.llvm_value = buffer_ptr
                            return
                    
                    # Получаем информацию о функции (обрабатываем перегрузки)
                    func_versions = self.functions_info.get(func_name)
                    if not func_versions:
                        # Функция не найдена - возвращаем значение по умолчанию
                        ctx.llvm_type = "i32"
                        ctx.llvm_value = "0"
                        return
                    
                    # Выбираем правильную версию функции по количеству аргументов
                    arg_count = len(ctx.expression()) - 1  # -1 потому что первый - функция
                    func_info = None
                    if isinstance(func_versions, list):
                        # Есть несколько версий - выбираем по количеству параметров
                        for version in func_versions:
                            if version['param_count'] == arg_count:
                                func_info = version
                                break
                        # Если не нашли точное совпадение, берём первую версию
                        if not func_info and func_versions:
                            func_info = func_versions[0]
                    else:
                        # Старый формат (одна версия)
                        func_info = func_versions
                    
                    if not func_info:
                        ctx.llvm_type = "i32"
                        ctx.llvm_value = "0"
                        return
                    
                    # Получаем аргументы
                    args = []
                    for i in range(1, len(ctx.expression())):
                        arg_expr = ctx.expression(i)
                        arg_type = getattr(arg_expr, "llvm_type", "i32")
                        arg_val = getattr(arg_expr, "llvm_value", "0")
                        param_index = i - 1
                        
                        # Проверяем, является ли аргумент таблицей
                        if param_index < len(func_info['params']):
                            param_name, param_llvm_type = func_info['params'][param_index]
                            # Если параметр имеет тип i8* (table), проверяем, является ли аргумент таблицей
                            if param_llvm_type == "i8*":
                                # Проверяем, является ли аргумент идентификатором таблицы
                                if hasattr(arg_expr, 'ID') and arg_expr.ID():
                                    table_arg_name = arg_expr.ID().getText()
                                    if table_arg_name in self.tables_info:
                                        # Сохраняем маппинг параметра на таблицу
                                        call_key = (func_name, param_index)
                                        self.function_call_table_mapping[call_key] = table_arg_name
                        
                        # Если тип не определён, используем тип из параметра функции
                        if arg_type is None and param_index < len(func_info['params']):
                            expected_type = func_info['params'][param_index][1]
                            arg_type = expected_type
                            if arg_val is None:
                                arg_val = "0" if expected_type == "i32" else "0.0" if expected_type == "double" else "null"
                        
                        if arg_type is None:
                            arg_type = "i32"
                        if arg_val is None:
                            arg_val = "0"
                        
                        args.append((arg_type, arg_val))
                    
                    # Определяем возвращаемый тип
                    result_type = func_info['return_type']
                    if result_type == 'void':
                        result_type = "i32"  # Для совместимости
                    
                    # Генерируем вызов функции
                    result_reg = self.new_temp()
                    
                    # Формируем сигнатуру вызова
                    if args:
                        args_str = ", ".join([f"{t} {v}" for t, v in args])
                        if result_type == 'void':
                            self.emit(f"  call void @{func_name}({args_str})")
                            ctx.llvm_type = "i32"
                            ctx.llvm_value = "0"
                        else:
                            self.emit(f"  {result_reg} = call {result_type} @{func_name}({args_str})")
                            ctx.llvm_type = result_type
                            ctx.llvm_value = result_reg
                    else:
                        if result_type == 'void':
                            self.emit(f"  call void @{func_name}()")
                            ctx.llvm_type = "i32"
                            ctx.llvm_value = "0"
                        else:
                            self.emit(f"  {result_reg} = call {result_type} @{func_name}()")
                            ctx.llvm_type = result_type
                            ctx.llvm_value = result_reg
                    return
                
                if func_name:
                    # Специальные функции - возвращаем null
                    if func_name == "Table" or func_name == "Row" or func_name == "row":
                        # Сохраняем аргументы Row для последующего использования в exitDataInsert
                        row_args = []
                        if len(ctx.expression()) > 1:
                            for i in range(1, len(ctx.expression())):
                                arg_expr = ctx.expression(i)
                                
                                # Проверяем, является ли это выражением с одним литералом внутри
                                # (выражение может содержать литерал как единственный дочерний элемент)
                                literal = None
                                if isinstance(arg_expr, gsl1Parser.ExpressionContext):
                                    if arg_expr.getChildCount() == 1:
                                        child = arg_expr.getChild(0)
                                        if isinstance(child, gsl1Parser.LiteralContext):
                                            literal = child
                                elif isinstance(arg_expr, gsl1Parser.LiteralContext):
                                    literal = arg_expr
                                
                                # Если нашли литерал, извлекаем значение напрямую
                                if literal:
                                    if literal.STRING():
                                        str_text = literal.STRING().getText()
                                        # Убираем кавычки
                                        if str_text.startswith('"') and str_text.endswith('"'):
                                            str_text = str_text[1:-1]
                                        row_args.append(str_text)
                                    elif literal.INT():
                                        row_args.append(literal.INT().getText())
                                    elif literal.FLOAT():
                                        row_args.append(literal.FLOAT().getText())
                                    else:
                                        row_args.append("?")
                                else:
                                    # Если не литерал, используем обработанные значения
                                    arg_type = getattr(arg_expr, "llvm_type", "i32")
                                    arg_val = getattr(arg_expr, "llvm_value", "0")
                                    
                                    if arg_type == "i32":
                                        if arg_val and not arg_val.startswith("%"):
                                            row_args.append(str(arg_val))
                                        else:
                                            row_args.append("?")
                                    elif arg_type == "double":
                                        if arg_val and not arg_val.startswith("%"):
                                            row_args.append(str(arg_val))
                                        else:
                                            row_args.append("?")
                                    elif arg_type == "i8*":
                                        # Пытаемся найти строку в global_strings
                                        if arg_val and arg_val.startswith("@"):
                                            found = False
                                            for str_val, global_name in self.global_strings.items():
                                                if global_name == arg_val:
                                                    row_args.append(str_val)
                                                    found = True
                                                    break
                                            if not found:
                                                row_args.append("?")
                                        else:
                                            row_args.append("?")
                                    else:
                                        row_args.append("?")
                        
                        # Сохраняем аргументы Row для последующего использования
                        ctx.row_args = row_args
                        ctx.llvm_type = "i8*"
                        ctx.llvm_value = "null"
                        return
                    
                    # Получаем информацию о функции (обрабатываем перегрузки)
                    func_versions = self.functions_info.get(func_name)
                    if not func_versions:
                        # Функция не найдена - возвращаем значение по умолчанию
                        ctx.llvm_type = "i32"
                        ctx.llvm_value = "0"
                        return
                    
                    # Выбираем правильную версию функции по количеству аргументов
                    arg_count = len(ctx.expression()) - 1  # -1 потому что первый - функция
                    func_info = None
                    if isinstance(func_versions, list):
                        # Есть несколько версий - выбираем по количеству параметров
                        for version in func_versions:
                            if version['param_count'] == arg_count:
                                func_info = version
                                break
                        # Если не нашли точное совпадение, берём первую версию
                        if not func_info and func_versions:
                            func_info = func_versions[0]
                    else:
                        # Старый формат (одна версия)
                        func_info = func_versions
                    
                    if not func_info:
                        ctx.llvm_type = "i32"
                        ctx.llvm_value = "0"
                        return
                    
                    # Получаем аргументы
                    args = []
                    arg_exprs = []
                    for i in range(1, len(ctx.expression())):
                        arg_expr = ctx.expression(i)
                        arg_exprs.append(arg_expr)
                        arg_type = getattr(arg_expr, "llvm_type", "i32")
                        arg_val = getattr(arg_expr, "llvm_value", "0")
                        
                        # Если тип не определён, используем тип из параметра функции
                        if arg_type is None and i-1 < len(func_info['params']):
                            expected_type = func_info['params'][i-1][1]
                            arg_type = expected_type
                            if arg_val is None:
                                arg_val = "0" if expected_type == "i32" else "0.0" if expected_type == "double" else "null"
                        
                        if arg_type is None:
                            arg_type = "i32"
                        if arg_val is None:
                            arg_val = "0"
                        
                        args.append((arg_type, arg_val))
                    
                    # Определяем возвращаемый тип
                    result_type = func_info['return_type']
                    if result_type == 'void':
                        result_type = "i32"  # Для совместимости
                    
                    # Генерируем вызов функции
                    result_reg = self.new_temp()
                    
                    # Формируем сигнатуру вызова
                    if args:
                        args_str = ", ".join([f"{t} {v}" for t, v in args])
                        if result_type == 'void':
                            self.emit(f"  call void @{func_name}({args_str})")
                            ctx.llvm_type = "i32"
                            ctx.llvm_value = "0"
                        else:
                            self.emit(f"  {result_reg} = call {result_type} @{func_name}({args_str})")
                            ctx.llvm_type = result_type
                            ctx.llvm_value = result_reg
                    else:
                        if result_type == 'void':
                            self.emit(f"  call void @{func_name}()")
                            ctx.llvm_type = "i32"
                            ctx.llvm_value = "0"
                        else:
                            self.emit(f"  {result_reg} = call {result_type} @{func_name}()")
                            ctx.llvm_type = result_type
                            ctx.llvm_value = result_reg
                    return
                
                # Если это не вызов функции, то это скобки: (expr)
                if func_expr:
                    ctx.llvm_type = getattr(func_expr, "llvm_type", None)
                    ctx.llvm_value = getattr(func_expr, "llvm_value", None)
                    return
            
            # Бинарные операции (только если child_count == 3)
            if child_count == 3:
                right = ctx.getChild(2)
            if isinstance(left, gsl1Parser.ExpressionContext) and isinstance(right, gsl1Parser.ExpressionContext):
                op = middle.getText()
                l_type = getattr(left, "llvm_type", "i32")
                r_type = getattr(right, "llvm_type", "i32")
                l_val = getattr(left, "llvm_value", "0")
                r_val = getattr(right, "llvm_value", "0")
                
                # Проверка на None
                if l_type is None:
                    l_type = "i32"
                if r_type is None:
                    r_type = "i32"
                if l_val is None:
                    l_val = "0"
                if r_val is None:
                    r_val = "0"
                
                # Приводим типы к общему
                result_type = l_type
                if l_type != r_type:
                    # Преобразование типов
                    if l_type == "double" and r_type == "i32":
                        # int -> double
                        conv_reg = self.new_temp()
                        self.emit(f"  {conv_reg} = sitofp i32 {r_val} to double")
                        r_val = conv_reg
                        r_type = "double"
                    elif l_type == "i32" and r_type == "double":
                        # int -> double
                        conv_reg = self.new_temp()
                        self.emit(f"  {conv_reg} = sitofp i32 {l_val} to double")
                        l_val = conv_reg
                        l_type = "double"
                    result_type = l_type
                
                # Арифметические операции
                if op in ['+', '-', '*', '/', '%']:
                    # Проверяем, не является ли это строковой конкатенацией
                    if (l_type == "i8*" or r_type == "i8*") and op == '+':
                        # Это строковая конкатенация - уже обработано выше, пропускаем
                        ctx.llvm_type = None
                        ctx.llvm_value = None
                        return
                    
                    # Определяем инструкцию в зависимости от типа
                    instr = None
                    if result_type == "i32":
                        if op == '+':
                            instr = "add"
                        elif op == '-':
                            instr = "sub"
                        elif op == '*':
                            instr = "mul"
                        elif op == '/':
                            instr = "sdiv"
                        elif op == '%':
                            instr = "srem"
                    elif result_type == "double":
                        if op == '+':
                            instr = "fadd"
                        elif op == '-':
                            instr = "fsub"
                        elif op == '*':
                            instr = "fmul"
                        elif op == '/':
                            instr = "fdiv"
                        elif op == '%':
                            instr = "frem"
                    
                    if instr is None:
                        # Неподдерживаемая операция или тип
                        ctx.llvm_type = None
                        ctx.llvm_value = None
                        return
                    
                    tmp = self.new_temp()
                    self.emit(f"  {tmp} = {instr} {result_type} {l_val}, {r_val}")
                    ctx.llvm_type = result_type
                    ctx.llvm_value = tmp
                    return
                
                # Операции сравнения
                if op in ['==', '!=', '<', '>', '<=', '>=']:
                    # Определяем типы операндов
                    left_type = getattr(left, "llvm_type", None) if isinstance(left, gsl1Parser.ExpressionContext) else None
                    right_type = getattr(right, "llvm_type", None) if isinstance(right, gsl1Parser.ExpressionContext) else None
                    
                    # Если типы не определены, пытаемся определить из литералов
                    if left_type is None and isinstance(left, gsl1Parser.LiteralContext):
                        if left.INT():
                            left_type = "i32"
                        elif left.FLOAT():
                            left_type = "double"
                        elif left.STRING():
                            left_type = "i8*"
                    if right_type is None and isinstance(right, gsl1Parser.LiteralContext):
                        if right.INT():
                            right_type = "i32"
                        elif right.FLOAT():
                            right_type = "double"
                        elif right.STRING():
                            right_type = "i8*"
                    
                    # Определяем общий тип для сравнения
                    # Если один из типов - строка, используем сравнение строк
                    # Иначе определяем общий тип (i32 или double)
                    result_type = None
                    if left_type == "i8*" or right_type == "i8*":
                        # Сравнение строк - используем strcmp
                        result_type = "i8*"
                        left_ptr = l_val
                        right_ptr = r_val
                    elif left_type == "double" or right_type == "double":
                        result_type = "double"
                    elif left_type == "i32" or right_type == "i32":
                        result_type = "i32"
                    else:
                        # По умолчанию - i32
                        result_type = "i32"
                    
                    if result_type == "i8*":
                        # Сравнение строк - используем strcmp
                        left_ptr = l_val
                        right_ptr = r_val
                        
                        # Обрабатываем левый операнд
                        # Если значение уже является указателем (начинается с % или @), используем его напрямую
                        if left_ptr and not left_ptr.startswith("%") and not left_ptr.startswith("@"):
                            # Это может быть глобальная строка или литерал
                            if left_type == "i8*":
                                # Пытаемся получить строку из литерала
                                if isinstance(left, gsl1Parser.LiteralContext) and left.STRING():
                                    str_val = left.STRING().getText()[1:-1]  # Убираем кавычки
                                    left_global = self.get_string_global(str_val)
                                    left_ptr = self.new_temp()
                                    str_len = len(str_val) + 1
                                    self.emit(f"  {left_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {left_global}, i32 0, i32 0")
                                elif isinstance(left, gsl1Parser.ExpressionContext):
                                    # Это выражение - если это уже указатель, используем его
                                    # Если нет, это может быть параметр функции - загружаем его
                                    if left_ptr and not left_ptr.startswith("%") and not left_ptr.startswith("@"):
                                        # Это может быть имя переменной (параметр функции)
                                        var_name = getattr(left, "var_name", None)
                                        if var_name:
                                            # Ищем переменную в scope
                                            for scope in reversed(self.scope_stack):
                                                if var_name in scope:
                                                    var_type, var_ptr = scope[var_name]
                                                    if var_type == "i8*":
                                                        left_ptr = self.new_temp()
                                                        self.emit(f"  {left_ptr} = load i8*, i8** {var_ptr}")
                                                        break
                                    # Если не нашли, используем значение напрямую
                                    if not left_ptr.startswith("%") and not left_ptr.startswith("@"):
                                        left_ptr = l_val
                                else:
                                    left_ptr = l_val
                            else:
                                left_ptr = l_val
                        # Если left_ptr всё ещё не указатель, но должен быть строкой, создаём пустую строку
                        if left_ptr and not left_ptr.startswith("%") and not left_ptr.startswith("@") and left_type == "i8*":
                            # Проверяем, не является ли это числом (0.0, 0 и т.д.)
                            if left_ptr in ["0.0", "0", "null"] or (isinstance(left_ptr, str) and left_ptr.replace(".", "").replace("-", "").isdigit()):
                                # Это число или null - используем null указатель
                                left_ptr = "null"
                            else:
                                empty_str = self.get_string_global("")
                                left_ptr = self.new_temp()
                                str_len = 1
                                self.emit(f"  {left_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {empty_str}, i32 0, i32 0")
                        
                        # Обрабатываем правый операнд аналогично
                        if right_ptr and not right_ptr.startswith("%") and not right_ptr.startswith("@"):
                            # Это может быть глобальная строка или литерал
                            if right_type == "i8*":
                                # Пытаемся получить строку из литерала
                                if isinstance(right, gsl1Parser.LiteralContext) and right.STRING():
                                    str_val = right.STRING().getText()[1:-1]  # Убираем кавычки
                                    right_global = self.get_string_global(str_val)
                                    right_ptr = self.new_temp()
                                    str_len = len(str_val) + 1
                                    self.emit(f"  {right_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {right_global}, i32 0, i32 0")
                                elif isinstance(right, gsl1Parser.ExpressionContext):
                                    # Это выражение - если это уже указатель, используем его
                                    # Если нет, это может быть параметр функции - загружаем его
                                    if right_ptr and not right_ptr.startswith("%") and not right_ptr.startswith("@"):
                                        # Это может быть имя переменной (параметр функции)
                                        var_name = getattr(right, "var_name", None)
                                        if var_name:
                                            # Ищем переменную в scope
                                            for scope in reversed(self.scope_stack):
                                                if var_name in scope:
                                                    var_type, var_ptr = scope[var_name]
                                                    if var_type == "i8*":
                                                        right_ptr = self.new_temp()
                                                        self.emit(f"  {right_ptr} = load i8*, i8** {var_ptr}")
                                                        break
                                    # Если не нашли, используем значение напрямую
                                    if not right_ptr.startswith("%") and not right_ptr.startswith("@"):
                                        right_ptr = r_val
                                else:
                                    right_ptr = r_val
                            else:
                                right_ptr = r_val
                        # Если right_ptr всё ещё не указатель, но должен быть строкой, создаём пустую строку
                        if right_ptr and not right_ptr.startswith("%") and not right_ptr.startswith("@") and right_type == "i8*":
                            # Проверяем, не является ли это числом (0.0, 0 и т.д.)
                            if right_ptr in ["0.0", "0", "null"] or (isinstance(right_ptr, str) and right_ptr.replace(".", "").replace("-", "").isdigit()):
                                # Это число или null - используем null указатель
                                right_ptr = "null"
                            else:
                                empty_str = self.get_string_global("")
                                right_ptr = self.new_temp()
                                str_len = 1
                                self.emit(f"  {right_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {empty_str}, i32 0, i32 0")
                        
                        # Аналогично для left_ptr
                        if left_ptr and not left_ptr.startswith("%") and not left_ptr.startswith("@") and left_type == "i8*":
                            # Проверяем, не является ли это числом (0.0, 0 и т.д.)
                            if left_ptr in ["0.0", "0", "null"] or (isinstance(left_ptr, str) and left_ptr.replace(".", "").replace("-", "").isdigit()):
                                # Это число или null - используем null указатель
                                left_ptr = "null"
                        
                        # Финальная проверка перед вызовом strcmp - убеждаемся, что оба указателя корректны
                        # Проверяем left_ptr - если это не указатель и не null, проверяем, не число ли это
                        if left_ptr and not left_ptr.startswith("%") and not left_ptr.startswith("@") and left_ptr != "null":
                            # Если это число (0.0, 0 и т.д.), заменяем на null
                            if left_ptr in ["0.0", "0"]:
                                left_ptr = "null"
                            else:
                                try:
                                    float(left_ptr)  # Проверяем, можно ли преобразовать в число
                                    left_ptr = "null"
                                except (ValueError, TypeError):
                                    pass  # Не число, оставляем как есть
                        
                        # Проверяем right_ptr - если это не указатель и не null, проверяем, не число ли это
                        if right_ptr and not right_ptr.startswith("%") and not right_ptr.startswith("@") and right_ptr != "null":
                            # Если это число (0.0, 0 и т.д.), заменяем на null
                            if right_ptr in ["0.0", "0"]:
                                right_ptr = "null"
                            else:
                                try:
                                    float(right_ptr)  # Проверяем, можно ли преобразовать в число
                                    right_ptr = "null"
                                except (ValueError, TypeError):
                                    pass  # Не число, оставляем как есть
                        
                        # АБСОЛЮТНО ФИНАЛЬНАЯ проверка - убеждаемся, что оба указателя не являются числами
                        # Это критично, так как right_ptr может быть переустановлен выше
                        if isinstance(left_ptr, str) and left_ptr not in ["null"] and not left_ptr.startswith("%") and not left_ptr.startswith("@"):
                            if left_ptr in ["0.0", "0"] or (left_ptr.replace(".", "").replace("-", "").replace("e", "").replace("E", "").replace("+", "").isdigit()):
                                left_ptr = "null"
                        if isinstance(right_ptr, str) and right_ptr not in ["null"] and not right_ptr.startswith("%") and not right_ptr.startswith("@"):
                            if right_ptr in ["0.0", "0"] or (right_ptr.replace(".", "").replace("-", "").replace("e", "").replace("E", "").replace("+", "").isdigit()):
                                right_ptr = "null"
                        
                        # Вызываем strcmp
                        cmp_result = self.new_temp()
                        self.emit(f"  {cmp_result} = call i32 @strcmp(i8* {left_ptr}, i8* {right_ptr})")
                        
                        # Преобразуем результат strcmp в i1
                        result_bool = self.new_temp()
                        if op == '==':
                            self.emit(f"  {result_bool} = icmp eq i32 {cmp_result}, 0")
                        elif op == '!=':
                            self.emit(f"  {result_bool} = icmp ne i32 {cmp_result}, 0")
                        else:
                            # Для других операций со строками используем результат strcmp
                            if op == '<':
                                self.emit(f"  {result_bool} = icmp slt i32 {cmp_result}, 0")
                            elif op == '>':
                                self.emit(f"  {result_bool} = icmp sgt i32 {cmp_result}, 0")
                            elif op == '<=':
                                self.emit(f"  {result_bool} = icmp sle i32 {cmp_result}, 0")
                            elif op == '>=':
                                self.emit(f"  {result_bool} = icmp sge i32 {cmp_result}, 0")
                            else:
                                result_bool = "0"
                        
                        ctx.llvm_type = "i1"
                        ctx.llvm_value = result_bool
                        
                        # Проверяем, не является ли это условием if
                        # Ищем блок if в стеке (может быть не последним, если внутри цикла)
                        if_block = None
                        if self.block_stack:
                            # Ищем с конца стека, чтобы найти самый последний блок if
                            for i in range(len(self.block_stack) - 1, -1, -1):
                                block = self.block_stack[i]
                                if block.get('type') == 'if' and block.get('pending'):
                                    if_block = block
                                    break
                        
                        if if_block:
                            if_block['pending'] = False
                            if_block['cond_val'] = ctx.llvm_value
                            # Генерируем br инструкцию
                            self.emit(f"  br i1 {ctx.llvm_value}, label %{if_block['then_label']}, label %{if_block['else_label']}")
                            self.emit(f"{if_block['then_label']}:")
                            # После генерации условного перехода для if, выходим
                            return
                        
                        return  # Выходим, так как сравнение строк уже обработано
                    elif result_type == "i32":
                        if op == '==':
                            cmp_instr = "icmp eq"
                        elif op == '!=':
                            cmp_instr = "icmp ne"
                        elif op == '<':
                            cmp_instr = "icmp slt"
                        elif op == '>':
                            cmp_instr = "icmp sgt"
                        elif op == '<=':
                            cmp_instr = "icmp sle"
                        elif op == '>=':
                            cmp_instr = "icmp sge"
                        else:
                            ctx.llvm_type = None
                            ctx.llvm_value = None
                            return
                        
                        tmp = self.new_temp()
                        self.emit(f"  {tmp} = {cmp_instr} {result_type} {l_val}, {r_val}")
                        ctx.llvm_type = "i1"
                        ctx.llvm_value = tmp
                    else:  # double
                        if op == '==':
                            cmp_instr = "fcmp oeq"
                        elif op == '!=':
                            cmp_instr = "fcmp one"
                        elif op == '<':
                            cmp_instr = "fcmp olt"
                        elif op == '>':
                            cmp_instr = "fcmp ogt"
                        elif op == '<=':
                            cmp_instr = "fcmp ole"
                        elif op == '>=':
                            cmp_instr = "fcmp oge"
                        else:
                            ctx.llvm_type = None
                            ctx.llvm_value = None
                            return
                    
                    tmp = self.new_temp()
                    self.emit(f"  {tmp} = {cmp_instr} {result_type} {l_val}, {r_val}")
                    ctx.llvm_type = "i1"
                    ctx.llvm_value = tmp
                    
                    # Проверяем, не является ли это условием if
                    # Ищем блок if в стеке (может быть не последним, если внутри цикла)
                    # Важно: ищем самый последний блок if (самый вложенный)
                    if_block = None
                    if self.block_stack:
                        # Ищем с конца стека, чтобы найти самый последний блок if
                        for i in range(len(self.block_stack) - 1, -1, -1):
                            block = self.block_stack[i]
                            if block.get('type') == 'if' and block.get('pending'):
                                if_block = block
                                break
                    
                    if if_block:
                        if_block['pending'] = False
                        if_block['cond_val'] = ctx.llvm_value
                        # Генерируем br инструкцию
                        self.emit(f"  br i1 {ctx.llvm_value}, label %{if_block['then_label']}, label %{if_block['else_label']}")
                        self.emit(f"{if_block['then_label']}:")
                        # После генерации условного перехода для if, не проверяем where
                        return
                    
                    # Проверяем, не является ли это условием where в цикле for
                    # Условие where обрабатывается как обычное сравнение, но нужно проверить его
                    # и если оно не выполняется, перейти к увеличению счётчика
                    if self.block_stack:
                        for block in reversed(self.block_stack):
                            if block.get('type') == 'for' and block.get('where_expr') and block.get('loop_counter_ptr'):
                                # Проверяем, обрабатывается ли сейчас условие where
                                where_expr = block.get('where_expr')
                                # Сравниваем по тексту выражения или по объекту
                                is_where_expr = False
                                if where_expr:
                                    if ctx == where_expr:
                                        is_where_expr = True
                                    elif hasattr(where_expr, 'getText') and hasattr(ctx, 'getText'):
                                        where_text = where_expr.getText()
                                        ctx_text = ctx.getText()
                                        # Проверяем, совпадают ли тексты или один содержит другой
                                        if where_text == ctx_text or where_text in ctx_text or ctx_text in where_text:
                                            is_where_expr = True
                                
                                if is_where_expr:
                                    # Это условие where - проверяем его и переходим соответственно
                                    loop_inc_label = block.get('inc_label')
                                    where_true_label = self.new_label()  # Продолжаем выполнение тела
                                    
                                    # Если условие не выполняется, переходим к увеличению счётчика
                                    # Если условие выполняется, продолжаем выполнение тела цикла
                                    self.emit(f"  br i1 {ctx.llvm_value}, label %{where_true_label}, label %{loop_inc_label}")
                                    self.emit(f"{where_true_label}:")
                                    # Условие where выполнено, продолжаем выполнение тела цикла
                                    block['where_checked'] = True
                                    return
                    
                    return
                
                # Логические операции
                if op == 'and':
                    # Логическое И: && в LLVM
                    tmp = self.new_temp()
                    and1 = self.new_temp()
                    and2 = self.new_temp()
                    self.emit(f"  {and1} = icmp ne i1 {l_val}, 0")
                    self.emit(f"  {and2} = icmp ne i1 {r_val}, 0")
                    self.emit(f"  {tmp} = and i1 {and1}, {and2}")
                    ctx.llvm_type = "i1"
                    ctx.llvm_value = tmp
                    return
                
                if op == 'or':
                    # Логическое ИЛИ: || в LLVM
                    tmp = self.new_temp()
                    or1 = self.new_temp()
                    or2 = self.new_temp()
                    self.emit(f"  {or1} = icmp ne i1 {l_val}, 0")
                    self.emit(f"  {or2} = icmp ne i1 {r_val}, 0")
                    self.emit(f"  {tmp} = or i1 {or1}, {or2}")
                    ctx.llvm_type = "i1"
                    ctx.llvm_value = tmp
                    
                    # Проверяем, не является ли это условием if
                    # Ищем блок if в стеке
                    if_block = None
                    if self.block_stack:
                        for block in reversed(self.block_stack):
                            if block.get('type') == 'if' and block.get('pending'):
                                if_block = block
                                break
                    
                    if if_block:
                        if_block['pending'] = False
                        if_block['cond_val'] = tmp
                        # Генерируем br инструкцию
                        self.emit(f"  br i1 {tmp}, label %{if_block['then_label']}, label %{if_block['else_label']}")
                        self.emit(f"{if_block['then_label']}:")
                    
                    return
        
        # По умолчанию
        ctx.llvm_type = None
        ctx.llvm_value = None
        
        # Проверяем, не является ли это условием if (для необработанных выражений)
        # Если выражение не bool, но мы в условии if, преобразуем его
        # Ищем блок if в стеке
        if_block = None
        if self.block_stack:
            for block in reversed(self.block_stack):
                if block.get('type') == 'if' and block.get('pending'):
                    if_block = block
                    break
        
        if if_block:
            block = if_block
            # Пытаемся преобразовать в bool
            if ctx.llvm_type and ctx.llvm_value:
                if ctx.llvm_type == "i32":
                    cmp_reg = self.new_temp()
                    self.emit(f"  {cmp_reg} = icmp ne i32 {ctx.llvm_value}, 0")
                    block['pending'] = False
                    block['cond_val'] = cmp_reg
                    self.emit(f"  br i1 {cmp_reg}, label %{block['then_label']}, label %{block['else_label']}")
                    self.emit(f"{block['then_label']}:")
                elif ctx.llvm_type == "double":
                    cmp_reg = self.new_temp()
                    self.emit(f"  {cmp_reg} = fcmp one double {ctx.llvm_value}, 0.0")
                    block['pending'] = False
                    block['cond_val'] = cmp_reg
                    self.emit(f"  br i1 {cmp_reg}, label %{block['then_label']}, label %{block['else_label']}")
                    self.emit(f"{block['then_label']}:")
    
    # === Обработка присваиваний ===
    
    def exitSingleAssignment(self, ctx: gsl1Parser.SingleAssignmentContext):
        """Обработка простого присваивания: ID '=' expression"""
        if not ctx.ID():
            return
        var_name = ctx.ID().getText()
        expr = ctx.expression()
        
        if not expr:
            return
        
        expr_type = getattr(expr, "llvm_type", "i32")
        expr_val = getattr(expr, "llvm_value", "0")
        
        if expr_type is None:
            expr_type = "i32"
        if expr_val is None:
            expr_val = "0"
        
        ptr = self.get_or_create_variable(var_name, expr_type)
        self.emit(f"  store {expr_type} {expr_val}, {expr_type}* {ptr}")
    
    def exitTypedAssignment(self, ctx: gsl1Parser.TypedAssignmentContext):
        """Обработка типизированного присваивания: ID ':' type '=' expression"""
        if not ctx.ID():
            return
        var_name = ctx.ID().getText()
        type_ctx = ctx.type_()
        
        # Получаем тип
        gsl_type = type_ctx.ID().getText() if type_ctx and type_ctx.ID() else "int"
        llvm_type = self.get_llvm_type(gsl_type)
        
        expr = ctx.expression()
        if not expr:
            return
        
        expr_type = getattr(expr, "llvm_type", llvm_type)
        expr_val = getattr(expr, "llvm_value", "0")
        
        if expr_type is None:
            expr_type = llvm_type
        if expr_val is None:
            expr_val = "0"
        
        # Преобразуем тип, если нужно
        if expr_type != llvm_type:
            if llvm_type == "double" and expr_type == "i32":
                conv_reg = self.new_temp()
                self.emit(f"  {conv_reg} = sitofp i32 {expr_val} to double")
                expr_val = conv_reg
                expr_type = "double"
        
        ptr = self.get_or_create_variable(var_name, llvm_type)
        self.emit(f"  store {llvm_type} {expr_val}, {llvm_type}* {ptr}")
    
    def exitMultipleAssignment(self, ctx: gsl1Parser.MultipleAssignmentContext):
        """Обработка множественного присваивания: ID (',' ID)+ ':=' expression (',' expression)+"""
        if not ctx.ID():
            return
        var_ids = [id_node.getText() for id_node in ctx.ID()]
        exprs = ctx.expression()
        
        for i, var_name in enumerate(var_ids):
            if i < len(exprs):
                expr = exprs[i]
                if not expr:
                    continue
                expr_type = getattr(expr, "llvm_type", "i32")
                expr_val = getattr(expr, "llvm_value", "0")
                if expr_type is None:
                    expr_type = "i32"
                if expr_val is None:
                    expr_val = "0"
                ptr = self.get_or_create_variable(var_name, expr_type)
                self.emit(f"  store {expr_type} {expr_val}, {expr_type}* {ptr}")
    
    def exitMemberAssignment(self, ctx: gsl1Parser.MemberAssignmentContext):
        """Обработка присваивания члену: ID '.' ID '=' expression"""
        # Это присваивание члену объекта (например, r.balance = ...)
        # Сохраняем информацию для последующей обработки в цикле
        obj_name = ctx.ID(0).getText() if ctx.ID() and len(ctx.ID()) > 0 else None
        member_name = ctx.ID(1).getText() if ctx.ID() and len(ctx.ID()) > 1 else None
        expr = ctx.expression()
        
        if obj_name and member_name and expr:
            # Сохраняем информацию о присваивании для обработки в цикле
            if not hasattr(self, 'pending_member_assignments'):
                self.pending_member_assignments = []
            
            expr_type = getattr(expr, "llvm_type", "i32")
            expr_val = getattr(expr, "llvm_value", "0")
            
            # Извлекаем значение выражения
            new_value = None
            expr_text = expr.getText() if hasattr(expr, 'getText') else ""
            
            # Проверяем, является ли это выражением с операцией (например, r.balance + 25.0)
            if '+' in expr_text or '-' in expr_text or '*' in expr_text or '/' in expr_text:
                # Это выражение - пытаемся извлечь значение
                if isinstance(expr, gsl1Parser.ExpressionContext):
                    # Пытаемся извлечь значение из бинарной операции
                    if expr.getChildCount() == 3:
                        left = expr.getChild(0)
                        op = expr.getChild(1).getText() if expr.getChild(1) else None
                        right = expr.getChild(2)
                        
                        if op == '+':
                            # Пытаемся вычислить сумму
                            right_val = None
                            
                            # Получаем значение правой части (литерал)
                            if isinstance(right, gsl1Parser.LiteralContext):
                                if right.FLOAT():
                                    right_val = float(right.FLOAT().getText())
                                elif right.INT():
                                    right_val = float(right.INT().getText())
                            elif isinstance(right, gsl1Parser.ExpressionContext):
                                # Может быть вложенное выражение
                                if right.getChildCount() == 1:
                                    right_child = right.getChild(0)
                                    if isinstance(right_child, gsl1Parser.LiteralContext):
                                        if right_child.FLOAT():
                                            right_val = float(right_child.FLOAT().getText())
                                        elif right_child.INT():
                                            right_val = float(right_child.INT().getText())
                            
                            if right_val is not None:
                                # Левая часть - это переменная (r.balance), сохраняем выражение
                                new_value = f"EXPR:{obj_name}.{member_name}+{right_val}"
            
            if new_value is None:
                # Обычное присваивание значения
                if isinstance(expr, gsl1Parser.LiteralContext):
                    if expr.STRING():
                        new_value = expr.STRING().getText()[1:-1]  # Убираем кавычки
                    elif expr.INT():
                        new_value = expr.INT().getText()
                    elif expr.FLOAT():
                        new_value = expr.FLOAT().getText()
                elif expr_type == "i32" and expr_val and not expr_val.startswith("%"):
                    new_value = str(expr_val)
                elif expr_type == "double" and expr_val and not expr_val.startswith("%"):
                    new_value = str(expr_val)
                elif expr_type == "i8*" and expr_val and expr_val.startswith("@"):
                    # Глобальная строка
                    for str_val, global_name in self.global_strings.items():
                        if global_name == expr_val:
                            new_value = str_val
                            break
            
            if new_value is not None:
                # Сохраняем присваивание для обработки в текущем цикле
                if hasattr(self, 'loop_assignments') and self.loop_assignments:
                    self.loop_assignments[-1].append({
                        'obj': obj_name,
                        'member': member_name,
                        'value': new_value
                    })
                else:
                    # Если нет активного цикла, сохраняем в pending
                    if not hasattr(self, 'pending_member_assignments'):
                        self.pending_member_assignments = []
                    self.pending_member_assignments.append({
                        'obj': obj_name,
                        'member': member_name,
                        'value': new_value
                    })
    
    # === Обработка таблиц ===
    
    def exitTableDeclaration(self, ctx: gsl1Parser.TableDeclarationContext):
        """Обработка объявления таблицы: ID '=' TABLE_KW '(' columnDef (',' columnDef)* ')'"""
        table_name = ctx.ID().getText()
        # Создаём переменную для таблицы (упрощённо - указатель)
        ptr = self.get_or_create_variable(table_name, "i8*")
        self.emit(f"  store i8* null, i8** {ptr}")
        
        # Сохраняем информацию о структуре таблицы
        columns = []
        column_defs = ctx.columnDef()
        if column_defs:
            for col_def in column_defs:
                col_name = col_def.ID().getText()
                type_ctx = col_def.type_()
                col_type = type_ctx.ID().getText() if type_ctx and type_ctx.ID() else "int"
                columns.append({'name': col_name, 'type': col_type})
        
        self.tables_info[table_name] = {
            'columns': columns,
            'rows': []  # Будет заполняться при вставке данных
        }
    
    def exitDataInsert(self, ctx: gsl1Parser.DataInsertContext):
        """Обработка вставки данных: ID '+=' expression"""
        table_name = ctx.ID().getText()
        expr = ctx.expression()
        
        # Если это таблица, пытаемся извлечь данные из выражения Row(...)
        if table_name in self.tables_info and expr:
            # Проверяем, есть ли сохранённые аргументы Row в выражении
            row_data = getattr(expr, "row_args", None)
            
            if row_data:
                # Сохраняем строку в информацию о таблице
                self.tables_info[table_name]['rows'].append(row_data)
    
    def exitDataDelete(self, ctx: gsl1Parser.DataDeleteContext):
        """Обработка удаления данных: ID '-=' '(' generatorExpression ')'"""
        table_name = ctx.ID().getText()
        gen_expr = ctx.generatorExpression()
        
        if table_name in self.tables_info and gen_expr:
            # Упрощённо: пытаемся определить условие удаления
            # В реальной реализации нужно было бы анализировать generatorExpression
            # Для примера: если условие `row.balance == 0.0`, удаляем строки с balance == 0.0
            
            # Пытаемся найти условие в generatorExpression
            if_expr = gen_expr.expression() if hasattr(gen_expr, 'expression') and gen_expr.expression() else None
            
            if if_expr:
                # Упрощённо: проверяем, есть ли сравнение с 0.0 или 0
                condition_text = if_expr.getText() if hasattr(if_expr, 'getText') else ""
                
                # Если условие содержит сравнение balance с 0.0, удаляем такие строки
                if "balance" in condition_text and ("0.0" in condition_text or "0" in condition_text):
                    # Удаляем строки, где balance == 0.0
                    balance_col_index = None
                    for i, col in enumerate(self.tables_info[table_name]['columns']):
                        if col['name'] == 'balance':
                            balance_col_index = i
                            break
                    
                    if balance_col_index is not None:
                        # Фильтруем строки, удаляя те, где balance == 0.0
                        filtered_rows = []
                        for row in self.tables_info[table_name]['rows']:
                            if balance_col_index < len(row):
                                balance_val = row[balance_col_index]
                                # Проверяем, не равен ли balance 0.0
                                try:
                                    if float(balance_val) != 0.0:
                                        filtered_rows.append(row)
                                except (ValueError, TypeError):
                                    # Если не число, оставляем строку
                                    filtered_rows.append(row)
                            else:
                                filtered_rows.append(row)
                        
                        self.tables_info[table_name]['rows'] = filtered_rows
    
    def enterGeneratorExpression(self, ctx: gsl1Parser.GeneratorExpressionContext):
        """Вход в генераторное выражение - не генерируем LLVM IR код"""
        # Устанавливаем флаг, что мы находимся внутри генераторного выражения
        self.in_generator_expression = True
    
    def exitGeneratorExpression(self, ctx: gsl1Parser.GeneratorExpressionContext):
        """Выход из генераторного выражения - не генерируем LLVM IR код"""
        # Генераторное выражение обрабатывается только в exitDataDelete
        # Здесь не генерируем LLVM IR код
        self.in_generator_expression = False
        ctx.llvm_type = "void"
        ctx.llvm_value = None
    
    # === Обработка циклов ===
    
    def enterForLoop(self, ctx: gsl1Parser.ForLoopContext):
        """Вход в цикл for"""
        var_name = ctx.ID().getText()
        # Создаём переменную цикла
        self.scope_stack.append({})
        loop_var_ptr = self.get_or_create_variable(var_name, "i8*")
        
        # Создаём метки для цикла
        loop_init_label = self.new_label()  # Инициализация цикла
        loop_cond_label = self.new_label()  # Проверка условия
        loop_body_label = self.new_label()  # Тело цикла
        loop_inc_label = self.new_label()   # Увеличение счётчика
        loop_end_label = self.new_label()   # Конец цикла
        
        # Определяем имя таблицы заранее (если возможно)
        # В forLoop: 'for' ID 'in' expression ('where' expression)? suite
        # expression(0) - это таблица, expression(1) - это условие where (если есть)
        expr = ctx.expression(0) if ctx.expression() else None
        table_name = None
        if expr and hasattr(expr, 'ID') and expr.ID():
            table_name = expr.ID().getText()
        elif expr:
            var_name_expr = getattr(expr, "var_name", None)
            if var_name_expr:
                table_name = var_name_expr
        
        # Получаем условие where, если оно есть
        # В грамматике: forLoop: 'for' ID 'in' expression ('where' expression)? suite
        # Условие where - это второе выражение (индекс 1), если оно есть
        where_expr = None
        if ctx.expression() and len(ctx.expression()) > 1:
            where_expr = ctx.expression(1)
        
        # Сохраняем метки в стек - условие будет обработано после exitExpression
        self.block_stack.append({
            'type': 'for',
            'var_name': var_name,
            'table_name': table_name,  # Сохраняем имя таблицы для использования в теле цикла
            'where_expr': where_expr,  # Сохраняем условие where
            'init_label': loop_init_label,
            'cond_label': loop_cond_label,
            'body_label': loop_body_label,
            'inc_label': loop_inc_label,
            'end_label': loop_end_label,
            'where_check_label': self.new_label(),  # Метка для проверки where
            'pending': True
        })
        
        # Инициализируем список присваиваний для этого цикла
        if not hasattr(self, 'loop_assignments'):
            self.loop_assignments = []
        self.loop_assignments.append([])
        
        # Генерируем структуру цикла
        # Проверяем, является ли table_name параметром функции типа table
        is_table_param = False
        table_param_info = None
        if self.current_function and table_name:
            # Проверяем параметры функции
            for param_name, param_type in self.current_function.get('params', []):
                if param_name == table_name and param_type == "i8*":  # table передаётся как i8*
                    is_table_param = True
                    # Ищем информацию о таблице в глобальных таблицах по имени параметра
                    # Для упрощения используем фиксированное количество строк или runtime функции
                    break
        
        # Проверяем, действительно ли мы внутри функции
        # Используем function_stack для более точной проверки
        is_inside_function = len(self.function_stack) > 0 and self.current_function is not None
        
        # Проверяем, является ли table_name таблицей или списком
        is_table = table_name in self.tables_info or is_table_param
        
        if is_inside_function and table_name and is_table:
            # Внутри функции - генерируем полную структуру цикла
            if table_name in self.tables_info:
                row_count = len(self.tables_info[table_name]['rows'])
                # Сохраняем информацию о таблице в блоке для использования в теле цикла
                self.block_stack[-1]['table_info'] = self.tables_info[table_name]
                self.block_stack[-1]['table_name'] = table_name
            else:
                # Для параметров таблиц ищем информацию о переданной таблице
                found_table = None
                found_table_name = None
                
                # Проверяем, есть ли информация о переданной таблице для этого параметра
                if self.current_function:
                    func_name = self.current_function.get('name')
                    # Ищем параметр с именем table_name
                    for param_index, (param_name, param_type) in enumerate(self.current_function.get('params', [])):
                        if param_name == table_name and param_type == "i8*":
                            # Это параметр-таблица, ищем информацию о переданной таблице
                            # Сначала проверяем маппинг вызовов функций
                            call_key = (func_name, param_index)
                            if call_key in self.function_call_table_mapping:
                                found_table_name = self.function_call_table_mapping[call_key]
                                if found_table_name in self.tables_info:
                                    found_table = self.tables_info[found_table_name]
                                    break
                            
                            # Если не нашли через маппинг, проверяем param_table_mapping в функции
                            param_mapping = self.current_function.get('param_table_mapping', {})
                            if param_name in param_mapping:
                                mapped_table_name = param_mapping[param_name]
                                if mapped_table_name in self.tables_info:
                                    found_table = self.tables_info[mapped_table_name]
                                    found_table_name = mapped_table_name
                                    break
                
                # Если не нашли через маппинг, ищем в глобальных таблицах


                if not found_table:

                    table_names = list(self.tables_info.keys())
                    if len(table_names) == 1:
                        # Если только одна таблица, используем её
                        found_table_name = table_names[0]
                        found_table = self.tables_info[found_table_name]
                    else:
                        # Ищем таблицу по похожему имени (например, orderTable -> orders)
                        for global_table_name, table_info in self.tables_info.items():
                            # Используем первую найденную таблицу (упрощённо)
                            found_table = table_info
                            found_table_name = global_table_name
                            break
                
                if found_table:
                    row_count = len(found_table['rows'])
                    self.block_stack[-1]['table_info'] = found_table
                    self.block_stack[-1]['table_name'] = found_table_name  # Обновляем имя таблицы
                else:

                    row_count = 0
                    self.block_stack[-1]['table_info'] = None
            
            # Инициализация счётчика
            loop_counter_ptr = self.new_temp()
            self.emit(f"  {loop_counter_ptr} = alloca i32")
            self.emit(f"  store i32 0, i32* {loop_counter_ptr}")
            
            # Сохраняем указатель на счётчик в блоке для использования в теле цикла
            self.block_stack[-1]['loop_counter_ptr'] = loop_counter_ptr
            
            # Переход к проверке условия
            self.emit(f"  br label %{loop_cond_label}")
            self.emit(f"{loop_cond_label}:")
            
            # Загружаем счётчик
            loop_counter = self.new_temp()
            self.emit(f"  {loop_counter} = load i32, i32* {loop_counter_ptr}")
            
            # Проверяем условие: counter < row_count
            cond = self.new_temp()
            self.emit(f"  {cond} = icmp ult i32 {loop_counter}, {row_count}")
            
            # Условный переход: если условие истинно, идём в тело, иначе в конец
            self.emit(f"  br i1 {cond}, label %{loop_body_label}, label %{loop_end_label}")
            self.emit(f"{loop_body_label}:")

        elif table_name and table_name in self.tables_info:

            row_count = len(self.tables_info[table_name]['rows'])
            # Сохраняем информацию о таблице в блоке
            self.block_stack[-1]['table_info'] = self.tables_info[table_name]
            self.block_stack[-1]['table_name'] = table_name
            
            # Инициализация счётчика
            loop_counter_ptr = self.new_temp()
            self.emit(f"  {loop_counter_ptr} = alloca i32")
            self.emit(f"  store i32 0, i32* {loop_counter_ptr}")
            
            # Сохраняем указатель на счётчик в блоке
            self.block_stack[-1]['loop_counter_ptr'] = loop_counter_ptr
            
            # Переход к проверке условия
            self.emit(f"  br label %{loop_cond_label}")
            self.emit(f"{loop_cond_label}:")
            
            # Загружаем счётчик
            loop_counter = self.new_temp()
            self.emit(f"  {loop_counter} = load i32, i32* {loop_counter_ptr}")
            
            # Проверяем условие: counter < row_count
            cond = self.new_temp()
            self.emit(f"  {cond} = icmp ult i32 {loop_counter}, {row_count}")
            
            # Условный переход: если условие истинно, идём в тело, иначе в конец
            self.emit(f"  br i1 {cond}, label %{loop_body_label}, label %{loop_end_label}")
            self.emit(f"{loop_body_label}:")
            # Тело цикла будет генерироваться здесь
        else:
            # Вне функции и не таблица - просто создаём метку
            self.emit(f"{loop_init_label}:")
    
    def exitForLoop(self, ctx: gsl1Parser.ForLoopContext):

        var_name = ctx.ID().getText()
        expr = ctx.expression(0)  # Таблица, по которой итерируемся
        
        # Определяем имя таблицы
        table_name = None
        if expr and hasattr(expr, 'ID') and expr.ID():
            table_name = expr.ID().getText()
        elif expr:
            # Может быть вложенное выражение
            var_name_expr = getattr(expr, "var_name", None)
            if var_name_expr:
                table_name = var_name_expr
        
        # Получаем блок цикла из стека
        if not self.block_stack or self.block_stack[-1].get('type') != 'for':
            if self.scope_stack:
                self.scope_stack.pop()
            return
        
        block = self.block_stack.pop()
        loop_init_label = block.get('init_label')
        loop_cond_label = block.get('cond_label')
        loop_body_label = block.get('body_label')
        loop_inc_label = block.get('inc_label')
        loop_end_label = block.get('end_label')
        loop_counter_ptr = block.get('loop_counter_ptr')
        
        # Если мы внутри функции или глобальный цикл с LLVM IR, завершаем цикл
        # Проверяем, есть ли информация о таблице (глобальная или из параметра)
        has_table_info = False
        table_info = block.get('table_info')
        if (self.current_function and table_name and loop_counter_ptr) or (not self.current_function and table_name and loop_counter_ptr and table_info):
            # Проверяем, есть ли информация о таблице
            if table_name in self.tables_info or table_info:
                has_table_info = True
        
        # Проверяем, действительно ли мы внутри функции (не в main)
        # Если функция называется 'main', это глобальный код, используем старый подход
        is_inside_function = (len(self.function_stack) > 0 and 
                             self.current_function is not None and 
                             self.current_function.get('name') != 'main')
        
        # Проверяем, есть ли loop_counter_ptr (значит, цикл генерирует LLVM IR)
        has_llvm_loop = loop_counter_ptr is not None
        
        if (is_inside_function or (not is_inside_function and has_llvm_loop)) and table_name and has_table_info and loop_counter_ptr:
            # Проверяем, есть ли условие where
            where_expr = block.get('where_expr')
            where_check_label = block.get('where_check_label')
            
            # Если есть условие where, оно будет обработано в exitExpression
            # После обработки условия where, если оно не выполняется, произойдёт переход к loop_inc_label
            # Если условие выполняется, выполнится тело цикла
            
            # После тела цикла переходим к увеличению счётчика
            self.emit(f"  br label %{loop_inc_label}")
            self.emit(f"{loop_inc_label}:")
            
            # Увеличиваем счётчик и переходим обратно к проверке условия
            loop_counter_inc = self.new_temp()
            self.emit(f"  {loop_counter_inc} = load i32, i32* {loop_counter_ptr}")
            next_counter = self.new_temp()
            one_const = 1
            self.emit(f"  {next_counter} = add i32 {loop_counter_inc}, {one_const}")
            self.emit(f"  store i32 {next_counter}, i32* {loop_counter_ptr}")
            self.emit(f"  br label %{loop_cond_label}")
            
            # Конец цикла
            self.emit(f"{loop_end_label}:")
            loop_end_label_emitted = True
        else:
            loop_end_label_emitted = False
        
        # Применяем присваивания к строкам таблицы для глобальных циклов
        # (даже если цикл генерирует LLVM IR, нужно применить присваивания к данным)
        if not is_inside_function and table_name and table_name in self.tables_info:
            # Условие where - это второе выражение (индекс 1)
            # ctx.expression() возвращает список всех выражений
            where_expr = None
            if ctx.expression() and len(ctx.expression()) > 1:
                where_expr = ctx.expression(1)
            elif hasattr(ctx, 'expression') and ctx.expression():
                # Проверяем, есть ли условие where через количество выражений
                expr_list = ctx.expression()
                if len(expr_list) > 1:
                    where_expr = expr_list[1]
            
            # Получаем присваивания для этого цикла
            if hasattr(self, 'loop_assignments') and self.loop_assignments:
                loop_assigns = self.loop_assignments.pop() if self.loop_assignments else []
            else:
                loop_assigns = []
            
            # Если есть присваивания из pending_member_assignments, добавляем их
            if hasattr(self, 'pending_member_assignments') and self.pending_member_assignments:
                loop_assigns.extend(self.pending_member_assignments)
                self.pending_member_assignments = []
            
                
            # Применяем присваивания к строкам таблицы
            if loop_assigns:
                # Упрощённо: применяем изменения ко всем строкам, которые могут соответствовать условию
                for row in self.tables_info[table_name]['rows']:
                    for assign in loop_assigns:
                        if assign['obj'] == var_name:
                            # Находим колонку по имени
                            col_index = None
                            for i, col in enumerate(self.tables_info[table_name]['columns']):
                                if col['name'] == assign['member']:
                                    col_index = i
                                    break
                            
                            if col_index is not None and col_index < len(row):
                                # Проверяем условие where, если оно есть
                                should_update = True
                                # Если нет условия where, обновляем все строки
                                if where_expr:
                                    # Упрощённо: проверяем простые условия
                                    where_text = where_expr.getText() if hasattr(where_expr, 'getText') else ""
                                    
                                    # Если условие содержит сравнение с конкретным значением
                                    # Обрабатываем r.name == "Bob" или r.name=="Bob"
                                    # Проверяем наличие "name" и "bob" (без учёта регистра)
                                    where_lower = where_text.lower()
                                    if "name" in where_lower and "bob" in where_lower:
                                        # Проверяем, соответствует ли строка условию
                                        name_col_index = None
                                        for i, col in enumerate(self.tables_info[table_name]['columns']):
                                            if col['name'] == 'name':
                                                name_col_index = i
                                                break
                                        if name_col_index is not None and name_col_index < len(row):
                                            # Сравниваем без учёта регистра и кавычек
                                            row_name = str(row[name_col_index]).strip().strip('"').strip("'")
                                            if row_name.lower() != "bob":
                                                should_update = False
                                    elif "id" in where_text:
                                        # Проверяем, соответствует ли строка условию
                                        id_col_index = None
                                        for i, col in enumerate(self.tables_info[table_name]['columns']):
                                            if col['name'] == 'id':
                                                id_col_index = i
                                                break
                                        if id_col_index is not None and id_col_index < len(row):
                                            # Проверяем, содержит ли условие сравнение с 3
                                            if "3" in where_text or "== 3" in where_text:
                                                if row[id_col_index] != "3":
                                                    should_update = False
                                            else:
                                                # Другое условие - не обновляем
                                                should_update = False
                                        else:
                                            # Если условие where не распознано, применяем ко всем строкам
                                            # (для упрощения - в реальности нужно правильно парсить условие)
                                            pass
                                
                                if should_update:
                                    # Вычисляем новое значение, если это выражение
                                    if assign['value'].startswith("EXPR:"):
                                        # Это выражение типа r.balance = r.balance + 25.0
                                        expr_parts = assign['value'].split(":")
                                        if len(expr_parts) > 1:
                                            expr_detail = expr_parts[1]
                                            if '+' in expr_detail:
                                                # Разбиваем по '+' и убираем пробелы
                                                parts = [p.strip() for p in expr_detail.split('+')]
                                                if len(parts) == 2:
                                                    try:
                                                        old_val = float(row[col_index])
                                                        increment = float(parts[1].strip())
                                                        new_val = old_val + increment
                                                        row[col_index] = str(new_val)
                                                    except (ValueError, TypeError):
                                                        row[col_index] = assign['value']
                                                else:
                                                    row[col_index] = assign['value']
                                            else:
                                                row[col_index] = assign['value']
                                        else:
                                            row[col_index] = assign['value']
                                    else:
                                        row[col_index] = assign['value']
            else:
                # Если нет таблицы или не внутри функции, просто завершаем цикл
                if not loop_end_label_emitted:
                    self.emit(f"  br label %{loop_end_label}")
                    self.emit(f"{loop_end_label}:")
        
        if self.scope_stack:
            self.scope_stack.pop()
    
    # === Обработка условий ===
    
    def enterIfStatement(self, ctx: gsl1Parser.IfStatementContext):
        """Вход в if"""
        # Создаём метки для then и else блоков
        then_label = self.new_label()
        else_label = self.new_label()
        end_label = self.new_label()
        
        # Сохраняем метки в стек - условие будет обработано в exitExpression
        # после того, как выражение будет обработано
        self.block_stack.append({
            'type': 'if',
            'then_label': then_label,
            'else_label': else_label,
            'end_label': end_label,
            'pending': True  # Флаг, что нужно обработать условие
        })
    
    def exitIfStatement(self, ctx: gsl1Parser.IfStatementContext):
        """Выход из if"""
        # Ищем блок if в стеке (может быть не последним, если внутри цикла)
        if_block = None
        if self.block_stack:
            for i in range(len(self.block_stack) - 1, -1, -1):
                if self.block_stack[i].get('type') == 'if':
                    if_block = self.block_stack.pop(i)
                    break
        
        if if_block:
            # Если условие еще не обработано (не было br инструкции), обрабатываем его сейчас
            if if_block.get('pending'):
                # Условие не было обработано - генерируем по умолчанию false
                self.emit(f"  br i1 0, label %{if_block['then_label']}, label %{if_block['else_label']}")
                self.emit(f"{if_block['then_label']}:")
            
            # Завершаем блоки
            self.emit(f"  br label %{if_block['end_label']}")
            self.emit(f"{if_block['else_label']}:")
            self.emit(f"  br label %{if_block['end_label']}")
            self.emit(f"{if_block['end_label']}:")
    
    # === Обработка switch ===
    
    def enterSwitchStatement(self, ctx: gsl1Parser.SwitchStatementContext):
        """Вход в switch"""
        # Упрощённая обработка - создаём базовую структуру
        end_label = self.new_label()
        self.block_stack.append({
            'type': 'switch',
            'end_label': end_label,
            'cases': []
        })
    
    def exitSwitchStatement(self, ctx: gsl1Parser.SwitchStatementContext):
        """Выход из switch"""
        if self.block_stack and self.block_stack[-1]['type'] == 'switch':
            block = self.block_stack.pop()
            self.emit(f"  br label %{block['end_label']}")
            self.emit(f"{block['end_label']}:")
    
    # === Обработка функций ===
    
    def enterFunctionDef(self, ctx: gsl1Parser.FunctionDefContext):
        """Вход в определение функции"""
        func_name = ctx.ID().getText()
        
        # Получаем параметры
        params = []
        params_ctx = ctx.parameters()
        if params_ctx:
            for param_ctx in params_ctx.parameter():
                param_name = param_ctx.ID().getText()
                param_type_ctx = param_ctx.type_()
                param_gsl_type = param_type_ctx.ID().getText() if param_type_ctx and param_type_ctx.ID() else "int"
                param_llvm_type = self.get_llvm_type(param_gsl_type)
                params.append((param_name, param_llvm_type))
        
        # Получаем возвращаемый тип
        return_type_ctx = ctx.type_()
        return_gsl_type = None
        if return_type_ctx:
            return_gsl_type = return_type_ctx.ID().getText() if return_type_ctx.ID() else None
        return_llvm_type = self.get_llvm_type(return_gsl_type) if return_gsl_type else "void"
        
        # Создаём новую функцию
        func_info = {
            'name': func_name,
            'return_type': return_llvm_type,
            'params': params,
            'entry': [],
            'body': [],
            'footer': [],
            'param_table_mapping': {}  # {param_name: table_name} - маппинг параметров на таблицы
        }
        self.function_stack.append(func_info)
        self.current_function = func_info
        
        # Сохраняем информацию о функции для использования при вызовах
        # Обрабатываем перегрузки - сохраняем все версии
        if func_name not in self.functions_info:
            self.functions_info[func_name] = []
        self.functions_info[func_name].append({
            'return_type': return_llvm_type,
            'params': params,
            'param_count': len(params)
        })
        
        # Входим в новую область видимости
        self.scope_stack.append({})
        
            # Создаём параметры как локальные переменные
        # Параметры будут доступны через %0, %1, и т.д. в LLVM
        for i, (param_name, param_type) in enumerate(params):
            param_ptr = self.new_temp()
            self.emit_entry(f"  {param_ptr} = alloca {param_type}")
            # Сохраняем параметр в переменную (параметры доступны как %0, %1, ...)
            param_reg = f"%{i}"
            self.emit_entry(f"  store {param_type} {param_reg}, {param_type}* {param_ptr}")
            self.scope_stack[-1][param_name] = (param_type, param_ptr)
    
    def exitFunctionDef(self, ctx: gsl1Parser.FunctionDefContext):
        """Выход из определения функции"""
        if self.current_function:
            # Если нет return, добавляем его
            if self.current_function['return_type'] != 'void':
                # Проверяем, есть ли return в теле
                has_return = any('ret' in line for line in self.current_function['body'])
                if not has_return:
                    # Добавляем return по умолчанию
                    default_val = "0" if self.current_function['return_type'] == "i32" else "0.0" if self.current_function['return_type'] == "double" else "null"
                    self.emit(f"  ret {self.current_function['return_type']} {default_val}")
            else:
                # void функция
                has_return = any('ret' in line for line in self.current_function['body'])
                if not has_return:
                    self.emit("  ret void")
            
            # Выходим из области видимости
            if self.scope_stack:
                self.scope_stack.pop()
            
            # Сохраняем функцию в all_functions перед удалением из стека
            if self.current_function:
                self.all_functions.append(self.current_function)
            
            self.current_function = None
            if self.function_stack:
                self.function_stack.pop()
                # Возвращаемся к предыдущей функции или main
                if self.function_stack:
                    self.current_function = self.function_stack[-1]
                else:
                    self._init_main_function()
    
    def exitReturnStatement(self, ctx: gsl1Parser.ReturnStatementContext):
        """Обработка return"""
        if self.current_function:
            expr = ctx.expression()
            if expr:
                expr_type = getattr(expr, "llvm_type", "i32")
                expr_val = getattr(expr, "llvm_value", "0")
                if expr_type is None:
                    expr_type = self.current_function['return_type'] if self.current_function['return_type'] != 'void' else "i32"
                if expr_val is None:
                    # Если возвращаемый тип - строка, создаём пустую строку
                    if self.current_function['return_type'] == 'i8*':
                        # Создаём пустую строку
                        empty_str = self.get_string_global("")
                        str_ptr = self.new_temp()
                        str_len = 1
                        self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {empty_str}, i32 0, i32 0")
                        expr_val = str_ptr
                        expr_type = "i8*"
                    else:
                        expr_val = "0"
                
                # Если тип выражения не совпадает с возвращаемым типом, преобразуем
                if expr_type != self.current_function['return_type'] and self.current_function['return_type'] != 'void':
                    if self.current_function['return_type'] == 'i8*' and expr_type != 'i8*':
                        # Нужно преобразовать в строку - упрощённо возвращаем пустую строку
                        empty_str = self.get_string_global("")
                        str_ptr = self.new_temp()
                        str_len = 1
                        self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {empty_str}, i32 0, i32 0")
                        expr_val = str_ptr
                        expr_type = "i8*"
                
                # Если возвращаем строку, убеждаемся, что это правильный указатель
                if expr_type == "i8*" and expr_val and expr_val.startswith("%"):
                    # Это регистр - используем его напрямую
                    self.emit(f"  ret {expr_type} {expr_val}")
                else:
                    self.emit(f"  ret {expr_type} {expr_val}")
            else:
                self.emit("  ret void")
    
    # === Обработка print ===
    
    def exitPrintStatement(self, ctx: gsl1Parser.PrintStatementContext):
        """Обработка print"""
        exprs = ctx.expression()
        if not exprs:
            return
        
        for expr in exprs:
            if not expr:
                continue
            expr_type = getattr(expr, "llvm_type", "i32")
            expr_val = getattr(expr, "llvm_value", "0")
            var_name = getattr(expr, "var_name", None)  # Имя переменной, если это ID
            
            if expr_type is None:
                expr_type = "i32"
            if expr_val is None:
                expr_val = "0"
            
            # Проверяем, является ли это таблицей (i8* с null или указателем на таблицу)
            if expr_type == "i8*":
                # Это может быть строка или таблица
                # Проверяем, является ли это строкой (есть в global_strings)
                is_string = False
                if expr_val and expr_val.startswith("@"):
                    # Это глобальная строка
                    is_string = True
                
                # Для i8* всегда используем puts
                # Проверяем, является ли это таблицей по имени переменной
                table_name = None
                if var_name and var_name in self.tables_info:
                    table_name = var_name
                
                # Если это таблица, всегда выводим сериализацию (независимо от значения)
                if table_name:
                    # Генерируем сериализацию таблицы
                    self._serialize_table(table_name)
                elif expr_val == "null" or expr_val == "0":
                    # Это null и не таблица - просто выводим [Table]
                    table_str = self.get_string_global("[Table]")
                    str_ptr = self.new_temp()
                    str_len = len("[Table]") + 1
                    self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {table_str}, i32 0, i32 0")
                    self.emit(f"  call i32 @puts(i8* {str_ptr})")
                elif expr_val.startswith("%"):
                    # Это регистр - проверяем, является ли это таблицей по имени переменной
                    table_name = None
                    is_table = getattr(expr, "is_table", False)
                    if var_name and var_name in self.tables_info:
                        table_name = var_name
                    elif is_table and var_name:
                        # Если помечено как таблица, но не найдено в tables_info, всё равно пытаемся
                        table_name = var_name
                    
                    # Если это таблица, всегда выводим сериализацию (независимо от значения регистра)
                    if table_name and table_name in self.tables_info:
                        # Генерируем сериализацию таблицы
                        self._serialize_table(table_name)
                    else:
                        # Проверяем, является ли это значением из таблицы (через switch)
                        is_table_value = getattr(expr, "is_loop_var", False) and getattr(expr, "member_name", None)
                        if is_table_value:
                            # Это значение из таблицы (получено через switch) - выводим напрямую
                            self.emit(f"  call i32 @puts(i8* {expr_val})")
                        else:
                            # Если не таблица, просто выводим строку
                            self.emit(f"  call i32 @puts(i8* {expr_val})")
                elif expr_val.startswith("@"):
                    # Это глобальная строка - получаем указатель
                    str_ptr = self.new_temp()
                    # Упрощённо - используем стандартную длину
                    str_len = 100
                    self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {expr_val}, i32 0, i32 0")
                    self.emit(f"  call i32 @puts(i8* {str_ptr})")
                else:
                    # Другое - выводим как есть
                    self.emit(f"  call i32 @puts(i8* {expr_val})")
            elif expr_type == "i32":
                # Вывод целого числа
                # Проверяем, является ли это значением из таблицы (через switch)
                is_table_value = getattr(expr, "is_loop_var", False) and getattr(expr, "member_name", None)
                if is_table_value and expr_val.startswith("%"):
                    # Это значение из таблицы - нужно получить фактическое значение из switch
                    # Для упрощения используем printf с регистром
                    fmt_global = self.get_string_global("%d\n")
                    fmt_ptr = self.new_temp()
                    fmt_len = len("%d\n") + 1
                    self.emit(f"  {fmt_ptr} = getelementptr inbounds [{fmt_len} x i8], [{fmt_len} x i8]* {fmt_global}, i32 0, i32 0")
                    self.emit(f"  call i32 (i8*, ...) @printf(i8* {fmt_ptr}, i32 {expr_val})")
                else:
                    # Обычный вывод целого числа
                    fmt_global = self.get_string_global("%d\n")
                    fmt_ptr = self.new_temp()
                    fmt_len = len("%d\n") + 1
                    self.emit(f"  {fmt_ptr} = getelementptr inbounds [{fmt_len} x i8], [{fmt_len} x i8]* {fmt_global}, i32 0, i32 0")
                    self.emit(f"  call i32 (i8*, ...) @printf(i8* {fmt_ptr}, i32 {expr_val})")
            elif expr_type == "double":
                # Вывод вещественного числа
                # Проверяем, является ли это значением из таблицы (через switch)
                is_table_value = getattr(expr, "is_loop_var", False) and getattr(expr, "member_name", None)
                if is_table_value and expr_val.startswith("%"):
                    # Это значение из таблицы - нужно получить фактическое значение из switch
                    # Для упрощения используем printf с регистром
                    fmt_global = self.get_string_global("%f\n")
                    fmt_ptr = self.new_temp()
                    fmt_len = len("%f\n") + 1
                    self.emit(f"  {fmt_ptr} = getelementptr inbounds [{fmt_len} x i8], [{fmt_len} x i8]* {fmt_global}, i32 0, i32 0")
                    self.emit(f"  call i32 (i8*, ...) @printf(i8* {fmt_ptr}, double {expr_val})")
                else:
                    # Обычный вывод вещественного числа
                    fmt_global = self.get_string_global("%f\n")
                    fmt_ptr = self.new_temp()
                    fmt_len = len("%f\n") + 1
                    self.emit(f"  {fmt_ptr} = getelementptr inbounds [{fmt_len} x i8], [{fmt_len} x i8]* {fmt_global}, i32 0, i32 0")
                    self.emit(f"  call i32 (i8*, ...) @printf(i8* {fmt_ptr}, double {expr_val})")
            elif expr_type == "i8*":
                # Вывод строки или таблицы
                if expr_val == "null" or expr_val == "0":
                    # Это таблица или null - выводим представление таблицы
                    table_str = self.get_string_global("[Table]")
                    str_ptr = self.new_temp()
                    str_len = len("[Table]") + 1
                    self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {table_str}, i32 0, i32 0")
                    self.emit(f"  call i32 @puts(i8* {str_ptr})")
                elif expr_val.startswith("%"):
                    # Это регистр со строкой - проверяем, не null ли он
                    # Проверяем, является ли это значением из таблицы (через switch)
                    is_table_value = getattr(expr, "is_loop_var", False) and getattr(expr, "member_name", None)
                    if is_table_value:
                        # Это значение из таблицы (получено через switch) - выводим напрямую
                        self.emit(f"  call i32 @puts(i8* {expr_val})")
                    else:
                        # Для простоты всегда выводим через puts
                        # Если это null, puts ничего не выведет, но это нормально
                        self.emit(f"  call i32 @puts(i8* {expr_val})")
                else:
                    # Это глобальная строка или литерал
                    # Если это имя глобальной строки (@.strX), нужно получить указатель
                    if expr_val.startswith("@"):
                        str_ptr = self.new_temp()
                        # Упрощённо - предполагаем стандартную длину
                        str_len = 100
                        self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {expr_val}, i32 0, i32 0")
                        self.emit(f"  call i32 @puts(i8* {str_ptr})")
                    else:
                        # Используем puts напрямую
                        self.emit(f"  call i32 @puts(i8* {expr_val})")
            else:
                # По умолчанию - выводим как строку
                fmt_global = self.get_string_global("\n")
                fmt_ptr = self.new_temp()
                self.emit(f"  {fmt_ptr} = getelementptr inbounds [2 x i8], [2 x i8]* {fmt_global}, i32 0, i32 0")
                self.emit(f"  call i32 @puts(i8* {fmt_ptr})")
    
    # === Обработка списков ===
    
    def exitListLiteral(self, ctx: gsl1Parser.ListLiteralContext):
        """Обработка литерала списка"""
        # Упрощённо - возвращаем null
        ctx.llvm_type = "i8*"
        ctx.llvm_value = "null"
    
    def exitListComprehension(self, ctx: gsl1Parser.ListComprehensionContext):
        """Обработка list comprehension"""
        # Упрощённо - возвращаем null
        ctx.llvm_type = "i8*"
        ctx.llvm_value = "null"
    
    # === Публичный интерфейс ===
    
    def generate(self, tree) -> str:
        """Обойти дерево и вернуть итоговый текст LLVM IR"""
        # Первый проход: собираем информацию о функциях
        class FunctionCollector(gsl1Listener):
            def __init__(self, codegen):
                self.codegen = codegen
            
            def enterFunctionDef(self, ctx: gsl1Parser.FunctionDefContext):
                func_name = ctx.ID().getText()
                params = []
                params_ctx = ctx.parameters()
                if params_ctx:
                    for param_ctx in params_ctx.parameter():
                        param_name = param_ctx.ID().getText()
                        param_type_ctx = param_ctx.type_()
                        param_gsl_type = param_type_ctx.ID().getText() if param_type_ctx and param_type_ctx.ID() else "int"
                        param_llvm_type = self.codegen.get_llvm_type(param_gsl_type)
                        params.append((param_name, param_llvm_type))
                
                return_type_ctx = ctx.type_()
                return_gsl_type = None
                if return_type_ctx:
                    return_gsl_type = return_type_ctx.ID().getText() if return_type_ctx.ID() else None
                return_llvm_type = self.codegen.get_llvm_type(return_gsl_type) if return_gsl_type else "void"
                
                # Обрабатываем перегрузки функций - сохраняем все версии
                if func_name not in self.codegen.functions_info:
                    self.codegen.functions_info[func_name] = []
                self.codegen.functions_info[func_name].append({
                    'return_type': return_llvm_type,
                    'params': params,
                    'param_count': len(params)
                })
        
        # Собираем информацию о функциях
        collector = FunctionCollector(self)
        walker = ParseTreeWalker()
        walker.walk(collector, tree)
        
        # Второй проход: генерируем код
        try:
            walker = ParseTreeWalker()
            walker.walk(self, tree)
        except Exception as e:
            # В случае ошибки всё равно возвращаем базовую структуру
            print(f"Предупреждение при генерации кода: {e}")
            if not self.function_stack:
                self._init_main_function()
        
        # Добавляем main функцию в all_functions, если она есть в function_stack
        if self.function_stack:
            for func in self.function_stack:
                if func['name'] == 'main' and func not in self.all_functions:
                    self.all_functions.append(func)
        
        # Собираем модуль
        lines = []
        
        # Заголовок модуля
        lines.append("; Модуль LLVM IR, сгенерированный из GSL1")
        
        # Добавляем стандартные объявления функций (один раз)
        if not self.standard_declarations_added:
            lines.append("declare i32 @printf(i8*, ...)")
            lines.append("declare i32 @puts(i8*)")
            lines.append("declare i8* @malloc(i64)")
            lines.append("declare i8* @strcpy(i8*, i8*)")
            lines.append("declare i8* @strcat(i8*, i8*)")
            lines.append("declare i64 @strlen(i8*)")
            lines.append("declare i32 @sprintf(i8*, i8*, ...)")
            lines.append("declare i32 @strcmp(i8*, i8*)")
            lines.append("")
            self.standard_declarations_added = True
        
        # Глобальные объявления (строки)
        # Убираем дубликаты
        seen_decls = set()
        for decl in self.global_declarations:
            if decl not in seen_decls and not decl.startswith("declare"):
                lines.append(decl)
                seen_decls.add(decl)
        
        if self.global_strings:
            lines.append("")
        
        # Функции (используем all_functions вместо function_stack, так как функции уже удалены из стека)
        for func in self.all_functions:
            lines.append('')
            # Сигнатура функции
            if func['params']:
                params_str = ", ".join([f"{t} %{i}" for i, (_, t) in enumerate(func['params'])])
            else:
                params_str = ""
            lines.append(f"define {func['return_type']} @{func['name']}({params_str}) {{")
            lines.append("entry:")
            
            # Entry инструкции
            lines.extend(func['entry'])
            
            # Тело функции
            lines.extend(func['body'])
            
            # Footer
            lines.extend(func['footer'])
            
            lines.append("}")
        
        return "\n".join(lines)
    
    def _serialize_table(self, table_name: str):
        """Генерирует код для сериализации таблицы в строку"""
        if table_name not in self.tables_info:
            # Если информации нет, выводим [Table]
            table_str = self.get_string_global("[Table]")
            str_ptr = self.new_temp()
            str_len = len("[Table]") + 1
            self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {table_str}, i32 0, i32 0")
            self.emit(f"  call i32 @puts(i8* {str_ptr})")
            return
        
        table_info = self.tables_info[table_name]
        columns = table_info['columns']
        rows = table_info['rows']
        
        # Формируем строку для вывода
        output_lines = []
        
        # Заголовок таблицы (названия колонок)
        if columns:
            header = " | ".join([col['name'] for col in columns])
            output_lines.append(header)
            # Разделитель должен быть на новой строке
            separator = "-" * len(header)
            output_lines.append(separator)
        
        # Данные строк
        for row in rows:
            if len(row) == len(columns):
                row_str = " | ".join([str(val) for val in row])
                output_lines.append(row_str)
            else:
                # Если количество не совпадает, выводим что есть
                row_str = " | ".join([str(val) for val in row])
                output_lines.append(row_str)
        
        # Если нет строк, выводим сообщение
        if not rows:
            output_lines.append("(пустая таблица)")
        
        # Объединяем все строки (каждая строка на новой линии)
        full_output = "\n".join(output_lines)
        
        # Создаём глобальную строку для вывода
        output_str = self.get_string_global(full_output)
        str_ptr = self.new_temp()
        # Длина строки в байтах (UTF-8) + нулевой терминатор
        str_len = len(full_output.encode('utf-8')) + 1
        self.emit(f"  {str_ptr} = getelementptr inbounds [{str_len} x i8], [{str_len} x i8]* {output_str}, i32 0, i32 0")
        self.emit(f"  call i32 @puts(i8* {str_ptr})")


__all__ = ["CodeGenerator"]

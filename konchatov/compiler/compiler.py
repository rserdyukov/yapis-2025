#!/usr/bin/env python3
"""
Компилятор XMLang в Python байт-код через ассемблер
"""

import os
import sys
import marshal
import types
import dis
import struct
import time
import keyword
from xml_parser import XMLParser
from semantic_analyzer import SemanticAnalyzer


class ASTAnalyzer:
    """Анализатор AST XMLang"""
    
    def __init__(self):
        self.functions = []
        self.global_vars = []
        self.imports = set()
        
    def analyze(self, parse_tree):
        """Анализирует AST и извлекает информацию"""
        self._traverse_tree(parse_tree)
        return {
            'functions': self.functions,
            'global_vars': self.global_vars,
            'imports': list(self.imports)
        }
    
    def _traverse_tree(self, node):
        """Рекурсивно обходит AST"""
        if node is None:
            return
            
        # Получаем имя класса узла
        class_name = type(node).__name__
        
        # Анализируем определение функции
        if 'DefContext' in class_name:
            self._analyze_function(node)
        
        # Анализируем присваивание (может быть глобальной переменной)
        elif 'AssignmentContext' in class_name:
            self._analyze_assignment(node)
        
        # Рекурсивно обходим детей
        if hasattr(node, 'children'):
            for child in node.children:
                self._traverse_tree(child)
        elif hasattr(node, '__iter__'):
            # Если node итерируемый (например, список)
            for child in node:
                self._traverse_tree(child)
    
    def _analyze_function(self, node):
        """Анализирует определение функции"""
        func_info = {
            'name': 'unknown',
            'params': [],
            'return_type': 'void',
            'body': node
        }
        
        # Получаем имя функции
        try:
            if hasattr(node, 'ID'):
                id_result = node.ID()
                if id_result:
                    if isinstance(id_result, list):
                        # Берем первый ID как имя функции
                        func_info['name'] = self._get_text_from_node(id_result[0])
                    else:
                        func_info['name'] = self._get_text_from_node(id_result)
        except Exception as e:
            print(f"Warning: Could not get function name: {e}")
        
        # Получаем тип возвращаемого значения
        try:
            if hasattr(node, 'type_'):
                type_node = node.type_()
                if type_node:
                    func_info['return_type'] = self._get_text_from_node(type_node)
        except Exception as e:
            print(f"Warning: Could not get return type: {e}")
        
        # Получаем параметры
        try:
            if hasattr(node, 'ID'):
                id_result = node.ID()
                if id_result:
                    if not isinstance(id_result, list):
                        id_result = [id_result]
                    if len(id_result) > 1:
                        for i in range(1, len(id_result)):
                            param_name = self._get_text_from_node(id_result[i])
                            if param_name and param_name != func_info['name']:
                                if keyword.iskeyword(param_name):
                                    param_name = param_name + '_'
                                func_info['params'].append(param_name)
        except Exception as e:
            print(f"Warning: Could not get function parameters: {e}")
        
        if not func_info['params'] and hasattr(node, 'children'):
            self._find_params_in_children(node, func_info)
        
        if func_info['name'] != 'unknown':
            if keyword.iskeyword(func_info['name']):
                func_info['name'] = func_info['name'] + '_'
            self.functions.append(func_info)
    
    def _find_params_in_children(self, node, func_info):
        """Ищет параметры функции в дочерних узлах"""
        if hasattr(node, 'children'):
            for child in node.children:
                child_text = self._get_text_from_node(child)
                if child_text and child_text in ['int', 'float', 'string', 'bool', 'list', 'document', 'node', 'attribute']:
                    pass
                elif child_text and child_text != func_info['name'] and child_text not in ['(', ')', ',']:
                    if keyword.iskeyword(child_text):
                        child_text = child_text + '_'
                    if child_text not in func_info['params']:
                        func_info['params'].append(child_text)
    
    def _analyze_assignment(self, node):
        """Анализирует присваивание (глобальная переменная)"""
        try:
            if hasattr(node, 'typeList'):
                type_list = node.typeList()
                if type_list:
                    if hasattr(type_list, 'ID'):
                        id_result = type_list.ID()
                        if id_result:
                            if not isinstance(id_result, list):
                                id_result = [id_result]
                            for id_node in id_result:
                                var_name = self._get_text_from_node(id_node)
                                if var_name:
                                    if keyword.iskeyword(var_name):
                                        var_name = var_name + '_'
                                    if var_name not in self.global_vars:
                                        self.global_vars.append(var_name)
                                        print(f"  Found global variable: {var_name}")
        except Exception as e:
            print(f"Warning: Could not analyze assignment: {e}")
    
    def _get_text_from_node(self, node):
        """Безопасно получает текст из узла"""
        try:
            if hasattr(node, 'getText'):
                return node.getText()
            elif hasattr(node, 'text'):
                return node.text
            elif hasattr(node, '__str__'):
                return str(node)
            else:
                return ''
        except:
            return ''


class BytecodeGenerator:
    """Генератор байт-кода Python"""
    
    def __init__(self, ast_info):
        self.ast_info = ast_info
        self.code_objects = {}
        self.python_version = sys.version_info
        
    def generate_bytecode(self):
        """Генерирует байт-код на основе анализа AST"""
        
        # 1. Генерируем вспомогательные функции
        self._generate_helper_functions()
        
        # 2. Генерируем пользовательские функции
        for func_info in self.ast_info['functions']:
            self._generate_function(func_info)
        
        # 3. Генерируем главный модуль
        main_module = self._generate_main_module()
        
        return main_module
    
    def _generate_helper_functions(self):
        """Генерирует вспомогательные функции для XMLang"""
        
        print("Generating helper functions...")
        
        try:
            write_code = compile('''
def xmlang_write():
    """Аналог write() из XMLang"""
    return "test output"
''', 'xmlang_helpers.py', 'exec')
            
            for const in write_code.co_consts:
                if isinstance(const, types.CodeType) and const.co_name == 'xmlang_write':
                    self.code_objects['xmlang_write'] = const
                    break
            
            read_code = compile('''
def xmlang_read():
    """Аналог read() из XMLang"""
    return "test"
''', 'xmlang_helpers.py', 'exec')
            
            for const in read_code.co_consts:
                if isinstance(const, types.CodeType) and const.co_name == 'xmlang_read':
                    self.code_objects['xmlang_read'] = const
                    break
            
            load_code = compile('''
def xmlang_load(path):
    """Аналог load() из XMLang"""
    return "test.xml"
''', 'xmlang_helpers.py', 'exec')
            
            for const in load_code.co_consts:
                if isinstance(const, types.CodeType) and const.co_name == 'xmlang_load':
                    self.code_objects['xmlang_load'] = const
                    break
                    
            print(f"  Created {len(self.code_objects)} helper functions")
            
        except Exception as e:
            print(f"Error generating helper functions: {e}")
    
    def _generate_function(self, func_info):
        """Генерирует байт-код для пользовательской функции"""
        func_name = func_info['name']
        params = func_info['params']
        
        print(f"Generating function: {func_name}")
        
        try:
            params_str = ', '.join(params) if params else ''
            
            if params:
                func_code = compile(f'''
def {func_name}({params_str}):
    """{func_name} function"""
    print("Function {func_name} called")
    return None
''', 'program.xmlang', 'exec')
            else:
                func_code = compile(f'''
def {func_name}():
    """{func_name} function"""
    print("Function {func_name} called")
    return None
''', 'program.xmlang', 'exec')
            
            for const in func_code.co_consts:
                if isinstance(const, types.CodeType) and const.co_name == func_name:
                    self.code_objects[func_name] = const
                    break
            
            if func_name not in self.code_objects:
                for const in func_code.co_consts:
                    if isinstance(const, types.CodeType):
                        self.code_objects[func_name] = const
                        break
            
            print(f"  Generated function {func_name}")
            
        except Exception as e:
            print(f"  Error generating function {func_name}: {e}")
    
    def _sanitize_variable_name(self, name):
        """Очищает имя переменной от конфликтов с ключевыми словами Python"""
        if keyword.iskeyword(name):
            return name + '_val'
        return name
    
    def _generate_main_module(self):
        """Генерирует главный модуль"""
        print("Generating main module...")
        
        try:
            func_defs = []
            for func_name in self.code_objects:
                if func_name not in ['xmlang_write', 'xmlang_read', 'xmlang_load']:
                    func_defs.append(func_name)
            
            module_code_lines = [
                '"""Generated XMLang module"""',
                'import xml.etree.ElementTree as ET',
                '',
                '# Helper functions',
                'def xmlang_write():',
                '    return "test output"',
                '',
                'def xmlang_read():',
                '    return "test"',
                '',
                'def xmlang_load(path):',
                '    return "test.xml"',
                '',
                '# Global variables initialization'
            ]
            
            for var in self.ast_info['global_vars']:
                sanitized_var = self._sanitize_variable_name(var)
                module_code_lines.append(f'{sanitized_var} = None')
            
            module_code_lines.append('')
            module_code_lines.append('# User functions')
            
            for func_name in func_defs:
                if func_name in self.code_objects:
                    module_code_lines.append(f'def {func_name}():')
                    module_code_lines.append(f'    print("Function {func_name} called")')
                    module_code_lines.append(f'    return None')
                    module_code_lines.append('')
            
            if 'main' in self.code_objects:
                module_code_lines.append('# Entry point')
                module_code_lines.append('if __name__ == "__main__":')
                module_code_lines.append('    main()')
            elif func_defs:
                module_code_lines.append('# Entry point')
                module_code_lines.append('if __name__ == "__main__":')
                module_code_lines.append(f'    {func_defs[0]}()')
            
            module_source = '\n'.join(module_code_lines)
            
            module_code = compile(module_source, 'program.xmlang', 'exec')
            
            print(f"  Generated main module with {len(module_code.co_consts)} constants")
            
            return module_code
            
        except Exception as e:
            print(f"  Error generating main module: {e}")
            import traceback
            traceback.print_exc()
            return compile('print("XMLang module loaded")', 'program.xmlang', 'exec')


class PycAssembler:
    """Ассемблер для создания .pyc файлов"""
    
    @staticmethod
    def create_pyc(code_obj, output_file):
        """Создает .pyc файл из код-объекта"""
        
        import importlib.util
        magic = importlib.util.MAGIC_NUMBER
        
        timestamp = int(time.time())
        
        code_size = len(marshal.dumps(code_obj))
        
        header = struct.pack(
            '<4sIII',  # little-endian, 4s=магия, I=timestamp, I=code_size
            magic,
            timestamp,
            code_size,
            0  # reserved
        )
        
        marshalled_code = marshal.dumps(code_obj)
        
        # Пишем в файл
        with open(output_file, 'wb') as f:
            f.write(header)
            f.write(marshalled_code)
        
        return True
    
    @staticmethod
    def disassemble_pyc(pyc_file):
        """Дизассемблирует .pyc файл"""
        try:
            with open(pyc_file, 'rb') as f:

                marshalled_code = f.read()
                

                code_obj = marshal.loads(marshalled_code)
           
                return code_obj
        except Exception as e:
            print(f"Error disassembling: {e}")
            import traceback
            traceback.print_exc()
            return None


class Compiler:
    """Компилятор XMLang в Python байт-код через ассемблер"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.generated_bytecode = None
        self.ast_info = None
    
    def compile_source(self, source_code, output_file=None):
        """Компилирует исходный код"""
        print("=" * 60)
        print("XMLang Compiler (Bytecode Assembler)")
        print(f"Python {sys.version}")
        print("=" * 60)
        
        # 1. Синтаксический анализ
        print("\n[1/5] Parsing syntax...")
        parser = XMLParser(source_code)
        parse_tree = parser.parse()
        
        if parser.has_errors():
            self.errors.extend(parser.get_errors())
            print("Syntax errors found:")
            for error in parser.get_errors():
                print(f"  - {error}")
            return False
        else:
            print("Syntax is valid")
        
        # 2. Семантический анализ
        print("\n[2/5] Semantic analysis...")
        sem_parser = XMLParser(source_code)
        tree = sem_parser.parse()
        analyzer = SemanticAnalyzer()
        errors = analyzer.analyze(tree)
            
        if errors:
            self.errors.extend(errors)
            print("Semantic errors found:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        print("Semantic analysis passed")
        
        # 3. Анализ AST
        print("\n[3/5] Analyzing AST and generating bytecode...")
        ast_analyzer = ASTAnalyzer()
        self.ast_info = ast_analyzer.analyze(parse_tree)
        
        # 4. Генерация байт-кода
        print("\n[4/5] Generating bytecode...")
        generator = BytecodeGenerator(self.ast_info)
        
        try:
            self.generated_bytecode = generator.generate_bytecode()
            
        except Exception as e:
            self.errors.append(f"Bytecode generation error: {str(e)}")
            print(f"Bytecode generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        # 5. Создание .pyc файла
        if output_file:
            print(f"\n[5/5] Assembling {output_file}...")
            return self._assemble_pyc(output_file)
        
        return True
    
    def _assemble_pyc(self, output_file):
        """Создает .pyc файл через ассемблер"""
        try:
            success = PycAssembler.create_pyc(self.generated_bytecode, output_file)
            
            if success:
                print(f"Successfully assembled {output_file}")

                PycAssembler.disassemble_pyc(output_file)
            
            return success
            
        except Exception as e:
            self.errors.append(f"Assembly error: {str(e)}")
            print(f"Assembly failed: {str(e)}")
            return False
    
    def compile_file(self, input_file, output_file=None):
        """Компилирует файл XMLang"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            if not output_file:
                base_name = os.path.splitext(input_file)[0]
                output_file = base_name + '_compiled.pyc'
            
            print(f"Compiling: {input_file}")
            print(f"Output: {output_file}")
            return self.compile_source(source_code, output_file)
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return False


def main():
    """Точка входа"""
    if len(sys.argv) < 2:
        print("Usage: python compiler.py <input_file> [-o output.pyc]")
        print("       python compiler.py --disassemble <file.pyc>")
        print("Example: python compiler.py program.xmlang -o program.pyc")
        return 1
    
    # Режим компиляции
    input_file = sys.argv[1]
    output_file = None
    
    # Обработка аргументов
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    compiler = Compiler()
    success = compiler.compile_file(input_file, output_file)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
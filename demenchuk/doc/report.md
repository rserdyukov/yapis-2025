# Отчет по разработке компилятора языка RivScript

ФИО: Деменчук Егор Михайлович  
Группа: 221703  
Вариант: 6

## Спецификация разработанного языка программирования

### Общее описание

RivScript - язык программирования для работы со списковыми структурами данных. Язык поддерживает семь встроенных типов данных, неявное объявление переменных, блочные операторы с отступами (подобно Python), управляющие конструкции и пользовательские функции с возможностью передачи параметров по ссылке.

### Синтаксис объявления переменных

Переменные объявляются неявно при первом присваивании:

```
<имя_переменной> = <выражение>
```

Примеры:
```
x = 42
name = "Alice"
is_active = true
numbers = [1, 2, 3]
```

Множественное присваивание:
```
a, b = 10, 20
p, q, r = [100, 200, 300]
```

### Синтаксис объявления функций

```
def <имя_функции>(<параметры>):
    <тело_функции>
```

Параметры могут передаваться по значению или по ссылке (с ключевым словом `ref`):

```
def add(a, b):
    return a + b

def swap(ref x, ref y):
    temp = x
    x = y
    y = temp
```

### Синтаксис управляющих конструкций

**Условный оператор:**
```
if <условие>:
    <блок_кода>
else:
    <блок_кода>
```

**Цикл while:**
```
while <условие>:
    <блок_кода>
```

**Цикл until:**
```
until <условие>:
    <блок_кода>
```

**Цикл for:**

Итерация по коллекции:
```
for <переменная> in <коллекция>:
    <блок_кода>
```

Цикл с диапазоном:
```
for <переменная> = <начало> to <конец>:
    <блок_кода>
```

Цикл с шагом:
```
for <переменная> = <начало> to <конец> step <шаг>:
    <блок_кода>
```

### Типы данных

1. **int** - целые числа
2. **string** - строки
3. **bool** - логические значения (true, false)
4. **element** - универсальный контейнер
5. **list** - списки
6. **tree** - деревья (бинарные деревья поиска)
7. **queue** - очереди

### Операции над данными

**Арифметические:**
- Сложение: `a + b`
- Вычитание: `a - b`
- Умножение: `a * b`
- Деление: `a / b`
- Остаток от деления: `a % b`
- Унарный минус: `-a`
- Унарный плюс: `+a`

**Логические:**
- Логическое И: `a and b`
- Логическое ИЛИ: `a or b`
- Логическое НЕ: `not a`

**Сравнения:**
- Равенство: `a == b`
- Неравенство: `a != b`
- Меньше: `a < b`
- Больше: `a > b`
- Меньше или равно: `a <= b`
- Больше или равно: `a >= b`

**Операции со списками:**
- Конкатенация: `list1 + list2`
- Повторение: `list * n`
- Добавление в конец: `list >> element`
- Добавление в начало: `element << list`
- Проверка принадлежности: `element @ list`
- Индексация: `list[index]`

**Приведение типов:**
```
(int) выражение
(string) выражение
(bool) выражение
(element) выражение
```

**Pipeline оператор:**
```
данные |> функция1 |> функция2
```

### Встроенные функции

**Ввод/вывод:**
- `write(value)` - вывод значения
- `read()` - чтение значения

**Работа с element:**
- `element(value)` - создание element
- `get_value(elem)` - извлечение значения
- `set_value(elem, value)` - установка значения

**Работа с деревьями:**
- `build_tree(list)` - построение дерева
- `balance(tree)` - балансировка дерева
- `height(tree)` - высота дерева
- `traverse(tree, order)` - обход дерева
- `merge_trees(tree1, tree2)` - слияние деревьев

**Работа с очередями:**
- `queue()` - создание очереди
- `enqueue(queue, elem)` - добавление в очередь
- `dequeue(queue)` - извлечение из очереди

**Работа со списками:**
- `length(list)` - длина списка
- `sort(list)` - сортировка
- `reverse(list)` - реверс
- `unique(list)` - уникальные элементы
- `join(list, separator)` - объединение в строку
- `merge(list1, list2)` - слияние списков

## Описание грамматики

```antlr
grammar RivScript;

program
    : NEWLINE* program_item* EOF
    ;

program_item
    : function_def NEWLINE*
    | statement NEWLINE*
    | NEWLINE
    ;

function_def
    : DEF ID LPAREN param_list? RPAREN COLON NEWLINE INDENT statement_block DEDENT
    ;

param_list
    : param (COMMA param)*
    ;

param
    : REF? ID
    ;

statement
    : assignment_stmt NEWLINE
    | if_stmt
    | while_stmt
    | until_stmt
    | for_stmt
    | return_stmt NEWLINE
    | expr_stmt NEWLINE
    ;

assignment_stmt
    : id_list ASSIGN expr_list
    ;

id_list
    : ID (COMMA ID)*
    ;

expr_list
    : expr (COMMA expr)*
    ;

statement_block
    : (NEWLINE | statement)+
    ;

if_stmt
    : IF expr COLON NEWLINE INDENT statement_block DEDENT
      (ELSE COLON NEWLINE INDENT statement_block DEDENT)?
    ;

while_stmt
    : WHILE expr COLON NEWLINE INDENT statement_block DEDENT
    ;

until_stmt
    : UNTIL expr COLON NEWLINE INDENT statement_block DEDENT
    ;

for_stmt
    : FOR ID IN expr COLON NEWLINE INDENT statement_block DEDENT
    | FOR ID ASSIGN expr TO expr COLON NEWLINE INDENT statement_block DEDENT
    | FOR ID ASSIGN expr TO expr STEP expr COLON NEWLINE INDENT statement_block DEDENT
    ;

return_stmt
    : RETURN expr?
    ;

expr_stmt
    : expr
    ;

expr
    : pipeline_expr
    ;

pipeline_expr
    : logical_or_expr (PIPELINE logical_or_expr)*
    ;

logical_or_expr
    : logical_and_expr (OR logical_and_expr)*
    ;

logical_and_expr
    : logical_not_expr (AND logical_not_expr)*
    ;

logical_not_expr
    : NOT logical_not_expr
    | comparison_expr
    ;

comparison_expr
    : additive_expr ((EQ | NE | LT | GT | LTE | GTE | MEMBER) additive_expr)?
    ;

additive_expr
    : multiplicative_expr ((PLUS | MINUS | RSHIFT | LSHIFT) multiplicative_expr)*
    ;

multiplicative_expr
    : unary_expr ((STAR | SLASH | MODULO) unary_expr)*
    ;

unary_expr
    : MINUS unary_expr
    | PLUS unary_expr
    | primary_expr
    ;

primary_expr
    : literal
    | function_call
    | list_expr
    | cast_expr
    | LPAREN expr RPAREN
    | primary_expr LBRACKET expr RBRACKET
    | ID
    ;

function_call
    : ID LPAREN arg_list? RPAREN
    ;

arg_list
    : expr (COMMA expr)*
    ;

list_expr
    : LBRACKET (expr (COMMA expr)*)? RBRACKET
    ;

cast_expr
    : LPAREN ID RPAREN expr
    ;

literal
    : INT
    | STRING
    | TRUE
    | FALSE
    | NIL
    ;

DEF: 'def';
RETURN: 'return';
REF: 'ref';
IF: 'if';
ELSE: 'else';
WHILE: 'while';
UNTIL: 'until';
FOR: 'for';
IN: 'in';
TO: 'to';
STEP: 'step';
AND: 'and';
OR: 'or';
NOT: 'not';
TRUE: 'true';
FALSE: 'false';
NIL: 'nil';

PLUS: '+';
MINUS: '-';
STAR: '*';
SLASH: '/';
MODULO: '%';
PIPELINE: '|>';
LSHIFT: '<<';
RSHIFT: '>>';
EQ: '==';
NE: '!=';
LTE: '<=';
GTE: '>=';
LT: '<';
GT: '>';
MEMBER: '@';
ASSIGN: '=';

LPAREN: '(';
RPAREN: ')';
LBRACKET: '[';
RBRACKET: ']';
COLON: ':';
COMMA: ',';

ID: [a-zA-Z_][a-zA-Z0-9_]*;
INT: [0-9]+;
STRING: '"' (~["\r\n] | '\\"')* '"';
COMMENT: '#' ~[\r\n]* -> skip;
MULTILINE_COMMENT: '/*' .*? '*/' -> skip;
NEWLINE: '\r'? '\n';
WS: [ \t]+ -> skip;
INDENT: '<<<INDENT>>>';
DEDENT: '<<<DEDENT>>>';
```

## Описание разработанных классов

### 1. RivScriptIndentLexer

Расширенный лексический анализатор, реализующий обработку отступов по принципу Python. Наследует стандартный лексер ANTLR и добавляет:
- Стек уровней отступов для отслеживания вложенности блоков
- Генерацию токенов INDENT и DEDENT при изменении уровня отступа
- Обработку пустых строк и комментариев
- Валидацию корректности отступов (только пробелы, кратность 4)

### 2. RivScriptParserWrapper

Обертка над сгенерированным ANTLR парсером. Предоставляет:
- Упрощенный интерфейс для инициализации парсера
- Управление error listeners
- Метод parse() для получения дерева разбора (AST)

### 3. SemanticAnalyzer (наследует RivScriptVisitor)

Семантический анализатор выполняет обход AST с использованием паттерна Visitor:
- Управление таблицей символов (SymbolTable) с поддержкой вложенных областей видимости
- Проверка определения переменных и функций перед использованием
- Проверка типов при присваивании и операциях
- Валидация аргументов функций (количество и типы)
- Проверка корректности передачи параметров по ссылке
- Валидация операций приведения типов
- Контроль возврата значений из функций

Основные методы:
- `analyze(tree)` - запуск анализа
- `visitFunction_def()` - обработка определения функции
- `visitAssignment_stmt()` - проверка присваиваний
- `visitFunction_call()` - валидация вызовов функций
- `_infer_type()` - вывод типов выражений

### 4. SymbolTable

Таблица символов для управления областями видимости:
- Стек областей видимости (Scope)
- Регистрация встроенных функций
- Определение и поиск символов (переменные, функции)
- Поддержка перегрузки функций по количеству параметров
- Методы `enter_scope()`, `exit_scope()` для управления вложенностью

### 5. Symbol

Класс для представления символов (переменных, параметров):
- Имя символа
- Тип данных (RivType)
- Категория (SymbolKind: VARIABLE, PARAMETER, FUNCTION, BUILTIN)
- Признак передачи по ссылке

### 6. Scope

Представление области видимости:
- Словарь символов в текущей области
- Ссылка на родительскую область
- Методы для определения и поиска символов

### 7. WATGenerator (наследует RivScriptVisitor)

Генератор кода в формате WebAssembly Text (WAT):
- Транслирует AST в инструкции WebAssembly
- Управляет локальными переменными и метками
- Генерирует заголовок модуля с импортами
- Создает встроенные функции (write, read, element operations)
- Обрабатывает управляющие конструкции (if, while, for)
- Реализует арифметические и логические операции
- Поддерживает работу со стеком операндов WASM

Основные методы:
- `generate(tree)` - генерация WAT кода
- `visitProgram()` - создание главной функции _start
- `visitFunction_def()` - генерация функций
- `visitIf_stmt()`, `visitWhile_stmt()`, `visitFor_stmt()` - управляющие конструкции
- `visitFunction_call()` - генерация вызовов функций

### 8. WATEmitter

Вспомогательный класс для форматированного вывода WAT кода:
- Управление уровнем отступов
- Буферизация выходных строк
- Методы `emit()`, `indent()`, `dedent()`

### 9. WATBuiltins

Класс для генерации встроенных функций WebAssembly:
- Функции ввода/вывода (print_i32, print_str, read_i32)
- Операции с памятью (alloc)
- Работа с element, list, tree, queue

### 10. Система обработки ошибок

**ErrorReporter** - форматирование и вывод ошибок с контекстом исходного кода

**CompilerErrorListener** - перехват ошибок ANTLR

**Иерархия классов ошибок:**
- CompilerError (базовый)
  - LexerError
    - InvalidCharacterError
    - UnclosedStringError
    - IndentationError
  - ParserError
    - SyntaxError
    - MissingTokenError
    - UnexpectedTokenError
  - SemanticError
    - UndefinedVariableError
    - UndefinedFunctionError
    - TypeMismatchError
    - WrongArgCountError
    - ScopeError
    - InvalidCastError
    - RefParamError
    - DuplicateDefinitionError

## Перечень генерируемых ошибок

### Лексические ошибки

1. `Invalid character` - недопустимый символ в исходном коде
2. `Unclosed string` - незакрытая строковая константа
3. `Indentation error` - некорректный отступ (смешивание табов и пробелов, неверная кратность)
4. `Unclosed comment` - незакрытый многострочный комментарий

### Синтаксические ошибки

1. `Syntax error` - общая синтаксическая ошибка
2. `Missing token` - ожидался определенный токен
3. `Unexpected token` - неожиданный токен в данном контексте
4. `Mismatched input` - несоответствие входных данных ожидаемым

### Семантические ошибки

1. `Undefined variable` - использование необъявленной переменной
2. `Undefined function` - вызов необъявленной функции
3. `Type mismatch` - несоответствие типов при операциях или присваивании
4. `Wrong argument count` - неверное количество аргументов функции
5. `Scope error` - переменная вне области видимости
6. `Invalid cast` - недопустимое приведение типов
7. `Ref parameter error` - передача литерала в ref-параметр
8. `Duplicate definition` - повторное определение символа в одной области видимости
9. `Function return type mismatch` - несоответствие типа возвращаемого значения

## Демонстрация работы компилятора

### Пример 1: Корректный код с базовыми типами

Исходный код (`examples/correct/01_basic_types.riv`):

```
x = 42
y = -10
z = 0

name = "Alice"
message = "Hello, RivScript!"

is_active = true
is_complete = false

elem1 = element(100)
value1 = get_value(elem1)
write("Element value: ")
write(value1)

numbers = [1, 2, 3, 4, 5]
names = ["Alice", "Bob", "Charlie"]

concatenated = numbers + [6, 7, 8]
repeated = [1, 2] * 3
added_end = numbers >> 10
added_start = 0 << numbers

first = numbers[0]
is_member = 3 @ numbers

a, b = 10, 20
write("Basic types demonstration complete")
write(x)
write(name)
write(is_active)
write(concatenated)
```

Результат компиляции:

```
Compiled: 01_basic_types.riv -> 01_basic_types.wat
```

Сгенерированный WAT код содержит корректные инструкции для работы со всеми типами данных.

### Пример 2: Ошибка неопределенной переменной

Исходный код (`examples/errors/semantic/01_undefined_variable.riv`):

```
x = 10
y = 20
result = x + undefined_var
write(result)
```

Вывод компилятора:

```
ERROR[E301]: Undefined variable 'undefined_var'
  --> examples/errors/semantic/01_undefined_variable.riv:6:13
   |
  6 | result = x + undefined_var
   |              ^
   |
  hint: Define 'undefined_var' before using it: undefined_var = <value>

1 error(s) generated.
```

### Пример 3: Ошибка несоответствия типов

Исходный код (`examples/errors/semantic/02_type_mismatch.riv`):

```
def number_function():
    return "not a number"

x = 10 + "hello"
y = number_function()
result = y * 2
```

Вывод компилятора:

```
ERROR[E302]: Type mismatch in addition
  --> examples/errors/semantic/02_type_mismatch.riv:4:5
   |
  4 | x = 10 + "hello"
   |     ^^^^^^^^^^^
   |
  hint: Cannot add INT and STRING types

ERROR[E302]: Type mismatch in multiplication
  --> examples/errors/semantic/02_type_mismatch.riv:6:10
   |
  6 | result = y * 2
   |          ^^^^^
   |

2 error(s) generated.
```

### Пример 4: Ошибка аргументов функции

Исходный код (`examples/errors/semantic/04_wrong_arg_count.riv`):

```
def add(a, b):
    return a + b

result1 = add(5)
result2 = add(1, 2, 3)
```

Вывод компилятора:

```
ERROR[E304]: Wrong argument count
  --> examples/errors/semantic/04_wrong_arg_count.riv:4:11
   |
  4 | result1 = add(5)
   |           ^^^^^^
   |
  hint: Function 'add' expects 2 arguments, but got 1

ERROR[E304]: Wrong argument count
  --> examples/errors/semantic/04_wrong_arg_count.riv:5:11
   |
  5 | result2 = add(1, 2, 3)
   |           ^^^^^^^^^^^^
   |
  hint: Function 'add' expects 2 arguments, but got 3

2 error(s) generated.
```

### Пример 5: Корректная работа с функциями

Исходный код (`examples/correct/03_functions.riv`):

```
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

def swap(ref a, ref b):
    temp = a
    a = b
    b = temp

result = factorial(5)
write("Factorial of 5:")
write(result)

x = 10
y = 20
write("Before swap:")
write(x)
write(y)

swap(ref x, ref y)
write("After swap:")
write(x)
write(y)
```

Результат компиляции:

```
Compiled: 03_functions.riv -> 03_functions.wat
```

Программа успешно компилируется, генерируя корректные инструкции для рекурсивных вызовов и передачи параметров по ссылке.

## Заключение

Разработанный компилятор RivScript реализует полный цикл трансляции исходного кода в WebAssembly:

1. Лексический анализ с поддержкой Python-подобных отступов
2. Синтаксический анализ на основе ANTLR4 грамматики
3. Семантический анализ с проверкой типов и областей видимости
4. Генерация целевого кода в формате WAT

Компилятор поддерживает все требуемые функции:
- 7 встроенных типов данных
- Более 10 встроенных операций
- Встроенные функции ввода/вывода и работы со структурами данных
- Блочные операторы с отступами
- Управляющие конструкции (if-else, while, until, for)
- Пользовательские функции с перегрузкой и передачей по ссылке
- Множественное присваивание
- Явное приведение типов

Система обработки ошибок предоставляет информативные сообщения с указанием местоположения и подсказками по исправлению.

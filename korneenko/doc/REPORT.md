# Отчет

ФИО: Корнеенко Егор Дмитриевич\
Группа: 221703\
Вариант: 8

## Спецификация разработанного языка программирования

### Синтаксис объявления таблиц:

```
<TABLE_NAME> = Table(
    <COLUMN_NAME_1> = Сolumn(<TYPE_1>),
    <COLUMN_NAME_2> = Сolumn(<TYPE_2>),
    ...
    <COLUMN_NAME_N> = Сolumn(<TYPE_N>)
)
```

### Синтаксис объявления подпрограмм:

```
func <FUNCTION_NAME> (
    <PARAM_NAME_1>: <PARAM_TYPE_1>, 
    <PARAM_NAME_2>: <PARAM_TYPE_2>, 
    ...
    <PARAM_NAME_N>: <PARAM_TYPE_N>
) -> <RETURN_TYPE>:
    <FUNCTION_BODY>
```

### Синтаксис управляющих конструкций:

1. **if-statement:**
```
if <CONDITION>:
    <IF_BODY>
```

2. **for-loop (итерация по таблице):**
```
for <VAR_NAME> in <TABLE_EXPRESSION>:
    <FOR_BODY>
```

3. **for-loop с условием where:**
```
for <VAR_NAME> in <TABLE_EXPRESSION> where <CONDITION>:
    <FOR_BODY>
```

4. **switch-statement:**
```
switch (<SWITCH_EXPRESSION>):
    case <CASE_VALUE_1>:
        <CASE_BODY_1>
    
    case <CASE_VALUE_2>:
        <CASE_BODY_2>
    
    ...
    
    case <CASE_VALUE_N>:
        <CASE_BODY_N>
    
    default:
        <DEFAULT_BODY>
```

### Синтаксис операций над данными:

1. **Арифметические операции:**
   - Сложение: `<EXPR> + <EXPR>`
   - Вычитание: `<EXPR> - <EXPR>`
   - Умножение: `<EXPR> * <EXPR>`
   - Деление: `<EXPR> / <EXPR>`
   - Остаток от деления: `<EXPR> % <EXPR>`

2. **Операции сравнения:**
   - Равно: `<EXPR> == <EXPR>`
   - Не равно: `<EXPR> != <EXPR>`
   - Меньше: `<EXPR> < <EXPR>`
   - Больше: `<EXPR> > <EXPR>`
   - Меньше или равно: `<EXPR> <= <EXPR>`
   - Больше или равно: `<EXPR> >= <EXPR>`

3. **Логические операции:**
   - Логическое И: `<EXPR> and <EXPR>`
   - Логическое ИЛИ: `<EXPR> or <EXPR>`

4. **Операции с таблицами:**
   - Добавление строки: `<TABLE_NAME> += Row(<VALUE_1>, <VALUE_2>, ..., <VALUE_N>)`
   - Добавление строки (альтернативный синтаксис): `<TABLE_NAME> += row(<VALUE_1>, <VALUE_2>, ..., <VALUE_N>)`
   - Обновление данных: `for <VAR> in <TABLE> where <CONDITION>: <VAR>.<MEMBER> = <VALUE>`
   - Удаление данных: `<TABLE_NAME> -= (<VAR> for <VAR> in <TABLE> if <CONDITION>)`

5. **Операции доступа к членам:**
   - Доступ к полю строки таблицы: `<ROW_VAR>.<MEMBER_NAME>`
   - Доступ к полю строки таблицы в выражении: `<TABLE_EXPR>.<MEMBER_NAME>`

6. **Операция вывода:**
   - Вывод на экран: `print(<EXPRESSION>)`
   - Вывод нескольких значений: `print(<EXPR_1>, <EXPR_2>, ..., <EXPR_N>)`

7. **Операция возврата из функции:**
   - Возврат значения: `return <EXPRESSION>`

8. **Вызов функции:**
   - Вызов функции: `<FUNCTION_NAME>(<ARG_1>, <ARG_2>, ..., <ARG_N>)`

9. **Литералы:**
   - Целые числа: `123`
   - Вещественные числа: `123.45`
   - Строки: `"текст"`
   - Булевы значения: `true`, `false`
   - Пустое значение: `None`

10. **Списки:**
    - Литерал списка: `[<EXPR_1>, <EXPR_2>, ..., <EXPR_N>]`
    - List comprehension: `[<EXPR> for <VAR> in <EXPR> if <CONDITION>]`

## Описание грамматики

```
grammar gsl1;

// ---------- Программа ----------
program
    : (statement | LINE_BREAK)* EOF
    ;

statement
    : functionDef
    | ifStatement
    | switchStatement
    | forLoop
    | simpleStmt
    | caseClause
    | defaultClause
    ;

simpleStmt
    : tableDeclaration
    | dataInsert
    | dataUpdate
    | dataDelete
    | assignment
    | typedAssignment
    | printStatement
    | returnStatement
    ;

// ---------- Объявление таблиц ----------
tableDeclaration: ID '=' TABLE_KW '(' columnDef (',' columnDef)* ')' LINE_BREAK?;
columnDef: ID '=' COLUMN_KW '(' type ')';
type: ID | ID '[' type ']';

// ---------- Операции с таблицами ----------
dataInsert: ID '+=' expression LINE_BREAK?;
dataUpdate: 'for' ID 'in' expression ('where' expression)? suite;
dataDelete: ID '-=' '(' generatorExpression ')' LINE_BREAK?;
generatorExpression: ID 'for' ID 'in' ID ('if' expression)?;

// ---------- Присваивания ----------
assignment: singleAssignment | multipleAssignment | memberAssignment;
singleAssignment: ID '=' expression LINE_BREAK?;
multipleAssignment: ID (',' ID)+ ':=' expression (',' expression)+ LINE_BREAK?;
memberAssignment: ID '.' ID '=' expression LINE_BREAK?;
typedAssignment: ID ':' type '=' expression LINE_BREAK?;

// ---------- Циклы ----------
forLoop: 'for' ID 'in' expression ('where' expression)? suite;

// ---------- Условия ----------
ifStatement: 'if' expression suite;

// ---------- Switch ----------
switchStatement: 'switch' '(' expression ')' suite;
suite
    : emptyBlock
    | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
    | ':' simpleStmt
    | ':' LINE_BREAK INDENT switchBody DEDENT
    ;
switchBody: (caseClause | defaultClause | LINE_BREAK)+;
caseClause: 'case' expression ':' (LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT | simpleStmt | LINE_BREAK);
defaultClause: 'default' ':' (LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT | simpleStmt | LINE_BREAK);
emptyBlock: ':' LINE_BREAK? INDENT? LINE_BREAK* DEDENT?;

// ---------- Функции ----------
functionDef: 'func' ID '(' parameters? ')' ('->' type)? (emptyBlock | ':' LINE_BREAK INDENT functionSuite DEDENT | ':' simpleStmt);
functionSuite: statement+;
parameters: parameter (',' parameter)*;
parameter: ID ':' type;
returnStatement: 'return' expression LINE_BREAK?;

// ---------- Вывод ----------
printStatement: 'print' '(' expression (',' expression)* ')' ';'? LINE_BREAK?;

// ---------- Выражения ----------
expression
    : literal
    | ID
    | expression '.' ID
    | expression '(' (expression (',' expression)*)? ')'
    | '(' expression ')'
    | expression op=('*' | '/' | '%') expression
    | expression op=('+' | '-') expression
    | expression op=('==' | '!=' | '<' | '>' | '<=' | '>=') expression
    | expression 'and' expression
    | expression 'or' expression
    | listLiteral
    | listComprehension
    ;

listLiteral: '[' (expression (',' expression)*)? ']';
listComprehension: '[' expression 'for' ID 'in' expression ('if' expression)? ']';

literal
    : INT
    | FLOAT
    | STRING
    | 'true'
    | 'false'
    | 'None'
    ;

// ---------- Лексер ----------
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]*;
STRING: '"' (~["\\\r\n] | '\\' .)* '"';

FOR: 'for';
IN: 'in';
WHERE: 'where';
IF: 'if';
SWITCH: 'switch';
CASE: 'case';
DEFAULT: 'default';
PRINT: 'print';
FUNC: 'func';
RETURN: 'return';
AND: 'and';
OR: 'or';
TABLE_KW: 'Table';
COLUMN_KW: 'Сolumn';
TRUE: 'true';
FALSE: 'false';
NONE: 'None';

ID: [a-zA-Z_][a-zA-Z_0-9]*;

WS: [ \t]+ -> channel(HIDDEN);
NEWLINE: ('\r'? '\n')+ -> channel(HIDDEN);
COMMENT: '#' ~[\r\n]* -> skip;
BLOCK_COMMENT: '# ===' .*? '===' -> skip;
```

## Описание разработанных классов

1. **Класс `Symbol`** (в `semantic_analyzer.py`). Класс представляет символ в таблице символов. Хранит информацию о переменной или функции: имя, тип, номер строки, является ли функцией, параметры (для функций), возвращаемый тип.

2. **Класс `SemanticAnalyzer`** (в `semantic_analyzer.py`). Класс наследуется от `gsl1Listener` и производит семантический анализ исходного кода. Проверяет:
   - Корректность типов переменных и выражений
   - Области видимости переменных
   - Использование необъявленных переменных и функций
   - Совместимость типов при присваивании
   - Инициализацию переменных перед использованием
   - Корректность вызовов функций (количество и типы аргументов)
   - Наличие return в функциях с возвращаемым типом

3. **Класс `CodeGenerator`** (в `code_generator.py`). Класс наследуется от `gsl1Listener` и производит генерацию LLVM IR кода из AST дерева. Генерирует:
   - Объявления функций
   - Арифметические и логические операции
   - Управляющие конструкции (if, for, switch)
   - Операции с таблицами (создание, добавление, обновление, удаление)
   - Вызовы функций
   - Вывод на экран
   - Сериализацию таблиц для вывода

4. **Класс `VerboseErrorListener`** (в `main.py`). Класс наследуется от `ErrorListener` и обрабатывает синтаксические ошибки парсинга. Собирает ошибки и выводит их в читаемом формате.

## Перечень генерируемых ошибок

### Синтаксические ошибки
Ошибки в синтаксисе исходного кода, проверяются с помощью грамматики ANTLR4:
- Неправильный синтаксис выражений
- Неправильный синтаксис операторов
- Неправильный синтаксис объявлений
- Неправильное использование ключевых слов

### Семантические ошибки
Ошибки в семантике исходного кода, проверяются с помощью класса `SemanticAnalyzer`:

1. **Использование необъявленной переменной** - переменная используется до объявления
2. **Использование необъявленной функции** - функция вызывается до определения
3. **Переменная уже объявлена** - попытка объявить переменную с именем, которое уже используется в текущей области видимости
4. **Функция уже определена** - попытка определить функцию с такой же сигнатурой
5. **Неверное количество аргументов** - функция вызывается с неправильным количеством аргументов
6. **Неверный тип аргумента** - аргумент функции имеет несовместимый тип
7. **Несовместимые типы при присваивании** - попытка присвоить значение несовместимого типа переменной
8. **Попытка обращения к неинициализированной переменной** - переменная используется до инициализации
9. **Обращение к члену недопустимого типа** - попытка обратиться к полю объекта, который не является таблицей или строкой
10. **Использование необъявленной таблицы** - таблица используется до объявления
11. **Операция применима только к таблицам** - операции `+=` и `-=` применяются к переменным, которые не являются таблицами
12. **Тип не объявлен в системе типов** - использование недопустимого типа
13. **return вне функции** - оператор return используется вне тела функции
14. **Неверный тип возвращаемого значения** - функция возвращает значение несовместимого типа
15. **Отсутствие return в функции** - функция с возвращаемым типом не содержит оператор return
16. **Деление на ноль** - попытка деления на константу ноль
17. **Отсутствие ветви default в switch** - switch statement не содержит обязательную ветвь default

## Демонстрация работы

### 1. Приложение для работы с таблицей клиентов:

**Код:**
```
# === Задание структуры таблицы клиентов ===
clients = Table(
    id = Сolumn(int),
    name = Сolumn(str),
    email = Сolumn(str),
    balance = Сolumn(float)
)

# === Добавление данных ===
clients += Row(1, "Alice", "alice@mail.com", 100.0)
clients += Row(2, "Bob", "bob@mail.com", 50.5)
clients += Row(3, "Charlie", "charlie@mail.com", 0.0)

# === Изменение данных ===
# Увеличим баланс клиента Bob на 25.0
for r in clients where r.name == "Bob":
    r.balance = r.balance + 25.0

# Изменим email клиента Charlie
for r in clients where r.id == 3:
    r.email = "charlie@newmail.com"

# === Удаление данных ===
# Удалим клиентов с нулевым балансом
clients -= (row for row in clients if row.balance == 0.0)

# === Вывод итоговой таблицы ===
print("Актуальные данные по клиентам:")
print(clients)
```

**Вывод:**
```
Актуальные данные по клиентам:
id | name | email | balance
---------------------------
1 | Alice | alice@mail.com | 100.0
2 | Bob | bob@mail.com | 75.5
```

### 2. Приложение для работы с заказами и подпрограммами:

**Код:**
```
# === Определение таблицы заказов ===
orders = Table(
    id = Сolumn(int),
    customer = Сolumn(str),
    amount = Сolumn(float),
    status = Сolumn(str)
)

# === Добавление данных ===
orders += row(1, "Alice", 250.0, "new")
orders += row(2, "Bob", 150.0, "shipped")
orders += row(3, "Charlie", 500.0, "cancelled")
orders += row(4, "Alice", 100.0, "processing")

# === Вызов подпрограмм ===
summary_alice: str = get_order_summary(orders, "Alice")
print("Статус по заказам Alice:")
print(summary_alice)

# === Первая версия подпрограммы ===
func get_order_summary(orderTable: table, customerName: str) -> str:
    totalAmount = 0.0
    
    for r in orderTable:
        if r.customer == customerName:
            totalAmount = totalAmount + r.amount
            print("Заказ #" + str(r.id) + " — " + r.status + ", сумма: " + str(r.amount))
    
    return "Общая сумма заказов: " + str(totalAmount)
```

**Вывод:**
```
Заказ #1 — new, сумма: 250.0
Заказ #4 — processing, сумма: 100.0
Статус по заказам Alice:
Общая сумма заказов: 350.0
```

### 3. Приложение для фильтрации сотрудников:

**Код:**
```
# === Определение таблицы сотрудников ===
employees = Table(
    id = Сolumn(int),
    name = Сolumn(str),
    age = Сolumn(int),
    department = Сolumn(str)
)

# === Добавление данных ===
employees += row(1, "Alice", 25, "IT")
employees += row(2, "Bob", 30, "Sales")
employees += row(3, "Charlie", 28, "IT")
employees += row(4, "David", 35, "HR")

# === Вызов подпрограммы ===
result: str = get_young_employees(employees, 30)
print("Сотрудники младше 30:")
print(result)

# === Подпрограмма для фильтрации сотрудников ===
func get_young_employees(empTable: table, maxAge: int) -> str:
    count = 0
    
    for emp in empTable:
        if emp.age < maxAge:
            count = count + 1
            print("Сотрудник: " + emp.name + ", возраст: " + str(emp.age))
    
    return "Всего сотрудников младше " + str(maxAge) + ": " + str(count)
```

**Вывод:**
```
Сотрудник: Alice, возраст: 25
Сотрудник: Charlie, возраст: 28
Сотрудники младше 30:
Всего сотрудников младше 30: 2
```


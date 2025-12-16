# Отчет

ФИО: *[Гордеюк Александра Ивановна]*  
Группа: *[221703]*  
Вариант: 5

---

## 1. Спецификация разработанного языка программирования StringLang

Язык реализует требования варианта 5 (работа со строками) и компилируется в байткод JVM через промежуточное представление Jasmin.

### 1.1. Типы данных

Согласно грамматике `StringLang.g4` и условию лабораторной работы:

Встроенные типы:

```ebnf
type
    : TYPE_CHAR      // 'char'
    | TYPE_STRING    // 'string'
    | TYPE_ARRAY     // 'array'  (массив строк)
    | TYPE_INT       // 'int'
    ;
```

---

### 1.2. Объявление и инициализация переменных

Синтаксис объявления переменной (из `StringLang.g4`):

```ebnf
varDecl
    : type ID (ASSIGN expression)?
    ;
```

То есть:
1. Без инициализации
2. С инициализацией

Семантический анализ объявления (`SemanticAnalyzer.exitVarDecl`):

- Проверка повторного объявления в текущей области видимости
- Запрет использовать имя функции как имя переменной
- Если есть инициализирующее выражение
- Переменная помечается как инициализированная (`is_initialized`) и сохраняется в таблице переменных.

---

### 1.3. Выражения и операции

Вся арифметика и строковые операции описаны в грамматике:

```ebnf
expression
    : inExpr
    | equality
    ;

inExpr
    : equality IN equality
    ;

equality
    : comparison ( (EQ | NEQ) comparison )*
    ;

comparison
    : addition ( (LT | GT) addition )*
    ;

addition
    : multiplication ( (PLUS | MINUS) multiplication )*
    ;

multiplication
    : unary ( (STAR | SLASH) unary )*
    ;

unary
    : MINUS unary
    | postfix
    ;

postfix
    : primary (LBRACK expression RBRACK)*
    ;
```

#### 1.3.1. Поддерживаемые операции

1. **Конкатенация**: `+`
   - Для `string + string`, `string + char`, `char + string`, `char + char`, `int + int`.
   - Семантика в `SemanticAnalyzer._type_of_plus`.
   - Генерация:
     - `int + int` → `iadd`;
     - строковые комбинации → `java/lang/String.concat`.

2. **Удаление подстроки**: `-`
   - Для `string - string` и `int - int`.
   - Типизация в `_type_of_minus`.
   - Для строк — вызов рантайм-функции:
     ```java
     invokestatic StringLangRuntime/removeSubstring(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
     ```
   - Для `int - int` → `isub`.

3. **Умножение**: `*`
   - `int * int` → численное умножение (`imul`).
   - `string * int` → повтор строки:
     ```java
     invokestatic StringLangRuntime/repeatString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
     ```

4. **Деление**: `/`
   - `int / int` → `idiv`.
   - `string / string` → разбиение строки по разделителю:
     ```java
     invokestatic StringLangRuntime/splitString(Ljava/lang/String;Ljava/lang/String;)[Ljava/lang/String;
     ```
   - Типизация в `_type_of_div` (`string / string` даёт `array`).

5. **Индексация**: `[]`
   - Синтаксис:
     ```ebnf
     postfix : primary (LBRACK expression RBRACK)* ;
     ```
   - Для `string[index]` → `char` (внутри как строка длины 1).
   - Для `array[index]` → элемент массива (`string`).
   - Семантика:
     - Проверка, что индекс `int`, иначе ошибка.
     - Проверка, что индексируемый тип — `array` или `string`.
   - Генерация:
     ```java
     // для массива
     invokestatic StringLangRuntime/indexArray([Ljava/lang/String;I)Ljava/lang/String;
     // для строки
     invokestatic StringLangRuntime/indexString(Ljava/lang/String;I)Ljava/lang/String;
     ```

6. **Сравнения**: `==`, `!=`
   - Описание в грамматике `equality`.
   - Типизация `SemanticAnalyzer.exitEquality` → всегда `bool` при сравнении.
   - В кодогенераторе `visitEquality`:
     - Все сравнения реализованы как строковые через:
       ```java
       invokevirtual java/lang/String/equals(Ljava/lang/Object;)Z
       ```
       и инверсия для `!=`.

7. **Сравнения**: `<`, `>`
   - Описание в `comparison`.
   - Типизация:
     - `string`–`string` и `int`–`int` → `bool` (`_type_of_comparison`).
   - Генерация:
     - для `int`–`int`:
       ```java
       if_icmplt / if_icmpgt ...
       ```
     - для строк:
       ```java
       invokestatic StringLangRuntime/stringLessThan(Ljava/lang/String;Ljava/lang/String;)Z
       invokestatic StringLangRuntime/stringGreaterThan(Ljava/lang/String;Ljava/lang/String;)Z
       ```

8. **Оператор `in`**:
   - Синтаксис:
     ```ebnf
     inExpr : equality IN equality ;
     ```
   - Правый операнд может быть `string` или `array`.
   - Семантика (`exitInExpr`):
     ```python
     "'in' operator requires string or array, not '<type>'"
     ```
   - Генерация:
     ```java
     invokestatic StringLangRuntime/stringIn(Ljava/lang/String;Ljava/lang/String;)Z
     ```

9. **Унарный минус**: `-x`
   - Только для `int` (иначе семантическая ошибка).
   - Генерация: `ineg`.

10. **Встроенные функции (как операции над данными)**:
    
    - `len(x)`:
      - тип результата — `int`.
      - Допустимые аргументы: `string` или `array`.
      - Генерация:
        ```java
        invokestatic StringLangRuntime/stringLength(Ljava/lang/String;)I
        ```
    
    - `substr(str, from, to)`:
      - результат `string`.
      - Семантика: первый аргумент должен быть `string`.
      - Генерация:
        ```java
        invokestatic StringLangRuntime/substring(Ljava/lang/String;II)Ljava/lang/String;
        ```
    
    - `replace(str, old, new)`:
      - результат `string`.
      - первый аргумент — `string`.
      - Генерация:
        ```java
        invokestatic StringLangRuntime/replace(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
        ```
    
    - `split(str, sep)`:
      - результат `array`.
      - первый аргумент — `string`.
      - Генерация:
        ```java
        invokestatic StringLangRuntime/splitString(Ljava/lang/String;Ljava/lang/String;)[Ljava/lang/String;
        ```
---

### 1.4. Ввод/вывод

Грамматика:

```ebnf
ioStmt
    : READ LPAREN RPAREN               # readCall
    | WRITE LPAREN expression RPAREN   # writeCall
    ;
```

- `read()`: ввод строки с клавиатуры.
  - Семантика:
    - В `SemanticAnalyzer._check_builtin_function` и `exitBuiltinFunc`:
      - ожидает 0 аргументов;
      - возвращает `string`.
  - Генерация:
    ```java
    invokestatic StringLangRuntime/readString()Ljava/lang/String;
    ```
    (`CodeGenerator._emit_read`)

- `write(x)`: вывод значения.
  - Семантика: один аргумент, тип результата `void`.
  - Генерация:
    ```java
    invokestatic StringLangRuntime/writeValue(Ljava/lang/String;)V
    ```

---

### 1.5. Пользовательские функции

#### Синтаксис объявления

Из грамматики:

```ebnf
functionDecl
    : type ID LPAREN paramList? RPAREN block
    ;

paramList
    : param (COMMA param)*
    ;

param
    : type ID
    ;
```

Функции:

- Всегда имеют возвращаемый тип (`char`, `string`, `array`, `int`).
- Объявляются *только в начале программы*.
- Параметры передаются по значению.


#### Вызов функций

```ebnf
functionCall
    : ID LPAREN (expression (COMMA expression)*)? RPAREN
    ;
```

Семантическая проверка (`exitFunctionCall`):

- Проверка, что функция объявлена
- Сопоставление количества аргументов
- Проверка типов аргументов
- Тип результата — объявленный тип функции.

Генерация вызова (`CodeGenerator.visitFunctionCall`):

  - Вычисление аргументов.
  - Получение сигнатуры JVM на основе типов параметров и возвращаемого типа:
    ```python
    param_desc = "".join(self._type_to_descriptor(t) for t in param_types)
    return_desc = self._type_to_descriptor(func.return_type)
    sig = f"({param_desc}){return_desc}"
    self.emit(f"invokestatic StringLang/{func_name}{sig}")
    ```
- Возврат из функции (`visitReturnStmt`):
  - Для `int` → `ireturn`, для остальных → `areturn`, без выражения → `return`.

---

### 1.6. Управляющие структуры

#### 1.6.1. Условный оператор `if-then-else`

Грамматика:

```ebnf
ifStmt
    : IF expression THEN block (ELSE block)? END
    ;
```

Семантический анализ:

- Для `if` создаётся отдельная область видимости:

  ```python
  enterIfStmt/exitIfStmt:
      scope_name = f"if_<counter>"
      push_scope(scope_name)
      ...
  ```

Генерация (`CodeGenerator.visitIfStmt`):

```pseudo
evaluate condition
ifeq else_label
  <then-block>
goto end_label
else_label:
  <else-block (если есть)>
end_label:
```

#### 1.6.2. Цикл `while`

Грамматика:

```ebnf
whileStmt
    : WHILE LPAREN expression RPAREN block
    ;
```

Семантический анализ:

- Создаётся область видимости `while_X`.
- Счётчик `in_loop_depth` увеличивается/уменьшается.

Генерация (`visitWhileStmt`):

```pseudo
loop_label:
  evaluate condition
  ifeq end_label
  <body>
  goto loop_label
end_label:
```

Есть дополнительная спец-обработка для функции `repeatNTimes` (конкатенация строки и счётчик), что демонстрирует возможность встроенных паттернов, но это частный случай.

#### 1.6.3. Цикл `until`

Грамматика:

```ebnf
untilStmt
    : UNTIL LPAREN expression RPAREN block
    ;
```

Семантика:

- Область видимости `until_X`, учёт глубины цикла.

Генерация (`visitUntilStmt`):

```pseudo
loop_label:
  <body>
  evaluate condition
  ifeq loop_label
end_label:
```

Т.е. повторяется, пока условие ложно (do-until).

#### 1.6.4. Цикл `for`

Вариант языка — «for по коллекции» (строка или массив):

Грамматика:

```ebnf
forInStmt
    : FOR ID IN expression block
    ;
```

Семантика (`SemanticAnalyzer.enterForInStmt`):

- Создаётся область видимости `for_X`.
- Определяется тип выражения-перебираемого.
- Переменная итератора объявляется и помечается инициализированной.

Генерация (`CodeGenerator.visitForInStmt`):

```pseudo
evaluate expression   // получаем массив или результат split
astore temp_array_index    // локальная переменная __for_array

ldc 0
istore counter_index       // __for_counter

loop_label:
  iload counter_index
  aload temp_array_index
  arraylength
  if_icmpge end_label

  aload temp_array_index
  iload counter_index
  aaload
  astore iter_var_index

  <body>

  iload counter_index
  ldc 1
  iadd
  istore counter_index

  goto loop_label
end_label:
```

---

### 1.7. Области видимости

Реализованы в `SemanticAnalyzer`:

- Таблица переменных: `variables_map: Dict[str, Dict[str, Variable]]`.
- Стек областей: `scope_stack: List[str]`.
- Глобальная область: `'.'`.

Принцип работы:

- `push_scope(name)`:
  - Новая область наследует все переменные родительской:
    ```python
    parent_vars = self.variables_map.get(parent_scope, {})
    self.variables_map[scope_name] = dict(parent_vars)
    ```
- `is_variable_locally_declared`:
  - Проверяет, что имя переменной есть в текущей области, но нет в непосредственном родителе — чтобы запретить повторное объявление внутри одного блока, но позволить «затенение» во вложенных блоках.

---

## 2. Описание грамматики языка

Ниже приведена сокращённая, но полная по ключевым конструкциям грамматика (`StringLang.g4`).

```antlr
grammar StringLang;

program
    : functionDecl* statement* EOF
    ;

// -------------------------
// ФУНКЦИИ
// -------------------------
functionDecl
    : type ID LPAREN paramList? RPAREN block
    ;

paramList
    : param (COMMA param)*
    ;

param
    : type ID
    ;

// -------------------------
// ИНСТРУКЦИИ
// -------------------------
statement
    : varDecl
    | assignment
    | ioStmt
    | ifStmt
    | whileStmt
    | untilStmt
    | forInStmt
    | returnStmt
    | exprStmt
    | block
    ;

varDecl
    : type ID (ASSIGN expression)?
    ;

assignment
    : lvalue (COMMA lvalue)* ASSIGN expression (COMMA expression)*
    ;

lvalue
    : ID (LBRACK expression RBRACK)*
    ;

ioStmt
    : READ LPAREN RPAREN               # readCall
    | WRITE LPAREN expression RPAREN   # writeCall
    ;

ifStmt
    : IF expression THEN block (ELSE block)? END
    ;

whileStmt
    : WHILE LPAREN expression RPAREN block
    ;

untilStmt
    : UNTIL LPAREN expression RPAREN block
    ;

forInStmt
    : FOR ID IN expression block
    ;

returnStmt
    : RETURN expression?
    ;

exprStmt
    : expression
    ;

block
    : LBRACE statement* RBRACE
    ;

// -------------------------
// ВЫРАЖЕНИЯ
// -------------------------

expression
    : inExpr
    | equality
    ;

inExpr
    : equality IN equality
    ;

equality
    : comparison ( (EQ | NEQ) comparison )*
    ;

comparison
    : addition ( (LT | GT) addition )*
    ;

addition
    : multiplication ( (PLUS | MINUS) multiplication )*
    ;

multiplication
    : unary ( (STAR | SLASH) unary )*
    ;

unary
    : MINUS unary
    | postfix
    ;

postfix
    : primary (LBRACK expression RBRACK)*
    ;

primary
    : castExpr
    | functionCall
    | builtinFunc
    | atom
    ;

// -------------------------
// ВСТРОЕННЫЕ ФУНКЦИИ
// -------------------------
builtinFunc
    : LEN LPAREN expression RPAREN
    | SUBSTR LPAREN expression COMMA expression COMMA expression RPAREN
    | REPLACE LPAREN expression COMMA expression COMMA expression RPAREN
    | SPLIT LPAREN expression COMMA expression RPAREN
    ;

castExpr
    : LPAREN type RPAREN expression
    ;

functionCall
    : ID LPAREN (expression (COMMA expression)*)? RPAREN
    ;

// -------------------------
// АТОМЫ
// -------------------------
atom
    : INT
    | CHAR_LITERAL
    | STRING_LITERAL
    | arrayLiteral
    | ID
    | LPAREN expression RPAREN
    ;

arrayLiteral
    : LBRACK (expression (COMMA expression)*)? RBRACK
    ;

// -------------------------
// ТИПЫ
// -------------------------
type
    : TYPE_CHAR
    | TYPE_STRING
    | TYPE_ARRAY
    | TYPE_INT
    ;

// -------------------------
// ЛЕКСЕР
// -------------------------
IF      : 'if' ;
THEN    : 'then' ;
ELSE    : 'else' ;
END     : 'end' ;
WHILE   : 'while' ;
UNTIL   : 'until' ;
FOR     : 'for' ;
IN      : 'in' ;
READ    : 'read' ;
WRITE   : 'write' ;
RETURN  : 'return' ;
LEN     : 'len' ;
SUBSTR  : 'substr';
REPLACE : 'replace';
SPLIT   : 'split';
TYPE_CHAR   : 'char' ;
TYPE_STRING : 'string' ;
TYPE_ARRAY  : 'array' ;
TYPE_INT    : 'int' ;

PLUS    : '+' ;
MINUS   : '-' ;
STAR    : '*' ;
SLASH   : '/' ;
EQ      : '==' ;
NEQ     : '!=' ;
LT      : '<' ;
GT      : '>' ;
ASSIGN  : '=' ;
COMMA   : ',' ;
SEMI    : ';' ;
LPAREN  : '(' ;
RPAREN  : ')' ;
LBRACK  : '[' ;
RBRACK  : ']' ;
LBRACE  : '{' ;
RBRACE  : '}' ;

ID  : [a-zA-Z_] [a-zA-Z0-9_]* ;
INT : [0-9]+ ;

CHAR_LITERAL
    : '\'' (~[\\'\r\n]) '\''
    ;

STRING_LITERAL
    : '"' ( ~["\\\r\n] | '\\' . )* '"'
    ;

WS  : [ \t\r\n]+ -> skip ;

COMMENT
    : '//' ~[\r\n]* -> skip
    ;
```

---

## 3. Описание разработанных классов

### 3.1. `SemanticAnalyzer` (семантический анализ)
Функции:

- Управление областями видимости:
  - `scope_stack`, `variables_map`, `push_scope`, `pop_scope`.
- Таблица функций: `functions_map: Dict[str, Function]`.
- Кэш типов для узлов дерева: `type_cache: Dict[ctx, str]`.
- Семантические ошибки: `semantic_errors: List[Error]`.

Основные проверки:

1. **Функции**:
   - Повторное объявление функции.
   - Конфликт имени функции и переменной.
   - Уникальность имён параметров внутри одной функции.
   - Сохранение списка параметров и типа возврата в `Function`.

2. **Переменные**:
   - Повторное объявление в одной области.
   - Конфликт с именем функции.
   - Использование необъявленной переменной.
   - Использование до инициализации.
   - Присваивание значения несовместимого типа.
   - Индексация не массива/строки.
   - Индекс массива/строки не `int`.

3. **Присваивание**:
   - Поддержка многоцелевого присваивания:
     - количество LHS и RHS должно совпадать.
     - типы RHS совместимы с типами LHS.

4. **Выражения**:
   - Определение типов атомов, массивов, идентификаторов.
   - Типизация операций `+`, `-`, `*`, `/`, сравнений, `in`.
   - Проверка аргументов встроенных функций (`len`, `substr`, `replace`, `split`).

5. **Циклы и if**:
   - Создание новых областей (`if_X`, `while_X`, `until_X`, `for_X`).
   - Проверка типа перебираемого в `for in` (`string` или `array`).

6. **Возврат**:
   - `return` только внутри функции.
   - Тип возвращаемого выражения совместим с типом функции.
   - При отсутствии выражения в `return` — функция должна иметь «пустой» ожидаемый тип (в текущей реализации это `TYPE_UNKNOWN`; если тип функции известен — ошибка).

---

### 3.2. `CodeGenerator` (генератор байткода JVM)
Назначение:

- Посещает дерево разбора (`ProgramContext`, `StatementContext`, ...).
- Генерирует инструкции JVM-подобного ассемблера (Jasmin).

Основные структуры:

- `instructions: List[str]` — инструкции для «глобального» кода (main).
- `function_instructions: Dict[str, List[str]]` — инструкции для каждой функции.
- `local_vars: Dict[str, int]` и `function_local_vars: Dict[str, Dict[str, int]]` — отображение имени переменной в индекс локала JVM.
- Счётчики локальных переменных и меток (`label_counter`).
- Стек меток циклов `loop_label_stack`.

Основные возможности:

1. Генерация кода для:
   - объявлений переменных (`visitVarDecl`);
   - присваиваний (`visitAssignment`);
   - ввод/вывод (`visitIoStmt`, `_emit_read`, `_emit_write`);
   - `if-then-else`, `while`, `until`, `for in`;
   - выражений, всех операций и встроенных функций;
   - пользовательских функций и `return`.

2. Управление локальными переменными:
   - `allocate_local_var`, `_load_var`, `_store_var`.

3. Поддержка пользовательских функций:
   - Для каждой функции формируется свой список инструкций.
   - Преобразование типов языка в дескрипторы JVM (`_type_to_descriptor`).

---

### 3.3. `SyntaxErrorListener`
Назначение:

- Перехват синтаксических ошибок лексера и парсера.
- Формирует объекты `Error` с типом `ErrorType.SYNTAX`.

---

### 3.4. `Emitter`
Назначение (по использованию):

- Получает:
  - инструкции глобального кода и функций,
  - числа локальных переменных,
  - семантическую информацию.
- Генерирует итоговый текст `.j` файла (Jasmin) для JVM.

---

### 3.5. Модели и константы
- `Error` — модель ошибки: строка, столбец, сообщение, тип.
- `ErrorType` — перечисление типов ошибок (синтаксическая, семантическая).
- `Variable` — модель переменной (имя, тип, тип присвоенного значения, флаги параметра/инициализации).
- `Function` — модель функции (имя, тип возврата, список параметров).

- Строковые константы типов (`TYPE_INT`, `TYPE_STRING`, `TYPE_CHAR`, `TYPE_ARRAY`, `TYPE_BOOL`, `TYPE_UNKNOWN`, `TYPE_VOID`).
- Отображение типов в дескрипторы JVM (`JVM_TYPE_DESCRIPTORS`).
- Множество встроенных функций `BUILTIN_FUNCTIONS`.

---

## 4. Перечень генерируемых ошибок

Система различает синтаксические и семантические ошибки.

### 4.1. Синтаксические ошибки

Генерируются ANTLR‑парсером и лексером, обрабатываются `SyntaxErrorListener`:

- Любое несоответствие исходного кода грамматике:
  - неожиданный токен;
  - отсутствующий закрывающий символ (`)`, `]`, `}`, `end` и т.п.);
  - неправильная структура выражений или операторов.


### 4.2. Семантические ошибки

Обнаруживаются в `SemanticAnalyzer`:

1. Повторное объявление функции
2. Конфликт идентификатора: функция / переменная
3. Повторное объявление параметра в сигнатуре функции
4. Повторное объявление переменной в той же области видимости
5. Несовместимость типов при инициализации
6. Несовместимость типов при присваивании
7. Использование необъявленной переменной
8. Использование переменной до инициализации
9. Неверное использование индексации
10. Несоответствие количества LHS и RHS в многоцелевом присваивании
11. Неверное использование оператора `in`
12. Неверные аргументы встроенных функций
13. Неверные типы аргументов пользовательских функций
14. Неверное количество аргументов в пользовательских функциях
15. Использование необъявленной функции
16. Некорректные операции над типами
17. Цикл `for in` по неподходящему типу
18. Ошибки возврата
---

## 5. Демонстрация работы

### 5.1. algoritm_1.txt

```text
string s = "hello";
string t = "world";
string u = s + ", " + t;   // "hello, world"

write(u);                  // вывод: hello, world

if "lo" in s then
    write("substring 'lo' found");
else
    write("not found");
end
```

Syntax and semantic analysis passed
Code generated: output\algorithm_1.j
Compilation successful!
Generated: output\StringLang.class
hahaha

---

### 5.2. algorithm_2.txt

```text
array words = ["a","b","c"];

for w in words {
    write(w);
}
```
Syntax and semantic analysis passed
Code generated: output\algorithm_2.j
Compilation successful!
Generated: output\StringLang.class
the
sun
shining

---

### 5.3. algorithm_3.txt

```text
string line = "a,b,c,d";
array parts = split(line, ",");

int n = len(parts);    // количество элементов

int i = 0;
while (i < n) {
    write(parts[i]);
    i = i + 1;
}
```
Syntax and semantic analysis passed
Code generated: output\algorithm_3.j
Compilation successful!
Generated: output\StringLang.class
Удаление прошло успешно: bnana

---

### 5.4. algorithm_4.txt

```text
string repeat(string s, int n) {
    string res = "";
    int i = 0;
    while (i < n) {
        res = res + s;
        i = i + 1;
    }
    return res;
}

string x = repeat("ha", 3);   // "hahaha"
write(x);
```
Syntax and semantic analysis passed
Code generated: output\algorithm_4.j
Compilation successful!
Generated: output\StringLang.class
Повтор: bananabananabanana
Подстрока и замена: b*n
Слишком длинная строка: bananabananabanana
Повтор: orangeorangeorange
Подстрока и замена: or*
Слишком длинная строка: orangeorangeorange
Повтор: appleappleapple
Подстрока и замена: *pp
Слишком длинная строка: appleappleapple
Комбинация с скобками: banana-orange-apple

---

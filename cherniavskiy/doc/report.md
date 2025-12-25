# Отчет

ФИО: _[Чернявский Максим Сергеевич]_  
Группа: _[221703]_  
Вариант: 15

---

## 1. Спецификация разработанного языка программирования

Разработанный язык является статически типизированным процедурным языком программирования. Компилятор генерирует ассемблерный код для виртуальной машины Java (Jasmin/JVM).

### a. Синтаксис объявления переменных и подпрограмм

**Типы данных:**

-   `int` (целое число)
-   `bool` (логический тип: `true`, `false`)
-   `string` (строка)
-   `char` (символ)
-   `rune` (юникод-символ, синоним int в реализации)
-   `void` (пустой тип, только для возвращаемых значений функций)
-   Массивы: `[]int`, `[]string` и т.д.

**Объявление переменных:**
Переменные объявляются с указанием типа. Поддерживается множественное объявление и инициализация.

```go
int a, b = 10, 20;
string str = "Hello";
char c; // Объявление без инициализации (значение по умолчанию)
[]string arr = {"item1", "item2"};
```

**Объявление функций (подпрограмм):**
Используется ключевое слово `func`.

```go
func имяФункции(тип аргумент1, тип аргумент2) типВозврата {
    // Тело функции
    return значение;
}

// Пример main (точка входа)
func main() {
    ...
}
```

### b. Синтаксис операций над данными

Реализовано более 10 операций. Особенностью языка является перегрузка операторов для различных типов (строк, массивов).

1.  **Присваивание (`=`):** `a = 5`
2.  **Сложение (`+`):**
    -   Числа: `1 + 2` (сумма)
    -   Строки: `"a" + "b"` (конкатенация)
    -   Массивы: `arr1 + arr2` (объединение массивов)
    -   Массив + Элемент: `arr + item` (добавление элемента)
3.  **Вычитание (`-`):**
    -   Числа: `5 - 3`
    -   Строки: `"hello" - "l"` (удаление первого вхождения подстроки)
    -   Массивы: `arr1 - arr2` (удаление элементов второго массива из первого)
4.  **Умножение (`*`):**
    -   Числа: `2 * 3`
    -   Строка _ Число: `"abc" _ 2`->`"abcabc"` (повторение строки)
    -   Массив _ Число: `arr _ 2` (повторение содержимого массива)
5.  **Деление (`/`):**
    -   Числа: `10 / 2`
    -   Строка / Число: `"abcd" / 2` -> `"ab"` (деление длины строки: взятие первой части)
    -   Массив / Число: `arr / n` (разбиение массива на подмассивы, возвращает массив массивов - реализовано частично как flatten в текущей версии)
6.  **Деление с остатком / Special Split (`\`):**
    -   Используется в грамматике как токен `SPLIT`.
7.  **Инкремент (`++`):** `i++` (аналог `i = i + 1`)
8.  **Сравнение на равенство (`==`):** Работает для чисел и строк.
9.  **Сравнение на неравенство (`!=`).**
10. **Отношения (`<`, `>`, `<=`, `>=`).**
11. **Взятие длины (`len`):** `len(str)` или `len(arr)`.
12. **Индексация (`[]`):** `str[0]`, `arr[5]`.

### c. Синтаксис управляющих конструкций

**Условный оператор:**

```go
if expression {
    ...
} else {
    ...
}
```

**Переключатель (Switch):**
Поддерживает `switch` без выражения (аналог цепочки if-else).

```go
switch {
    case x > 0 { ... }
    case x == 0 { ... }
    default { ... }
}
```

**Цикл (For):**
C-подобный синтаксис.

```go
for int i = 0; i < 10; i++ {
    if i == 5 { break; }
    continue;
}
```

**Ввод/Вывод:**

```go
print(expression); // Вывод с новой строкой
read(variable);    // Чтение
write(expression); // Вывод
```

---

## 2. Оформленный файл грамматики (Variant15.g4)

```antlr
grammar Variant15;

// === Синтаксический анализ ===

// Точка входа: программа состоит из функций
program: functionDeclaration* EOF;

// Блок кода в фигурных скобках
block: LBRACE statement* RBRACE;

// Возможные инструкции
statement
    : variableDeclaration       // Объявление переменных
    | assignment                // Присваивание
    | ifStatement               // Ветвление
    | switchStatement           // Выбор
    | forStatement              // Цикл
    | functionCall              // Вызов функции
    | ioStatement               // Ввод-вывод
    | functionDeclaration       // Вложенные функции (разрешены грамматикой)
    | BREAK                     // Прерывание цикла
    | CONTINUE                  // Продолжение цикла
    | RETURN expression?        // Возврат из функции
    | block                     // Вложенный блок
    ;

// Объявление переменных: тип имя [= знач], имя2 [= знач2]
variableDeclaration: typeSpecifier IDENTIFIER (COMMA IDENTIFIER)* (ASSIGN expression (COMMA expression)*)?;

// Присваивание или инкремент
assignment: designator (COMMA designator)* ASSIGN expression (COMMA expression)*
          | designator INC;

// Обозначение переменной или элемента массива (a, a[0], a[0][1])
designator: IDENTIFIER (LBRACK expression (COLON expression)? RBRACK)*;

// If-Else
ifStatement: IF expression? block (ELSE block)?;

// Switch-Case
switchStatement: SWITCH LBRACE caseBlock* defaultBlock? RBRACE;
caseBlock: CASE expression block;
defaultBlock: DEFAULT block;

// Цикл For
forStatement: FOR (variableDeclaration | assignment)? SEMI expression? SEMI (assignment | expression)? block;

// Объявление функции
functionDeclaration: FUNC IDENTIFIER LPAREN parameterList? RPAREN typeSpecifier? block;
parameterList: parameter (COMMA parameter)*;
parameter: typeSpecifier IDENTIFIER;

// Вызов функции
functionCall: IDENTIFIER LPAREN argumentList? RPAREN;
argumentList: expression (COMMA expression)*;

// Ввод-вывод
ioStatement: READ LPAREN IDENTIFIER RPAREN
           | WRITE LPAREN expression RPAREN
           | PRINT LPAREN argumentList RPAREN;

// Выражения с приоритетами
expression
    : LPAREN expression RPAREN
    | expression (MULT | DIV | SPLIT) expression
    | expression (PLUS | MINUS) expression
    | expression (EQ | NEQ | LT | GT | LE | GE) expression
    | atom
    ;

// Атомарные элементы выражения
atom: designator
    | STRING_LITERAL
    | CHAR_LITERAL
    | INT_LITERAL
    | BOOL_LITERAL
    | functionCall
    | LEN LPAREN expression RPAREN
    | arrayLiteral
    ;

arrayLiteral: LBRACE (expression (COMMA expression)*)? RBRACE;

// Типы данных (включая массивы)
typeSpecifier: LBRACK RBRACK? primitiveType LBRACK RBRACK?
             | primitiveType;

primitiveType: STRING | CHAR | RUNE | INT | BOOL | VOID;

// === Лексический анализ (Токены) ===

FUNC: 'func';
RETURN: 'return';
IF: 'if';
ELSE: 'else';
SWITCH: 'switch';
CASE: 'case';
DEFAULT: 'default';
FOR: 'for';
BREAK: 'break';
CONTINUE: 'continue';
READ: 'read';
WRITE: 'write';
PRINT: 'print';
LEN: 'len';
STRING: 'string';
CHAR: 'char';
RUNE: 'rune';
INT: 'int';
BOOL: 'bool';
VOID: 'void';

BOOL_LITERAL: 'true' | 'false';

PLUS: '+';
MINUS: '-';
MULT: '*';
SPLIT: '\\';
DIV: '/';
INC: '++';
ASSIGN: '=';
EQ: '==';
NEQ: '!=';
LT: '<';
GT: '>';
LE: '<=';
GE: '>=';
SEMI: ';';
COMMA: ',';
COLON: ':';
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';

IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
INT_LITERAL: [0-9]+;
STRING_LITERAL: '"' .*? '"';
CHAR_LITERAL: '\'' . '\'' | '\'' '\\' . '\'';

WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
```

---

## 3. Описание дополнительно разработанных классов

### `JvmCompiler` (compiler.ts)

Основной класс, реализующий паттерн `Listener` (Visitor) для обхода дерева разбора ANTLR.

-   **Цель:** Генерация байт-кода Jasmin (ассемблер JVM).
-   **Ключевые возможности:**
    -   Поддержка стека контекстов методов (`MethodContext`) для генерации кода внутри функций.
    -   Управление локальными переменными (маппинг имен переменных на индексы JVM слотов).
    -   Реализация перегрузки операторов через статические хелпер-методы (`__repeatString`, `__subList` и т.д.), которые инжектируются в начало генерируемого файла.
    -   Генерация меток (`labels`) для реализации `if`, `switch` и циклов `for`.

### `SemanticAnalyzer` & `SemanticListener` (semantic.ts)

Классы для семантического анализа перед компиляцией.

-   **Scope:** Класс, моделирующий область видимости. Поддерживает вложенность областей (например, блок `if` внутри функции).
-   **Symbol Table:** Хранит информацию об объявленных идентификаторах (имя, тип, вид: переменная/функция).
-   **Checks:** Проверяет повторное объявление переменных и использование необъявленных идентификаторов. Проверяет сигнатуры функций для поддержки перегрузки.

### `CustomErrorListener`

Перехватывает синтаксические ошибки от ANTLR Lexer и Parser для отображения их в пользовательском интерфейсе, предотвращая падение приложения.

---

## 4. Перечень генерируемых ошибок

Компилятор и анализатор генерируют следующие типы ошибок:

### Синтаксические ошибки (от ANTLR):

1.  `mismatched input` — встречен токен, который не ожидался грамматикой (например, `if` без условия).
2.  `missing X at Y` — пропущен обязательный символ (например, `;` или `}`).
3.  `extraneous input` — лишние символы.
4.  `token recognition error` — лексическая ошибка (неизвестный символ).

### Семантические ошибки:

1.  `SemError (Pos X): Identifier 'name' already declared in this scope.` — попытка повторного объявления переменной в том же блоке.
2.  `SemError (Pos X): Undefined identifier 'name'.` — использование переменной или функции, которая не была объявлена.
3.  `SemError (Pos X): Function 'name' with signature '...' already declared in this scope.` — ошибка перегрузки функций (дубликат сигнатуры).

---

## 5. Примеры работы компилятора

### Пример 1: Работа со строками и перегрузка операторов

**Исходный код:**

```go
func main() {
    string str = "abc"
    // Умножение строки на число (повторение)
    print(str * 2)
    // Вычитание подстроки
    print("hello" - "l")
}
```

**Результат компиляции (фрагмент Jasmin):**

```jasmin
.method public static main([Ljava/lang/String;)V
    ...
    ldc "abc"
    astore 1
    aload 1
    iconst_2
    invokestatic Program/__repeatString(Ljava/lang/String;I)Ljava/lang/String;
    invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
    ...
    ldc "hello"
    ldc "l"
    invokestatic Program/__subString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    invokevirtual java/io/PrintStream/println(Ljava/lang/String;)V
    return
.end method
```

**Вывод:**

```
abcabc
helo
```

### Пример 2: Split (Пример 3 из ЛР)

**Исходный код:**

```go
func Split(string str, char delim, []string parts) []string{
    string newString = ""
    for int strPos = 0;strPos < len(str); strPos++ {
        if str[strPos] == delim {
            if len(newString) == 0 { continue }
            parts = parts + newString
            newString = ""
            continue
        }
        newString = newString + str[strPos]
    }
    if len(newString) > 0 {
        parts = parts + newString
    }
    return parts
}

func main() {
    []string parts = {}
    string str = "В стране магнолий\nплещет\nморе"
    parts = Split(str, '\n', parts)
    print(parts)
}
```

**Вывод (Output):**

```
[В стране магнолий, плещет, море]
```

Этот пример демонстрирует сложные конструкции: циклы, условия, работу с символами (`\n`), массивами (`parts + newString`) и пользовательскими функциями.

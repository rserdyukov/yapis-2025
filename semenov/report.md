# Отчет

ФИО: Семенов Егор Геннадьевич\
Группа: 221703\
Вариант: 14

## Спецификация разработанного языка программирования

#### Объявление функций

```
<TYPE> <FUNCTION_NAME>(<PARAM_LIST>):
    <FUNCTION_BODY>
<PARAM_LIST> = <PARAM> (, <PARAM>)*
<PARAM> = ('out')? <TYPE> <NAME>
```

#### Объявление переменных:

1. Без инициализации:
```
<TYPE> <NAME>
```

2. С инициализацией:
```
<TYPE> <NAME> = <EXPR>
```

3. Множественное объявление
```
<TYPE> <ID> (',' <ID>)*
```

4. Множественная инициализация
```
<ID> (',' <ID>)* '=' <EXPR> (',' <EXPR>)*
```

5. Неявное объявление (тип выводится из выражения)
```
<ID> = <EXPR>
```

#### Управляющие конструкции:

1. if/else: 
```
if (<EXPR>):
    <BODY>
else:
    <BODY>
```

2. while
```
while (<CONDITION>):
    <BODY>
```

3. for
```
for (<INIT>; <COND>; <ITER>):
    <BODY>
```

#### Вызовы функций:
```
<ID>(<ARG_LIST>)
```

#### Операции над данными: 

1. Арифметические операции
```
<EXPR> + <EXPR>
<EXPR> - <EXPR>
<EXPR> * <EXPR>
<EXPR> / <EXPR>
<EXPR> % <EXPR>
```

2. Логические операции
```
<EXPR> && <EXPR>
<EXPR> || <EXPR>
!<EXPR>
```

3. Операции сравнения
```
<EXPR> >  <EXPR>
<EXPR> >= <EXPR>
<EXPR> <  <EXPR>
<EXPR> <= <EXPR>
<EXPR> == <EXPR>
<EXPR> != <EXPR>
```

4. Операции инкремента/декремента
```
++<EXPR>
--<EXPR>
<EXPR>++
<EXPR>--
```

5. Операции присваивания
```
<ID> += <EXPR>
<ID> -= <EXPR>
<ID> *= <EXPR>
<ID> /= <EXPR>
```

6. Операция каста 
```
(<TYPE>) <EXPR>
```

7. Литералы коллекций
```
set[<EXPR_LIST>?]
element(<EXPR>)
```

8. Доступ по индексу
```
<ID>[<EXPR>]
```

#### Типы данных:
```
1. int 
2. float
3. double
4. char
5. str
6. bool
7. element
8. set
9. void
```

## Описание грамматики

```
grammar lang;

// Программа состоит из набора функций и операторов
program
    : (statement | LINE_BREAK)* EOF
    ;

// Оператор - функция или простое выражение
statement
    : functionDef
    | simpleStmt
    ;

// Объявление функции
functionDef
    : type ID '(' parameterList? ')'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
    ;

// Список параметров
parameterList
    : parameter (',' parameter)*
    ;

// Параметр функции (может быть out)
parameter
    : ('out')? type ID
    ;

// Простые операторы
simpleStmt
    : varDecl
    | assignment
    | funcCall
    | 'return' expr? LINE_BREAK
    | ifStmt
    | whileStmt
    | forStmt
    ;

// Объявление переменных
varDecl
    : type ID (',' ID)* ('=' exprList)? LINE_BREAK
    | ID '=' exprList LINE_BREAK
    | ID LINE_BREAK
    ;

// Присваивание
assignment
    : type ID (',' ID)* (('=' exprList)
         | PLUS_ASSIGN expr
         | MINUS_ASSIGN expr
         | MUL_ASSIGN expr
         | DIV_ASSIGN expr
         | INC
         | DEC)? LINE_BREAK
    | ID (('=' exprList)
         | PLUS_ASSIGN expr
         | MINUS_ASSIGN expr
         | MUL_ASSIGN expr
         | DIV_ASSIGN expr
         | INC
         | DEC)? LINE_BREAK
    ;

// Список выражений
exprList
    : expr (',' expr)*
    ;

// Пустой блок
emptyBlock
    : ':' LINE_BREAK? INDENT? LINE_BREAK* DEDENT?
    ;

// Условный оператор
ifStmt
    : 'if' '(' expr ')'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
      ('else'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
      )?
    ;

// Цикл while
whileStmt
    : 'while' '(' expr ')'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
    ;

// Цикл for
forStmt
    : 'for' '(' forInit? ';' forCond? ';' forIter? ')'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
    ;

// Инициализация for
forInit
    : type? ID ('=' expr)? (',' ID ('=' expr)? )*
    ;

// Условие for
forCond
    : expr
    ;

// Итерация for
forIter
    : ID (INC | DEC)
    | ID '=' expr
    ;

// Вызов функции
funcCall
    : ID '(' argList? ')'
    ;

// Список аргументов
argList
    : expr (',' expr)*
    ;

// Выражения (в порядке убывания приоритета)
expr
    : expr OR expr
    | expr AND expr
    | expr EQ expr
    | expr NEQ expr
    | expr LT expr
    | expr LE expr
    | expr GT expr
    | expr GE expr
    | expr PLUS expr
    | expr MINUS expr
    | expr MUL expr
    | expr DIV expr
    | expr MOD expr
    | prefixExpr
    | postfixExpr
    | primary
    ;

// Префиксные операции
prefixExpr
    : (INC | DEC | NOT) expr
    ;

// Постфиксные операции
postfixExpr
    : primary (INC | DEC)
    ;

// Базовые выражения
primary
    : '(' expr ')'                        # parensExpr
    | '(' type ')' expr                   # castExpr
    | funcCall                            # funcCallPrimary
    | setLiteral                          # setLiteralPrimary
    | elementLiteral                      # elementLiteralPrimary
    | literal                             # literalPrimary
    | ID indexSuffix*                     # idWithIndex
    ;

// Суффикс индекса
indexSuffix
    : '[' expr ']'
    ;

// Литерал множества
setLiteral
    : 'set' '[' exprList? ']'
    ;

// Литерал элемента
elementLiteral
    : 'element' '(' expr ')'
    ;

// Литералы
literal
    : INT
    | STRING
    | BOOLEAN
    | FLOAT
    ;

// Типы
type
    : 'int'
    | 'float'
    | 'double'
    | 'char'
    | 'str'
    | 'bool'
    | 'element'
    | 'set'
    | 'void'
    ;

// Лексер
MUL : '*';
DIV : '/';
MOD : '%';
PLUS: '+';
MINUS: '-';
LT  : '<';
GT  : '>';
LE  : '<=';
GE  : '>=';
EQ  : '==';
NEQ : '!=';
AND : '&&';
OR  : '||';
NOT : '!';
INC : '++';
DEC : '--';
PLUS_ASSIGN : '+=';
MINUS_ASSIGN : '-=';
MUL_ASSIGN : '*=';
DIV_ASSIGN : '/=';

BOOLEAN : 'true' | 'false';
INT     : [0-9]+;
FLOAT   : [0-9]+'.'[0-9]+;
STRING  : '"' ( ~["\\] | '\\' . )* '"';
ID      : [a-zA-Z_][a-zA-Z0-9_]*;

// Пробелы и комментарии
WS          : [ \t]+ -> channel(HIDDEN);
LINE_COMMENT: '//' ~[\r\n]* -> skip;
NEWLINE     : ('\r'? '\n')+ -> channel(HIDDEN);

// Специальные токены для отступов (Python-подобный синтаксис)
INDENT      : специальная обработка отступов;
DEDENT      : специальная обработка отступов;
LINE_BREAK : специальная обработка переносов строк;
```

## Описание разработанных компонентов:

#### Классы

1. **`SemanticAnalyzer`** - класс выполняет семантический анализ программы на основе дерева, построенного парсером. Проверяет типы, области видимости, корректность вызовов функций, наличие return в функциях с возвращаемым значением.

2. **`ILCodeGenerator`** - класс отвечает за трансляцию дерева разбора в целевой код (IL - Intermediate Language для .NET). Генерирует IL код для всех конструкций языка.

3. **`VerboseErrorListener`** - класс обрабатывает синтаксические ошибки, генерируемые парсером ANTLR. Форматирует сообщения об ошибках с указанием строки и позиции.

4. **`langVisitor`** - базовый класс-визитор, сгенерированный ANTLR для обхода дерева разбора.

5. **`langParser`** - парсер, сгенерированный ANTLR на основе грамматики `lang.g4`.

6. **`langLexer`** - лексер, сгенерированный ANTLR. Поддерживает Python-подобные отступы через специальную обработку INDENT/DEDENT токенов.

#### Основные методы

**SemanticAnalyzer:**
- `visitProgram` - обход программы, сбор функций и проверка
- `visitFunctionDef` - проверка объявления функций, параметров, наличия return
- `visitVarDecl` - проверка объявления переменных
- `visitAssignment` - проверка присваиваний и совместимости типов
- `visitFuncCall` - проверка вызовов функций
- `infer_type` - вывод типов выражений
- `visitIfStmt`, `visitWhileStmt`, `visitForStmt` - проверка условий в управляющих конструкциях

**ILCodeGenerator:**
- `visitProgram` - генерация заголовка программы и всех функций
- `visitFunctionDef` - генерация IL кода для функций
- `visitVarDecl` - генерация объявлений переменных
- `visitAssignment` - генерация присваиваний
- `visitFuncCall` - генерация вызовов функций
- `visitIfStmt`, `visitWhileStmt`, `visitForStmt` - генерация управляющих конструкций
- `type_to_il` - преобразование типов языка в IL типы
- `emit_method_header`, `emit_method_end` - генерация заголовка и конца метода

#### Остальные файлы

1. **`main.py`** - точка входа программы. Осуществляет запуск компилятора (лексический анализ -> синтаксический анализ -> семантический анализ -> кодогенерация).

2. **`lang.g4`** - грамматика языка в формате ANTLR. Определяет синтаксис языка с поддержкой Python-подобных отступов.

3. **`compile_and_run.sh`** - скрипт для компиляции и запуска программы. Генерирует IL код, компилирует его в .exe через ilasm и запускает.

## Перечень генерируемых ошибок

1. **Дублирование названия переменной/функции** - переменная или функция уже объявлена в текущей области видимости
2. **Несовместимость типов при присваивании** - тип выражения не совпадает с типом переменной
3. **Неправильное количество аргументов в вызове функции** - количество переданных аргументов не соответствует ни одной перегрузке функции
4. **Использование переменной вне области видимости** - переменная используется до объявления или в другой области видимости
5. **Несовместимость типов в условии** - условие в if/while/for должно быть типа boolean
6. **Несоответствие возвращаемого типа функции** - функция возвращает значение не того типа, который указан в сигнатуре
7. **Отсутствие оператора return** - функция с возвращаемым значением (не void) не содержит return
8. **Множественное присваивание с несовпадающими типами** - типы выражений справа не соответствуют типам переменных слева
9. **Вызов необъявленной функции** - функция вызывается, но не объявлена
10. **Использование имени встроенной функции/типа** - попытка использовать зарезервированное имя для переменной или функции
11. **Функция с такой сигнатурой уже объявлена** - дублирование функции с теми же параметрами
12. **Функция void возвращает значение** - функция объявлена как void, но содержит return с выражением
13. **Функция должна возвращать значение** - функция не void, но return пустой или отсутствует

## Демонстрация работы

### 1. Первый пример (example1.txt):

**Код:**
```lang
int minIndex(set numbers, int start):
    minVal = numbers[start]
    index = start
    i = start + 1
    while (i < size(numbers)):
        if (numbers[i] < minVal):
            minVal = numbers[i]
            index = i
        i++
    return index

int minIndex(set numbers):
    return minIndex(numbers, 0)

set sortSet(set numbers):
    sortedNumbers = set[]
    while (!isEmpty(numbers)):
        index = minIndex(numbers)
        add(sortedNumbers, numbers[index])
        remove(numbers, index)
    return sortedNumbers

void main():
    println("Enter numbers separated by spaces:")
    inputLine = read()
    inputs = split(inputLine, " ")
    numbers = set[]

    i = 0
    while (i < size(inputs)):
        add(numbers, toInt(inputs[i]))
        i++

    println("Original set: " + numbers)
    sortedNumbers = sortSet(numbers)
    println("Sorted set: " + sortedNumbers)
```

**Описание:** Программа демонстрирует работу с множествами (set), сортировку чисел, перегрузку функций, работу с индексами массивов, циклы while и условные операторы if.

### 2. Второй пример (example2.txt):

**Код:**
```lang
folderName = "C:/path/"
sum = 0

int countLettersInFile(str fileName, str letter):
    count = 0
    file = open(fileName)
    i = 0
    while (i != size(file)):
        currentChar = get(file, i)
        println("Index: " + i + ", Current char: " + currentChar + ", Looking for: " + letter)
        if (currentChar == letter):
            count++
            println("  -> Match! Count now: " + count)
        i++
    return count

void main():
    println("Input letter: ")
    letter = read()
    fileNamesSet = getFileNames(folderName)
    println(fileNamesSet)
    while (!isEmpty(fileNamesSet)):
        fileName = fileNamesSet[0]
        remove(fileNamesSet, 0)
        count = countLettersInFile(fileName, letter)
        sum += count

    println("total amount: " + sum)
```

**Описание:** Программа демонстрирует работу с файлами, чтение символов из файла, работу с множествами файлов, конкатенацию строк, операции инкремента и составного присваивания.

### 3. Третий пример (example3.txt):

**Код:**
```lang
bool isPrime(int n):
    if (n < 2):
        return false

    i = 2
    while (i * i <= n):
        if (n % i == 0):
            return false
        i++
    return true

void main():
    println("Input upper bound: ")
    limit = toInt(read())

    println("Prime numbers up to " + limit + ":")
    for (num = 0; num <= limit; num++):
        if (isPrime(num)):
            println(num)
```

**Описание:** Программа демонстрирует проверку простых чисел, работу с циклом for, логические операции, арифметические операции (включая остаток от деления), преобразование типов.

### 4. Четвертый пример (example4.txt):

**Код:**
```lang
int factorial(int n):
    if (n <= 1):
        return 1
    return n * factorial(n - 1)

void main():
    println("Введите число:")
    n = toInt(read())
    println("Факториал " + n + " = " + factorial(n))
```

**Описание:** Программа демонстрирует рекурсивные вызовы функций, вычисление факториала, работу с условными операторами.

### 5. Пятый пример (example5.txt):

**Код:**
```lang
set unique(set numbers):
    result = set[]

    i = 0
    while (i < size(numbers)):
        value = numbers[i]

        // проверяем, есть ли уже value в result
        found = false
        j = 0
        while (j < size(result)):
            if (result[j] == value):
                found = true
            j++

        if (!found):
            add(result, value)

        i++

    return result


void main():
    println("Введите числа через пробел:")
    inputLine = read()
    inputs = split(inputLine, " ")

    numbers = set[]
    i = 0
    while (i < size(inputs)):
        add(numbers, toInt(inputs[i]))
        i++

    println("Исходный set: " + numbers)
    uniqueNumbers = unique(numbers)
    println("Уникальные числа: " + uniqueNumbers)
```

**Описание:** Программа демонстрирует поиск уникальных элементов в множестве, вложенные циклы, работу с логическими переменными, операции сравнения.

## Особенности реализации

1. **Python-подобный синтаксис** - язык использует отступы вместо фигурных скобок для обозначения блоков кода
2. **Неявная типизация** - переменные могут объявляться без указания типа, тип выводится из выражения
3. **Перегрузка функций** - поддержка нескольких функций с одним именем, но разными параметрами
4. **Работа с множествами** - встроенная поддержка типа `set` с операциями добавления, удаления, доступа по индексу
5. **Генерация IL кода** - компилятор генерирует Intermediate Language для .NET, который затем компилируется в исполняемый файл
6. **Семантический анализ** - проверка типов, областей видимости, корректности вызовов функций на этапе компиляции


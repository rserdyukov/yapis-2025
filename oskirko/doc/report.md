# Отчет

ФИО: Оскирко Дмитрий Анатольевич\
Группа: 221703\
Вариант: 11

## Спецификация разработанного языка программирования
#### Синтаксис объявления переменных:

1. Без присваивания: `<TYPE> <VAR_NAME>;`
2. С присваиванием: `<TYPE> <VAR_NAME> = <EXPRESSION>`

#### Синтаксис объявления подпрограмм:

1. Функции:
```
function <FUNCTION_NAME> (
    <PARAM_TYPE_1> <PARAM_NAME_1>, ..., <PARAM_TYPE_N> <PARAM_NAME_N>, 
    <RESULT_PARAM_TYPE_1> ?<RESULT_PARAM_NAME_1>, ... <RESULT_PARAM_TYPE_N> ?<RESULT_PARAM_NAME_N>
) {
    <FUNCTION_BODY>
}
```

2. Lambda-функции
```
lambda (
    <PARAM_TYPE_1> <PARAM_NAME_1>, ..., <PARAM_TYPE_N> <PARAM_NAME_N>, 
    <RESULT_PARAM_TYPE_1> ?<RESULT_PARAM_NAME_1>, ... <RESULT_PARAM_TYPE_N> ?<RESULT_PARAM_NAME_N>,
    external <CLOSURE_VARIABLE_NAME_1>, ..., external <CLOSURE_VARIABLE_NAME_N>
) -> {
    <LAMBDA_FUNCTION_BODY>
}
```

#### Синтаксис управляющих конструкций:

1. for-statement:
```
for (<INIT_STATEMENT>; <CONDITION_STATEMENT>; <UPDATE_STATEMENT>) {
    <FOR_BODY>
}
```

2. while-statement:
```
while (<CONDITION_STATEMENT>) {
    <WHILE_BODY>
}
```

3. if-else-statement:
```
if (<IF_CONDITION>) {
    <IF_BODY>
} else {
    <ELSE_BODY>
}
```

4. switch-statement:
```
switch (<SWITCH_PARAMETER>) {
    case <CASE_PARAMETER_1> {
        <CASE_BODY>
    }
    
    case <CASE_PARAMETER_2> {
        <CASE_BODY>
    }
    
    ...
    
    case <CASE_PARAMETER_N> {
        <CASE_BODY>
    }
    
    default {
        <DEFAULT_BODY>
    }
}
```

#### Синтаксис операций над данными:
1. Сложение: `<EXPR> + <EXPR>`
2. Вычитание: `<EXPR> - <EXPR>`
3. Деление: `<EXPR> / <EXPR>`
4. Возведение в степень: `pow(<BASE>, <POWER>, <RESULT_PARAM>)`
5. Нахождение синуса: `sin(<ANGLE_IN_DIGREES>, <RESULT_PARAM>)`
6. Нахождение косинуса: `cos(<ANGLE_IN_DIGREES>, <RESULT_PARAM>)`
7. Нахождение логарифма: `log(<BASE>, <ARG>, <RESULT_PARAM>)`
8. Операция вывода на экран: `out(<EXPR>)`
9. Операция ввода с клавиатуры: `in(<MESSAGE>, <RESULT_PARAM>)`
10. Операция получения значения из массива по индексу: `<ARRAY_NAME>[<INDEX>]`
11. Логические операции:
    1. Логическое ИЛИ: `<EXPR> || <EXPR>`
    2. Логическое И: `<EXPR> && <EXPR>`
    3. Логическое НЕ: `!<EXPR>`
12. Операции сравнения: 
    1. Больше: `<EXPR> > <EXPR>`
    2. Больше или равно: `<EXPR> >= <EXPR>`
    3. Меньше: `<EXPR> < <EXPR>`
    4. Меньше или равно: `<EXPR> <= <EXPR>`
    5. Равно: `<EXPR> == <EXPR>`
    6. Не равно: `<EXPR> != <EXPR>`

## Описание грамматики
```
grammar grammarPL;

program
    : functionDeclarationPart statement* EOF
    ;

// -----------------------------------------------
// БАЗОВЫЕ ПРАВИЛА ПАРСЕРА
// -----------------------------------------------

// Правило для типа объявляемой переменной
declarationType
    : baseType
    ;

// Правило для базового типа
baseType
    : TYPE_INTEGER
    | TYPE_FLOAT
    | TYPE_FUNCTION
    ;

// Правило для типа объявляемого массива
declarationArrayType
    : baseType LSQBRACKET expr RSQBRACKET
    ;

// Правило для элемента массива
arrayIndex
    : ID LSQBRACKET expr RSQBRACKET
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ФУНКЦИЙ
// -----------------------------------------------

// Правило для представления lambda-функции
lambdaFunctionDeclaration
    : LAMBDA LRBRACKET declarationLambdaParamList? RRBRACKET ARROW block
    ;

// Правило для представляения параметров для lambda-функции
declarationLambdaParamList
    : declarationLambdaParam (COMMA declarationLambdaParam)* (COMMA declarationLambdaResultParam)* (COMMA declarationClosureParam)*
    ;

// Правило для параметра lambda-функции
declarationLambdaParam
    : paramType ID
    ;

// Правило для параметра lambda-функции
declarationArrayLambdaParam
    : paramArrayType ID
    ;

// Правило для результирующего параметра lambda-функции
declarationLambdaResultParam
    : paramType QUESTION ID
    ;

// Правило для результирующего параметра функции
declarationClosureParam
    : EXTERNAL ID
    ;

// Правило для части кода для объявления функции
functionDeclarationPart
    : functionDeclaration*
    ;

// Правило для объявления функции
functionDeclaration
    : FUNCTION ID LRBRACKET declarationFunctionParamList? RRBRACKET block
    ;

// Правило для типа параметра в функции
paramType
    : baseType
    ;

// Правило для типа объявляемого массива в функции
paramArrayType
    : baseType '[]'
    ;

// Правило для параметра функции
declarationFunctionParam
    : paramType ID
    ;

// Правило для параметра функции
declarationArrayFunctionParam
    : paramArrayType ID
    ;

// Правилол для результирующего параметра функции
declarationFunctionResultParam
    : paramType QUESTION ID
    ;

// Правило для параметров функции
declarationFunctionParamList
    : declarationFunctionParam (COMMA declarationFunctionParam)* (COMMA declarationFunctionResultParam)*
    ;

// Правило для списка аргументов для вызова функции
argList
    : functionArg (COMMA functionArg)*
    ;

// Правило для выхова функции
functionCall
    : ID LRBRACKET argList? RRBRACKET
    ;

functionArg
    : functionArgExpr
    ;

// Правило для аргумента функции
functionArgExpr
    : NOT? functionArgPrimary
    | LRBRACKET functionArgExpr RRBRACKET
    | functionArgExpr (MULT | DIV | REMDIV) functionArgExpr
    | functionArgExpr (PLUS | MINUS) functionArgExpr
    | functionArgExpr (EQ | NEQ | LT | LE | GT | GE) functionArgExpr
    | functionArgExpr AND functionArgExpr
    | functionArgExpr OR functionArgExpr
    | lambdaFunctionDeclaration
    ;

// Правило для примитивного элемента в аргументе функции
functionArgPrimary
    : INT
    | FLOAT
    | STRING
    | ID
    | arrayIndex
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ВЫРАЖЕНИЙ (ОТ БОЛЬШЕГО ПРИОРИТЕТА К МЕНЬШЕМУ)
// -----------------------------------------------

expr
    : NOT? primary
    | LRBRACKET expr RRBRACKET
    | expr (MULT | DIV | REMDIV) expr
    | expr (PLUS | MINUS) expr
    | expr (EQ | NEQ | LT | LE | GT | GE) expr
    | expr AND expr
    | expr OR expr
    | lambdaFunctionDeclaration
    ;

primary
    : INT
    | FLOAT
    | STRING
    | ID
    | arrayIndex
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ИНСТРУКЦИЙ
// -----------------------------------------------

// Правило для интсрукции с выражением
exprStatement
    : expr SEMICOLON
    ;

// Правило для инструкции с объявлением переменной
varDeclarationStatement
    : declarationType ID (ASSIGN expr)? SEMICOLON
    ;

// Правило для объявления массива
arrayDeclarationStatement
    : declarationArrayType ID SEMICOLON
    ;

// Правило для объявления переменной
varDeclarationWithoutSemicolon
    : declarationType ID (ASSIGN expr)?
    ;

// Правило для инструкции с присвоением переменной значения
assignmentStatement
    : (arrayIndexAccess | ID) ASSIGN expr SEMICOLON
    ;

// Правило для получения элемента массива по индексу
arrayIndexAccess
    : ID LSQBRACKET expr RSQBRACKET
    ;

// Правило для инструкции с присвоением переменной значения
assignmentStatementWithoutSemicolon
    : (ID LSQBRACKET expr RSQBRACKET | ID) ASSIGN expr
    ;

// Правило для инстуркции условного оператора
ifStatement
    : ifBlock elseBlock?
    ;

// Правило для сигнатуры конструкции if
ifSignature
    : IF LRBRACKET expr RRBRACKET
    ;

// Правило для сигнатуры конструкции if
ifBlock
    : ifSignature block
    ;

// Правило для блока else
elseBlock
    : ELSE block
    ;

// Правило для инструкции оператора for
forStatement
    : FOR LRBRACKET forInit? SEMICOLON forCondition? SEMICOLON forUpdate? RRBRACKET block
    ;

// Правило для инициализации оператора for
forInit
    : varDeclarationWithoutSemicolon
    | expr
    ;

// Правило для условия оператора for
forCondition
    : expr
    ;

// Правило для обновления оператора for
forUpdate
    : (assignmentStatementWithoutSemicolon|expr) (COMMA (assignmentStatementWithoutSemicolon|expr))*
    ;

// Правило для инструкции switch
switchStatement
    : SWITCH LRBRACKET switchExpression RRBRACKET LFIGBRACKET caseBlock* defaultBlock? RFIGRACKET
    ;

// Правило для условного цикла
whileStatement
    : WHILE LRBRACKET whileCondition RRBRACKET block
    ;

// Правило для конструкции while
whileCondition
    : expr
    ;

// Правило для выражения в switch
switchExpression
    : expr
    ;

// Правило для вызова функции
functionCallStatement
    : functionCall SEMICOLON
    ;

// Правило для инструкции
statement
    : varDeclarationStatement
    | arrayDeclarationStatement
    | assignmentStatement
    | ifStatement
    | forStatement
    | switchStatement
    | exprStatement
    | whileStatement
    | functionCallStatement
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ БЛОКОВ
// -----------------------------------------------

// Правило для блока case
caseBlock
    : CASE caseExpr block
    ;

// Правило для выражения блока case
caseExpr
    : expr
    ;

// Правило для блока default
defaultBlock
    : DEFAULT block
    ;

// Правило для блока кода
block
    : LFIGBRACKET statement* RFIGRACKET
    ;

// -----------------------------------------------
// ПРАВИЛА ЛЕКСЕРА
// -----------------------------------------------

FUNCTION: 'function' ;
LAMBDA: 'lambda' ;
ARROW: '->' ;
EXTERNAL: 'external' ;
TYPE_INTEGER: 'integer' ;
TYPE_FLOAT: 'float' ;
TYPE_STRING: 'string' ;
TYPE_BOOLEAN: 'boolean' ;
TYPE_FUNCTION: 'func' ;
IF: 'if' ;
ELSE: 'else' ;
FOR: 'for' ;
WHILE: 'while' ;
SWITCH: 'switch' ;
CASE: 'case' ;
TRUE: 'true' ;
FALSE: 'false' ;
DEFAULT: 'default' ;

ID: [a-zA-Z][a-zA-Z0-9$_]* ;

INT: [0-9]+ ;
FLOAT: [0-9]*'.'[0-9]+ ;
STRING: '"' (~["\\\r\n] | '\\' .)* '"' ;
BOOLEAN: (TRUE|FALSE) ;

QUESTION: '?' ;
LT: '<' ;
GT: '>';
LE: '<=' ;
GE: '>=' ;
EQ: '==' ;
NEQ: '!=' ;
AND: '&&' ;
OR: '||' ;
NOT: '!' ;
LSQBRACKET: '[' ;
RSQBRACKET: ']' ;
LRBRACKET: '(' ;
RRBRACKET: ')' ;
LFIGBRACKET: '{' ;
RFIGRACKET: '}' ;
SEMICOLON: ';' ;
COMMA: ',' ;
ASSIGN: '=' ;
REMDIV: '%' ;
DIV: '/' ;
PLUS: '+' ;
MINUS: '-' ;
MULT: '*' ;

WS: [ \t\r\n]+ -> skip ;
COMMENT: '#' ~[\r\n]* -> skip ;
```

## Описание разработанных классов
1. Класс для семантического анализа `SemanticAnalyzeListener`. Класс произовдит семантический анализ поданного на вход исходного кода.
2. Класс для перевода в целевой код `ConvertListener`. Класс производит перевод исходного кода в целевой.
3. Класс для обработки синтаксических ошибок `ErrorListener`. Класс обрабатывает синтаксические ошибки исходного кода.
4. Класс для предстваления ошибок `Error`. Класс хранит информацию об ошибке исходного кода (синтаксическая / семантическая).
5. Класс для предстваления выражения `Expression`. Класс хранит информацию о выражении из исходного кода.
6. Класс для представления переменной `Variable`. Класс хранит информацию о переменной из исходного кода.
7. Класс (интерфейс) для предствления типизированного значения `Typed`. Интерфейс хранит функции для анализа типизации структуры (выражения / переменные).
8. Класс (перечисление) для типа ошибки `ErrorType`. Перечисление хранит все возможные типы ошибок.

## Перечень генерируемых ошибок
1. Синтаксические ошибки. Ошибки в синтаксисе исходного кода, проверяются с помощью грамматики.
2. Семантические ошибки. Ошибки в семантике исходного кода, проверяются с помощью класса `SemanticAnalyzeListener`.
   1. Определение переменной в текущей области видимости с уже зарезервированным именем
   2. Присваивание переменной определенного типа значения отличного типа
   3. Определение функции в текущей области видимости с уже зарезервированным именем
   4. Передача неверного числа аргументов в функцию
   5. Передача аргумента неверного типа в функцию
   6. Использование необъявленной переменной
   7. Использование необъявленной функции

## Демонстрация работы
1. Приложение для вычисления факториала:

Код:
```
function factorial(integer n, integer ?result) {
    if (n <= 1) {
        result = 1;
    } else {
        integer nextFactorial;
        factorial(n-1, nextFactorial);
        result = n * nextFactorial;
    }
}

integer input;
in("Enter a number to calculate the factorial: ", input);

integer result;

factorial(input, result);

out("Factorial of a number ");
out(input);
out(" = ");
out(result);
```

Вывод:
```
No errors found (001_example.txt)
Enter a number to calculate the factorial: 10
Factorial of a number 10 = 3628800
```

2. Приложение для вычисления числа Фибоначчи по индексу:

Код:
```
function fibonacci(integer n, integer ?result) {
    integer[n] numbers;
    numbers[0] = 0;
    numbers[1] = 1;
    
    for (integer i = 2; i < n; i = i + 1) {
        numbers[i] = numbers[i-1] + numbers[i-2];
    }

    result = numbers[n-1]; 
}

integer input;
in("Enter a number to calculate a specific number from an array of Fibonacci numbers: ", input);

integer result;

fibonacci(input, result);

out("Fibonacci number at index ");
out(input);
out(" = ");
out(result);
```

Вывод:
```
No errors found (002_example.txt)
Enter a number to calculate a specific number from an array of Fibonacci numbers: 10
Fibonacci number at index 10 = 34
```

3. Приложение для проверки областей видимости:

Код:
```
function scopeCheck() {
    integer x = 10;
    out("x before executing the loop in the function: ");
    out(x);
    newLine();

    for (integer i = 0; i <= 10; i = i + 1) {
        integer x = 5;
        out("x during the execution of a loop in a function: ");
        out(x);
        newLine();
    }

    out("x after executing the loop in the function: ");
    out(x);
    newLine();
}

integer x = 20;
out("x before the function is executed: ");
out(x);
newLine();
scopeCheck();
out("x after loop execution: ");
out(x);
newLine();
```

Вывод:
```
No errors found (004_example.txt)
x before the function is executed: 20
x before executing the loop in the function: 10
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x during the execution of a loop in a function: 5
x after executing the loop in the function: 10
x after loop execution: 20
```

3. Приложение c Lambda-функциями:

Код:
```
integer a = 10;
float b = 30.4;

func testLambda1 = lambda (integer input, integer ?output, external a) -> {
    out(input + a);
    newLine();
    output = input * a;
};

func testLambda2 = lambda (integer input, integer ?output, external a, external b) -> {
    out(a);
    newLine();
    out(b);
    newLine();
    output = input / a;
};

integer output1;
integer output2;
testLambda1(20, output1);
testLambda2(30, output2);
out(output1);
newLine();
out(output2);
```

Вывод:
```
No errors found (002_example.txt)
30
10
30.399999618530273
200
3
```
# Отчет по лабораторному практикуму 

## Спецификация языка MCL

Язык **MCL (Matrix Calculation Language)** — статически типизированный императивный язык программирования, ориентированный на математические вычисления.

**Ключевые особенности:**

* **Типизация:** Строгая статическая (`int`, `float`, `boolean`, `string`, `vector`, `matrix`). Поддержка вывода типов.
* **Структура:** Программа состоит из функций и глобальных инструкций. Поддерживаются вложенные блоки кода (отступы).
* **Функции:** Поддержка именованных функций и анонимных `lambda`-выражений.
* **Встроенные операции:** Арифметика скаляров, векторов и матриц, логические операторы (`and`, `or`, `not`), условные операторы (`if-else`, тернарный оператор), циклы (`while`, `until`, `for`).


Можно ознакомиться по [ссылке](DOCS.md)

## Файл грамматики

```MCL.g4
grammar MCL;


//===================================================
//------------PARSER RULES-----------------
//===================================================

program: NL* (functionDefinition | NL)* (statement | NL)* EOF;

suite: NL INDENT (NL* statement NL*)+ DEDENT; //блок кода


functionDefinition:
    FUNC IDENTIFIER LPAREN parameterList? RPAREN ARROW type COLON suite NL*;

parameterList: parameter (COMMA parameter)*;
parameter: IDENTIFIER COLON type;


type:
    scalarType
    | VECTOR_TYPE
    | MATRIX_TYPE
    | TUPLE_TYPE
    | BOOLEAN_TYPE
    | STRING_TYPE
    | VOID_TYPE;

scalarType: INT_TYPE | FLOAT_TYPE;


statement:
     assignment
    | functionCall
    | ifStatement
    | whileStatement
    | untilStatement
    | forStatement
    | returnStatement
    ;

assignment: (type QMARK)? assignable ASSIGN expression;

assignable:
    IDENTIFIER # assignableIdentifier
    | assignable LBRACK expression RBRACK # assignableElementAccess
    ;

functionCall: IDENTIFIER LPAREN argumentList? RPAREN;
argumentList: expression (COMMA expression)*;

ifStatement:
    IF expression COLON suite (ELSE COLON suite)?;

whileStatement: WHILE expression COLON suite;
untilStatement: UNTIL expression COLON suite;
forStatement: FOR IDENTIFIER IN expression COLON suite;

returnStatement: RETURN expression?;


// операторы описываются в порядке своего приоритета
expression:
    <assoc=right> expression IF expression ELSE expression # ternaryExpression
    | logicalOrExpression                                  # logicalOrExpr
    ;

logicalOrExpression:
    logicalAndExpression (OR logicalAndExpression)*;

logicalAndExpression:
    equalityExpression (AND equalityExpression)*;

equalityExpression:
    relationalExpression ((EQ | NEQ) relationalExpression)*;

relationalExpression:
    additiveExpression ((GT | LT | GTE | LTE) additiveExpression)*;

additiveExpression:
    multiplicativeExpression ((PLUS | MINUS) multiplicativeExpression)*;

multiplicativeExpression:
    unaryExpression ((MUL | DIV | MOD) unaryExpression)*;

unaryExpression:
    (PLUS | MINUS) unaryExpression # unaryMinusPlus
    | NOT unaryExpression            # unaryNot
    | powerExpression                # powerExpr
    ;

powerExpression:
    <assoc=right> primary (POW unaryExpression)?;


primary:
    LPAREN type RPAREN primary # typeCast
    | literal # literalExpr
    | IDENTIFIER # identifierExpr
    | LPAREN expression RPAREN # parenthesizedExpr
    | VBAR expression VBAR # normOrDeterminantExpr
    | functionCall # functionCallExpr
    | creator # creatorExpr
    | vectorLiteral # vectorLiteralExpr
    | matrixLiteral # matrixLiteralExpr
    | assignable # assignableExpr
    ;


literal:
    INTEGER
    | FLOAT
    | STRING
    | TRUE
    | FALSE
    | NAN
    | INFINITY
    ;

vectorLiteral: LBRACE expressionList? RBRACE;

matrixLiteral: LBRACE vectorLiteral (COMMA vectorLiteral)* RBRACE;

expressionList: expression (COMMA expression)*;

creator:
    // [size] или [rows][cols]
    LBRACK expression RBRACK (LBRACK expression RBRACK)?
    // Опциональный инициализатор: (value) или (lambda)
    (LPAREN (expression | lambdaExpression) RPAREN)?;

lambdaExpression:
    LAMBDA (IDENTIFIER (COMMA IDENTIFIER)*)? COLON expression;


    //===================================================
    //------------LEXER RULES-----------------
    //===================================================

    IF: 'if';
    ELSE: 'else';
    WHILE: 'while';
    UNTIL: 'until';
    FOR: 'for';
    IN: 'in';

    FUNC: 'func';
    RETURN: 'return';
    VOID_TYPE: 'void';

    LAMBDA: 'lambda';

    AND: 'and';
    OR: 'or';
    NOT: 'not';
    TRUE: 'true';
    FALSE: 'false';

    INT_TYPE: 'int';
    FLOAT_TYPE: 'float';
    VECTOR_TYPE: 'vector';
    MATRIX_TYPE: 'matrix';
    TUPLE_TYPE: 'tuple';
    BOOLEAN_TYPE: 'boolean';
    STRING_TYPE: 'string';

    NAN: 'NaN';
    INFINITY: 'Infinity';

    FLOAT: (DIGIT+ '.' DIGIT*) | ('.' DIGIT+);

    INTEGER: DIGIT+;

    STRING: '"' ( ~["\r\n] )*? '"';

    PLUS: '+';
    MINUS: '-';
    MUL: '*';
    DIV: '/';
    POW: '^';
    MOD: '%';

    EQ: '==';
    NEQ: '!=';
    GT: '>';
    LT: '<';
    GTE: '>=';
    LTE: '<=';

    ASSIGN: '=';
    LPAREN: '(';
    RPAREN: ')';
    LBRACE: '{';
    RBRACE: '}';
    LBRACK: '[';
    RBRACK: ']';
    VBAR: '|';
    COMMA: ',';
    COLON: ':';
    ARROW: '->';
    QMARK: '?';


    IDENTIFIER: [a-zA-Z_] [a-zA-Z0-9_]*;

    COMMENT: '#' ~[\r\n]* -> skip;

    WS: [ \t]+;

    NL: ( '\r'? '\n' | '\r' );

    INDENT: 'indent';
    DEDENT: 'dedent';

    fragment DIGIT: [0-9];

```

### Описание разработанных классов
#### Синтаксический анализатор
Модуль отвечает за преобразование исходного текста в дерево разбора (Parse Tree) с учетом отступов.

* **`MclSyntaxAnalyzer`**: Точка входа в этап парсинга. Инициализирует лексер и парсер, регистрирует слушатели ошибок и возвращает результат анализа.
* **`IndentHandlingLexer`**: Расширение стандартного лексера ANTLR. Реализует логику Python-подобных отступов: использует стек для отслеживания уровня вложенности и генерирует виртуальные токены `INDENT` и `DEDENT` на основе анализа пробельных символов.
* **`SyntaxErrorListener`**: Накапливает синтаксические ошибки (неверные токены, нарушение структуры грамматики, ошибки отступов) для последующего вывода.

#### Семантический анализатор
Модуль выполняет проверку типов, областей видимости и корректности использования конструкций языка.

* **`MclSemanticAnalyzer`**: Оркестратор семантического анализа. Запускает обход дерева (Walker) с использованием `SemanticErrorListener`.
* **`AnalysisContext`**: Контейнер состояния анализа. Хранит `ScopeManager` (таблицу символов), карты вычисленных типов выражений и список обнаруженных ошибок. Также отслеживает контекст текущей функции (для проверки `return`).
* **`ScopeManager` & `Scope**`: Реализуют управление областями видимости (стек scopes). Позволяют определять переменные/функции и искать их (lookup) с учетом вложенности блоков.
* **Handlers (`FunctionHandler`, `StatementHandler` и др.)**: Разделяют логику проверки по типам узлов (обработка определений функций, проверка типов в выражениях, валидация циклов и присваиваний).

#### Компилятор в байт-код Python (.pyc)
Реализует генерацию исполняемого кода в два этапа: трансляция в промежуточный ассемблер и сборка бинарного файла.

* **`MclCompiler`**: Главный класс приложения. Управляет всем конвейером: чтение файла -> парсинг -> семантический анализ -> генерация ассемблера -> вызов внешнего сборщика.
* **`MclAsmGenerator`**: Реализован на основе паттерна **Visitor**. Обходит AST и генерирует текстовое представление инструкций стековой машины Python (промежуточный код `.pyasm`). Управляет созданием объектов кода (Code Objects) для функций и лямбд.
* **`assembler.py`**: Вспомогательный скрипт на Python. Читает сгенерированный `.pyasm`, использует библиотеку `bytecode` для расчета смещений и стека, и сериализует результат в валидный бинарный формат `.pyc` (с "магическими числами" и заголовками).

### Перечень генерируемых ошибок

Компилятор диагностирует и выводит следующие классы ошибок:

1. **Синтаксические ошибки:**
* `Invalid indentation`: нарушение правил вложенности блоков.
* `Mismatched input / Extraneous input`: несоответствие кода грамматике (пропущенные скобки, неверные ключевые слова).


2. **Семантические ошибки:**
* **Ошибки типов (`Type Mismatch`):** Попытка присвоить `float` в `int`, использование не-boolean выражений в условиях `if/while`, некорректные операции (например, сложение строк).
* **Ошибки областей видимости (`Undeclared Variable`):** Использование переменных, которые не были объявлены в текущей или родительской области.
* **Ошибки функций:**
* Перегрузка функций (не поддерживается для пользовательских функций).
* Несоответствие сигнатуре (неверное количество или типы аргументов).
* Отсутствие `return` в non-void функции или возврат значения из void-функции.


* **Ошибки инициализации:** Некорректные литералы векторов/матриц (смешивание типов элементов).




## Примеры работы

Листинг вывода компилятора в терминал. Тестирование системы проводилось на тестовых примерах из examples/

```
$ ./mcl examples/
Found 11 file(s) to compile.

>> Compiling: examples\correct_examples\lambda_and_io.mcl
   [CODEGEN] Generating assembly...
   [GENERATED] examples\correct_examples\lambda_and_io.pyasm
   [ASSEMBLER] Compiling to .pyc...
      > Successfully assembled examples\correct_examples\lambda_and_io.pyc
   [SUCCESS] Compiled successfully.

>> Compiling: examples\correct_examples\loops.mcl
   [CODEGEN] Generating assembly...
   [GENERATED] examples\correct_examples\loops.pyasm
   [ASSEMBLER] Compiling to .pyc...
      > Successfully assembled examples\correct_examples\loops.pyc
   [SUCCESS] Compiled successfully.

>> Compiling: examples\correct_examples\solve_linear_equation.mcl
   [CODEGEN] Generating assembly...
   [GENERATED] examples\correct_examples\solve_linear_equation.pyasm
   [ASSEMBLER] Compiling to .pyc...
      > Successfully assembled examples\correct_examples\solve_linear_equation.pyc
   [SUCCESS] Compiled successfully.

>> Compiling: examples\semantic_errors\err_condition.mcl
   [FAILED] Semantic Errors:
     Semantic Error at [4:3]: If statement condition must be BOOLEAN, but got INT
     Semantic Error at [10:6]: While loop condition must be BOOLEAN, but got VECTOR
     Semantic Error at [16:6]: Until loop condition must be BOOLEAN, but got STRING
     Semantic Error at [22:10]: Ternary condition must be BOOLEAN, but got FLOAT
     Semantic Error at [26:7]: Logical 'not' expects BOOLEAN, but got INT
     Semantic Error at [31:17]: Logical operators expect BOOLEAN, but got MATRIX
     Semantic Error at [36:6]: Logical operators expect BOOLEAN, but got VECTOR

>> Compiling: examples\semantic_errors\err_func_call.mcl
   [FAILED] Semantic Errors:
     Semantic Error at [3:4]: No overload for function 'zeros' takes 3 arguments with provided types.
     Semantic Error at [7:16]: Argument 1 of 'identity': expected type INT, but got FLOAT

>> Compiling: examples\semantic_errors\err_redeclaration.mcl
   [FAILED] Semantic Errors:
     Semantic Error at [6:5]: Function 'my_func' is already defined. User function overloading is not allowed.
     Semantic Error at [11:5]: Function 'write' is already defined. User function overloading is not allowed.

>> Compiling: examples\semantic_errors\err_return_type.mcl
   [FAILED] Semantic Errors:
     Semantic Error at [3:5]: Function 'get_int' must return a value of type INT
     Semantic Error at [9:4]: Void function 'do_nothing' cannot return a value.
     Semantic Error at [14:4]: Return type mismatch: function 'get_float' expects FLOAT, but got STRING

>> Compiling: examples\semantic_errors\err_type_mismatch.mcl
   [FAILED] Semantic Errors:
     Semantic Error at [3:9]: Type mismatch: cannot assign FLOAT to INT.
     Semantic Error at [8:9]: Type mismatch: cannot assign VECTOR to INT.

>> Compiling: examples\semantic_errors\err_undeclared.mcl
   [FAILED] Semantic Errors:
     Semantic Error at [3:4]: Undeclared variable: 'b'
     Semantic Error at [13:4]: Undeclared variable: 'local_var'

>> Compiling: examples\syntax_errors\err_bad_indents_and_punct.mcl
   [FAILED] Syntax Errors:
     Error at [1:36]: mismatched input 'b' expecting {')', ','}
     Error at [1:45]: mismatched input ')' expecting {')', ','}
     Error at [1:56]: mismatched input ':' expecting {')', ','}
     Error at [2:4]: extraneous input '<INDENT>' expecting {<EOF>, 'if', 'while', 'until', 'for', 'return', 'void', 'int', 'float', 'vector', 'matrix', 'tuple', 'boolean', 'string', IDENTIFIER, NL}
     Error at [9:8]: no viable alternative at input '\r\n<INDENT>'
     Error at [9:8]: extraneous input '<INDENT>' expecting {<EOF>, 'if', 'while', 'until', 'for', 'return', 'void', 'int', 'float', 'vector', 'matrix', 'tuple', 'boolean', 'string', IDENTIFIER, NL}
     Error at [13:2]: Invalid indentation: expected 0, but got 2
     Error at [12:40]: missing ')' at '\r\n'
     Error at [13:2]: extraneous input '<DEDENT>' expecting {<EOF>, 'if', 'while', 'until', 'for', 'return', 'void', 'int', 'float', 'vector', 'matrix', 'tuple', 'boolean', 'string', IDENTIFIER, NL}

>> Compiling: examples\syntax_errors\err_func_definition_after_statement.mcl
   [FAILED] Syntax Errors:
     Error at [6:0]: extraneous input 'func' expecting {<EOF>, 'if', 'while', 'until', 'for', 'return', 'void', 'int', 'float', 'vector', 'matrix', 'tuple', 'boolean', 'string', IDENTIFIER, NL}
     Error at [6:10]: no viable alternative at input 'x:'
     Error at [6:15]: mismatched input ',' expecting '?'
     Error at [6:23]: mismatched input ')' expecting '?'
     Error at [6:32]: mismatched input ':' expecting '?'
     Error at [7:4]: extraneous input '<INDENT>' expecting {<EOF>, 'if', 'while', 'until', 'for', 'return', 'void', 'int', 'float', 'vector', 'matrix', 'tuple', 'boolean', 'string', IDENTIFIER, NL}
     Error at [9:0]: extraneous input '<DEDENT>' expecting {<EOF>, 'if', 'while', 'until', 'for', 'return', 'void', 'int', 'float', 'vector', 'matrix', 'tuple', 'boolean', 'string', IDENTIFIER, NL}

Found 11 file(s) to compile.

```
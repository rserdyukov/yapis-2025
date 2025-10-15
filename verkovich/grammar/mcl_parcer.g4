parser grammar mcl_parcer;

options { tokenVocab = mcl_lexer; }


program: functionDefinition* statement* EOF;

// Блок кода (suite) - это то, что идет после ':' в if/for/while/func.
// Он начинается с новой строки, увеличения отступа (INDENT),
// содержит одно или несколько выражений, и заканчивается уменьшением отступа (DEDENT).
suite: NL INDENT statement+ DEDENT;


// Определение пользовательской функции
functionDefinition:
    FUNC IDENTIFIER LPAREN parameterList? RPAREN ARROW type COLON suite;

// Список параметров для функции
parameterList: parameter (COMMA parameter)*;
parameter: IDENTIFIER COLON type;

// Тип данных
type:
    scalarType
    | vectorType
    | MATRIX_TYPE
    | TUPLE_TYPE
    | BOOLEAN_TYPE
    | STRING_TYPE
    | VOID_TYPE;

scalarType: INT_TYPE | FLOAT_TYPE;
// В спецификации есть `vector<int>`, но это усложняет грамматику.
// Пока оставим простой `VECTOR_TYPE` для базовой реализации.
vectorType: VECTOR_TYPE;


// Выражение верхнего уровня. Может быть одним из перечисленных.
// Завершается новой строкой для разделения.
statement:
    ( assignment
    | functionCall // Может быть частью `assignment`, но также может быть самостоятельным
    | ifStatement
    | whileStatement
    | untilStatement
    | forStatement
    | returnStatement
    ) NL+; // Принимаем одну или несколько новых строк после выражения

// Присваивание. Может быть с явным указанием типа или без.
assignment: (type QMARK)? IDENTIFIER ASSIGN expression;

// Вызов функции (например, write(...))
functionCall: IDENTIFIER LPAREN argumentList? RPAREN;
argumentList: expression (COMMA expression)*;

// Управляющие конструкции
ifStatement:
    IF expression COLON suite (ELSE COLON suite)?; // 'else' часть опциональна

whileStatement: WHILE expression COLON suite;
untilStatement: UNTIL expression COLON suite;
forStatement: FOR IDENTIFIER IN expression COLON suite;

// Оператор return
returnStatement: RETURN expression?; // Выражение опционально (для void функций)


// Выражение (expression) - это центральная и самая сложная часть грамматики.
// Правила организованы по убыванию приоритета операторов.

expression:
    // Тернарный оператор (самый низкий приоритет)
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
    // Возведение в степень право-ассоциативно (2^3^2 == 2^(3^2))
    <assoc=right> primary (POW unaryExpression)?;


// `primary` - это "атомы" выражений, имеющие наивысший приоритет.
primary:
    // Явное преобразование типов
    LPAREN type RPAREN primary # typeCast

    // Литералы (числа, строки, и т.д.)
    | literal # literalExpr

    // Идентификаторы (переменные)
    | IDENTIFIER # identifierExpr

    // Выражение в скобках для изменения приоритета
    | LPAREN expression RPAREN # parenthesizedExpr

    // Норма вектора или определитель матрицы
    | VBAR expression VBAR # normOrDeterminantExpr

    // Вызов функции
    | functionCall # functionCallExpr

    // Конструкторы векторов и матриц
    | creator # creatorExpr

    // Литералы векторов и матриц
    | vectorLiteral # vectorLiteralExpr
    | matrixLiteral # matrixLiteralExpr

    // Доступ к элементу по индексу (постфиксная операция)
    | primary LBRACK expression RBRACK # elementAccess
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

// Литерал вектора: {1, 2, 3}
vectorLiteral: LBRACE expressionList? RBRACE;

// Литерал матрицы: {{1,2}, {3,4}}
matrixLiteral: LBRACE vectorLiteral (COMMA vectorLiteral)* RBRACE;

expressionList: expression (COMMA expression)*;

// Конструкторы для векторов и матриц
creator:
    // [size] или [rows][cols]
    LBRACK expression RBRACK (LBRACK expression RBRACK)?
    // Опциональный инициализатор: (value) или (lambda)
    (LPAREN (expression | lambdaExpression) RPAREN)?;

// Анонимная (лямбда) функция
lambdaExpression:
    LAMBDA (IDENTIFIER (COMMA IDENTIFIER)*)? COLON expression;
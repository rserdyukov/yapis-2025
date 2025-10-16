parser grammar mcl_parcer;

options { tokenVocab = mcl_lexer; }


program: NL* (functionDefinition NL | NL)* (statement NL | NL)* EOF;

suite: NL INDENT statement+ DEDENT; //блок кода


functionDefinition:
    FUNC IDENTIFIER LPAREN parameterList? RPAREN ARROW type COLON suite;

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

assignment: (type QMARK)? IDENTIFIER ASSIGN expression;

functionCall: IDENTIFIER LPAREN argumentList? RPAREN;
argumentList: expression (COMMA expression)*;

ifStatement:
    IF expression COLON suite (ELSE COLON suite)?; 

whileStatement: WHILE expression COLON suite;
untilStatement: UNTIL expression COLON suite;
forStatement: FOR IDENTIFIER IN expression COLON suite;

returnStatement: RETURN expression?; 

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
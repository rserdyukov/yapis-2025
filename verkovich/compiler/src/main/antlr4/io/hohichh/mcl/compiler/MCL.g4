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


    // Пробелы будут отдельно обрабатываться для корректной генерации виртуальных отступов
    // За счёт расширения класса лексера уже при реализации синт. анализатора
    // собственно их мы не скипаем, тк надо контролировать их количество в начале строки
    WS: [ \t]+;

    NL: ( '\r'? '\n' | '\r' );

    INDENT: 'indent';
    DEDENT: 'dedent';

    fragment DIGIT: [0-9];

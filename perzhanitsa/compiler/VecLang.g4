grammar VecLang;

/* ---------------------------
   Парсерные правила
   --------------------------- */

program: (statement | functionDecl)* EOF;

statement
    : assignment
    | expression
    | printStatement
    | writeStatement
    | readStatement
    | returnStatement
    | raiseStatement
    | ifStatement
    | whileStatement
    | forStatement
    | switchStatement
    ;

assignment
    : ('&')? ID ASSIGN expression
    ;

/* --- управляющие конструкции --- */
ifStatement
    : IF expression COLON block (ELSE  COLON block)?
    ;

whileStatement
    : WHILE expression COLON block
    ;

forStatement
    : FOR ID IN expression COLON block
    ;

switchStatement
    : SWITCH expression COLON (CASE expression COLON block)* (DEFAULT COLON block)?
    ;

block
    :  statement+   // Если хотите разрешить пустой блок — изменить на statement*
    ;

functionDecl
    : DEF ID LPAREN parameterList? RPAREN COLON block
    ;

parameterList
    : ('&'? ID) (COMMA '&'? ID)*
    ;

type
    : VECTOR
    | MATRIX
    | INT_TYPE
    | FLOAT_TYPE
    | STRING_TYPE
    ;

/* --- выражения с приоритетами --- */
expression
    : equalityExpr
    | logicalExpr
    ;

equalityExpr
    : relationalExpr ((EQ | NEQ) relationalExpr)*
    ;

relationalExpr
    : additiveExpr ((LT | GT | LE | GE) additiveExpr)*
    ;

additiveExpr
    : multiplicativeExpr ((ADD | SUB) multiplicativeExpr)*
    ;

multiplicativeExpr
    : unaryExpr ((MUL | DIV) unaryExpr)*
    ;
logicalExpr
    : equalityExpr ((AND | OR) equalityExpr)*
    ;
unaryExpr
    : SUB unaryExpr
    | PIPE expression PIPE
    | postfixExpr
    ;

/* Постфиксные выражения: индексация, вызов, member-access (.id) */
postfixExpr
    : primary ( (DOT ID) | LBRACK expression RBRACK | LPAREN argumentList? RPAREN )*
    ;

primary
    : LPAREN expression RPAREN
    | literal
    | ID
    | MATRIX
    | VECTOR
    | MATRIX LPAREN argumentList? RPAREN   // matrix(...)
    | VECTOR LPAREN argumentList? RPAREN   // vector(...)
    ;

/* Аргументы (именованные и позиционные) */
argument
    : ID ASSIGN expression   // named argument
    | expression             // positional argument
    ;

argumentList
    : argument (COMMA argument)*
    ;

/* --- литералы --- */
literal
    : INT
    | FLOAT
    | STRING
    | vectorLiteral
    | matrixLiteral
    | TRUE
    | FALSE
    ;

vectorLiteral
    : LPAREN expression (COMMA expression)+ RPAREN
    ;

/* Матрица: [[...], [...]] или [expr, expr, ...] */
matrixLiteral
    : LBRACK ( row (COMMA row)* | expression (COMMA expression)* )? RBRACK
    ;

row
    : LBRACK expression (COMMA expression)* RBRACK
    ;

/* --- дополнительные инструкции --- */
writeStatement
    : WRITE LPAREN expression RPAREN
    ;

printStatement
    : PRINT LPAREN expression RPAREN
    ;

readStatement
    : READ LPAREN RPAREN
    ;

returnStatement
    : RETURN expression?
    ;

raiseStatement
    : RAISE ID
    ;

/* ---------------------------
   Лексерные правила
   --------------------------- */

/* ключевые слова */
DEF         : 'def';
IF          : 'if';
ELSE        : 'else';
WHILE       : 'while';
UNTIL       : 'until';
FOR         : 'for';
IN          : 'in';
SWITCH      : 'switch';
CASE        : 'case';
DEFAULT     : 'default';
RETURN      : 'return';
WRITE       : 'write';
PRINT       : 'print';
READ        : 'read';
RAISE       : 'raise';

TRUE        : 'true';
FALSE       : 'false';

VECTOR      : 'vector';
MATRIX      : 'matrix';
INT_TYPE    : 'int';
FLOAT_TYPE  : 'float';
STRING_TYPE : 'string';

AUTO        : 'auto';

/* операторы */
EQ          : '==';
NEQ         : '!=';
LE          : '<=';
GE          : '>=';
LT          : '<';
GT          : '>';
AND : 'and';
OR  : 'or';

ASSIGN      : '=';
ADD         : '+';
SUB         : '-';
MUL         : '*';
DIV         : '/';

PIPE        : '|';

LPAREN      : '(';
RPAREN      : ')';
LBRACE      : '{';
RBRACE      : '}';
LBRACK      : '[';
RBRACK      : ']';

COMMA       : ',';
SEMI        : ';';
COLON       : ':';

DOT         : '.';

/* литералы */
STRING
    : '"' ( ~["\\\r\n] | '\\' . )* '"'
    ;

// FLOAT: используем более конкретный паттерн, чтобы не конфликтовать с DOT
FLOAT
    : [0-9]+ '.' [0-9]* ([eE] [+-]? [0-9]+)?
    | '.' [0-9]+ ([eE] [+-]? [0-9]+)?
    ;

/* INT после FLOAT — порядок в файле важен, FLOAT выше INT */
INT
    : [0-9]+
    ;

/* идентификаторы */
ID
    : [a-zA-Z_][a-zA-Z_0-9]*
    ;

/* пробелы и комментарии */
WS
    : [ \t\r\n]+ -> skip
    ;

COMMENT
    : '#' ~[\r\n]* -> skip
    ;

ML_COMMENT
    : '/*' .*? '*/' -> skip
    ;

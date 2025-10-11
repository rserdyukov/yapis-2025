grammar lang;

program
    : (statement | NEWLINE)* EOF
    ;

statement
    : functionDef
    | simpleStmt
    ;

functionDef
    : type ID '(' parameterList? ')' ':' NEWLINE+ statement*
    ;

parameterList
    : parameter (',' parameter)*
    ;

parameter
    : ('out')? type ID
    ;

simpleStmt
    : varDecl
    | assignment
    | funcCall
    | 'return' expr?
    | ifStmt
    | whileStmt
    | forStmt
    ;

varDecl
    : type ID (',' ID)* ('=' exprList)? NEWLINE
    | ID '=' exprList NEWLINE
    | ID NEWLINE
    ;

assignment
    : type ID (',' ID)* (('=' exprList)
         | PLUS_ASSIGN expr
         | MINUS_ASSIGN expr
         | MUL_ASSIGN expr
         | DIV_ASSIGN expr
         | INC
         | DEC)? NEWLINE
    | ID (('=' exprList)
         | PLUS_ASSIGN expr
         | MINUS_ASSIGN expr
         | MUL_ASSIGN expr
         | DIV_ASSIGN expr
         | INC
         | DEC)? NEWLINE
    ;



exprList
    : expr (',' expr)*
    ;

ifStmt
    : 'if' '(' expr ')' ':' NEWLINE+ statement*
      ('else' ':' NEWLINE+ statement*)?
    ;

whileStmt
    : 'while' '(' expr ')' ':' NEWLINE+ statement*
    ;

forStmt
    : 'for' '(' forInit? ';' forCond? ';' forIter? ')' ':' NEWLINE+ statement*
    ;

forInit
    : type? ID ('=' expr)? (',' ID ('=' expr)? )*
    ;

forCond
    : expr
    ;

forIter
    : ID (INC | DEC)
    | ID '=' expr
    ;

funcCall
    : ID '(' argList? ')'
    ;

argList
    : expr (',' expr)*
    ;

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

prefixExpr
    : (INC | DEC | NOT) expr
    ;

postfixExpr
    : primary (INC | DEC)
    ;

primary
    : '(' expr ')'                     # parensExpr
    | '(' type ')' expr                # castExpr
    | funcCall                         # funcCallPrimary
    | setLiteral                        # setLiteralPrimary
    | elementLiteral                    # elementLiteralPrimary
    | literal                           # literalPrimary
    | ID indexSuffix*                   # idWithIndex
    ;

indexSuffix
    : '[' expr ']'
    ;

setLiteral
    : 'set' '[' exprList? ']'
    ;

elementLiteral
    : 'element' '(' expr ')'
    ;

literal
    : INT
    | STRING
    | BOOLEAN
    ;

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

MUL : '*';
DIV : '/';
MOD : '%';
PLUS: '+';
MINUS: '-';
LT  : '<';
GT  : '>';
LE  : '<=' ;
GE  : '>=' ;
EQ  : '==' ;
NEQ : '!=' ;
AND : '&&' ;
OR  : '||' ;
NOT : '!' ;
INC : '++' ;
DEC : '--' ;
PLUS_ASSIGN : '+=' ;
MINUS_ASSIGN : '-=' ;
MUL_ASSIGN : '*=' ;
DIV_ASSIGN : '/=' ;

LPAREN : '(' ;
RPAREN : ')' ;
LBRACK : '[' ;
RBRACK : ']' ;
COMMA  : ',' ;

BOOLEAN : 'true' | 'false' ;
INT     : [0-9]+ ;
STRING  : '"' ( ~["\\] | '\\' . )* '"' ;
ID      : [a-zA-Z_][a-zA-Z0-9_]* ;

NEWLINE : ('\r'? '\n')+ ;
WS      : [ \t]+ -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;

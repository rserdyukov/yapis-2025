grammar Gsl;

program
    : function* EOF
    ;

function
    : head body
    ;

head
    : type ID '(' parameterList? ')'
    ;

body
    : '{' op* '}'
    ;

parameterList
    : parameter (',' parameter)*
    ;

parameter
    : ('out')? type ID
    ;

op
    : opAssign ';'
    | opReturn ';'
    | opDeclare
    | opGlobal ';'
    | opMethodCall ';'
    | opIf
    | opFor
    | opWhile
    | opUntil
    | opExpr ';'
    ;

opGlobal
    : 'global' (type ID ('=' expr)? (',' type? ID ('=' expr)?)*)
    ;

opAssign
    : leftAssign '=' exprList
    ;

exprList
    : expr (',' expr)*
    ;

opDeclare
    : leftAssign ';'
    ;

leftAssign
    : (type? ID) (',' (type? ID))*
    ;

opReturn
    : 'return' expr?
    ;

opMethodCall
    : ID '(' argList? ')'
    ;

opExpr
    : expr
    ;

opIf
    : 'if' '(' expr ')' body ( 'else' opIf )?
    | 'if' '(' expr ')' body ('else' body)?
    ;

opWhile
    : 'while' '(' expr ')' body
    ;

opUntil
    : 'until' '(' expr ')' body
    ;

opFor
    : 'for' '(' opAssign? ';' expr? ';' (opAssign | opExpr)? ')' body
    ;

argList
    : expr (',' expr)*
    ;

expr
    : expr OR expr        #orExpr
    | expr AND expr       #andExpr
    | expr EQ expr        #eqExpr
    | expr NEQ expr       #neqExpr
    | expr LT expr        #ltExpr
    | expr LE expr        #leExpr
    | expr GT expr        #gtExpr
    | expr GE expr        #geExpr
    | expr PLUS expr      #addExpr
    | expr MINUS expr     #subExpr
    | expr MUL expr       #mulExpr
    | expr DIV expr       #divExpr
    | prefixExpr          #prefixOpExpr
    | postfixExpr         #postfixOpExpr
    | primary             #primaryExpr
    ;

prefixExpr
    : (INC | DEC | NOT) expr
    ;

postfixExpr
    : primary (INC | DEC)
    ;

primary
    : '(' expr ')'                        #parensExpr
    | '(' type ')' expr                   #castExpr
    | opMethodCall                         #methodCallPrimary
    | nodeLiteral                          #nodePrimary
    | arcLiteral                           #arcPrimary
    | graphLiteral                         #graphPrimary
    | literal                              #literalPrimary
    | ID                                   #idPrimary
    ;

nodeLiteral
    : 'node' '(' expr ')'
    ;

arcLiteral
    : 'arc' '(' expr ',' expr ')'
    ;

graphLiteral
    : 'graph' '(' '[' nodeList? ']' ',' '[' arcList? ']' ')'
    | '[[' nodeList? ']' ',' '[' arcList? ']]'
    ;

nodeList
    : expr (',' expr)*
    ;

arcList
    : expr (',' expr)*
    ;

literal
    : INT
    | STRING
    | BOOLEAN
    ;

type
    : 'int'
    | 'boolean'
    | 'string'
    | 'void'
    | 'node'
    | 'graph'
    | 'arc'
    ;

MUL : '*';
DIV : '/';
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

ASSIGN : '=';

LPAREN : '(';
RPAREN : ')';
LBRACE : '{';
RBRACE : '}';
LBRACK : '[';
RBRACK : ']';
COMMA  : ',';
SEMI   : ';';

BOOLEAN : 'true' | 'false';

INT
    : [0-9]+
    ;

STRING
    : '"' ( ~["\\] | '\\' . )* '"'
    ;

ID
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

WS
    : [ \t\r\n]+ -> skip
    ;

LINE_COMMENT
    : '//' ~[\r\n]* -> skip
    ;
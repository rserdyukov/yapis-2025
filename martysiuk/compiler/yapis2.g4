grammar yapis2;

program
    : functionDecl* statement* EOF
    ;

functionDecl
    : 'func' IDENTIFIER '(' parameterList? ')' (IDENTIFIER type)? ':' block
    ;

parameterList
    : parameter (',' parameter)*
    ;

parameter
    : IDENTIFIER type
    ;

type
    : 'int'
    | 'point'
    | 'line'
    | 'circle'
    | 'polygon'
    | 'bool'
    | 'string'
    ;

block
    : statement+
    ;

statement
    : assignment
    | variableDecl
    | ifStatement
    | whileStatement
    | forStatement
    | breakStatement
    | returnStatement
    | functionCall
    ;

assignment
    : IDENTIFIER '=' expression
    ;

variableDecl
    : IDENTIFIER '=' expression
    ;

ifStatement
    : 'if' expression 'then' block ('else' block)?
    ;

whileStatement
    : 'while' expression 'do:' block
    ;

forStatement
    : 'for' IDENTIFIER '=' expression 'to' expression ('step' '=' expression)? ':' block
    ;

breakStatement
    : 'break'
    ;

returnStatement
    : 'return' expression?
    ;

functionCall
    : IDENTIFIER '(' argumentList? ')'
    | builtInFunction '(' argumentList? ')'
    ;

argumentList
    : expression (',' expression)*
    ;

expression
    : literal                                    #literalExpr
    | IDENTIFIER                                 #identifierExpr
    | functionCall                               #functionCallExpr
    | '(' expression ')'                         #parenthesizedExpr
    | '(' type ')' expression                    #castExpr
    | '!' expression                             #notExpr
    | expression op=('*' | '/' | '%') expression #multiplicativeExpr
    | expression op=('+' | '-') expression       #additiveExpr
    | expression op=('<' | '>' | '<=' | '>=' | '==' | '!=') expression #comparisonExpr
    | expression op=('&&' | '||') expression     #logicalExpr
    | expression '.' IDENTIFIER                  #memberAccessExpr
    ;

builtInFunction
    : 'read'
    | 'write'
    | 'point'
    | 'line'
    | 'circle'
    | 'polygon'
    | 'distance'
    | 'intersection'
    | 'inside'
    ;

literal
    : INT
    | STRING
    | BOOL
    ;

IDENTIFIER: [a-zA-Z_][a-zA-Z_0-9]*;

INT: [0-9]+;

BOOL: 'true' | 'false';

STRING: '"' (~["\r\n])* '"';

WS: [ \t\r\n]+ -> skip;

COMMENT: '//' ~[\r\n]* -> skip;



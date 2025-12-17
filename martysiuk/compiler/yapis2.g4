grammar yapis2;

tokens { INDENT, DEDENT }

program
    : (functionDecl | statement)* EOF
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
    | 'circle'
    ;

block
    : INDENT statement+ DEDENT
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
    : 'return' expression
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
<<<<<<< Updated upstream
    | IDENTIFIER                                #identifierExpr
    | functionCall                              #functionCallExpr
    | '(' expression ')'                        #parenthesizedExpr
    | '(' type ')' expression                   #castExpr
    | '!' expression                            #notExpr
=======
    | IDENTIFIER                                 #identifierExpr
    | functionCall                               #functionCallExpr
    | '(' expression ')'                         #parenthesizedExpr
    | '(' type ')' expression                    #castExpr
    | '!' expression                             #notExpr
    | expression '.' IDENTIFIER                  #memberAccessExpr
>>>>>>> Stashed changes
    | expression op=('*' | '/' | '%') expression #multiplicativeExpr
    | expression op=('+' | '-') expression      #additiveExpr
    | expression op=('<' | '>' | '<=' | '>=' | '==' | '!=') expression #comparisonExpr
<<<<<<< Updated upstream
    | expression op=('&&' | '||') expression    #logicalExpr
    | expression '.' IDENTIFIER                 #memberAccessExpr
=======
    | expression op=('&&' | '||') expression     #logicalExpr
>>>>>>> Stashed changes
    ;

builtInFunction
    : 'read'
    | 'write'
    | 'point'
    | 'circle'
    | 'distance'
    | 'inside'
    ;

literal
    : INT
    | STRING
    ;

IDENTIFIER: [a-zA-Z_][a-zA-Z_0-9]*;

INT: [0-9]+;

STRING: '"' (~["\r\n])* '"';

NEWLINE: ('\r'? '\n' | '\r') [ \t]*;

WS: [ \t]+ -> skip;

COMMENT: '//' ~[\r\n]* -> skip;
<<<<<<< Updated upstream
=======



>>>>>>> Stashed changes

grammar StringLang;

program
    : functionDecl* statement* EOF
    ;

functionDecl
    : type ID LPAREN paramList? RPAREN block
    ;

paramList
    : param (COMMA param)*
    ;

param
    : type ID
    ;

statement
    : varDecl
    | assignment
    | ioStmt
    | ifStmt
    | whileStmt
    | untilStmt
    | forInStmt
    | returnStmt
    | exprStmt
    | block
    ;

varDecl
    : type ID (ASSIGN expression)?
    ;

assignment
    : lvalue (COMMA lvalue)* ASSIGN expression (COMMA expression)*
    ;

lvalue
    : ID (LBRACK expression RBRACK)*
    ;

ioStmt
    : READ LPAREN RPAREN              # readCall
    | WRITE LPAREN expression RPAREN   # writeCall
    ;

ifStmt
    : IF expression THEN block (ELSE block)? END
    ;

whileStmt
    : WHILE LPAREN expression RPAREN block
    ;

untilStmt
    : UNTIL LPAREN expression RPAREN block
    ;

forInStmt
    : FOR ID IN expression block
    ;

returnStmt
    : RETURN expression?
    ;

exprStmt
    : expression
    ;

block
    : LBRACE statement* RBRACE
    ;

expression
    : inExpr
    | equality
    ;

inExpr
    : equality IN equality
    ;

equality
    : comparison ( (EQ | NEQ) comparison )*
    ;

comparison
    : addition ( (LT | GT) addition )*
    ;

addition
    : multiplication ( (PLUS | MINUS) multiplication )*
    ;

multiplication
    : unary ( (STAR | SLASH) unary )*
    ;

unary
    : MINUS unary
    | postfix
    ;

postfix
    : primary (LBRACK expression RBRACK)*
    ;

primary
    : castExpr
    | functionCall
    | builtinFunc
    | atom
    ;

builtinFunc
    : LEN LPAREN expression RPAREN
    | SUBSTR LPAREN expression COMMA expression COMMA expression RPAREN
    | REPLACE LPAREN expression COMMA expression COMMA expression RPAREN
    | SPLIT LPAREN expression COMMA expression RPAREN
    ;

castExpr
    : LPAREN type RPAREN expression
    ;

functionCall
    : ID LPAREN (expression (COMMA expression)*)? RPAREN
    ;

atom
    : INT
    | CHAR_LITERAL
    | STRING_LITERAL
    | arrayLiteral
    | ID
    | LPAREN expression RPAREN
    ;

arrayLiteral
    : LBRACK (expression (COMMA expression)*)? RBRACK
    ;

type
    : TYPE_CHAR
    | TYPE_STRING
    | TYPE_ARRAY
    | TYPE_INT
    ;

IF      : 'if' ;
THEN    : 'then' ;
ELSE    : 'else' ;
END     : 'end' ;
WHILE   : 'while' ;
UNTIL   : 'until' ;
FOR     : 'for' ;
IN      : 'in' ;
READ    : 'read' ;
WRITE   : 'write' ;
RETURN  : 'return' ;
LEN     : 'len' ;
SUBSTR  : 'substr';
REPLACE : 'replace';
SPLIT   : 'split';
TYPE_CHAR   : 'char' ;
TYPE_STRING : 'string' ;
TYPE_ARRAY  : 'array' ;
TYPE_INT    : 'int' ;

PLUS    : '+' ;
MINUS   : '-' ;
STAR    : '*' ;
SLASH   : '/' ;
EQ      : '==' ;
NEQ     : '!=' ;
LT      : '<' ;
GT      : '>' ;
ASSIGN  : '=' ;
COMMA   : ',' ;
SEMI    : ';' ;
LPAREN  : '(' ;
RPAREN  : ')' ;
LBRACK  : '[' ;
RBRACK  : ']' ;
LBRACE  : '{' ;
RBRACE  : '}' ;

ID  : [a-zA-Z_] [a-zA-Z0-9_]* ;
INT : [0-9]+ ;

CHAR_LITERAL
    : '\'' (~[\\'\r\n]) '\''
    ;

STRING_LITERAL
    : '"' ( ~["\\\r\n] | '\\' . )* '"'
    ;

WS  : [ \t\r\n]+ -> skip ;

COMMENT
    : '//' ~[\r\n]* -> skip
    ;

grammar GrammarMathPL;

program
    : (functionDefinition | statement)* EOF
    ;

functionDefinition
    : FUNC ID LPAREN functionInParameters? RPAREN ARROW functionOutType block
    ;

functionInParameters
    : type ID (COMMA type ID)*
    ;

functionArguments
    : expression (COMMA expression)*
    ;

functionOutType
    : (type | VOID)
    ;

functionCall
    : ID LPAREN functionArguments? RPAREN
    ;

block
    : LBRACE (statement)* RBRACE
    ;

statement
    : variableDeclaration
    | assignmentStatement
    | ifStatement
    | forStatement
    | whileStatement
    | returnStatement
    | functionCall SEMI
    | incDecStatement
    | arrayStatement
    ;

variableDeclaration
    : type ID (ASSIGN expression)? SEMI
    ;

assignmentStatement
    : expression (ASSIGN | PLUS_ASSIGN | MINUS_ASSIGN | MUL_ASSIGN | DIV_ASSIGN) expression SEMI
    ;

ifStatement
    : IF LPAREN expression RPAREN THEN block
      ( ELSE ifStatement
      | ELSE block
      )?
    ;

whileStatement
    : WHILE LPAREN expression RPAREN block
    ;

forStatement
    : FOR LPAREN forInitializer SEMI expression? SEMI forUpdate? RPAREN block
    ;

incDecStatement
    : expression (INC | DEC) SEMI
    | (INC | DEC) expression SEMI
    ;

forInitializer
    : type ID ASSIGN expression
    ;

forUpdate
    : ID (ASSIGN | PLUS_ASSIGN | MINUS_ASSIGN | MUL_ASSIGN | DIV_ASSIGN) expression
    | (INC | DEC) ID
    | ID (INC | DEC)
    ;

returnStatement
    : RETURN expression? SEMI
    ;

arrayStatement
    : expression DOT APPEND LPAREN expression RPAREN SEMI
    | expression DOT REVERSE LPAREN RPAREN SEMI
    ;

expression
    : atom
    | expression LBRACK expression RBRACK
    | expression LBRACK expression COLON expression RBRACK
    | expression DOT LENGTH
    | expression (INC | DEC)
    | (INC | DEC) expression
    | MINUS expression
    | NOT expression
    | expression POW expression
    | expression (MUL | DIV | MOD) expression
    | expression (PLUS | MINUS) expression
    | expression (GT | LT | GTE | LTE | EQ | NEQ) expression
    | expression AND expression
    | expression OR expression
    ;

atom
    : LPAREN expression RPAREN
    | typeCast
    | literal
    | variable
    | functionCall
    | LBRACK (expression (COMMA expression)*)? RBRACK
    | NEW type LBRACK atom RBRACK
    ;

typeCast
    : LPAREN type RPAREN atom
    ;

type
    : INT | FLOAT | BOOL | STRING
    | type LBRACK RBRACK
    ;

literal
    : INT_LITERAL | FLOAT_LITERAL | BOOL_LITERAL | STRING_LITERAL
    ;

variable
    : ID
    ;

// ------------
// LEXER RULES
// ------------

INT: 'int';
FLOAT: 'float';
BOOL: 'bool';
STRING: 'str';
VOID: 'void';

WS: [ \t\r\n]+ -> skip;
COMMENT: '#' ~[\r\n]* -> skip;

LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
COLON: ':';
DOT: '.';
SEMI: ';';
COMMA: ',';
ARROW: '->';

FUNC: 'func';
RETURN: 'return';
IF: 'if';
THEN: 'then';
ELSE: 'else';
WHILE: 'while';
FOR: 'for';
AND: 'and';
OR: 'or';
NOT: 'not';
NEW: 'new';
LENGTH: 'length';
APPEND: 'append';
REVERSE: 'reverse';

BOOL_LITERAL: TRUE | FALSE;
TRUE: 'true';
FALSE: 'false';
ID: [a-zA-Z_] [a-zA-Z_0-9]*;
INT_LITERAL: '0' | [1-9] [0-9]*;
FLOAT_LITERAL: [0-9]+ '.' [0-9]+;
STRING_LITERAL: '"' ( '\\' . | ~[\\"] )* '"';

ASSIGN: '=';
PLUS_ASSIGN: '+=';
MINUS_ASSIGN: '-=';
MUL_ASSIGN: '*=';
DIV_ASSIGN: '/=';
INC: '++';
DEC: '--';
PLUS: '+';
MINUS: '-';
MUL: '*';
DIV: '/';
MOD: '%';
POW: '^';

GT: '>';
LT: '<';
GTE: '>=';
LTE: '<=';
EQ: '==';
NEQ: '!=';
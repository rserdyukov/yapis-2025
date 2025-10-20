grammar SetLang;


program
    : statement* EOF
    ;

statement
    : variableDeclaration
    | functionDeclaration
    | functionCall
    | ifStatement
    | switchStatement
    | whileStatement
    | forStatement
    | returnStatement
    | breakStatement
    ;

variableDeclaration
    : ID ASSIGN expr
    ;

functionDeclaration
    : FUNCTION ID LRBRACKET paramList? RRBRACKET COLON block
    ;

paramList
    : ID (COMMA ID)*
    ;

ifStatement
    : IF logicalExpr COLON block (ELSE COLON block)?
    ;

switchStatement
    : SWITCH ID COLON caseBlock+ defaultblock?
    ;

caseBlock
    : CASE expr COLON block
    ;

defaultblock
    : DEFAULT COLON block
    ;
whileStatement
    : WHILE logicalExpr COLON block;

forStatement
    : FOR  ID IN range COLON block;

range: LRBRACKET (ID|INT) COMMA ((ID|INT) (COMMA (ID|INT))?)?| COMMA (ID|INT) RRBRACKET;

returnStatement: RETURN expr;

breakStatement: BREAK;

block: statement+;

expr: simpleExpr | complexExpr | functionCall | comparisonExpression| logicalExpr ;

functionCall
    : ID LRBRACKET exprList RRBRACKET
    | ID POINT LRBRACKET exprList RRBRACKET
    | ID POINT functionCall
    ;

exprList
    : expr (COMMA expr)*
    ;

logicalExpr
    : NOT? logicalOperand
    | LRBRACKET logicalExpr (AND | OR) logicalExpr RRBRACKET
    ;

comparisonExpression: LRBRACKET expr (LT | GT | LE | GE |EQUAL| NEQUAL) expr RRBRACKET;

logicalOperand
    :functionCall
    |ID
    |comparisonExpression
    |BOOL
    ;

complexExpr
    : simpleExpr
    | LRBRACKET complexExpr (PLUS | MINUS | UN | DIFF | SYMDIFF)  complexExpr RRBRACKET;

simpleExpr:
    | setLiteral
    | tupleLiteral
    | element
    | ID
    ;

setLiteral: LFIGBRACKET simpleExprList RFIGBRACKET   ;

tupleLiteral: LSQBRACKET simpleExprList RSQBRACKET;

simpleExprList: simpleExpr (COMMA simpleExpr)*;

element
    : INT
    | STRING
    | BOOL
    ;


FUNCTION: 'function' ;
IF: 'if' ;
ELSE: 'else' ;
FOR: 'for' ;
IN: 'in';
WHILE: 'while' ;
SWITCH: 'switch' ;
CASE: 'case' ;
DEFAULT: 'default';
BREAK: 'break' ;
RETURN: 'return';
TRUE: 'true' ;
FALSE: 'false' ;

ID: [a-zA-Z][a-zA-Z0-9$_]* ;

INT: [0-9]+ ;
STRING: '"' (~["\\\r\n] | '\\' .)* '"' ;
BOOL: (TRUE|FALSE) ;
QUESTION: '?' ;
LT: '<' ;
GT: '>';
LE: '<=' ;
GE: '>=' ;
EQUAL: '==' ;
NEQUAL: '!=' ;
AND: '&&' ;
OR: '||' ;
NOT: '!' ;
LSQBRACKET: '[' ;
RSQBRACKET: ']' ;
LRBRACKET: '(' ;
RRBRACKET: ')' ;
LFIGBRACKET: '{' ;
RFIGBRACKET: '}' ;
SEMICOLON: ';' ;
COLON: ':' ;
COMMA: ',' ;
POINT: '.';
ASSIGN: '=' ;
DIFF: '/' ;
SYMDIFF: '/\\' ;
PLUS: '+' ;
MINUS: '-' ;
UN: '*' ;
WS: [ \t\r\n]+ -> skip ;
COMMENT: '//' ~[\r\n]* -> skip ;
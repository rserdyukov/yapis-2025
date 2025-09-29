grammar SetLang;

program
    : statement* EOF
    ;

statement
    : variableDeclaration
    | functionDeclaration
    | functionCall
    | printStatement
    | ifStatement
    | switchStatement
    | forStatement
    | returnStatement
    | breakStatement
    | expressionStatement
    ;

variableDeclaration
    : ID '=' expressionStatement
    ;

functionDeclaration
    : 'function' ID '(' paramList? ')' ':' block
    ;

paramList
    : ID (',' ID)*
    ;

return
    : 'return' expressionStatement
    ;

functionCall
    : ID '(' argList? ')'
    ;

argList
    : expressionStatement (',' expressionStatement)*
    ;

printStatement
    : 'print(' expressionStatement ')'
    ;

ifStatement
    : 'if' logicalExpression ':' block ('else:' block)?
    ;

switchStatement
    : 'switch' ID ':' caseBlock+ defaultblock?
    ;

caseBlock
    : 'case' expression ':' block
    ;

defaultblock
    : 'default:' block
    ;

forStatement
    : 'for' (forCondition|forInit) ':' block;

forCondition:logicalExpression;

forInit: ID 'in' range;

range: '('(ID|INT)','((ID|INT) (','(ID|INT))?)?|','(ID|INT)')';

returnStatement: 'return' expressionStatement;

breakStatement: 'break';

block: statement+;

expressionStatement
    :logicalExpression
    |comparisonExpression
    |expression
    ;

logicalExpression
    : '(''!'? logicalOperand ')'
    |  '('logicalExpression ('and'|'or') logicalExpression')'
    ;

comparisonExpression: '('expression ('<' | '>' | '<=' | '>=' |'=='|'!=') expression')';

logicalOperand
    :expression ('+' | '-' | '*' | '/') expression
    |expression '.' functionCall
    |functionCall
    |expression '['(ID|INT)']'
    |ID
    |comparisonExpression
    |BOOL
    | (tupleLiteral|setLiteral|elementLiteral) 'in' (tupleLiteral|setLiteral)
    ;

expression
    : expression ('+' | '-' | '*' | '/') expression
    | expression '.' functionCall
    | expression '['(ID|INT)']'
    | functionCall
    | ID
    | tupleLiteral
    | setLiteral
    | elementLiteral
    ;

tupleLiteral: '<' (dataType (','dataType)*)? '>' ;

setLiteral: '{' (dataType (','dataType)*)? '}' ;

elementLiteral: INT|FLOAT|STRING|BOOL;

dataType:INT|FLOAT|STRING|BOOL|setLiteral|tupleLiteral|elementLiteral;

ID : [a-zA-Z_][a-zA-Z_0-9]* ;
INT : [0-9]+ ;
FLOAT: [0-9]*'.'[0-9]+ ;
STRING : '"' (~["\\\r\n] | '\\' .)* '"' ;
BOOL : 'true'|'false';
COMMENT: '//' ~[\r\n]* -> skip ;
WS : [ \t\r\n]+ -> skip ;

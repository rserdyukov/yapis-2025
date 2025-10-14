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


ifStatement
    : 'if' logicalExpression ':' block ('else:' block)?
    ;

switchStatement
    : 'switch' ID ':' caseBlock+ defaultblock?
    ;

caseBlock
    : 'case' complexExpression ':' block
    ;

defaultblock
    : 'default:' block
    ;
whileStatement
    : 'while' logicalExpression ':' block;

forStatement
    : 'for'  ID 'in' range ':' block;

range: '('(ID|INT)','((ID|INT) (','(ID|INT))?)?|','(ID|INT)')';

returnStatement: 'return' expressionStatement;

breakStatement: 'break';

block: statement+;

expressionStatement
    :logicalExpression
    |comparisonExpression
    |complexExpression
    |expression
    ;

logicalExpression
    : '('('!')? logicalOperand ')'
    |  '('logicalExpression ('and'|'or') logicalExpression')'
    ;

comparisonExpression: '('expression ('<' | '>' | '<=' | '>=' |'=='|'!=') expression')';

logicalOperand
    :complexExpression
    |expression '.' functionCall
    |functionCall
    |expression '['(ID|INT)']'
    |ID
    |comparisonExpression
    |BOOL
    ;

complexExpression
    : expression
    | '('complexExpression ('+' | '-' | '*' | '/') complexExpression')';

expression
    : expression '.' functionCall
    | expression '['(ID|INT)']'
    | functionCall
    | ID
    | tupleLiteral
    | setLiteral
    | elementLiteral
    ;

tupleLiteral: '<' (dataType (','dataType)*)? '>' ;

setLiteral: '{' (dataType (','dataType)*)? '}' ;

elementLiteral: INT|STRING|BOOL;

dataType:INT|STRING|BOOL|setLiteral|tupleLiteral|elementLiteral;

ID : [a-zA-Z_][a-zA-Z_0-9]* ;
INT : [0-9]+ ;
STRING : '"' (~["\\\r\n] | '\\' .)* '"' ;
BOOL : 'true'|'false';
COMMENT: '//' ~[\r\n]* -> skip ;
WS : [ \t\r\n]+ -> skip ;

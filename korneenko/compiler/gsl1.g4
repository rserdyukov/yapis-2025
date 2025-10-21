grammar gsl1;

program: (statement | functionDef)* EOF;

statement
    : tableDeclaration
    | dataInsert
    | dataUpdate
    | dataDelete
    | assignment
    | typedAssignment
    | ifStatement
    | switchStatement
    | returnStatement
    | functionDef
    | forLoop
    | printStatement
    ;

tableDeclaration: ID '=' 'Table' '(' columnDef (',' columnDef)* ')';
columnDef: ID '=' 'Сolumn' '(' type ')';
type: ID | ID '[' type ']';

dataInsert: ID '+=' expression;

dataUpdate: 'for' ID 'in' expression ('where' expression)? ':' memberAssignment;
dataDelete: ID '-=' '(' generatorExpression ')';
generatorExpression: ID 'for' ID 'in' ID ('if' expression)?;

assignment: singleAssignment | multipleAssignment | memberAssignment;
singleAssignment: ID '=' expression;
multipleAssignment: ID (',' ID)+ ':=' expression (',' expression)+;
memberAssignment: ID '.' ID '=' expression;
// also allow nested member chains: r.a.b = expr
// parsed via expression on LHS in assignment, but keep simple here

typedAssignment: ID ':' type '=' expression;

forLoop: 'for' ID 'in' expression ('where' expression)? ':' (statement | block);
block: '{' statement* '}' | statement;

ifStatement: 'if' expression ':' (statement | block);

switchStatement
    : 'switch' '(' expression ')' ':' (caseClause+ defaultClause?)
    ;

caseClause: 'case' expression ':' (statement | block);
defaultClause: 'default' ':' (statement | block);

printStatement: 'print' '(' expression (',' expression)* ')' ';'?;

functionDef: 'func' ID '(' parameters? ')' ('->' type)? ':' functionSuite
           | 'func' ID '(' parameters? ')' ('->' type)? block;
functionSuite: statement+;
parameters: parameter (',' parameter)*;
parameter: ID ':' type;

returnStatement: 'return' expression;

expression
    : literal                                                    # literalExpr
    | ID                                                         # idExpr
    | expression '.' ID                                          # memberAccessExpr
    | expression '(' (expression (',' expression)*)? ')'         # callExpr
    | '[' ']'                                                    # emptyListExpr
    | '[' expression (',' expression)* ']'                       # listLiteralExpr
    | '[' comprehension ']'                                      # listComprehensionExpr
    | '(' expression ')'                                         # parenExpr
    | expression op=('*' | '/' | '%') expression                # multExpr
    | expression op=('+' | '-') expression                      # addExpr
    | expression op=('==' | '!=' | '<' | '>' | '<=' | '>=') expression # compareExpr
    | expression 'and' expression                                # andExpr
    | expression 'or' expression                                 # orExpr
    ;

comprehension: expression 'for' ID 'in' expression ('if' expression)?;

literal
    : INT
    | FLOAT
    | STRING
    | 'true'
    | 'false'
    | 'None'
    ;

// Literals
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]*;
STRING: '"' (~["\\\r\n] | '\\' .)* '"';

ID: [a-zA-Z_][a-zA-Z_0-9]*;

// Whitespace and comments
WS: [ \t\r\n]+ -> skip;
COMMENT: '#' ~[\r\n]* -> skip;
BLOCK_COMMENT: '# ===' .*? '===' -> skip;
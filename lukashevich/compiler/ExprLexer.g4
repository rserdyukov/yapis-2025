lexer grammar ExprLexer;

FUN: 'func';
RETURN: 'return';
IF: 'if';
THEN: 'then';
ELSE: 'else';
FOR: 'for';
IN: 'in';
AS: 'as';

LPAREN : '(';
RPAREN : ')';
LCURLY : '{';
RCURLY : '}';
COMMA : ',';
DOT : '.';
SEMI: ';';

TYPE_INT: 'int';
TYPE_COLOR: 'color';
TYPE_PIXEL: 'pixel';
TYPE_IMAGE: 'image';
TYPE_FLOAT: 'float';
ASSIGN: '=';
EQ_EQ: '==';
GT: '>';
LT: '<';
PLUS: '+';
MINUS: '-';
DIV: '/';
MULT: '*';
OUT: ' -> ';


INT : [0-9]+;
FLOAT : [+-]?([0-9]*[.])?[0-9]+;
STRING : '"' ( ~["] | '""' )* '"';

ID : [a-zA-Z_][a-zA-Z_0-9]*; 

WS : [ \t\n\r]+ -> skip;

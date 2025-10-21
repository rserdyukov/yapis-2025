lexer grammar mcl_lexer;

IF: 'if';
ELSE: 'else';
WHILE: 'while';
UNTIL: 'until';
FOR: 'for';
IN: 'in';

FUNC: 'func';
RETURN: 'return';
VOID_TYPE: 'void'; 

LAMBDA: 'lambda';

AND: 'and';
OR: 'or';
NOT: 'not';
TRUE: 'true';
FALSE: 'false';

INT_TYPE: 'int';
FLOAT_TYPE: 'float';
VECTOR_TYPE: 'vector';
MATRIX_TYPE: 'matrix';
TUPLE_TYPE: 'tuple';
BOOLEAN_TYPE: 'boolean';
STRING_TYPE: 'string';

NAN: 'NaN';
INFINITY: 'Infinity';

FLOAT: (DIGIT+ '.' DIGIT*) | ('.' DIGIT+);

INTEGER: DIGIT+;

STRING: '"' ( ~["\r\n] )*? '"';

PLUS: '+';
MINUS: '-';
MUL: '*';
DIV: '/';
POW: '^';
MOD: '%';

EQ: '==';
NEQ: '!=';
GT: '>';
LT: '<';
GTE: '>=';
LTE: '<=';

ASSIGN: '=';
LPAREN: '(';   
RPAREN: ')';   
LBRACE: '{';   
RBRACE: '}';   
LBRACK: '[';   
RBRACK: ']';   
VBAR: '|';     
COMMA: ',';
COLON: ':';
ARROW: '->';   
QMARK: '?';    


IDENTIFIER: [a-zA-Z_] [a-zA-Z0-9_]*;

COMMENT: '#' ~[\r\n]* -> skip;


// Пробелы будут отдельно обрабатываться для корректной генерации виртуальных отступов
// За счёт расширения класса лексера уже при реализации синт. анализатора
// собственно их мы не скипаем, тк надо контролировать их количество в начале строки
WS: [ \t]+; 

NL: ( '\r'? '\n' | '\r' );

INDENT: 'indent';
DEDENT: 'dedent';

fragment DIGIT: [0-9];
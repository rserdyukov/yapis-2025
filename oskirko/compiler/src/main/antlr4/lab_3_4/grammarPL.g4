grammar grammarPL;

program
    : (functionDeclaration | statement)* EOF
    ;

// -----------------------------------------------
// БАЗОВЫЕ ПРАВИЛА ПАРСЕРА
// -----------------------------------------------

// Правило для типа объявляемой переменной
declarationType
    : baseType
    | declarationArrayType
    ;

// Правило для базового типа
baseType
    : TYPE_INTEGER
    | TYPE_FLOAT
    | TYPE_STRING
    | TYPE_BOOLEAN
    ;

// Правило для типа объявляемого массива
declarationArrayType
    : baseType LSQBRACKET expr RSQBRACKET
    ;

// Правило для литерала массива
arrayLiteral
    : LSQBRACKET expr (COMMA expr)* RSQBRACKET
    | '[]'
    ;

// Правило для элемента массива
arrayIndex
    : ID LSQBRACKET expr RSQBRACKET
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ФУНКЦИЙ
// -----------------------------------------------

// Правило для объявления функции
functionDeclaration
    : FUNCTION ID LRBRACKET declarationFunctionParamList? RRBRACKET block
    ;

// Правило для типа параметра в функции
paramType
    : baseType
    | paramArrayType
    ;

// Правило для типа объявляемого массива в функции
paramArrayType
    : baseType '[]'
    ;

// Правило для параметра функции
declarationFunctionParam
    : paramType ID
    ;

// Правилол для результирующего параметра функции
declarationFunctionResultParam
    : paramType QUESTION ID
    ;

// Правило для параметров функции
declarationFunctionParamList
    : declarationFunctionParam (COMMA declarationFunctionParam)* (COMMA declarationFunctionResultParam)*
    ;

// Правило для списка аргументов для вызова функции
argList
    : functionArgExpr (COMMA functionArgExpr)*
    ;

// Правило для выхова функции
functionCall
    : ID LRBRACKET argList? RRBRACKET
    ;

// Правило для аргумента функции
functionArgExpr
    : (INCREMENT | DECREMENT | NOT)* functionArgPrimary (INCREMENT | DECREMENT)*
    | LRBRACKET functionArgExpr RRBRACKET
    | functionArgExpr POW functionArgExpr
    | functionArgExpr (MULT | DIV | REMDIV) functionArgExpr
    | functionArgExpr (PLUS | MINUS) functionArgExpr
    | functionArgExpr (EQ | NEQ | LT | LE | GT | GE) functionArgExpr
    | functionArgExpr AND functionArgExpr
    | functionArgExpr OR functionArgExpr
    ;

// Правило для примитивного элемента в аргументе функции
functionArgPrimary
    : INT
    | FLOAT
    | STRING
    | ID
    | arrayIndex
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ВЫРАЖЕНИЙ (ОТ БОЛЬШЕГО ПРИОРИТЕТА К МЕНЬШЕМУ)
// -----------------------------------------------

expr
    : (INCREMENT | DECREMENT | NOT)* primary (INCREMENT | DECREMENT)*
    | LRBRACKET expr RRBRACKET
    | functionArgExpr POW functionArgExpr
    | expr (MULT | DIV | REMDIV) expr
    | expr (PLUS | MINUS) expr
    | expr (EQ | NEQ | LT | LE | GT | GE) expr
    | expr AND expr
    | expr OR expr
    ;

primary
    : INT
    | FLOAT
    | STRING
    | ID
    | functionCall
    | arrayIndex
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ИНСТРУКЦИЙ
// -----------------------------------------------

// Правило для интсрукции с выражением
exprStatement
    : expr SEMICOLON
    ;

// Правило для инструкции с объявлением переменной
varDeclarationStatement
    : declarationType ID (ASSIGN (arrayLiteral | expr))? SEMICOLON
    ;

// Правило для объявления переменной
varDeclarationWithoutSemicolon
    : declarationType ID (ASSIGN (arrayLiteral | expr))?
    ;

// Правило для инструкции с присвоением переменной значения
assignmentStatement
    : (ID LSQBRACKET expr RSQBRACKET | ID) ASSIGN expr SEMICOLON
    ;

// Правило для инстуркции условного оператора
ifStatement
    : IF LRBRACKET expr RRBRACKET block (ELSE block)?
    ;

// Правило для инструкции оператора for
forStatement
    : FOR LRBRACKET forInit? SEMICOLON forCondition? SEMICOLON forUpdate? RRBRACKET block
    ;

// Правило для инициализации оператора for
forInit
    : varDeclarationWithoutSemicolon
    | expr
    ;

// Правило для условия оператора for
forCondition
    : expr
    ;

// Правило для обновления оператора for
forUpdate
    : expr (COMMA expr)*
    ;

// Правило для инструкции switch
switchStatement
    : SWITCH LRBRACKET expr RRBRACKET LFIGBRACKET caseBlock* RFIGRACKET
    ;

// Правило для условного цикла
whileStatement
    : WHILE LRBRACKET expr RRBRACKET block
    ;

// Правило для инструкции
statement
    : varDeclarationStatement
    | assignmentStatement
    | ifStatement
    | forStatement
    | switchStatement
    | exprStatement
    | whileStatement
    | BREAK SEMICOLON
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ БЛОКОВ
// -----------------------------------------------

// Правило для блока case
caseBlock
    : CASE expr block
    ;

// Правило для блока кода
block
    : LFIGBRACKET statement* RFIGRACKET
    ;

// -----------------------------------------------
// ПРАВИЛА ЛЕКСЕРА
// -----------------------------------------------

FUNCTION: 'function' ;
TYPE_INTEGER: 'integer' ;
TYPE_FLOAT: 'float' ;
TYPE_STRING: 'string' ;
TYPE_BOOLEAN: 'boolean' ;
IF: 'if' ;
ELSE: 'else' ;
FOR: 'for' ;
WHILE: 'while' ;
SWITCH: 'switch' ;
CASE: 'case' ;
BREAK: 'break' ;
TRUE: 'true' ;
FALSE: 'false' ;

ID: [a-zA-Z][a-zA-Z0-9$_]* ;

INT: [0-9]+ ;
FLOAT: [0-9]*'.'[0-9]+ ;
STRING: '"' (~["\\\r\n] | '\\' .)* '"' ;
BOOLEAN: (TRUE|FALSE) ;

QUESTION: '?' ;
LT: '<' ;
GT: '>';
LE: '<=' ;
GE: '>=' ;
EQ: '==' ;
NEQ: '!=' ;
AND: '&&' ;
OR: '||' ;
NOT: '!' ;
LSQBRACKET: '[' ;
RSQBRACKET: ']' ;
LRBRACKET: '(' ;
RRBRACKET: ')' ;
LFIGBRACKET: '{' ;
RFIGRACKET: '}' ;
SEMICOLON: ';' ;
COMMA: ',' ;
ASSIGN: '=' ;
REMDIV: '%' ;
DIV: '/' ;
PLUS: '+' ;
MINUS: '-' ;
MULT: '*' ;
DECREMENT: '--' ;
INCREMENT: '++' ;
POW: '^' ;

WS: [ \t\r\n]+ -> skip ;
COMMENT: '#' ~[\r\n]* -> skip ;
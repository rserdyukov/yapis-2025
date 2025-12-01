grammar grammarPL;

program
    : functionDeclarationPart statement* EOF
    ;

// -----------------------------------------------
// БАЗОВЫЕ ПРАВИЛА ПАРСЕРА
// -----------------------------------------------

// Правило для типа объявляемой переменной
declarationType
    : baseType
    ;

// Правило для базового типа
baseType
    : TYPE_INTEGER
    | TYPE_FLOAT
    ;

// Правило для типа объявляемого массива
declarationArrayType
    : baseType LSQBRACKET expr RSQBRACKET
    ;

// Правило для элемента массива
arrayIndex
    : ID LSQBRACKET expr RSQBRACKET
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ФУНКЦИЙ
// -----------------------------------------------

// Правило для части кода для объявления функции
functionDeclarationPart
    : functionDeclaration*
    ;

// Правило для объявления функции
functionDeclaration
    : FUNCTION ID LRBRACKET declarationFunctionParamList? RRBRACKET block
    ;

// Правило для типа параметра в функции
paramType
    : baseType
    ;

// Правило для типа объявляемого массива в функции
paramArrayType
    : baseType '[]'
    ;

// Правило для параметра функции
declarationFunctionParam
    : paramType ID
    ;

// Правило для параметра функции
declarationArrayFunctionParam
    : paramArrayType ID
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
    : NOT? functionArgPrimary
    | LRBRACKET functionArgExpr RRBRACKET
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
    : NOT? primary
    | LRBRACKET expr RRBRACKET
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
    : declarationType ID (ASSIGN expr)? SEMICOLON
    ;

// Правило для объявления массива
arrayDeclarationStatement
    : declarationArrayType ID SEMICOLON
    ;

// Правило для объявления переменной
varDeclarationWithoutSemicolon
    : declarationType ID (ASSIGN expr)?
    ;

// Правило для инструкции с присвоением переменной значения
assignmentStatement
    : (arrayIndexAccess | ID) ASSIGN expr SEMICOLON
    ;

// Правило для получения элемента массива по индексу
arrayIndexAccess
    : ID LSQBRACKET expr RSQBRACKET
    ;

// Правило для инструкции с присвоением переменной значения
assignmentStatementWithoutSemicolon
    : (ID LSQBRACKET expr RSQBRACKET | ID) ASSIGN expr
    ;

// Правило для инстуркции условного оператора
ifStatement
    : ifBlock elseBlock?
    ;

// Правило для сигнатуры конструкции if
ifSignature
    : IF LRBRACKET expr RRBRACKET
    ;

// Правило для сигнатуры конструкции if
ifBlock
    : ifSignature block
    ;

// Правило для блока else
elseBlock
    : ELSE block
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
    : (assignmentStatementWithoutSemicolon|expr) (COMMA (assignmentStatementWithoutSemicolon|expr))*
    ;

// Правило для инструкции switch
switchStatement
    : SWITCH LRBRACKET switchExpression RRBRACKET LFIGBRACKET caseBlock* defaultBlock? RFIGRACKET
    ;

// Правило для условного цикла
whileStatement
    : WHILE LRBRACKET whileCondition RRBRACKET block
    ;

// Правило для конструкции while
whileCondition
    : expr
    ;

// Правило для выражения в switch
switchExpression
    : expr
    ;

// Правило для вызова функции
functionCallStatement
    : functionCall SEMICOLON
    ;

// Правило для инструкции
statement
    : varDeclarationStatement
    | arrayDeclarationStatement
    | assignmentStatement
    | ifStatement
    | forStatement
    | switchStatement
    | exprStatement
    | whileStatement
    | functionCallStatement
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ БЛОКОВ
// -----------------------------------------------

// Правило для блока case
caseBlock
    : CASE caseExpr block
    ;

// Правило для выражения блока case
caseExpr
    : expr
    ;

// Правило для блока default
defaultBlock
    : DEFAULT block
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
TRUE: 'true' ;
FALSE: 'false' ;
DEFAULT: 'default' ;

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

WS: [ \t\r\n]+ -> skip ;
COMMENT: '#' ~[\r\n]* -> skip ;
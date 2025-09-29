grammar grammarPL;

program
    : (functionDeclaration | statement)* EOF
    ;

// -----------------------------------------------
// БАЗОВЫЕ ПРАВИЛА ПАРСЕРА
// -----------------------------------------------

// Правило для типа объявляемой переменной
declarationType
    : baseType                                                                  #baseDeclarationType_
    | declarationArrayType                                                      #arrayDeclarationType_
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

// Правило для литерала массива
arrayLiteral
    : LSQBRACKET expr (COMMA expr)* RSQBRACKET
    | '[]'
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
    : baseType                                                                  #baseParameterType_
    | paramArrayType                                                            #arrayParameterType_
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
    : expr (COMMA expr)*
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ВЫРАЖЕНИЙ (ОТ БОЛЬШЕГО ПРИОРИТЕТА К МЕНЬШЕМУ)
// -----------------------------------------------

expr
    : (INCREMENT | DECREMENT | NOT)* primary (INCREMENT | DECREMENT)*           #firstPriority_
    | expr (MULT | DIV | '%' | INTDIV) expr                                     #secondPriority_
    | expr (PLUS | MINUS) expr                                                  #thirdPriority_
    | expr (EQ | NEQ | LT | LE | GT | GE) expr                                  #fourthPriority_
    | expr AND expr                                                             #fifthPriority_
    | expr OR expr                                                              #sixthPriority_
    ;

primary
    : INT                                                                       #int_
    | FLOAT                                                                     #float_
    | STRING                                                                    #string_
    | ID                                                                        #id_
    | ID LRBRACKET argList? RRBRACKET                                           #function_
    | ID LSQBRACKET expr RSQBRACKET                                             #arrayWithIndex_
    | LRBRACKET expr RRBRACKET                                                  #bracketsExpr_
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
    : varDeclarationWithoutSemicolon                                            #varDeclarationWithoutSemicolon_
    | expr                                                                      #expr_
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

// Правило для инструкции
statement
    : varDeclarationStatement                                                   #varDeclarationStatement_
    | assignmentStatement                                                       #assignmentStatement_
    | ifStatement                                                               #ifStatement_
    | forStatement                                                              #forStatement_
    | switchStatement                                                           #switchStatement_
    | exprStatement                                                             #exprStatement_
    | BREAK SEMICOLON                                                           #breakStatement_
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
IF: 'if' ;
ELSE: 'else' ;
FOR: 'for' ;
SWITCH: 'switch' ;
CASE: 'case' ;
BREAK: 'break' ;

ID: [a-zA-Z][a-zA-Z0-9$_]* ;

INT: [0-9]+ ;
FLOAT: [0-9]*'.'[0-9]+ ;
STRING : '"' (~["\\\r\n] | '\\' .)* '"' ;

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
INTDIV: '//' ;
DIV: '/' ;
PLUS: '+' ;
MINUS: '-' ;
MULT: '*' ;
DECREMENT: '--' ;
INCREMENT: '++' ;

WS: [ \t\r\n]+ -> skip ;
COMMENT: '#' ~[\r\n]* -> skip ;
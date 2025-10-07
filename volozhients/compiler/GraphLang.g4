grammar GraphLang;

program
    : (functionDeclaration | topLevelStatement | statement)* EOF
    ;

//////////////////////////////
// БАЗОВЫЕ ПРАВИЛА ПАРСЕРА //
/////////////////////////////

topLevelStatement
    : nodeDecl
    | arcDecl
    | graphDecl
    ;

nodeDecl
    : NODE ID SEMICOLON
    ;

arcDecl
    : ARC arcLiteral SEMICOLON
    ;

graphDecl
    : GRAPH ID SEMICOLON
    ;

arcLiteral
    : LT ID COMMA ID GT
    ;

/////////////////////////////////
// ПРАВИЛА ПАРСЕРА ДЛЯ ФУНКЦИЙ //
/////////////////////////////////

functionDeclaration
    : VOID ID LRBRACKET functionParamList? RRBRACKET block
    ;

functionParam
    : type ID
    ;

functionParamList
    : functionParam (COMMA functionParam)*
    ;

type
    : NODE
    | GRAPH
    | ARC
    | ID
    ;

///////////////////////////////////
// ПРАВИЛА ПАРСЕРА ДЛЯ ВЫРАЖЕНИЙ //
///////////////////////////////////

expr
    : primary                                                              #primaryExpr_
    | expr (MULT | DIV) expr                                               #mulDivExpr_
    | expr (PLUS | MINUS) expr                                             #addSubExpr_
    | expr (EQ | NEQ | LT | LE | GT | GE) expr                             #compExpr_
    | expr AND expr                                                        #andExpr_
    | expr OR expr                                                         #orExpr_
    ;


primary
    : INT                                                                 #int_
    | FLOAT                                                               #float_
    | STRING                                                              #string_
    | arcLiteral                                                          #arcLiteral_
    | funcCall                                                            #funcCall_
    | memberAccess                                                        #memberAccess_
    | ID                                                                  #id_
    | nodeGroup                                                           #nodeGroup_
    | LRBRACKET ( nodeGroupInner | expr ) RRBRACKET                       #bracketsExprOrGroup_
    ;


funcCall
    : ID LRBRACKET argList? RRBRACKET
    ;

nodeGroup
    : LRBRACKET nodeGroupInner RRBRACKET
    ;

nodeGroupInner
    : ID COMMA ID (COMMA ID)*
    ;

memberAccess
    : accessStart ( DOT accessElement )*
    ;

accessStart
    : ID
    ;


accessElement
    : ID ( LRBRACKET argList? RRBRACKET )?
    ;


argList
    : expr (COMMA expr)*
    ;

////////////////////////////////////
// ПРАВИЛА ПАРСЕРА ДЛЯ ИНСТРУКЦИЙ //
////////////////////////////////////

exprStatement
    : expr SEMICOLON
    ;

assignmentStatement
    : (ID | memberAccess) ASSIGN expr SEMICOLON
    ;

varDeclarationStatement
    : NODE ID SEMICOLON
    | GRAPH ID SEMICOLON
    ;

arcDeclarationStatement
    : ARC arcLiteral SEMICOLON
    ;

ifStatement
    : IF LRBRACKET expr RRBRACKET block (ELSE block)?
    ;

forEachStatement
    : FOR LRBRACKET type ID COLON expr RRBRACKET block
    ;

switchStatement
    : SWITCH LRBRACKET expr RRBRACKET LFIGBRACKET switchBlock* RFIGRACKET
    ;

switchBlock
    : CASE caseLabel COLON statement*
    | statement
    ;

caseLabel
    : ID
    | STRING
    | INT
    ;

printStatement
    : PRINT LRBRACKET argList? RRBRACKET SEMICOLON
    ;

statement
    : varDeclarationStatement                                                  #varDeclStmt_
    | arcDeclarationStatement                                                  #arcDeclStmt_
    | assignmentStatement                                                      #assignStmt_
    | ifStatement                                                              #ifStmt_
    | forEachStatement                                                         #forEachStmt_
    | switchStatement                                                          #switchStmt_
    | printStatement                                                           #printStmt_
    | exprStatement                                                            #exprStmt_
    | SEMICOLON                                                                #emptyStmt_
    ;

////////////////////////
// ПРАВИЛА ДЛЯ БЛОКОВ //
////////////////////////

block
    : LFIGBRACKET statement* RFIGRACKET
    ;

////////////
// ЛЕКСЕР //
////////////

NODE        : 'node' ;
ARC         : 'arc' ;
GRAPH       : 'graph' ;
VOID        : 'void' ;
IF          : 'if' ;
ELSE        : 'else' ;
FOR         : 'for' ;
SWITCH      : 'switch' ;
CASE        : 'case' ;
PRINT       : 'print' ;
RETURN      : 'return' ;

// Операторы сравнения и логические (длинные формы раньше коротких)
EQ          : '==' ;
NEQ         : '!=' ;
LE          : '<=' ;
GE          : '>=' ;
AND         : '&&' ;
OR          : '||' ;
INTDIV      : '//' ;

// Одиночные символы и пунктуация
ASSIGN      : '=' ;
LT          : '<' ;
GT          : '>' ;
SEMICOLON   : ';' ;
COMMA       : ',' ;
COLON       : ':' ;
LRBRACKET   : '(' ;
RRBRACKET   : ')' ;
LFIGBRACKET : '{' ;
RFIGRACKET  : '}' ;
DOT         : '.' ;

// Арифметика
PLUS        : '+' ;
MINUS       : '-' ;
MULT        : '*' ;
DIV         : '/' ;
NOT         : '!' ;

// Литералы
STRING
    : '"' (ESC | ~["\\\r\n])* '"'
    ;

fragment ESC
    : '\\' ["\\/bfnrt]
    | '\\' 'u' HEX HEX HEX HEX
    ;

fragment HEX
    : [0-9a-fA-F]
    ;

FLOAT
    : [0-9]+ '.' [0-9]+
    ;

INT
    : [0-9]+
    ;

ID
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

// Комментарии и пробелы
WS
    : [ \t\r\n\u000C]+ -> skip
    ;

LINE_COMMENT
    : '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;
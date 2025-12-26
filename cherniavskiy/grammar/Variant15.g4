grammar Variant15;

// --- Parser Rules ---

program: functionDeclaration* EOF;

block: LBRACE statement* RBRACE;

statement
    : variableDeclaration           # VarDeclStmt
    | assignment                    # AssignStmt
    | ifStatement                   # IfStmt
    | switchStatement               # SwitchStmt
    | forStatement                  # ForStmt
    | functionCall                  # FuncCallStmt
    | ioStatement                   # IOStmt
    | functionDeclaration           # FuncDeclStmt
    | BREAK                         # BreakStmt
    | CONTINUE                      # ContinueStmt
    | RETURN expression?            # ReturnStmt
    | block                         # BlockStmt
    ;

// Handles: string str = "val" AND char r1, r2 = 'a', 'b'
variableDeclaration
    : typeSpecifier IDENTIFIER (COMMA IDENTIFIER)* (ASSIGN expression (COMMA expression)*)?
    ;

// Handles: i = i + 1 AND i++ AND strs[0] = "val"
assignment
    : designator (COMMA designator)* ASSIGN expression (COMMA expression)*
    | designator INC
    ;

designator
    : IDENTIFIER (LBRACK expression (COLON expression)? RBRACK)*
    ;

ifStatement
    : IF expression? block (ELSE block)?
    ;

// Go-style switch: switch { case cond { } }
switchStatement
    : SWITCH LBRACE caseBlock* defaultBlock? RBRACE
    ;

caseBlock
    : CASE expression block
    ;

defaultBlock
    : DEFAULT block
    ;

// Handles: for int i = 0; i < 5; i = i + 1 { }
forStatement
    : FOR (variableDeclaration | assignment)? SEMI expression? SEMI (assignment | expression)? block
    ;

// Handles: func main() { } AND func Split(...) []string { }
functionDeclaration
    : FUNC IDENTIFIER LPAREN parameterList? RPAREN typeSpecifier? block
    ;

parameterList
    : parameter (COMMA parameter)*
    ;

parameter
    : typeSpecifier IDENTIFIER
    ;

functionCall
    : IDENTIFIER LPAREN argumentList? RPAREN
    ;

argumentList
    : expression (COMMA expression)*
    ;

ioStatement
    : READ LPAREN IDENTIFIER RPAREN
    | WRITE LPAREN expression RPAREN
    | PRINT LPAREN argumentList RPAREN
    ;

expression
    : expression (MULT | DIV | SPLIT) expression    # MultiplicativeExpr
    | expression (PLUS | MINUS) expression          # AdditiveExpr
    | expression (EQ | NEQ | LT | GT | LE | GE) expression # RelationalExpr
    | LPAREN expression RPAREN                      # ParenExpr
    | atom                                          # AtomExpr
    ;

atom
    : designator
    | STRING_LITERAL
    | CHAR_LITERAL
    | INT_LITERAL
    | BOOL_LITERAL
    | functionCall
    | LEN LPAREN expression RPAREN  // Built-in len()
    | arrayLiteral
    ;

arrayLiteral
    : LBRACE (expression (COMMA expression)*)? RBRACE
    ;

// Handles: string, []string, string[], rune, char
typeSpecifier
    : (LBRACK RBRACK)? primitiveType (LBRACK RBRACK)?
    ;

primitiveType
    : STRING | CHAR | RUNE | INT | BOOL | VOID
    ;

// --- Lexer Rules ---

// Keywords
FUNC:   'func';
RETURN: 'return';
IF:     'if';
ELSE:   'else';
SWITCH: 'switch';
CASE:   'case';
DEFAULT:'default';
FOR:    'for';
BREAK:  'break';
CONTINUE: 'continue';
READ:   'read';
WRITE:  'write';
PRINT:  'print';
LEN:    'len';

// Types
STRING: 'string';
CHAR:   'char';
RUNE:   'rune'; // Alias for char in examples
INT:    'int';
BOOL:   'bool';
VOID:   'void';

// Literals
BOOL_LITERAL: 'true' | 'false';

// Operators
PLUS:   '+';
MINUS:  '-';
MULT:   '*';
SPLIT:  '\\';
DIV:    '/';
INC:    '++';

ASSIGN: '=';
EQ:     '==';
NEQ:    '!=';
LT:     '<';
GT:     '>';
LE:     '<=';
GE:     '>=';

// Delimiters
SEMI:   ';';
COMMA:  ',';
COLON:  ':';
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';

// Literals
IDENTIFIER: [a-zA-Z_] [a-zA-Z0-9_]*;
INT_LITERAL: [0-9]+;

STRING_LITERAL: '"' ( '\\' . | ~["\\\r\n] )* '"';
CHAR_LITERAL:   '\'' ( '\\' . | ~['\\\r\n] )* '\'';

// Skip
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;

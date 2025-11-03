grammar lang;

options { language = Python3; }

tokens {
    INDENT,
    DEDENT,
    LINE_BREAK
}

@lexer::header {
from antlr4.Token import CommonToken
from gen.langParser import langParser

class IndentStack:
    def __init__(self): self._s = []
    def empty(self): return len(self._s) == 0
    def push(self, wsval): self._s.append(wsval)
    def pop(self): self._s.pop()
    def wsval(self): return self._s[-1] if self._s else 0

class TokenQueue:
    def __init__(self): self._q = []
    def empty(self): return len(self._q) == 0
    def enq(self, t): self._q.append(t)
    def deq(self): return self._q.pop(0)
}

@lexer::members {
    self._tokens = TokenQueue()
    self._indents = IndentStack()
    self._suppressNewlines = False

def nextToken(self):
    if not self._tokens.empty():
        return self._tokens.deq()

    t = super(langLexer, self).nextToken()
    if t.type == Token.EOF:
        self.emitFullDedent()
        self.emitEndToken(t)
        return self._tokens.deq()
    return t

def emitIndent(self, length=0, text='INDENT'):
    t = self.createToken(langParser.INDENT, text, length)
    self._tokens.enq(t)

def emitDedent(self):
    t = self.createToken(langParser.DEDENT, 'DEDENT')
    self._tokens.enq(t)

def emitFullDedent(self):
    while not self._indents.empty():
        self._indents.pop()
        self.emitDedent()

def emitLineBreak(self):
    t = self.createToken(langParser.LINE_BREAK, 'LINE_BREAK')
    self._tokens.enq(t)

def emitEndToken(self, token):
    self._tokens.enq(token)

def createToken(self, type_, text="", length=0):
    start = self._tokenStartCharIndex
    stop = start + length
    t = CommonToken(self._tokenFactorySourcePair,
                    type_, self.DEFAULT_TOKEN_CHANNEL,
                    start, stop)
    t.text = text
    return t
}

program
    : (statement | LINE_BREAK)* EOF
    ;

statement
    : functionDef
    | simpleStmt
    ;

functionDef
    : type ID '(' parameterList? ')'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
    ;

parameterList
    : parameter (',' parameter)*
    ;

parameter
    : ('out')? type ID
    ;

simpleStmt
    : varDecl
    | assignment
    | funcCall
    | 'return' expr? LINE_BREAK
    | ifStmt
    | whileStmt
    | forStmt
    ;

varDecl
    : type ID (',' ID)* ('=' exprList)? LINE_BREAK
    | ID '=' exprList LINE_BREAK
    | ID LINE_BREAK
    ;

assignment
    : type ID (',' ID)* (('=' exprList)
         | PLUS_ASSIGN expr
         | MINUS_ASSIGN expr
         | MUL_ASSIGN expr
         | DIV_ASSIGN expr
         | INC
         | DEC)? LINE_BREAK
    | ID (('=' exprList)
         | PLUS_ASSIGN expr
         | MINUS_ASSIGN expr
         | MUL_ASSIGN expr
         | DIV_ASSIGN expr
         | INC
         | DEC)? LINE_BREAK
    ;

exprList
    : expr (',' expr)*
    ;

emptyBlock
    : ':' LINE_BREAK? INDENT? LINE_BREAK* DEDENT?
    ;

ifStmt
    : 'if' '(' expr ')'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
      ('else'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
      )?
    ;

whileStmt
    : 'while' '(' expr ')'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
    ;

forStmt
    : 'for' '(' forInit? ';' forCond? ';' forIter? ')'
        (
          emptyBlock
        | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
        | ':' LINE_BREAK statement+
        )
    ;

forInit
    : type? ID ('=' expr)? (',' ID ('=' expr)? )*
    ;

forCond
    : expr
    ;

forIter
    : ID (INC | DEC)
    | ID '=' expr
    ;

funcCall
    : ID '(' argList? ')'
    ;

argList
    : expr (',' expr)*
    ;

expr
    : expr OR expr
    | expr AND expr
    | expr EQ expr
    | expr NEQ expr
    | expr LT expr
    | expr LE expr
    | expr GT expr
    | expr GE expr
    | expr PLUS expr
    | expr MINUS expr
    | expr MUL expr
    | expr DIV expr
    | expr MOD expr
    | prefixExpr
    | postfixExpr
    | primary
    ;

prefixExpr
    : (INC | DEC | NOT) expr
    ;

postfixExpr
    : primary (INC | DEC)
    ;

primary
    : '(' expr ')'                     # parensExpr
    | '(' type ')' expr                # castExpr
    | funcCall                         # funcCallPrimary
    | setLiteral                       # setLiteralPrimary
    | elementLiteral                   # elementLiteralPrimary
    | literal                          # literalPrimary
    | ID indexSuffix*                  # idWithIndex
    ;

indexSuffix
    : '[' expr ']'
    ;

setLiteral
    : 'set' '[' exprList? ']'
    ;

elementLiteral
    : 'element' '(' expr ')'
    ;

literal
    : INT
    | STRING
    | BOOLEAN
    | FLOAT
    ;

type
    : 'int'
    | 'float'
    | 'double'
    | 'char'
    | 'str'
    | 'bool'
    | 'element'
    | 'set'
    | 'void'
    ;

MUL : '*';
DIV : '/';
MOD : '%';
PLUS: '+';
MINUS: '-';
LT  : '<';
GT  : '>';
LE  : '<=' ;
GE  : '>=' ;
EQ  : '==' ;
NEQ : '!=' ;
AND : '&&' ;
OR  : '||' ;
NOT : '!' ;
INC : '++' ;
DEC : '--' ;
PLUS_ASSIGN : '+=' ;
MINUS_ASSIGN : '-=' ;
MUL_ASSIGN : '*=' ;
DIV_ASSIGN : '/=' ;

LPAREN : '(' ;
RPAREN : ')' ;
LBRACK : '[' ;
RBRACK : ']' ;
COMMA  : ',' ;

BOOLEAN : 'true' | 'false' ;
INT     : [0-9]+ ;
FLOAT     : [0-9]+'.'[0-9]+;
STRING  : '"' ( ~["\\] | '\\' . )* '"' ;
ID      : [a-zA-Z_][a-zA-Z0-9_]* ;

NEWLINE
    : ('\r'? '\n')+ {
if not self._suppressNewlines:
    self.emitLineBreak()
self._suppressNewlines = True
la = self._input.LA(1)
if la not in [ord(' '), ord('\t'), ord('#')]:
    self._suppressNewlines = False
    self.emitFullDedent()
} -> channel(HIDDEN)
;

WS
    : [ \t]+ {
if self._tokenStartColumn == 0:
    la = self._input.LA(1)
    if la not in [ord('\r'), ord('\n'), ord('#'), -1]:
        self._suppressNewlines = False
        wsCount = 0
        for ch in self.text:
            wsCount += 1 if ch == ' ' else 8
        if wsCount > self._indents.wsval():
            self.emitIndent(len(self.text))
            self._indents.push(wsCount)
        else:
            while wsCount < self._indents.wsval():
                self.emitDedent()
                self._indents.pop()
} -> channel(HIDDEN)
;

LINE_COMMENT : '//' ~[\r\n]* -> skip ;

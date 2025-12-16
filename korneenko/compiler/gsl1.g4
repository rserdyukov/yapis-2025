grammar gsl1;

options { language = Python3; }

tokens { INDENT, DEDENT, LINE_BREAK }

// ---------- Лексер: механизм отступов ----------
@lexer::header {
from antlr4.Token import CommonToken
from gen.gsl1Parser import gsl1Parser

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
    self._parenDepth = 0

def nextToken(self):
    if not self._tokens.empty():
        return self._tokens.deq()
    t = super(gsl1Lexer, self).nextToken()
    # Отслеживаем уровень вложенности скобок
    if t.text == '(':
        self._parenDepth += 1
    elif t.text == ')':
        self._parenDepth -= 1
    if t.type == Token.EOF:
        self.emitFullDedent()
        self.emitEndToken(t)
        return self._tokens.deq()
    return t

def emitIndent(self, length=0, text='INDENT'):
    t = self.createToken(gsl1Parser.INDENT, text, length)
    self._tokens.enq(t)

def emitDedent(self):
    t = self.createToken(gsl1Parser.DEDENT, 'DEDENT')
    self._tokens.enq(t)

def emitFullDedent(self):
    while not self._indents.empty():
        self._indents.pop()
        self.emitDedent()

def emitLineBreak(self):
    t = self.createToken(gsl1Parser.LINE_BREAK, 'LINE_BREAK')
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

// ---------- Синтаксис ----------
program
: (statement | LINE_BREAK)* EOF;

statement
    : functionDef
    | ifStatement
    | switchStatement
    | forLoop
    | simpleStmt
    | caseClause        // <- добавлено
    | defaultClause     // <- добавлено
    ;

simpleStmt
    : tableDeclaration
    | dataInsert
    | dataUpdate
    | dataDelete
    | assignment
    | typedAssignment
    | printStatement
    | returnStatement
    ;

tableDeclaration: ID '=' TABLE_KW '(' columnDef (',' columnDef)* ')' LINE_BREAK?;
columnDef: ID '=' COLUMN_KW '(' type ')';
type: ID | ID '[' type ']';

dataInsert: ID '+=' expression LINE_BREAK?;
dataUpdate: 'for' ID 'in' expression ('where' expression)? suite;
dataDelete: ID '-=' '(' generatorExpression ')' LINE_BREAK?;
generatorExpression: ID 'for' ID 'in' ID ('if' expression)?;

assignment: singleAssignment | multipleAssignment | memberAssignment;
singleAssignment: ID '=' expression LINE_BREAK?;
multipleAssignment: ID (',' ID)+ ':=' expression (',' expression)+ LINE_BREAK?;
memberAssignment: ID '.' ID '=' expression LINE_BREAK?;

typedAssignment: ID ':' type '=' expression LINE_BREAK?;

forLoop: 'for' ID 'in' expression ('where' expression)? suite;

emptyBlock : ':' LINE_BREAK? INDENT? LINE_BREAK* DEDENT?;

ifStatement: 'if' expression suite;

// ---------- switch/case/default ----------
switchStatement
    : 'switch' '(' expression ')' suite
    ;

suite
    : emptyBlock
    | ':' LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
    | ':' simpleStmt
    | ':' LINE_BREAK INDENT switchBody DEDENT
    ;

switchBody
    : (caseClause | defaultClause | LINE_BREAK)+
    ;

caseClause
    : 'case' expression ':' (LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
                          | simpleStmt
                          | LINE_BREAK
                          )
    ;

defaultClause
    : 'default' ':' (LINE_BREAK INDENT (statement | LINE_BREAK)* DEDENT
                  | simpleStmt
                  | LINE_BREAK
                  )
    ;


caseBlock
    : caseClause
    | defaultClause
    ;

printStatement: 'print' '(' expression (',' expression)* ')' ';'? LINE_BREAK?;

functionDef
    : 'func' ID '(' parameters? ')' ('->' type)? ( emptyBlock | ':' LINE_BREAK INDENT functionSuite DEDENT | ':' simpleStmt )
    ;

functionSuite: statement+;
parameters: parameter (',' parameter)*;
parameter: ID ':' type;

returnStatement: 'return' expression LINE_BREAK?;

// ---------- Выражения ----------
expression
    : literal
    | ID
    | expression '.' ID
    | expression '(' (expression (',' expression)*)? ')'
    | '(' expression ')'
    | expression op=('*' | '/' | '%') expression
    | expression op=('+' | '-') expression
    | expression op=('==' | '!=' | '<' | '>' | '<=' | '>=') expression
    | expression 'and' expression
    | expression 'or' expression
    | listLiteral
    | listComprehension
    ;

listLiteral: '[' (expression (',' expression)*)? ']';
listComprehension: '[' expression 'for' ID 'in' expression ('if' expression)? ']';

literal
    : INT
    | FLOAT
    | STRING
    | 'true'
    | 'false'
    | 'None'
    ;

// ---------- Лексерные правила ----------
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]*;
STRING: '"' (~["\\\r\n] | '\\' .)* '"';

// Keywords (они будут распознаваться лексером, но в парсере используем строчные)
FOR: 'for';
IN: 'in';
WHERE: 'where';
IF: 'if';
SWITCH: 'switch';
CASE: 'case';
DEFAULT: 'default';
PRINT: 'print';
FUNC: 'func';
RETURN: 'return';
AND: 'and';
OR: 'or';
TABLE_KW: 'Table';
COLUMN_KW: 'Сolumn';
TRUE: 'true';
FALSE: 'false';
NONE: 'None';

ID: [a-zA-Z_][a-zA-Z_0-9]*;

NEWLINE
    : ('\r'? '\n')+ {
if not self._suppressNewlines and self._parenDepth == 0:
    self.emitLineBreak()
self._suppressNewlines = True
la = self._input.LA(1)
if la not in [ord(' '), ord('\t'), ord('#')]:
    self._suppressNewlines = False
    if self._parenDepth == 0:
        self.emitFullDedent()
} -> channel(HIDDEN)
;

WS
    : [ \t]+ {
if self._tokenStartColumn == 0 and self._parenDepth == 0:
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

COMMENT: '#' ~[\r\n]* -> skip;
BLOCK_COMMENT: '# ===' .*? '===' -> skip;
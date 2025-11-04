grammar SimplePython;

options {
    language = Python3;
}

tokens {
    INDENT,
    DEDENT,
    LINE_BREAK
}

@lexer::header {
from antlr4.Token import CommonToken
from generated.SimplePythonParser import SimplePythonParser

class IndentStack:
    def __init__(self)    : self._s = []
    def empty(self)       : return len(self._s) == 0
    def push(self, wsval) : self._s.append(wsval)
    def pop(self)         : self._s.pop()
    def wsval(self)       : return self._s[-1] if len(self._s) > 0 else 0

class TokenQueue:
    def __init__(self)  : self._q = []
    def empty(self)     : return len(self._q) == 0
    def enq(self, t)    : self._q.append(t)
    def deq(self)       : return self._q.pop(0)
}

@lexer::members {
    self._suppressNewlines  = False
    self._lineContinuation  = False
    self._tokens            = TokenQueue()
    self._indents           = IndentStack()

def nextToken(self):
    if not self._tokens.empty():
        return self._tokens.deq()
    else:
        t = super(SimplePythonLexer, self).nextToken()
        if t.type != Token.EOF:
            return t
        else:
            if not self._suppressNewlines:
                self.emitLineBreak()
            self.emitFullDedent()
            self.emitEndToken(t)
            return self._tokens.deq()

def emitEndToken(self, token):
    self._tokens.enq(token)

def emitIndent(self, length=0, text='INDENT'):
    t = self.createToken(SimplePythonParser.INDENT, text, length)
    self._tokens.enq(t)

def emitDedent(self):
    t = self.createToken(SimplePythonParser.DEDENT, 'DEDENT')
    self._tokens.enq(t)

def emitFullDedent(self):
    while not self._indents.empty():
        self._indents.pop()
        self.emitDedent()

def emitLineBreak(self):
    t = self.createToken(SimplePythonParser.LINE_BREAK, 'LINE_BREAK')
    self._tokens.enq(t)

def createToken(self, type_, text="", length=0):
    start = self._tokenStartCharIndex
    stop = start + length
    t = CommonToken(self._tokenFactorySourcePair,
                    type_, self.DEFAULT_TOKEN_CHANNEL,
                    start, stop)
    t.text = text
    return t
}


program : (LINE_BREAK | statement)+ EOF ;

statement : (simple_statement | compound_statement) ;

simple_statement : (assign_statement | call_func | return_statement) LINE_BREAK ;

compound_statement : def_statement | if_statement | for_statement ;

def_statement : DEF ID OPEN_PAREN def_args_list? CLOSE_PAREN COLON statement_list ;

def_args_list : ID (COMMA ID)* ;

statement_list : LINE_BREAK INDENT statement+ DEDENT ;

if_statement : IF expr COLON statement_list (ELSE COLON statement_list)? ;
for_statement : FOR ID IN expr COLON statement_list ;
return_statement : RETURN expr? ;
assign_statement : ID ASSIGN expr ;
call_func : ID OPEN_PAREN args_list? CLOSE_PAREN ;

expr : atom
     | ('+' | '-') expr
     | expr ('*' | '/' | '%') expr
     | expr ('+' | '-') expr
     | expr '==' expr
     ;

atom : INT
     | ID
     | call_func
     | '(' expr ')'
     ;

args_list : expr (COMMA expr)* ;

DEF : 'def' ;
IF : 'if' ;
FOR : 'for' ;
RETURN : 'return' ;
ASSIGN : '=' ;
IN : 'in' ;
COLON : ':' ;
COMMA : ',' ;
ELSE : 'else' ;

OPEN_PAREN : '(' ;
CLOSE_PAREN : ')' ;

INT : [0-9]+ ;
ID : [a-zA-Z_][a-zA-Z0-9_]* ;

LINENDING
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

WHITESPACE
    : ('\t' | ' ')+ {
if (self._tokenStartColumn == 0):
    la = self._input.LA(1)
    if la not in [ord('\r'), ord('\n'), ord('#'), -1]:
        self._suppressNewlines = False
        wsCount = 0
        for ch in self.text:
            if   ch == ' ' : wsCount += 1
            elif ch == '\t': wsCount += 8

        if wsCount > self._indents.wsval():
            self.emitIndent(len(self.text))
            self._indents.push(wsCount)
        else:
            while wsCount < self._indents.wsval():
                self.emitDedent()
                self._indents.pop()
            if wsCount != self._indents.wsval():
                raise Exception()
} -> channel(HIDDEN)
;

COMMENT : '#' ~[\r\n\f]* -> channel(HIDDEN) ;

# Отчет

ФИО: Пержаница Александр Петрович\
Группа: 221703\
Вариант: 12

## Спецификация разработанного языка программирования

#### Объявление функций

```
<RETURN_TYPE> <FUNCTION_NAME>(<PARAM_LIST>):
    <FUNCTION_BODY>

<PARAM_LIST> = <PARAM> (, <PARAM>)*

<PARAM> = &<NAME>
```

#### Объявление переменных:

1. Без инициализации:
```
global? <NAME>;
```

2. С инициализацией:
```
global?<NAME> = <EXPR>;

```

#### Управляющие конструкции:

1. if/else: 
```
if <EXPR>:
    <BODY>
else: 
    <BODY>

```

2. while
```
while <CONDITION>: 
    <BODY>

```

4. for
```
for <EXPR>: 
    <BODY>

```
5.switch
```
switch <EXPR>:
    case <EXPR>: <BODY>
    (case <EXPR>: <BODY>)*
    (default <EXPR>: <BODY>)?

```

#### Вызовы функций:
```
ID(<ARG_LIST>);
```

#### Операции над данными: 

1. Арифметические операции
```
<EXPR> + <EXPR>
<EXPR> - <EXPR>
<EXPR> * <EXPR>
<EXPR> / <EXPR>
|<EXPR>|
```

2. Логические операции
```
<EXPR> and <EXPR>
<EXPR> or <EXPR>
!<EXPR>
```

3. Операции сравнения
```
<EXPR> >  <EXPR>
<EXPR> >= <EXPR>
<EXPR> <  <EXPR>
<EXPR> <= <EXPR>
<EXPR> == <EXPR>
<EXPR> != <EXPR>
```
4. встроенные функции
```
len(arr)- длина вектора, матрицы
matrix(value=n,columns=n,rows=n)-создание матрицы
 ```
#### Типы данных:
```
1. int 
2. bool
3. string
4. vector
5. matrix
6. float
7. Ref
```

## Описание грамматики
```
grammar VecLang;

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
from generated.VecLangParser import VecLangParser

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
    self._openBRCount      = 0
    self._suppressNewlines = False
    self._lineContinuation = False
    self._tokens           = TokenQueue()
    self._indents          = IndentStack()

def nextToken(self):
    if not self._tokens.empty():
        return self._tokens.deq()

    t = super(VecLangLexer, self).nextToken()

    if t.type != Token.EOF:
        return t

    # EOF reached — emit final LINE_BREAK + full DEDENT
    if not self._suppressNewlines:
        self.emitLineBreak()

    self.emitFullDedent()
    self.emitEndToken(t)
    return self._tokens.deq()

def emitEndToken(self, token):
    self._tokens.enq(token)

def emitIndent(self, length=0, text="INDENT"):
    t = self.createToken(VecLangParser.INDENT, text, length)
    self._tokens.enq(t)

def emitDedent(self):
    t = self.createToken(VecLangParser.DEDENT, "DEDENT")
    self._tokens.enq(t)

def emitFullDedent(self):
    while not self._indents.empty():
        self._indents.pop()
        self.emitDedent()

def emitLineBreak(self):
    t = self.createToken(VecLangParser.LINE_BREAK, "LINE_BREAK")
    self._tokens.enq(t)

def createToken(self, type_, text="", length=0):
    start = self._tokenStartCharIndex
    stop = start + length
    t = CommonToken(
        self._tokenFactorySourcePair,
        type_,
        self.DEFAULT_TOKEN_CHANNEL,
        start,
        stop
    )
    t.text = text
    return t
}

/* ---------------------------
   Парсерные правила (объединенные)
   --------------------------- */

program: (LINE_BREAK | statement | functionDecl)* EOF;

statement
    : simple_statement
    | compound_statement
    ;

simple_statement : (assign_statement | call_func  |
                   printStatement | writeStatement |
                   raiseStatement | expression) LINE_BREAK ;

compound_statement : ifStatement | whileStatement | forStatement | switchStatement | functionDecl ;

/* Простые операторы из первой грамматики */
assign_statement : (REF)? ID ASSIGN expression ;
call_func : ID OPEN_PAREN args_list? CLOSE_PAREN ;


/* Управляющие конструкции из обеих грамматик */
ifStatement
    : IF expression COLON statement_list (ELSE COLON statement_list)?
    ;

whileStatement
    : WHILE expression COLON statement_list
    ;

forStatement
    : FOR ID IN expression COLON statement_list
    ;

switchStatement
    : SWITCH expression COLON (CASE expression COLON statement_list)* (DEFAULT COLON statement_list)?
    ;

functionDecl
    : DEF ID OPEN_PAREN parameterList? CLOSE_PAREN COLON statement_list
    ;

parameterList
    : ((REF)? ID) (COMMA (REF)? ID)*
    ;

statement_list
    : LINE_BREAK INDENT statement+ DEDENT
    ;

/* Выражения - объединенный подход */
expression
    : logicalExpr
    | equalityExpr
    ;

logicalExpr
    : equalityExpr ((AND | OR) equalityExpr)*
    ;

equalityExpr
    : relationalExpr ((EQ | NEQ) relationalExpr)*
    ;

relationalExpr
    : additiveExpr ((LT | GT | LE | GE) additiveExpr)*
    ;

additiveExpr
    : multiplicativeExpr ((ADD | SUB) multiplicativeExpr)*
    ;

multiplicativeExpr
    : unaryExpr ((MUL | DIV | MOD) unaryExpr)*
    ;

unaryExpr
    : (ADD | SUB) unaryExpr
    | PIPE expression PIPE
    | postfixExpr
    ;

/* Постфиксные выражения */
postfixExpr
    : primary ( (DOT ID) | OPEN_BRACKET expression CLOSE_BRACKET | OPEN_PAREN argumentList? CLOSE_PAREN )*
    ;

primary
    : OPEN_PAREN expression CLOSE_PAREN
    | literal
    | READ OPEN_PAREN CLOSE_PAREN
    | ID
    | call_func
    | MATRIX OPEN_PAREN argumentList? CLOSE_PAREN   // matrix(...)
    | VECTOR OPEN_PAREN argumentList? CLOSE_PAREN   // vector(...)
    ;

/* Аргументы функций */
args_list : expression (COMMA expression)* ;
argumentList : argument (COMMA argument)* ;
argument
    : ID ASSIGN expression   // named argument
    | expression             // positional argument
    ;

/* Литералы */
literal
    : INT
    | FLOAT
    | STRING
    | vectorLiteral
    | matrixLiteral
    | TRUE
    | FALSE
    ;

vectorLiteral
    : OPEN_PAREN expression (COMMA expression)+ CLOSE_PAREN
    ;

matrixLiteral
    : OPEN_BRACKET ( row (COMMA row)* | expression (COMMA expression)* )? CLOSE_BRACKET
    ;

row
    : OPEN_BRACKET expression (COMMA expression)* CLOSE_BRACKET
    ;

/* Дополнительные операторы */
writeStatement
    : WRITE OPEN_PAREN expression CLOSE_PAREN
    ;

printStatement
    : PRINT OPEN_PAREN expression CLOSE_PAREN
    ;

//readStatement
//    : READ OPEN_PAREN CLOSE_PAREN
//    ;

raiseStatement
    : RAISE ID
    ;

/* Типы */
type
    : VECTOR
    | MATRIX
    | INT_TYPE
    | FLOAT_TYPE
    | STRING_TYPE
    | AUTO
    ;

/* ---------------------------
   Лексерные правила (объединенные)
   --------------------------- */

/* Ключевые слова из обеих грамматик */
DEF         : 'def';
IF          : 'if';
ELSE        : 'else';
WHILE       : 'while';
FOR         : 'for';
IN          : 'in';
SWITCH      : 'switch';
CASE        : 'case';
DEFAULT     : 'default';

WRITE       : 'write';
PRINT       : 'print';
READ        : 'read';
RAISE       : 'raise';
REF         :'&';
TRUE        : 'true';
FALSE       : 'false';

VECTOR      : 'vector';
MATRIX      : 'matrix';
INT_TYPE    : 'int';
FLOAT_TYPE  : 'float';
STRING_TYPE : 'string';
AUTO        : 'auto';

/* Операторы из обеих грамматик */
EQ          : '==';
NEQ         : '!=';
LE          : '<=';
GE          : '>=';
LT          : '<';
GT          : '>';
AND         : 'and';
OR          : 'or';

ASSIGN      : '=';
ADD         : '+';
SUB         : '-';
MUL         : '*';
DIV         : '/';
MOD         : '%';

PIPE        : '|';

/* Скобки и разделители */


COMMA       : ',';
SEMI        : ';';
COLON       : ':';
DOT         : '.';

/* Литералы */
STRING
    : '"' ( ~["\\\r\n] | '\\' . )* '"'
    ;

FLOAT
    : [0-9]+ '.' [0-9]* ([eE] [+-]? [0-9]+)?
    | '.' [0-9]+ ([eE] [+-]? [0-9]+)?
    ;

INT
    : [0-9]+
    ;

/* Идентификаторы */
ID
    : [a-zA-Z_][a-zA-Z_0-9]*
    ;

LINENDING
    : (
        ('\r'? '\n')+ { self._lineContinuation = False }
        | '\\' [ \t]* ('\r'? '\n') { self._lineContinuation = True }
    )
    {
        if self._openBRCount == 0 and not self._lineContinuation:
            if not self._suppressNewlines:
                self.emitLineBreak()
                self._suppressNewlines = True

            la = self._input.LA(1)
            if la not in [ord(' '), ord('\t'), ord('#')]:
                self._suppressNewlines = False
                self.emitFullDedent()
    }
    -> channel(HIDDEN)
    ;

WHITESPACE
    : ('\t' | ' ')+
    {
        if (
            self._tokenStartColumn == 0
            and self._openBRCount == 0
            and not self._lineContinuation
        ):
            la = self._input.LA(1)

            if la not in [ord('\r'), ord('\n'), ord('#'), -1]:
                self._suppressNewlines = False

                wsCount = 0
                for ch in self.text:
                    if ch == ' ': wsCount += 1
                    elif ch == '\t': wsCount += 8

                if wsCount > self._indents.wsval():
                    self.emitIndent(len(self.text))
                    self._indents.push(wsCount)

                else:
                    while wsCount < self._indents.wsval():
                        self.emitDedent()
                        self._indents.pop()

                    if wsCount != self._indents.wsval():
                        raise Exception("Indentation error")
    }
    -> channel(HIDDEN)
    ;

OPEN_PAREN: '(' { self._openBRCount += 1 };
CLOSE_PAREN: ')' { self._openBRCount -= 1 };
OPEN_BRACE: '{' { self._openBRCount += 1 };
CLOSE_BRACE: '}' { self._openBRCount -= 1 };
OPEN_BRACKET: '[' { self._openBRCount += 1 };
CLOSE_BRACKET: ']' { self._openBRCount -= 1 };

COMMENT
    : '#' ~[\r\n]* -> skip
    ;

ML_COMMENT
    : '/*' .*? '*/' -> skip
    ;
```

## Описание разработанных компонентов:

#### Классы
1. `SemanticAnalyzer` - класс выполняет семантический анализ программы VecLang на основе дерева, построенного парсером, а также заполняет контекст, нужный для работы самого семантичесвкого анализатора.
2. `Scope` - класс хранящий область видимости переменных.
3. `SyntaxError` - класс для поиска синтаксических ошибок.
4. `CompilerVisitor` - класс генерирующий из дерева байт-код в .pyc при помощи библиотеки bytecode.
5. `Ref` - класс для работы ссылок в виде чисел, а также матриц и векторов.
6. `Runtime` - файл с реализацие необходимых классов и функций для работы.


## Перечень генерируемых ошибок
1. Необъявленная переменная
2. Необъявленная функция
3. Несовместимые типы для операции
4. Неправильное количество аргументов переданные функцию
5. Неправильные данные для for


## Демонстрация работы
1. Первый пример:

Код:
```
#example1
#find cosinus among two vectors and test for

def cos_vectors(&vec1,&vec2):
    vec1=(|vec1|*|vec2|)/(vec1*vec2)
if __name__=="__main__":
    example_vec1=(1,2,3)
    example_vec2=(1,2,3)
    &ref_example_vec1=example_vec1
    &ref_example_vec2=example_vec2
    cos_vectors(ref_example_vec1,ref_example_vec2)
    print(ref_example_vec1)
    for i in example_vec1:
        print(i)
```

Вывод:
```
1.0
1
2
3
```

1. Второй пример:

Код:
```
#example2
#transform Celcius gradus to Kelvin and test while

def transform_to_Kelvin(&celcius):
    kelvin=matrix(value=273,columns=len(celcius),rows=1)
    celcius=celcius+kelvin
    i=0
    while i<len(celcius):
        print(celcius[0][i])
        i=i+1
if __name__=="__main__":
    gradus=[20,30,40]
    &ref_gradus=gradus
    transform_to_Kelvin(ref_gradus)
    print(ref_gradus)
```

Вывод:
```
293
303
313
[[293, 303, 313]]
```

1. Третий пример:

Код:
```
#example3
#rotation matrix on 90 degrees

def rotation_90(&mat):
    mat_rotation=[[0,-1],
                  [1,0]]
    if (mat.n_cols!=2 and mat.n_rows!=2):
        raise Expectation
    mat=mat*mat_rotation
if __name__=="__main__":
    mat=[[1,1],[1,1]]
    &ref_mat=mat
    rotation_90(ref_mat)
    print(ref_mat)
```

Вывод:
```
[[1, -1], [1, -1]]
```

1. Пример с семантической ошибкой:

Код:
```
def rotation_90(&mat):
    mat_rotation=[[0,-1],
                  [1,0]]
    if (mat.n_cols!=2 and mat.n_rows!=2):
        raise Expectation
    mat=mat*mat_rotation
if __name__=="__main__":
    mat=[[1,1],[1,1]]
    &ref_mat=mat
    rotation_90(ref_mat, mat)# not correct number argument
    print(ref_mat)
```

Вывод:
```
Line 13: Функция 'rotation_90' ожидает 1 аргументов, получено 2
```
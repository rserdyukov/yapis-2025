# Отчет

ФИО: Гаврилович Алиса Юрьевна\
Группа: 221703\
Вариант: 4

## Спецификация разработанного языка программирования
#### Синтаксис объявления переменных:

 `<VAR_NAME> = <EXPRESSION>;`

#### Синтаксис объявления подпрограмм:

```
function <FUNCTION_NAME> (<PARAM_TYPE> <PARAM_NAME>, ...) -> <RETURN_TYPE>: 
    <FUNCTION_BODY>
```

#### Синтаксис управляющих конструкций:
1. for-statement:
```
for <ITERATION_VARIABLE> in range(<MIN_VALUE>, <MAX_VALUE>, <STEP>):
    <FOR_BODY>
```

1. while-statement:
```
while (<WHILE_CONDITION>): 
    <WHILE_BODY>
```

3. if-else-statement:
```
if (<IF_CONDITION>):
    <IF_BODY>
else:
    <ELSE_BODY>
```

4. switch-statement:
```
switch <SWITCH_PARAMETER> 
    case <CASE_PARAMETER_1>:
        <CASE_BODY>;
    
    case <CASE_PARAMETER_2>:
        <CASE_BODY>;
    
    ...
    
    case <CASE_PARAMETER_N>:
        <CASE_BODY>;
    
    default:
        <DEFAULT_BODY>;
```

#### Синтаксис операций над данными:
1. Добавление элемента в множество: `<SET>=add(<SET>,<ELEMENT>|<SET>|<TUPLE>)`
2. Добавление элемента в кортеж: `<TUPLE>=add(<TUPLE>,<ELEMENT>|<SET>|<TUPLE>)`
3. Удаление элемента из множества: `<SET>=delete(<SET>,<ELEMENT>|<SET>|<TUPLE>)`
4. Удаление элемента из кортежа: `<TUPLE>=delete(<TUPLE>,<ELEMENT>|<SET>|<TUPLE>)`
5. Вычисление количества элементов множества: `<INT>=len(<SET>)`
6. Вычисление количества элементов кортежа: `<INT>=len(<TUPLE>)`
7. Вычисление количества вхождений элемента в кортеж: `<INT>=count(<TUPLE>,<ELEMENT>|<SET>|<TUPLE>)`
8. Проверка вхождения элемента во множество: `<BOOL>=includes(<SET>,<ELEMENT>|<SET>|<TUPLE>)`
9. Проверка вхождения элемента в кортеж: `<BOOL>=includes(<TUPLE>,<ELEMENT>|<SET>|<TUPLE>)`
10. Операция вывода на экран: `print(<EXPR>)`
11. Арифметические операции:
    1. Для целочисленных значений:
        1. Сложение: `<INT> + <INT>`
        2. Умножение: `<INT> * <INT>`
        3. Разность: `<INT> - <INT>`
        4. Деление: `<INT> / <INT>`
    2. Для множеств:
        1. Объединение: `<SET> + <SET>`
        2. Пересечение: `<SET> * <SET>`
        3. Разность: `<SET> - <SET>`
        4. Симметрическая разность: `<SET> / <SET>`
    3. Для кортежей
        1. Объединение: `<TUPLE> + <TUPLE>`
        2. Пересечение: `<TUPLE> * <TUPLE>`
        3. Разность: `<TUPLE> - <TUPLE>`
        4. Симметрическая разность: `<TUPLE> / <TUPLE>`
    4. Для строк
        1. Конкатенация: `<STRING> + <STRING>`
12. Логические операции:
    1. Логическое ИЛИ: `<EXPR> || <EXPR>`
    2. Логическое И: `<EXPR> && <EXPR>`
    3. Логическое НЕ: `!<EXPR>`
14. Операции сравнения: 
    1. Для целочисленных значений:
        1. Больше: `<INT> > <INT>`
        2. Больше или равно: `<INT> >= <INT>`
        3. Меньше: `<INT> < <INT>`
        4. Меньше или равно: `<INT> <= <INT>`
        5. Равно: `<INT> == <INT>`
        6. Не равно: `<INT> != <INT>`
    2. Для множеств:
        1. Строгое подмножество: `<SET> > <SET>` или `<SET> < <SET>`
        2. Нестрогое подмножество `<SET> >= <SET>` или `<SET> <= <SET>`
        3. Равно: `<SET> == <SET>`
        4. Не равно: `<SET> != <SET>`
    3. Для кортежей
        1. Строгое подмножество: `<TUPLE> > <TUPLE>` или `<TUPLE> < <TUPLE>`
        2. Нестрогое подмножество `<TUPLE> >= <TUPLE>` или `<TUPLE> <= <TUPLE>`
        3. Равно: `<TUPLE> == <TUPLE>`
        4. Не равно: `<TUPLE> != <TUPLE>`

#### Типы данных:
1. Множество Set (элементы не повторяются)
2. Кортеж Tuple (элементы могут повторяться)
3. Элемент целочисленного типа ElementInt
4. Элемент строкового типа ElementStr
5. Элемент логического типа ElementBool
  

## Описание грамматики
```
grammar SetLang;

tokens { INDENT, DEDENT }

// -----------------------------------------------
// ОБРАБОТКА ОТСТУПОВ
// -----------------------------------------------
@lexer::members {
  private java.util.LinkedList<Token> tokens = new java.util.LinkedList<>();
  private java.util.Stack<Integer> indents = new java.util.Stack<>();
  private int opened = 0;
  private Token lastToken = null;
  @Override
  public void emit(Token t) {
    super.setToken(t);
    tokens.offer(t);
  }

  @Override
  public Token nextToken() {
    if (_input.LA(1) == EOF && !this.indents.isEmpty()) {
      for (int i = tokens.size() - 1; i >= 0; i--) {
        if (tokens.get(i).getType() == EOF) {
          tokens.remove(i);
        }
      }

      this.emit(commonToken(SetLangParser.NEWLINE, "\n"));

      while (!indents.isEmpty()) {
        this.emit(createDedent());
        indents.pop();
      }

      this.emit(commonToken(SetLangParser.EOF, "<EOF>"));
    }

    Token next = super.nextToken();

    if (next.getChannel() == Token.DEFAULT_CHANNEL) {
      this.lastToken = next;
    }

    return tokens.isEmpty() ? next : tokens.poll();
  }

  private Token createDedent() {
    CommonToken dedent = commonToken(SetLangParser.DEDENT, "");
    dedent.setLine(this.lastToken.getLine());
    return dedent;
  }

  private CommonToken commonToken(int type, String text) {
    int stop = this.getCharIndex() - 1;
    int start = text.isEmpty() ? stop : stop - text.length() + 1;
    return new CommonToken(this._tokenFactorySourcePair, type, DEFAULT_TOKEN_CHANNEL, start, stop);
  }
  static int getIndentationCount(String spaces) {
    int count = 0;
    for (char ch : spaces.toCharArray()) {
      switch (ch) {
        case '\t':
          count += 8 - (count % 8);
          break;
        default:
          // A normal space char.
          count++;
      }
    }

    return count;
  }

  boolean atStartOfInput() {
    return super.getCharPositionInLine() == 0 && super.getLine() == 1;
  }
}

program
    : (NEWLINE|statement)* EOF
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА
// -----------------------------------------------
statement
    : variableDeclaration
    | functionCall
    | returnStatement
    | breakStatement
    | functionDeclaration
    | ifStatement
    | forStatement
    | whileStatement
    | switchStatement
    |emptyLine
    ;
emptyLine: NEWLINE;

// Декларация переменной
variableDeclaration
    : ID ASSIGN expr (NEWLINE | EOF)
    ;

// Декларация функции
functionDeclaration
    : FUNCTION ID LRBRACKET paramList? RRBRACKET returnType COLON block
    ;

paramList
    : types+=type args+=ID (COMMA types+=type args+=ID)*
    ;

returnType
    :'->' type
    ;

// Оператор if-else
ifStatement
    : IF logicalExpr COLON then_=block (ELSE COLON else_=block)?
    ;
// Оператор switch-case-default
switchStatement
    : SWITCH ID COLON NEWLINE INDENT caseBlock+ (defaultblock)? DEDENT
    ;

caseBlock
    : CASE (ID|INT) COLON block
    ;

defaultblock
    : DEFAULT COLON block
    ;

// Оператор while
whileStatement
    : WHILE logicalExpr COLON block;

// Оператор for
forStatement
    : FOR ID IN RANGE LRBRACKET range RRBRACKET COLON block;

range: min=(ID|INT) COMMA max=(ID|INT) COMMA step=(ID|INT);

// Оператор return
returnStatement: RETURN expr (NEWLINE | EOF);

// Оператор break
breakStatement: BREAK (NEWLINE | EOF);

// Блок функции и управляющих конструкций 
block: NEWLINE INDENT statement+ DEDENT;

// Вызов функции
functionCall: ID LRBRACKET exprList? RRBRACKET;

exprList
    : expr (COMMA expr)*
    ;

expr: simpleExpr | complexExpr | functionCall | comparisonExpr| logicalExpr ;

// Логическое выражения
logicalExpr
    : NOT? logicalOperand
    | NOT? LRBRACKET left=logicalExpr op=(AND | OR) right=logicalExpr RRBRACKET
    ;

logicalOperand
    : 'true'
    | 'false'
    | ID
    | comparisonExpr
    ;

// Выражение сравнения
comparisonExpr
    : LRBRACKET left=expr op=(LT | GT | LE | GE | EQUAL | NEQUAL) right=expr RRBRACKET
    ;

// Арифметическое выражение
complexExpr
    : simpleExpr
    | LRBRACKET left=complexExpr op=(PLUS | MINUS | UN | DIFF  )  right=complexExpr RRBRACKET;

// Правило для обозначения множества
setLiteral: LFIGBRACKET simpleExprList? RFIGBRACKET   ;

// Правило для обозначение кортежа
tupleLiteral: LSQBRACKET simpleExprList? RSQBRACKET;

simpleExpr
    : setLiteral
    | tupleLiteral
    | element
    | ID
    ;

simpleExprList: simpleExpr (COMMA simpleExpr)*;

// Правило для обозначения элемента
element
    : INT
    | 'true'
    | 'false'
    | STRING
    ;

// Типы данных
type: ELEMENTSTR| ELEMENTINT| ELEMENTBOOL |SET| TUPLE |VOID;


// -----------------------------------------------
// ПРАВИЛА ЛЕКСЕРА
// -----------------------------------------------

RANGE: 'range';
FUNCTION: 'function' ;
IF: 'if' ;
ELSE: 'else' ;
FOR: 'for' ;
IN: 'in';
WHILE: 'while' ;
SWITCH: 'switch' ;
CASE: 'case' ;
DEFAULT: 'default';
BREAK: 'break' ;
RETURN: 'return';
ELEMENTSTR: 'ElementStr';
ELEMENTINT: 'ElementInt';
ELEMENTBOOL: 'ElementBool';
SET: 'Set';
TUPLE: 'Tuple';
VOID: 'void';

ID: [a-zA-Z][a-zA-Z0-9$_]* ;
INT: [0-9]+ ;
STRING: '"' (~["\\\r\n] | '\\' .)* '"' ;

QUESTION: '?' ;
LT: '<' ;
GT: '>';
LE: '<=' ;
GE: '>=' ;
EQUAL: '==' ;
NEQUAL: '!=' ;
AND: '&&' ;
OR: '||' ;
NOT: '!' ;

LSQBRACKET: '[' { this.opened += 1 } ;
RSQBRACKET: ']' { this.opened -= 1 } ;
LRBRACKET: '(' { this.opened += 1 } ;
RRBRACKET: ')' { this.opened -= 1 } ;
LFIGBRACKET: '{' { this.opened += 1 } ;
RFIGBRACKET: '}' { this.opened -= 1 } ;

SEMICOLON: ';' ;
COLON: ':' ;
COMMA: ',' ;
POINT: '.';
ASSIGN: '=' ;
DIFF: '/' ;
PLUS: '+' ;
MINUS: '-' ;
UN: '*' ;

LINE_COMMENT: '#' ~[\r\n]* -> skip;
WS: [ \t]+ -> skip;

NEWLINE
 : ( {atStartOfInput()}?   WS
   | ( '\r'? '\n' | '\r' ) WS?
   )
   {
     String newLine = getText().replaceAll("[^\r\n]+", "");
     String spaces = getText().replaceAll("[\r\n]+", "");
     int next = _input.LA(1);
     if (opened > 0 || next == '\r' || next == '\n' || next == '#') {
       skip();
     }
     else {
       emit(commonToken(NEWLINE, newLine));
       int indent = getIndentationCount(spaces);
       int previous = indents.isEmpty() ? 0 : indents.peek();
       if (indent == previous) {
         skip();
       }
       else if (indent > previous) {
         indents.push(indent);
         emit(commonToken(SetLangParser.INDENT, spaces));
       }
       else {
         while(!indents.isEmpty() && indents.peek() > indent) {
           this.emit(createDedent());
           indents.pop();
         }
       }
     }
   }
 ;
```

## Описание разработанных классов
1. Класс для синтаксического анализа SyntaxAnalyzer. Класс производит синтаксический анализ поданного на вход исходного кода с помощью грамматики.
2. Класс для семантического анализа SemanticAnalyzer. Класс производит семантический анализ поданного на вход исходного кода.
3. Класс для перевода в целевой код CILGenerator. Класс производит перевод AST/ParseTree в Common Intermediate Language.
4. Класс среды выполнения Ops. Класс предоставляет методы для объединения, пересечения, разности, симметрической разности, 
а также определения подмножества, надмножества, равенства и неравенства множеств и кортежей.
5. Класс для компиляции кода Main. Класс последовательно с помощью выше перечисленных классов выполняет синтаксический и семантический анализ, трансляцию в CIL, а затем преобразование в байт-код .NET и запуск .exe файла.

## Перечень генерируемых ошибок
1. Синтаксические ошибки. Ошибки в семантике исходного кода, проверяются с помощью класса `SyntaxAnalyzer`.
2. Семантические ошибки. Ошибки в семантике исходного кода, проверяются с помощью класса `SemanticAnalyzer`.
    - `Проверка области видимости (область видимости переменной ограничивается подпрограммой)`
    - `Использование необъявленной переменной,функции`
    - `Неправильно переданы аргументы в функцию (неверное количество)`
    - `Код после return/break`
    - `Перегрузка функций`
    - `Использование break вне for,switch,while`
    - `Операции +,-,*,/,/\,<,>,<=,>=,!=,== между разными типами`
    - `Использование не int значений в range`
    - `Использование не int значений в case, switch`
    - `Использование не логических выражений в if, while`

## Демонстрация работы
1. Демонстрация операций над множествами и кортежами:

Код:
```
a = {1, 2, 3}           # множество (Set)
b = {3, 4, 5}           # множество (Set)

c = (a + b)             # объединение множеств
d = (a - b)             # разность множеств
e = (a * b)             # пересечение множеств
f = (a / b)             # симметрическая разность множеств

k = [1,5,5,2]           # кортеж (Tuple)
m= [1,2,3]              # кортеж (Tuple)
g=(k + m)               # объединение кортежей

x="abc"                 # элемент множества (Element)
y=4                     # элемент множества (Element)
a=add(a,x)              # включение элемента в множество
b=delete(b,y)           # удаление элемента из множества
l=includes(f,4)
p=includes(f,"hello")
h=count(k,5)		    # количество вхождений элемента в кортеж
j=len(a)		        # размер множества
print(a)                # {1, 2, 3, 'abc'}
print(b)                # {3, 5}
print(c)                # {1, 2, 3, 4, 5}
print(d)                # {1, 2}
print(e)                # {3}
print(f)                # {1, 2, 4, 5}
print(g)                # <1,5,5,2,1,2,3>
print(h)  		        # 2
print(j)  		        # 4
print(l)  		        # true
print(p)  		        # false
```

Вывод:
```
{1, 2, 3, "abc"}
{3, 5}
{1, 2, 3, 4, 5}
{1, 2}
{3}
{1, 2, 4, 5}
[1, 5, 5, 2, 1, 2, 3]
2
4
true
false
```

2. Демонстрация работы операторов if-else, switch-case-default.

Код:
```
function func1(Set s1, Set s2, ElementInt el)->Set:
    z = includes(s1, el)
    y_local = includes(s2, el)
    if (z && y_local):
        s1 = delete(s1, el)
        s2 = delete(s2, el)
    switch el:
        case 1:
            return add(s1, s2)
        case 2:
            return add(s2, s1)
        default:
            return s1

a = {1, 2, 5, "a", 34, "hello", {"6", 7, "8"}}
b = {56, 77, "abababa", "11110", 1, 9, 8}
y = 1

c = func1(a, b, y)
y = 2
d = func1(a, b, y)
y = 3
e = func1(a, b, y)

print(c)
print("------------------")
print(d)
print("------------------")
print(e)
```

Вывод:
```
{{56, 77, "abababa", "11110", 9, 8}, 2, 5, "a", 34, "hello", {"6", 7, "8"}}
"------------------"
{56, 77, "abababa", "11110", 1, 9, 8, {1, 2, 5, "a", 34, "hello", {"6", 7, "8"}}}
"------------------"
{1, 2, 5, "a", 34, "hello", {"6", 7, "8"}}
```

3. Демонстрация работы оператора for.

Код:
```
coords = []
for row in range(1, 4, 1):
    for col in range(1, 4, 1):
        pair = [row, col]
        coords = add(coords, pair)

print(coords)
}

```

Вывод:
```
[[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3], [3, 1], [3, 2], [3, 3]]
```

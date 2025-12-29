# Отчет

ФИО: Воложинец Архип Александрович\
Группа: 221703\
Вариант: 5

## Спецификация разработанного языка программирования
#### Синтаксис объявления переменных:

1. Без присваивания: `<TYPE> <VAR_NAME>;`
2. Без присваивания(для arc): `arc = <a,b>;`

#### Синтаксис объявления подпрограмм:

```
function <FUNCTION_NAME> (
    <PARAM_TYPE_1> <PARAM_NAME_1>, ..., <PARAM_TYPE_N> <PARAM_NAME_N>, 
    <RESULT_PARAM_TYPE_1> ?<RESULT_PARAM_NAME_1>, ... <RESULT_PARAM_TYPE_N> ?<RESULT_PARAM_NAME_N>
) {
    <FUNCTION_BODY>
}
```

#### Синтаксис управляющих конструкций:

1. for-statement:
```
for (<ITERATION_VARIABLE> : <COLLECTION>) {
    <FOR_BODY>
}
```

3. if-else-statement:
```
if (<IF_CONDITION>) {
    <IF_BODY>
} else {
    <ELSE_BODY>
}
```

4. switch-statement:
```
switch (<SWITCH_PARAMETER>) {
    case <CASE_PARAMETER_1>:
        <CASE_BODY>;
    
    case <CASE_PARAMETER_2>:
        <CASE_BODY>;
    
    ...
    
    case <CASE_PARAMETER_N>:
        <CASE_BODY>;
    
    default:
        <DEFAULT_BODY>;
}
```

#### Синтаксис операций над данными:
1. Добавление узла в граф: `<GRAPH> * <NODE>`
2. Удаление узла из графа: `<GRAPH> / <NODE>`
3. Добавление связи в граф: `<GRAPH> + <ARC>`
4. Удаление связи из графа: `<GRAPH> - <ARC>`
5. Поиск в ширину: `BFS(<GRAPH>, <NODE>)`
6. Поиск в глубину: `DFS(<GRAPH>, <NODE>)`
8. Операция вывода на экран: `print(<EXPR>)`
9. Операция вывода имени графа на экран: `print(<GRAPH>)`
10. Операция вывода полной информации о графе на экран: `print(<GRAPH>, "%d")`
12. Логические операции:
    1. Логическое ИЛИ: `<EXPR> || <EXPR>`
    2. Логическое И: `<EXPR> && <EXPR>`
    3. Логическое НЕ: `!<EXPR>`
14. Операции сравнения: 
    1. Больше: `<EXPR> > <EXPR>`
    2. Больше или равно: `<EXPR> >= <EXPR>`
    3. Меньше: `<EXPR> < <EXPR>`
    4. Меньше или равно: `<EXPR> <= <EXPR>`
    5. Равно: `<EXPR> == <EXPR>`
    6. Не равно: `<EXPR> != <EXPR>`

## Описание грамматики
```
grammar GraphLang;

program
    : (functionDeclaration | topLevelStatement | statement)* EOF
    ;

// -----------------------------------------------
// БАЗОВЫЕ ПРАВИЛА ПАРСЕРА (ТОП-LEVEL)
// -----------------------------------------------

// Топ-уровневые инструкции (объявления нод/дуг/графа)
topLevelStatement
    : nodeDecl
    | arcDecl
    | graphDecl
    ;

// Объявление ноды:  node <ID>;
nodeDecl
    : NODE ID SEMICOLON
    ;

// Объявление дуги литералом: arc < <ID, ID> >;
arcDecl
    : ARC arcLiteral SEMICOLON
    ;

// Объявление графа: graph <ID>;
graphDecl
    : GRAPH ID SEMICOLON
    ;

// Литерал дуги — тройка: <from, to>
arcLiteral
    : LT ID COMMA ID GT
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ФУНКЦИЙ
// -----------------------------------------------

// Объявление функции: void <ID>( params? ) { ... }
functionDeclaration
    : VOID ID LRBRACKET functionParamList? RRBRACKET block
    ;

// Параметр функции: <type> <ID>
functionParam
    : type ID
    ;

// Список параметров: p, p, p
functionParamList
    : functionParam (COMMA functionParam)*
    ;

// Тип в сигнатуре — может быть ключевым типом (node/graph/arc) или именованным типом (ID)
type
    : NODE
    | GRAPH
    | ARC
    | ID
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ВЫРАЖЕНИЙ
// (от более высокого приоритета к меньшему)
// -----------------------------------------------

// Корневое правило выражения; леворекурсивная запись обеспечивает бинарные операции
expr
    : primary                                                              #primaryExpr_
    | expr (MULT | DIV) expr                                               #mulDivExpr_
    | expr (PLUS | MINUS) expr                                             #addSubExpr_
    | expr (EQ | NEQ | LT | LE | GT | GE) expr                             #compExpr_
    | expr AND expr                                                        #andExpr_
    | expr OR expr                                                         #orExpr_
    ;

// Примитивы, вызовы, группы и т.п.
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

// Вызов функции: id(arg1, arg2)
funcCall
    : ID LRBRACKET argList? RRBRACKET
    ;

// Группа нод: (a, b, c)
nodeGroup
    : LRBRACKET nodeGroupInner RRBRACKET
    ;

// Внутренности группы нод: ID, ID, ID...
nodeGroupInner
    : ID COMMA ID (COMMA ID)*
    ;

// Доступ к полям/методам: start (. element)*
memberAccess
    : accessStart ( DOT accessElement )*
    ;

// Начало доступа — идентификатор (например имя переменной/объекта)
accessStart
    : ID
    ;

// Элемент доступа может быть именем или вызовом: name or name(...)
accessElement
    : ID ( LRBRACKET argList? RRBRACKET )?
    ;

// Список аргументов в вызове: expr, expr, ...
argList
    : expr (COMMA expr)*
    ;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА ДЛЯ ИНСТРУКЦИЙ / СТАТЕМЕНТОВ
// -----------------------------------------------

// Выражение как инструкция: expr;
exprStatement
    : expr SEMICOLON
    ;

// Присвоение: id|memberAccess = expr;
assignmentStatement
    : (ID | memberAccess) ASSIGN expr SEMICOLON
    ;

// Объявление переменной (верхнего уровня): node id; | graph id;
varDeclarationStatement
    : NODE ID SEMICOLON
    | GRAPH ID SEMICOLON
    ;

// Объявление дуги как инструкция: arc <a,b>;
arcDeclarationStatement
    : ARC arcLiteral SEMICOLON
    ;

// Условие if (expr) { ... } (else { ... })?
ifStatement
    : IF LRBRACKET expr RRBRACKET block (ELSE block)?
    ;

// Конструкция for-each: for ( <type> id : expr ) { ... }
forEachStatement
    : FOR LRBRACKET type ID COLON expr RRBRACKET block
    ;

// Switch: switch(expr) { ... }
switchStatement
    : SWITCH LRBRACKET expr RRBRACKET LFIGBRACKET switchBlock* RFIGRACKET
    ;

// Блок switch — либо case label: statements, либо "простая" инструкция в теле
switchBlock
    : CASE caseLabel COLON statement*
    | statement
    ;

// Метка case: может быть ID, STRING или INT
caseLabel
    : ID
    | STRING
    | INT
    ;

// Печать: print(argList?)
printStatement
    : PRINT LRBRACKET argList? RRBRACKET SEMICOLON
    ;

// Общее правило statement (с альтернативами)
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

// -----------------------------------------------
// ПРАВИЛА ДЛЯ БЛОКОВ
// -----------------------------------------------

// Блок кода: { statement* }
block
    : LFIGBRACKET statement* RFIGRACKET
    ;

// -----------------------------------------------
// ПРАВИЛА ЛЕКСЕРА
// -----------------------------------------------

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

// Сравнения и логика (длинные формы определены до коротких, чтобы избежать конфликтов)
EQ          : '==' ;
NEQ         : '!=' ;
LE          : '<=' ;
GE          : '>=' ;
AND         : '&&' ;
OR          : '||' ;
INTDIV      : '//' ;

// Символы пунктуации и операторы
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

// Идентификатор (буква или подчёркивание, далее буквы/цифры/подчёрки)
ID
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

// Пробелы и комментарии (пропускаются)
WS
    : [ \t\r\n\u000C]+ -> skip
    ;

LINE_COMMENT
    : '//' ~[\r\n]* -> skip
    ;

BLOCK_COMMENT
    : '/*' .*? '*/' -> skip
    ;
```

## Описание разработанных классов
1. Класс для семантического анализа GraphLangSemanticAnalyzer. Класс производит семантический анализ поданного на вход исходного кода.
2. Класс для перевода в целевой код GraphLangCodeGenerator. Класс производит перевод AST/ParseTree в целевой C‑код (включая вставку рантайма).
3. Класс(ы) для представления ошибок: SyntaxException / SemanticException. Классы хранят информацию об ошибках исходного кода (синтаксическая / семантическая).
4. Класс для представления переменной VariableSymbol. Класс хранит информацию о переменной из исходного кода (имя, тип и т.п.).
5. Класс (интерфейс) для представления типизированного значения Symbol / GraphLangType. Symbol предоставляет метод type(), а GraphLangType — перечисление доступных типов.

## Перечень генерируемых ошибок
1. Синтаксические ошибки. Ошибки в синтаксисе исходного кода, проверяются с помощью грамматики.
2. Семантические ошибки. Ошибки в семантике исходного кода, проверяются с помощью класса `GraphLangSemanticAnalyzer`.
   1. Повторное объявление переменной
   2. Использование необъявленного идентификатора
   3. Обращение к функции как к переменной
   4. Неизвестный тип в объявлении параметров функций
   5. Неправильный тип параметра цикла
   6. Несовместимость типов при присваивании.
   7. Некорректные операции: +, -, *, / между неподдерживаемыми типами, логические (&&, ||) с не-boolean операндами
   8. Группы узлов могут содержать только переменные типа node
   9. Условие if обязано иметь тип boolean
   10. В switch тип метки case должен быть совместим с типом выражения switch
   11. Повторное определение функции
   12. Неизвестная функция при вызове
   13. Несовпадение числа аргументов и несовместимость типов аргументов
   14. Неверное количество или типы аргументов
   15. Повторное объявление параметров функции
   16. Скрытие переменной с тем же именем.

## Демонстрация работы
1. Демонстрация операций над графами, а также варианты вывода:

Код:
```
node a;
node b;
node c;

arc <a,b>;
arc <b,c>;

graph G;
G = G * b; // Добавление узла a в граф G
G = G / b; // Удаление узла b из графа G
G = G * (a,b,c); // Добавление группы узлов a,b,c в граф G
G = G + <b,c> + <a,b>; // Добавление связи в граф (связь между B и C)
G = G - <a,b>; // Удаление связи из графа (узлы B и C остаются)

print(a, " ");
print(b, " ");
print(c, "\n");
print(G, "%d"); // выводит полную информацию о графе
```

Вывод:
```
a b c
Graph(nodes=(a,b,c), arcs=(<b,c>))
```

2. Демонстрация работы функций BFS, DFS.

Код:
```
node A;
node B;
node C;
node D;
node E;

arc <A,B>;
arc <A,C>;
arc <B,D>;
arc <C,E>;

graph G;
G = G * (A,B,C,D,E);
G = G + <A,B> + <A,C> + <B,D> + <C,E>;

print(BFS(G,A), "\n");
print(DFS(G,A), "\n");

void delNode(graph G, node B) {
    if (G.hasNode(B)) {
        G = G / B;
    }
}

delNode(G,B);

print(G, "%d");
```

Вывод:
```
(A,B,C,D,E)
(A,B,D,C,E)
Graph(nodes=(A,C,D,E), arcs=(<A,C>,<C,E>))
```

3. Демонстрация работы for, switch.

Код:
```
node a;
node b;
node c;
node d;

arc <a,b>;
arc <a,d>;
arc <c,d>;

graph G;
G = G*(a,b,c,d);
G = G + <a,b> + <a,d> + <c,d>;

void checkGraph(graph G) {
    print("Graph ", G, " have nodes: ");
    for (node temp : G) {
        switch(temp) {
            case a:
                print(temp, ", ");
            case b:
                print(temp, ", ");
            case c:
                print(temp, ", ");
            case d:
                print(temp,".\n");
        }
    }
}

checkGraph(G);
```

Вывод:
```
Graph G have nodes: a, b, c, d.
```
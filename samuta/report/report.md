# Отчет

ФИО: Самута Даниил Владимирович\
Группа: 221703\
Вариант: 13

## Спецификация разработанного языка программирования

#### Объявление функций

```
<RETURN_TYPE> <FUNCTION_NAME>(<PARAM_LIST>) {
    <FUNCTION_BODY>
}

<PARAM_LIST> = <PARAM> (, <PARAM>)*

<PARAM> = <TYPE> <NAME>
```

#### Объявление переменных:

1. Без инициализации:
```
global? <TYPE> <NAME>;
```

2. С инициализацией:
```
global? <TYPE> <NAME> = <EXPR>;
```

3. Множественное объявление
```
global? <TYPE?> <ID> (',' <ID>)*
```

4. Множественная инициализация
```
global? <ID> (',' <ID>)* '=' <EXPR> (',' <EXPR>)*
```

#### Управляющие конструкции:

1. if/else: 
```
if (<EXPR>) {
    <BODY>
} else {
    <BODY>
}
```

2. while
```
while (<CONDITION>) {
    <BODY>
}
```

3. until
```
until (<CONDITION>) {
    <BODY>
}
```

4. for
```
for (<INIT>; <COND>; <UPDATE>) {
    <BODY>
}
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
```

2. Логические операции
```
<EXPR> && <EXPR>
<EXPR> || <EXPR>
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

4. Операции инкремента
```
++<EXPR>
--<EXPR>
<EXPR>++
<EXPR>--
```

5. Операция каста 
```
(<TYPE>) <EXPR>
```

6. Литералы графовых структур
```
node(<EXPR>)
arc(<EXPR>, <EXPR>)
graph([ <NODE_LIST>? ], [ <ARC_LIST>? ])
```

#### Типы данных:
```
1. int 
2. boolean
3. string
4. node
5. graph
6. arc
```

## Описание грамматики
```
grammar Gsl;

// ---------------------------
// Программа состоит из набора функций
// ---------------------------
program
    : function* EOF
    ;

// ---------------------------
// Объявление функции: сигнатура + тело
// ---------------------------
function
    : head body
    ;

// ---------------------------
// Заголовок функции: <type> <name>(<parameters>)
// ---------------------------
head
    : type ID '(' parameterList? ')'
    ;

// ---------------------------
// Тело функции: последовательность операторов в блоке
// ---------------------------
body
    : '{' op* '}'
    ;

// ---------------------------
// Список параметров функции
// ---------------------------
parameterList
    : parameter (',' parameter)*
    ;

// ---------------------------
// Параметр функции
// ---------------------------
parameter
    : ('out')? type ID
    ;

// ---------------------------
// Все возможные операторы (statement)
// ---------------------------
op
    : opAssign ';'         // присваивание
    | opReturn ';'         // return
    | opDeclare            // объявление переменной
    | opGlobal ';'         // глобальное объявление
    | opMethodCall ';'     // вызов функции
    | opIf                 // if / else / else if
    | opFor                // цикл for
    | opWhile              // цикл while
    | opUntil              // цикл until
    | opExpr ';'           // выражение как оператор
    ;

// ---------------------------
// Объявление глобальной переменной
// ---------------------------
opGlobal
    : 'global' (type ID ('=' expr)? (',' type? ID ('=' expr)?)*)
    ;

// ---------------------------
// Присваивание: <vars> = <exprList>
// ---------------------------
opAssign
    : leftAssign '=' exprList
    ;

// ---------------------------
// Список выражений для множественного присваивания
// ---------------------------
exprList
    : expr (',' expr)*
    ;

// ---------------------------
// Объявление переменных.
// ---------------------------
opDeclare
    : leftAssign ';'
    ;

// ---------------------------
// Список переменных: может содержать тип только у первой
// ---------------------------
leftAssign
    : (type? ID) (',' (type? ID))*
    ;

// ---------------------------
// Оператор return
// ---------------------------
opReturn
    : 'return' expr?
    ;

// ---------------------------
// Вызов функции как отдельный оператор
// ---------------------------
opMethodCall
    : ID '(' argList? ')'
    ;

// ---------------------------
// Оператор — любое выражение
// ---------------------------
opExpr
    : expr
    ;

// ---------------------------
// if / else / else if
// ---------------------------
opIf
    : 'if' '(' expr ')' body ( 'else' opIf )?      // else if
    | 'if' '(' expr ')' body ('else' body)?        // else
    ;

// ---------------------------
// while (<expr>) <body>
// ---------------------------
opWhile
    : 'while' '(' expr ')' body
    ;

// ---------------------------
// until (<expr>) <body>
// Выполнять пока условие ложно
// ---------------------------
opUntil
    : 'until' '(' expr ')' body
    ;

// ---------------------------
// for(init; cond; update) body
// ---------------------------
opFor
    : 'for' '(' opAssign? ';' expr? ';' (opAssign | opExpr)? ')' body
    ;

// ---------------------------
// Список аргументов функции
// ---------------------------
argList
    : expr (',' expr)*
    ;

// ---------------------------
// Выражения (в порядке убывания приоритета)
// ---------------------------
expr
    : expr OR expr        #orExpr
    | expr AND expr       #andExpr
    | expr EQ expr        #eqExpr
    | expr NEQ expr       #neqExpr
    | expr LT expr        #ltExpr
    | expr LE expr        #leExpr
    | expr GT expr        #gtExpr
    | expr GE expr        #geExpr
    | expr PLUS expr      #addExpr
    | expr MINUS expr     #subExpr
    | expr MUL expr       #mulExpr
    | expr DIV expr       #divExpr
    | prefixExpr          #prefixOpExpr
    | postfixExpr         #postfixOpExpr
    | primary             #primaryExpr
    ;

// ---------------------------
// Префиксные операции: ++x, --x, !x
// ---------------------------
prefixExpr
    : (INC | DEC | NOT) expr
    ;

// ---------------------------
// Постфиксные операции: x++, x--
// ---------------------------
postfixExpr
    : primary (INC | DEC)
    ;

// ---------------------------
// Базовые выражения
// ---------------------------
primary
    : '(' expr ')'                        #parensExpr      // скобки
    | '(' type ')' expr                   #castExpr        // приведение типа
    | opMethodCall                        #methodCallPrimary
    | nodeLiteral                         #nodePrimary
    | arcLiteral                          #arcPrimary
    | graphLiteral                        #graphPrimary
    | literal                             #literalPrimary
    | ID                                   #idPrimary      // идентификатор
    ;

// ---------------------------
// Литерал node("A")
// ---------------------------
nodeLiteral
    : 'node' '(' expr ')'
    ;

// ---------------------------
// Литерал arc(a, b)
// ---------------------------
arcLiteral
    : 'arc' '(' expr ',' expr ')'
    ;

// ---------------------------
// Литерал graph([..], [..])
// ---------------------------
graphLiteral
    : 'graph' '(' '[' nodeList? ']' ',' '[' arcList? ']' ')'
    | '[[' nodeList? ']' ',' '[' arcList? ']]'
    ;

// ---------------------------
// Список узлов графа
// ---------------------------
nodeList
    : expr (',' expr)*
    ;

// ---------------------------
// Список ребер графа
// ---------------------------
arcList
    : expr (',' expr)*
    ;

// ---------------------------
// Литералы: числа, строки, boolean
// ---------------------------
literal
    : INT
    | STRING
    | BOOLEAN
    ;

// ---------------------------
// Система типов
// ---------------------------
type
    : 'int'
    | 'boolean'
    | 'string'
    | 'void'
    | 'node'
    | 'graph'
    | 'arc'
    ;

// ---------------------------
// Лексер
// ---------------------------

MUL : '*';
DIV : '/';
PLUS: '+';
MINUS: '-';
LT  : '<';
GT  : '>';
LE  : '<=';
GE  : '>=';
EQ  : '==';
NEQ : '!=';
AND : '&&';
OR  : '||';
NOT : '!';
INC : '++';
DEC : '--';

ASSIGN : '=';

LPAREN : '(';
RPAREN : ')';
LBRACE : '{';
RBRACE : '}';
LBRACK : '[';
RBRACK : ']';
COMMA  : ',';
SEMI   : ';';

BOOLEAN : 'true' | 'false';

INT
    : [0-9]+
    ;

STRING
    : '"' ( ~["\\] | '\\' . )* '"'
    ;

ID
    : [a-zA-Z_] [a-zA-Z0-9_]*
    ;

// Пробелы пропускаются
WS
    : [ \t\r\n]+ -> skip
    ;

// Комментарии вида // ...
LINE_COMMENT
    : '//' ~[\r\n]* -> skip
    ;
```

## Описание разработанных компонентов:

#### Классы
1. `DefaultGslVisitor` - класс выполняет семантический анализ программы GSL на основе дерева, построенного парсером, а также заполняет контекст, нужный для работы самого семантичесвкого анализатора, а также класса для кодогенерации.
2. `DefaultCodegenVisitor` - класс отвечает за трансляцию дерева разбора GSL в целевой код (LLVM IR).
3. `GslErrorListener` - класс обрабатывает синтаксические ошибки GSL, генерируемые парсером ANTLR.
4. `NodeValue` - класс представляет результат вычисления выражения(узла дерева, построенного парсером) во время обхода AST. Содержит информацию о типе данных, LLVM IR типе и операнде.
5. `Type` - класс, содержащий перечисление типов разрабатываемого языка.
6. `Context` - класс, хранящий информацию о функциях, переменных и типах во время обходов.
7. `FunctionInfo` - класс, содержащий описание функции, которое нужно для генерации вызова.
8. `VariableInfo` - класс для описания перменной(глобальная ли она, ее тип, является ли она параметром функции, аллоцирована ли) во время обхода дерева.
9. `SemanticException` - класс, представляющий семантическую ошибку, и содержащий метод для формирования строкового представления.
10. `IRGenerator` - класс, предоставляющий методы для геенарации LLVM IR, генерации названий переменных.
11. `Main` - класс осуществляющий запуск программы(синтаксический анализ -> семантический анализ -> кодогенерация).

#### Остальные файлы
1. `runtime.c` - функции, написанные на C, которые нужны для реализации алгоритмов, создания структур во время выполнения программы.
2. `build_and_run.sh` - скрипт для сборки и запуска проекта.

## Перечень генерируемых ошибок
1. Переменная уже объявлена в этой функции(учитываются объявления как внутри функции, так и аргументы фукнции)
2. Количество переменных и выражений справа от равно не совпадает с кол-вом переменных слева
3. Функция с такими параметрами уже определена
4. Каждая декларация переменных должна содержать тип
5. Невозможное приведение типа
6. Переменная не объявлена
7. Неправильные переданные параметры для создания node, arc, graph(детальное описание в сообщении)
8. Ошибки при вызове метода(не объявлен такой метод, неверные параметры)
9. Проверка, что для операций сложения/вычитания/умножения/деления используется int/node/arc/graph/string
10. Проверка, что для логических операций используется только boolean
11. Проверка, что для инкремента/декремента используется только int, а оператор "!" для булевого значения
12. Условие операторов if, while, until должно принимать boolean
13. Проверка возвращаемого значения оператором return, и того, что функция должна вернуть
14. Проверка, что глобальная переменная объявлена в функции void main()
15. Проверка наличия функции void main()

## Демонстрация работы
1. Первый пример:

Код:
```
//Главная цель файла -  проденстрировать примеры объявления, присваивания переменных, все возможные типы и операции языка.
//Также сделал один пример для многоскобочного выражения
graph checkMultiAssignment() {
    node a, b, c;
    a, b, c = node("A"), node("B"), node("C");
    return graph([a,b,c], []);
}

graph checkPlusOperator(node a, node b) {
    node c = a + b; //складывает строковые идентификаторы вершин
    node d = b + a;
    arc arcA = arc(a, b);
    arc arcB = arc(b, c);
    arc arcC = arc(c, d);
    arc arcD = arcA + arcB; //ноды будут иметь другие названия, полученные сложением соответствующих названий нод
    graph graphA = [[a,b], [arcA]];
    graph graphB = [[b,c], [arcB]];
    graph graphC = graphA + graphB; //получится граф a - b - c
    return graphC;
}

graph checkMinusOperator(node a, node b) {
    node c = a - b; //вычитает строковые идентификаторы вершин(предполагаю, что буду удалять символы из первой строки.) Пример "aa" - "ab" = "a"
    node d = b - a;
    arc arcA = arc(a, b);
    arc arcB = arc(b, c);
    arc arcC = arc(c, d);
    arc arcD = arcA - arcB; //ноды будут иметь другие названия, полученные вычитанием соответствующих названий нод
    graph graphA = [[a,b], [arcA]];
    graph graphB = [[b,c], [arcB]];
    graph graphC = graphA - graphB; //Удаляет узлы и дуги второго графа из первого. Получится граф a
    return graphC;
}

graph checkMultiplicationOperator(node a, node b) {
    node c = a * b;
    node d = b * a;
    arc arcA = arc(a, b);
    arc arcB = arc(b, c);
    arc arcC = arc(c, d);
    arc arcD = arcA * arcB;
    graph graphA = [[a,b], [arcA]];
    graph graphB = [[b,c], [arcB]];
    graph graphC = graphA * graphB; //декартово произведение графов
    return graphC;
}

graph checkDivisionOperator(node a, node b) {
    node c = a / b;
    node d = b / a;
    arc arcA = arc(a, b);
    arc arcB = arc(b, c);
    arc arcC = arc(c, d);
    arc arcD = arcA / arcB;
    graph graphA = [[a,b], [arcA]];
    graph graphB = [[b,c], [arcB]];
    graph graphC = graphA / graphB;
    return graphC;
}

//операторы ||, &&, !, ==, !=
void checkBooleanExample() {
    node a = node("A");
    node b = node("B");
    node c = node("C");
    arc ab = arc(a, b);
    arc bc = arc(b, c);
    graph g1 = [[a, b], [ab]];
    graph g2 = [[b, c], [bc]];
    graph g3 = [[a, c], [arc(a,c)]];
    boolean result = !((g1 == g2) || (g2 != g3)) && (a == node("A"));
}

void checkIntIncrementDecrement() {
    int a = 5;
    int b = 10;
    int c = ++a;
    int d = b--;
    ++a;
    --b;
    printInt(a);
    printInt(b);
    printInt(c);
    printInt(d);
}

void main() {
    string x = read();
    boolean flag = true;
    string name = "GraphTest";
    node A = node(name);
    node B = node("B");
    node n1 = (node) "A";
    node n2 = (node) "B";
    arc AB = arc(A, B);
    arc AA = (arc) A;
    graph H = graph([A, B], [AA, AB]);
    graph G2 = (graph) AB;
    graph G3 = checkMultiAssignment();
    graph G4 = checkPlusOperator(A, B);
    graph G5 = checkMinusOperator(A, B);
    graph G6 = checkMultiplicationOperator(A, B);
    graph G7 = checkDivisionOperator(A, B);
    checkBooleanExample();
    checkIntIncrementDecrement();
    printStr("A:");
    printNode(A);
    printStr("n1:");
    printNode(n1);
    printStr("AB:");
    printArc(AB);
    printStr("AA:");
    printArc(AA);
    printStr("H:");
    printGraph(H);
    printStr("G2:");
    printGraph(G2);
    printStr("G3:");
    printGraph(G3);
    printStr("G4:");
    printGraph(G4);
    printStr("G5:");
    printGraph(G5);
    printStr("G6:");
    printGraph(G6);
    printStr("G7:");
    printGraph(G7);
}
```

Вывод:
```
10
7
8
6
9
A:node(GraphTest)
n1:node(A)
AB:arc(GraphTest->B)
AA:arc(GraphTest->GraphTest)
H:graph {
  nodes: ["GraphTest", "B"]
  arcs: [(GraphTest->GraphTest), (GraphTest->B)]
}
G2:graph {
  nodes: []
  arcs: []
}
G3:graph {
  nodes: ["A", "B", "C"]
  arcs: []
}
G4:graph {
  nodes: ["GraphTest", "B", "B", "GraphTestB"]
  arcs: [(GraphTest->B), (B->GraphTestB)]
}
G5:graph {
  nodes: ["GraphTest", "B"]
  arcs: [(GraphTest->B)]
}
G6:graph {
  nodes: ["GraphTestB", "GraphTestGBraphTest", "BB", "BGBraphTest"]
  arcs: [(GraphTestB->BGBraphTest)]
}
G7:graph {
  nodes: []
  arcs: [(GraphTest->B)]
}
```

2. Второй пример:

Код:
```
//В файле продемонстрировал всё, кроме работы со встроенными функциями: блочный, условный операторы, циклы,
//работа с параметрами в функциях, глобальные переменные, видимость переменных
int add(int a, int b) {
    return a + b;
}

node add(node a, node b) {
    return a + b;
}

node add(node a, node b, node c) {
    return a * (b - c);
}

void incByValue(int x) {
    int a = x + 1;
    printInt(a);
}

boolean isZero(int x) {
    if (x == 0) {
        return true;
    } else {
        return false;
    }
}

void globalVariableExample(node a, node b) {
    GLOBAL_GRAPH = graph([a, b], [arc(a,b)]);
    printGraph(GLOBAL_GRAPH);
}

void loopExamples() {
    int i = 0;
    while (i < 3) {
        i++;
	printStr("i: ");
        printInt(i);
    }

    int j = 0;
    until (j >= 3) {
        j++;
	printStr("j: ");
        printInt(j);
    }

    for (int k = 0; k < 4; k++) {
	printStr("k: ");
	printInt(k);
    }
}

void main() {
    global graph GLOBAL_GRAPH = graph([], []);
    int val = 5;
    incByValue(val);
    int sumInt = add(2, 3);
    printStr("sumInt: ");
    printInt(sumInt);
    node n1 = node("A");
    node n2 = node("B");
    node n3 = node("C");
    node sumNode = add(n1, n2);
    printStr("sumNode: ");
    printNode(sumNode);
    node sumNode1 = add(n1, n2, n3);
    printStr("sumNode1: ");
    printNode(sumNode1);
    if (isZero(sumInt)) {
        sumNode = node("BA");
    } else {
        sumNode = node("BA");
    }
    printStr("sumNode: ");
    printNode(sumNode);
    globalVariableExample(n1, n2);
    loopExamples();
    printGraph(GLOBAL_GRAPH);
}
```

Вывод:
```
6
sumInt: 5
sumNode: node(AB)
sumNode1: node(AB)
sumNode: node(BA)
graph {
  nodes: ["A", "B"]
  arcs: [(A->B)]
}
i: 1
i: 2
i: 3
j: 1
j: 2
j: 3
k: 0
k: 1
k: 2
k: 3
graph {
  nodes: ["A", "B"]
  arcs: [(A->B)]
}
```

3. Третий пример:

Код:
```
//В данном файле продемонстрировал встроенные функции и показал, что с помощью языка можно работать с графами
void main() {
    printStr("Enter graph size: ");
    string strN = read();
    int n = (int) strN;
    printStr("n: ");
    printInt(n);
    graph G = graph([], []);
    printGraph(G);
    for (int i = 1; i <= n; i++) {
        string strI = (string) i;
        node v = node("N" + strI);
        G = addNode(G, v);
    }
    printGraph(G);
    for (int i = 0; i < (n-1); i++) {
        node f = getNode(G, i);
        node t = getNode(G, i + 1);
        arc e = arc(f, t);
        G = addArc(G, e);
    }
    printGraph(G);
    node first = getNode(G, 0);
    node last = getNode(G, n-1);
    printNode(first);
    printNode(last);
    arc testArc = arc(first, last);
    if (hasNode(G, first)) {
        printStr("Graph has node: ");
        printNode(first);
    }
    if (!hasArc(G, testArc)) {
        printStr("Graph has no direct arc from first to last");
    }
    node neighbour = getNeighbour(G, first, 0);
    printStr("Neighbour of ");
    printNode(first);
    printStr(" = ");
    printNode(neighbour);
    graph shortest = shortestPath(G, first, last);
    printStr("Shortest path from ");
    printNode(first);
    printStr(" to ");
    printNode(last);
    printStr(" = ");
    printGraph(shortest);
    graph bfsResult = bfs(G, first);
    printStr("BFS from ");
    printNode(first);
    printGraph(bfsResult);
    graph dfsResult = dfs(G, first);
    printStr("DFS from ");
    printNode(first);
    printGraph(dfsResult);
    arc deleteTest = arc(getNode(G, 0), getNode(G, 1));
    printStr("Arc for delete: ");
    printArc(deleteTest);
    if (hasArc(G, deleteTest)) {
        G = deleteArc(G, deleteTest);
    }
    printStr("Graph after delete arc ");
    printGraph(G);
    node delNode = getNode(G, 0);
    printStr("Node for delete ");
    printNode(delNode);
    if (hasNode(G, delNode)) {
        G = deleteNode(G, delNode);
    }
    printStr("Final graph: ");
    printGraph(G);
    printStr("Graph size: ");
    printInt(size(G));
}
```

Вывод:
```
10
Enter graph size: n: 10
graph {
  nodes: []
  arcs: []
}
graph {
  nodes: ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10"]
  arcs: []
}
graph {
  nodes: ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10"]
  arcs: [(N1->N2), (N2->N3), (N3->N4), (N4->N5), (N5->N6), (N6->N7), (N7->N8), (N8->N9), (N9->N10)]
}
node(N1)
node(N10)
Graph has node: node(N1)
Graph has no direct arc from first to lastNeighbour of node(N1)
 = node(N2)
Shortest path from node(N1)
 to node(N10)
 = graph {
  nodes: ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10"]
  arcs: [(N1->N2), (N2->N3), (N3->N4), (N4->N5), (N5->N6), (N6->N7), (N7->N8), (N8->N9), (N9->N10)]
}
BFS from node(N1)
graph {
  nodes: ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10"]
  arcs: [(N1->N2), (N2->N3), (N3->N4), (N4->N5), (N5->N6), (N6->N7), (N7->N8), (N8->N9), (N9->N10)]
}
DFS from node(N1)
graph {
  nodes: ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10"]
  arcs: [(N1->N2), (N2->N3), (N3->N4), (N4->N5), (N5->N6), (N6->N7), (N7->N8), (N8->N9), (N9->N10)]
}
Arc for delete: arc(N1->N2)
Graph after delete arc graph {
  nodes: ["N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10"]
  arcs: [(N2->N3), (N3->N4), (N4->N5), (N5->N6), (N6->N7), (N7->N8), (N8->N9), (N9->N10)]
}
Node for delete node(N1)
Final graph: graph {
  nodes: ["N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10"]
  arcs: [(N2->N3), (N3->N4), (N4->N5), (N5->N6), (N6->N7), (N7->N8), (N8->N9), (N9->N10)]
}
Graph size: 9
```
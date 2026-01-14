\# Отчет по лабораторному практикуму 



\## Спецификация языка XMLang



Язык \*\*XMLang\*\* — язык программирования, основным направлением которого является работа с xml документами.



\*\*Ключевые особенности:\*\*



\* \*\*Типизация:\*\* Строгая статическая (`int`, `float`, `boolean`, `string`, `document`, `node`, `attribute`, `list`).

\* \*\*Структура:\*\* Программа состоит из функций и глобальных инструкций. Поддерживаются вложенные блоки кода.

\* \*\*Функции:\*\* Поддержка именованных функций.

\* \*\*Встроенные операции:\*\* Создание документов, узлов и атрибутов; получение и изменение узлов и атрибутов, условные операторы (`if-else`, `switch`), циклы (`while`, `for`).



\## Файл грамматики



```

grammar XMLlang;



start: program\* EOF;



program

&nbsp;   : defDecl

&nbsp;   | def

&nbsp;   | defCall

&nbsp;   | stat

&nbsp;   ;



def: (type|TYPEVOID) FUNC ID LC (type ID (COM type ID)\*)? RC body;



defDecl: (type|TYPEVOID) FUNC ID LC (type (COM type)\*)? RC;



stat

&nbsp;   : conCycOperator

&nbsp;   | assignment

&nbsp;   | assFunc

&nbsp;   | statFunc

&nbsp;   | returnVal

&nbsp;   | BREAK

&nbsp;   | COMMENT

&nbsp;   ;



conCycOperator

&nbsp;   : ifcon

&nbsp;   | switchcon

&nbsp;   | forcon

&nbsp;   | whilecon

&nbsp;   ;



ifcon: IF condition body (ELSE body)?;

switchcon: SWITCH ID LF (CASE (INT|FLOAT|STRING|BOOL) ':' body)+ (DEFAULT body)? RF;

forcon: FOR ID IN ID body;

whilecon: WHILE condition body;



body: LF program\* RF;



assignment: typeList (EQ opList)?;



typeList: type? ID (COM type? ID)\*;

opList: (val|assFunc|INT|STRING|FLOAT|BOOL|list|PASS) (COM (val|assFunc|INT|FLOAT|STRING|BOOL|list|PASS))\*;//|assFunc



assFunc

&nbsp;   : write

&nbsp;   | create

&nbsp;   | load

&nbsp;   | getAttribute

&nbsp;   | getNodeText

&nbsp;   | getName

&nbsp;   | getValue

&nbsp;   | getNodes

&nbsp;   | getListElement

&nbsp;   | nodeSumm

&nbsp;   ;



statFunc

&nbsp;   : read

&nbsp;   | xmldelete

&nbsp;   | save

&nbsp;   | transform

&nbsp;   | addAttribute

&nbsp;   | append

&nbsp;   | edit

&nbsp;   ;



read: READ LC (ID|defCall|INT|FLOAT|STRING|BOOL|list)\* RC;

write: WRITE LC RC;



create: CREATE PNT

&nbsp;   ( createDoc

&nbsp;   | createNode

&nbsp;   | createAttribute)

&nbsp;   ;



createDoc: DOCUMENT LC (ROOT EQ (val|STRING))? (FILE EQ (val|PASS))? RC;

createNode: NODE LC (NAME EQ (val|STRING)) (TEXT EQ (val|STRING))? RC;

createAttribute: ATTRIBUTE LC (NAME EQ (val|STRING)) (VALUE EQ (val|STRING)) RC;



edit: ID PNT EDIT LC

&nbsp;   ( docEdit

&nbsp;   | nodeEdite

&nbsp;   | attributeEdit) RC

&nbsp;   ;



docEdit: ((ROOT EQ (ID|STRING|defCall)) (FILE EQ (ID|PASS|defCall))?)|(FILE EQ (ID|PASS|defCall));

nodeEdite: ((NAME EQ (ID|STRING|defCall)) (TEXT EQ (ID|STRING|defCall))?)|(TEXT EQ (ID|STRING|defCall));

attributeEdit: ((NAME EQ (val|STRING)) (VALUE EQ (val|STRING))?)|(VALUE EQ (val|STRING));



load: LOAD LC (PASS|ID|defCall) RC;

transform: ID PNT TRANSFORM LC (TO EQ TRANSFTO) (FILE EQ (PASS|ID|defCall|STRING)) RC;

xmldelete: DELETE ID;

save: ID PNT SAVE LC (PASS|ID)? RC;



getAttribute: ID PNT GETATTR LC (ID|STRING|defCall)? RC;

addAttribute: ID PNT ADDA LC (ID|defCall|CREATE PNT createAttribute) RC;

append: ID PNT APPEND LC (val|ID (SL ID)\*) RC;

getNodeText: ID PNT GETTEXT LC RC;



getName: ID PNT GETNAME LC RC;

getValue: ID PNT GETVALUE LC RC;



getNodes: ID (SL ID)\* (LS condition (COM condition)\* RS)?;



getListElement: val LS INT RS;



nodeSumm: val PLS val;



condition: NEG\* (NEG\* (val|INT|FLOAT|STRING|BOOL) INEQUALITYSIGN NEG\* (val|INT|FLOAT|STRING|BOOL)|(val|BOOL));



returnVal: RETURN (val|INT|FLOAT|STRING|BOOL|list)?;



defCall: ID LC ((val|INT|FLOAT|STRING|BOOL|list) (COM (val|INT|FLOAT|STRING|BOOL|list))\*)? RC;



type

&nbsp;   : DOCUMENT 

&nbsp;   | NODE 

&nbsp;   | ATTRIBUTE

&nbsp;   | BASETYPE

&nbsp;   ;



DOCUMENT: 'document';

NODE: 'node';

ATTRIBUTE: 'attribute';

BASETYPE: 'bool' | 'string' | 'int' | 'float' | 'list';



DELETE: 'delete';

LOAD: 'load';

FUNC: 'func';

IF: 'if';

ELSE: 'else';

SWITCH: 'switch';

FOR: 'for';

WHILE: 'while';

READ: 'read';

WRITE: 'write';

CREATE: 'create';

IN: 'in';

CASE: 'case';

DEFAULT: 'default';

TO: 'to';

TYPEVOID: 'void';



ADDA: 'addAttribute';

APPEND: 'appendTo';

SAVE: 'save';

GETATTR: 'getAttribute';

GETTEXT: 'getText';

GETNAME: 'getName';

GETVALUE: 'getValue';

GETNODES: 'getNodes';

EDIT: 'edit';

TRANSFORM: 'transform';



ROOT: 'root';

FILE: 'file';

NAME: 'name';

TEXT: 'text';

VALUE: 'value';

TRANSFTO: '"json"' | '"html"';



RETURN: 'return';

BREAK: 'break';



COMMENT: '//' ~\[\\r\\n]\* -> skip;

MULTILINE\_COMMENT: '/\*' .\*? '\*/' -> skip;

PASS: '"'  (~\["\\\\\\r\\n] | '\\\\' .)\*'.xml' '"';

BOOL: 'True' | 'False';

ID: \[a-zA-Z] \[a-zA-Z0-9\_]\*;

STRING: '"' (~\["\\\\\\r\\n] | '\\\\' .)\* '"'| '\\'' (~\["\\\\\\r\\n] | '\\\\' .)\* '\\'';

INT: \[0-9]+;

FLOAT: \[0-9]+ '.' \[0-9]\*;



list: LS RS

&nbsp;   | LS (val|BOOL|INT|FLOAT|STRING|list) (COM (val|BOOL|INT|FLOAT|STRING|list))\* RS

&nbsp;   ;



val: ID| defCall ;



INEQUALITYSIGN: '==' | '!=' | '>' | '<' | '>=' | '<=';

EQ: '=';

NEG: '!';



LC: '(';

RC: ')';

LF: '{';

RF: '}';

LS: '\[';

RS: ']';

PNT: '.';

COM: ',';

PLS: '+';

SL: '/';



WS: \[ \\t\\r\\n]+ -> skip;

```



\### Описание разработанных классов

\#### Синтаксический анализатор

Модуль отвечает за преобразование исходного текста в дерево разбора (Parse Tree) с учетом отступов.



\* \*\*`XMLParser`\*\*: Точка входа в этап парсинга. Инициализирует лексер и парсер, регистрирует слушатели ошибок и возвращает результат анализа.

\* \*\*`CustomErrorListener`\*\*: Накапливает синтаксические ошибки (неверные токены, нарушение структуры грамматики, ошибки отступов) для последующего вывода.



\#### Семантический анализатор

Модуль выполняет проверку типов, областей видимости и корректности использования конструкций языка.



\* \*\*`SemanticAnalyzer`\*\*: Оркестратор семантического анализа. Запускает обход дерева (Walker) с использованием `SemanticErrorListener`.

\* \*\*`Scope`\*\*: Реализуют управление областями видимости (стек scopes). Позволяют определять переменные/функции и искать их (lookup) с учетом вложенности блоков.

\* \*\*`SemanticError`\*\*: Накапливает семантические ошибки для последующего вывода.

\* \*\*`FunctionOverload`\*\*: Проверка переменных на повторное использование с учётом возможности перегрузки функции.



\#### Компилятор в байт-код Python (.pyc)

Реализует генерацию исполняемого кода в два этапа: трансляция в промежуточный ассемблер и сборка бинарного файла.



\* \*\*`Compiler`\*\*: Главный класс приложения. Управляет всем конвейером: чтение файла -> парсинг -> семантический анализ -> генерация ассемблера -> вызов внешнего сборщика.

\* \*\*`PycAssembler`\*\*: Создаёт промежуточный ассемблер-код.

\* \*\*`BytecodeGenerator`\*\*: Создание конечного целевого кода (.pyc).



\### Перечень генерируемых ошибок



Компилятор диагностирует и выводит следующие классы ошибок:



1\. \*\*Синтаксические ошибки:\*\*

\* `Mismatched input / Extraneous input`: несоответствие кода грамматике (пропущенные скобки, неверные ключевые слова).





2\. \*\*Семантические ошибки:\*\*

\* \*\*Ошибки типов (`Type Mismatch`):\*\* Попытка присвоить 

&nbsp;	- node в int, float, list, attribute и наоборот

&nbsp;	- document в int, float, list, attribute и наоборот

&nbsp;	- list в какой либо

\* \*\*Ошибки областей видимости (`Undeclared Variable`):\*\* Использование переменных, которые не были объявлены в текущей или родительской области.

\* Несоответствие количества присваиваемых значений при декларации.

\* Несоответствие сигнатуре (неверное количество или типы аргументов).

\* Повторение аргументов switch.











\## Примеры работы



Листинг вывода компилятора в терминал. Тестирование системы проводилось на тестовых примерах из examples/



Активация происходит через терминальную команду `./xmlang.sh  filepass.xmlang `



```

$ ./xmlang.sh  examples\\\\example1.xmlang

Компиляция examples\\example1.xmlang в examples\\example1.pyc...

============================================================

XMLang Compiler (Bytecode Assembler)

Python 3.11.0 (main, Oct 24 2022, 18:26:48) \[MSC v.1933 64 bit (AMD64)]

============================================================



\[1/5] Parsing syntax...

Syntax is valid



\[2/5] Semantic analysis...

Semantic analysis passed



\[3/5] Analyzing AST and generating bytecode...

&nbsp; Found global variable: doc

&nbsp; Found global variable: r

&nbsp; Found global variable: pass1

&nbsp; Found global variable: one

&nbsp; Found global variable: two

&nbsp; Found global variable: pass2

&nbsp; Found global variable: doc1

&nbsp; Found global variable: doc2

&nbsp; Found global variable: r1

&nbsp; Found global variable: r2

&nbsp; Found global variable: nr

&nbsp; Found global variable: ndoc



\[4/5] Generating bytecode...

Generating helper functions...

&nbsp; Created 3 helper functions

Generating function: A

&nbsp; Error generating function A: invalid syntax (program.xmlang, line 2)

Generating function: A

&nbsp; Generated function A

Generating main module...

&nbsp; Generated main module with 8 constants



\[5/5] Assembling examples\\example1.pyc...

Successfully assembled examples\\example1.pyc



$ ./xmlang.sh  examples\\\\example3.xmlang

Компиляция examples\\example3.xmlang в examples\\example3.pyc...

Compiling: examples\\example3.xmlang

Output: examples\\example3.pyc

============================================================

XMLang Compiler (Bytecode Assembler)

Python 3.11.0 (main, Oct 24 2022, 18:26:48) \[MSC v.1933 64 bit (AMD64)]

============================================================



\[1/5] Parsing syntax...

Syntax is valid



\[2/5] Semantic analysis...

Semantic analysis passed



\[3/5] Analyzing AST and generating bytecode...

&nbsp; Found global variable: pass\_

&nbsp; Found global variable: doc

&nbsp; Found global variable: l

&nbsp; Found global variable: b

&nbsp; Found global variable: d



\[4/5] Generating bytecode...

Generating helper functions...

&nbsp; Created 3 helper functions

Generating main module...

&nbsp; Generated main module with 6 constants



\[5/5] Assembling examples\\example3.pyc...

Successfully assembled examples\\example3.pyc



$ ./xmlang.sh  examples\\\\synt\_error\_example1.xmlang

Компиляция examples\\synt\_error\_example1.xmlang в examples\\synt\_error\_example1.pyc...

Compiling: examples\\synt\_error\_example1.xmlang

Output: examples\\synt\_error\_example1.pyc

============================================================

XMLang Compiler (Bytecode Assembler)

Python 3.11.0 (main, Oct 24 2022, 18:26:48) \[MSC v.1933 64 bit (AMD64)]

============================================================



\[1/5] Parsing syntax...

Syntax errors found:

&nbsp; - Error at line 6:1 - extraneous input 'return' expecting {'load', 'write', 'create', PASS, BOOL, ID, STRING, INT, FLOAT, '\['}

&nbsp; - Lexical at line 8:0 - token recognition error at: '\\'

&nbsp; - Error at line 24:0 - extraneous input '<EOF>' expecting {'document', 'node', 'attribute', BASETYPE, 'delete', 'load', 'if', 'switch', 'for', 'while', 'read', 'write', 'create', 'void', 'return', 'break', COMMENT, ID, '}'}

Ошибка компиляции



$ ./xmlang.sh  examples\\\\synt\_error\_example2.xmlang

Компиляция examples\\synt\_error\_example2.xmlang в examples\\synt\_error\_example2.pyc...

Compiling: examples\\synt\_error\_example2.xmlang

Output: examples\\synt\_error\_example2.pyc

============================================================

XMLang Compiler (Bytecode Assembler)

Python 3.11.0 (main, Oct 24 2022, 18:26:48) \[MSC v.1933 64 bit (AMD64)]

============================================================



\[1/5] Parsing syntax...

Syntax errors found:

&nbsp; - Lexical at line 5:25 - token recognition error at: '\\'

&nbsp; - Error at line 3:16 - no viable alternative at input 'documentfuncA(inp\_pass'

&nbsp; - Error at line 3:25 - extraneous input '{' expecting {<EOF>, 'document', 'node', 'attribute', BASETYPE, 'delete', 'load', 'if', 'switch', 'for', 'while', 'read', 'write', 'create', 'void', 'return', 'break', COMMENT, ID}

&nbsp; - Error at line 15:0 - no viable alternative at input 'doc}'

Ошибка компиляции



$ ./xmlang.sh  examples\\\\sem\_error\_example1.xmlang

Компиляция examples\\sem\_error\_example1.xmlang в examples\\sem\_error\_example1.pyc...

Compiling: examples\\sem\_error\_example1.xmlang

Output: examples\\sem\_error\_example1.pyc

============================================================

XMLang Compiler (Bytecode Assembler)

Python 3.11.0 (main, Oct 24 2022, 18:26:48) \[MSC v.1933 64 bit (AMD64)]

============================================================



\[1/5] Parsing syntax...

Syntax is valid



\[2/5] Semantic analysis...

Semantic errors found:

&nbsp; - Semantic Error at line 6:1: Cannot assign unknown to node

&nbsp; - Semantic Error at line 6:10: Variable 'do' is not declared

&nbsp; - Semantic Error at line 12:1: Cannot assign document to attribute

&nbsp; - Semantic Error at line 17:0: Mismatch in multiple assignment. Expected 1 values, got 2

&nbsp; - Semantic Error at line 18:10: Variable 'two' is not declared

Ошибка компиляции



$ ./xmlang.sh  examples\\\\sem\_error\_example2.xmlang

Компиляция examples\\sem\_error\_example2.xmlang в examples\\sem\_error\_example2.pyc...

Compiling: examples\\sem\_error\_example2.xmlang

Output: examples\\sem\_error\_example2.pyc

============================================================

XMLang Compiler (Bytecode Assembler)

Python 3.11.0 (main, Oct 24 2022, 18:26:48) \[MSC v.1933 64 bit (AMD64)]

============================================================



\[1/5] Parsing syntax...

Syntax is valid



\[2/5] Semantic analysis...

Semantic errors found:

&nbsp; - Semantic Error at line 4:5: Variable 'doc' is not declared

Ошибка компиляции



```




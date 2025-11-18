grammar XMLlang;

program
    :defDecl? .*? def
    |def .* defCall
    |stat
	;

def:(type|voidType) 'func' ID '('(type ID (',' type ID)*)?')' body;

defDecl:(type|voidType) 'func' ID '('(type (',' type )*)?')';

stat
    :conCycOperator
    |assignment
	|assFunc
	;

conCycOperator
    :if
    |switch
    |for
    |while
    ;

if:'if' condition body ('else' body)?;
switch:'switch' ID '{'('case' (INT|FLOAT|STRING|BOOL)':' body)+('default:' body)?'}';
for:'for' ID 'in' ID body;
while:'while' condition;

body:'{'program*'}';

assignment:typeList '=' opList;

typeList:type ID (','type ID)*;
opList:(val|assFunc|INT|STRING|FLOAT|BOOL|LIST) (','(val|assFunc|INT|FLOAT|STRING|BOOL|LIST))*;

assFunc
    :write
    |create
    |load
    |getAttribute
    |getText
    |getName
    |getValue
    |getNodes
    |getListElement
    |nodeSumm
    ;

statFunc
    :read
    |delete
    |docEdit
    |save
    |transform
    |nodeEdite
    |addAttribute
    |append
    |attributeEdit
    ;

read:'read('(ID|defCall)')';
write:'write()';

create:'create.'
    (createDoc
    |createNode
    |createAttribute)
    ;
createDoc:ID'.''document('('root'EQ (val|STRING))?('file'EQ (val|PASS))?')';
createNode:ID'.''node('('name'EQ(val|STRING))('text'EQ(val|STRING))?')';
createAttribute:ID'.''attribute('('name'EQ(val|STRING))('value'EQ(val|STRING))')';

load:'load(' (PASS|ID|defCall)')';
transform:ID'.''transform('('to'EQ('json'|'html'))('file'EQ(PASS|ID|defCall))')';
delete:'delete' ID;
save:ID'.''save('(PASS|ID)?')';
docEdit:ID'.''edit('('root'EQ (ID|STRING|defCall))?('file'EQ (ID|PASS|defCall))?')';

nodeEdite:ID'.''edit('('name'EQ(ID|STRING|defCall))?('text'EQ(ID|STRING|defCall))?')';
getAttribute:ID'.''getAttribute('(ID|STRING|defCall)?')';
addAttribute:ID'.''addAttribute('(ID|defCall)')';
append:ID'.''appendTo('(ID|defCall)')';
getText:ID'.''getText()';

attributeEdit:ID'.''edit('('name'EQ(val|STRING))?('value'EQ(val|STRING))?')';
getName:ID'.''getName()';
getValue:ID'.''getValue()';

getNodes:ID('/'ID)*('['condition(','condition)*']');

getListElement:val'['INT']';

nodeSumm:val '+' val;

condition:NEG? NEG? (val|INT|FLOAT|STRING|BOOL) INEQUALITYSIGN NEG? (val|INT|FLOAT|STRING|BOOL);
val
    :ID
    |defCall
    ;
defCall:ID'('((val|INT|FLOAT|STRING|BOOL|LIST)(','(val|INT|FLOAT|STRING|BOOL|LIST))*)?')';

type
    :xmlType
    |baseType
    ;

xmlType
	:'document'
	|'node'
	|'attribute'
	;

baseType
	:'bool'
    |'string'
	|'int'
    |'float'
    |'list'
	;
voidType:'void';

BOOL:'True'|'False';
ID:[a-zA-Z][a-zA-Z0-9_]*;
STRING:'"' ( ~["\\\r\n] | '\\' . )* '"';
INT:[0-9]+;
FLOAT:[0-9]+'.'[0-9]*;
LIST:'['(ID(',' ID)*|EOF)']';
PASS:'"'([A-Z]':')?[a-zA-Z0-9_-]+''('.xml')?'"';
INEQUALITYSIGN
	:'=='
    |'!='
	|'>'
	|'<'
	|'>='
	|'<='
	;
EQ:'=';
NEG:'!';
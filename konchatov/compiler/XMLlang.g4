
grammar XMLlang;

start: program* EOF;

program
    : defDecl
    | def
    | defCall
    | stat
    ;

def: (type|TYPEVOID) FUNC ID LC (type ID (COM type ID)*)? RC body;

defDecl: (type|TYPEVOID) FUNC ID LC (type (COM type)*)? RC;

stat
    : conCycOperator
    | assignment
    | assFunc
    | statFunc
    | returnVal
    | BREAK
    | COMMENT
    ;

conCycOperator
    : ifcon
    | switchcon
    | forcon
    | whilecon
    ;

ifcon: IF condition body (ELSE body)?;
switchcon: SWITCH ID LF (CASE (INT|FLOAT|STRING|BOOL) ':' body)+ (DEFAULT body)? RF;
forcon: FOR ID IN ID body;
whilecon: WHILE condition body;

body: LF program* RF;

assignment: typeList (EQ opList)?;

typeList: type? ID (COM type? ID)*;
opList: (val|assFunc|INT|STRING|FLOAT|BOOL|list|PASS) (COM (val|assFunc|INT|FLOAT|STRING|BOOL|list|PASS))*;//|assFunc

assFunc
    : write
    | create
    | load
    | getAttribute
    | getNodeText
    | getName
    | getValue
    | getNodes
    | getListElement
    | nodeSumm
    ;

statFunc
    : read
    | xmldelete
    | save
    | transform
    | addAttribute
    | append
    | edit
    ;

read: READ LC (ID|defCall|INT|FLOAT|STRING|BOOL|list)* RC;
write: WRITE LC RC;

create: CREATE PNT
    ( createDoc
    | createNode
    | createAttribute)
    ;

createDoc: DOCUMENT LC (ROOT EQ (val|STRING))? (FILE EQ (val|PASS))? RC;
createNode: NODE LC (NAME EQ (val|STRING)) (TEXT EQ (val|STRING))? RC;
createAttribute: ATTRIBUTE LC (NAME EQ (val|STRING)) (VALUE EQ (val|STRING)) RC;

edit: ID PNT EDIT LC
    ( docEdit
    | nodeEdite
    | attributeEdit) RC
    ;

docEdit: ((ROOT EQ (ID|STRING|defCall)) (FILE EQ (ID|PASS|defCall))?)|(FILE EQ (ID|PASS|defCall));
nodeEdite: ((NAME EQ (ID|STRING|defCall)) (TEXT EQ (ID|STRING|defCall))?)|(TEXT EQ (ID|STRING|defCall));
attributeEdit: ((NAME EQ (val|STRING)) (VALUE EQ (val|STRING))?)|(VALUE EQ (val|STRING));

load: LOAD LC (PASS|ID|defCall) RC;
transform: ID PNT TRANSFORM LC (TO EQ TRANSFTO) (FILE EQ (PASS|ID|defCall|STRING)) RC;
xmldelete: DELETE ID;
save: ID PNT SAVE LC (PASS|ID)? RC;

getAttribute: ID PNT GETATTR LC (ID|STRING|defCall)? RC;
addAttribute: ID PNT ADDA LC (ID|defCall|CREATE PNT createAttribute) RC;
append: ID PNT APPEND LC (val|ID (SL ID)*) RC;
getNodeText: ID PNT GETTEXT LC RC;

getName: ID PNT GETNAME LC RC;
getValue: ID PNT GETVALUE LC RC;

getNodes: ID (SL ID)* (LS condition (COM condition)* RS)?;

getListElement: val LS INT RS;

nodeSumm: val PLS val;

condition: NEG* (NEG* (val|INT|FLOAT|STRING|BOOL) INEQUALITYSIGN NEG* (val|INT|FLOAT|STRING|BOOL)|(val|BOOL));

returnVal: RETURN (val|INT|FLOAT|STRING|BOOL|list)?;

defCall: ID LC ((val|INT|FLOAT|STRING|BOOL|list) (COM (val|INT|FLOAT|STRING|BOOL|list))*)? RC;



type
    : DOCUMENT 
    | NODE 
    | ATTRIBUTE
    | BASETYPE
    ;


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

COMMENT: '//' ~[\r\n]* -> skip;
MULTILINE_COMMENT: '/*' .*? '*/' -> skip;
PASS: '"'  (~["\\\r\n] | '\\' .)*'.xml' '"';
BOOL: 'True' | 'False';
ID: [a-zA-Z] [a-zA-Z0-9_]*;
STRING: '"' (~["\\\r\n] | '\\' .)* '"'| '\'' (~["\\\r\n] | '\\' .)* '\'';
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]*;

list: LS RS
    | LS (val|BOOL|INT|FLOAT|STRING|list) (COM (val|BOOL|INT|FLOAT|STRING|list))* RS
    ;

val: ID| defCall ;

INEQUALITYSIGN: '==' | '!=' | '>' | '<' | '>=' | '<=';
EQ: '=';
NEG: '!';

LC: '(';
RC: ')';
LF: '{';
RF: '}';
LS: '[';
RS: ']';
PNT: '.';
COM: ',';
PLS: '+';
SL: '/';

WS: [ \t\r\n]+ -> skip;
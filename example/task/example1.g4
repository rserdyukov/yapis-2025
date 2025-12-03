/*

int a = 5, b;
scanf("%d", &b);
if (b == a) {
	printf("test");
} else {
	a = b / 3 + 7;
}

*/

grammar example1;

options {
superClass = BaseParser;
}

program
	: statement_list {
self.codes = $statement_list.result_codes.copy()
	}
	;

statement_list returns [result_codes] locals [codes]
@init {
$codes = []
}
    : statement+ {
$result_codes = $codes.copy()
    }
    ;


statement
	: declarete_var_statement
	| call_function
	| if_statement
	| assign_statement
	;

declarete_var_statement
	: type declarete_var[$type.declare_type] (',' declarete_var[$type.declare_type])* ';'
	;

type returns [declare_type]
	: 'int' {
$declare_type = "int"
	}
	;

declarete_var [declare_type]
	: ID ('=' NUMBER)? {
if $ID.text in self.names:
	self.errors.append(f"Variable {$ID.text} is already declated")
	return
else:
	self.names[$ID.text] = { 'type': $declare_type, 'init_value': $NUMBER.text }
	if $NUMBER.text:
	    $statement_list::codes.append(("ASSIGN", $ID.text, $NUMBER.text))
	}
	;

call_function
	: ID '(' (arg_list+=argument (',' arg_list+=argument)*)? ')' ';' {
for argument in $arg_list:
    $statement_list::codes.append(("PARAM", argument.result_var))
$statement_list::codes.append(("CALL", $ID.text, len($arg_list)))
	}
	;

argument returns [result_var]
	: expr {
$result_var = $expr.result_var
	}
	;

if_statement
	: 'if' '(' logic_expr ')' '{' s1=statement_list '}'  ('else' '{' s2=statement_list '}')? {
label_then = self.next_temporal_label()
label_finish = self.next_temporal_label()
$statement_list::codes.append(("IF", $logic_expr.result_var, label_then))
if $s2.text:
    $statement_list::codes.extend($s2.result_codes)
$statement_list::codes.append(("GOTO", label_finish))
$statement_list::codes.append(("LABEL", label_then))
$statement_list::codes.extend($s1.result_codes)
$statement_list::codes.append(("LABEL", label_finish))
	}
	;

logic_expr returns [result_var]
	: i1=ID '==' i2=ID {
$result_var = self.next_temporal_variable()
$statement_list::codes.append(("EQ", $result_var, $i1.text, $i2.text))
	}
	;

assign_statement
	: ID '=' expr ';' {
if $ID.text not in self.names:
	self.errors.append(f"Variable {$ID.text} not declated")
	return
else:
	if $expr.result_type != self.names[$ID.text].get('type'):
		self.errors.append(f"Incorrect type")
		return
$statement_list::codes.append(("ASSIGN", $ID.text, $expr.result_var))
	}
	;

expr returns [result_var, result_type]
	: ID {
if $ID.text not in self.names:
	self.errors.append(f"Variable {$ID.text} not declated")
	return
else:
	$result_var = $ID.text
	$result_type = self.names[$ID.text].get('type')
	}
	| NUMBER {
$result_var = $NUMBER.text
$result_type = "int"
	}
	| STRING {
$result_var = self.next_temporal_const()
$result_type = "string"
self.consts.append(($result_var, $STRING.text))
	}
	| '&'ID {
if $ID.text not in self.names:
	self.errors.append(f"Variable {$ID.text} not declated")
	return
else:
	$result_type = "addr"
	$result_var = self.next_temporal_variable()
	$statement_list::codes.append(("ADDR", $result_var, $ID.text))
	}
	| e1=expr '/' e2=expr {
if $e1.result_type != $e2.result_type:
    self.errors.append(f"Incorrect type {$e1.result_type} / {$e2.result_type}")
    return
else:
    $result_type = $e1.result_type
    $result_var = self.next_temporal_variable()
	$statement_list::codes.append(("DIV", $result_var, $e1.result_var, $e2.result_var))
    }
	| e1=expr '+' e2=expr {
if $e1.result_type != $e2.result_type:
	self.errors.append(f"Incorrect type {$e1.result_type} + {$e2.result_type}")
	return
else:
	$result_type = $e1.result_type
	$result_var = self.next_temporal_variable()
	$statement_list::codes.append(("ADD", $result_var, $e1.result_var, $e2.result_var))
	}
	;

ID
	: [a-zA-Z][a-zA-Z0-9_]*
	;

STRING
	: '"'~["]*'"'
	;

NUMBER
	: [0-9]+
	;

WS
	: [ \t\r\n]+ -> skip
	;

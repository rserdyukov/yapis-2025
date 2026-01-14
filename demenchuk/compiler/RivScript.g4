grammar RivScript;

program
    : NEWLINE* program_item* EOF
    ;

program_item
    : function_def NEWLINE*
    | statement NEWLINE*
    | NEWLINE
    ;

function_def
    : DEF ID LPAREN param_list? RPAREN COLON NEWLINE INDENT statement_block DEDENT
    ;

param_list
    : param (COMMA param)*
    ;

param
    : REF? ID
    ;

statement
    : assignment_stmt NEWLINE
    | if_stmt
    | while_stmt
    | until_stmt
    | for_stmt
    | return_stmt NEWLINE
    | expr_stmt NEWLINE
    ;

assignment_stmt
    : id_list ASSIGN expr_list
    ;

id_list
    : ID (COMMA ID)*
    ;

expr_list
    : expr (COMMA expr)*
    ;

statement_block
    : (NEWLINE | statement)+
    ;

if_stmt
    : IF expr COLON NEWLINE INDENT statement_block DEDENT
      (ELSE COLON NEWLINE INDENT statement_block DEDENT)?
    ;

while_stmt
    : WHILE expr COLON NEWLINE INDENT statement_block DEDENT
    ;

until_stmt
    : UNTIL expr COLON NEWLINE INDENT statement_block DEDENT
    ;

for_stmt
    : FOR ID IN expr COLON NEWLINE INDENT statement_block DEDENT              # ForInStmt
    | FOR ID ASSIGN expr TO expr COLON NEWLINE INDENT statement_block DEDENT  # ForRangeStmt
    | FOR ID ASSIGN expr TO expr STEP expr COLON NEWLINE INDENT statement_block DEDENT  # ForStepStmt
    ;

return_stmt
    : RETURN expr?
    ;

expr_stmt
    : expr
    ;

expr
    : pipeline_expr
    ;

pipeline_expr
    : logical_or_expr (PIPELINE logical_or_expr)*
    ;

logical_or_expr
    : logical_and_expr (OR logical_and_expr)*
    ;

logical_and_expr
    : logical_not_expr (AND logical_not_expr)*
    ;

logical_not_expr
    : NOT logical_not_expr
    | comparison_expr
    ;

comparison_expr
    : additive_expr ((EQ | NE | LT | GT | LTE | GTE | MEMBER) additive_expr)?
    ;

additive_expr
    : multiplicative_expr ((PLUS | MINUS | RSHIFT | LSHIFT) multiplicative_expr)*
    ;

multiplicative_expr
    : unary_expr ((STAR | SLASH | MODULO) unary_expr)*
    ;

unary_expr
    : MINUS unary_expr
    | PLUS unary_expr
    | primary_expr
    ;

primary_expr
    : literal                                   # LiteralExpr
    | function_call                             # FunctionCallExpr
    | list_expr                                 # ListExpr
    | cast_expr                                 # CastExpr
    | LPAREN expr RPAREN                        # ParenExpr
    | primary_expr LBRACKET expr RBRACKET       # IndexExpr
    | ID                                        # IdExpr
    ;

function_call
    : ID LPAREN arg_list? RPAREN
    ;

arg_list
    : expr (COMMA expr)*
    ;

list_expr
    : LBRACKET (expr (COMMA expr)*)? RBRACKET
    ;

cast_expr
    : LPAREN ID RPAREN expr
    ;

literal
    : INT
    | STRING
    | TRUE
    | FALSE
    | NIL
    ;

DEF         : 'def';
RETURN      : 'return';
REF         : 'ref';
IF          : 'if';
ELSE        : 'else';
WHILE       : 'while';
UNTIL       : 'until';
FOR         : 'for';
IN          : 'in';
TO          : 'to';
STEP        : 'step';
AND         : 'and';
OR          : 'or';
NOT         : 'not';
TRUE        : 'true';
FALSE       : 'false';
NIL         : 'nil';

PLUS     : '+';
MINUS    : '-';
STAR     : '*';
SLASH    : '/';
MODULO   : '%';
PIPELINE : '|>';
LSHIFT   : '<<';
RSHIFT   : '>>';
EQ       : '==';
NE       : '!=';
LTE      : '<=';
GTE      : '>=';
LT       : '<';
GT       : '>';
MEMBER   : '@';
ASSIGN   : '=';

LPAREN   : '(';
RPAREN   : ')';
LBRACKET : '[';
RBRACKET : ']';
COLON    : ':';
COMMA    : ',';

ID
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

INT
    : [0-9]+
    ;

STRING
    : '"' (~["\r\n] | '\\"')* '"'
    ;

COMMENT
    : '#' ~[\r\n]* -> skip
    ;

MULTILINE_COMMENT
    : '/*' .*? '*/' -> skip
    ;

NEWLINE
    : '\r'? '\n'
    ;

WS
    : [ \t]+ -> skip
    ;

INDENT : '<<<INDENT>>>' ;
DEDENT : '<<<DEDENT>>>' ;

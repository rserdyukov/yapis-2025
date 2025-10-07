parser grammar ExprParser;
options { tokenVocab=ExprLexer; }

program: funcDef* EOF;

funcDef
    : FUN ID LPAREN parameterList? RPAREN (OUT type)? block
    ;

block
    : LCURLY stat* RCURLY
    ;

constructibleType
    : TYPE_COLOR
    ;

type
    : TYPE_INT
    | TYPE_COLOR
    | TYPE_PIXEL
    | TYPE_IMAGE
    | TYPE_FLOAT
    ;

parameterList
    : parameter (COMMA parameter)*
    ;
    
parameter
    : type ID
    ;
    
stat
    : variableDef
    | assignment
    | ifStat
    | forStat
    | returnStat
    | expr SEMI?
    ;

variableDef: type ID (ASSIGN expr)? SEMI?;
assignment: ID ASSIGN expr SEMI?;
ifStat: IF expr THEN? block (ELSE block)?;
forStat: FOR type ID IN expr block;
returnStat: RETURN expr? SEMI?;

expr: assignmentExpr;

assignmentExpr
    : relationalExpr (ASSIGN assignmentExpr)?
    ;

relationalExpr
    : additiveExpr ((EQ_EQ | GT | LT) additiveExpr)*
    ;

additiveExpr
    : multiplicativeExpr ((PLUS | MINUS) multiplicativeExpr)*
    ;

multiplicativeExpr
    : castExpr ((DIV | MULT) castExpr)*
    ;

castExpr
    : atom (AS type)?
    ;

atom 
    : LPAREN expr RPAREN    
    | literal                       
    | ID
    | constructibleType LPAREN argumentList? RPAREN
    | atom DOT ID                                
    | atom LPAREN argumentList? RPAREN 
    ;

argumentList: expr (COMMA expr)*;
literal: INT | STRING | FLOAT;
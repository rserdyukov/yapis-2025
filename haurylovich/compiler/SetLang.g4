grammar SetLang;

tokens { INDENT, DEDENT }

@lexer::members {
  // A queue where extra tokens are pushed on (see the NEWLINE lexer rule).
  private java.util.LinkedList<Token> tokens = new java.util.LinkedList<>();
  // The stack that keeps track of the indentation level.
  private java.util.Stack<Integer> indents = new java.util.Stack<>();
  // The amount of opened braces, brackets and parenthesis.
  private int opened = 0;
  // The most recently produced token.
  private Token lastToken = null;
  @Override
  public void emit(Token t) {
    super.setToken(t);
    tokens.offer(t);
  }

  @Override
  public Token nextToken() {
    // Check if the end-of-file is ahead and there are still some DEDENTS expected.
    if (_input.LA(1) == EOF && !this.indents.isEmpty()) {
      // Remove any trailing EOF tokens from our buffer.
      for (int i = tokens.size() - 1; i >= 0; i--) {
        if (tokens.get(i).getType() == EOF) {
          tokens.remove(i);
        }
      }

      // First emit an extra line break that serves as the end of the statement.
      this.emit(commonToken(SetLangParser.NEWLINE, "\n"));

      // Now emit as much DEDENT tokens as needed.
      while (!indents.isEmpty()) {
        this.emit(createDedent());
        indents.pop();
      }

      // Put the EOF back on the token stream.
      this.emit(commonToken(SetLangParser.EOF, "<EOF>"));
    }

    Token next = super.nextToken();

    if (next.getChannel() == Token.DEFAULT_CHANNEL) {
      // Keep track of the last token on the default channel.
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

  // Calculates the indentation of the provided spaces, taking the
  // following rules into account:
  //
  // "Tabs are replaced (from left to right) by one to eight spaces
  //  such that the total number of characters up to and including
  //  the replacement is a multiple of eight [...]"
  //
  //  -- https://docs.python.org/3.1/reference/lexical_analysis.html#indentation
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

variableDeclaration
    : ID ASSIGN expr (NEWLINE | EOF)
    ;

functionDeclaration
    : FUNCTION ID LRBRACKET paramList? RRBRACKET returnType? COLON block
    ;
returnType: COLON type;

paramList
    : ID (COMMA ID)*
    ;

ifStatement
    : IF logicalExpr COLON block (ELSE COLON block)?
    ;

switchStatement
    : SWITCH ID COLON NEWLINE INDENT caseBlock+ (defaultblock)? DEDENT
    ;

caseBlock
    : CASE expr COLON block
    ;

defaultblock
    : DEFAULT COLON block
    ;

whileStatement
    : WHILE logicalExpr COLON block;

forStatement
    : FOR ID IN RANGE LRBRACKET range RRBRACKET COLON block;

range: (ID|INT) COMMA ((ID|INT) (COMMA (ID|INT))?)?| COMMA (ID|INT);

returnStatement: RETURN expr (NEWLINE | EOF);

breakStatement: BREAK (NEWLINE | EOF);

block: NEWLINE INDENT statement+ DEDENT;

expr: simpleExpr | complexExpr | functionCall | comparisonExpr| logicalExpr ;

functionCall
    : ID LRBRACKET exprList RRBRACKET
    | ID POINT LRBRACKET exprList RRBRACKET
    | ID POINT functionCall
    ;

exprList
    : expr (COMMA expr)*
    ;

logicalExpr
    : NOT? logicalOperand
    | LRBRACKET left=logicalExpr op=(AND | OR) right=logicalExpr RRBRACKET
    ;

comparisonExpr
    : LRBRACKET left=expr op=(LT | GT | LE | GE | EQUAL | NEQUAL) right=expr RRBRACKET
    ;
logicalOperand
    : 'true'
    | 'false'
    | functionCall
    | ID
    | comparisonExpr
    ;

complexExpr
    : simpleExpr
    | LRBRACKET left=complexExpr op=(PLUS | MINUS | UN | DIFF | SYMDIFF)  right=complexExpr RRBRACKET;

simpleExpr:
    | setLiteral
    | tupleLiteral
    | element
    | ID
    ;

setLiteral: LFIGBRACKET simpleExprList RFIGBRACKET   ;

tupleLiteral: LSQBRACKET simpleExprList RSQBRACKET;

simpleExprList: simpleExpr (COMMA simpleExpr)*;

element
    : INT
    | 'true'
    | 'false'
    | STRING
    ;

type: ELEMENT | SET| TUPLE;
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
//TRUE: 'true';
//FALSE: 'false';
//BOOL: TRUE|FALSE ;

ID: [a-zA-Z][a-zA-Z0-9$_]* ;

INT: [0-9]+ ;
STRING: '"' (~["\\\r\n] | '\\' .)* '"' ;
ELEMENT: 'Element';
SET: 'Set';
TUPLE: 'Tuple';
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
SYMDIFF: '/\\' ;
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
       // If we're inside a list or on a blank line, ignore all indents,
       // dedents and line breaks.
       skip();
     }
     else {
       emit(commonToken(NEWLINE, newLine));
       int indent = getIndentationCount(spaces);
       int previous = indents.isEmpty() ? 0 : indents.peek();
       if (indent == previous) {
         // skip indents of the same size as the present indent-size
         skip();
       }
       else if (indent > previous) {
         indents.push(indent);
         emit(commonToken(SetLangParser.INDENT, spaces));
       }
       else {
         // Possibly emit more than 1 DEDENT token.
         while(!indents.isEmpty() && indents.peek() > indent) {
           this.emit(createDedent());
           indents.pop();
         }
       }
     }
   }
 ;


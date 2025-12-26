export const ANTLR_GRAMMAR = `grammar Variant15;

program: functionDeclaration* EOF;

block: LBRACE statement* RBRACE;

statement
    : variableDeclaration
    | assignment
    | ifStatement
    | switchStatement
    | forStatement
    | functionCall
    | ioStatement
    | functionDeclaration
    | BREAK
    | CONTINUE
    | RETURN expression?
    | block
    ;

variableDeclaration: typeSpecifier IDENTIFIER (COMMA IDENTIFIER)* (ASSIGN expression (COMMA expression)*)?;

assignment: designator (COMMA designator)* ASSIGN expression (COMMA expression)*
          | designator INC;

designator: IDENTIFIER (LBRACK expression (COLON expression)? RBRACK)*;

ifStatement: IF expression? block (ELSE block)?;

switchStatement: SWITCH LBRACE caseBlock* defaultBlock? RBRACE;

caseBlock: CASE expression block;

defaultBlock: DEFAULT block;

forStatement: FOR (variableDeclaration | assignment)? SEMI expression? SEMI (assignment | expression)? block;

functionDeclaration: FUNC IDENTIFIER LPAREN parameterList? RPAREN typeSpecifier? block;

parameterList: parameter (COMMA parameter)*;

parameter: typeSpecifier IDENTIFIER;

functionCall: IDENTIFIER LPAREN argumentList? RPAREN;

argumentList: expression (COMMA expression)*;

ioStatement: READ LPAREN IDENTIFIER RPAREN
           | WRITE LPAREN expression RPAREN
           | PRINT LPAREN argumentList RPAREN;

expression
    : LPAREN expression RPAREN
    | expression (MULT | DIV | SPLIT) expression
    | expression (PLUS | MINUS) expression
    | expression (EQ | NEQ | LT | GT | LE | GE) expression
    | atom
    ;

atom: designator
    | STRING_LITERAL
    | CHAR_LITERAL
    | INT_LITERAL
    | BOOL_LITERAL
    | functionCall
    | LEN LPAREN expression RPAREN
    | arrayLiteral
    ;

arrayLiteral: LBRACE (expression (COMMA expression)*)? RBRACE;

typeSpecifier: LBRACK RBRACK? primitiveType LBRACK RBRACK?
             | primitiveType;

primitiveType: STRING | CHAR | RUNE | INT | BOOL | VOID;

// Lexer Rules
FUNC: 'func';
RETURN: 'return';
IF: 'if';
ELSE: 'else';
SWITCH: 'switch';
CASE: 'case';
DEFAULT: 'default';
FOR: 'for';
BREAK: 'break';
CONTINUE: 'continue';
READ: 'read';
WRITE: 'write';
PRINT: 'print';
LEN: 'len';
STRING: 'string';
CHAR: 'char';
RUNE: 'rune';
INT: 'int';
BOOL: 'bool';
VOID: 'void';

BOOL_LITERAL: 'true' | 'false';

PLUS: '+';
MINUS: '-';
MULT: '*';
SPLIT: '\\\\';
DIV: '/';
INC: '++';
ASSIGN: '=';
EQ: '==';
NEQ: '!=';
LT: '<';
GT: '>';
LE: '<=';
GE: '>=';
SEMI: ';';
COMMA: ',';
COLON: ':';
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';

IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;
INT_LITERAL: [0-9]+;
STRING_LITERAL: '"' .*? '"';
CHAR_LITERAL: '\\'' . '\\'' | '\\'' '\\\\' . '\\'';

WS: [ \\t\\r\\n]+ -> skip;
COMMENT: '//' ~[\\r\\n]* -> skip;
`;

export const EXAMPLES = {
    example1: `// Пример 1: Строки, Руны и Операции
func main() {
    char rune1, rune2 = ' ', ' '
    rune1, rune2 = 'r', '2'
    string str = "string"
    string concStr = str + rune2 //Неявное преобразование rune в string
    print(concStr) //"stringa"

    {
        concStr = "sttring"
        print(rune2) //'2'
        print(concStr) //"sttring"
    }

    print(concStr) //"stringa"

    func process(rune r, string answ) {
        for int i = 0; i < 5; i = i + 1 {
            answ = answ + r
        }
    }

    func process(rune r1, rune r2, string answ) {
        for int i = 0; i < 5; i = i + 1 {
            answ = answ + r1 + r2
        }
    }

    string answ = ""
    if rune1 == 'r' {
        process(rune1, answ) //"rrrrr"
    } else {
        process(rune1, rune2, answ) //"r2r2r2r2r2"
    }

    string[] strs = {"str1", "str2", "str3"}
    // str[0] = 's'
    // strs[0] = "str1"
    //str[0:2] = "st"
    //strs[0:2] = {"str1", "str2"}
    string[] strs1 = {"str4", "str5", "str6", "str1"}

    print(str + rune2) //string2
    print(strs + strs1) //{"str1", "str2", "str3", "str4", "str5", "str6", "str1"}
    print(strs + str) //{"str1", "str2", "str3", "string"}
    print(strs + rune1) //{"str1", "str2", "str3", "r"}

    print(str - rune1) //sting
    print(concStr - str) //a
    print(str - concStr) //string
    print(strs - "str1") //{"str2", "str3"}
    print(strs - rune1) //{"str1", "str2", "str3"}
    print(strs - strs1) //{"str2", "str3"}

    print(str * 2) //"stringstring"
    print(rune1 * 2) //"rr"
    print(strs * 2) //{"str1", "str2", "str3", "str1", "str2", "str3"}

    print(str / 2) //"str"
    print(rune1 / 2) //""
    print(strs / 2) //{"str1", "str2"}
}`,
    example2: `// Пример 2: Contains и Switch
func Contains(string str, string substr) bool {
    int substrLen = len(substr)
    switch {
        case substrLen == 0 {
            return false
        }
        case substrLen == len(str) {
            if substr == str {
                return true
            }
            return false
        }
        case substrLen > len(str) {
            return false
        }
        default {
            for int strPos = 0; strPos < len(str); strPos++ {
                // Если оставшаяся длина меньше подстроки, можно выходить
                if len(str) - strPos < substrLen {
                    return false
                }
                
                if str[strPos] == substr[0] {
                    int foundQueryLen = 0
                    for int substrPos = 0; substrPos < substrLen; substrPos++ {
                        if str[strPos+substrPos] == substr[substrPos] {
                            foundQueryLen++
                        } else {
                            break
                        }
                    }
                    if foundQueryLen == substrLen {
                        return true
                    }
                }
            }
        }
    }
    return false
}

func main() {
    bool contains
    string str = "string"

    string substr1 = "str"
    contains = Contains(str, substr1)
    print(contains) //true

    string substr2 = "g"
    contains = Contains(str, substr2)
    print(contains) //true

    string substr3 = "rang"
    contains = Contains(str, substr3)
    print(contains) //false

    string substr4 = "string"
    contains = Contains(str, substr4)
    print(contains) //true
}`,
    example3: `// Пример 3: Split и Срезы
func Split(string str, char delim, []string parts) []string{
    string newString = ""
    for int strPos = 0;strPos < len(str); strPos++ {
        if str[strPos] == delim {
            if len(newString) == 0 {
                continue
            }
            parts = parts + newString
            newString = ""
            continue
        }
        newString = newString + str[strPos]
    }
    if len(newString) > 0 {
        parts = parts + newString
    }
    return parts
}

func main() {
    []string parts = {} 
    string str = "В стране магнолий\\nплещет\\nморе"
    parts = Split(str, '\\n', parts)
    print(parts) //{"В стране магнолий", "плещет", "море"}
}`,
    errorExample1: `// Ошибка 1: Пропущена закрывающая скобка блока if
func main() {
    int x = 10
    if x > 5 {
        print("x is big")
        x = x + 1
    // Ожидается закрывающая фигурная скобка '}' перед print
    print("End")
}`,
    errorExample2: `// Ошибка 2: Неверный синтаксис цикла for (пропущены точки с запятой)
func main() {
    int i = 0
    // Ожидается формат: for int i=0; i<10; i++
    // Здесь пропущены разделители ';'
    for int i = 0 i < 10 i++ { 
        print(i)
    }
}`,
    errorExample3: `// Ошибка 3: Некорректное объявление переменной
func main() {
    string s = "hello"
    // Ошибка: ожидается имя переменной после запятой, найден знак '='
    int a, = 10 
    print(s)
}`,
    semanticError1: `// Семантическая ошибка 1: Повторное объявление переменной
func main() {
    int x = 10
    print(x)
    
    // Ошибка: переменная x уже объявлена в этой области видимости
    string x = "error" 
}`,
    semanticError2: `// Семантическая ошибка 2: Использование необъявленной переменной
func main() {
    int a = 5
    
    // Ошибка: переменная b не объявлена
    a = b + 1
    print(a)
}`,
    semanticError3: `// Семантическая ошибка 3: Конфликт сигнатур функций (Overloading)
func calculate(int x) int {
    return x * 2
}

// Ошибка: Функция с именем 'calculate' и сигнатурой 'int' уже существует
func calculate(int y) int {
    return y + 10
}

func main() {
    print(calculate(5))
}`,
    semanticError4: `// Семантическая ошибка 4: Несовпадение количества операндов
func main() {
    // 1. Ошибка при инициализации (2 переменные, 1 значение)
    int a, b = 10 
    
    // 2. Ошибка при присваивании (1 переменная, 2 значения)
    int c = 0
    c = 1, 2
}`,
    semanticError5: `// Семантическая ошибка 5: Отсутствие или дублирование функции main
func test() {
    print("No main here")
}

// Раскомментируйте, чтобы проверить ошибку "Multiple main functions"

func main() {
    print("Main 1")
}

func main() {
    print("Main 2")
}

// В данном виде ошибка: No 'main' function defined.
`,
    semanticError6: `// Семантическая ошибка 6: Конфликт сигнатур при вложенности
func helper(int x) {
    print(x)
}

func main() {
    // Ошибка: Функция 'helper' с сигнатурой 'int' уже объявлена во внешней области видимости.
    // Язык запрещает затенение функций с идентичной сигнатурой.
    func helper(int y) {
        print(y * 2)
    }
    
    helper(5)
}`,
};

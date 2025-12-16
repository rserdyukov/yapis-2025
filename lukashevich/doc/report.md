# Отчет

ФИО: Лукашевич Алина Дмитриевна
Группа: 221703  
Вариант: 9

## Спецификация разработанного языка программирования

#### Синтаксис объявления переменных:

1.  Без инициализации: `<TYPE> <VAR_NAME>;`
2.  С инициализацией: `<TYPE> <VAR_NAME> = <EXPRESSION>;`

Поддерживаемые типы: `int`, `float`, `color`, `pixel`, `image`.

#### Синтаксис объявления подпрограмм:

```text
func <FUNCTION_NAME> (<PARAM_TYPE> <PARAM_NAME>, ...) -> <RETURN_TYPE> {
    <FUNCTION_BODY>
}
```

*Примечание: Если функция ничего не возвращает, `-> <RETURN_TYPE>` опускается.*

#### Синтаксис управляющих конструкций:

1.  Цикл for (итерация по пикселям изображения):

<!-- end list -->

```text
for <TYPE> <VAR_NAME> in <IMAGE_EXPRESSION> {
    <BLOCK>
}
```

2.  Условный оператор if-else:

<!-- end list -->

```text
if <CONDITION> {
    <THEN_BLOCK>
} else {
    <ELSE_BLOCK>
}
```

3.  Возврат значения:

<!-- end list -->

```text
return <EXPRESSION>;
```

#### Синтаксис операций над данными:

1.  **Арифметические операции:**

      * Сложение: `<EXPR> + <EXPR>`
      * Вычитание: `<EXPR> - <EXPR>`
      * Умножение: `<EXPR> * <EXPR>`
      * Деление: `<EXPR> / <EXPR>`

2.  **Операции сравнения:**

      * Равно: `<EXPR> == <EXPR>` (поддерживает сравнение чисел и цветов)
      * Больше: `<EXPR> > <EXPR>`
      * Меньше: `<EXPR> < <EXPR>`

3.  **Работа с типами и объектами:**

      * Явное приведение типов: `<EXPR> as <TYPE>`
      * Доступ к полям/свойствам: `<OBJECT>.<PROPERTY>` (например, `color.R`, `pixel.x`, `image.width`)
      * Вызов методов: `<OBJECT>.<METHOD>(<ARGS>)`
      * Конструктор цвета: `color(<R>, <G>, <B>)`

4.  **Встроенные функции и методы:**

      * Вывод на экран: `print(<MSG>)`
      * Загрузка изображения: `load(<PATH>)`
      * Математика: `sqrt(<VALUE>)`
      * Сохранение изображения: `<IMAGE>.save(<PATH>)`
      * Получение пикселя: `<IMAGE>.get_pixel(<X>, <Y>)`
      * Установка цвета пикселя: `<PIXEL>.set_color(<COLOR>)`
      * Получение цвета пикселя: `<PIXEL>.get_color()`

## Описание грамматики

```antlr
grammar Expr;

// -----------------------------------------------
// ПРАВИЛА ПАРСЕРА
// -----------------------------------------------

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

// -----------------------------------------------
// ПРАВИЛА ЛЕКСЕРА
// -----------------------------------------------

FUN: 'func';
RETURN: 'return';
IF: 'if';
THEN: 'then';
ELSE: 'else';
FOR: 'for';
IN: 'in';
AS: 'as';

TYPE_INT: 'int';
TYPE_COLOR: 'color';
TYPE_PIXEL: 'pixel';
TYPE_IMAGE: 'image';
TYPE_FLOAT: 'float';

LPAREN: '(';
RPAREN: ')';
LCURLY: '{';
RCURLY: '}';
COMMA: ',';
DOT: '.';
SEMI: ';';
ASSIGN: '=';
EQ_EQ: '==';
GT: '>';
LT: '<';
PLUS: '+';
MINUS: '-';
DIV: '/';
MULT: '*';
OUT: ' -> ';

INT: [0-9]+;
FLOAT: [+-]? ([0-9]* [.])? [0-9]+;
STRING: '"' ( ~["] | '""')* '"';
ID: [a-zA-Z_\u0400-\u04ff][a-zA-Z_0-9\u0400-\u04ff]*;
COMMENT: '//' .*? '\n' -> skip;
WS: [ \t\n\r]+ -> skip;
```

## Описание разработанных классов

1.  **SemanticAnalyzer (`semantic_analyzer.py`)**: Класс, реализующий паттерн Visitor. Производит полный семантический анализ AST-дерева, проверку типов, областей видимости и корректности вызовов методов.
2.  **Compiler (`compiler.py`)**: Класс-компилятор, проходящий по AST-дереву и генерирующий код на языке IL (Intermediate Language) для платформы .NET. Управляет генерацией методов, локальных переменных и стеком вычислений.
3.  **AnalysisErrorManager (`semantic_analyzer.py`)**: Класс для сбора и управления списком ошибок (как синтаксических, так и семантических), возникающих в процессе трансляции.
4.  **SymbolInfo (`semantic_analyzer.py`)**: Класс для хранения информации о символах (переменных и функциях) в таблице символов, включая их тип, имя, параметры и состояние инициализации.
5.  **SysImage (`Runtime.cs`)**: Класс среды выполнения, обертка над системным `Bitmap`. Предоставляет API для загрузки, сохранения изображений и доступа к их размерам.
6.  **SysPixel (`Runtime.cs`)**: Класс среды выполнения, представляющий отдельный пиксель. Позволяет читать и изменять цвет в координатах изображения.
7.  **SysColor (`Runtime.cs`)**: Класс среды выполнения для представления цвета (RGB).

## Перечень генерируемых ошибок

1.  **Синтаксические ошибки**: Ошибки парсинга, несоответствие грамматике языка.
2.  **Семантические ошибки**:
    1.  Повторная инициализация функции или переменной в той же области видимости.
    2.  Несоответствие типов при присваивании (`Type mismatch`).
    3.  Использование необъявленной переменной или функции.
    4.  Присваивание значения функции (попытка записи в идентификатор функции).
    5.  Некорректное условие в `if` (ожидается `boolean`).
    6.  Ошибка оператора `for` (ожидается итерация `pixel in image`).
    7.  Оператор `return` вне функции или несоответствие возвращаемого типа.
    8.  Некорректное явное приведение типов (cast).
    9.  Вызов метода у типа, который не поддерживает методы.
    10. Неверное количество аргументов или неверные типы аргументов при вызове функций/методов.
    11. Обращение к несуществующему свойству объекта.
    12. Использование переменной до её инициализации.

## Демонстрация работы

1.  Приложение для обработки изображения (подмена цветов):

Код:

```text
func calculate_brightness(color c) -> int {
    int brightness = ((c.R + c.G + c.B) / 3) as int
    return brightness
}

func replace_color(image img, color old_color, color new_color) {
    for pixel p in img {
        color current_color = p.get_color()

        if current_color == old_color then {
            if calculate_brightness(current_color) > 50 then {
                p.set_color(new_color)
            }
        }
    }
}

func main() {
    image source_image
    color green_screen_color
    color blue_sky_color

    source_image = load("me_on_greenscreen.jpeg")
    green_screen_color = color(1, 216, 0) 
    blue_sky_color = color(0, 191, 255)   

    replace_color(source_image, green_screen_color, blue_sky_color)

    source_image.save("./results/me_on_blue.jpeg")
}
```

Вывод (картинка):

[Me on blue](../results/me_on_blue.jpeg)

2.  Приложение для обработки изображения (виньетка):

Код:

```text
func darken_pixel(color c, float factor) {
    c.R = (c.R * factor) as int
    c.G = (c.G * factor) as int
    c.B = (c.B * factor) as int
}

func apply_vignette(image img) {
    int center_x = (img.width / 2) as int
    int center_y = (img.height / 2) as int

    float max_distance = sqrt( (center_x * center_x) + (center_y * center_y) as float );

    for pixel p in img {
        int dx = p.x - center_x
        int dy = p.y - center_y
        float distance = sqrt( (dx * dx) + (dy * dy) as float );

        float darkness_factor = 1.0 - (distance / max_distance)

        if darkness_factor < 0.8 then {
            color current_color = p.get_color()
            darken_pixel(current_color, darkness_factor)
            p.set_color(current_color)
        }
    }
}

func main() {
    image my_photo

    my_photo = load("me_on_greenscreen.jpeg")
    apply_vignette(my_photo)

    my_photo.save("./results/photo_vignette.jpeg")
}
```

Вывод (картинка):

[Me with vignette](../results/photo_vignette.jpeg)

3.  Приложение для обработки изображения (наложение логотипа):

Код:

```text
func overlay_image(image base_img, image watermark_img, int offset_x, int offset_y) {
    for pixel p_watermark in watermark_img {
            int target_x = offset_x + p_watermark.x
            int target_y = offset_y + p_watermark.y

            pixel p_base = base_img.get_pixel(target_x, target_y)

            p_base.set_color(p_watermark.get_color())
    }
}

func main() {
    image photo
    image logo

    photo = load("me_on_greenscreen.jpeg")
    logo = load("watermark.jpeg")

    int pos_x = photo.width - logo.width - 10 
    int pos_y = photo.height - logo.height - 10

    overlay_image(photo, logo, pos_x, pos_y)

    photo.save("./results/photo_with_watermark.jpeg")
}
```

Вывод (картинка):

[Me with logo](../results/photo_with_watermark.jpeg)

4.  Пример проверки статического анализатора (ошибки):

Код:

```text
def darken_pixel(color c, float factor) { 
    c.R = (c.R * factor) as int
    c.G = (c.G * factor) as int
    c.B = (c.B * factor) as int
}
```

Вывод:

```text
Compiling examples/error-1.txt
Syntax error: row 1, position 0: mismatched input 'def' expecting {<EOF>, 'func'}
Error compiling examples/error-1.txt
```

5.  Пример проверки статического анализатора (ошибки):

Код:

```text
func main() {
    int x = 10;
    int y = x + undeclared_var;//undeclared variable
}
```

Вывод:

```text
Compiling examples/semantic-error-1.txt
Semantic error: row 3, position 16: Using undeclared variable 'undeclared_var'.
Error compiling examples/semantic-error-1.txt
```
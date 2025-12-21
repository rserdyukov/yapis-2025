# Отчет (Дополнение по массивам)

## Спецификация функциональности массивов

### Типы данных:
Язык поддерживает одномерные динамические массивы для любого примитивного типа. Синтаксис типа: `<PRIMITIVE_TYPE>[]`.
*   `int[]` — массив целых чисел.
*   `float[]` — массив чисел с плавающей точкой.
*   `bool[]` — массив булевых значений.
*   `str[]` — массив строк.

### Синтаксис операций над массивами:

1.  **Инициализация через литерал**: Создание массива с предопределенным набором элементов. Все элементы должны быть одного типа.
    `<TYPE>[] <VAR_NAME> = [<EXPR_1>, <EXPR_2>, ..., <EXPR_N>];`

2.  **Инициализация с выделением памяти**: Создание массива указанного размера, заполненного значениями по умолчанию (0, 0.0, false, null).
    `<TYPE>[] <VAR_NAME> = new <TYPE>[<SIZE_EXPR>];`

3.  **Доступ к элементу**: Получение или изменение элемента по его индексу. Индексация начинается с нуля. Поддерживаются отрицательные индексы для доступа с конца (`-1` — последний элемент).
    `<ARRAY_EXPR>[<INDEX_EXPR>]`

4.  **Получение среза (slice)**: Создание нового массива, содержащего копию части исходного.
    `<ARRAY_EXPR>[<START_INDEX>:<END_INDEX>]`
    *Примечание: `END_INDEX` не включается в срез. Индексы, выходящие за границы, автоматически и безопасно обрезаются до фактического размера массива.*

5.  **Получение длины**: Свойство, возвращающее текущее количество элементов в массиве.
    `<ARRAY_EXPR>.length`

6.  **Добавление элемента в конец**: Метод, добавляющий элемент в конец массива. Если внутренней емкости недостаточно, происходит автоматическое перераспределение памяти.
    `<ARRAY_EXPR>.append(<ELEMENT_EXPR>);`

7.  **Разворот массива**: Метод, изменяющий исходный массив, располагая его элементы в обратном порядке.
    `<ARRAY_EXPR>.reverse();`

## Описание изменений в грамматике
(По сравнению с грамматикой, представленной в основном отчете)

### Новые правила

```antlr
// Правило для вызова методов массива (.append, .reverse)
arrayStatement
    : expression DOT APPEND LPAREN expression RPAREN SEMI
    | expression DOT REVERSE LPAREN RPAREN SEMI
    ;
```

### Измененные правила

```antlr
// В `statement` добавлена поддержка операций с массивами.
// И `assignmentStatement` был удален в пользу более общего `expression`.
statement
    : variableDeclaration
    | assignmentStatement // assignmentStatement был заменен более общей логикой
    | ...
    | arrayStatement // Добавлено
    ;

// Правило `expression` значительно расширено для поддержки
// доступа к элементам, срезов и получения длины.
expression
    : atom
    | expression LBRACK expression RBRACK                  // Добавлено: Доступ по индексу
    | expression LBRACK expression COLON expression RBRACK // Добавлено: Создание среза
    | expression DOT LENGTH                                // Добавлено: Получение длины
    ...
    ;

// Правило `atom` теперь включает литералы массивов и оператор `new`.
atom
    : ...
    | LBRACK (expression (COMMA expression)*)? RBRACK // Добавлено: Литерал массива
    | NEW type LBRACK atom RBRACK                     // Добавлено: new type[size]
    ;

// Правило `type` теперь поддерживает объявление типа массива.
type
    : INT | FLOAT | BOOL | STRING
    | type LBRACK RBRACK // Добавлено
    ;
```

### Новые лексемы (токены)

```antlr
LBRACK: '[';       // Квадратные скобки
RBRACK: ']';
COLON: ':';        // Двоеточие для срезов
DOT: '.';          // Точка для доступа к методам/свойствам
NEW: 'new';        // Ключевое слово для выделения памяти
LENGTH: 'length';  // Свойство длины
APPEND: 'append';  // Метод добавления
REVERSE: 'reverse';// Метод разворота
```

## Описание разработанных классов (в контексте массивов)

1.  **`MathPLSemanticAnalyzer`**:
    *   Добавлена поддержка нового типа `ArrayType`.
    *   Реализована проверка типов для литералов массивов (все элементы должны быть одного типа).
    *   Добавлены проверки для операций индексации (база должна быть массивом, индекс — `int`).
    *   Проверяет корректность вызовов методов `.append()` и `.reverse()` и свойства `.length`.

2.  **`WatCodeGenerator`**:
    *   Реализована модель управления памятью в куче (heap) с помощью `malloc`.
    *   Сгенерированы внутренние вспомогательные функции на WAT для операций с массивами: `$slice_i32/f64`, `$append_i32/f64`, `$reverse_i32/f64`, `$normalize_index`, `$check_bounds`.
    *   Добавлена логика генерации кода для создания массивов (`new` и литералы), вычисления смещений для доступа к элементам и вызова вспомогательных функций.

3.  **`MathPLType`**, **`ArrayType`**:
    *   Система типов была расширена классом `ArrayType`, который хранит информацию о типе элементов массива. Это позволяет анализатору корректно работать с вложенными типами, например `int[][]`.

## Перечень генерируемых ошибок (связанных с массивами)

1.  `Array elements must be of the same type` — элементы в литерале массива имеют разные типы.
2.  `Base of an index operation must be an array type` — попытка использовать `[]` на переменной, не являющейся массивом (например, `int x = 5; x[0];`).
3.  `Index and slice bounds must be of type INT` — использование `float` или `str` в качестве индекса.
4.  `Type mismatch` — попытка присвоить массив одного типа переменной другого типа (`int[] a = float_array;`).
5.  `Method 'append' requires 1 argument(s), but got N` — неверное количество аргументов у `append`.
6.  `Method '...' not found for type '...'` — попытка вызвать метод массива у примитивного типа.

## Демонстрация работы компилятора

### Пример 1: Корректный код с массивами

*   **Исходный код (`extra_task_examples/example_1.txt`)**
    ```
    int[] numbers = [10, 20, 30, 40, 50];
    int len = numbers.length;
    print("Initial length: " + (str)len);
    int first = numbers[0];
    int last = numbers[-1];
    print("First element: " + (str)first);
    print("Last element: " + (str)last);
    print("Changing element at index 1...");
    numbers[1] = 25;
    int changed = numbers[1];
    print("New element at index 1: " + (str)changed);

*   **Вывод через `wasm_runner/`**

![](extra_correct_example.png)

### Пример 2: Синтаксические ошибки с массивами
*   **Исходный код (`extra_task_examples/syntax_error_examples.txt`)**
    ```
    int[] a = {1, 2, 3};
    float[] b = [1.0, 2.0, 3.0,];
    int c[] = [1, 2, 3];
    int[] d = [1 2 3];
    int[] e = [10, 20];
    int val = e(0);
    int[] f = e[0; 1];
    int[] g = [1];
    int len = g.length();
    g.append 100;
    ```

*   **Вывод компилятора**
    ```
      Starting syntax check for: D:\Uni\SEM7\YAPIS\yapis-2025\avrukevich\compiler\..\examples\extra_task_examples\syntax_error_examples.txt
      Syntax check failed. Errors found:
        SYNTAX ERROR on line 6:12 -> mismatched input ',' expecting ';'
        SYNTAX ERROR on line 10:27 -> mismatched input ']' expecting {'(', '[', 'not', 'new', BOOL_LITERAL, ID, INT_LITERAL, FLOAT_LITERAL, STRING_LITERAL, '++', '--', '-'}
        SYNTAX ERROR on line 14:5 -> mismatched input '[' expecting {';', '='}
        SYNTAX ERROR on line 17:13 -> mismatched input '2' expecting {']', ','}
        SYNTAX ERROR on line 28:13 -> no viable alternative at input '[0;'
        SYNTAX ERROR on line 36:18 -> missing ';' at '('
        SYNTAX ERROR on line 39:9 -> missing '(' at '100'
        SYNTAX ERROR on line 39:12 -> missing ')' at ';'
    ```

### Пример 3: Семантические ошибки с массивами
*   **Исходный код (`extra_task_examples/semantic_error_examples.txt`)**
    ```java
    int[] mixed_type_array = [1, 2.5, 3];.
    str[] string_array = ["a", "b", "c"];
    string_array[0] = 123;  получен int.

    int not_an_array = 10;
    not_an_array.append(5);

    int[] arr1 = [1, 2];
    int[] arr2 = [3, 4];
    int[] result = arr1 + arr2; 

    if (arr1) then {
        print("This should not work");
    }

    arr1[0.5] = 1;
    arr1["zero"] = 1;

    func takes_int(int x) -> void {
        print("Received int");
    }

    int[] array_arg = [100];
    takes_int(array_arg);
    ```

*   **Вывод компилятора**
    ```
      Starting semantic analysis...
      Compilation failed. Errors found:
        SEMANTIC ERROR on line 8:29 -> Array literal type mismatch. Expected 'INT', got 'FLOAT'
        SEMANTIC ERROR on line 12:0 -> Type mismatch: Cannot assign 'INT' to 'STRING'
        SEMANTIC ERROR on line 19:0 -> Method 'append' is undefined for type 'INT'
        SEMANTIC ERROR on line 25:15 -> Operator '+' requires numeric operands
        SEMANTIC ERROR on line 28:4 -> 'If' condition must be of type BOOL, but got 'INT[]'
        SEMANTIC ERROR on line 36:5 -> Array index must be INT
        SEMANTIC ERROR on line 39:5 -> Array index must be INT
        SEMANTIC ERROR on line 44:0 -> Functions must be defined before any statements in the global scope
        SEMANTIC ERROR on line 49:10 -> Argument 1 of 'takes_int': Expected type 'INT', but got 'INT[]'
    ```
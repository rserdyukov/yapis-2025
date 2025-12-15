BUILTIN_FUNCTIONS = ['read', 'write', 'len', 'substr', 'replace', 'split']

TYPE_CHAR = 'char'
TYPE_STRING = 'string'
TYPE_ARRAY = 'array'
TYPE_INT = 'int'
TYPE_BOOL = 'bool'
TYPE_UNKNOWN = 'unknown'
TYPE_VOID = "void"

ARITHMETIC_OPS = ['+', '-', '*', '/']
COMPARISON_OPS = ['==', '!=', '<', '>']
LOGICAL_OPS = ['and', 'or', 'not']

JVM_TYPE_DESCRIPTORS = {
    TYPE_INT: 'I',
    TYPE_CHAR: 'C',
    TYPE_STRING: 'Ljava/lang/String;',
    TYPE_ARRAY: '[Ljava/lang/String;',
    TYPE_BOOL: 'Z',
}

JVM_TYPE_NAMES = {
    TYPE_INT: 'int',
    TYPE_CHAR: 'char',
    TYPE_STRING: 'java/lang/String',
    TYPE_ARRAY: '[Ljava/lang/String;',
    TYPE_BOOL: 'boolean',
}
# Generated from ./ExprParser.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys

if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO


def serializedATN():
    return [
        4,
        1,
        34,
        216,
        2,
        0,
        7,
        0,
        2,
        1,
        7,
        1,
        2,
        2,
        7,
        2,
        2,
        3,
        7,
        3,
        2,
        4,
        7,
        4,
        2,
        5,
        7,
        5,
        2,
        6,
        7,
        6,
        2,
        7,
        7,
        7,
        2,
        8,
        7,
        8,
        2,
        9,
        7,
        9,
        2,
        10,
        7,
        10,
        2,
        11,
        7,
        11,
        2,
        12,
        7,
        12,
        2,
        13,
        7,
        13,
        2,
        14,
        7,
        14,
        2,
        15,
        7,
        15,
        2,
        16,
        7,
        16,
        2,
        17,
        7,
        17,
        2,
        18,
        7,
        18,
        2,
        19,
        7,
        19,
        2,
        20,
        7,
        20,
        2,
        21,
        7,
        21,
        1,
        0,
        5,
        0,
        46,
        8,
        0,
        10,
        0,
        12,
        0,
        49,
        9,
        0,
        1,
        0,
        1,
        0,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        3,
        1,
        57,
        8,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        3,
        1,
        62,
        8,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        1,
        2,
        5,
        2,
        68,
        8,
        2,
        10,
        2,
        12,
        2,
        71,
        9,
        2,
        1,
        2,
        1,
        2,
        1,
        3,
        1,
        3,
        1,
        4,
        1,
        4,
        1,
        5,
        1,
        5,
        1,
        5,
        5,
        5,
        82,
        8,
        5,
        10,
        5,
        12,
        5,
        85,
        9,
        5,
        1,
        6,
        1,
        6,
        1,
        6,
        1,
        7,
        1,
        7,
        1,
        7,
        1,
        7,
        1,
        7,
        1,
        7,
        1,
        7,
        3,
        7,
        97,
        8,
        7,
        3,
        7,
        99,
        8,
        7,
        1,
        8,
        1,
        8,
        1,
        8,
        1,
        8,
        3,
        8,
        105,
        8,
        8,
        1,
        8,
        3,
        8,
        108,
        8,
        8,
        1,
        9,
        1,
        9,
        1,
        9,
        1,
        9,
        3,
        9,
        114,
        8,
        9,
        1,
        10,
        1,
        10,
        1,
        10,
        3,
        10,
        119,
        8,
        10,
        1,
        10,
        1,
        10,
        1,
        10,
        3,
        10,
        124,
        8,
        10,
        1,
        11,
        1,
        11,
        1,
        11,
        1,
        11,
        1,
        11,
        1,
        11,
        1,
        11,
        1,
        12,
        1,
        12,
        3,
        12,
        135,
        8,
        12,
        1,
        12,
        3,
        12,
        138,
        8,
        12,
        1,
        13,
        1,
        13,
        1,
        14,
        1,
        14,
        1,
        14,
        3,
        14,
        145,
        8,
        14,
        1,
        15,
        1,
        15,
        1,
        15,
        5,
        15,
        150,
        8,
        15,
        10,
        15,
        12,
        15,
        153,
        9,
        15,
        1,
        16,
        1,
        16,
        1,
        16,
        5,
        16,
        158,
        8,
        16,
        10,
        16,
        12,
        16,
        161,
        9,
        16,
        1,
        17,
        1,
        17,
        1,
        17,
        5,
        17,
        166,
        8,
        17,
        10,
        17,
        12,
        17,
        169,
        9,
        17,
        1,
        18,
        1,
        18,
        1,
        18,
        3,
        18,
        174,
        8,
        18,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        3,
        19,
        186,
        8,
        19,
        1,
        19,
        1,
        19,
        3,
        19,
        190,
        8,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        1,
        19,
        3,
        19,
        198,
        8,
        19,
        1,
        19,
        5,
        19,
        201,
        8,
        19,
        10,
        19,
        12,
        19,
        204,
        9,
        19,
        1,
        20,
        1,
        20,
        1,
        20,
        5,
        20,
        209,
        8,
        20,
        10,
        20,
        12,
        20,
        212,
        9,
        20,
        1,
        21,
        1,
        21,
        1,
        21,
        0,
        1,
        38,
        22,
        0,
        2,
        4,
        6,
        8,
        10,
        12,
        14,
        16,
        18,
        20,
        22,
        24,
        26,
        28,
        30,
        32,
        34,
        36,
        38,
        40,
        42,
        0,
        5,
        1,
        0,
        16,
        20,
        1,
        0,
        22,
        24,
        1,
        0,
        25,
        26,
        1,
        0,
        27,
        28,
        1,
        0,
        30,
        32,
        224,
        0,
        47,
        1,
        0,
        0,
        0,
        2,
        52,
        1,
        0,
        0,
        0,
        4,
        65,
        1,
        0,
        0,
        0,
        6,
        74,
        1,
        0,
        0,
        0,
        8,
        76,
        1,
        0,
        0,
        0,
        10,
        78,
        1,
        0,
        0,
        0,
        12,
        86,
        1,
        0,
        0,
        0,
        14,
        98,
        1,
        0,
        0,
        0,
        16,
        100,
        1,
        0,
        0,
        0,
        18,
        109,
        1,
        0,
        0,
        0,
        20,
        115,
        1,
        0,
        0,
        0,
        22,
        125,
        1,
        0,
        0,
        0,
        24,
        132,
        1,
        0,
        0,
        0,
        26,
        139,
        1,
        0,
        0,
        0,
        28,
        141,
        1,
        0,
        0,
        0,
        30,
        146,
        1,
        0,
        0,
        0,
        32,
        154,
        1,
        0,
        0,
        0,
        34,
        162,
        1,
        0,
        0,
        0,
        36,
        170,
        1,
        0,
        0,
        0,
        38,
        189,
        1,
        0,
        0,
        0,
        40,
        205,
        1,
        0,
        0,
        0,
        42,
        213,
        1,
        0,
        0,
        0,
        44,
        46,
        3,
        2,
        1,
        0,
        45,
        44,
        1,
        0,
        0,
        0,
        46,
        49,
        1,
        0,
        0,
        0,
        47,
        45,
        1,
        0,
        0,
        0,
        47,
        48,
        1,
        0,
        0,
        0,
        48,
        50,
        1,
        0,
        0,
        0,
        49,
        47,
        1,
        0,
        0,
        0,
        50,
        51,
        5,
        0,
        0,
        1,
        51,
        1,
        1,
        0,
        0,
        0,
        52,
        53,
        5,
        1,
        0,
        0,
        53,
        54,
        5,
        33,
        0,
        0,
        54,
        56,
        5,
        9,
        0,
        0,
        55,
        57,
        3,
        10,
        5,
        0,
        56,
        55,
        1,
        0,
        0,
        0,
        56,
        57,
        1,
        0,
        0,
        0,
        57,
        58,
        1,
        0,
        0,
        0,
        58,
        61,
        5,
        10,
        0,
        0,
        59,
        60,
        5,
        29,
        0,
        0,
        60,
        62,
        3,
        8,
        4,
        0,
        61,
        59,
        1,
        0,
        0,
        0,
        61,
        62,
        1,
        0,
        0,
        0,
        62,
        63,
        1,
        0,
        0,
        0,
        63,
        64,
        3,
        4,
        2,
        0,
        64,
        3,
        1,
        0,
        0,
        0,
        65,
        69,
        5,
        11,
        0,
        0,
        66,
        68,
        3,
        14,
        7,
        0,
        67,
        66,
        1,
        0,
        0,
        0,
        68,
        71,
        1,
        0,
        0,
        0,
        69,
        67,
        1,
        0,
        0,
        0,
        69,
        70,
        1,
        0,
        0,
        0,
        70,
        72,
        1,
        0,
        0,
        0,
        71,
        69,
        1,
        0,
        0,
        0,
        72,
        73,
        5,
        12,
        0,
        0,
        73,
        5,
        1,
        0,
        0,
        0,
        74,
        75,
        5,
        17,
        0,
        0,
        75,
        7,
        1,
        0,
        0,
        0,
        76,
        77,
        7,
        0,
        0,
        0,
        77,
        9,
        1,
        0,
        0,
        0,
        78,
        83,
        3,
        12,
        6,
        0,
        79,
        80,
        5,
        13,
        0,
        0,
        80,
        82,
        3,
        12,
        6,
        0,
        81,
        79,
        1,
        0,
        0,
        0,
        82,
        85,
        1,
        0,
        0,
        0,
        83,
        81,
        1,
        0,
        0,
        0,
        83,
        84,
        1,
        0,
        0,
        0,
        84,
        11,
        1,
        0,
        0,
        0,
        85,
        83,
        1,
        0,
        0,
        0,
        86,
        87,
        3,
        8,
        4,
        0,
        87,
        88,
        5,
        33,
        0,
        0,
        88,
        13,
        1,
        0,
        0,
        0,
        89,
        99,
        3,
        16,
        8,
        0,
        90,
        99,
        3,
        18,
        9,
        0,
        91,
        99,
        3,
        20,
        10,
        0,
        92,
        99,
        3,
        22,
        11,
        0,
        93,
        99,
        3,
        24,
        12,
        0,
        94,
        96,
        3,
        26,
        13,
        0,
        95,
        97,
        5,
        15,
        0,
        0,
        96,
        95,
        1,
        0,
        0,
        0,
        96,
        97,
        1,
        0,
        0,
        0,
        97,
        99,
        1,
        0,
        0,
        0,
        98,
        89,
        1,
        0,
        0,
        0,
        98,
        90,
        1,
        0,
        0,
        0,
        98,
        91,
        1,
        0,
        0,
        0,
        98,
        92,
        1,
        0,
        0,
        0,
        98,
        93,
        1,
        0,
        0,
        0,
        98,
        94,
        1,
        0,
        0,
        0,
        99,
        15,
        1,
        0,
        0,
        0,
        100,
        101,
        3,
        8,
        4,
        0,
        101,
        104,
        5,
        33,
        0,
        0,
        102,
        103,
        5,
        21,
        0,
        0,
        103,
        105,
        3,
        26,
        13,
        0,
        104,
        102,
        1,
        0,
        0,
        0,
        104,
        105,
        1,
        0,
        0,
        0,
        105,
        107,
        1,
        0,
        0,
        0,
        106,
        108,
        5,
        15,
        0,
        0,
        107,
        106,
        1,
        0,
        0,
        0,
        107,
        108,
        1,
        0,
        0,
        0,
        108,
        17,
        1,
        0,
        0,
        0,
        109,
        110,
        5,
        33,
        0,
        0,
        110,
        111,
        5,
        21,
        0,
        0,
        111,
        113,
        3,
        26,
        13,
        0,
        112,
        114,
        5,
        15,
        0,
        0,
        113,
        112,
        1,
        0,
        0,
        0,
        113,
        114,
        1,
        0,
        0,
        0,
        114,
        19,
        1,
        0,
        0,
        0,
        115,
        116,
        5,
        3,
        0,
        0,
        116,
        118,
        3,
        26,
        13,
        0,
        117,
        119,
        5,
        4,
        0,
        0,
        118,
        117,
        1,
        0,
        0,
        0,
        118,
        119,
        1,
        0,
        0,
        0,
        119,
        120,
        1,
        0,
        0,
        0,
        120,
        123,
        3,
        4,
        2,
        0,
        121,
        122,
        5,
        5,
        0,
        0,
        122,
        124,
        3,
        4,
        2,
        0,
        123,
        121,
        1,
        0,
        0,
        0,
        123,
        124,
        1,
        0,
        0,
        0,
        124,
        21,
        1,
        0,
        0,
        0,
        125,
        126,
        5,
        6,
        0,
        0,
        126,
        127,
        3,
        8,
        4,
        0,
        127,
        128,
        5,
        33,
        0,
        0,
        128,
        129,
        5,
        7,
        0,
        0,
        129,
        130,
        3,
        26,
        13,
        0,
        130,
        131,
        3,
        4,
        2,
        0,
        131,
        23,
        1,
        0,
        0,
        0,
        132,
        134,
        5,
        2,
        0,
        0,
        133,
        135,
        3,
        26,
        13,
        0,
        134,
        133,
        1,
        0,
        0,
        0,
        134,
        135,
        1,
        0,
        0,
        0,
        135,
        137,
        1,
        0,
        0,
        0,
        136,
        138,
        5,
        15,
        0,
        0,
        137,
        136,
        1,
        0,
        0,
        0,
        137,
        138,
        1,
        0,
        0,
        0,
        138,
        25,
        1,
        0,
        0,
        0,
        139,
        140,
        3,
        28,
        14,
        0,
        140,
        27,
        1,
        0,
        0,
        0,
        141,
        144,
        3,
        30,
        15,
        0,
        142,
        143,
        5,
        21,
        0,
        0,
        143,
        145,
        3,
        28,
        14,
        0,
        144,
        142,
        1,
        0,
        0,
        0,
        144,
        145,
        1,
        0,
        0,
        0,
        145,
        29,
        1,
        0,
        0,
        0,
        146,
        151,
        3,
        32,
        16,
        0,
        147,
        148,
        7,
        1,
        0,
        0,
        148,
        150,
        3,
        32,
        16,
        0,
        149,
        147,
        1,
        0,
        0,
        0,
        150,
        153,
        1,
        0,
        0,
        0,
        151,
        149,
        1,
        0,
        0,
        0,
        151,
        152,
        1,
        0,
        0,
        0,
        152,
        31,
        1,
        0,
        0,
        0,
        153,
        151,
        1,
        0,
        0,
        0,
        154,
        159,
        3,
        34,
        17,
        0,
        155,
        156,
        7,
        2,
        0,
        0,
        156,
        158,
        3,
        34,
        17,
        0,
        157,
        155,
        1,
        0,
        0,
        0,
        158,
        161,
        1,
        0,
        0,
        0,
        159,
        157,
        1,
        0,
        0,
        0,
        159,
        160,
        1,
        0,
        0,
        0,
        160,
        33,
        1,
        0,
        0,
        0,
        161,
        159,
        1,
        0,
        0,
        0,
        162,
        167,
        3,
        36,
        18,
        0,
        163,
        164,
        7,
        3,
        0,
        0,
        164,
        166,
        3,
        36,
        18,
        0,
        165,
        163,
        1,
        0,
        0,
        0,
        166,
        169,
        1,
        0,
        0,
        0,
        167,
        165,
        1,
        0,
        0,
        0,
        167,
        168,
        1,
        0,
        0,
        0,
        168,
        35,
        1,
        0,
        0,
        0,
        169,
        167,
        1,
        0,
        0,
        0,
        170,
        173,
        3,
        38,
        19,
        0,
        171,
        172,
        5,
        8,
        0,
        0,
        172,
        174,
        3,
        8,
        4,
        0,
        173,
        171,
        1,
        0,
        0,
        0,
        173,
        174,
        1,
        0,
        0,
        0,
        174,
        37,
        1,
        0,
        0,
        0,
        175,
        176,
        6,
        19,
        -1,
        0,
        176,
        177,
        5,
        9,
        0,
        0,
        177,
        178,
        3,
        26,
        13,
        0,
        178,
        179,
        5,
        10,
        0,
        0,
        179,
        190,
        1,
        0,
        0,
        0,
        180,
        190,
        3,
        42,
        21,
        0,
        181,
        190,
        5,
        33,
        0,
        0,
        182,
        183,
        3,
        6,
        3,
        0,
        183,
        185,
        5,
        9,
        0,
        0,
        184,
        186,
        3,
        40,
        20,
        0,
        185,
        184,
        1,
        0,
        0,
        0,
        185,
        186,
        1,
        0,
        0,
        0,
        186,
        187,
        1,
        0,
        0,
        0,
        187,
        188,
        5,
        10,
        0,
        0,
        188,
        190,
        1,
        0,
        0,
        0,
        189,
        175,
        1,
        0,
        0,
        0,
        189,
        180,
        1,
        0,
        0,
        0,
        189,
        181,
        1,
        0,
        0,
        0,
        189,
        182,
        1,
        0,
        0,
        0,
        190,
        202,
        1,
        0,
        0,
        0,
        191,
        192,
        10,
        2,
        0,
        0,
        192,
        193,
        5,
        14,
        0,
        0,
        193,
        201,
        5,
        33,
        0,
        0,
        194,
        195,
        10,
        1,
        0,
        0,
        195,
        197,
        5,
        9,
        0,
        0,
        196,
        198,
        3,
        40,
        20,
        0,
        197,
        196,
        1,
        0,
        0,
        0,
        197,
        198,
        1,
        0,
        0,
        0,
        198,
        199,
        1,
        0,
        0,
        0,
        199,
        201,
        5,
        10,
        0,
        0,
        200,
        191,
        1,
        0,
        0,
        0,
        200,
        194,
        1,
        0,
        0,
        0,
        201,
        204,
        1,
        0,
        0,
        0,
        202,
        200,
        1,
        0,
        0,
        0,
        202,
        203,
        1,
        0,
        0,
        0,
        203,
        39,
        1,
        0,
        0,
        0,
        204,
        202,
        1,
        0,
        0,
        0,
        205,
        210,
        3,
        26,
        13,
        0,
        206,
        207,
        5,
        13,
        0,
        0,
        207,
        209,
        3,
        26,
        13,
        0,
        208,
        206,
        1,
        0,
        0,
        0,
        209,
        212,
        1,
        0,
        0,
        0,
        210,
        208,
        1,
        0,
        0,
        0,
        210,
        211,
        1,
        0,
        0,
        0,
        211,
        41,
        1,
        0,
        0,
        0,
        212,
        210,
        1,
        0,
        0,
        0,
        213,
        214,
        7,
        4,
        0,
        0,
        214,
        43,
        1,
        0,
        0,
        0,
        25,
        47,
        56,
        61,
        69,
        83,
        96,
        98,
        104,
        107,
        113,
        118,
        123,
        134,
        137,
        144,
        151,
        159,
        167,
        173,
        185,
        189,
        197,
        200,
        202,
        210,
    ]


class ExprParser(Parser):

    grammarFileName = "ExprParser.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [DFA(ds, i) for i, ds in enumerate(atn.decisionToState)]

    sharedContextCache = PredictionContextCache()

    literalNames = [
        "<INVALID>",
        "'func'",
        "'return'",
        "'if'",
        "'then'",
        "'else'",
        "'for'",
        "'in'",
        "'as'",
        "'('",
        "')'",
        "'{'",
        "'}'",
        "','",
        "'.'",
        "';'",
        "'int'",
        "'color'",
        "'pixel'",
        "'image'",
        "'float'",
        "'='",
        "'=='",
        "'>'",
        "'<'",
        "'+'",
        "'-'",
        "'/'",
        "'*'",
        "' -> '",
    ]

    symbolicNames = [
        "<INVALID>",
        "FUN",
        "RETURN",
        "IF",
        "THEN",
        "ELSE",
        "FOR",
        "IN",
        "AS",
        "LPAREN",
        "RPAREN",
        "LCURLY",
        "RCURLY",
        "COMMA",
        "DOT",
        "SEMI",
        "TYPE_INT",
        "TYPE_COLOR",
        "TYPE_PIXEL",
        "TYPE_IMAGE",
        "TYPE_FLOAT",
        "ASSIGN",
        "EQ_EQ",
        "GT",
        "LT",
        "PLUS",
        "MINUS",
        "DIV",
        "MULT",
        "OUT",
        "INT",
        "FLOAT",
        "STRING",
        "ID",
        "WS",
    ]

    RULE_program = 0
    RULE_funcDef = 1
    RULE_block = 2
    RULE_constructibleType = 3
    RULE_type = 4
    RULE_parameterList = 5
    RULE_parameter = 6
    RULE_stat = 7
    RULE_variableDef = 8
    RULE_assignment = 9
    RULE_ifStat = 10
    RULE_forStat = 11
    RULE_returnStat = 12
    RULE_expr = 13
    RULE_assignmentExpr = 14
    RULE_relationalExpr = 15
    RULE_additiveExpr = 16
    RULE_multiplicativeExpr = 17
    RULE_castExpr = 18
    RULE_atom = 19
    RULE_argumentList = 20
    RULE_literal = 21

    ruleNames = [
        "program",
        "funcDef",
        "block",
        "constructibleType",
        "type",
        "parameterList",
        "parameter",
        "stat",
        "variableDef",
        "assignment",
        "ifStat",
        "forStat",
        "returnStat",
        "expr",
        "assignmentExpr",
        "relationalExpr",
        "additiveExpr",
        "multiplicativeExpr",
        "castExpr",
        "atom",
        "argumentList",
        "literal",
    ]

    EOF = Token.EOF
    FUN = 1
    RETURN = 2
    IF = 3
    THEN = 4
    ELSE = 5
    FOR = 6
    IN = 7
    AS = 8
    LPAREN = 9
    RPAREN = 10
    LCURLY = 11
    RCURLY = 12
    COMMA = 13
    DOT = 14
    SEMI = 15
    TYPE_INT = 16
    TYPE_COLOR = 17
    TYPE_PIXEL = 18
    TYPE_IMAGE = 19
    TYPE_FLOAT = 20
    ASSIGN = 21
    EQ_EQ = 22
    GT = 23
    LT = 24
    PLUS = 25
    MINUS = 26
    DIV = 27
    MULT = 28
    OUT = 29
    INT = 30
    FLOAT = 31
    STRING = 32
    ID = 33
    WS = 34

    def __init__(self, input: TokenStream, output: TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(
            self, self.atn, self.decisionsToDFA, self.sharedContextCache
        )
        self._predicates = None

    class ProgramContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(ExprParser.EOF, 0)

        def funcDef(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(ExprParser.FuncDefContext)
            else:
                return self.getTypedRuleContext(ExprParser.FuncDefContext, i)

        def getRuleIndex(self):
            return ExprParser.RULE_program

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterProgram"):
                listener.enterProgram(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitProgram"):
                listener.exitProgram(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitProgram"):
                return visitor.visitProgram(self)
            else:
                return visitor.visitChildren(self)

    def program(self):

        localctx = ExprParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 47
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == 1:
                self.state = 44
                self.funcDef()
                self.state = 49
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 50
            self.match(ExprParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FuncDefContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FUN(self):
            return self.getToken(ExprParser.FUN, 0)

        def ID(self):
            return self.getToken(ExprParser.ID, 0)

        def LPAREN(self):
            return self.getToken(ExprParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(ExprParser.RPAREN, 0)

        def block(self):
            return self.getTypedRuleContext(ExprParser.BlockContext, 0)

        def parameterList(self):
            return self.getTypedRuleContext(ExprParser.ParameterListContext, 0)

        def OUT(self):
            return self.getToken(ExprParser.OUT, 0)

        def type_(self):
            return self.getTypedRuleContext(ExprParser.TypeContext, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_funcDef

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterFuncDef"):
                listener.enterFuncDef(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitFuncDef"):
                listener.exitFuncDef(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitFuncDef"):
                return visitor.visitFuncDef(self)
            else:
                return visitor.visitChildren(self)

    def funcDef(self):

        localctx = ExprParser.FuncDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_funcDef)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            self.match(ExprParser.FUN)
            self.state = 53
            self.match(ExprParser.ID)
            self.state = 54
            self.match(ExprParser.LPAREN)
            self.state = 56
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((_la) & ~0x3F) == 0 and ((1 << _la) & 2031616) != 0:
                self.state = 55
                self.parameterList()

            self.state = 58
            self.match(ExprParser.RPAREN)
            self.state = 61
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == 29:
                self.state = 59
                self.match(ExprParser.OUT)
                self.state = 60
                self.type_()

            self.state = 63
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class BlockContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LCURLY(self):
            return self.getToken(ExprParser.LCURLY, 0)

        def RCURLY(self):
            return self.getToken(ExprParser.RCURLY, 0)

        def stat(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(ExprParser.StatContext)
            else:
                return self.getTypedRuleContext(ExprParser.StatContext, i)

        def getRuleIndex(self):
            return ExprParser.RULE_block

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterBlock"):
                listener.enterBlock(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitBlock"):
                listener.exitBlock(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitBlock"):
                return visitor.visitBlock(self)
            else:
                return visitor.visitChildren(self)

    def block(self):

        localctx = ExprParser.BlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_block)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 65
            self.match(ExprParser.LCURLY)
            self.state = 69
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((_la) & ~0x3F) == 0 and ((1 << _la) & 16108159564) != 0:
                self.state = 66
                self.stat()
                self.state = 71
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 72
            self.match(ExprParser.RCURLY)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ConstructibleTypeContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TYPE_COLOR(self):
            return self.getToken(ExprParser.TYPE_COLOR, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_constructibleType

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterConstructibleType"):
                listener.enterConstructibleType(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitConstructibleType"):
                listener.exitConstructibleType(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitConstructibleType"):
                return visitor.visitConstructibleType(self)
            else:
                return visitor.visitChildren(self)

    def constructibleType(self):

        localctx = ExprParser.ConstructibleTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_constructibleType)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74
            self.match(ExprParser.TYPE_COLOR)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TypeContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TYPE_INT(self):
            return self.getToken(ExprParser.TYPE_INT, 0)

        def TYPE_COLOR(self):
            return self.getToken(ExprParser.TYPE_COLOR, 0)

        def TYPE_PIXEL(self):
            return self.getToken(ExprParser.TYPE_PIXEL, 0)

        def TYPE_IMAGE(self):
            return self.getToken(ExprParser.TYPE_IMAGE, 0)

        def TYPE_FLOAT(self):
            return self.getToken(ExprParser.TYPE_FLOAT, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_type

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterType"):
                listener.enterType(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitType"):
                listener.exitType(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitType"):
                return visitor.visitType(self)
            else:
                return visitor.visitChildren(self)

    def type_(self):

        localctx = ExprParser.TypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_type)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 76
            _la = self._input.LA(1)
            if not ((((_la) & ~0x3F) == 0 and ((1 << _la) & 2031616) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ParameterListContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def parameter(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(ExprParser.ParameterContext)
            else:
                return self.getTypedRuleContext(ExprParser.ParameterContext, i)

        def COMMA(self, i: int = None):
            if i is None:
                return self.getTokens(ExprParser.COMMA)
            else:
                return self.getToken(ExprParser.COMMA, i)

        def getRuleIndex(self):
            return ExprParser.RULE_parameterList

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterParameterList"):
                listener.enterParameterList(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitParameterList"):
                listener.exitParameterList(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitParameterList"):
                return visitor.visitParameterList(self)
            else:
                return visitor.visitChildren(self)

    def parameterList(self):

        localctx = ExprParser.ParameterListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_parameterList)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.parameter()
            self.state = 83
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == 13:
                self.state = 79
                self.match(ExprParser.COMMA)
                self.state = 80
                self.parameter()
                self.state = 85
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ParameterContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def type_(self):
            return self.getTypedRuleContext(ExprParser.TypeContext, 0)

        def ID(self):
            return self.getToken(ExprParser.ID, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_parameter

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterParameter"):
                listener.enterParameter(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitParameter"):
                listener.exitParameter(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitParameter"):
                return visitor.visitParameter(self)
            else:
                return visitor.visitChildren(self)

    def parameter(self):

        localctx = ExprParser.ParameterContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_parameter)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 86
            self.type_()
            self.state = 87
            self.match(ExprParser.ID)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class StatContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def variableDef(self):
            return self.getTypedRuleContext(ExprParser.VariableDefContext, 0)

        def assignment(self):
            return self.getTypedRuleContext(ExprParser.AssignmentContext, 0)

        def ifStat(self):
            return self.getTypedRuleContext(ExprParser.IfStatContext, 0)

        def forStat(self):
            return self.getTypedRuleContext(ExprParser.ForStatContext, 0)

        def returnStat(self):
            return self.getTypedRuleContext(ExprParser.ReturnStatContext, 0)

        def expr(self):
            return self.getTypedRuleContext(ExprParser.ExprContext, 0)

        def SEMI(self):
            return self.getToken(ExprParser.SEMI, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_stat

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterStat"):
                listener.enterStat(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitStat"):
                listener.exitStat(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitStat"):
                return visitor.visitStat(self)
            else:
                return visitor.visitChildren(self)

    def stat(self):

        localctx = ExprParser.StatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_stat)
        self._la = 0  # Token type
        try:
            self.state = 98
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 6, self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 89
                self.variableDef()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 90
                self.assignment()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 91
                self.ifStat()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 92
                self.forStat()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 93
                self.returnStat()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 94
                self.expr()
                self.state = 96
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la == 15:
                    self.state = 95
                    self.match(ExprParser.SEMI)

                pass

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class VariableDefContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def type_(self):
            return self.getTypedRuleContext(ExprParser.TypeContext, 0)

        def ID(self):
            return self.getToken(ExprParser.ID, 0)

        def ASSIGN(self):
            return self.getToken(ExprParser.ASSIGN, 0)

        def expr(self):
            return self.getTypedRuleContext(ExprParser.ExprContext, 0)

        def SEMI(self):
            return self.getToken(ExprParser.SEMI, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_variableDef

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterVariableDef"):
                listener.enterVariableDef(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitVariableDef"):
                listener.exitVariableDef(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitVariableDef"):
                return visitor.visitVariableDef(self)
            else:
                return visitor.visitChildren(self)

    def variableDef(self):

        localctx = ExprParser.VariableDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_variableDef)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 100
            self.type_()
            self.state = 101
            self.match(ExprParser.ID)
            self.state = 104
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == 21:
                self.state = 102
                self.match(ExprParser.ASSIGN)
                self.state = 103
                self.expr()

            self.state = 107
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == 15:
                self.state = 106
                self.match(ExprParser.SEMI)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AssignmentContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(ExprParser.ID, 0)

        def ASSIGN(self):
            return self.getToken(ExprParser.ASSIGN, 0)

        def expr(self):
            return self.getTypedRuleContext(ExprParser.ExprContext, 0)

        def SEMI(self):
            return self.getToken(ExprParser.SEMI, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_assignment

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterAssignment"):
                listener.enterAssignment(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitAssignment"):
                listener.exitAssignment(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitAssignment"):
                return visitor.visitAssignment(self)
            else:
                return visitor.visitChildren(self)

    def assignment(self):

        localctx = ExprParser.AssignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_assignment)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 109
            self.match(ExprParser.ID)
            self.state = 110
            self.match(ExprParser.ASSIGN)
            self.state = 111
            self.expr()
            self.state = 113
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == 15:
                self.state = 112
                self.match(ExprParser.SEMI)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class IfStatContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IF(self):
            return self.getToken(ExprParser.IF, 0)

        def expr(self):
            return self.getTypedRuleContext(ExprParser.ExprContext, 0)

        def block(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(ExprParser.BlockContext)
            else:
                return self.getTypedRuleContext(ExprParser.BlockContext, i)

        def THEN(self):
            return self.getToken(ExprParser.THEN, 0)

        def ELSE(self):
            return self.getToken(ExprParser.ELSE, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_ifStat

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterIfStat"):
                listener.enterIfStat(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitIfStat"):
                listener.exitIfStat(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitIfStat"):
                return visitor.visitIfStat(self)
            else:
                return visitor.visitChildren(self)

    def ifStat(self):

        localctx = ExprParser.IfStatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_ifStat)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 115
            self.match(ExprParser.IF)
            self.state = 116
            self.expr()
            self.state = 118
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == 4:
                self.state = 117
                self.match(ExprParser.THEN)

            self.state = 120
            self.block()
            self.state = 123
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == 5:
                self.state = 121
                self.match(ExprParser.ELSE)
                self.state = 122
                self.block()

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ForStatContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def FOR(self):
            return self.getToken(ExprParser.FOR, 0)

        def type_(self):
            return self.getTypedRuleContext(ExprParser.TypeContext, 0)

        def ID(self):
            return self.getToken(ExprParser.ID, 0)

        def IN(self):
            return self.getToken(ExprParser.IN, 0)

        def expr(self):
            return self.getTypedRuleContext(ExprParser.ExprContext, 0)

        def block(self):
            return self.getTypedRuleContext(ExprParser.BlockContext, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_forStat

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterForStat"):
                listener.enterForStat(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitForStat"):
                listener.exitForStat(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitForStat"):
                return visitor.visitForStat(self)
            else:
                return visitor.visitChildren(self)

    def forStat(self):

        localctx = ExprParser.ForStatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_forStat)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 125
            self.match(ExprParser.FOR)
            self.state = 126
            self.type_()
            self.state = 127
            self.match(ExprParser.ID)
            self.state = 128
            self.match(ExprParser.IN)
            self.state = 129
            self.expr()
            self.state = 130
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ReturnStatContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def RETURN(self):
            return self.getToken(ExprParser.RETURN, 0)

        def expr(self):
            return self.getTypedRuleContext(ExprParser.ExprContext, 0)

        def SEMI(self):
            return self.getToken(ExprParser.SEMI, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_returnStat

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterReturnStat"):
                listener.enterReturnStat(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitReturnStat"):
                listener.exitReturnStat(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitReturnStat"):
                return visitor.visitReturnStat(self)
            else:
                return visitor.visitChildren(self)

    def returnStat(self):

        localctx = ExprParser.ReturnStatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_returnStat)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 132
            self.match(ExprParser.RETURN)
            self.state = 134
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input, 12, self._ctx)
            if la_ == 1:
                self.state = 133
                self.expr()

            self.state = 137
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == 15:
                self.state = 136
                self.match(ExprParser.SEMI)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ExprContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assignmentExpr(self):
            return self.getTypedRuleContext(ExprParser.AssignmentExprContext, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_expr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterExpr"):
                listener.enterExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitExpr"):
                listener.exitExpr(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitExpr"):
                return visitor.visitExpr(self)
            else:
                return visitor.visitChildren(self)

    def expr(self):

        localctx = ExprParser.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_expr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 139
            self.assignmentExpr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AssignmentExprContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def relationalExpr(self):
            return self.getTypedRuleContext(ExprParser.RelationalExprContext, 0)

        def ASSIGN(self):
            return self.getToken(ExprParser.ASSIGN, 0)

        def assignmentExpr(self):
            return self.getTypedRuleContext(ExprParser.AssignmentExprContext, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_assignmentExpr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterAssignmentExpr"):
                listener.enterAssignmentExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitAssignmentExpr"):
                listener.exitAssignmentExpr(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitAssignmentExpr"):
                return visitor.visitAssignmentExpr(self)
            else:
                return visitor.visitChildren(self)

    def assignmentExpr(self):

        localctx = ExprParser.AssignmentExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_assignmentExpr)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 141
            self.relationalExpr()
            self.state = 144
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == 21:
                self.state = 142
                self.match(ExprParser.ASSIGN)
                self.state = 143
                self.assignmentExpr()

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class RelationalExprContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def additiveExpr(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(ExprParser.AdditiveExprContext)
            else:
                return self.getTypedRuleContext(ExprParser.AdditiveExprContext, i)

        def EQ_EQ(self, i: int = None):
            if i is None:
                return self.getTokens(ExprParser.EQ_EQ)
            else:
                return self.getToken(ExprParser.EQ_EQ, i)

        def GT(self, i: int = None):
            if i is None:
                return self.getTokens(ExprParser.GT)
            else:
                return self.getToken(ExprParser.GT, i)

        def LT(self, i: int = None):
            if i is None:
                return self.getTokens(ExprParser.LT)
            else:
                return self.getToken(ExprParser.LT, i)

        def getRuleIndex(self):
            return ExprParser.RULE_relationalExpr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterRelationalExpr"):
                listener.enterRelationalExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitRelationalExpr"):
                listener.exitRelationalExpr(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitRelationalExpr"):
                return visitor.visitRelationalExpr(self)
            else:
                return visitor.visitChildren(self)

    def relationalExpr(self):

        localctx = ExprParser.RelationalExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_relationalExpr)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 146
            self.additiveExpr()
            self.state = 151
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while ((_la) & ~0x3F) == 0 and ((1 << _la) & 29360128) != 0:
                self.state = 147
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3F) == 0 and ((1 << _la) & 29360128) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 148
                self.additiveExpr()
                self.state = 153
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AdditiveExprContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def multiplicativeExpr(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(ExprParser.MultiplicativeExprContext)
            else:
                return self.getTypedRuleContext(ExprParser.MultiplicativeExprContext, i)

        def PLUS(self, i: int = None):
            if i is None:
                return self.getTokens(ExprParser.PLUS)
            else:
                return self.getToken(ExprParser.PLUS, i)

        def MINUS(self, i: int = None):
            if i is None:
                return self.getTokens(ExprParser.MINUS)
            else:
                return self.getToken(ExprParser.MINUS, i)

        def getRuleIndex(self):
            return ExprParser.RULE_additiveExpr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterAdditiveExpr"):
                listener.enterAdditiveExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitAdditiveExpr"):
                listener.exitAdditiveExpr(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitAdditiveExpr"):
                return visitor.visitAdditiveExpr(self)
            else:
                return visitor.visitChildren(self)

    def additiveExpr(self):

        localctx = ExprParser.AdditiveExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_additiveExpr)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 154
            self.multiplicativeExpr()
            self.state = 159
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == 25 or _la == 26:
                self.state = 155
                _la = self._input.LA(1)
                if not (_la == 25 or _la == 26):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 156
                self.multiplicativeExpr()
                self.state = 161
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class MultiplicativeExprContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def castExpr(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(ExprParser.CastExprContext)
            else:
                return self.getTypedRuleContext(ExprParser.CastExprContext, i)

        def DIV(self, i: int = None):
            if i is None:
                return self.getTokens(ExprParser.DIV)
            else:
                return self.getToken(ExprParser.DIV, i)

        def MULT(self, i: int = None):
            if i is None:
                return self.getTokens(ExprParser.MULT)
            else:
                return self.getToken(ExprParser.MULT, i)

        def getRuleIndex(self):
            return ExprParser.RULE_multiplicativeExpr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterMultiplicativeExpr"):
                listener.enterMultiplicativeExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitMultiplicativeExpr"):
                listener.exitMultiplicativeExpr(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitMultiplicativeExpr"):
                return visitor.visitMultiplicativeExpr(self)
            else:
                return visitor.visitChildren(self)

    def multiplicativeExpr(self):

        localctx = ExprParser.MultiplicativeExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_multiplicativeExpr)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 162
            self.castExpr()
            self.state = 167
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == 27 or _la == 28:
                self.state = 163
                _la = self._input.LA(1)
                if not (_la == 27 or _la == 28):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 164
                self.castExpr()
                self.state = 169
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class CastExprContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atom(self):
            return self.getTypedRuleContext(ExprParser.AtomContext, 0)

        def AS(self):
            return self.getToken(ExprParser.AS, 0)

        def type_(self):
            return self.getTypedRuleContext(ExprParser.TypeContext, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_castExpr

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterCastExpr"):
                listener.enterCastExpr(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitCastExpr"):
                listener.exitCastExpr(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitCastExpr"):
                return visitor.visitCastExpr(self)
            else:
                return visitor.visitChildren(self)

    def castExpr(self):

        localctx = ExprParser.CastExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_castExpr)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 170
            self.atom(0)
            self.state = 173
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la == 8:
                self.state = 171
                self.match(ExprParser.AS)
                self.state = 172
                self.type_()

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AtomContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(ExprParser.LPAREN, 0)

        def expr(self):
            return self.getTypedRuleContext(ExprParser.ExprContext, 0)

        def RPAREN(self):
            return self.getToken(ExprParser.RPAREN, 0)

        def literal(self):
            return self.getTypedRuleContext(ExprParser.LiteralContext, 0)

        def ID(self):
            return self.getToken(ExprParser.ID, 0)

        def constructibleType(self):
            return self.getTypedRuleContext(ExprParser.ConstructibleTypeContext, 0)

        def argumentList(self):
            return self.getTypedRuleContext(ExprParser.ArgumentListContext, 0)

        def atom(self):
            return self.getTypedRuleContext(ExprParser.AtomContext, 0)

        def DOT(self):
            return self.getToken(ExprParser.DOT, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_atom

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterAtom"):
                listener.enterAtom(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitAtom"):
                listener.exitAtom(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitAtom"):
                return visitor.visitAtom(self)
            else:
                return visitor.visitChildren(self)

    def atom(self, _p: int = 0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = ExprParser.AtomContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 38
        self.enterRecursionRule(localctx, 38, self.RULE_atom, _p)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 189
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [9]:
                self.state = 176
                self.match(ExprParser.LPAREN)
                self.state = 177
                self.expr()
                self.state = 178
                self.match(ExprParser.RPAREN)
                pass
            elif token in [30, 31, 32]:
                self.state = 180
                self.literal()
                pass
            elif token in [33]:
                self.state = 181
                self.match(ExprParser.ID)
                pass
            elif token in [17]:
                self.state = 182
                self.constructibleType()
                self.state = 183
                self.match(ExprParser.LPAREN)
                self.state = 185
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if ((_la) & ~0x3F) == 0 and ((1 << _la) & 16106258944) != 0:
                    self.state = 184
                    self.argumentList()

                self.state = 187
                self.match(ExprParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 202
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input, 23, self._ctx)
            while _alt != 2 and _alt != ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 200
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input, 22, self._ctx)
                    if la_ == 1:
                        localctx = ExprParser.AtomContext(
                            self, _parentctx, _parentState
                        )
                        self.pushNewRecursionContext(
                            localctx, _startState, self.RULE_atom
                        )
                        self.state = 191
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException

                            raise FailedPredicateException(
                                self, "self.precpred(self._ctx, 2)"
                            )
                        self.state = 192
                        self.match(ExprParser.DOT)
                        self.state = 193
                        self.match(ExprParser.ID)
                        pass

                    elif la_ == 2:
                        localctx = ExprParser.AtomContext(
                            self, _parentctx, _parentState
                        )
                        self.pushNewRecursionContext(
                            localctx, _startState, self.RULE_atom
                        )
                        self.state = 194
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException

                            raise FailedPredicateException(
                                self, "self.precpred(self._ctx, 1)"
                            )
                        self.state = 195
                        self.match(ExprParser.LPAREN)
                        self.state = 197
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if ((_la) & ~0x3F) == 0 and ((1 << _la) & 16106258944) != 0:
                            self.state = 196
                            self.argumentList()

                        self.state = 199
                        self.match(ExprParser.RPAREN)
                        pass

                self.state = 204
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input, 23, self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx

    class ArgumentListContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expr(self, i: int = None):
            if i is None:
                return self.getTypedRuleContexts(ExprParser.ExprContext)
            else:
                return self.getTypedRuleContext(ExprParser.ExprContext, i)

        def COMMA(self, i: int = None):
            if i is None:
                return self.getTokens(ExprParser.COMMA)
            else:
                return self.getToken(ExprParser.COMMA, i)

        def getRuleIndex(self):
            return ExprParser.RULE_argumentList

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterArgumentList"):
                listener.enterArgumentList(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitArgumentList"):
                listener.exitArgumentList(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitArgumentList"):
                return visitor.visitArgumentList(self)
            else:
                return visitor.visitChildren(self)

    def argumentList(self):

        localctx = ExprParser.ArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_argumentList)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 205
            self.expr()
            self.state = 210
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la == 13:
                self.state = 206
                self.match(ExprParser.COMMA)
                self.state = 207
                self.expr()
                self.state = 212
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class LiteralContext(ParserRuleContext):
        __slots__ = "parser"

        def __init__(
            self, parser, parent: ParserRuleContext = None, invokingState: int = -1
        ):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(ExprParser.INT, 0)

        def STRING(self):
            return self.getToken(ExprParser.STRING, 0)

        def FLOAT(self):
            return self.getToken(ExprParser.FLOAT, 0)

        def getRuleIndex(self):
            return ExprParser.RULE_literal

        def enterRule(self, listener: ParseTreeListener):
            if hasattr(listener, "enterLiteral"):
                listener.enterLiteral(self)

        def exitRule(self, listener: ParseTreeListener):
            if hasattr(listener, "exitLiteral"):
                listener.exitLiteral(self)

        def accept(self, visitor: ParseTreeVisitor):
            if hasattr(visitor, "visitLiteral"):
                return visitor.visitLiteral(self)
            else:
                return visitor.visitChildren(self)

    def literal(self):

        localctx = ExprParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_literal)
        self._la = 0  # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 213
            _la = self._input.LA(1)
            if not ((((_la) & ~0x3F) == 0 and ((1 << _la) & 7516192768) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    def sempred(self, localctx: RuleContext, ruleIndex: int, predIndex: int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[19] = self.atom_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def atom_sempred(self, localctx: AtomContext, predIndex: int):
        if predIndex == 0:
            return self.precpred(self._ctx, 2)

        if predIndex == 1:
            return self.precpred(self._ctx, 1)

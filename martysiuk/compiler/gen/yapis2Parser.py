# Generated from grammar/yapis2.g4 by ANTLR 4.13.2
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
        4,1,52,203,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,1,0,5,0,40,8,0,
        10,0,12,0,43,9,0,1,0,5,0,46,8,0,10,0,12,0,49,9,0,1,0,1,0,1,1,1,1,
        1,1,1,1,3,1,57,8,1,1,1,1,1,1,1,3,1,62,8,1,1,1,1,1,1,1,1,2,1,2,1,
        2,5,2,70,8,2,10,2,12,2,73,9,2,1,3,1,3,1,3,1,4,1,4,1,5,1,5,4,5,82,
        8,5,11,5,12,5,83,1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,1,6,1,6,3,6,96,
        8,6,1,7,1,7,1,7,1,7,1,8,1,8,1,8,1,8,1,9,1,9,1,9,1,9,1,9,1,9,3,9,
        112,8,9,1,10,1,10,1,10,1,10,1,10,1,11,1,11,1,11,1,11,1,11,1,11,1,
        11,1,11,1,11,3,11,128,8,11,1,11,1,11,1,11,1,12,1,12,1,13,1,13,3,
        13,137,8,13,1,14,1,14,1,14,3,14,142,8,14,1,14,1,14,1,14,1,14,3,14,
        148,8,14,1,14,1,14,3,14,152,8,14,1,15,1,15,1,15,5,15,157,8,15,10,
        15,12,15,160,9,15,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,
        16,1,16,1,16,1,16,1,16,1,16,3,16,177,8,16,1,16,1,16,1,16,1,16,1,
        16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,1,16,5,16,194,8,
        16,10,16,12,16,197,9,16,1,17,1,17,1,18,1,18,1,18,0,1,32,19,0,2,4,
        6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,0,7,1,0,6,12,1,0,26,
        28,1,0,29,30,1,0,31,36,1,0,37,38,2,0,7,10,39,43,1,0,45,47,213,0,
        41,1,0,0,0,2,52,1,0,0,0,4,66,1,0,0,0,6,74,1,0,0,0,8,77,1,0,0,0,10,
        79,1,0,0,0,12,95,1,0,0,0,14,97,1,0,0,0,16,101,1,0,0,0,18,105,1,0,
        0,0,20,113,1,0,0,0,22,118,1,0,0,0,24,132,1,0,0,0,26,134,1,0,0,0,
        28,151,1,0,0,0,30,153,1,0,0,0,32,176,1,0,0,0,34,198,1,0,0,0,36,200,
        1,0,0,0,38,40,3,2,1,0,39,38,1,0,0,0,40,43,1,0,0,0,41,39,1,0,0,0,
        41,42,1,0,0,0,42,47,1,0,0,0,43,41,1,0,0,0,44,46,3,12,6,0,45,44,1,
        0,0,0,46,49,1,0,0,0,47,45,1,0,0,0,47,48,1,0,0,0,48,50,1,0,0,0,49,
        47,1,0,0,0,50,51,5,0,0,1,51,1,1,0,0,0,52,53,5,1,0,0,53,54,5,44,0,
        0,54,56,5,2,0,0,55,57,3,4,2,0,56,55,1,0,0,0,56,57,1,0,0,0,57,58,
        1,0,0,0,58,61,5,3,0,0,59,60,5,44,0,0,60,62,3,8,4,0,61,59,1,0,0,0,
        61,62,1,0,0,0,62,63,1,0,0,0,63,64,5,4,0,0,64,65,3,10,5,0,65,3,1,
        0,0,0,66,71,3,6,3,0,67,68,5,5,0,0,68,70,3,6,3,0,69,67,1,0,0,0,70,
        73,1,0,0,0,71,69,1,0,0,0,71,72,1,0,0,0,72,5,1,0,0,0,73,71,1,0,0,
        0,74,75,5,44,0,0,75,76,3,8,4,0,76,7,1,0,0,0,77,78,7,0,0,0,78,9,1,
        0,0,0,79,81,5,51,0,0,80,82,3,12,6,0,81,80,1,0,0,0,82,83,1,0,0,0,
        83,81,1,0,0,0,83,84,1,0,0,0,84,85,1,0,0,0,85,86,5,52,0,0,86,11,1,
        0,0,0,87,96,3,14,7,0,88,96,3,16,8,0,89,96,3,18,9,0,90,96,3,20,10,
        0,91,96,3,22,11,0,92,96,3,24,12,0,93,96,3,26,13,0,94,96,3,28,14,
        0,95,87,1,0,0,0,95,88,1,0,0,0,95,89,1,0,0,0,95,90,1,0,0,0,95,91,
        1,0,0,0,95,92,1,0,0,0,95,93,1,0,0,0,95,94,1,0,0,0,96,13,1,0,0,0,
        97,98,5,44,0,0,98,99,5,13,0,0,99,100,3,32,16,0,100,15,1,0,0,0,101,
        102,5,44,0,0,102,103,5,13,0,0,103,104,3,32,16,0,104,17,1,0,0,0,105,
        106,5,14,0,0,106,107,3,32,16,0,107,108,5,15,0,0,108,111,3,10,5,0,
        109,110,5,16,0,0,110,112,3,10,5,0,111,109,1,0,0,0,111,112,1,0,0,
        0,112,19,1,0,0,0,113,114,5,17,0,0,114,115,3,32,16,0,115,116,5,18,
        0,0,116,117,3,10,5,0,117,21,1,0,0,0,118,119,5,19,0,0,119,120,5,44,
        0,0,120,121,5,13,0,0,121,122,3,32,16,0,122,123,5,20,0,0,123,127,
        3,32,16,0,124,125,5,21,0,0,125,126,5,13,0,0,126,128,3,32,16,0,127,
        124,1,0,0,0,127,128,1,0,0,0,128,129,1,0,0,0,129,130,5,4,0,0,130,
        131,3,10,5,0,131,23,1,0,0,0,132,133,5,22,0,0,133,25,1,0,0,0,134,
        136,5,23,0,0,135,137,3,32,16,0,136,135,1,0,0,0,136,137,1,0,0,0,137,
        27,1,0,0,0,138,139,5,44,0,0,139,141,5,2,0,0,140,142,3,30,15,0,141,
        140,1,0,0,0,141,142,1,0,0,0,142,143,1,0,0,0,143,152,5,3,0,0,144,
        145,3,34,17,0,145,147,5,2,0,0,146,148,3,30,15,0,147,146,1,0,0,0,
        147,148,1,0,0,0,148,149,1,0,0,0,149,150,5,3,0,0,150,152,1,0,0,0,
        151,138,1,0,0,0,151,144,1,0,0,0,152,29,1,0,0,0,153,158,3,32,16,0,
        154,155,5,5,0,0,155,157,3,32,16,0,156,154,1,0,0,0,157,160,1,0,0,
        0,158,156,1,0,0,0,158,159,1,0,0,0,159,31,1,0,0,0,160,158,1,0,0,0,
        161,162,6,16,-1,0,162,177,3,36,18,0,163,177,5,44,0,0,164,177,3,28,
        14,0,165,166,5,2,0,0,166,167,3,32,16,0,167,168,5,3,0,0,168,177,1,
        0,0,0,169,170,5,2,0,0,170,171,3,8,4,0,171,172,5,3,0,0,172,173,3,
        32,16,7,173,177,1,0,0,0,174,175,5,24,0,0,175,177,3,32,16,6,176,161,
        1,0,0,0,176,163,1,0,0,0,176,164,1,0,0,0,176,165,1,0,0,0,176,169,
        1,0,0,0,176,174,1,0,0,0,177,195,1,0,0,0,178,179,10,4,0,0,179,180,
        7,1,0,0,180,194,3,32,16,5,181,182,10,3,0,0,182,183,7,2,0,0,183,194,
        3,32,16,4,184,185,10,2,0,0,185,186,7,3,0,0,186,194,3,32,16,3,187,
        188,10,1,0,0,188,189,7,4,0,0,189,194,3,32,16,2,190,191,10,5,0,0,
        191,192,5,25,0,0,192,194,5,44,0,0,193,178,1,0,0,0,193,181,1,0,0,
        0,193,184,1,0,0,0,193,187,1,0,0,0,193,190,1,0,0,0,194,197,1,0,0,
        0,195,193,1,0,0,0,195,196,1,0,0,0,196,33,1,0,0,0,197,195,1,0,0,0,
        198,199,7,5,0,0,199,35,1,0,0,0,200,201,7,6,0,0,201,37,1,0,0,0,17,
        41,47,56,61,71,83,95,111,127,136,141,147,151,158,176,193,195
    ]

class yapis2Parser ( Parser ):

    grammarFileName = "yapis2.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'func'", "'('", "')'", "':'", "','", 
                     "'int'", "'point'", "'line'", "'circle'", "'polygon'", 
                     "'bool'", "'string'", "'='", "'if'", "'then'", "'else'", 
                     "'while'", "'do:'", "'for'", "'to'", "'step'", "'break'", 
                     "'return'", "'!'", "'.'", "'*'", "'/'", "'%'", "'+'", 
                     "'-'", "'<'", "'>'", "'<='", "'>='", "'=='", "'!='", 
                     "'&&'", "'||'", "'read'", "'write'", "'distance'", 
                     "'intersection'", "'inside'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "IDENTIFIER", "INT", "BOOL", "STRING", "NEWLINE", 
                      "WS", "COMMENT", "INDENT", "DEDENT" ]

    RULE_program = 0
    RULE_functionDecl = 1
    RULE_parameterList = 2
    RULE_parameter = 3
    RULE_type = 4
    RULE_block = 5
    RULE_statement = 6
    RULE_assignment = 7
    RULE_variableDecl = 8
    RULE_ifStatement = 9
    RULE_whileStatement = 10
    RULE_forStatement = 11
    RULE_breakStatement = 12
    RULE_returnStatement = 13
    RULE_functionCall = 14
    RULE_argumentList = 15
    RULE_expression = 16
    RULE_builtInFunction = 17
    RULE_literal = 18

    ruleNames =  [ "program", "functionDecl", "parameterList", "parameter", 
                   "type", "block", "statement", "assignment", "variableDecl", 
                   "ifStatement", "whileStatement", "forStatement", "breakStatement", 
                   "returnStatement", "functionCall", "argumentList", "expression", 
                   "builtInFunction", "literal" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    T__33=34
    T__34=35
    T__35=36
    T__36=37
    T__37=38
    T__38=39
    T__39=40
    T__40=41
    T__41=42
    T__42=43
    IDENTIFIER=44
    INT=45
    BOOL=46
    STRING=47
    NEWLINE=48
    WS=49
    COMMENT=50
    INDENT=51
    DEDENT=52

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(yapis2Parser.EOF, 0)

        def functionDecl(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.FunctionDeclContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.FunctionDeclContext,i)


        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.StatementContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.StatementContext,i)


        def getRuleIndex(self):
            return yapis2Parser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProgram" ):
                return visitor.visitProgram(self)
            else:
                return visitor.visitChildren(self)




    def program(self):

        localctx = yapis2Parser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 41
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==1:
                self.state = 38
                self.functionDecl()
                self.state = 43
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 47
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 34634629531520) != 0):
                self.state = 44
                self.statement()
                self.state = 49
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 50
            self.match(yapis2Parser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FunctionDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self, i:int=None):
            if i is None:
                return self.getTokens(yapis2Parser.IDENTIFIER)
            else:
                return self.getToken(yapis2Parser.IDENTIFIER, i)

        def block(self):
            return self.getTypedRuleContext(yapis2Parser.BlockContext,0)


        def parameterList(self):
            return self.getTypedRuleContext(yapis2Parser.ParameterListContext,0)


        def type_(self):
            return self.getTypedRuleContext(yapis2Parser.TypeContext,0)


        def getRuleIndex(self):
            return yapis2Parser.RULE_functionDecl

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunctionDecl" ):
                listener.enterFunctionDecl(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunctionDecl" ):
                listener.exitFunctionDecl(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunctionDecl" ):
                return visitor.visitFunctionDecl(self)
            else:
                return visitor.visitChildren(self)




    def functionDecl(self):

        localctx = yapis2Parser.FunctionDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_functionDecl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 52
            self.match(yapis2Parser.T__0)
            self.state = 53
            self.match(yapis2Parser.IDENTIFIER)
            self.state = 54
            self.match(yapis2Parser.T__1)
            self.state = 56
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==44:
                self.state = 55
                self.parameterList()


            self.state = 58
            self.match(yapis2Parser.T__2)
            self.state = 61
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==44:
                self.state = 59
                self.match(yapis2Parser.IDENTIFIER)
                self.state = 60
                self.type_()


            self.state = 63
            self.match(yapis2Parser.T__3)
            self.state = 64
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ParameterListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def parameter(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.ParameterContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.ParameterContext,i)


        def getRuleIndex(self):
            return yapis2Parser.RULE_parameterList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParameterList" ):
                listener.enterParameterList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParameterList" ):
                listener.exitParameterList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParameterList" ):
                return visitor.visitParameterList(self)
            else:
                return visitor.visitChildren(self)




    def parameterList(self):

        localctx = yapis2Parser.ParameterListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_parameterList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.parameter()
            self.state = 71
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==5:
                self.state = 67
                self.match(yapis2Parser.T__4)
                self.state = 68
                self.parameter()
                self.state = 73
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
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(yapis2Parser.IDENTIFIER, 0)

        def type_(self):
            return self.getTypedRuleContext(yapis2Parser.TypeContext,0)


        def getRuleIndex(self):
            return yapis2Parser.RULE_parameter

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParameter" ):
                listener.enterParameter(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParameter" ):
                listener.exitParameter(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParameter" ):
                return visitor.visitParameter(self)
            else:
                return visitor.visitChildren(self)




    def parameter(self):

        localctx = yapis2Parser.ParameterContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_parameter)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74
            self.match(yapis2Parser.IDENTIFIER)
            self.state = 75
            self.type_()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TypeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return yapis2Parser.RULE_type

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterType" ):
                listener.enterType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitType" ):
                listener.exitType(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitType" ):
                return visitor.visitType(self)
            else:
                return visitor.visitChildren(self)




    def type_(self):

        localctx = yapis2Parser.TypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_type)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 77
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 8128) != 0)):
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


    class BlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INDENT(self):
            return self.getToken(yapis2Parser.INDENT, 0)

        def DEDENT(self):
            return self.getToken(yapis2Parser.DEDENT, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.StatementContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.StatementContext,i)


        def getRuleIndex(self):
            return yapis2Parser.RULE_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBlock" ):
                listener.enterBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBlock" ):
                listener.exitBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBlock" ):
                return visitor.visitBlock(self)
            else:
                return visitor.visitChildren(self)




    def block(self):

        localctx = yapis2Parser.BlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 79
            self.match(yapis2Parser.INDENT)
            self.state = 81 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 80
                self.statement()
                self.state = 83 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not ((((_la) & ~0x3f) == 0 and ((1 << _la) & 34634629531520) != 0)):
                    break

            self.state = 85
            self.match(yapis2Parser.DEDENT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assignment(self):
            return self.getTypedRuleContext(yapis2Parser.AssignmentContext,0)


        def variableDecl(self):
            return self.getTypedRuleContext(yapis2Parser.VariableDeclContext,0)


        def ifStatement(self):
            return self.getTypedRuleContext(yapis2Parser.IfStatementContext,0)


        def whileStatement(self):
            return self.getTypedRuleContext(yapis2Parser.WhileStatementContext,0)


        def forStatement(self):
            return self.getTypedRuleContext(yapis2Parser.ForStatementContext,0)


        def breakStatement(self):
            return self.getTypedRuleContext(yapis2Parser.BreakStatementContext,0)


        def returnStatement(self):
            return self.getTypedRuleContext(yapis2Parser.ReturnStatementContext,0)


        def functionCall(self):
            return self.getTypedRuleContext(yapis2Parser.FunctionCallContext,0)


        def getRuleIndex(self):
            return yapis2Parser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = yapis2Parser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_statement)
        try:
            self.state = 95
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 87
                self.assignment()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 88
                self.variableDecl()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 89
                self.ifStatement()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 90
                self.whileStatement()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 91
                self.forStatement()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 92
                self.breakStatement()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 93
                self.returnStatement()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 94
                self.functionCall()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignmentContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(yapis2Parser.IDENTIFIER, 0)

        def expression(self):
            return self.getTypedRuleContext(yapis2Parser.ExpressionContext,0)


        def getRuleIndex(self):
            return yapis2Parser.RULE_assignment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssignment" ):
                listener.enterAssignment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssignment" ):
                listener.exitAssignment(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssignment" ):
                return visitor.visitAssignment(self)
            else:
                return visitor.visitChildren(self)




    def assignment(self):

        localctx = yapis2Parser.AssignmentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_assignment)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 97
            self.match(yapis2Parser.IDENTIFIER)
            self.state = 98
            self.match(yapis2Parser.T__12)
            self.state = 99
            self.expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VariableDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(yapis2Parser.IDENTIFIER, 0)

        def expression(self):
            return self.getTypedRuleContext(yapis2Parser.ExpressionContext,0)


        def getRuleIndex(self):
            return yapis2Parser.RULE_variableDecl

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVariableDecl" ):
                listener.enterVariableDecl(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVariableDecl" ):
                listener.exitVariableDecl(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariableDecl" ):
                return visitor.visitVariableDecl(self)
            else:
                return visitor.visitChildren(self)




    def variableDecl(self):

        localctx = yapis2Parser.VariableDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_variableDecl)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 101
            self.match(yapis2Parser.IDENTIFIER)
            self.state = 102
            self.match(yapis2Parser.T__12)
            self.state = 103
            self.expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IfStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(yapis2Parser.ExpressionContext,0)


        def block(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.BlockContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.BlockContext,i)


        def getRuleIndex(self):
            return yapis2Parser.RULE_ifStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIfStatement" ):
                listener.enterIfStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIfStatement" ):
                listener.exitIfStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIfStatement" ):
                return visitor.visitIfStatement(self)
            else:
                return visitor.visitChildren(self)




    def ifStatement(self):

        localctx = yapis2Parser.IfStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_ifStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 105
            self.match(yapis2Parser.T__13)
            self.state = 106
            self.expression(0)
            self.state = 107
            self.match(yapis2Parser.T__14)
            self.state = 108
            self.block()
            self.state = 111
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==16:
                self.state = 109
                self.match(yapis2Parser.T__15)
                self.state = 110
                self.block()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WhileStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(yapis2Parser.ExpressionContext,0)


        def block(self):
            return self.getTypedRuleContext(yapis2Parser.BlockContext,0)


        def getRuleIndex(self):
            return yapis2Parser.RULE_whileStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWhileStatement" ):
                listener.enterWhileStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWhileStatement" ):
                listener.exitWhileStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWhileStatement" ):
                return visitor.visitWhileStatement(self)
            else:
                return visitor.visitChildren(self)




    def whileStatement(self):

        localctx = yapis2Parser.WhileStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_whileStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 113
            self.match(yapis2Parser.T__16)
            self.state = 114
            self.expression(0)
            self.state = 115
            self.match(yapis2Parser.T__17)
            self.state = 116
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ForStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(yapis2Parser.IDENTIFIER, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.ExpressionContext,i)


        def block(self):
            return self.getTypedRuleContext(yapis2Parser.BlockContext,0)


        def getRuleIndex(self):
            return yapis2Parser.RULE_forStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterForStatement" ):
                listener.enterForStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitForStatement" ):
                listener.exitForStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitForStatement" ):
                return visitor.visitForStatement(self)
            else:
                return visitor.visitChildren(self)




    def forStatement(self):

        localctx = yapis2Parser.ForStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_forStatement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 118
            self.match(yapis2Parser.T__18)
            self.state = 119
            self.match(yapis2Parser.IDENTIFIER)
            self.state = 120
            self.match(yapis2Parser.T__12)
            self.state = 121
            self.expression(0)
            self.state = 122
            self.match(yapis2Parser.T__19)
            self.state = 123
            self.expression(0)
            self.state = 127
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==21:
                self.state = 124
                self.match(yapis2Parser.T__20)
                self.state = 125
                self.match(yapis2Parser.T__12)
                self.state = 126
                self.expression(0)


            self.state = 129
            self.match(yapis2Parser.T__3)
            self.state = 130
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BreakStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return yapis2Parser.RULE_breakStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBreakStatement" ):
                listener.enterBreakStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBreakStatement" ):
                listener.exitBreakStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBreakStatement" ):
                return visitor.visitBreakStatement(self)
            else:
                return visitor.visitChildren(self)




    def breakStatement(self):

        localctx = yapis2Parser.BreakStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_breakStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 132
            self.match(yapis2Parser.T__21)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReturnStatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(yapis2Parser.ExpressionContext,0)


        def getRuleIndex(self):
            return yapis2Parser.RULE_returnStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReturnStatement" ):
                listener.enterReturnStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReturnStatement" ):
                listener.exitReturnStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitReturnStatement" ):
                return visitor.visitReturnStatement(self)
            else:
                return visitor.visitChildren(self)




    def returnStatement(self):

        localctx = yapis2Parser.ReturnStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_returnStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 134
            self.match(yapis2Parser.T__22)
            self.state = 136
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.state = 135
                self.expression(0)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class FunctionCallContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(yapis2Parser.IDENTIFIER, 0)

        def argumentList(self):
            return self.getTypedRuleContext(yapis2Parser.ArgumentListContext,0)


        def builtInFunction(self):
            return self.getTypedRuleContext(yapis2Parser.BuiltInFunctionContext,0)


        def getRuleIndex(self):
            return yapis2Parser.RULE_functionCall

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunctionCall" ):
                listener.enterFunctionCall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunctionCall" ):
                listener.exitFunctionCall(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunctionCall" ):
                return visitor.visitFunctionCall(self)
            else:
                return visitor.visitChildren(self)




    def functionCall(self):

        localctx = yapis2Parser.FunctionCallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_functionCall)
        self._la = 0 # Token type
        try:
            self.state = 151
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [44]:
                self.enterOuterAlt(localctx, 1)
                self.state = 138
                self.match(yapis2Parser.IDENTIFIER)
                self.state = 139
                self.match(yapis2Parser.T__1)
                self.state = 141
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 280925237675908) != 0):
                    self.state = 140
                    self.argumentList()


                self.state = 143
                self.match(yapis2Parser.T__2)
                pass
            elif token in [7, 8, 9, 10, 39, 40, 41, 42, 43]:
                self.enterOuterAlt(localctx, 2)
                self.state = 144
                self.builtInFunction()
                self.state = 145
                self.match(yapis2Parser.T__1)
                self.state = 147
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & 280925237675908) != 0):
                    self.state = 146
                    self.argumentList()


                self.state = 149
                self.match(yapis2Parser.T__2)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArgumentListContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.ExpressionContext,i)


        def getRuleIndex(self):
            return yapis2Parser.RULE_argumentList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArgumentList" ):
                listener.enterArgumentList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArgumentList" ):
                listener.exitArgumentList(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArgumentList" ):
                return visitor.visitArgumentList(self)
            else:
                return visitor.visitChildren(self)




    def argumentList(self):

        localctx = yapis2Parser.ArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_argumentList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 153
            self.expression(0)
            self.state = 158
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==5:
                self.state = 154
                self.match(yapis2Parser.T__4)
                self.state = 155
                self.expression(0)
                self.state = 160
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return yapis2Parser.RULE_expression

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class NotExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(yapis2Parser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNotExpr" ):
                listener.enterNotExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNotExpr" ):
                listener.exitNotExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNotExpr" ):
                return visitor.visitNotExpr(self)
            else:
                return visitor.visitChildren(self)


    class CastExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def type_(self):
            return self.getTypedRuleContext(yapis2Parser.TypeContext,0)

        def expression(self):
            return self.getTypedRuleContext(yapis2Parser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCastExpr" ):
                listener.enterCastExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCastExpr" ):
                listener.exitCastExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCastExpr" ):
                return visitor.visitCastExpr(self)
            else:
                return visitor.visitChildren(self)


    class ParenthesizedExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(yapis2Parser.ExpressionContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterParenthesizedExpr" ):
                listener.enterParenthesizedExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitParenthesizedExpr" ):
                listener.exitParenthesizedExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParenthesizedExpr" ):
                return visitor.visitParenthesizedExpr(self)
            else:
                return visitor.visitChildren(self)


    class LiteralExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def literal(self):
            return self.getTypedRuleContext(yapis2Parser.LiteralContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteralExpr" ):
                listener.enterLiteralExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteralExpr" ):
                listener.exitLiteralExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteralExpr" ):
                return visitor.visitLiteralExpr(self)
            else:
                return visitor.visitChildren(self)


    class LogicalExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLogicalExpr" ):
                listener.enterLogicalExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLogicalExpr" ):
                listener.exitLogicalExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLogicalExpr" ):
                return visitor.visitLogicalExpr(self)
            else:
                return visitor.visitChildren(self)


    class FunctionCallExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def functionCall(self):
            return self.getTypedRuleContext(yapis2Parser.FunctionCallContext,0)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterFunctionCallExpr" ):
                listener.enterFunctionCallExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitFunctionCallExpr" ):
                listener.exitFunctionCallExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFunctionCallExpr" ):
                return visitor.visitFunctionCallExpr(self)
            else:
                return visitor.visitChildren(self)


    class MemberAccessExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expression(self):
            return self.getTypedRuleContext(yapis2Parser.ExpressionContext,0)

        def IDENTIFIER(self):
            return self.getToken(yapis2Parser.IDENTIFIER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMemberAccessExpr" ):
                listener.enterMemberAccessExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMemberAccessExpr" ):
                listener.exitMemberAccessExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMemberAccessExpr" ):
                return visitor.visitMemberAccessExpr(self)
            else:
                return visitor.visitChildren(self)


    class ComparisonExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComparisonExpr" ):
                listener.enterComparisonExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComparisonExpr" ):
                listener.exitComparisonExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitComparisonExpr" ):
                return visitor.visitComparisonExpr(self)
            else:
                return visitor.visitChildren(self)


    class AdditiveExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAdditiveExpr" ):
                listener.enterAdditiveExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAdditiveExpr" ):
                listener.exitAdditiveExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAdditiveExpr" ):
                return visitor.visitAdditiveExpr(self)
            else:
                return visitor.visitChildren(self)


    class MultiplicativeExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(yapis2Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(yapis2Parser.ExpressionContext,i)


        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMultiplicativeExpr" ):
                listener.enterMultiplicativeExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMultiplicativeExpr" ):
                listener.exitMultiplicativeExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMultiplicativeExpr" ):
                return visitor.visitMultiplicativeExpr(self)
            else:
                return visitor.visitChildren(self)


    class IdentifierExprContext(ExpressionContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a yapis2Parser.ExpressionContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def IDENTIFIER(self):
            return self.getToken(yapis2Parser.IDENTIFIER, 0)

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifierExpr" ):
                listener.enterIdentifierExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifierExpr" ):
                listener.exitIdentifierExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIdentifierExpr" ):
                return visitor.visitIdentifierExpr(self)
            else:
                return visitor.visitChildren(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = yapis2Parser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 32
        self.enterRecursionRule(localctx, 32, self.RULE_expression, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 176
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
            if la_ == 1:
                localctx = yapis2Parser.LiteralExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 162
                self.literal()
                pass

            elif la_ == 2:
                localctx = yapis2Parser.IdentifierExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 163
                self.match(yapis2Parser.IDENTIFIER)
                pass

            elif la_ == 3:
                localctx = yapis2Parser.FunctionCallExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 164
                self.functionCall()
                pass

            elif la_ == 4:
                localctx = yapis2Parser.ParenthesizedExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 165
                self.match(yapis2Parser.T__1)
                self.state = 166
                self.expression(0)
                self.state = 167
                self.match(yapis2Parser.T__2)
                pass

            elif la_ == 5:
                localctx = yapis2Parser.CastExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 169
                self.match(yapis2Parser.T__1)
                self.state = 170
                self.type_()
                self.state = 171
                self.match(yapis2Parser.T__2)
                self.state = 172
                self.expression(7)
                pass

            elif la_ == 6:
                localctx = yapis2Parser.NotExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 174
                self.match(yapis2Parser.T__23)
                self.state = 175
                self.expression(6)
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 195
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,16,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 193
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,15,self._ctx)
                    if la_ == 1:
                        localctx = yapis2Parser.MultiplicativeExprContext(self, yapis2Parser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 178
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 179
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 469762048) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 180
                        self.expression(5)
                        pass

                    elif la_ == 2:
                        localctx = yapis2Parser.AdditiveExprContext(self, yapis2Parser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 181
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 182
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==29 or _la==30):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 183
                        self.expression(4)
                        pass

                    elif la_ == 3:
                        localctx = yapis2Parser.ComparisonExprContext(self, yapis2Parser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 184
                        if not self.precpred(self._ctx, 2):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 2)")
                        self.state = 185
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 135291469824) != 0)):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 186
                        self.expression(3)
                        pass

                    elif la_ == 4:
                        localctx = yapis2Parser.LogicalExprContext(self, yapis2Parser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 187
                        if not self.precpred(self._ctx, 1):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 1)")
                        self.state = 188
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==37 or _la==38):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 189
                        self.expression(2)
                        pass

                    elif la_ == 5:
                        localctx = yapis2Parser.MemberAccessExprContext(self, yapis2Parser.ExpressionContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 190
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 191
                        self.match(yapis2Parser.T__24)
                        self.state = 192
                        self.match(yapis2Parser.IDENTIFIER)
                        pass

             
                self.state = 197
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class BuiltInFunctionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return yapis2Parser.RULE_builtInFunction

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBuiltInFunction" ):
                listener.enterBuiltInFunction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBuiltInFunction" ):
                listener.exitBuiltInFunction(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBuiltInFunction" ):
                return visitor.visitBuiltInFunction(self)
            else:
                return visitor.visitChildren(self)




    def builtInFunction(self):

        localctx = yapis2Parser.BuiltInFunctionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_builtInFunction)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 198
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 17042430232448) != 0)):
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


    class LiteralContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(yapis2Parser.INT, 0)

        def STRING(self):
            return self.getToken(yapis2Parser.STRING, 0)

        def BOOL(self):
            return self.getToken(yapis2Parser.BOOL, 0)

        def getRuleIndex(self):
            return yapis2Parser.RULE_literal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral" ):
                listener.enterLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral" ):
                listener.exitLiteral(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLiteral" ):
                return visitor.visitLiteral(self)
            else:
                return visitor.visitChildren(self)




    def literal(self):

        localctx = yapis2Parser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_literal)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 200
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 246290604621824) != 0)):
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



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[16] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 3)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 2)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 1)
         

            if predIndex == 4:
                return self.precpred(self._ctx, 5)
         





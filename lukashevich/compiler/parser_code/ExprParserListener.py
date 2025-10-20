# Generated from ./ExprParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ExprParser import ExprParser
else:
    from ExprParser import ExprParser

# This class defines a complete listener for a parse tree produced by ExprParser.
class ExprParserListener(ParseTreeListener):

    # Enter a parse tree produced by ExprParser#program.
    def enterProgram(self, ctx:ExprParser.ProgramContext):
        pass

    # Exit a parse tree produced by ExprParser#program.
    def exitProgram(self, ctx:ExprParser.ProgramContext):
        pass


    # Enter a parse tree produced by ExprParser#funcDef.
    def enterFuncDef(self, ctx:ExprParser.FuncDefContext):
        pass

    # Exit a parse tree produced by ExprParser#funcDef.
    def exitFuncDef(self, ctx:ExprParser.FuncDefContext):
        pass


    # Enter a parse tree produced by ExprParser#block.
    def enterBlock(self, ctx:ExprParser.BlockContext):
        pass

    # Exit a parse tree produced by ExprParser#block.
    def exitBlock(self, ctx:ExprParser.BlockContext):
        pass


    # Enter a parse tree produced by ExprParser#constructibleType.
    def enterConstructibleType(self, ctx:ExprParser.ConstructibleTypeContext):
        pass

    # Exit a parse tree produced by ExprParser#constructibleType.
    def exitConstructibleType(self, ctx:ExprParser.ConstructibleTypeContext):
        pass


    # Enter a parse tree produced by ExprParser#type.
    def enterType(self, ctx:ExprParser.TypeContext):
        pass

    # Exit a parse tree produced by ExprParser#type.
    def exitType(self, ctx:ExprParser.TypeContext):
        pass


    # Enter a parse tree produced by ExprParser#parameterList.
    def enterParameterList(self, ctx:ExprParser.ParameterListContext):
        pass

    # Exit a parse tree produced by ExprParser#parameterList.
    def exitParameterList(self, ctx:ExprParser.ParameterListContext):
        pass


    # Enter a parse tree produced by ExprParser#parameter.
    def enterParameter(self, ctx:ExprParser.ParameterContext):
        pass

    # Exit a parse tree produced by ExprParser#parameter.
    def exitParameter(self, ctx:ExprParser.ParameterContext):
        pass


    # Enter a parse tree produced by ExprParser#stat.
    def enterStat(self, ctx:ExprParser.StatContext):
        pass

    # Exit a parse tree produced by ExprParser#stat.
    def exitStat(self, ctx:ExprParser.StatContext):
        pass


    # Enter a parse tree produced by ExprParser#variableDef.
    def enterVariableDef(self, ctx:ExprParser.VariableDefContext):
        pass

    # Exit a parse tree produced by ExprParser#variableDef.
    def exitVariableDef(self, ctx:ExprParser.VariableDefContext):
        pass


    # Enter a parse tree produced by ExprParser#assignment.
    def enterAssignment(self, ctx:ExprParser.AssignmentContext):
        pass

    # Exit a parse tree produced by ExprParser#assignment.
    def exitAssignment(self, ctx:ExprParser.AssignmentContext):
        pass


    # Enter a parse tree produced by ExprParser#ifStat.
    def enterIfStat(self, ctx:ExprParser.IfStatContext):
        pass

    # Exit a parse tree produced by ExprParser#ifStat.
    def exitIfStat(self, ctx:ExprParser.IfStatContext):
        pass


    # Enter a parse tree produced by ExprParser#forStat.
    def enterForStat(self, ctx:ExprParser.ForStatContext):
        pass

    # Exit a parse tree produced by ExprParser#forStat.
    def exitForStat(self, ctx:ExprParser.ForStatContext):
        pass


    # Enter a parse tree produced by ExprParser#returnStat.
    def enterReturnStat(self, ctx:ExprParser.ReturnStatContext):
        pass

    # Exit a parse tree produced by ExprParser#returnStat.
    def exitReturnStat(self, ctx:ExprParser.ReturnStatContext):
        pass


    # Enter a parse tree produced by ExprParser#expr.
    def enterExpr(self, ctx:ExprParser.ExprContext):
        pass

    # Exit a parse tree produced by ExprParser#expr.
    def exitExpr(self, ctx:ExprParser.ExprContext):
        pass


    # Enter a parse tree produced by ExprParser#assignmentExpr.
    def enterAssignmentExpr(self, ctx:ExprParser.AssignmentExprContext):
        pass

    # Exit a parse tree produced by ExprParser#assignmentExpr.
    def exitAssignmentExpr(self, ctx:ExprParser.AssignmentExprContext):
        pass


    # Enter a parse tree produced by ExprParser#relationalExpr.
    def enterRelationalExpr(self, ctx:ExprParser.RelationalExprContext):
        pass

    # Exit a parse tree produced by ExprParser#relationalExpr.
    def exitRelationalExpr(self, ctx:ExprParser.RelationalExprContext):
        pass


    # Enter a parse tree produced by ExprParser#additiveExpr.
    def enterAdditiveExpr(self, ctx:ExprParser.AdditiveExprContext):
        pass

    # Exit a parse tree produced by ExprParser#additiveExpr.
    def exitAdditiveExpr(self, ctx:ExprParser.AdditiveExprContext):
        pass


    # Enter a parse tree produced by ExprParser#multiplicativeExpr.
    def enterMultiplicativeExpr(self, ctx:ExprParser.MultiplicativeExprContext):
        pass

    # Exit a parse tree produced by ExprParser#multiplicativeExpr.
    def exitMultiplicativeExpr(self, ctx:ExprParser.MultiplicativeExprContext):
        pass


    # Enter a parse tree produced by ExprParser#castExpr.
    def enterCastExpr(self, ctx:ExprParser.CastExprContext):
        pass

    # Exit a parse tree produced by ExprParser#castExpr.
    def exitCastExpr(self, ctx:ExprParser.CastExprContext):
        pass


    # Enter a parse tree produced by ExprParser#atom.
    def enterAtom(self, ctx:ExprParser.AtomContext):
        pass

    # Exit a parse tree produced by ExprParser#atom.
    def exitAtom(self, ctx:ExprParser.AtomContext):
        pass


    # Enter a parse tree produced by ExprParser#argumentList.
    def enterArgumentList(self, ctx:ExprParser.ArgumentListContext):
        pass

    # Exit a parse tree produced by ExprParser#argumentList.
    def exitArgumentList(self, ctx:ExprParser.ArgumentListContext):
        pass


    # Enter a parse tree produced by ExprParser#literal.
    def enterLiteral(self, ctx:ExprParser.LiteralContext):
        pass

    # Exit a parse tree produced by ExprParser#literal.
    def exitLiteral(self, ctx:ExprParser.LiteralContext):
        pass



del ExprParser
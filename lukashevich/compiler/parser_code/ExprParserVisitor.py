# Generated from ExprParser.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .ExprParser import ExprParser
else:
    from ExprParser import ExprParser

# This class defines a complete generic visitor for a parse tree produced by ExprParser.

class ExprParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ExprParser#program.
    def visitProgram(self, ctx:ExprParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#funcDef.
    def visitFuncDef(self, ctx:ExprParser.FuncDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#block.
    def visitBlock(self, ctx:ExprParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#constructibleType.
    def visitConstructibleType(self, ctx:ExprParser.ConstructibleTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#type.
    def visitType(self, ctx:ExprParser.TypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#parameterList.
    def visitParameterList(self, ctx:ExprParser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#parameter.
    def visitParameter(self, ctx:ExprParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#stat.
    def visitStat(self, ctx:ExprParser.StatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#variableDef.
    def visitVariableDef(self, ctx:ExprParser.VariableDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#assignment.
    def visitAssignment(self, ctx:ExprParser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#ifStat.
    def visitIfStat(self, ctx:ExprParser.IfStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#forStat.
    def visitForStat(self, ctx:ExprParser.ForStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#returnStat.
    def visitReturnStat(self, ctx:ExprParser.ReturnStatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#expr.
    def visitExpr(self, ctx:ExprParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#assignmentExpr.
    def visitAssignmentExpr(self, ctx:ExprParser.AssignmentExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#relationalExpr.
    def visitRelationalExpr(self, ctx:ExprParser.RelationalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#additiveExpr.
    def visitAdditiveExpr(self, ctx:ExprParser.AdditiveExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#multiplicativeExpr.
    def visitMultiplicativeExpr(self, ctx:ExprParser.MultiplicativeExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#castExpr.
    def visitCastExpr(self, ctx:ExprParser.CastExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#atom.
    def visitAtom(self, ctx:ExprParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#argumentList.
    def visitArgumentList(self, ctx:ExprParser.ArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExprParser#literal.
    def visitLiteral(self, ctx:ExprParser.LiteralContext):
        return self.visitChildren(ctx)



del ExprParser
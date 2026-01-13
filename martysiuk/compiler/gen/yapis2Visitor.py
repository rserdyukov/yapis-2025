# Generated from grammar/yapis2.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .yapis2Parser import yapis2Parser
else:
    from yapis2Parser import yapis2Parser

# This class defines a complete generic visitor for a parse tree produced by yapis2Parser.

class yapis2Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by yapis2Parser#program.
    def visitProgram(self, ctx:yapis2Parser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#functionDecl.
    def visitFunctionDecl(self, ctx:yapis2Parser.FunctionDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#parameterList.
    def visitParameterList(self, ctx:yapis2Parser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#parameter.
    def visitParameter(self, ctx:yapis2Parser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#type.
    def visitType(self, ctx:yapis2Parser.TypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#block.
    def visitBlock(self, ctx:yapis2Parser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#statement.
    def visitStatement(self, ctx:yapis2Parser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#assignment.
    def visitAssignment(self, ctx:yapis2Parser.AssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#variableDecl.
    def visitVariableDecl(self, ctx:yapis2Parser.VariableDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#ifStatement.
    def visitIfStatement(self, ctx:yapis2Parser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#whileStatement.
    def visitWhileStatement(self, ctx:yapis2Parser.WhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#forStatement.
    def visitForStatement(self, ctx:yapis2Parser.ForStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#breakStatement.
    def visitBreakStatement(self, ctx:yapis2Parser.BreakStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#returnStatement.
    def visitReturnStatement(self, ctx:yapis2Parser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#functionCall.
    def visitFunctionCall(self, ctx:yapis2Parser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#argumentList.
    def visitArgumentList(self, ctx:yapis2Parser.ArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#notExpr.
    def visitNotExpr(self, ctx:yapis2Parser.NotExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#castExpr.
    def visitCastExpr(self, ctx:yapis2Parser.CastExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#parenthesizedExpr.
    def visitParenthesizedExpr(self, ctx:yapis2Parser.ParenthesizedExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#literalExpr.
    def visitLiteralExpr(self, ctx:yapis2Parser.LiteralExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#logicalExpr.
    def visitLogicalExpr(self, ctx:yapis2Parser.LogicalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#functionCallExpr.
    def visitFunctionCallExpr(self, ctx:yapis2Parser.FunctionCallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#memberAccessExpr.
    def visitMemberAccessExpr(self, ctx:yapis2Parser.MemberAccessExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#comparisonExpr.
    def visitComparisonExpr(self, ctx:yapis2Parser.ComparisonExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#additiveExpr.
    def visitAdditiveExpr(self, ctx:yapis2Parser.AdditiveExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#multiplicativeExpr.
    def visitMultiplicativeExpr(self, ctx:yapis2Parser.MultiplicativeExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#identifierExpr.
    def visitIdentifierExpr(self, ctx:yapis2Parser.IdentifierExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#builtInFunction.
    def visitBuiltInFunction(self, ctx:yapis2Parser.BuiltInFunctionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by yapis2Parser#literal.
    def visitLiteral(self, ctx:yapis2Parser.LiteralContext):
        return self.visitChildren(ctx)



del yapis2Parser

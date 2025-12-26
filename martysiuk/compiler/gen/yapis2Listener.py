# Generated from grammar/yapis2.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .yapis2Parser import yapis2Parser
else:
    from yapis2Parser import yapis2Parser

# This class defines a complete listener for a parse tree produced by yapis2Parser.
class yapis2Listener(ParseTreeListener):

    # Enter a parse tree produced by yapis2Parser#program.
    def enterProgram(self, ctx:yapis2Parser.ProgramContext):
        pass

    # Exit a parse tree produced by yapis2Parser#program.
    def exitProgram(self, ctx:yapis2Parser.ProgramContext):
        pass


    # Enter a parse tree produced by yapis2Parser#functionDecl.
    def enterFunctionDecl(self, ctx:yapis2Parser.FunctionDeclContext):
        pass

    # Exit a parse tree produced by yapis2Parser#functionDecl.
    def exitFunctionDecl(self, ctx:yapis2Parser.FunctionDeclContext):
        pass


    # Enter a parse tree produced by yapis2Parser#parameterList.
    def enterParameterList(self, ctx:yapis2Parser.ParameterListContext):
        pass

    # Exit a parse tree produced by yapis2Parser#parameterList.
    def exitParameterList(self, ctx:yapis2Parser.ParameterListContext):
        pass


    # Enter a parse tree produced by yapis2Parser#parameter.
    def enterParameter(self, ctx:yapis2Parser.ParameterContext):
        pass

    # Exit a parse tree produced by yapis2Parser#parameter.
    def exitParameter(self, ctx:yapis2Parser.ParameterContext):
        pass


    # Enter a parse tree produced by yapis2Parser#type.
    def enterType(self, ctx:yapis2Parser.TypeContext):
        pass

    # Exit a parse tree produced by yapis2Parser#type.
    def exitType(self, ctx:yapis2Parser.TypeContext):
        pass


    # Enter a parse tree produced by yapis2Parser#block.
    def enterBlock(self, ctx:yapis2Parser.BlockContext):
        pass

    # Exit a parse tree produced by yapis2Parser#block.
    def exitBlock(self, ctx:yapis2Parser.BlockContext):
        pass


    # Enter a parse tree produced by yapis2Parser#statement.
    def enterStatement(self, ctx:yapis2Parser.StatementContext):
        pass

    # Exit a parse tree produced by yapis2Parser#statement.
    def exitStatement(self, ctx:yapis2Parser.StatementContext):
        pass


    # Enter a parse tree produced by yapis2Parser#assignment.
    def enterAssignment(self, ctx:yapis2Parser.AssignmentContext):
        pass

    # Exit a parse tree produced by yapis2Parser#assignment.
    def exitAssignment(self, ctx:yapis2Parser.AssignmentContext):
        pass


    # Enter a parse tree produced by yapis2Parser#variableDecl.
    def enterVariableDecl(self, ctx:yapis2Parser.VariableDeclContext):
        pass

    # Exit a parse tree produced by yapis2Parser#variableDecl.
    def exitVariableDecl(self, ctx:yapis2Parser.VariableDeclContext):
        pass


    # Enter a parse tree produced by yapis2Parser#ifStatement.
    def enterIfStatement(self, ctx:yapis2Parser.IfStatementContext):
        pass

    # Exit a parse tree produced by yapis2Parser#ifStatement.
    def exitIfStatement(self, ctx:yapis2Parser.IfStatementContext):
        pass


    # Enter a parse tree produced by yapis2Parser#whileStatement.
    def enterWhileStatement(self, ctx:yapis2Parser.WhileStatementContext):
        pass

    # Exit a parse tree produced by yapis2Parser#whileStatement.
    def exitWhileStatement(self, ctx:yapis2Parser.WhileStatementContext):
        pass


    # Enter a parse tree produced by yapis2Parser#forStatement.
    def enterForStatement(self, ctx:yapis2Parser.ForStatementContext):
        pass

    # Exit a parse tree produced by yapis2Parser#forStatement.
    def exitForStatement(self, ctx:yapis2Parser.ForStatementContext):
        pass


    # Enter a parse tree produced by yapis2Parser#breakStatement.
    def enterBreakStatement(self, ctx:yapis2Parser.BreakStatementContext):
        pass

    # Exit a parse tree produced by yapis2Parser#breakStatement.
    def exitBreakStatement(self, ctx:yapis2Parser.BreakStatementContext):
        pass


    # Enter a parse tree produced by yapis2Parser#returnStatement.
    def enterReturnStatement(self, ctx:yapis2Parser.ReturnStatementContext):
        pass

    # Exit a parse tree produced by yapis2Parser#returnStatement.
    def exitReturnStatement(self, ctx:yapis2Parser.ReturnStatementContext):
        pass


    # Enter a parse tree produced by yapis2Parser#functionCall.
    def enterFunctionCall(self, ctx:yapis2Parser.FunctionCallContext):
        pass

    # Exit a parse tree produced by yapis2Parser#functionCall.
    def exitFunctionCall(self, ctx:yapis2Parser.FunctionCallContext):
        pass


    # Enter a parse tree produced by yapis2Parser#argumentList.
    def enterArgumentList(self, ctx:yapis2Parser.ArgumentListContext):
        pass

    # Exit a parse tree produced by yapis2Parser#argumentList.
    def exitArgumentList(self, ctx:yapis2Parser.ArgumentListContext):
        pass


    # Enter a parse tree produced by yapis2Parser#notExpr.
    def enterNotExpr(self, ctx:yapis2Parser.NotExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#notExpr.
    def exitNotExpr(self, ctx:yapis2Parser.NotExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#castExpr.
    def enterCastExpr(self, ctx:yapis2Parser.CastExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#castExpr.
    def exitCastExpr(self, ctx:yapis2Parser.CastExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#parenthesizedExpr.
    def enterParenthesizedExpr(self, ctx:yapis2Parser.ParenthesizedExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#parenthesizedExpr.
    def exitParenthesizedExpr(self, ctx:yapis2Parser.ParenthesizedExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#literalExpr.
    def enterLiteralExpr(self, ctx:yapis2Parser.LiteralExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#literalExpr.
    def exitLiteralExpr(self, ctx:yapis2Parser.LiteralExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#logicalExpr.
    def enterLogicalExpr(self, ctx:yapis2Parser.LogicalExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#logicalExpr.
    def exitLogicalExpr(self, ctx:yapis2Parser.LogicalExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#functionCallExpr.
    def enterFunctionCallExpr(self, ctx:yapis2Parser.FunctionCallExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#functionCallExpr.
    def exitFunctionCallExpr(self, ctx:yapis2Parser.FunctionCallExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#memberAccessExpr.
    def enterMemberAccessExpr(self, ctx:yapis2Parser.MemberAccessExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#memberAccessExpr.
    def exitMemberAccessExpr(self, ctx:yapis2Parser.MemberAccessExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#comparisonExpr.
    def enterComparisonExpr(self, ctx:yapis2Parser.ComparisonExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#comparisonExpr.
    def exitComparisonExpr(self, ctx:yapis2Parser.ComparisonExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#additiveExpr.
    def enterAdditiveExpr(self, ctx:yapis2Parser.AdditiveExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#additiveExpr.
    def exitAdditiveExpr(self, ctx:yapis2Parser.AdditiveExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#multiplicativeExpr.
    def enterMultiplicativeExpr(self, ctx:yapis2Parser.MultiplicativeExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#multiplicativeExpr.
    def exitMultiplicativeExpr(self, ctx:yapis2Parser.MultiplicativeExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#identifierExpr.
    def enterIdentifierExpr(self, ctx:yapis2Parser.IdentifierExprContext):
        pass

    # Exit a parse tree produced by yapis2Parser#identifierExpr.
    def exitIdentifierExpr(self, ctx:yapis2Parser.IdentifierExprContext):
        pass


    # Enter a parse tree produced by yapis2Parser#builtInFunction.
    def enterBuiltInFunction(self, ctx:yapis2Parser.BuiltInFunctionContext):
        pass

    # Exit a parse tree produced by yapis2Parser#builtInFunction.
    def exitBuiltInFunction(self, ctx:yapis2Parser.BuiltInFunctionContext):
        pass


    # Enter a parse tree produced by yapis2Parser#literal.
    def enterLiteral(self, ctx:yapis2Parser.LiteralContext):
        pass

    # Exit a parse tree produced by yapis2Parser#literal.
    def exitLiteral(self, ctx:yapis2Parser.LiteralContext):
        pass



del yapis2Parser
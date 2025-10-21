package org.bsuir.parser;
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link LangParser}.
 */
public interface LangListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link LangParser#program}.
	 * @param ctx the parse tree
	 */
	void enterProgram(LangParser.ProgramContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#program}.
	 * @param ctx the parse tree
	 */
	void exitProgram(LangParser.ProgramContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#statement}.
	 * @param ctx the parse tree
	 */
	void enterStatement(LangParser.StatementContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#statement}.
	 * @param ctx the parse tree
	 */
	void exitStatement(LangParser.StatementContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#functionDef}.
	 * @param ctx the parse tree
	 */
	void enterFunctionDef(LangParser.FunctionDefContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#functionDef}.
	 * @param ctx the parse tree
	 */
	void exitFunctionDef(LangParser.FunctionDefContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#parameterList}.
	 * @param ctx the parse tree
	 */
	void enterParameterList(LangParser.ParameterListContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#parameterList}.
	 * @param ctx the parse tree
	 */
	void exitParameterList(LangParser.ParameterListContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#parameter}.
	 * @param ctx the parse tree
	 */
	void enterParameter(LangParser.ParameterContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#parameter}.
	 * @param ctx the parse tree
	 */
	void exitParameter(LangParser.ParameterContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#simpleStmt}.
	 * @param ctx the parse tree
	 */
	void enterSimpleStmt(LangParser.SimpleStmtContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#simpleStmt}.
	 * @param ctx the parse tree
	 */
	void exitSimpleStmt(LangParser.SimpleStmtContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#varDecl}.
	 * @param ctx the parse tree
	 */
	void enterVarDecl(LangParser.VarDeclContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#varDecl}.
	 * @param ctx the parse tree
	 */
	void exitVarDecl(LangParser.VarDeclContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#assignment}.
	 * @param ctx the parse tree
	 */
	void enterAssignment(LangParser.AssignmentContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#assignment}.
	 * @param ctx the parse tree
	 */
	void exitAssignment(LangParser.AssignmentContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#exprList}.
	 * @param ctx the parse tree
	 */
	void enterExprList(LangParser.ExprListContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#exprList}.
	 * @param ctx the parse tree
	 */
	void exitExprList(LangParser.ExprListContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#ifStmt}.
	 * @param ctx the parse tree
	 */
	void enterIfStmt(LangParser.IfStmtContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#ifStmt}.
	 * @param ctx the parse tree
	 */
	void exitIfStmt(LangParser.IfStmtContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#whileStmt}.
	 * @param ctx the parse tree
	 */
	void enterWhileStmt(LangParser.WhileStmtContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#whileStmt}.
	 * @param ctx the parse tree
	 */
	void exitWhileStmt(LangParser.WhileStmtContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#forStmt}.
	 * @param ctx the parse tree
	 */
	void enterForStmt(LangParser.ForStmtContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#forStmt}.
	 * @param ctx the parse tree
	 */
	void exitForStmt(LangParser.ForStmtContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#forInit}.
	 * @param ctx the parse tree
	 */
	void enterForInit(LangParser.ForInitContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#forInit}.
	 * @param ctx the parse tree
	 */
	void exitForInit(LangParser.ForInitContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#forCond}.
	 * @param ctx the parse tree
	 */
	void enterForCond(LangParser.ForCondContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#forCond}.
	 * @param ctx the parse tree
	 */
	void exitForCond(LangParser.ForCondContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#forIter}.
	 * @param ctx the parse tree
	 */
	void enterForIter(LangParser.ForIterContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#forIter}.
	 * @param ctx the parse tree
	 */
	void exitForIter(LangParser.ForIterContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#funcCall}.
	 * @param ctx the parse tree
	 */
	void enterFuncCall(LangParser.FuncCallContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#funcCall}.
	 * @param ctx the parse tree
	 */
	void exitFuncCall(LangParser.FuncCallContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#argList}.
	 * @param ctx the parse tree
	 */
	void enterArgList(LangParser.ArgListContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#argList}.
	 * @param ctx the parse tree
	 */
	void exitArgList(LangParser.ArgListContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#expr}.
	 * @param ctx the parse tree
	 */
	void enterExpr(LangParser.ExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#expr}.
	 * @param ctx the parse tree
	 */
	void exitExpr(LangParser.ExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#prefixExpr}.
	 * @param ctx the parse tree
	 */
	void enterPrefixExpr(LangParser.PrefixExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#prefixExpr}.
	 * @param ctx the parse tree
	 */
	void exitPrefixExpr(LangParser.PrefixExprContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#postfixExpr}.
	 * @param ctx the parse tree
	 */
	void enterPostfixExpr(LangParser.PostfixExprContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#postfixExpr}.
	 * @param ctx the parse tree
	 */
	void exitPostfixExpr(LangParser.PostfixExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code parensExpr}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterParensExpr(LangParser.ParensExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code parensExpr}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitParensExpr(LangParser.ParensExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code castExpr}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterCastExpr(LangParser.CastExprContext ctx);
	/**
	 * Exit a parse tree produced by the {@code castExpr}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitCastExpr(LangParser.CastExprContext ctx);
	/**
	 * Enter a parse tree produced by the {@code funcCallPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterFuncCallPrimary(LangParser.FuncCallPrimaryContext ctx);
	/**
	 * Exit a parse tree produced by the {@code funcCallPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitFuncCallPrimary(LangParser.FuncCallPrimaryContext ctx);
	/**
	 * Enter a parse tree produced by the {@code setLiteralPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterSetLiteralPrimary(LangParser.SetLiteralPrimaryContext ctx);
	/**
	 * Exit a parse tree produced by the {@code setLiteralPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitSetLiteralPrimary(LangParser.SetLiteralPrimaryContext ctx);
	/**
	 * Enter a parse tree produced by the {@code elementLiteralPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterElementLiteralPrimary(LangParser.ElementLiteralPrimaryContext ctx);
	/**
	 * Exit a parse tree produced by the {@code elementLiteralPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitElementLiteralPrimary(LangParser.ElementLiteralPrimaryContext ctx);
	/**
	 * Enter a parse tree produced by the {@code literalPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterLiteralPrimary(LangParser.LiteralPrimaryContext ctx);
	/**
	 * Exit a parse tree produced by the {@code literalPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitLiteralPrimary(LangParser.LiteralPrimaryContext ctx);
	/**
	 * Enter a parse tree produced by the {@code idWithIndex}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void enterIdWithIndex(LangParser.IdWithIndexContext ctx);
	/**
	 * Exit a parse tree produced by the {@code idWithIndex}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 */
	void exitIdWithIndex(LangParser.IdWithIndexContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#indexSuffix}.
	 * @param ctx the parse tree
	 */
	void enterIndexSuffix(LangParser.IndexSuffixContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#indexSuffix}.
	 * @param ctx the parse tree
	 */
	void exitIndexSuffix(LangParser.IndexSuffixContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#setLiteral}.
	 * @param ctx the parse tree
	 */
	void enterSetLiteral(LangParser.SetLiteralContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#setLiteral}.
	 * @param ctx the parse tree
	 */
	void exitSetLiteral(LangParser.SetLiteralContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#elementLiteral}.
	 * @param ctx the parse tree
	 */
	void enterElementLiteral(LangParser.ElementLiteralContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#elementLiteral}.
	 * @param ctx the parse tree
	 */
	void exitElementLiteral(LangParser.ElementLiteralContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#literal}.
	 * @param ctx the parse tree
	 */
	void enterLiteral(LangParser.LiteralContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#literal}.
	 * @param ctx the parse tree
	 */
	void exitLiteral(LangParser.LiteralContext ctx);
	/**
	 * Enter a parse tree produced by {@link LangParser#type}.
	 * @param ctx the parse tree
	 */
	void enterType(LangParser.TypeContext ctx);
	/**
	 * Exit a parse tree produced by {@link LangParser#type}.
	 * @param ctx the parse tree
	 */
	void exitType(LangParser.TypeContext ctx);
}
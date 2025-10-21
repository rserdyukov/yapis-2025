package org.bsuir.parser;
import org.antlr.v4.runtime.tree.ParseTreeVisitor;

/**
 * This interface defines a complete generic visitor for a parse tree produced
 * by {@link LangParser}.
 *
 * @param <T> The return type of the visit operation. Use {@link Void} for
 * operations with no return type.
 */
public interface LangVisitor<T> extends ParseTreeVisitor<T> {
	/**
	 * Visit a parse tree produced by {@link LangParser#program}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitProgram(LangParser.ProgramContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#statement}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitStatement(LangParser.StatementContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#functionDef}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFunctionDef(LangParser.FunctionDefContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#parameterList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParameterList(LangParser.ParameterListContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#parameter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParameter(LangParser.ParameterContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#simpleStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSimpleStmt(LangParser.SimpleStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#varDecl}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitVarDecl(LangParser.VarDeclContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#assignment}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitAssignment(LangParser.AssignmentContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#exprList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExprList(LangParser.ExprListContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#ifStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIfStmt(LangParser.IfStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#whileStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitWhileStmt(LangParser.WhileStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#forStmt}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForStmt(LangParser.ForStmtContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#forInit}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForInit(LangParser.ForInitContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#forCond}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForCond(LangParser.ForCondContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#forIter}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitForIter(LangParser.ForIterContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#funcCall}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFuncCall(LangParser.FuncCallContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#argList}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitArgList(LangParser.ArgListContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#expr}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitExpr(LangParser.ExprContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#prefixExpr}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPrefixExpr(LangParser.PrefixExprContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#postfixExpr}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitPostfixExpr(LangParser.PostfixExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code parensExpr}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitParensExpr(LangParser.ParensExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code castExpr}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitCastExpr(LangParser.CastExprContext ctx);
	/**
	 * Visit a parse tree produced by the {@code funcCallPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitFuncCallPrimary(LangParser.FuncCallPrimaryContext ctx);
	/**
	 * Visit a parse tree produced by the {@code setLiteralPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSetLiteralPrimary(LangParser.SetLiteralPrimaryContext ctx);
	/**
	 * Visit a parse tree produced by the {@code elementLiteralPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitElementLiteralPrimary(LangParser.ElementLiteralPrimaryContext ctx);
	/**
	 * Visit a parse tree produced by the {@code literalPrimary}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLiteralPrimary(LangParser.LiteralPrimaryContext ctx);
	/**
	 * Visit a parse tree produced by the {@code idWithIndex}
	 * labeled alternative in {@link LangParser#primary}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIdWithIndex(LangParser.IdWithIndexContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#indexSuffix}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitIndexSuffix(LangParser.IndexSuffixContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#setLiteral}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitSetLiteral(LangParser.SetLiteralContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#elementLiteral}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitElementLiteral(LangParser.ElementLiteralContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#literal}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitLiteral(LangParser.LiteralContext ctx);
	/**
	 * Visit a parse tree produced by {@link LangParser#type}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitType(LangParser.TypeContext ctx);
}
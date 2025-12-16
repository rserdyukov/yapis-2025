package io.hohichh.mcl.compiler.analyzer.handlers;

import io.hohichh.mcl.compiler.MCLBaseListener;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.SemanticError;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.*;
import io.hohichh.mcl.compiler.analyzer.handlers.nodes.*;
import io.hohichh.mcl.compiler.analyzer.handlers.scope.ScopeManager;


import java.util.*;


public class SemanticErrorListener extends MCLBaseListener {
    private final AnalysisContext context = new AnalysisContext();
    private final FunctionHandler functionHandler;
    private final SuiteHandler suiteHandler;
    private final StatementHandler statementHandler;
    private final ExpressionHandler expressionHandler;
    private final PrimaryHandler primaryHandler;

    public SemanticErrorListener(){
        functionHandler = new FunctionHandler(context);
        statementHandler = new StatementHandler(context);
        expressionHandler = new ExpressionHandler(context);
        suiteHandler = new SuiteHandler(context);
        primaryHandler = new PrimaryHandler(context);
    }

    public List<SemanticError> getErrors() {
        return context.getErrors();
    }

    @Override
    public void enterProgram(MCLParser.ProgramContext ctx) {
        ScopeManager scopeManager = context.getScopeManager();

        // --- IO-operations ---

        // write(value: any)
        scopeManager.define(new FunctionSymbol("write", MclType.VOID,
                List.of(new VariableSymbol("value", MclType.UNKNOWN))
        ));

        // read() -> int | float | vector | matrix | boolean
        scopeManager.define(new FunctionSymbol("read", MclType.UNKNOWN, List.of()));

        // read_file(path: string) -> vector | matrix
        scopeManager.define(new FunctionSymbol("read_file", MclType.UNKNOWN,
                List.of(new VariableSymbol("path", MclType.STRING))
        ));

        // write_file(path: string, data: vector | matrix) -> void
        scopeManager.define(new FunctionSymbol("write_file", MclType.VOID,
                List.of(
                        new VariableSymbol("path", MclType.STRING),
                        new VariableSymbol("data", MclType.UNKNOWN)
                )
        ));

        // --- data structures generation

        // zeros(size: int) -> vector
        scopeManager.define(new FunctionSymbol("zeros", MclType.VECTOR,
                List.of(new VariableSymbol("size", MclType.INT))
        ));

        // zeros(rows: int, cols: int) -> matrix
        scopeManager.define(new FunctionSymbol("zeros", MclType.MATRIX,
                List.of(
                        new VariableSymbol("rows", MclType.INT),
                        new VariableSymbol("cols", MclType.INT)
                )
        ));

        // ones(size: int) -> vector
        scopeManager.define(new FunctionSymbol("ones", MclType.VECTOR,
                List.of(new VariableSymbol("size", MclType.INT))
        ));

        // ones(rows: int, cols: int) -> matrix
        scopeManager.define(new FunctionSymbol("ones", MclType.MATRIX,
                List.of(
                        new VariableSymbol("rows", MclType.INT),
                        new VariableSymbol("cols", MclType.INT)
                )
        ));

        // identity(s: int) -> matrix
        scopeManager.define(new FunctionSymbol("identity", MclType.MATRIX,
                List.of(new VariableSymbol("s", MclType.INT))
        ));

        // random_int(size: int, limit: int) -> vector
        scopeManager.define(new FunctionSymbol("random_int", MclType.VECTOR,
                List.of(
                        new VariableSymbol("size", MclType.INT),
                        new VariableSymbol("limit", MclType.INT)
                )
        ));

        // random_int(size: int, start: int, limit: int) -> vector
        scopeManager.define(new FunctionSymbol("random_int", MclType.VECTOR,
                List.of(
                        new VariableSymbol("size", MclType.INT),
                        new VariableSymbol("start", MclType.INT),
                        new VariableSymbol("limit", MclType.INT)
                )
        ));

        // random_int(rows: int, cols: int, limit: int) -> matrix
        scopeManager.define(new FunctionSymbol("random_int", MclType.MATRIX,
                List.of(
                        new VariableSymbol("rows", MclType.INT),
                        new VariableSymbol("cols", MclType.INT),
                        new VariableSymbol("limit", MclType.INT)
                )
        ));

        // random_int(rows: int, cols: int, start: int, limit: int) -> matrix
        scopeManager.define(new FunctionSymbol("random_int", MclType.MATRIX,
                List.of(
                        new VariableSymbol("rows", MclType.INT),
                        new VariableSymbol("cols", MclType.INT),
                        new VariableSymbol("start", MclType.INT),
                        new VariableSymbol("limit", MclType.INT)
                )
        ));

        // random_float(size: int) -> vector
        scopeManager.define(new FunctionSymbol("random_float", MclType.VECTOR,
                List.of(new VariableSymbol("size", MclType.INT))
        ));

        // random_float(rows: int, cols: int) -> matrix
        scopeManager.define(new FunctionSymbol("random_float", MclType.MATRIX,
                List.of(
                        new VariableSymbol("rows", MclType.INT),
                        new VariableSymbol("cols", MclType.INT)
                )
        ));

        // range(limit: int) -> vector
        scopeManager.define(new FunctionSymbol("range", MclType.RANGE,
                List.of(new VariableSymbol("limit", MclType.INT))
        ));

        // range(start: int, limit: int) -> vector
        scopeManager.define(new FunctionSymbol("range", MclType.RANGE,
                List.of(
                        new VariableSymbol("start", MclType.INT),
                        new VariableSymbol("limit", MclType.INT)
                )
        ));

        // range(start: int, limit: int, step: int) -> vector
        scopeManager.define(new FunctionSymbol("range", MclType.RANGE,
                List.of(
                        new VariableSymbol("start", MclType.INT),
                        new VariableSymbol("limit", MclType.INT),
                        new VariableSymbol("step", MclType.INT)
                )
        ));

        // diag(v: vector) -> matrix
        scopeManager.define(new FunctionSymbol("diag", MclType.MATRIX,
                List.of(new VariableSymbol("v", MclType.VECTOR))
        ));


        // --- utils ---

        // transpose(m: matrix) -> matrix
        scopeManager.define(new FunctionSymbol("transpose", MclType.MATRIX,
                List.of(new VariableSymbol("m", MclType.MATRIX))
        ));

        // dimension(m: matrix) -> tuple
        scopeManager.define(new FunctionSymbol("dimension", MclType.DIMENSIONS,
                List.of(new VariableSymbol("m", MclType.MATRIX))
        ));

        // dimension(v: vector) -> int
        scopeManager.define(new FunctionSymbol("dimension", MclType.INT,
                List.of(new VariableSymbol("v", MclType.VECTOR))
        ));

        // triag_upper(m: matrix) -> matrix
        scopeManager.define(new FunctionSymbol("triag_upper", MclType.MATRIX,
                List.of(new VariableSymbol("m", MclType.MATRIX))
        ));

        // triag_lower(m: matrix) -> matrix
        scopeManager.define(new FunctionSymbol("triag_lower", MclType.MATRIX,
                List.of(new VariableSymbol("m", MclType.MATRIX))
        ));

        // LU(m: matrix) -> tuple
        scopeManager.define(new FunctionSymbol("LU", MclType.TUPLE,
                List.of(new VariableSymbol("m", MclType.MATRIX))
        ));

        // inverse(m: matrix) -> matrix
        scopeManager.define(new FunctionSymbol("inverse", MclType.MATRIX,
                List.of(new VariableSymbol("m", MclType.MATRIX))
        ));
    }



    @Override
    public void exitReturnStatement(MCLParser.ReturnStatementContext ctx) {
        statementHandler.exitReturnStatement(ctx);
    }

    //scope entering control
    @Override
    public void enterSuite(MCLParser.SuiteContext ctx){
        suiteHandler.enterSuite(ctx);
    }

    @Override
    public void exitSuite(MCLParser.SuiteContext ctx){
        suiteHandler.exitSuite(ctx);
    }

    @Override
    public void exitAssignment(MCLParser.AssignmentContext ctx) {
        statementHandler.exitAssignment(ctx);
    }

    @Override
    public void exitForStatement(MCLParser.ForStatementContext ctx) {
        statementHandler.exitForStatement(ctx);
    }

    @Override
    public void exitIfStatement(MCLParser.IfStatementContext ctx) {
        statementHandler.exitIfStatement(ctx);
    }

    @Override
    public void exitWhileStatement(MCLParser.WhileStatementContext ctx) {
        statementHandler.exitWhileStatement(ctx);
    }

    @Override
    public void exitUntilStatement(MCLParser.UntilStatementContext ctx) {
        statementHandler.exitUntilStatement(ctx);
    }
    //==================================================================
    //---------------------FUNCTIONS--------------------------------------
    //===================================================================

    @Override
    public void enterFunctionDefinition(MCLParser.FunctionDefinitionContext ctx){
        functionHandler.enterFunctionDefinition(ctx);
    }

    @Override
    public void exitFunctionDefinition(MCLParser.FunctionDefinitionContext ctx){
        functionHandler.exitFunctionDefinition(ctx);
    }

    @Override
    public void enterLambdaExpression(MCLParser.LambdaExpressionContext ctx) {
        functionHandler.enterLambdaExpression(ctx);
    }

    @Override
    public void exitLambdaExpression(MCLParser.LambdaExpressionContext ctx){
        functionHandler.exitLambdaExpression(ctx);
    }

    //==================================================================
    //---------------------EXPRESSION--------------------------------------
    //===================================================================

    @Override
    public void exitUnaryMinusPlus(MCLParser.UnaryMinusPlusContext ctx) {
        expressionHandler.exitUnaryMinusPlus(ctx);
    }

    @Override
    public void exitUnaryNot(MCLParser.UnaryNotContext ctx) {
        expressionHandler.exitUnaryNot(ctx);
    }

    @Override
    public void exitPowerExpr(MCLParser.PowerExprContext ctx) {
        expressionHandler.exitPowerExpr(ctx);
    }

    @Override
    public void exitPowerExpression(MCLParser.PowerExpressionContext ctx) {
        expressionHandler.exitPowerExpression(ctx);
    }

    @Override
    public void exitMultiplicativeExpression(MCLParser.MultiplicativeExpressionContext ctx) {
        expressionHandler.exitMultiplicativeExpression(ctx);
    }

    @Override
    public void exitAdditiveExpression(MCLParser.AdditiveExpressionContext ctx) {
        expressionHandler.exitAdditiveExpression(ctx);
    }

    @Override
    public void exitRelationalExpression(MCLParser.RelationalExpressionContext ctx) {
        expressionHandler.exitRelationalExpression(ctx);
    }

    @Override
    public void exitEqualityExpression(MCLParser.EqualityExpressionContext ctx) {
        expressionHandler.exitEqualityExpression(ctx);
    }

    @Override
    public void exitLogicalAndExpression(MCLParser.LogicalAndExpressionContext ctx) {
        expressionHandler.exitLogicalAndExpression(ctx);
    }

    @Override
    public void exitLogicalOrExpression(MCLParser.LogicalOrExpressionContext ctx) {
        expressionHandler.exitLogicalOrExpression(ctx);
    }

    @Override
    public void exitLogicalOrExpr(MCLParser.LogicalOrExprContext ctx) {
        expressionHandler.exitLogicalOrExpr(ctx);
    }

    @Override
    public void exitTernaryExpression(MCLParser.TernaryExpressionContext ctx) {
        expressionHandler.exitTernaryExpression(ctx);
    }

    //==================================================================
    //---------------------PRIMARY--------------------------------------
    //===================================================================

    @Override
    public void exitVectorLiteralExpr(MCLParser.VectorLiteralExprContext ctx){
        primaryHandler.exitVectorLiteralExpr(ctx);
    }

    @Override
    public void exitMatrixLiteralExpr(MCLParser.MatrixLiteralExprContext ctx){
        primaryHandler.exitMatrixLiteralExpr(ctx);
    }

    @Override
    public void exitCreatorExpr(MCLParser.CreatorExprContext ctx) {
        primaryHandler.exitCreatorExpr(ctx);
    }

    @Override
    public void exitNormOrDeterminantExpr(MCLParser.NormOrDeterminantExprContext ctx){
        primaryHandler.exitNormOrDeterminantExpr(ctx);
    }

    @Override
    public void exitIdentifierExpr(MCLParser.IdentifierExprContext ctx){
        primaryHandler.exitIdentifierExpr(ctx);
    }

    @Override
    public void exitAssignableIdentifier(MCLParser.AssignableIdentifierContext ctx) {
        primaryHandler.exitAssignableIdentifier(ctx);
    }

    @Override
    public void exitAssignableElementAccess(MCLParser.AssignableElementAccessContext ctx) {
        primaryHandler.exitAssignableElementAccess(ctx);
    }

    @Override
    public void exitAssignableExpr(MCLParser.AssignableExprContext ctx) {
        primaryHandler.exitAssignableExpr(ctx);
    }

    @Override
    public void exitFunctionCall(MCLParser.FunctionCallContext ctx) {
        primaryHandler.exitFunctionCall(ctx);
    }

    @Override
    public void exitFunctionCallExpr(MCLParser.FunctionCallExprContext ctx) {
        primaryHandler.exitFunctionCallExpr(ctx);
    }

    @Override
    public void exitLiteralExpr(MCLParser.LiteralExprContext ctx) {
        primaryHandler.exitLiteralExpr(ctx);
    }

    @Override
    public void exitTypeCast(MCLParser.TypeCastContext ctx) {
        primaryHandler.exitTypeCast(ctx);
    }

    @Override
    public void exitParenthesizedExpr(MCLParser.ParenthesizedExprContext ctx) {
        primaryHandler.exitParenthesizedExpr(ctx);
    }
}

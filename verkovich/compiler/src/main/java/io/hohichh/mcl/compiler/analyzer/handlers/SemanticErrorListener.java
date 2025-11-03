package io.hohichh.mcl.compiler.analyzer.handlers;

import io.hohichh.mcl.compiler.MCLBaseListener;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.SemanticError;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.*;
import io.hohichh.mcl.compiler.analyzer.handlers.nodes.*;
import io.hohichh.mcl.compiler.analyzer.handlers.scope.ScopeManager;


import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.Token;

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
        scopeManager.define(new FunctionSymbol("range", MclType.VECTOR,
                List.of(new VariableSymbol("limit", MclType.INT))
        ));

        // range(start: int, limit: int) -> vector
        scopeManager.define(new FunctionSymbol("range", MclType.VECTOR,
                List.of(
                        new VariableSymbol("start", MclType.INT),
                        new VariableSymbol("limit", MclType.INT)
                )
        ));

        // range(start: int, limit: int, step: int) -> vector
        scopeManager.define(new FunctionSymbol("range", MclType.VECTOR,
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

        // dimension(v: vector) -> int
        scopeManager.define(new FunctionSymbol("dimension", MclType.INT,
                List.of(new VariableSymbol("v", MclType.VECTOR))
        ));

        // dimension(m: matrix) -> tuple
        scopeManager.define(new FunctionSymbol("dimension", MclType.TUPLE,
                List.of(new VariableSymbol("m", MclType.MATRIX))
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
    public void enterFunctionDefinition(MCLParser.FunctionDefinitionContext ctx){
        functionHandler.enterFunctionDefinition(ctx);
    }

    @Override
    public void exitFunctionDefinition(MCLParser.FunctionDefinitionContext ctx){
        functionHandler.exitFunctionDefinition(ctx);
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
    public void exitAssignableIdentifier(MCLParser.AssignableIdentifierContext ctx) {
        expressionHandler.exitAssignableIdentifier(ctx);
    }

    @Override
    public void exitAssignableElementAccess(MCLParser.AssignableElementAccessContext ctx) {
        expressionHandler.exitAssignableElementAccess(ctx);
    }

    @Override
    public void exitAssignableExpr(MCLParser.AssignableExprContext ctx) {
        expressionHandler.exitAssignableExpr(ctx);
    }


    public void exitFunctionCall(MCLParser.FunctionCallContext ctx){
        expressionHandler.exitFunctionCall(ctx);
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

    public void exitIdentifier(MCLParser.IdentifierExprContext ctx){
        primaryHandler.exitIdentifier(ctx);
    }
}

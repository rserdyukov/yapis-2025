package io.hohichh.mcl.compiler.analyzer.handlers.nodes;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.MclType;

public class StatementHandler {
    private final AnalysisContext env;

    public StatementHandler(AnalysisContext context){
        env = context;
    }

    public void exitReturnStatement(MCLParser.ReturnStatementContext ctx) {
        var currentFunction = env.getCurrentFunction();

        if (env.getCurrentFunction() == null) {
            env.addError(ctx, "Return statement found outside of a function body.");
            return;
        }

        env.setCurrentFunctionHasReturn(true);

        MclType expectedType = currentFunction.getType();
        MclType providedType;

        if (ctx.expression() != null) {
            providedType = env.getExpressionTypes().get(ctx.expression());
        } else {
            providedType = MclType.VOID;
        }
        //check return type match
        if (expectedType == MclType.VOID && providedType != MclType.VOID) {
            env.addError(ctx, "Void function '" + currentFunction.getName() + "' cannot return a value.");
        } else if (expectedType != MclType.VOID && providedType == MclType.VOID) {
            env.addError(ctx, "Function '" + currentFunction.getName() + "' must return a value of type "
                    + expectedType + ", but 'return' is empty.");
        } else if (expectedType != providedType && providedType != MclType.UNKNOWN) {
            env.addError(ctx, "Return type mismatch: function '" + currentFunction.getName() +
                    "' expects " + expectedType + ", but got " + providedType);
        }
    }


    public void exitIfStatement(MCLParser.IfStatementContext ctx) {
        var expressionTypes = env.getExpressionTypes();

        MCLParser.ExpressionContext conditionCtx = ctx.expression();

        MclType conditionType = expressionTypes.get(conditionCtx);

        if (conditionType != MclType.UNKNOWN && conditionType != MclType.BOOLEAN) {
            env.addError(conditionCtx.getStart(),
                    "If statement condition must be BOOLEAN, but got " + conditionType);
        }
    }


    public void exitWhileStatement(MCLParser.WhileStatementContext ctx) {
        var expressionTypes = env.getExpressionTypes();

        MCLParser.ExpressionContext conditionCtx = ctx.expression();
        MclType conditionType = expressionTypes.get(conditionCtx);

        if (conditionType != MclType.UNKNOWN && conditionType != MclType.BOOLEAN) {
            env.addError(conditionCtx.getStart(),
                    "While loop condition must be BOOLEAN, but got " + conditionType);
        }
    }


    public void exitUntilStatement(MCLParser.UntilStatementContext ctx) {
        var expressionTypes = env.getExpressionTypes();

        MCLParser.ExpressionContext conditionCtx = ctx.expression();
        MclType conditionType = expressionTypes.get(conditionCtx);

        if (conditionType != MclType.UNKNOWN && conditionType != MclType.BOOLEAN) {
            env.addError(conditionCtx.getStart(),
                    "Until loop condition must be BOOLEAN, but got " + conditionType);
        }
    }
}

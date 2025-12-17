package io.hohichh.mcl.compiler.analyzer.handlers.nodes;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.FunctionSymbol;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.MclType;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.Symbol;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.VariableSymbol;
import io.hohichh.mcl.compiler.analyzer.handlers.scope.ScopeManager;
import org.antlr.v4.runtime.Token;

import java.util.List;

public class StatementHandler {
    private final AnalysisContext env;

    public StatementHandler(AnalysisContext context){
        env = context;
    }

    public void exitAssignment(MCLParser.AssignmentContext ctx) {
        MCLParser.ExpressionContext rhsExprCtx = ctx.expression();
        MclType rhsType = env.getExpressionTypes().get(rhsExprCtx);

        if (rhsType == null) {
            return;
        }
        if (rhsType == MclType.VOID) {
            env.addError(rhsExprCtx.getStart(), "Cannot assign from a void function.");
            return;
        }
//        if(rhsType == MclType.UNKNOWN){}

        MCLParser.AssignableContext lhsCtx = ctx.assignable();

        if (lhsCtx instanceof MCLParser.AssignableIdentifierContext idCtx) {
            handleIdentifierAssignment(ctx, idCtx, rhsType);
        }
        else if (lhsCtx instanceof MCLParser.AssignableElementAccessContext accessCtx) {
            handleElementAccessAssignment(ctx, accessCtx, rhsType);
        }
    }

    private void handleIdentifierAssignment(MCLParser.AssignmentContext parentCtx,
                                            MCLParser.AssignableIdentifierContext lhsCtx,
                                            MclType rhsType) {
        ScopeManager scopeManager = env.getScopeManager();
        String varName = lhsCtx.IDENTIFIER().getText();
        Token varToken = lhsCtx.IDENTIFIER().getSymbol();

        MclType explicitType = (parentCtx.type() != null) ? env.resolveType(parentCtx.type()) : null;

        List<Symbol> existingSymbols = scopeManager.lookup(varName);
        boolean isDeclared = existingSymbols != null && !existingSymbols.isEmpty();

        MclType targetType;

        if (isDeclared) {
            if (explicitType != null) {
                env.addError(parentCtx.type().getStart(), "Cannot redeclare variable '"
                        + varName + "' with an explicit type.");
                return;
            }

            Symbol lhsSymbol = existingSymbols.get(0);
            if (lhsSymbol instanceof FunctionSymbol) {
                env.addError(varToken, "Cannot assign a value to a function: '" + varName + "'");
                return;
            }
            targetType = lhsSymbol.getType();

        } else {
            if (explicitType != null) {
                targetType = explicitType;
            } else {
                targetType = rhsType;
            }
            scopeManager.define(new VariableSymbol(varName, targetType));
        }

        checkTypeCompatibility(targetType, rhsType, parentCtx.expression().getStart());
    }

    private void handleElementAccessAssignment(MCLParser.AssignmentContext parentCtx,
                                               MCLParser.AssignableElementAccessContext lhsCtx,
                                               MclType rhsType) {
        if (parentCtx.type() != null) {
            env.addError(parentCtx.type().getStart(), "Cannot specify type when assigning to an element access.");
        }

        MclType lhsType = env.getAssignableTypes().get(lhsCtx);

        if (lhsType == MclType.UNKNOWN) return;

        checkTypeCompatibility(lhsType, rhsType, parentCtx.expression().getStart());
    }

    private void checkTypeCompatibility(MclType lhsType, MclType rhsType, Token errorToken) {
        if (lhsType == MclType.UNKNOWN || rhsType == MclType.UNKNOWN) return;

        if (lhsType == MclType.FLOAT && rhsType == MclType.INT) {
            return;
        }

        if (lhsType != rhsType) {
            env.addError(errorToken, "Type mismatch: cannot assign " + rhsType + " to " + lhsType + ".");
        }
    }


    public void exitForStatement(MCLParser.ForStatementContext ctx) {
        MclType iterableType = env.getExpressionTypes().get(ctx.expression());

        if (iterableType == MclType.UNKNOWN) return;

        if (iterableType != MclType.VECTOR &&
                iterableType != MclType.MATRIX &&
                iterableType != MclType.STRING &&
                iterableType != MclType.RANGE) {

            env.addError(ctx.expression().getStart(),
                    "For-loop expects an iterable type (VECTOR, MATRIX, STRING), but got " + iterableType);
        }
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

        if (expectedType == MclType.VOID && providedType != MclType.VOID) {
            env.addError(ctx, "Void function '" + currentFunction.getName() + "' cannot return a value.");
        } else if (expectedType != MclType.VOID && providedType == MclType.VOID) {
            env.addError(ctx, "Function '" + currentFunction.getName() + "' must return a value of type "
                    + expectedType + ", but 'return' is empty.");
        } else if (expectedType != providedType && providedType != MclType.UNKNOWN) {

            if (expectedType == MclType.FLOAT && providedType == MclType.INT) return;

            env.addError(ctx, "Return type mismatch: function '" + currentFunction.getName() +
                    "' expects " + expectedType + ", but got " + providedType);
        }
    }


    public void exitIfStatement(MCLParser.IfStatementContext ctx) {
        checkBooleanCondition(ctx.expression(), "If statement");
    }

    public void exitWhileStatement(MCLParser.WhileStatementContext ctx) {
        checkBooleanCondition(ctx.expression(), "While loop");
    }

    public void exitUntilStatement(MCLParser.UntilStatementContext ctx) {
        checkBooleanCondition(ctx.expression(), "Until loop");
    }

    private void checkBooleanCondition(MCLParser.ExpressionContext ctx, String stmtName) {
        MclType type = env.getExpressionTypes().get(ctx);
        if (type != MclType.UNKNOWN && type != MclType.BOOLEAN) {
            env.addError(ctx.getStart(), stmtName + " condition must be BOOLEAN, but got " + type);
        }
    }
}
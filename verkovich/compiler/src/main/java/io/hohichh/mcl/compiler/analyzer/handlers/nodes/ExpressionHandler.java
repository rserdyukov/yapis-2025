package io.hohichh.mcl.compiler.analyzer.handlers.nodes;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.FunctionSymbol;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.MclType;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.Symbol;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.VariableSymbol;
import io.hohichh.mcl.compiler.analyzer.handlers.scope.ScopeManager;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.Token;

import java.util.ArrayList;
import java.util.List;


public class ExpressionHandler {
    private final AnalysisContext env;

    public ExpressionHandler(AnalysisContext context) {
        env = context;
    }

    public void exitAssignment(MCLParser.AssignmentContext ctx) {
        MCLParser.ExpressionContext rhsExprCtx = ctx.expression();
        MclType rhsType = env.getExpressionTypes().get(rhsExprCtx);

        if (rhsType == null || rhsType == MclType.UNKNOWN) {
            return;
        }
        if (rhsType == MclType.VOID) {
            env.addError(rhsExprCtx.getStart(), "Cannot assign from a void function.");
            return;
        }

        MCLParser.AssignableContext lhsCtx = ctx.assignable();

        if (lhsCtx instanceof MCLParser.AssignableIdentifierContext) {
            handleIdentifierAssignment(ctx, (MCLParser.AssignableIdentifierContext) lhsCtx, rhsType);

        } else if (lhsCtx instanceof MCLParser.AssignableElementAccessContext) {
            handleElementAccessAssignment(ctx, (MCLParser.AssignableElementAccessContext) lhsCtx, rhsType);
        }
    }

    private void handleIdentifierAssignment(MCLParser.AssignmentContext parentCtx,
                                            MCLParser.AssignableIdentifierContext lhsCtx,
                                            MclType rhsType) {
        ScopeManager scopeManager = env.getScopeManager();
        String varName = lhsCtx.IDENTIFIER().getText();
        Token varToken = lhsCtx.IDENTIFIER().getSymbol();

        MclType lhsType;
        MclType explicitType = (parentCtx.type() != null) ? env.resolveType(parentCtx.type()) : null;

        List<Symbol> existingSymbols = scopeManager.lookup(varName);
        if (existingSymbols != null && !existingSymbols.isEmpty()) {

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

            lhsType = lhsSymbol.getType();

        } else {
            if (explicitType != null) {
                lhsType = explicitType;
            } else {
                lhsType = rhsType;
            }

            scopeManager.define(new VariableSymbol(varName, lhsType));
        }

        checkTypeCompatibility(lhsType, rhsType, parentCtx.expression().getStart());
    }


    private void handleElementAccessAssignment(MCLParser.AssignmentContext parentCtx,
                                               MCLParser.AssignableElementAccessContext lhsCtx,
                                               MclType rhsType) {


        MclType lhsType = env.getAssignableTypes().get(lhsCtx);

        if (lhsType == MclType.UNKNOWN) {
            return;
        }

        checkTypeCompatibility(lhsType, rhsType, parentCtx.expression().getStart());
    }

    public void exitAssignableIdentifier(MCLParser.AssignableIdentifierContext ctx) {
        String varName = ctx.IDENTIFIER().getText();
        List<Symbol> symbols = env.getScopeManager().lookup(varName);

        MclType finalType = MclType.UNKNOWN;
        if (symbols == null || symbols.isEmpty()) {
            env.addError(ctx.getStart(), "Undeclared variable: '" + varName + "'");
        } else if (symbols.get(0) instanceof FunctionSymbol) {
            env.addError(ctx.getStart(), "Cannot use function '" + varName + "' as a variable.");
        } else {
            finalType = symbols.get(0).getType();
        }

        env.getAssignableTypes().put(ctx, finalType);
    }


    public void exitAssignableElementAccess(MCLParser.AssignableElementAccessContext ctx) {
        MCLParser.AssignableContext baseCtx = ctx.assignable();
        MCLParser.ExpressionContext indexCtx = ctx.expression();

        MclType baseType = env.getAssignableTypes().get(baseCtx);
        MclType indexType = env.getExpressionTypes().get(indexCtx);

        MclType finalType = MclType.UNKNOWN;

        if (baseType == MclType.UNKNOWN || indexType == MclType.UNKNOWN) {
            env.getAssignableTypes().put(ctx, MclType.UNKNOWN);
            return;
        }

        if (indexType != MclType.INT) {
            env.addError(indexCtx.getStart(), "Index must be an INT, but got " + indexType);
        }

        switch (baseType) {
            case VECTOR:
                finalType = MclType.FLOAT;
                break;
            case MATRIX:
                finalType = MclType.VECTOR;
                break;
            case TUPLE:
                finalType = MclType.UNKNOWN;
                break;
            default:
                env.addError(baseCtx.getStart(), "Cannot apply index operator '[]' to a scalar type: " + baseType);
                break;
        }

        env.getAssignableTypes().put(ctx, finalType);
    }


    public void exitAssignableExpr(MCLParser.AssignableExprContext ctx) {
        MclType assignableType = env.getAssignableTypes().get(ctx.assignable());
        if (assignableType != null) {
            env.getExpressionTypes().put(ctx, assignableType);
        } else {
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
        }
    }

    private void checkTypeCompatibility(MclType lhsType, MclType rhsType, Token rhsToken) {
        if (rhsType == MclType.UNKNOWN || lhsType == MclType.UNKNOWN) {
            return;
        }

        if (lhsType == MclType.INT && rhsType == MclType.FLOAT) {
            env.addError(rhsToken, "Type mismatch: cannot assign FLOAT to INT. Use explicit (int) cast.");
        }
        else if (lhsType == MclType.FLOAT && rhsType == MclType.INT) {

        }
        else if (lhsType != rhsType) {
            env.addError(rhsToken, "Type mismatch: cannot assign " + rhsType + " to " + lhsType + ".");
        }
    }


    public void exitFunctionCall(MCLParser.FunctionCallContext ctx) {
        ScopeManager scopeManager = env.getScopeManager();
        var expressionTypes = env.getExpressionTypes();
        String funcName = ctx.IDENTIFIER().getText();
        Token funcToken = ctx.IDENTIFIER().getSymbol();

        List<Symbol> candidates = scopeManager.lookup(funcName);

        if (candidates == null || candidates.isEmpty()) {
            env.addError(funcToken, "Undeclared function: '" + funcName + "'");
            expressionTypes.put(ctx, MclType.UNKNOWN);
            return;
        }

        List<MCLParser.ExpressionContext> providedArgNodes = new ArrayList<>();
        if (ctx.argumentList() != null && ctx.argumentList().expression() != null) {
            providedArgNodes = ctx.argumentList().expression();
        }
        int providedArgCount = providedArgNodes.size();

        FunctionSymbol matchingOverload = null;
        for (Symbol s : candidates) {
            if (s instanceof FunctionSymbol fs) {
                if (fs.parameters().size() == providedArgCount) {
                    matchingOverload = fs;
                    break;
                }
            } else {
                env.addError(funcToken, "Symbol '" + funcName + "' is not a function and cannot be called.");
                expressionTypes.put(ctx, MclType.UNKNOWN);
                return;
            }
        }

        // check arguments amount
        if (matchingOverload == null) {
            env.addError(funcToken, "No overload for function '" + funcName +
                    "' takes " + providedArgCount + " arguments.");
            expressionTypes.put(ctx, MclType.UNKNOWN);
            return;
        }

        // check argument types
        List<VariableSymbol> expectedParams = matchingOverload.parameters();
        for (int i = 0; i < providedArgCount; i++) {
            MclType expectedType = expectedParams.get(i).getType();

            ParserRuleContext argNode = providedArgNodes.get(i);
            MclType providedType = expressionTypes.get(argNode);

            if (expectedType == MclType.UNKNOWN || providedType == MclType.UNKNOWN) {
                continue;
            }
            if (expectedType == MclType.FLOAT && providedType == MclType.INT) {
                continue;
            }
            if (expectedType != providedType) {
                env.addError(argNode.getStart(), "Argument " + (i + 1) + " of '" + funcName +
                        "': expected type " + expectedType + ", but got " + providedType);
            }
        }

        expressionTypes.put(ctx, matchingOverload.getType());
        if (ctx.getParent() instanceof MCLParser.FunctionCallExprContext) {
            expressionTypes.put(ctx.getParent(), matchingOverload.getType());
        }
    }
}
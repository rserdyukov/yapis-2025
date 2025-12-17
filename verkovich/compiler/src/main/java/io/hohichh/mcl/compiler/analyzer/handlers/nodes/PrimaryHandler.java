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

public class PrimaryHandler {
    private final AnalysisContext env;

    public PrimaryHandler(AnalysisContext context){
        env = context;
    }

    public void exitLiteralExpr(MCLParser.LiteralExprContext ctx) {
        MCLParser.LiteralContext lit = ctx.literal();
        MclType type = MclType.UNKNOWN;

        if (lit.INTEGER() != null) {
            type = MclType.INT;
        } else if (lit.FLOAT() != null || lit.NAN() != null || lit.INFINITY() != null) {
            type = MclType.FLOAT;
        } else if (lit.STRING() != null) {
            type = MclType.STRING;
        } else if (lit.TRUE() != null || lit.FALSE() != null) {
            type = MclType.BOOLEAN;
        }

        env.getExpressionTypes().put(ctx, type);
    }

    public void exitIdentifierExpr(MCLParser.IdentifierExprContext ctx){
        ScopeManager scopeManager = env.getScopeManager();
        String varName = ctx.IDENTIFIER().getText();
        Token varToken = ctx.IDENTIFIER().getSymbol();

        List<Symbol> symbols = scopeManager.lookup(varName);

        //сheck if identidier belongs to undefined or local-scope variable
        if (symbols == null || symbols.isEmpty()) {
            env.addError(varToken, "Undeclared variable: '" + varName + "'");
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
            return;
        }

        //check mistype of function call
        Symbol symbol = symbols.getFirst();
        if (symbol instanceof FunctionSymbol) {
            env.addError(varToken, "Cannot use function '" + varName + "' as a variable. Did you mean to call it using '()'?");
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
            return;
        }
        env.getExpressionTypes().put(ctx, symbol.getType());
    }

    public void exitParenthesizedExpr(MCLParser.ParenthesizedExprContext ctx) {
        MclType innerType = env.getExpressionTypes().get(ctx.expression());
        env.getExpressionTypes().put(ctx, innerType != null ? innerType : MclType.UNKNOWN);
    }

    public void exitVectorLiteralExpr(MCLParser.VectorLiteralExprContext ctx) {
        MCLParser.VectorLiteralContext vectorCtx = ctx.vectorLiteral();

        if (vectorCtx.expressionList() == null || vectorCtx.expressionList().expression().isEmpty()) {
            env.getExpressionTypes().put(ctx, MclType.VECTOR);
            return;
        }

        List<MCLParser.ExpressionContext> elements = vectorCtx.expressionList().expression();

        MclType firstType = env.getExpressionTypes().get(elements.get(0));

        boolean expectingScalars = (firstType == MclType.INT || firstType == MclType.FLOAT);
        boolean expectingVectors = (firstType == MclType.VECTOR);

        if (!expectingScalars && !expectingVectors) {
            if (firstType != MclType.UNKNOWN) {
                env.addError(elements.get(0).getStart(),
                        "Vector/Matrix literal can only contain scalars or vectors, but got " + firstType);
            }
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
            return;
        }

        for (MCLParser.ExpressionContext exprCtx : elements) {
            MclType type = env.getExpressionTypes().get(exprCtx);

            if (type == MclType.UNKNOWN) {
                env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
                return;
            }

            if (expectingScalars) {
                if (type != MclType.INT && type != MclType.FLOAT) {
                    env.addError(exprCtx.getStart(), "Vector literal must contain only scalars (INT/FLOAT), but found " + type);
                    env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
                    return;
                }
            } else {
                if (type != MclType.VECTOR) {
                    env.addError(exprCtx.getStart(), "Matrix literal must contain only vectors, but found " + type);
                    env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
                    return;
                }
            }
        }

        if (expectingScalars) {
            env.getExpressionTypes().put(ctx, MclType.VECTOR);
        } else {
            env.getExpressionTypes().put(ctx, MclType.MATRIX);
        }
    }

    public void exitMatrixLiteralExpr(MCLParser.MatrixLiteralExprContext ctx) {
        env.getExpressionTypes().put(ctx, MclType.MATRIX);
    }

    public void exitCreatorExpr(MCLParser.CreatorExprContext ctx) {
        MCLParser.CreatorContext creatorCtx = ctx.creator();

        int bracketsCount = creatorCtx.LBRACK().size();

        //check collection type by its creator([] - vector, [][] - matrix)
        MclType structureType = (bracketsCount == 1) ? MclType.VECTOR :
                (bracketsCount == 2) ? MclType.MATRIX : MclType.UNKNOWN;

        env.getExpressionTypes().put(ctx, structureType);

        //check that size of collection is int type
        List<MCLParser.ExpressionContext> exprs = creatorCtx.expression();
        for (int i = 0; i < bracketsCount && i < exprs.size(); i++) {
            MclType type = env.getExpressionTypes().get(exprs.get(i));
            if (type != MclType.INT && type != MclType.UNKNOWN) {
                env.addError(exprs.get(i).getStart(), "Array size must be INT, got " + type);
            }
        }

        if (creatorCtx.expression().size() > bracketsCount) {
            // check for expression initlzr [5](0)
            MCLParser.ExpressionContext initExpr = creatorCtx.expression(bracketsCount); // Последний expr
            MclType initType = env.getExpressionTypes().get(initExpr);
            checkCreatorContentType(initType, creatorCtx.getStart());

        } else if (creatorCtx.lambdaExpression() != null) {
            // Check for lambda initlzr [5](lambda i: i*2)
            MclType lambdaReturnType = env.getExpressionTypes().get(creatorCtx.lambdaExpression());
            checkCreatorContentType(lambdaReturnType, creatorCtx.getStart());
        }
    }

    private void checkCreatorContentType(MclType type, Token token) {
        if (type == MclType.UNKNOWN) return;
        if (type != MclType.INT && type != MclType.FLOAT) {
            env.addError(token, "Creator initializer must return a scalar (INT or FLOAT), but got " + type);
        }
    }

    public void exitNormOrDeterminantExpr(MCLParser.NormOrDeterminantExprContext ctx) {
        MclType innerType = env.getExpressionTypes().get(ctx.expression());

        if (innerType == MclType.UNKNOWN) {
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
            return;
        }

        if (innerType == MclType.INT || innerType == MclType.FLOAT) {
            env.getExpressionTypes().put(ctx, innerType);
        } else if (innerType == MclType.VECTOR || innerType == MclType.MATRIX) {
            env.getExpressionTypes().put(ctx, MclType.FLOAT);
        } else {
            env.addError(ctx.getStart(), "Operator '|...|' is not defined for type " + innerType);
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
        }
    }

    public void exitTypeCast(MCLParser.TypeCastContext ctx) {
        MclType targetType = env.resolveType(ctx.type());
        MclType originalType = env.getExpressionTypes().get(ctx.primary());

        if (originalType == null || originalType == MclType.UNKNOWN) {
            env.getExpressionTypes().put(ctx, targetType);
            return;
        }

        boolean isTargetScalar = (targetType == MclType.INT || targetType == MclType.FLOAT);
        boolean isOriginalScalar = (originalType == MclType.INT || originalType == MclType.FLOAT);

        if (isTargetScalar && isOriginalScalar) {
            env.getExpressionTypes().put(ctx, targetType);
        } else {
            env.addError(ctx.getStart(), "Type casting is only supported between scalar types (INT, FLOAT), " +
                    "but got cast from " + originalType + " to " + targetType);
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
        }
    }

    public void exitAssignableIdentifier(MCLParser.AssignableIdentifierContext ctx) {
        String varName = ctx.IDENTIFIER().getText();
        List<Symbol> symbols = env.getScopeManager().lookup(varName);

        if (symbols == null || symbols.isEmpty()) {

            if (ctx.getParent() instanceof MCLParser.AssignmentContext) {
                env.getAssignableTypes().put(ctx, MclType.UNKNOWN);
                return;
            }

            env.addError(ctx.getStart(), "Undeclared variable: '" + varName + "'");
            env.getAssignableTypes().put(ctx, MclType.UNKNOWN);
            return;
        }

        Symbol symbol = symbols.get(0);

        if (symbol instanceof FunctionSymbol) {
            env.addError(ctx.getStart(), "Cannot use function '" + varName + "' as a variable.");
            env.getAssignableTypes().put(ctx, MclType.UNKNOWN);
        } else {
            env.getAssignableTypes().put(ctx, symbol.getType());
        }
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
            case DIMENSIONS:
                finalType = MclType.INT;
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
                if (fs.parameters().size() != providedArgCount) {
                    continue;
                }

                if (areArgumentsCompatible(fs.parameters(), providedArgNodes)) {
                    matchingOverload = fs;
                    break;
                }
            }
        }

        if (matchingOverload == null) {
            for (Symbol s : candidates) {
                if (s instanceof FunctionSymbol fs && fs.parameters().size() == providedArgCount) {
                    matchingOverload = fs;
                    break;
                }
            }
        }

        if (matchingOverload == null) {
            env.addError(funcToken, "No overload for function '" + funcName +
                    "' takes " + providedArgCount + " arguments with provided types.");
            expressionTypes.put(ctx, MclType.UNKNOWN);
            return;
        }

        expressionTypes.put(ctx, matchingOverload.getType());

        checkArgumentsAndReportErrors(matchingOverload, providedArgNodes, funcName);
    }

    private boolean areArgumentsCompatible(List<VariableSymbol> expectedParams,
                                           List<MCLParser.ExpressionContext> providedArgs) {
        for (int i = 0; i < expectedParams.size(); i++) {
            MclType expected = expectedParams.get(i).getType();
            MclType provided = env.getExpressionTypes().get(providedArgs.get(i));

            if (provided == null) provided = MclType.UNKNOWN;

            if (expected == MclType.UNKNOWN || provided == MclType.UNKNOWN) continue;

            if (expected == provided) continue;

            if (expected == MclType.FLOAT && provided == MclType.INT) continue;
            return false;
        }
        return true;
    }

    private void checkArgumentsAndReportErrors(FunctionSymbol function,
                                               List<MCLParser.ExpressionContext> providedArgs,
                                               String funcName) {
        List<VariableSymbol> expectedParams = function.parameters();
        for (int i = 0; i < expectedParams.size(); i++) {
            MclType expectedType = expectedParams.get(i).getType();
            MCLParser.ExpressionContext argNode = providedArgs.get(i);
            MclType providedType = env.getExpressionTypes().get(argNode);

            if (expectedType == MclType.UNKNOWN || providedType == MclType.UNKNOWN) continue;
            if (expectedType == MclType.FLOAT && providedType == MclType.INT) continue;

            if (expectedType != providedType) {
                env.addError(argNode.getStart(), "Argument " + (i + 1) + " of '" + funcName +
                        "': expected type " + expectedType + ", but got " + providedType);
            }
        }
    }


    public void exitFunctionCallExpr(MCLParser.FunctionCallExprContext ctx) {
        MclType type = env.getExpressionTypes().get(ctx.functionCall());
        env.getExpressionTypes().put(ctx, type != null ? type : MclType.UNKNOWN);
    }
}

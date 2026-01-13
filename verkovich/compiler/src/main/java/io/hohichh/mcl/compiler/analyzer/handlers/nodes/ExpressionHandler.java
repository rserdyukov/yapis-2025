package io.hohichh.mcl.compiler.analyzer.handlers.nodes;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.MclType;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.Token;

import java.util.List;

public class ExpressionHandler {
    private final AnalysisContext env;

    public ExpressionHandler(AnalysisContext context) {
        env = context;
    }

//----------------UNARY_OPS----------------------------------------


    public void exitUnaryMinusPlus(MCLParser.UnaryMinusPlusContext ctx) {
        MclType type = env.getExpressionTypes().get(ctx.unaryExpression());

        if (type == MclType.UNKNOWN) {
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
            return;
        }

        var opNode = (org.antlr.v4.runtime.tree.TerminalNode) ctx.getChild(0);
        String opText = opNode.getText();

        if (type == MclType.INT || type == MclType.FLOAT ||
                type == MclType.VECTOR || type == MclType.MATRIX) {
            env.getExpressionTypes().put(ctx, type);
        } else {
            env.addError(opNode.getSymbol(), "Unary operator '" + opText + "' cannot be applied to type " + type);
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
        }
    }

    public void exitUnaryNot(MCLParser.UnaryNotContext ctx) {
        MclType type = env.getExpressionTypes().get(ctx.unaryExpression());

        if (type == MclType.BOOLEAN) {
            env.getExpressionTypes().put(ctx, MclType.BOOLEAN);
        } else if (type != MclType.UNKNOWN) {
            env.addError(ctx.getStart(), "Logical 'not' expects BOOLEAN, but got " + type);
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
        } else {
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
        }
    }

    public void exitPowerExpr(MCLParser.PowerExprContext ctx) {
        MclType type = env.getExpressionTypes().get(ctx.powerExpression());
        env.getExpressionTypes().put(ctx, type != null ? type : MclType.UNKNOWN);
    }

    public void exitPowerExpression(MCLParser.PowerExpressionContext ctx) {
        MclType baseType = env.getExpressionTypes().get(ctx.primary());

        if (ctx.unaryExpression() == null) {
            env.getExpressionTypes().put(ctx, baseType != null ? baseType : MclType.UNKNOWN);
            return;
        }

        MclType expType = env.getExpressionTypes().get(ctx.unaryExpression());

        if (baseType == MclType.UNKNOWN || expType == MclType.UNKNOWN) {
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
            return;
        }

        if ((baseType == MclType.INT || baseType == MclType.FLOAT) &&
                (expType == MclType.INT || expType == MclType.FLOAT)) {

            env.getExpressionTypes().put(ctx, MclType.FLOAT);

        } else {
            env.addError(ctx.POW().getSymbol(),
                    "Operator '^' is not defined for types " + baseType + " and " + expType);
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
        }
    }

    //-----------------BINARY_ARITHMETICAL_OPS

    public void exitMultiplicativeExpression(MCLParser.MultiplicativeExpressionContext ctx) {
        processBinaryChain(ctx, ctx.unaryExpression());
    }

    public void exitAdditiveExpression(MCLParser.AdditiveExpressionContext ctx) {
        processBinaryChain(ctx, ctx.multiplicativeExpression());
    }


    private void processBinaryChain(ParserRuleContext ctx,
                                    List<? extends ParserRuleContext> operands) {
        if (operands.isEmpty()) return;

        MclType resultType = env.getExpressionTypes().get(operands.get(0));
        if (resultType == null) resultType = MclType.UNKNOWN;

        for (int i = 1; i < operands.size(); i++) {
            MclType nextType = env.getExpressionTypes().get(operands.get(i));

            org.antlr.v4.runtime.tree.TerminalNode opNode =
                    (org.antlr.v4.runtime.tree.TerminalNode) ctx.getChild(2 * i - 1);

            Token opToken = opNode.getSymbol();

            if (resultType == MclType.UNKNOWN || nextType == MclType.UNKNOWN) {
                resultType = MclType.UNKNOWN;
                continue;
            }

            resultType = calculateBinaryType(resultType, nextType, opToken);
        }

        env.getExpressionTypes().put(ctx, resultType);
    }

    private MclType calculateBinaryType(MclType left, MclType right, Token opToken) {
        String op = opToken.getText();

        if (left == MclType.STRING && right == MclType.STRING) {
            if (op.equals("+")) {
                return MclType.STRING;
            } else {
                env.addError(opToken, "Operator '" + op + "' is not defined for Strings.");
                return MclType.UNKNOWN;
            }
        }

        if (left == MclType.INT && right == MclType.INT) return MclType.INT;
        if ((left == MclType.INT || left == MclType.FLOAT) && (right == MclType.INT || right == MclType.FLOAT)) {
            return MclType.FLOAT;
        }

        if (left == MclType.VECTOR && right == MclType.VECTOR) return MclType.VECTOR;
        // Matrix + Matrix
        if (left == MclType.MATRIX && right == MclType.MATRIX) return MclType.MATRIX;


        boolean leftScalar = (left == MclType.INT || left == MclType.FLOAT);
        boolean rightScalar = (right == MclType.INT || right == MclType.FLOAT);

        if (leftScalar && right == MclType.VECTOR) return MclType.VECTOR;
        if (left == MclType.VECTOR && rightScalar) return MclType.VECTOR;

        if (leftScalar && right == MclType.MATRIX) return MclType.MATRIX;
        if (left == MclType.MATRIX && rightScalar) return MclType.MATRIX;


        if (left == MclType.MATRIX && right == MclType.VECTOR) return MclType.VECTOR;

        env.addError(opToken, "Operation " + op + "does not supported between types " + left + " and " + right);
        return MclType.UNKNOWN;
    }

//-------------------------RELATIONAL_OPS

    public void exitRelationalExpression(MCLParser.RelationalExpressionContext ctx) {
        checkBooleanLogic(ctx, ctx.additiveExpression(), false);
    }

    public void exitEqualityExpression(MCLParser.EqualityExpressionContext ctx) {
        checkBooleanLogic(ctx, ctx.relationalExpression(), true);
    }

    private void checkBooleanLogic(ParserRuleContext ctx, List<? extends ParserRuleContext> operands, boolean allowAnyType) {
        if (operands.size() == 1) {
            MclType type = env.getExpressionTypes().get(operands.get(0));
            env.getExpressionTypes().put(ctx, type != null ? type : MclType.UNKNOWN);
            return;
        }

        MclType firstType = env.getExpressionTypes().get(operands.get(0));

        for (int i = 1; i < operands.size(); i++) {
            MclType nextType = env.getExpressionTypes().get(operands.get(i));

            if (firstType == MclType.UNKNOWN || nextType == MclType.UNKNOWN) {
                env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
                return;
            }

            if (!allowAnyType) {
                if ((firstType != MclType.INT && firstType != MclType.FLOAT) ||
                        (nextType != MclType.INT && nextType != MclType.FLOAT)) {
                    env.addError(operands.get(i).getStart(), "Relational operators require numeric types.");
                }
            } else {
                if (firstType != nextType) {
                    if (!((firstType == MclType.INT || firstType == MclType.FLOAT) &&
                            (nextType == MclType.INT || nextType == MclType.FLOAT))) {
                        env.addError(operands.get(i).getStart(), "Cannot compare " + firstType + " with " + nextType);
                    }
                }
            }
        }

        env.getExpressionTypes().put(ctx, MclType.BOOLEAN);
    }

    //-------------------------LOGICAL_OP-----------------------------

    public void exitLogicalAndExpression(MCLParser.LogicalAndExpressionContext ctx) {
        checkLogicalOp(ctx, ctx.equalityExpression());
    }

    public void exitLogicalOrExpression(MCLParser.LogicalOrExpressionContext ctx) {
        checkLogicalOp(ctx, ctx.logicalAndExpression());
    }

    private void checkLogicalOp(ParserRuleContext ctx, List<? extends ParserRuleContext> operands) {
        if (operands.size() == 1) {
            MclType type = env.getExpressionTypes().get(operands.get(0));
            env.getExpressionTypes().put(ctx, type != null ? type : MclType.UNKNOWN);
            return;
        }

        for (ParserRuleContext operand : operands) {
            MclType type = env.getExpressionTypes().get(operand);
            if (type != MclType.BOOLEAN && type != MclType.UNKNOWN) {
                env.addError(operand.getStart(), "Logical operators expect BOOLEAN, but got " + type);
            }
        }
        env.getExpressionTypes().put(ctx, MclType.BOOLEAN);
    }

    public void exitLogicalOrExpr(MCLParser.LogicalOrExprContext ctx) {
        MclType type = env.getExpressionTypes().get(ctx.logicalOrExpression());
        env.getExpressionTypes().put(ctx, type != null ? type : MclType.UNKNOWN);
    }

//-------------------------TERNARY_OP-----------------------------

    public void exitTernaryExpression(MCLParser.TernaryExpressionContext ctx) {
        // expression IF expression ELSE expression
        List<MCLParser.ExpressionContext> exprs = ctx.expression();
        MCLParser.ExpressionContext trueVal = exprs.get(0);
        MCLParser.ExpressionContext condition = exprs.get(1);
        MCLParser.ExpressionContext falseVal = exprs.get(2);

        MclType condType = env.getExpressionTypes().get(condition);
        if (condType != MclType.BOOLEAN && condType != MclType.UNKNOWN) {
            env.addError(condition.getStart(), "Ternary condition must be BOOLEAN, but got " + condType);
        }

        MclType trueType = env.getExpressionTypes().get(trueVal);
        MclType falseType = env.getExpressionTypes().get(falseVal);

        if (trueType == MclType.UNKNOWN || falseType == MclType.UNKNOWN) {
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
            return;
        }

        if (trueType == falseType) {
            env.getExpressionTypes().put(ctx, trueType);
        } else if ((trueType == MclType.INT || trueType == MclType.FLOAT) &&
                (falseType == MclType.INT || falseType == MclType.FLOAT)) {
            env.getExpressionTypes().put(ctx, MclType.FLOAT);
        } else {
            env.addError(ctx.getStart(), "Ternary branches must have compatible types. Got " + trueType + " and " + falseType);
            env.getExpressionTypes().put(ctx, MclType.UNKNOWN);
        }
    }
}
package dev.dezzzl;

import dev.dezzzl.semantics.Context;
import dev.dezzzl.semantics.exception.SemanticException;
import dev.dezzzl.semantics.function.FunctionSignature;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.tree.TerminalNode;

import java.util.ArrayList;
import java.util.List;

public class DefaultGslVisitor extends GslBaseVisitor<String>{

    private final Context context = new Context();

    @Override
    public String visitProgram(GslParser.ProgramContext ctx) {
        context.addBuiltInFunctions();
        boolean mainFound = false;
        for (GslParser.FunctionContext fnCtx : ctx.function()) {
            String returnType = fnCtx.head().type().getText();
            String name = fnCtx.head().ID().getText();
            if ("main".equals(name) && "void".equals(returnType)) {
                mainFound = true;
                for (GslParser.OpGlobalContext globalCtx : findGlobalOps(fnCtx.body())) {
                    visitOpGlobal(globalCtx);
                }
                break;
            }
        }
        if (!mainFound) {
            addException(ctx, "no function named 'void main()' found");
        }
        collectFunctionSignatures(ctx);
        for (GslParser.FunctionContext fnCtx : ctx.function()) {
            visitFunction(fnCtx);
        }
        return null;
    }

    private List<GslParser.OpGlobalContext> findGlobalOps(GslParser.BodyContext body) {
        List<GslParser.OpGlobalContext> result = new ArrayList<>();
        for (GslParser.OpContext op : body.op()) {
            if (op.opGlobal() != null) {
                result.add(op.opGlobal());
            }
        }
        return result;
    }


    private void collectFunctionSignatures(GslParser.ProgramContext ctx) {
        for (GslParser.FunctionContext fnCtx : ctx.function()) {
            FunctionSignature signature = formFunctionSignature(fnCtx);
            try {
                context.addFunction(signature);
            } catch (RuntimeException e) {
                addException(fnCtx, e.getMessage());
            }
        }
    }

    private FunctionSignature formFunctionSignature(GslParser.FunctionContext ctx) {
        String returnType = ctx.head().type().getText();
        String name = ctx.head().ID().getText();
        List<String> paramTypes = new ArrayList<>();
        if (ctx.head().parameterList() != null) {
            for (GslParser.ParameterContext paramCtx : ctx.head().parameterList().parameter()) {
                paramTypes.add(paramCtx.type().getText());
            }
        }

        return new FunctionSignature(name, returnType, paramTypes);
    }

    @Override
    public String visitFunction(GslParser.FunctionContext ctx) {
        FunctionSignature signature = formFunctionSignature(ctx);
        context.enterFunction(signature);
        if (ctx.head().parameterList() != null) {
            for (GslParser.ParameterContext paramCtx : ctx.head().parameterList().parameter()) {
                String paramName = paramCtx.ID().getText();
                String paramType = paramCtx.type().getText();
                context.declareVar(paramName, paramType.toLowerCase());
            }
        }
        visitBody(ctx.body());
        context.exitFunction();
        return null;
    }

    @Override
    public String visitOpIf(GslParser.OpIfContext ctx) {
        Type conditionType = asType(visit(ctx.expr()));
        if (conditionType != Type.BOOLEAN) {
            addException(ctx, String.format(
                    "the condition in the if statement must be of type boolean, found: %s",
                    conditionType.getValue()
            ));
        }
        context.pushBlock();
        visit(ctx.body(0));
        context.popBlock();
        if (ctx.body().size() > 1) {
            context.pushBlock();
            visit(ctx.body(1));
            context.popBlock();
        } else if (ctx.opIf() != null) {
            visit(ctx.opIf());
        }
        return null;
    }

    @Override
    public String visitOpWhile(GslParser.OpWhileContext ctx) {
        Type conditionType = asType(visit(ctx.expr()));
        if (conditionType != Type.BOOLEAN) {
            addException(ctx, String.format(
                    "the condition in the while statement must be of type boolean, found: %s",
                    conditionType.getValue()
            ));
        }
        context.pushBlock();
        visit(ctx.body());
        context.popBlock();
        return null;
    }

    @Override
    public String visitOpUntil(GslParser.OpUntilContext ctx) {
        Type conditionType = asType(visit(ctx.expr()));
        if (conditionType != Type.BOOLEAN) {
            addException(ctx, String.format(
                    "the condition in the until statement must be of type boolean, found: %s",
                    conditionType.getValue()
            ));
        }
        context.pushBlock();
        visit(ctx.body());
        context.popBlock();
        return null;
    }

    @Override
    public String visitOpGlobal(GslParser.OpGlobalContext ctx) {
        FunctionSignature current = context.getCurrentFunction();
        if (current!=null && current.name.equals("main") && current.returnType.equals(Type.VOID.getValue())) {
            return null;
        }
        if (current != null && (!current.name.equals("main") || !current.returnType.equals(Type.VOID.getValue()))) {
            addException(ctx, "global variables can only be declared in the 'void main()' function");
            return null;
        }
        List<TerminalNode> ids = ctx.ID();
        List<GslParser.TypeContext> types = ctx.type();
        for (int i = 0; i < ids.size(); i++) {
            String varName = ids.get(i).getText();
            Type type = Type.valueOf(types.get(Math.min(i, types.size() - 1)).getText().toUpperCase());
            if (context.getVarType(varName) != null) {
                addException(ctx, "global variable '" + varName + "' has already been declared");
                continue;
            }
            context.declareGlobalVar(varName, type.getValue());
            if (ctx.expr(i) != null) {
                Type rhsType = asType(visit(ctx.expr(i)));
                if (!rhsType.canCastTo(type)) {
                    addException(ctx, "it is impossible to assign a value of the type '" + rhsType.getValue() + "' to a value with type '" + type.getValue() + "'");
                }
            }
        }
        return null;
    }

    @Override
    public String visitOpDeclare(GslParser.OpDeclareContext ctx) {
        List<TerminalNode> ids = ctx.leftAssign().ID();
        List<GslParser.TypeContext> types = ctx.leftAssign().type();
        if (types.isEmpty()) {
            addException(ctx, "each variable declaration must contain a type");
            return null;
        }
        String typeName = types.get(0).getText();
        for (TerminalNode idCtx : ids) {
            String varName = idCtx.getText();
            try {
                context.declareVar(varName, typeName.toLowerCase());
            } catch (RuntimeException e) {
                addException(ctx, e.getMessage());
            }
        }
        return null;
    }

    @Override
    public String visitOpFor(GslParser.OpForContext ctx) {
        context.pushBlock();
        if (ctx.opAssign(0) != null) {
            visit(ctx.opAssign(0));
        }
        if (ctx.expr() != null) {
            Type conditionType = asType(visit(ctx.expr()));
            if (conditionType != Type.BOOLEAN) {
                addException(ctx, String.format(
                        "the for loop condition must be of type boolean, found: %s",
                        conditionType.getValue()
                ));
            }
        }
        if (ctx.opAssign(1) != null) {
            visit(ctx.opAssign(1));
        } else if (ctx.opExpr() != null) {
            visit(ctx.opExpr());
        }
        visit(ctx.body());
        context.popBlock();
        return null;
    }

    @Override
    public String visitOpReturn(GslParser.OpReturnContext ctx) {
        Type expectedType = asType(context.getCurrentFunction().returnType);
        if (ctx.expr() == null) {
            if (expectedType != Type.VOID) {
                addException(ctx, String.format(
                        "the function should return a value of type '%s', but the return statement does not contain an expression",
                        expectedType.getValue()
                ));
            }
            return Type.VOID.getValue();
        }
        Type actualType = asType(visit(ctx.expr()));
        if (!actualType.equals(expectedType)) {
            addException(ctx, String.format(
                    "return type mismatch: expected '%s', received '%s''",
                    expectedType.getValue(), actualType.getValue()
            ));
        }
        return expectedType.getValue();
    }

    @Override
    public String visitOpAssign(GslParser.OpAssignContext ctx) {
        List<TerminalNode> ids = ctx.leftAssign().ID();
        List<GslParser.TypeContext> types = ctx.leftAssign().type();
        List<GslParser.ExprContext> exprs = ctx.exprList().expr();
        List<Type> rhsTypes = resolveRightExprTypes(ctx, exprs);
        if (!checkCountMatch(ctx, ids.size(), rhsTypes.size())) {
            return null;
        }
        boolean hasExplicitType = !types.isEmpty();
        Type declaredType = hasExplicitType ? resolveDeclaredType(types.get(0)) : null;
        for (int i = 0; i < ids.size(); i++) {
            String varName = ids.get(i).getText();
            Type rhsType = rhsTypes.get(i);

            if (hasExplicitType) {
                handleTypedAssignment(ctx, varName, declaredType, rhsType);
            } else {
                handleUntypedAssignment(ctx, varName, rhsType);
            }
        }
        return null;
    }

    private List<Type> resolveRightExprTypes(GslParser.OpAssignContext ctx, List<GslParser.ExprContext> exprs) {
        List<Type> rhsTypes = new ArrayList<>();
        for (GslParser.ExprContext exprCtx : exprs) {
            String rhsTypeName = visit(exprCtx);
            try {
                rhsTypes.add(Type.valueOf(rhsTypeName.toUpperCase()));
            } catch (Exception e) {
                addException(ctx, "unknown type of expression on the right: " + rhsTypeName.toLowerCase());
                rhsTypes.add(Type.VOID);
            }
        }
        return rhsTypes;
    }

    private boolean checkCountMatch(GslParser.OpAssignContext ctx, int lhsCount, int rhsCount) {
        if (lhsCount != rhsCount) {
            addException(ctx, String.format(
                    "the number of variables (%d) and expressions on the right (%d) does not match",
                    lhsCount, rhsCount
            ));
            return false;
        }
        return true;
    }

    private Type resolveDeclaredType(GslParser.TypeContext typeCtx) {
        return asType(typeCtx.getText());
    }

    private void handleTypedAssignment(GslParser.OpAssignContext ctx, String varName, Type declaredType, Type rhsType) {
        if (context.getVarType(varName) != null) {
            addException(ctx, "variable '" + varName + "' has already been declared");
            return;
        }
        if (rhsType != declaredType) {
            addException(ctx, String.format(
                    "the type of the expression on the right (%s) does not match the type of the declared variable (%s) — %s = ...",
                    rhsType.getValue(), declaredType.getValue(), varName
            ));
        }
        context.declareVar(varName, declaredType.getValue());
    }

    private void handleUntypedAssignment(GslParser.OpAssignContext ctx, String varName, Type rhsType) {
            String existingTypeName = context.getVarType(varName);
            if (existingTypeName == null) {
                addException(ctx, "variable '" + varName + "' not declared");
                return;
            }
            Type existingType = asType(existingTypeName);
            if (rhsType != existingType) {
                addException(ctx, String.format(
                        "incompatible types in assignment: '%s' has type %s, but the expression on the right has type %s",
                        varName, existingType.getValue(), rhsType.getValue()
                ));
            }
    }

    @Override
    public String visitParensExpr(GslParser.ParensExprContext ctx) {
        return visit(ctx.expr());
    }

    @Override
    public String visitCastExpr(GslParser.CastExprContext ctx) {
        Type targetType = Type.valueOf(ctx.type().getText().toUpperCase());
        String exprTypeStr = visit(ctx.expr());
        Type exprType;
        exprType = asType(exprTypeStr.toUpperCase());
        if (!exprType.canCastTo(targetType)) {
            addException(ctx, "impossible type conversion: " + exprType.getValue() + " -> " + targetType.getValue());
        }
        return targetType.name().toLowerCase();
    }

    @Override
    public String visitIdPrimary(GslParser.IdPrimaryContext ctx) {
        String varName = ctx.ID().getText();
        String varType = context.getVarType(varName);
        if (varType == null) {
            addException(ctx, "variable'" + varName + "' is not declared");
            return Type.VOID.getValue();
        }
        return varType;
    }

    @Override
    public String visitLiteralPrimary(GslParser.LiteralPrimaryContext ctx) {
        if (ctx.literal().INT() != null) return Type.INT.getValue();
        if (ctx.literal().STRING() != null) return Type.STRING.getValue();
        if (ctx.literal().BOOLEAN() != null) return Type.BOOLEAN.getValue();
        return Type.VOID.getValue();
    }

    @Override
    public String visitNodePrimary(GslParser.NodePrimaryContext ctx) {
        String innerType = visit(ctx.nodeLiteral().expr());
        Type exprType = asType(innerType);
        if (exprType != Type.STRING) {
            addException(ctx, String.format(
                    "invalid argument type '%s' in node(...). Expected string.",
                    exprType.getValue()
            ));
        }
        return Type.NODE.getValue();
    }

    @Override
    public String visitArcPrimary(GslParser.ArcPrimaryContext ctx) {
        List<GslParser.ExprContext> args = ctx.arcLiteral().expr();
        Type fromType  = asType(visit(args.get(0)));
        Type toType  = asType(visit(args.get(1)));
        if (fromType != Type.NODE || toType != Type.NODE) {
            addException(ctx, String.format(
                    "both arguments of arc(...) must be node, received (%s, %s)",
                    fromType.getValue(), toType.getValue()
            ));
        }
        return Type.ARC.getValue();
    }

    @Override
    public String visitGraphPrimary(GslParser.GraphPrimaryContext ctx) {
        GslParser.GraphLiteralContext literal = ctx.graphLiteral();
        GslParser.NodeListContext nodeList = literal.nodeList();
        GslParser.ArcListContext arcList = literal.arcList();
        if (nodeList != null) {
            for (GslParser.ExprContext nodeExpr : nodeList.expr()) {
                Type nodeType = asType(visit(nodeExpr));
                if (nodeType != Type.NODE) {
                    addException(ctx, String.format(
                            "all elements of the node list in graph(...) must be of type node, but %s was received",
                            nodeType.getValue()
                    ));
                }
            }
        }
        if (arcList != null) {
            for (GslParser.ExprContext arcExpr : arcList.expr()) {
                Type arcType = asType(visit(arcExpr));
                if (arcType != Type.ARC) {
                    addException(ctx, String.format(
                            "all elements of the arc list in graph(...) must be of type arc, but %s was received",
                            arcType.getValue()
                    ));
                }
            }
        }
        return Type.GRAPH.getValue();
    }

    @Override
    public String visitOpMethodCall(GslParser.OpMethodCallContext ctx) {
        return handleFunctionCall(ctx);
    }

    @Override
    public String visitMethodCallPrimary(GslParser.MethodCallPrimaryContext ctx) {
        return handleFunctionCall(ctx.opMethodCall());
    }


    private String handleFunctionCall(GslParser.OpMethodCallContext ctx) {
        String functionName = ctx.ID().getText();
        List<String> argTypes = new ArrayList<>();
        if (ctx.argList() != null) {
            for (var exprCtx : ctx.argList().expr()) {
                argTypes.add(visit(exprCtx));
            }
        }
        FunctionSignature function = context.getFunction(functionName, argTypes);
        if (function == null) {
            addException(ctx, String.format(
                    "could not find a suitable overload of the '%s' function with arguments %s",
                    functionName, argTypes
            ));
            return Type.VOID.getValue();
        }
        return function.returnType;
    }


    @Override
    public String visitAddExpr(GslParser.AddExprContext ctx) {
        return checkBinaryArithmetic(ctx, "+");
    }

    @Override
    public String visitSubExpr(GslParser.SubExprContext ctx) {
        return checkBinaryArithmetic(ctx, "-");
    }

    @Override
    public String visitMulExpr(GslParser.MulExprContext ctx) {
        return checkBinaryArithmetic(ctx, "*");
    }

    @Override
    public String visitDivExpr(GslParser.DivExprContext ctx) {
        return checkBinaryArithmetic(ctx, "/");
    }

    @Override
    public String visitOrExpr(GslParser.OrExprContext ctx) {
        return checkBinaryBoolean(ctx, "||");
    }

    @Override
    public String visitAndExpr(GslParser.AndExprContext ctx) {
        return checkBinaryBoolean(ctx, "&&");
    }

    @Override
    public String visitEqExpr(GslParser.EqExprContext ctx) {
        return checkBinaryEquality(ctx, "==");
    }

    @Override
    public String visitNeqExpr(GslParser.NeqExprContext ctx) {
        return checkBinaryEquality(ctx, "!=");
    }

    @Override
    public String visitLtExpr(GslParser.LtExprContext ctx) {
        return checkBinaryInt(ctx, "<");
    }

    @Override
    public String visitLeExpr(GslParser.LeExprContext ctx) {
        return checkBinaryInt(ctx, "<=");
    }

    @Override
    public String visitGtExpr(GslParser.GtExprContext ctx) {
        return checkBinaryInt(ctx, ">");
    }

    @Override
    public String visitGeExpr(GslParser.GeExprContext ctx) {
        return checkBinaryInt(ctx, ">=");
    }

    @Override
    public String visitPrefixOpExpr(GslParser.PrefixOpExprContext ctx) {
        Type exprType = asType(visit(ctx.prefixExpr().expr()));
        String op = ctx.prefixExpr().getChild(0).getText();

        if (op.equals("++") || op.equals("--")) {
            if (exprType != Type.INT) {
                addException(ctx, "operators '" + op + "' are only allowed for int, found: " + exprType.getValue());
            }
            return Type.INT.getValue();
        } else if (op.equals("!")) {
            if (exprType != Type.BOOLEAN) {
                addException(ctx, "operator '!' is only allowed for boolean, found: " + exprType.getValue());
            }
            return Type.BOOLEAN.getValue();
        }
        return exprType.getValue();
    }

    @Override
    public String visitPostfixOpExpr(GslParser.PostfixOpExprContext ctx) {
        Type exprType = asType(visit(ctx.postfixExpr().getChild(0)));
        String op = ctx.postfixExpr().getChild(1).getText();
        if (exprType != Type.INT) {
            addException(ctx, "the postfix operator '" + op + "'  is only allowed for int, found: " + exprType.getValue());
        }
        return Type.INT.getValue();
    }

    private String checkBinaryArithmetic(GslParser.ExprContext ctx, String operator) {
        String leftTypeName = visit(ctx.getChild(0));
        String rightTypeName = visit(ctx.getChild(2));

        Type left = asType(leftTypeName.toUpperCase());
        Type right = asType(rightTypeName.toUpperCase());

        if (left == right && isArithmeticType(left)) {
            return left.getValue();
        }

        addException(ctx, String.format(
                "cannot apply '%s' to '%s' and '%s' types",
                operator, left.getValue(), right.getValue()
        ));

        return left.getValue();
    }

    private boolean isArithmeticType(Type type) {
        return switch (type) {
            case INT, NODE, ARC, GRAPH, STRING -> true;
            default -> false;
        };
    }


    private String checkBinaryBoolean(GslParser.ExprContext ctx, String operator) {
        Type leftType = asType(visit(ctx.getChild(0)));
        Type rightType = asType(visit(ctx.getChild(2)));
        boolean isBoolean = leftType == Type.BOOLEAN && rightType == Type.BOOLEAN;
        boolean isInt = leftType == Type.INT && rightType == Type.INT;
        if (!isBoolean && !isInt) {
            addException(ctx, String.format(
                    "the '%s' operator is only allowed for boolean or int, but '%s' and '%s' were received",
                    operator, leftType.getValue(), rightType.getValue()
            ));
        }
        return Type.BOOLEAN.getValue();
    }


    private String checkBinaryInt(GslParser.ExprContext ctx, String operator) {
        Type leftType = asType(visit(ctx.getChild(0)));
        Type rightType = asType(visit(ctx.getChild(2)));

        if (leftType != Type.INT || rightType != Type.INT) {
            addException(ctx,
                    String.format("the '%s' operator is only allowed for int, but '%s' and '%s' were received",
                            operator, leftType.getValue(), rightType.getValue()));
        }
        return Type.BOOLEAN.getValue();
    }

    private String checkBinaryEquality(GslParser.ExprContext ctx, String operator) {
        Type leftType = asType(visit(ctx.getChild(0)));
        Type rightType = asType(visit(ctx.getChild(2)));
        if (!leftType.equals(rightType)) {
            addException(ctx, String.format(
                    "the '%s' operator is only allowed for identical types, and '%s' and '%s' were received",
                    operator, leftType.getValue(), rightType.getValue()
            ));
        } else {
            if (!(leftType == Type.INT ||
                    leftType == Type.BOOLEAN ||
                    leftType == Type.NODE ||
                    leftType == Type.ARC ||
                    leftType == Type.GRAPH)) {
                addException(ctx, String.format(
                        "the '%s' operator is not supported for the '%s' type",
                        operator, leftType.getValue()
                ));
            }
        }
        return Type.BOOLEAN.getValue();
    }


    private void addException(ParserRuleContext ctx, String message) {
        SemanticException exception = new SemanticException(
                message,
                ctx.start.getLine(),
                ctx.start.getCharPositionInLine()
        );
        context.addError(exception);
    }

    private Type asType(String raw) {
        if (raw == null) return Type.VOID;
        try {
            return Type.valueOf(raw.toUpperCase());
        } catch (IllegalArgumentException e) {
            return Type.VOID;
        }
    }

    public Context getContext() {
        return context;
    }

}
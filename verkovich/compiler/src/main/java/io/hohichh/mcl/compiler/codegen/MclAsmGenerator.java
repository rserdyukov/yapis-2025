package io.hohichh.mcl.compiler.codegen;

import io.hohichh.mcl.compiler.MCLBaseVisitor;
import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.handlers.nodes.AnalysisContext;

import java.util.ArrayList;
import java.util.List;

public class MclAsmGenerator extends MCLBaseVisitor<Void> {
    private final StringBuilder mainBuffer = new StringBuilder();

    private final List<String> functionBlocks = new ArrayList<>();
    private StringBuilder currentBuffer = mainBuffer;

    private boolean inFunction = false;
    private int labelCounter = 0;

    private final AnalysisContext context;

    public MclAsmGenerator(AnalysisContext context) {
        this.context = context;
    }

    //--------------UTILS-----------------------------

    public String getGeneratedCode() {
        StringBuilder finalCode = new StringBuilder();
        finalCode.append(mainBuffer);

        for (String funcBlock : functionBlocks) {
            finalCode.append("\n").append(funcBlock);
        }

        return finalCode.toString();
    }

    private void emit(String opcode) {
        currentBuffer.append(opcode).append("\n");
    }

    private void emit(String opcode, String arg) {
        currentBuffer.append(opcode).append(" ").append(arg).append("\n");
    }

    private void emitLabel(String label) {
        currentBuffer.append(label).append(":\n");
    }

    private String newLabel() {
        return "L" + (labelCounter++);
    }

    private String getLoadOp() {
        return inFunction ? "LOAD_FAST" : "LOAD_NAME";
    }

    private String getStoreOp() {
        return inFunction ? "STORE_FAST" : "STORE_NAME";
    }

    //---------------STATEMENTS------------------------

    @Override
    public Void visitProgram(MCLParser.ProgramContext ctx) {
        visitChildren(ctx);
        emit("LOAD_CONST", "None");
        emit("RETURN_VALUE");
        return null;
    }

    @Override
    public Void visitFunctionDefinition(MCLParser.FunctionDefinitionContext ctx) {
        String funcName = ctx.IDENTIFIER().getText();

        StringBuilder previousBuffer = this.currentBuffer;
        StringBuilder funcBodyBuffer = new StringBuilder();
        this.currentBuffer = funcBodyBuffer;

        boolean wasInFunction = this.inFunction;
        this.inFunction = true;

        currentBuffer.append(".def ").append(funcName);

        List<String> params = new ArrayList<>();
        if (ctx.parameterList() != null) {
            for (var param : ctx.parameterList().parameter()) {
                String paramName = param.IDENTIFIER().getText();
                currentBuffer.append(" ").append(paramName);
                params.add(paramName);
            }
        }
        currentBuffer.append("\n");

        visit(ctx.suite());

        emit("LOAD_CONST", "None");
        emit("RETURN_VALUE");


        currentBuffer.append(".enddef\n");
        functionBlocks.add(funcBodyBuffer.toString());

        this.currentBuffer = previousBuffer;
        this.inFunction = wasInFunction;

        emit("LOAD_CONST", "CODE:" + funcName);
        emit("LOAD_CONST", funcName);
        emit("MAKE_FUNCTION", "0");
        emit("STORE_NAME", funcName);

        return null;
    }

    @Override
    public Void visitStatement(MCLParser.StatementContext ctx) {
        return visitChildren(ctx);
    }

    @Override
    public Void visitAssignment(MCLParser.AssignmentContext ctx) {
        MCLParser.AssignableContext lhs = ctx.assignable();
        MCLParser.ExpressionContext rhs = ctx.expression();

        if (lhs instanceof MCLParser.AssignableIdentifierContext idCtx) {
            visit(rhs);
            String varName = idCtx.IDENTIFIER().getText();
            emit(getStoreOp(), varName);
        }
        else if (lhs instanceof MCLParser.AssignableElementAccessContext accessCtx) {
            visit(rhs);
            visit(accessCtx.assignable());
            visit(accessCtx.expression());
            emit("STORE_SUBSCR");
        }

        return null;
    }

    @Override
    public Void visitAssignableElementAccess(MCLParser.AssignableElementAccessContext ctx) {
        visit(ctx.assignable());
        visit(ctx.expression());
        emit("BINARY_SUBSCR");

        return null;
    }

    @Override
    public Void visitIfStatement(MCLParser.IfStatementContext ctx) {
        String elseLabel = newLabel();
        String endLabel = newLabel();

        visit(ctx.expression());
        emit("POP_JUMP_IF_FALSE", ctx.ELSE() != null ? elseLabel : endLabel);

        visit(ctx.suite(0));

        if (ctx.ELSE() != null) {
            emit("JUMP_FORWARD", endLabel);

            emitLabel(elseLabel);
            visit(ctx.suite(1));
        }
        emitLabel(endLabel);

        return null;
    }

    @Override
    public Void visitAssignableIdentifier(MCLParser.AssignableIdentifierContext ctx) {
        emit(getLoadOp(), ctx.IDENTIFIER().getText());
        return null;
    }

    @Override
    public Void visitWhileStatement(MCLParser.WhileStatementContext ctx) {
        String startLabel = newLabel();
        String endLabel = newLabel();

        emitLabel(startLabel);
        visit(ctx.expression());
        emit("POP_JUMP_IF_FALSE", endLabel);
        visit(ctx.suite());
        emit("JUMP_ABSOLUTE", startLabel);
        emitLabel(endLabel);

        return null;
    }

    @Override
    public Void visitUntilStatement(MCLParser.UntilStatementContext ctx) {
        String startLabel = newLabel();
        String endLabel = newLabel();

        emitLabel(startLabel);

        visit(ctx.expression());
        emit("POP_JUMP_IF_TRUE", endLabel);
        visit(ctx.suite());
        emit("JUMP_ABSOLUTE", startLabel);

        emitLabel(endLabel);

        return null;
    }

    @Override
    public Void visitForStatement(MCLParser.ForStatementContext ctx) {
        String startLabel = newLabel();
        String endLabel = newLabel();
        String loopVar = ctx.IDENTIFIER().getText();

        visit(ctx.expression());
        emit("GET_ITER");
        emitLabel(startLabel);
        emit("FOR_ITER", endLabel);
        emit("STORE_NAME", loopVar);
        visit(ctx.suite());
        emit("JUMP_ABSOLUTE", startLabel);
        emitLabel(endLabel);

        return null;
    }

    @Override
    public Void visitReturnStatement(MCLParser.ReturnStatementContext ctx) {
        if (ctx.expression() != null) {
            visit(ctx.expression());
        } else {
            emit("LOAD_CONST", "None");
        }
        emit("RETURN_VALUE");
        return null;
    }

    @Override
    public Void visitSuite(MCLParser.SuiteContext ctx) {
        visitChildren(ctx);
        return null;
    }

    //--------------EXPRESSIONS---------------------------

    @Override
    public Void visitAdditiveExpression(MCLParser.AdditiveExpressionContext ctx) {

        visit(ctx.multiplicativeExpression(0));

        for (int i = 1; i < ctx.multiplicativeExpression().size(); i++) {
            visit(ctx.multiplicativeExpression(i));

            String op = ctx.getChild(2 * i - 1).getText();
            switch (op) {
                case "+": emit("BINARY_ADD"); break;
                case "-": emit("BINARY_SUBTRACT"); break;
            }
        }
        return null;
    }

    @Override
    public Void visitMultiplicativeExpression(MCLParser.MultiplicativeExpressionContext ctx) {
        visit(ctx.unaryExpression(0));

        for (int i = 1; i < ctx.unaryExpression().size(); i++) {
            visit(ctx.unaryExpression(i));

            String op = ctx.getChild(2 * i - 1).getText();
            switch (op) {
                case "*": emit("BINARY_MULTIPLY"); break;
                case "/": emit("BINARY_TRUE_DIVIDE"); break;
                case "%": emit("BINARY_MODULO"); break;
            }
        }
        return null;
    }

    @Override
    public Void visitTypeCast(MCLParser.TypeCastContext ctx) {
        String pythonType = "int";

        if (ctx.type().scalarType() != null) {
            if (ctx.type().scalarType().FLOAT_TYPE() != null) pythonType = "float";
            else if (ctx.type().scalarType().INT_TYPE() != null) pythonType = "int";
        } else if (ctx.type().STRING_TYPE() != null) {
            pythonType = "str";
        } else if (ctx.type().BOOLEAN_TYPE() != null) {
            pythonType = "bool";
        }

        emit("LOAD_NAME", pythonType);
        visit(ctx.primary());
        emit("CALL_FUNCTION", "1");

        return null;
    }

    @Override
    public Void visitPowerExpression(MCLParser.PowerExpressionContext ctx) {
        visit(ctx.primary());

        if (ctx.unaryExpression() != null) {
            visit(ctx.unaryExpression());
            emit("BINARY_POWER");
        }
        return null;
    }

    @Override
    public Void visitRelationalExpression(MCLParser.RelationalExpressionContext ctx) {
        visit(ctx.additiveExpression(0));

        for (int i = 1; i < ctx.additiveExpression().size(); i++) {
            visit(ctx.additiveExpression(i));
            String op = ctx.getChild(2 * i - 1).getText();
            emit("COMPARE_OP", op);
        }
        return null;
    }

    @Override
    public Void visitEqualityExpression(MCLParser.EqualityExpressionContext ctx) {
        visit(ctx.relationalExpression(0));

        for (int i = 1; i < ctx.relationalExpression().size(); i++) {
            visit(ctx.relationalExpression(i));
            String op = ctx.getChild(2 * i - 1).getText();
            emit("COMPARE_OP", op);
        }
        return null;
    }

    @Override
    public Void visitLogicalOrExpression(MCLParser.LogicalOrExpressionContext ctx) {
        visit(ctx.logicalAndExpression(0));

        for (int i = 1; i < ctx.logicalAndExpression().size(); i++) {
            String endLabel = newLabel();
            visit(ctx.logicalAndExpression(i));
            emitLabel(endLabel);
        }
        return null;
    }

    @Override
    public Void visitLogicalAndExpression(MCLParser.LogicalAndExpressionContext ctx) {
        visit(ctx.equalityExpression(0));

        for (int i = 1; i < ctx.equalityExpression().size(); i++) {
            String endLabel = newLabel();
            emit("JUMP_IF_FALSE_OR_POP", endLabel);
            visit(ctx.equalityExpression(i));
            emitLabel(endLabel);
        }
        return null;
    }

    @Override
    public Void visitUnaryNot(MCLParser.UnaryNotContext ctx) {
        visit(ctx.unaryExpression());
        emit("UNARY_NOT");
        return null;
    }

    @Override
    public Void visitUnaryMinusPlus(MCLParser.UnaryMinusPlusContext ctx) {
        visit(ctx.unaryExpression());

        if (ctx.MINUS() != null) {
            emit("UNARY_NEGATIVE");
        } else {
            emit("UNARY_POSITIVE");
        }
        return null;
    }

    @Override
    public Void visitParenthesizedExpr(MCLParser.ParenthesizedExprContext ctx) {
        visit(ctx.expression());
        return null;
    }

    @Override
    public Void visitTernaryExpression(MCLParser.TernaryExpressionContext ctx) {
        String elseLabel = newLabel();
        String endLabel = newLabel();

        visit(ctx.expression(1));
        emit("POP_JUMP_IF_FALSE", elseLabel);

        visit(ctx.expression(0));
        emit("JUMP_FORWARD", endLabel);

        emitLabel(elseLabel);
        visit(ctx.expression(2));

        emitLabel(endLabel);
        return null;
    }

    @Override
    public Void visitLambdaExpression(MCLParser.LambdaExpressionContext ctx) {
        String lambdaName = "<lambda_" + (labelCounter++) + ">";

        StringBuilder previousBuffer = this.currentBuffer;
        StringBuilder lambdaBodyBuffer = new StringBuilder();
        this.currentBuffer = lambdaBodyBuffer;

        boolean wasInFunction = this.inFunction;
        this.inFunction = true;

        currentBuffer.append(".def ").append(lambdaName);
        if (ctx.IDENTIFIER() != null) {
            for (var param : ctx.IDENTIFIER()) {
                currentBuffer.append(" ").append(param.getText());
            }
        }
        currentBuffer.append("\n");

        visit(ctx.expression());
        emit("RETURN_VALUE");

        currentBuffer.append(".enddef\n");
        functionBlocks.add(lambdaBodyBuffer.toString());

        this.currentBuffer = previousBuffer;
        this.inFunction = wasInFunction;

        emit("LOAD_CONST", "CODE:" + lambdaName);
        emit("LOAD_CONST", lambdaName);
        emit("MAKE_FUNCTION", "0");

        return null;
    }

    //---------------PRIMARIES---------------------------------
    @Override
    public Void visitFunctionCallExpr(MCLParser.FunctionCallExprContext ctx) {
        return visitFunctionCall(ctx.functionCall());
    }

    @Override
    public Void visitFunctionCall(MCLParser.FunctionCallContext ctx) {
        String funcName = ctx.IDENTIFIER().getText();

        if (funcName.equals("write")) funcName = "print";
        if (funcName.equals("read")) funcName = "input";

        emit("LOAD_NAME", funcName);

        int argsCount = 0;
        if (ctx.argumentList() != null) {
            argsCount = ctx.argumentList().expression().size();
            for (var expr : ctx.argumentList().expression()) {
                visit(expr);
            }
        }

        emit("CALL_FUNCTION", String.valueOf(argsCount));
        return null;
    }

    @Override
    public Void visitIdentifierExpr(MCLParser.IdentifierExprContext ctx) {
        emit(getLoadOp(), ctx.IDENTIFIER().getText());
        return null;
    }

    @Override
    public Void visitLiteralExpr(MCLParser.LiteralExprContext ctx) {
        MCLParser.LiteralContext lit = ctx.literal();
        if (lit.INTEGER() != null) emit("LOAD_CONST", lit.getText());
        else if (lit.FLOAT() != null) emit("LOAD_CONST", lit.getText());
        else if (lit.STRING() != null) emit("LOAD_CONST", lit.getText());
        else if (lit.TRUE() != null) emit("LOAD_CONST", "True");
        else if (lit.FALSE() != null) emit("LOAD_CONST", "False");
        return null;
    }

    @Override
    public Void visitVectorLiteralExpr(MCLParser.VectorLiteralExprContext ctx) {
        return visitVectorLiteral(ctx.vectorLiteral());
    }

    @Override
    public Void visitMatrixLiteralExpr(MCLParser.MatrixLiteralExprContext ctx) {
        return visitMatrixLiteral(ctx.matrixLiteral());
    }

    @Override
    public Void visitVectorLiteral(MCLParser.VectorLiteralContext ctx) {
        int count = 0;
        if (ctx.expressionList() != null) {
            count = ctx.expressionList().expression().size();
            for (var expr : ctx.expressionList().expression()) {
                visit(expr);
            }
        }
        emit("BUILD_LIST", String.valueOf(count));
        return null;
    }

    @Override
    public Void visitMatrixLiteral(MCLParser.MatrixLiteralContext ctx) {
        int count = ctx.vectorLiteral().size();
        for (var vec : ctx.vectorLiteral()) {
            visitVectorLiteral(vec);
        }
        emit("BUILD_LIST", String.valueOf(count));
        return null;
    }

    @Override
    public Void visitCreatorExpr(MCLParser.CreatorExprContext ctx) {
        int dimensions = ctx.creator().LBRACK().size();

        MCLParser.ExpressionContext initExpr = null;
        if (ctx.creator().expression().size() > dimensions) {
            initExpr = ctx.creator().expression(dimensions);
        }

        if (dimensions == 1 && initExpr != null) {
            visit(initExpr);
            emit("BUILD_LIST", "1");
            visit(ctx.creator().expression(0));
            emit("BINARY_MULTIPLY");
        }
        else {
            emit("BUILD_LIST", "0");
        }

        return null;
    }

    @Override
    public Void visitNormOrDeterminantExpr(MCLParser.NormOrDeterminantExprContext ctx) {
        emit("LOAD_NAME", "abs");
        visit(ctx.expression());
        emit("CALL_FUNCTION", "1");

        return null;
    }
}
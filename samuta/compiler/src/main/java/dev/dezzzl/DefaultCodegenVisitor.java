package dev.dezzzl;

import dev.dezzzl.codegen.IRGenerator;
import dev.dezzzl.semantics.Context;
import dev.dezzzl.semantics.function.FunctionSignature;
import dev.dezzzl.semantics.function.VariableInfo;
import lombok.Getter;
import org.antlr.v4.runtime.tree.TerminalNode;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DefaultCodegenVisitor extends GslBaseVisitor<NodeValue> {

    @Getter
    private final IRGenerator generator;

    private final Context context;

    public DefaultCodegenVisitor(IRGenerator generator, Context context) {
        this.generator = generator;
        this.context = context;
        generator.initModule();
    }

    @Override
    public NodeValue visitProgram(GslParser.ProgramContext ctx) {
        StringBuilder module = new StringBuilder();
        for (GslParser.FunctionContext fnCtx : ctx.function()) {
            NodeValue fn = visitFunction(fnCtx);
            if (fn != null && fn.code != null) {
                module.append(fn.code);
            }
        }
        generator.addInstruction(module.toString());
        return new NodeValue(module.toString());
    }

    @Override
    public NodeValue visitFunction(GslParser.FunctionContext ctx) {
        FunctionSignature signature = formFunctionSignature(ctx);
        List<String> paramNames = new ArrayList<>();
        if (ctx.head().parameterList() != null) {
            for (GslParser.ParameterContext paramCtx : ctx.head().parameterList().parameter()) {
                String paramName = paramCtx.ID().getText();
                paramNames.add(paramName);
            }
        }
        String startFunction = generator.startFunction(context.getFunctionSignature(signature), paramNames);
        FunctionSignature functionRef = context.getFunctionSignature(signature);
        context.enterFunction(functionRef);
        String entry = visitBody(ctx.body()).code;
        String endFunction = generator.endFunction(context.getFunctionSignature(signature));
        String function = startFunction + entry + endFunction;
        context.exitFunction();
        return new NodeValue(function);
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
    public NodeValue visitBody(GslParser.BodyContext ctx) {
        StringBuilder bodyCode = new StringBuilder();
            for (var stmt : ctx.op()) {
            NodeValue nv = visit(stmt);
            if (nv != null && nv.code != null) {
                bodyCode.append(nv.code);
            }
        }
        return new NodeValue(bodyCode.toString());
    }

    @Override
    public NodeValue visitOp(GslParser.OpContext ctx) {
        if (ctx.opAssign() != null) return visit(ctx.opAssign());
        if (ctx.opReturn() != null) return visit(ctx.opReturn());
        if (ctx.opDeclare() != null) return visit(ctx.opDeclare());
        if (ctx.opGlobal() != null) return visit(ctx.opGlobal());
        if (ctx.opMethodCall() != null) return visit(ctx.opMethodCall());
        if (ctx.opIf() != null) return visit(ctx.opIf());
        if (ctx.opFor() != null) return visit(ctx.opFor());
        if (ctx.opWhile() != null) return visit(ctx.opWhile());
        if (ctx.opUntil() != null) return visit(ctx.opUntil());
        if (ctx.opExpr() != null) return visit(ctx.opExpr());
        return new NodeValue("");
    }

    @Override
    public NodeValue visitOpGlobal(GslParser.OpGlobalContext ctx) {
        StringBuilder code = new StringBuilder();
        List<TerminalNode> ids = ctx.ID();
        List<GslParser.TypeContext> types = ctx.type();
        List<GslParser.ExprContext> exprs = ctx.expr();
        for (int i = 0; i < ids.size(); i++) {
            String varName = ids.get(i).getText();
            String llvmName = "@" + varName;
            String typeName = types.get(Math.min(i, types.size() - 1)).getText();
            String llvmType = generator.toLLVMType(typeName);
            if (exprs.size() > i && exprs.get(i) != null) {
                NodeValue initExpr = visit(exprs.get(i));
                String tmpVar = generator.tmpVar();
                code.append(initExpr.code);
                code.append("  store ").append(initExpr.irType).append(" ").append(initExpr.operand)
                        .append(", ").append(llvmType).append("* ").append(llvmName)
                        .append(", align ").append(generator.getAlign(typeName)).append("\n");
            }

            VariableInfo info = new VariableInfo(varName, typeName, true);
            context.addGlobalVariableToMain(info);
        }

        return new NodeValue(code.toString());
    }

    @Override
    public NodeValue visitOpAssign(GslParser.OpAssignContext ctx) {
        List<TerminalNode> ids = ctx.leftAssign().ID();
        List<GslParser.ExprContext> exprs = ctx.exprList().expr();
        StringBuilder code = new StringBuilder();

        for (int i = 0; i < ids.size(); i++) {
            String varName = ids.get(i).getText();
            VariableInfo varInfo = context.getCurrentFunction().getVariable(varName);
            boolean isGlobal = false;

            if (varInfo == null) {
                varInfo = context.getGlobalVariable(varName);
                if (varInfo == null) {
                    throw new RuntimeException("Переменная " + varName + " не найдена ни локально, ни глобально");
                }
                isGlobal = true;
            }

            NodeValue rhs = visit(exprs.get(i));
            code.append(rhs.code);

            if (isGlobal) {
                String llvmName = "@" + varInfo.name;
                code.append("  store ")
                        .append(rhs.irType).append(" ").append(rhs.operand)
                        .append(", ").append(generator.toLLVMType(varInfo.type))
                        .append("* ").append(llvmName)
                        .append(", align ").append(generator.getAlign(varInfo.type))
                        .append("\n");
            } else {
                String llvmName = "%" + varName + ".addr";
                if (!varInfo.isOut() && !varInfo.isAllocaGenerated()) {
                    code.append(generator.alloca(llvmName, varInfo.type));
                    varInfo.setAllocaGenerated(true);
                }

                code.append(generator.store(llvmName, rhs.operand, rhs.irType, varInfo.type));
            }
        }

        return new NodeValue(code.toString());
    }

    @Override
    public NodeValue visitOpDeclare(GslParser.OpDeclareContext ctx) {
        List<TerminalNode> ids = ctx.leftAssign().ID();
        StringBuilder code = new StringBuilder();

        for (TerminalNode idNode : ids) {
            String varName = idNode.getText();
            VariableInfo varInfo = context.getCurrentFunction().getVariable(varName);

            if (!varInfo.isOut() && !varInfo.isAllocaGenerated()) {
                String llvmName = "%" + varInfo.name + ".addr";
                code.append(generator.alloca(llvmName, varInfo.type));
                varInfo.setAllocaGenerated(true);
            }
        }

        return new NodeValue(code.toString());
    }


    @Override
    public NodeValue visitOpReturn(GslParser.OpReturnContext ctx) {
        if (ctx.expr() == null)
            return new NodeValue("  ret void\n");

        NodeValue value = visit(ctx.expr());
        StringBuilder code = new StringBuilder(value.code);

        String operand = value.operand;
        String retType = value.irType;

        String varName = tryExtractVarName(operand);

        VariableInfo info = findVarInCurrentFunction(varName);

        boolean needLoad = false;

        if (info != null) {
            if (!info.isGlobal) {

                if (operand.endsWith(".addr"))
                    needLoad = true;

                if (info.isParameter && !operand.endsWith(".addr"))
                    needLoad = true;

                if (info.isOut)
                    needLoad = false;
            }
        }

        if (needLoad) {
            String llvmType = generator.toLLVMType(value.type);
            String tmp = generator.tmpVar();

            code.append("  ")
                    .append(tmp)
                    .append(" = load ").append(llvmType)
                    .append(", ").append(llvmType).append("* ").append(operand+".addr")
                    .append("\n");

            operand = tmp;
        }

        code.append("  ret ")
                .append(retType)
                .append(" ")
                .append(operand)
                .append("\n");

        return new NodeValue(code.toString());
    }


    private String tryExtractVarName(String operand) {
        if (!operand.startsWith("%"))
            return null;

        String name = operand.substring(1);

        if (name.endsWith(".addr")) {
            return name.substring(0, name.length() - 5);
        }

        return name;
    }

    private VariableInfo findVarInCurrentFunction(String varName) {
        if (varName == null) return null;
        return context.getCurrentFunction().getVariable(varName);
    }


    @Override
    public NodeValue visitOpIf(GslParser.OpIfContext ctx) {
        String thenLabel = generator.newLabel("if.then");
        String elseLabel = generator.newLabel("if.else");
        String endLabel  = generator.newLabel("if.end");
        StringBuilder code = new StringBuilder();
        NodeValue cond = visit(ctx.expr());
        code.append(cond.code);

        String condVar = cond.operand;
        if (!cond.irType.equals("i1")) {
            String cmpTmp = generator.tmpVar();
            code.append("  ").append(cmpTmp)
                    .append(" = icmp ne ").append(cond.irType)
                    .append(" ").append(condVar).append(", 0\n");
            condVar = cmpTmp;
        }

        code.append("  br i1 ").append(condVar)
                .append(", label %").append(thenLabel)
                .append(", label %").append(elseLabel)
                .append("\n");

        code.append(thenLabel).append(":\n");
        String thenCode = visit(ctx.body(0)).code;
        code.append(thenCode);

        boolean thenReturns = thenCode.trim().endsWith("ret void")
                || thenCode.trim().matches("ret [a-z0-9]+.*");

        if (!thenReturns) {
            code.append("  br label %").append(endLabel).append("\n");
        }

        code.append(elseLabel).append(":\n");

        String elseCode = "";
        if (ctx.opIf() != null) {
            elseCode = visit(ctx.opIf()).code; // else if
        } else if (ctx.body().size() > 1) {
            elseCode = visit(ctx.body(1)).code; // обычный else
        }
        code.append(elseCode);

        boolean elseReturns = elseCode.trim().endsWith("ret void")
                || elseCode.trim().matches("ret [a-z0-9]+.*");

        if (!elseReturns) {
            code.append("  br label %").append(endLabel).append("\n");
        }

        if (!thenReturns || !elseReturns) {
            code.append(endLabel).append(":\n");
        }

        return new NodeValue(code.toString());
    }


    @Override
    public NodeValue visitOpWhile(GslParser.OpWhileContext ctx) {
        String condLabel = generator.newLabel("while.cond");
        String bodyLabel = generator.newLabel("while.body");
        String endLabel  = generator.newLabel("while.end");

        StringBuilder code = new StringBuilder();

        code.append("  br label %").append(condLabel).append("\n");

        code.append(condLabel).append(":\n");
        NodeValue cond = visit(ctx.expr());
        String condVar = cond.operand;
        code.append(cond.code);

        if (!cond.irType.equals("i1")) {
            String tmp = generator.tmpVar();
            code.append("  ").append(tmp).append(" = icmp ne ").append(cond.irType)
                    .append(" ").append(condVar).append(", 0\n");
            condVar = tmp;
        }

        code.append("  br i1 ").append(condVar).append(", label %").append(bodyLabel)
                .append(", label %").append(endLabel).append("\n");

        code.append(bodyLabel).append(":\n");
        code.append(visit(ctx.body()).code);
        code.append("  br label %").append(condLabel).append("\n");

        code.append(endLabel).append(":\n");

        return new NodeValue(code.toString());
    }

    @Override
    public NodeValue visitOpUntil(GslParser.OpUntilContext ctx) {
        String bodyLabel = generator.newLabel("until.body");
        String condLabel = generator.newLabel("until.cond");
        String endLabel  = generator.newLabel("until.end");

        StringBuilder code = new StringBuilder();

        code.append("  br label %").append(bodyLabel).append("\n");

        code.append(bodyLabel).append(":\n");
        code.append(visit(ctx.body()).code);
        code.append("  br label %").append(condLabel).append("\n");

        code.append(condLabel).append(":\n");
        NodeValue cond = visit(ctx.expr());
        String condVar = cond.operand;
        code.append(cond.code);

        if (!cond.irType.equals("i1")) {
            String tmp = generator.tmpVar();
            code.append("  ").append(tmp).append(" = icmp ne ").append(cond.irType)
                    .append(" ").append(condVar).append(", 0\n");
            condVar = tmp;
        }

        String invCond = generator.tmpVar();
        code.append("  ").append(invCond).append(" = xor i1 ").append(condVar).append(", 1\n");
        code.append("  br i1 ").append(invCond).append(", label %").append(bodyLabel)
                .append(", label %").append(endLabel).append("\n");

        code.append(endLabel).append(":\n");

        return new NodeValue(code.toString());
    }

    @Override
    public NodeValue visitOpFor(GslParser.OpForContext ctx) {
        String initLabel = generator.newLabel("for.init");
        String condLabel = generator.newLabel("for.cond");
        String bodyLabel = generator.newLabel("for.body");
        String incrLabel = generator.newLabel("for.incr");
        String endLabel  = generator.newLabel("for.end");
        StringBuilder code = new StringBuilder();
        if (ctx.opAssign(0) != null) {
            code.append(visit(ctx.opAssign(0)).code);
        }
        code.append("  br label %").append(condLabel).append("\n");
        code.append(condLabel).append(":\n");
        NodeValue cond = ctx.expr() != null ? visit(ctx.expr()) : null;
        String condVar = "1";
        if (cond != null) {
            code.append(cond.code);
            condVar = cond.operand;
            if (!cond.irType.equals("i1")) {
                String tmp = generator.tmpVar();
                code.append("  ").append(tmp).append(" = icmp ne ").append(cond.irType)
                        .append(" ").append(condVar).append(", 0\n");
                condVar = tmp;
            }
        }
        code.append("  br i1 ").append(condVar).append(", label %").append(bodyLabel)
                .append(", label %").append(endLabel).append("\n");
        code.append(bodyLabel).append(":\n");
        code.append(visit(ctx.body()).code);
        code.append("  br label %").append(incrLabel).append("\n");
        code.append(incrLabel).append(":\n");
        if (ctx.opAssign().size() > 1) {
            code.append(visit(ctx.opAssign(1)).code);
        } else if (ctx.opExpr() != null) {
            code.append(visit(ctx.opExpr()).code);
        }
        code.append("  br label %").append(condLabel).append("\n");
        code.append(endLabel).append(":\n");
        return new NodeValue(code.toString());
    }


    @Override
    public NodeValue visitLiteralPrimary(GslParser.LiteralPrimaryContext ctx) {
        if (ctx.literal().INT() != null) {
            String value = ctx.literal().INT().getText();
            return new NodeValue(Type.INT.getValue(), "i32", value, "");
        }
        if (ctx.literal().BOOLEAN() != null) {
            String value = ctx.literal().BOOLEAN().getText().equals("true") ? "1" : "0";
            return new NodeValue(Type.BOOLEAN.getValue(), "i1", value, "");
        }
        if (ctx.literal().STRING() != null) {
            String strValue = ctx.literal().STRING().getText();
            strValue = strValue.substring(1, strValue.length() - 1);
            generator.createStringLiteral(strValue);
            String name = generator.getStringLiteralName(strValue);
            return new NodeValue(Type.STRING.getValue(), "i8*", name, "");
        }
        throw new RuntimeException();
    }

    @Override
    public NodeValue visitOpMethodCall(GslParser.OpMethodCallContext ctx) {
        String fname = ctx.ID().getText();
        List<NodeValue> args = new ArrayList<>();
        context.setMethodCalled(true);
        context.setCalledMethod(context.getFirst(fname));
        if (ctx.argList() != null) {
            int i = 0;
            for (var e : ctx.argList().expr()) {
                context.setMethodParameterIndex(i);
                args.add(visit(e));
                i++;
            }
        }
        context.setMethodCalled(false);
        List<String> argTypes = args.stream().map(a -> a.type).toList();
        FunctionSignature fn = context.getFunction(fname, argTypes);
        if (fn.isFromCode) {
            return generator.call(fn, args);
        }
        return generator.generateCall(fn, args);
    }

    @Override
    public NodeValue visitIdPrimary(GslParser.IdPrimaryContext ctx) {
        String varName = ctx.ID().getText();
        VariableInfo info = context.getCurrentFunction().getVariable(varName);
        boolean isGlobal = false;
        if (info == null) {
            for (VariableInfo globalVar : context.getFunction("main", List.of()).variables) {
                if (globalVar.name.equals(varName)) {
                    info = globalVar;
                    isGlobal = true;
                    break;
                }
            }
            if (info == null) {
                throw new RuntimeException("variable '" + varName + "' not found");
            }
        }
        if (info.isGlobal) {
            isGlobal = true;
        }
        boolean isOut = false;
        if (context.isMethodCalled() && context.getCalledMethod() != null && context.getCalledMethod().isFromCode) {
            FunctionSignature fn = context.getCalledMethod();
            int paramIndex = context.getMethodParameterIndex();
            if (paramIndex < fn.paramTypes.size()) {
                VariableInfo paramInfo = fn.getVariable(fn.variables.get(paramIndex).name);
                if (paramInfo != null && paramInfo.isOut) {
                    isOut = true;
                }
            }
        }
        String llvmType = generator.toLLVMType(info.type);
        String operand;
        String code = "";
        if (isGlobal) {
            operand = generator.tmpVar();
            code = "  " + operand + " = load " + llvmType + ", " + llvmType + "* @" + varName + "\n";
        } else if (info.isParameter || isOut) {
            operand = "%" + info.name;
        } else {
            String allocaName = "%" + info.name + ".addr";
            operand = generator.tmpVar();
            code = "  " + operand + " = load " + llvmType + ", " + llvmType + "* " + allocaName + "\n";
        }

        return new NodeValue(info.type, llvmType, operand, code);
    }


    @Override
    public NodeValue visitPrimaryExpr(GslParser.PrimaryExprContext ctx) {
        return visit(ctx.primary());
    }

    @Override
    public NodeValue visitNodeLiteral(GslParser.NodeLiteralContext ctx) {
        NodeValue value = visit(ctx.expr());
        return generator.generateCall(
                context.getFunction("makeNode", List.of("string")),
                List.of(value)
        );
    }

    @Override
    public NodeValue visitArcLiteral(GslParser.ArcLiteralContext ctx) {
        NodeValue from = visit(ctx.expr(0));
        NodeValue to   = visit(ctx.expr(1));
        return generator.generateCall(
                context.getFunction("makeArc", List.of("node", "node")),
                List.of(from, to)
        );
    }

    @Override
    public NodeValue visitGraphLiteral(GslParser.GraphLiteralContext ctx) {
        List<NodeValue> nodes = new ArrayList<>();
        List<NodeValue> arcs  = new ArrayList<>();
        if (ctx.nodeList() != null) {
            for (GslParser.ExprContext nodeCtx : ctx.nodeList().expr()) {
                nodes.add(visit(nodeCtx));
            }
        }
        if (ctx.arcList() != null) {
            for (GslParser.ExprContext arcCtx : ctx.arcList().expr()) {
                arcs.add(visit(arcCtx));
            }
        }
        return generateGraph(nodes, arcs);
    }

    private NodeValue generateGraph(List<NodeValue> nodes, List<NodeValue> arcs) {
        String makeTmp = generator.tmpVar();
        String makeCode = "  " + makeTmp + " = call %graph* @makeGraph(%node* null, %arc* null)\n";
        NodeValue graph = new NodeValue("graph", "%graph*", makeTmp, makeCode);
        if (nodes != null) {
            for (NodeValue node : nodes) {
                graph = generator.generateCall(
                        context.getFunction("addNode", List.of("graph", "node")),
                        List.of(graph, node)
                );
            }
        }
        if (arcs != null) {
            for (NodeValue arc : arcs) {
                graph = generator.generateCall(
                        context.getFunction("addArc", List.of("graph", "arc")),
                        List.of(graph, arc)
                );
            }
        }
        return graph;
    }


    @Override
    public NodeValue visitAddExpr(GslParser.AddExprContext ctx) {
        NodeValue left = visit(ctx.expr(0));
        NodeValue right = visit(ctx.expr(1));
        if (left.type.equals(Type.INT.getValue()) &&
                right.type.equals(Type.INT.getValue())) {
            String tmp = generator.tmpVar();
            String code = left.code + right.code;
            code += "  " + tmp + " = add i32 " + left.operand + ", " + right.operand + "\n";
            return new NodeValue(Type.INT.getValue(), "i32", tmp, code);
        }
        if (left.type.equals(Type.STRING.getValue()) &&
                right.type.equals(Type.STRING.getValue())) {

            return generator.generateCall(
                    context.getFunction("concatString", List.of("string", "string")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.ARC.getValue()) &&
                right.type.equals(Type.ARC.getValue())) {

            return generator.generateCall(
                    context.getFunction("concatArc", List.of("arc", "arc")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.NODE.getValue()) &&
                right.type.equals(Type.NODE.getValue())) {
            return generator.generateCall(
                    context.getFunction("concatNode", List.of("node", "node")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.GRAPH.getValue()) &&
                right.type.equals(Type.GRAPH.getValue())) {
            return generator.generateCall(
                    context.getFunction("concatGraph", List.of("graph", "graph")),
                    List.of(left, right)
            );
        }
        throw new RuntimeException("Unsupported operands for +: " + left.type + " and " + right.type);
    }

    @Override
    public NodeValue visitSubExpr(GslParser.SubExprContext ctx) {
        NodeValue left = visit(ctx.expr(0));
        NodeValue right = visit(ctx.expr(1));
        if (left.type.equals(Type.INT.getValue()) &&
                right.type.equals(Type.INT.getValue())) {

            String tmp = generator.tmpVar();
            String code = left.code + right.code;
            code += "  " + tmp + " = sub i32 " + left.operand + ", " + right.operand + "\n";

            return new NodeValue(Type.INT.getValue(), "i32", tmp, code);
        }
        if (left.type.equals(Type.STRING.getValue()) &&
                right.type.equals(Type.STRING.getValue())) {

            return generator.generateCall(
                    context.getFunction("subtractString", List.of("string", "string")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.NODE.getValue()) &&
                right.type.equals(Type.NODE.getValue())) {
            return generator.generateCall(
                    context.getFunction("nodeSub", List.of("node", "node")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.ARC.getValue()) &&
                right.type.equals(Type.ARC.getValue())) {

            return generator.generateCall(
                    context.getFunction("arcSub", List.of("arc", "arc")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.GRAPH.getValue()) &&
                right.type.equals(Type.GRAPH.getValue())) {

            return generator.generateCall(
                    context.getFunction("graphSub", List.of("graph", "graph")),
                    List.of(left, right)
            );
        }
        throw new RuntimeException("Unsupported operands for -: "
                + left.type + " and " + right.type);
    }

    @Override
    public NodeValue visitMulExpr(GslParser.MulExprContext ctx) {
        NodeValue left = visit(ctx.expr(0));
        NodeValue right = visit(ctx.expr(1));
        if (left.type.equals(Type.INT.getValue()) &&
                right.type.equals(Type.INT.getValue())) {
            String tmp = generator.tmpVar();
            String code = left.code + right.code;
            code += "  " + tmp + " = mul i32 " + left.operand + ", " + right.operand + "\n";
            return new NodeValue(Type.INT.getValue(), "i32", tmp, code);
        }
        if (left.type.equals(Type.STRING.getValue()) &&
                right.type.equals(Type.STRING.getValue())) {
            return generator.generateCall(
                    context.getFunction("multiplyString", List.of("string", "string")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.NODE.getValue()) &&
                right.type.equals(Type.NODE.getValue())) {
            return generator.generateCall(
                    context.getFunction("nodeMul", List.of("node", "node")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.ARC.getValue()) &&
                right.type.equals(Type.ARC.getValue())) {

            return generator.generateCall(
                    context.getFunction("arcMul", List.of("arc", "arc")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.GRAPH.getValue()) &&
                right.type.equals(Type.GRAPH.getValue())) {
            return generator.generateCall(
                    context.getFunction("graphMul", List.of("graph", "graph")),
                    List.of(left, right)
            );
        }
        throw new RuntimeException("Unsupported operands for *: "
                + left.type + " and " + right.type);
    }

    @Override
    public NodeValue visitDivExpr(GslParser.DivExprContext ctx) {
        NodeValue left = visit(ctx.expr(0));
        NodeValue right = visit(ctx.expr(1));
        if (left.type.equals(Type.INT.getValue()) &&
                right.type.equals(Type.INT.getValue())) {
            String tmp = generator.tmpVar();
            String code = left.code + right.code;
            code += "  " + tmp + " = sdiv i32 " + left.operand + ", " + right.operand + "\n";
            return new NodeValue(Type.INT.getValue(), "i32", tmp, code);
        }
        if (left.type.equals(Type.STRING.getValue()) &&
                right.type.equals(Type.STRING.getValue())) {
            return generator.generateCall(
                    context.getFunction("divideString", List.of("string", "string")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.NODE.getValue()) &&
                right.type.equals(Type.NODE.getValue())) {
            return generator.generateCall(
                    context.getFunction("nodeDiv", List.of("node", "node")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.ARC.getValue()) &&
                right.type.equals(Type.ARC.getValue())) {
            return generator.generateCall(
                    context.getFunction("arcDiv", List.of("arc", "arc")),
                    List.of(left, right)
            );
        }
        if (left.type.equals(Type.GRAPH.getValue()) &&
                right.type.equals(Type.GRAPH.getValue())) {
            return generator.generateCall(
                    context.getFunction("graphDiv", List.of("graph", "graph")),
                    List.of(left, right)
            );
        }
        throw new RuntimeException("Unsupported operands for /: "
                + left.type + " and " + right.type);
    }

    @Override
    public NodeValue visitOrExpr(GslParser.OrExprContext ctx) {
        NodeValue lhs = visit(ctx.expr(0));
        NodeValue rhs = visit(ctx.expr(1));
        return generator.genBinaryOp("||", lhs, rhs);
    }

    @Override
    public NodeValue visitAndExpr(GslParser.AndExprContext ctx) {
        NodeValue lhs = visit(ctx.expr(0));
        NodeValue rhs = visit(ctx.expr(1));
        return generator.genBinaryOp("&&", lhs, rhs);
    }

    @Override
    public NodeValue visitEqExpr(GslParser.EqExprContext ctx) {
        NodeValue lhs = visit(ctx.expr(0));
        NodeValue rhs = visit(ctx.expr(1));
        if (lhs.type.equals(Type.INT.getValue()) || lhs.type.equals(Type.BOOLEAN.getValue())) {
            return generator.genBinaryOp("==", lhs, rhs);
        }
        if (lhs.type.equals(Type.STRING.getValue())) {
            return generator.generateCall(
                    context.getFunction("stringEq", List.of("string","string")),
                    List.of(lhs, rhs)
            );
        }
        if (lhs.type.equals(Type.NODE.getValue())) {
            return generator.generateCall(
                    context.getFunction("nodeEq", List.of("node","node")),
                    List.of(lhs, rhs)
            );
        }
        if (lhs.type.equals(Type.ARC.getValue())) {
            return generator.generateCall(
                    context.getFunction("arcEq", List.of("arc","arc")),
                    List.of(lhs, rhs)
            );
        }
        if (lhs.type.equals(Type.GRAPH.getValue())) {
            return generator.generateCall(
                    context.getFunction("graphEq", List.of("graph","graph")),
                    List.of(lhs, rhs)
            );
        }
        throw new RuntimeException("Unsupported operands for ==: " + lhs.type + " and " + rhs.type);
    }

    @Override
    public NodeValue visitNeqExpr(GslParser.NeqExprContext ctx) {
        NodeValue lhs = visit(ctx.expr(0));
        NodeValue rhs = visit(ctx.expr(1));

        if (lhs.type.equals(Type.INT.getValue()) || lhs.type.equals(Type.BOOLEAN.getValue())) {
            return generator.genBinaryOp("!=", lhs, rhs);
        }
        if (lhs.type.equals(Type.STRING.getValue())) {
            return generator.generateCall(
                    context.getFunction("stringNeq", List.of("string","string")),
                    List.of(lhs, rhs)
            );
        }
        if (lhs.type.equals(Type.NODE.getValue())) {
            return generator.generateCall(
                    context.getFunction("nodeNeq", List.of("node","node")),
                    List.of(lhs, rhs)
            );
        }
        if (lhs.type.equals(Type.ARC.getValue())) {
            return generator.generateCall(
                    context.getFunction("arcNeq", List.of("arc","arc")),
                    List.of(lhs, rhs)
            );
        }
        if (lhs.type.equals(Type.GRAPH.getValue())) {
            return generator.generateCall(
                    context.getFunction("graphNeq", List.of("graph","graph")),
                    List.of(lhs, rhs)
            );
        }

        throw new RuntimeException("Unsupported operands for !=: " + lhs.type + " and " + rhs.type);
    }


    @Override
    public NodeValue visitLtExpr(GslParser.LtExprContext ctx) {
        NodeValue lhs = visit(ctx.expr(0));
        NodeValue rhs = visit(ctx.expr(1));
        return generator.genBinaryOp("<", lhs, rhs);
    }

    @Override
    public NodeValue visitLeExpr(GslParser.LeExprContext ctx) {
        NodeValue lhs = visit(ctx.expr(0));
        NodeValue rhs = visit(ctx.expr(1));
        return generator.genBinaryOp("<=", lhs, rhs);
    }

    @Override
    public NodeValue visitGtExpr(GslParser.GtExprContext ctx) {
        NodeValue lhs = visit(ctx.expr(0));
        NodeValue rhs = visit(ctx.expr(1));
        return generator.genBinaryOp(">", lhs, rhs);
    }

    @Override
    public NodeValue visitGeExpr(GslParser.GeExprContext ctx) {
        NodeValue lhs = visit(ctx.expr(0));
        NodeValue rhs = visit(ctx.expr(1));
        return generator.genBinaryOp(">=", lhs, rhs);
    }

    @Override
    public NodeValue visitCastExpr(GslParser.CastExprContext ctx) {
        NodeValue value = visit(ctx.expr());
        String targetType = ctx.type().getText();

        // ----- Примитивные касты между int <-> boolean -----
        if ((value.type.equals("int") || value.type.equals("boolean")) &&
                (targetType.equals("int") || targetType.equals("boolean"))) {
            String tmp = generator.tmpVar();
            String code = value.code;
            if (value.irType.equals("i32") && targetType.equals("boolean")) {
                code += "  " + tmp + " = icmp ne i32 " + value.operand + ", 0\n";
                return new NodeValue("boolean", "i1", tmp, code);
            }
            if (value.irType.equals("i1") && targetType.equals("int")) {
                code += "  " + tmp + " = zext i1 " + value.operand + " to i32\n";
                return new NodeValue("int", "i32", tmp, code);
            }
            return value;
        }
        switch (targetType) {
            case "node":
                return generator.generateCall(
                        context.getFunction("castStringToNode", List.of("string")),
                        List.of(value)
                );
            case "arc":
                return generator.generateCall(
                        context.getFunction("castNodeToArc", List.of("node")),
                        List.of(value)
                );
            case "graph":
                return generator.generateCall(
                        context.getFunction("castArcToGraph", List.of("arc")),
                        List.of(value)
                );
            case "int":
                if (value.type.equals("string")) {
                    // каст string -> int
                    return generator.generateCall(
                            context.getFunction("castStringToInt", List.of("string")),
                            List.of(value)
                    );
                }
            case "string":
                if (value.type.equals("int")) {
                    // каст int -> string
                    return generator.generateCall(
                            context.getFunction("castIntToString", List.of("int")),
                            List.of(value)
                    );
                }
            default:
                throw new RuntimeException(
                        "Unsupported cast from " + value.type + " to " + targetType
                );
        }
    }


    @Override
    public NodeValue visitPrefixOpExpr(GslParser.PrefixOpExprContext ctx) {
        NodeValue value = visit(ctx.prefixExpr().expr());
        String op = ctx.prefixExpr().getChild(0).getText(); // ++, --, !
        String tmp = generator.tmpVar();
        String code = value.code;

        switch (op) {
            case "++":
                code += "  " + tmp + " = add i32 " + value.operand + ", 1\n";

                Pattern pInc = Pattern.compile("load i32, i32\\* (%\\w+)(?:\\.addr)?");
                Matcher mInc = pInc.matcher(value.code);

                if (mInc.find()) {
                    String varPtr = mInc.group(1);
                    if (!varPtr.endsWith(".addr")) varPtr += ".addr";

                    code += "  store i32 " + tmp + ", i32* " + varPtr + "\n";
                }
                return new NodeValue(value.type, value.irType, tmp, code);

            case "--":
                code += "  " + tmp + " = sub i32 " + value.operand + ", 1\n";

                Pattern pDec = Pattern.compile("load i32, i32\\* (%\\w+)(?:\\.addr)?");
                Matcher mDec = pDec.matcher(value.code);

                if (mDec.find()) {
                    String varPtr = mDec.group(1);
                    if (!varPtr.endsWith(".addr")) varPtr += ".addr";

                    code += "  store i32 " + tmp + ", i32* " + varPtr + "\n";
                }
                return new NodeValue(value.type, value.irType, tmp, code);

            case "!":
                String notTmp = generator.tmpVar();
                if (value.irType.equals("i1")) {
                    code += "  " + notTmp + " = xor i1 " + value.operand + ", true\n";
                } else {
                    String cmpTmp = generator.tmpVar();
                    code += "  " + cmpTmp + " = icmp eq " + value.irType + " " + value.operand + ", 0\n";
                    code += "  " + notTmp + " = xor i1 " + cmpTmp + ", true\n";
                }
                return new NodeValue("boolean", "i1", notTmp, code);

            default:
                throw new RuntimeException("Unsupported prefix operator: " + op);
        }
    }


    @Override
    public NodeValue visitParensExpr(GslParser.ParensExprContext ctx) {
        return visit(ctx.expr());
    }

    @Override
    public NodeValue visitPostfixOpExpr(GslParser.PostfixOpExprContext ctx) {
        NodeValue value = visit(ctx.postfixExpr().primary());
        String op = ctx.postfixExpr().getChild(1).getText();
        String tmp = generator.tmpVar();
        String code = value.code;

        switch (op) {
            case "++":
                code += "  " + tmp + " = add i32 " + value.operand + ", 1\n";
                break;
            case "--":
                code += "  " + tmp + " = sub i32 " + value.operand + ", 1\n";
                break;
            default:
                throw new RuntimeException("Unsupported postfix operator: " + op);
        }

        Pattern p = Pattern.compile("load i32, i32\\* (%\\w+)(?:\\.addr)?");
        Matcher m = p.matcher(value.code);

        if (m.find()) {
            String varPtr = m.group(1);
            if (!varPtr.endsWith(".addr")) varPtr += ".addr";

            code += "  store i32 " + tmp + ", i32* " + varPtr + "\n";
        }

        return new NodeValue(value.type, value.irType, tmp, code);
    }

}
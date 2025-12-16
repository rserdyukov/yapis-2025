package dev.dezzzl.codegen;

import dev.dezzzl.NodeValue;
import dev.dezzzl.semantics.function.FunctionSignature;
import dev.dezzzl.semantics.function.VariableInfo;
import lombok.Getter;
import lombok.Setter;

import java.util.*;

public class IRGenerator {

    private static final Map<String, TypeInfo> typeMap = Map.of(
            "int", new TypeInfo("i32", 4),
            "boolean", new TypeInfo("i1", 1),
            "void", new TypeInfo("void", 0),
            "node", new TypeInfo("%node*", 8),
            "arc", new TypeInfo("%arc*", 8),
            "graph", new TypeInfo("%graph*", 8)
    );

    private final Map<String, String> stringLiterals = new LinkedHashMap<>();

    private int stringCounter = 0;

    private final StringBuilder module = new StringBuilder();

    private final List<String> structs = new ArrayList<>();

    private final List<String> builtinFunctions = new ArrayList<>();

    private final Deque<StringBuilder> blocks = new ArrayDeque<>();

    private final Map<String, String> localVars = new HashMap<>();

    @Getter
    private final List<String> globalVarsStrs = new ArrayList<>();

    @Setter
    private int tempVarCounter = 0;

    @Setter
    private int methodPrefixCounter = 0;

    private int labelCounter = 0;

    public IRGenerator() {

    }

    public void initModule() {
        module.append("; ModuleID = 'gsl_module'\n");
        module.append("source_filename = \"gsl_module\"\n\n");
        structs.add("%node = type { i8* }");
        structs.add("%arc = type { %node*, %node* }");
        structs.add("%graph = type { %node*, %arc* }");
        builtinFunctions.add("declare i8* @read()");
        builtinFunctions.add("declare void @printInt(i32)");
        builtinFunctions.add("declare void @printStr(i8*)");
        builtinFunctions.add("declare void @printNode(%node*)");
        builtinFunctions.add("declare void @printArc(%arc*)");
        builtinFunctions.add("declare void @printGraph(%graph*)");
        builtinFunctions.add("declare void @printBoolean(i1)");
        builtinFunctions.add("declare %node* @makeNode(i8*)");
        builtinFunctions.add("declare %arc*  @makeArc(%node*, %node*)");
        builtinFunctions.add("declare %graph* @makeGraph(%node*, %arc*)");
        builtinFunctions.add("declare %graph* @addNode(%graph*, %node*)");
        builtinFunctions.add("declare %graph* @deleteNode(%graph*, %node*)");
        builtinFunctions.add("declare %node*  @getNode(%graph*, i32)");
        builtinFunctions.add("declare %node*  @getNeighbour(%graph*, %node*, i32)");
        builtinFunctions.add("declare %graph* @addArc(%graph*, %arc*)");
        builtinFunctions.add("declare i1     @hasNode(%graph*, %node*)");
        builtinFunctions.add("declare i1     @hasArc(%graph*, %arc*)");
        builtinFunctions.add("declare %graph* @deleteArc(%graph*, %arc*)");
        builtinFunctions.add("declare i32    @size(%graph*)");
        builtinFunctions.add("declare %graph* @shortestPath(%graph*, %node*, %node*)");
        builtinFunctions.add("declare %graph* @bfs(%graph*, %node*)");
        builtinFunctions.add("declare %graph* @dfs(%graph*, %node*)");
        builtinFunctions.add("declare i8*    @concatString(i8*, i8*)");
        builtinFunctions.add("declare %node* @concatNode(%node*, %node*)");
        builtinFunctions.add("declare %arc*  @concatArc(%arc*, %arc*)");
        builtinFunctions.add("declare %graph* @concatGraph(%graph*, %graph*)");
        builtinFunctions.add("declare i8*    @subtractString(i8*, i8*)");
        builtinFunctions.add("declare %node* @nodeSub(%node*, %node*)");
        builtinFunctions.add("declare %arc*  @arcSub(%arc*, %arc*)");
        builtinFunctions.add("declare %graph* @graphSub(%graph*, %graph*)");
        builtinFunctions.add("declare i8*    @multiplyString(i8*, i8*)");
        builtinFunctions.add("declare %node* @nodeMul(%node*, %node*)");
        builtinFunctions.add("declare %arc*  @arcMul(%arc*, %arc*)");
        builtinFunctions.add("declare %graph* @graphMul(%graph*, %graph*)");
        builtinFunctions.add("declare i8*    @divideString(i8*, i8*)");
        builtinFunctions.add("declare %node* @nodeDiv(%node*, %node*)");
        builtinFunctions.add("declare %arc*  @arcDiv(%arc*, %arc*)");
        builtinFunctions.add("declare %graph* @graphDiv(%graph*, %graph*)");
        builtinFunctions.add("declare i1 @stringEq(i8*, i8*)");
        builtinFunctions.add("declare i1 @stringNeq(i8*, i8*)");
        builtinFunctions.add("declare i1 @nodeEq(%node*, %node*)");
        builtinFunctions.add("declare i1 @nodeNeq(%node*, %node*)");
        builtinFunctions.add("declare i1 @arcEq(%arc*, %arc*)");
        builtinFunctions.add("declare i1 @arcNeq(%arc*, %arc*)");
        builtinFunctions.add("declare i1 @graphEq(%graph*, %graph*)");
        builtinFunctions.add("declare i1 @graphNeq(%graph*, %graph*)");
        builtinFunctions.add("declare %node* @castStringToNode(i8*)");
        builtinFunctions.add("declare %arc*  @castNodeToArc(%node*)");
        builtinFunctions.add("declare %graph* @castArcToGraph(%arc*)");
        builtinFunctions.add("declare i32 @castStringToInt(i8*)");
        builtinFunctions.add("declare i8* @castIntToString(i32)");
        for (String s : structs) module.append(s).append("\n");
        module.append("\n");
        for (String s : builtinFunctions) module.append(s).append("\n");
        module.append("\n");
        for (String s : globalVarsStrs) {
            module.append(s).append("\n");
        }
        if (!globalVarsStrs.isEmpty()) module.append("\n");
    }

    public String getStringLiteralName(String literal) {
        return stringLiterals.get(literal);
    }

    public void createStringLiteral(String value) {
        if (stringLiterals.containsKey(value)) {
            return;
        }
        String name = "@.str" + stringCounter++;
        stringLiterals.put(value, name);
        int length = value.length() + 1;
        StringBuilder sb = new StringBuilder();
        sb.append(name)
                .append(" = private unnamed_addr constant [")
                .append(length)
                .append(" x i8] c\"")
                .append(escapeString(value))
                .append("\\00\"");
        globalVarsStrs.add(sb.toString());
    }

    /**
     * Экранирует спецсимволы для LLVM IR строки
     */
    private String escapeString(String s) {
        return s
                .replace("\\", "\\5C")
                .replace("\"", "\\22")
                .replace("\n", "\\0A")
                .replace("\r", "\\0D")
                .replace("\t", "\\09");
    }

    public String startFunction(FunctionSignature sig, List<String> paramNames) {
        String prefix = sig.prefix == null ? "" : sig.prefix;
        if (Objects.equals(sig.name, "main")) {
            prefix = "";
        }
        StringBuilder sb = new StringBuilder();
        sb.append("define ")
                .append(toLLVMType(sig.returnType))
                .append(" @")
                .append(sig.name + prefix)
                .append("(");

        List<String> params = new ArrayList<>();
        for (int i = 0; i < sig.paramTypes.size(); i++) {
            String pType = toLLVMType(sig.paramTypes.get(i));
            VariableInfo paramInfo = sig.getVariable(paramNames.get(i));

            if (paramInfo.isOut()) {
                pType = pType + "*";
            }

            String pName = "%" + paramNames.get(i);
            params.add(pType + " " + pName);
        }

        sb.append(String.join(", ", params));
        sb.append(") {\nentry:\n");
        return sb.toString();
    }



    public String tmpVar() {
        return "%t" + (tempVarCounter++);
    }

    public String prefix() {
        return "_" + (methodPrefixCounter++);
    }

    public void addInstruction(String instr) {
        module.append("  ").append(instr).append("\n");
    }

    public String endFunction(FunctionSignature signature) {
        if (signature.returnType.equals("void")) {
            return "  ret void\n}\n\n";
        }
        return "}\n\n";
    }

    public String alloca(String llvmName, String type) {
        String llvmType = toLLVMType(type);
        int align = getAlign(type);
        return "  " + llvmName + " = alloca " + llvmType + ", align " + align + "\n";
    }

    public String store(String llvmVar, String value, String valueType, String varType) {
        return "  store " + valueType + " " + value + ", " + toLLVMType(varType) + "* " + llvmVar
                + ", align " + getAlign(varType) + "\n";
    }

    public NodeValue generateCall(FunctionSignature fn, List<NodeValue> args) {
        String prefix = fn.prefix==null ? "" : fn.prefix;
        StringBuilder code = new StringBuilder();
        for (NodeValue a : args) {
            if (a.code != null && !a.code.isEmpty())
                code.append(a.code);
        }
        String retType = fn.returnType;
        String llvmRetType = toLLVMType(retType);
        List<String> params = new ArrayList<>();
        for (NodeValue a : args) {
            params.add(a.irType + " " + a.operand);
        }
        if (!retType.equals("void")) {
            String tmp = tmpVar();
            code.append("  ")
                    .append(tmp)
                    .append(" = call ")
                    .append(llvmRetType)
                    .append(" @")
                    .append(fn.name+prefix)
                    .append("(")
                    .append(String.join(", ", params))
                    .append(")\n");

            return new NodeValue(
                    retType,
                    llvmRetType,
                    tmp,
                    code.toString()
            );
        } else {
            code.append("  call void @")
                    .append(fn.name+prefix)
                    .append("(")
                    .append(String.join(", ", params))
                    .append(")\n");

            return new NodeValue(
                    "void",
                    "void",
                    "",
                    code.toString()
            );
        }
    }

    public NodeValue call(FunctionSignature fn, List<NodeValue> args) {
        String prefix = fn.prefix == null ? "" : fn.prefix;
        StringBuilder code = new StringBuilder();

        for (NodeValue a : args) {
            if (a.code != null && !a.code.isEmpty())
                code.append(a.code);
        }

        String retType = fn.returnType;
        String llvmRetType = toLLVMType(retType);
        List<String> params = new ArrayList<>();

        for (int i = 0; i < args.size(); i++) {
            NodeValue arg = args.get(i);
            VariableInfo paramInfo = fn.getVariableByIndex(i);

            String operand = arg.operand;
            String irType = arg.irType;

            if (paramInfo != null && paramInfo.isOut()) {
                if (!operand.endsWith(".addr")) {
                    operand += ".addr";
                }
                irType += "*";
            }

            params.add(irType + " " + operand);
        }

        if (!retType.equals("void")) {
            String tmp = tmpVar();
            code.append("  ")
                    .append(tmp)
                    .append(" = call ")
                    .append(llvmRetType)
                    .append(" @")
                    .append(fn.name + prefix)
                    .append("(")
                    .append(String.join(", ", params))
                    .append(")\n");

            return new NodeValue(retType, llvmRetType, tmp, code.toString());
        } else {
            code.append("  call void @")
                    .append(fn.name + prefix)
                    .append("(")
                    .append(String.join(", ", params))
                    .append(")\n");

            return new NodeValue("void", "void", "", code.toString());
        }
    }

    public NodeValue genBinaryOp(String op, NodeValue lhs, NodeValue rhs) {
        String code = lhs.code + rhs.code;
        String tmp = tmpVar();
        String irType = lhs.irType;
        switch (op) {
            case "||", "&&" -> {
                code += "  " + tmp + " = " + (op.equals("||") ? "or" : "and") + " i1 "
                        + lhs.operand + ", " + rhs.operand + "\n";
                irType = "i1";
            }
            case "==", "!=" -> {
                code += "  " + tmp + " = icmp " + (op.equals("==") ? "eq" : "ne") + " "
                        + lhs.irType + " " + lhs.operand + ", " + rhs.operand + "\n";
                irType = "i1";
            }
            case "<", "<=", ">", ">=" -> {
                String cmpOp = switch (op) {
                    case "<" -> "slt";
                    case "<=" -> "sle";
                    case ">" -> "sgt";
                    case ">=" -> "sge";
                    default -> throw new RuntimeException("Unknown op " + op);
                };
                code += "  " + tmp + " = icmp " + cmpOp + " " + lhs.irType + " "
                        + lhs.operand + ", " + rhs.operand + "\n";
                irType = "i1";
            }
            default -> throw new RuntimeException("Unsupported binary op " + op);
        }
        return new NodeValue("boolean", irType, tmp, code);
    }


    public String getLLVMDefaultValue(String typeName) {
        return switch (typeName) {
            case "int" -> "0";         // i32
            case "boolean" -> "0";     // i1
            case "string" -> "null";   // i8*
            case "node" -> "null";
            case "arc" -> "null";
            case "graph" -> "null";
            default -> throw new RuntimeException("Unsupported type for global default: " + typeName);
        };
    }

    public String toLLVMType(String type) {
        return typeMap.getOrDefault(type, new TypeInfo("i8*", 8)).llvmType;
    }

    public int getAlign(String type) {
        return typeMap.getOrDefault(type, new TypeInfo("i8*", 8)).align;
    }

    public String getModule() {
        return module.toString();
    }

    private static class TypeInfo {
        final String llvmType;
        final int align;

        TypeInfo(String llvmType, int align) {
            this.llvmType = llvmType;
            this.align = align;
        }
    }

    public String newLabel(String base) {
        return base + "_" + (labelCounter++);
    }

}

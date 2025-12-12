package graphlang.backend;

import graphlang.GraphLangBaseVisitor;
import graphlang.GraphLangParser;
import graphlang.semantics.GraphLangType;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.TerminalNode;

import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.regex.Pattern;

public final class GraphLangCodeGenerator extends GraphLangBaseVisitor<String> {

    private final StringBuilder topDecls = new StringBuilder();      
    private final List<String> topInitializers = new ArrayList<>();  
    private final StringBuilder functions = new StringBuilder();     
    private final StringBuilder mainBody = new StringBuilder();      

    private final Deque<Map<String, GraphLangType>> scopes = new ArrayDeque<>();
    private final Deque<Boolean> inFunction = new ArrayDeque<>();
    private String currentFunctionName = null;
    private final AtomicInteger tmpCounter = new AtomicInteger();
    private final Set<String> iteratorVars = new HashSet<>();

    private final Map<String, String> nodeGroupCountVar = new HashMap<>();

    private static final Pattern IDENT_RE = Pattern.compile("[a-zA-Z_][a-zA-Z0-9_]*");

    public GraphLangCodeGenerator() {
        scopes.push(new LinkedHashMap<>());
        inFunction.push(false);
    }

    private String fresh(String prefix) {
        return "_" + prefix + "_" + tmpCounter.getAndIncrement();
    }

    private void appendStatement(String stmt) {
        if (inFunction.peek() && currentFunctionName != null) {
            functions.append(stmt).append("\n");
        } else {
            mainBody.append(stmt).append("\n");
        }
    }

    private String cType(GraphLangType t) {
        return switch (t) {
            case NODE -> "int";
            case GRAPH -> "Graph*";
            case ARC -> "Arc";
            case NODE_GROUP -> "int*";
            case INT -> "int";
            case FLOAT -> "double";
            case STRING -> "char*";
            case BOOLEAN -> "int";
            case VOID -> "void";
            default -> "void*";
        };
    }

    private void declareVariable(String name, GraphLangType type, boolean isGlobal) {
        scopes.peek().put(name, type);
        String decl;
        if (isGlobal) {
            if (type == GraphLangType.NODE) {
                decl = String.format("%s %s;", cType(type), name);
                topInitializers.add(String.format("%s = node_create(\"%s\");", name, name));
            } else if (type == GraphLangType.GRAPH) {
                decl = String.format("%s %s;", cType(type), name);
                topInitializers.add(String.format("%s = graph_create();", name));
            } else if (type == GraphLangType.ARC) {
                decl = String.format("%s %s; /* arc */", cType(type), name);
            } else {
                decl = String.format("%s %s;", cType(type), name);
            }
            topDecls.append(decl).append("\n");
        } else {
            if (type == GraphLangType.NODE) {
                decl = String.format("%s %s = node_create(\"%s\");", cType(type), name, name);
            } else if (type == GraphLangType.GRAPH) {
                decl = String.format("%s %s = graph_create();", cType(type), name);
            } else if (type == GraphLangType.ARC) {
                decl = String.format("%s %s; /* arc */", cType(type), name);
            } else {
                decl = String.format("%s %s = 0;", cType(type), name);
            }
            if (inFunction.peek() && currentFunctionName != null) {
                functions.append(decl).append("\n");
            } else {
                mainBody.append(decl).append("\n");
            }
        }
    }

    private Optional<GraphLangType> lookupType(String name) {
        for (Map<String, GraphLangType> scope : scopes) {
            if (scope.containsKey(name)) return Optional.of(scope.get(name));
        }
        return Optional.empty();
    }

    public String generate(GraphLangParser.ProgramContext ctx) {
        visitProgram(ctx);

        StringBuilder out = new StringBuilder();
        out.append("#include <stdio.h>\n")
                .append("#include <stdlib.h>\n")
                .append("#include <string.h>\n")
                .append("\n")
                .append("/* Runtime declarations and minimal implementations */\n")
                .append(RuntimeC.RUNTIME_C_HEADER)
                .append("\n")
                .append(topDecls)
                .append("\n")
                .append(functions)
                .append("\n")
                .append("int main(int argc, char** argv) {\n");

        for (String init : topInitializers) {
            out.append("    ").append(init).append("\n");
        }

        if (mainBody.length() > 0) {
            String[] lines = mainBody.toString().split("\n");
            for (String line : lines) {
                if (line.isBlank()) continue;
                out.append("    ").append(line).append("\n");
            }
        }

        out.append("    return 0;\n");
        out.append("}\n");

        return out.toString();
    }


    @Override
    public String visitProgram(GraphLangParser.ProgramContext ctx) {

        for (GraphLangParser.FunctionDeclarationContext fnCtx : ctx.functionDeclaration()) {
            visit(fnCtx);
        }

        for (int i = 0; i < ctx.getChildCount(); i++) {
            ParseTree child = ctx.getChild(i);
            if (child instanceof GraphLangParser.FunctionDeclarationContext) continue;
            String s = visit(child);
            if (s != null && !s.isBlank()) {
                mainBody.append(s);
                if (!s.endsWith("\n")) mainBody.append("\n");
            }
        }
        return "";
    }

    @Override
    public String visitFunctionDeclaration(GraphLangParser.FunctionDeclarationContext ctx) {
        String name = ctx.ID().getText();
        String cName = "fn_" + name;
        currentFunctionName = cName;

        boolean prevInFunc = inFunction.pop();
        inFunction.push(true);
        scopes.push(new LinkedHashMap<>());

        List<String> paramDecls = new ArrayList<>();
        if (ctx.functionParamList() != null) {
            for (GraphLangParser.FunctionParamContext paramCtx : ctx.functionParamList().functionParam()) {
                String pname = paramCtx.ID().getText();
                GraphLangType ptype = resolveTypeKeyword(paramCtx.type());
                scopes.peek().put(pname, ptype);
                paramDecls.add(cType(ptype) + " " + pname);
            }
        }

        StringBuilder fn = new StringBuilder();
        fn.append("void ").append(cName).append("(").append(String.join(", ", paramDecls)).append(") {\n");

        String body = visit(ctx.block());
        if (body != null && !body.isBlank()) {
            String[] lines = body.split("\n");
            for (String line : lines) {
                if (line.isBlank()) continue;
                fn.append("    ").append(line).append("\n");
            }
        }
        fn.append("}\n\n");

        scopes.pop();
        inFunction.pop();
        inFunction.push(prevInFunc);
        currentFunctionName = null;

        functions.append(fn.toString());
        return "";
    }

    @Override
    public String visitBlock(GraphLangParser.BlockContext ctx) {
        scopes.push(new LinkedHashMap<>());
        StringBuilder local = new StringBuilder();
        for (GraphLangParser.StatementContext st : ctx.statement()) {
            String s = visit(st);
            if (s != null && !s.isBlank()) {
                local.append(s);
                if (!s.endsWith("\n")) local.append("\n");
            }
        }
        scopes.pop();
        return local.toString();
    }


    @Override
    public String visitNodeDecl(GraphLangParser.NodeDeclContext ctx) {
        String name = ctx.ID().getText();
        declareVariable(name, GraphLangType.NODE, !inFunction.peek());
        return "";
    }

    @Override
    public String visitGraphDecl(GraphLangParser.GraphDeclContext ctx) {
        String name = ctx.ID().getText();
        declareVariable(name, GraphLangType.GRAPH, !inFunction.peek());
        return "";
    }

    @Override
    public String visitArcDecl(GraphLangParser.ArcDeclContext ctx) {

        return "";
    }

    @Override
    public String visitVarDeclStmt_(GraphLangParser.VarDeclStmt_Context ctx) {
        GraphLangParser.VarDeclarationStatementContext decl = ctx.varDeclarationStatement();
        if (decl.NODE() != null) {
            declareVariable(decl.ID().getText(), GraphLangType.NODE, !inFunction.peek());
        } else {
            declareVariable(decl.ID().getText(), GraphLangType.GRAPH, !inFunction.peek());
        }
        return "";
    }

    @Override
    public String visitArcDeclStmt_(GraphLangParser.ArcDeclStmt_Context ctx) {
        return "";
    }

    @Override
    public String visitAssignStmt_(GraphLangParser.AssignStmt_Context ctx) {
        GraphLangParser.AssignmentStatementContext assign = ctx.assignmentStatement();
        String target;
        if (assign.ID() != null) {
            target = assign.ID().getText();
        } else {
            target = visit(assign.memberAccess());
        }
        String expr = visit(assign.expr());
        return target + " = " + expr + ";";
    }

    @Override
    public String visitExprStmt_(GraphLangParser.ExprStmt_Context ctx) {
        return visit(ctx.exprStatement().expr()) + ";";
    }

    @Override
    public String visitIfStmt_(GraphLangParser.IfStmt_Context ctx) {
        GraphLangParser.IfStatementContext ifCtx = ctx.ifStatement();
        String cond = visit(ifCtx.expr());
        StringBuilder out = new StringBuilder();
        out.append("if (").append(cond).append(") {\n");
        out.append(indentBlock(visit(ifCtx.block(0))));
        out.append("}");
        if (ifCtx.ELSE() != null) {
            out.append(" else {\n");
            out.append(indentBlock(visit(ifCtx.block(1))));
            out.append("}");
        }
        return out.toString();
    }

    @Override
    public String visitForEachStmt_(GraphLangParser.ForEachStmt_Context ctx) {
        GraphLangParser.ForEachStatementContext forCtx = ctx.forEachStatement();
        GraphLangType declaredType = resolveTypeKeyword(forCtx.type());
        String iterVar = forCtx.ID().getText();
        String expr = visit(forCtx.expr());
        String nodesArr = fresh("nodesarr");
        String cnt = fresh("cnt");
        String idx = fresh("i");
        StringBuilder out = new StringBuilder();
        out.append(String.format("int %s = 0;\n", cnt));
        out.append(String.format("int* %s = graph_get_nodes(%s, &%s);\n", nodesArr, expr, cnt));

        scopes.peek().put(iterVar, declaredType);
        iteratorVars.add(iterVar);

        out.append(String.format("for (int %s = 0; %s < %s; ++%s) {\n", idx, idx, cnt, idx));
        out.append(String.format("    %s %s = %s[%s];\n", cType(declaredType), iterVar, nodesArr, idx));
        String body = visit(forCtx.block());
        out.append(indentBlock(body, 1));
        out.append("}\n");
        out.append("free(").append(nodesArr).append(");\n");

        scopes.peek().remove(iterVar);
        iteratorVars.remove(iterVar);

        return out.toString();
    }

    @Override
    public String visitSwitchStmt_(GraphLangParser.SwitchStmt_Context ctx) {
        GraphLangParser.SwitchStatementContext switchCtx = ctx.switchStatement();
        String subject = visit(switchCtx.expr());
        StringBuilder out = new StringBuilder();
        boolean firstCase = true;
        for (GraphLangParser.SwitchBlockContext blockCtx : switchCtx.switchBlock()) {
            if (blockCtx.CASE() != null) {
                String caseExpr = visit(blockCtx.caseLabel());
                if (firstCase) {
                    out.append("if (").append(subject).append(" == ").append(caseExpr).append(") {\n");
                    firstCase = false;
                } else {
                    out.append(" else if (").append(subject).append(" == ").append(caseExpr).append(") {\n");
                }
                for (GraphLangParser.StatementContext s : blockCtx.statement()) {
                    out.append(indentBlock(visit(s)));
                }
                out.append("}\n");
            } else {
                for (GraphLangParser.StatementContext s : blockCtx.statement()) {
                    out.append(visit(s)).append("\n");
                }
            }
        }
        return out.toString();
    }

    @Override
    public String visitCaseLabel(GraphLangParser.CaseLabelContext ctx) {
        if (ctx.ID() != null) {
            return ctx.ID().getText();
        }
        if (ctx.STRING() != null) {
            return ctx.STRING().getText();
        }
        return ctx.INT().getText();
    }


    @Override
    public String visitPrintStmt_(GraphLangParser.PrintStmt_Context ctx) {
        GraphLangParser.PrintStatementContext printCtx = ctx.printStatement();
        StringBuilder out = new StringBuilder();

        List<GraphLangParser.ExprContext> args = new ArrayList<>();
        if (printCtx.argList() != null) {
            args.addAll(printCtx.argList().expr());
        }

        for (int ai = 0; ai < args.size(); ++ai) {
            GraphLangParser.ExprContext exprCtx = args.get(ai);
            String e = visit(exprCtx);
            GraphLangType t = guessExprType(exprCtx);

            Optional<String> maybeId = extractSimpleIdentifier(e);
            if (maybeId.isPresent()) {
                GraphLangType symType = lookupType(maybeId.get()).orElse(GraphLangType.UNKNOWN);
                if (symType != GraphLangType.UNKNOWN) t = symType;
            }

            if (e != null) {
                if (e.contains("graph_has_node(") || e.contains(".hasNode(") || e.contains("hasNode(")) {
                    t = GraphLangType.BOOLEAN;
                }
                if (e.startsWith("BFS(") || e.startsWith("DFS(")) {
                    t = GraphLangType.VOID;
                }
                if (t == GraphLangType.UNKNOWN && (e.contains("graph_add_") || e.contains("graph_create(") || e.contains("graph_"))) {
                    t = GraphLangType.GRAPH;
                }
                if (t == GraphLangType.UNKNOWN && e.contains("arc_create(")) {
                    t = GraphLangType.ARC;
                }
                if (t == GraphLangType.UNKNOWN && (e.contains("(int[]") || e.contains("int[]"))) {
                    t = GraphLangType.NODE_GROUP;
                }
            }

            boolean handled = false;
            if (maybeId.isPresent() && t == GraphLangType.GRAPH && ai + 1 < args.size()) {
                GraphLangParser.ExprContext nextExpr = args.get(ai + 1);
                String nextCode = visit(nextExpr);
                if (nextCode != null && nextCode.equals("\"%d\"")) {
                    out.append("print_graph(").append(e).append(");\n");
                    handled = true;
                    ai++; 
                    continue;
                }
            }
            if (handled) continue;

            if (maybeId.isPresent() && (t == GraphLangType.NODE || t == GraphLangType.ARC)) {
                String varName = maybeId.get();

                if (t == GraphLangType.NODE && iteratorVars.contains(varName)) {
                    out.append("print_node_name(").append(varName).append(");\n");
                } else {

                    out.append("printf(\"").append(escapeCString(varName)).append("\");\n");
                }
                continue;
            }

            if (t == GraphLangType.STRING) {
                out.append("print_str(").append(e).append(");\n");
            } else if (t == GraphLangType.INT || t == GraphLangType.NODE) {
                out.append("printf(\"%d\\n\", ").append(e).append(");\n");
            } else if (t == GraphLangType.BOOLEAN) {
                out.append("printf(\"%d\\n\", ").append(e).append(");\n");
            } else if (t == GraphLangType.FLOAT) {
                out.append("printf(\"%f\\n\", ").append(e).append(");\n");
            } else if (t == GraphLangType.GRAPH) {
                if (maybeId.isPresent()) {
                    out.append("printf(\"").append(escapeCString(maybeId.get())).append("\");\n");
                } else {
                    out.append("print_graph(").append(e).append(");\n");
                }
            } else if (t == GraphLangType.ARC) {
                out.append("print_arc(").append(e).append(");\n");
            } else if (t == GraphLangType.NODE_GROUP) {
                Optional<String> maybePtr = extractSimpleIdentifier(e);
                if (maybePtr.isPresent() && nodeGroupCountVar.containsKey(maybePtr.get())) {
                    String cntVar = nodeGroupCountVar.get(maybePtr.get());
                    out.append("print_node_group(").append(e).append(", ").append(cntVar).append(");\n");
                } else {
                    int count = countNodeGroup(exprCtx);
                    out.append("print_node_group(").append(e).append(", ").append(count).append(");\n");
                }
            } else if (t == GraphLangType.VOID) {
                out.append("/* void */\n");
            } else {
                out.append("print_any((void*) (long) (").append(e).append("));\n");
            }
        }

        if (args.isEmpty()) out.append("printf(\"\\n\");\n");

        return out.toString();
    }


    @Override
    public String visitPrimaryExpr_(GraphLangParser.PrimaryExpr_Context ctx) {
        return visit(ctx.getChild(0));
    }

    @Override
    public String visitInt_(GraphLangParser.Int_Context ctx) {
        return ctx.INT().getText();
    }

    @Override
    public String visitFloat_(GraphLangParser.Float_Context ctx) {
        return ctx.FLOAT().getText();
    }

    @Override
    public String visitString_(GraphLangParser.String_Context ctx) {
        return ctx.STRING().getText();
    }

    @Override
    public String visitArcLiteral_(GraphLangParser.ArcLiteral_Context ctx) {

        for (int i = 0; i < ctx.getChildCount(); i++) {
            ParseTree ch = ctx.getChild(i);
            if (ch instanceof GraphLangParser.ArcLiteralContext) {
                GraphLangParser.ArcLiteralContext al = (GraphLangParser.ArcLiteralContext) ch;
                return String.format("arc_create(%s, %s)", al.ID(0).getText(), al.ID(1).getText());
            }
        }
        if (ctx.arcLiteral() != null) {
            GraphLangParser.ArcLiteralContext al = ctx.arcLiteral();
            return String.format("arc_create(%s, %s)", al.ID(0).getText(), al.ID(1).getText());
        }
        return "arc_create(0,0)";
    }

    @Override
    public String visitFuncCall_(GraphLangParser.FuncCall_Context ctx) {
        return visit(ctx.getChild(0));
    }

    @Override
    public String visitMemberAccess_(GraphLangParser.MemberAccess_Context ctx) {
        return visit(ctx.getChild(0));
    }

    @Override
    public String visitId_(GraphLangParser.Id_Context ctx) {
        return ctx.ID().getText();
    }

    @Override
    public String visitNodeGroup_(GraphLangParser.NodeGroup_Context ctx) {
        List<String> ids = collectIds(ctx);
        StringBuilder arr = new StringBuilder();
        arr.append("(int[]){");
        for (int i = 0; i < ids.size(); i++) {
            if (i > 0) arr.append(", ");
            arr.append(ids.get(i));
        }
        arr.append("}");
        return arr.toString();
    }

    @Override
    public String visitBracketsExprOrGroup_(GraphLangParser.BracketsExprOrGroup_Context ctx) {
        for (int i = 0; i < ctx.getChildCount(); i++) {
            ParseTree ch = ctx.getChild(i);
            if (ch instanceof GraphLangParser.NodeGroupInnerContext) return visit(ch);
            if (ch instanceof GraphLangParser.ExprContext) return visit(ch);
        }
        return "";
    }

    @Override
    public String visitNodeGroupInner(GraphLangParser.NodeGroupInnerContext ctx) {
        List<String> ids = new ArrayList<>();
        for (TerminalNode idNode : ctx.ID()) ids.add(idNode.getText());
        StringBuilder arr = new StringBuilder();
        arr.append("(int[]){");
        for (int i = 0; i < ids.size(); i++) {
            if (i > 0) arr.append(", ");
            arr.append(ids.get(i));
        }
        arr.append("}");
        return arr.toString();
    }

    @Override
    public String visitArcLiteral(GraphLangParser.ArcLiteralContext ctx) {
        return String.format("arc_create(%s, %s)", ctx.ID(0).getText(), ctx.ID(1).getText());
    }

    @Override
    public String visitFuncCall(GraphLangParser.FuncCallContext ctx) {
        String name = ctx.ID().getText();
        List<String> args = new ArrayList<>();
        if (ctx.argList() != null) {
            for (GraphLangParser.ExprContext e : ctx.argList().expr()) {
                args.add(visit(e));
            }
        }

        if (name.equals("BFS") || name.equals("DFS")) {
            if (args.size() < 2) {
                return name + "(" + String.join(", ", args) + ")";
            }
            String gExpr = args.get(0);
            String startExpr = args.get(1);

            String tmpCnt = fresh(name.toLowerCase() + "_cnt");
            String tmpNodes = fresh(name.toLowerCase() + "_nodes");

            String stmt = String.format("int %s = 0;\nint* %s = %s_nodes(%s, %s, &%s);",
                    tmpCnt, tmpNodes, name, gExpr, startExpr, tmpCnt);
            appendStatement(stmt);

            nodeGroupCountVar.put(tmpNodes, tmpCnt);

            return tmpNodes;
        }

        return "fn_" + name + "(" + String.join(", ", args) + ")";
    }

    @Override
    public String visitMemberAccess(GraphLangParser.MemberAccessContext ctx) {
        String owner = visit(ctx.accessStart());
        for (int i = 0; i < ctx.getChildCount(); i++) {
            ParseTree ch = ctx.getChild(i);
            if (ch instanceof GraphLangParser.AccessElementContext) {
                GraphLangParser.AccessElementContext el = (GraphLangParser.AccessElementContext) ch;
                String member = el.ID().getText();
                List<String> args = new ArrayList<>();
                if (el.argList() != null) {
                    for (GraphLangParser.ExprContext e : el.argList().expr()) {
                        args.add(visit(e));
                    }
                }
                if (member.equals("hasNode")) {
                    owner = "graph_has_node(" + owner + ", " + String.join(", ", args) + ")";
                } else {
                    owner = owner + "_" + member + "(" + owner + (args.isEmpty() ? "" : ", " + String.join(", ", args)) + ")";
                }
            }
        }
        return owner;
    }

    @Override
    public String visitAccessStart(GraphLangParser.AccessStartContext ctx) {
        return ctx.ID().getText();
    }


    @Override
    public String visitMulDivExpr_(GraphLangParser.MulDivExpr_Context ctx) {
        String left = visit(ctx.expr(0));
        String right = visit(ctx.expr(1));
        String op = ctx.getChild(1).getText();

        GraphLangType lt = inferType(ctx.expr(0));
        GraphLangType rt = inferType(ctx.expr(1));

        Optional<String> leftId = extractSimpleIdentifier(left);
        if (leftId.isPresent()) lt = lookupType(leftId.get()).orElse(lt);
        Optional<String> rightId = extractSimpleIdentifier(right);
        if (rightId.isPresent()) rt = lookupType(rightId.get()).orElse(rt);

        if (right.contains("(int[]") || right.contains("int[]")) rt = GraphLangType.NODE_GROUP;
        if (right.contains("arc_create(")) rt = GraphLangType.ARC;

        if ("*".equals(op) && lt == GraphLangType.GRAPH) {
            if (rt == GraphLangType.NODE) return "graph_add_node(" + left + ", " + right + ")";
            if (rt == GraphLangType.NODE_GROUP) {
                int count = countNodeGroup(ctx.expr(1));
                return "graph_add_nodes(" + left + ", " + right + ", " + count + ")";
            }
        }
        if ("/".equals(op) && lt == GraphLangType.GRAPH && rt == GraphLangType.NODE) {
            return "graph_remove_node(" + left + ", " + right + ")";
        }
        return "(" + left + " " + op + " " + right + ")";
    }

    @Override
    public String visitAddSubExpr_(GraphLangParser.AddSubExpr_Context ctx) {
        String left = visit(ctx.expr(0));
        String right = visit(ctx.expr(1));
        String op = ctx.getChild(1).getText();

        GraphLangType lt = inferType(ctx.expr(0));
        GraphLangType rt = inferType(ctx.expr(1));

        Optional<String> leftId = extractSimpleIdentifier(left);
        if (leftId.isPresent()) lt = lookupType(leftId.get()).orElse(lt);
        Optional<String> rightId = extractSimpleIdentifier(right);
        if (rightId.isPresent()) rt = lookupType(rightId.get()).orElse(rt);

        if (right.contains("(int[]") || right.contains("int[]")) rt = GraphLangType.NODE_GROUP;
        if (right.contains("arc_create(")) rt = GraphLangType.ARC;

        boolean leftIsGraph = lt == GraphLangType.GRAPH
                || (left != null && (left.contains("graph_add_") || left.contains("graph_remove_") || left.contains("graph_")))
                || (leftId.isPresent() && lookupType(leftId.get()).orElse(GraphLangType.UNKNOWN) == GraphLangType.GRAPH);

        boolean rightIsArc = rt == GraphLangType.ARC || (right != null && right.contains("arc_create("));

        if ("+".equals(op) && leftIsGraph && rightIsArc) return "graph_add_arc(" + left + ", " + right + ")";
        if ("-".equals(op) && leftIsGraph && rightIsArc) return "graph_remove_arc(" + left + ", " + right + ")";

        if ("+".equals(op) && (lt == GraphLangType.STRING || rt == GraphLangType.STRING)) return "str_concat(" + left + ", " + right + ")";

        return "(" + left + " " + op + " " + right + ")";
    }


    private GraphLangType resolveTypeKeyword(GraphLangParser.TypeContext ctx) {
        String text = ctx.getText();
        return switch (text) {
            case "node" -> GraphLangType.NODE;
            case "graph" -> GraphLangType.GRAPH;
            case "arc" -> GraphLangType.ARC;
            default -> throw new RuntimeException("Unsupported type: " + text);
        };
    }

    private GraphLangType inferType(ParseTree expr) {
        if (expr instanceof GraphLangParser.ExprContext) {
            GraphLangParser.ExprContext e = (GraphLangParser.ExprContext) expr;

            if (e.getChildCount() >= 3) {
                ParseTree left = e.getChild(0);
                ParseTree right = e.getChild(e.getChildCount() - 1);
                String op = e.getChild(1).getText();

                GraphLangType lt = inferType(left);
                GraphLangType rt = inferType(right);

                if ((op.equals("+") || op.equals("-")) && lt == GraphLangType.GRAPH && rt == GraphLangType.ARC) {
                    return GraphLangType.GRAPH;
                }
                if ((op.equals("*") || op.equals("/")) && lt == GraphLangType.GRAPH &&
                        (rt == GraphLangType.NODE || rt == GraphLangType.NODE_GROUP)) {
                    return GraphLangType.GRAPH;
                }

                if (lt == GraphLangType.FLOAT || rt == GraphLangType.FLOAT) return GraphLangType.FLOAT;
                if (lt == GraphLangType.INT || rt == GraphLangType.INT) return GraphLangType.INT;
            }

            if (e.getChildCount() == 1) {
                ParseTree c = e.getChild(0);
                if (c instanceof GraphLangParser.PrimaryContext) {
                    GraphLangParser.PrimaryContext p = (GraphLangParser.PrimaryContext) c;
                    if (p.getChildCount() == 1) {
                        ParseTree pc = p.getChild(0);
                        if (pc instanceof TerminalNode) {
                            int tt = ((TerminalNode) pc).getSymbol().getType();
                            if (tt == GraphLangParser.INT) return GraphLangType.INT;
                            if (tt == GraphLangParser.FLOAT) return GraphLangType.FLOAT;
                            if (tt == GraphLangParser.STRING) return GraphLangType.STRING;
                            if (tt == GraphLangParser.ID) {
                                String id = ((TerminalNode) pc).getText();
                                return lookupType(id).orElse(GraphLangType.UNKNOWN);
                            }
                        } else if (pc instanceof GraphLangParser.ArcLiteralContext) {
                            return GraphLangType.ARC;
                        } else if (pc instanceof GraphLangParser.NodeGroupContext) {
                            return GraphLangType.NODE_GROUP;
                        } else if (pc instanceof GraphLangParser.FuncCallContext) {
                            GraphLangParser.FuncCallContext fc = (GraphLangParser.FuncCallContext) pc;
                            String id = fc.ID().getText();
                            if (id.equals("BFS") || id.equals("DFS") || id.equals("BFS_nodes") || id.equals("DFS_nodes")) return GraphLangType.NODE_GROUP;
                            return GraphLangType.UNKNOWN;
                        } else if (pc instanceof GraphLangParser.MemberAccessContext) {
                            GraphLangParser.MemberAccessContext mac = (GraphLangParser.MemberAccessContext) pc;
                            for (int i = 0; i < mac.getChildCount(); i++) {
                                ParseTree ch = mac.getChild(i);
                                if (ch instanceof GraphLangParser.AccessElementContext) {
                                    GraphLangParser.AccessElementContext ae = (GraphLangParser.AccessElementContext) ch;
                                    if (ae.ID().getText().equals("hasNode")) return GraphLangType.BOOLEAN;
                                }
                            }
                        } else if (pc instanceof GraphLangParser.Id_Context) {
                            String id = ((GraphLangParser.Id_Context) pc).ID().getText();
                            return lookupType(id).orElse(GraphLangType.UNKNOWN);
                        }
                    }
                } else if (c instanceof GraphLangParser.NodeGroupContext) {
                    return GraphLangType.NODE_GROUP;
                }
            }
        } else if (expr instanceof GraphLangParser.PrimaryContext) {
            GraphLangParser.PrimaryContext p = (GraphLangParser.PrimaryContext) expr;
            if (p.getChildCount() == 1) {
                ParseTree pc = p.getChild(0);
                if (pc instanceof TerminalNode) {
                    int tt = ((TerminalNode) pc).getSymbol().getType();
                    if (tt == GraphLangParser.INT) return GraphLangType.INT;
                    if (tt == GraphLangParser.FLOAT) return GraphLangType.FLOAT;
                    if (tt == GraphLangParser.STRING) return GraphLangType.STRING;
                    if (tt == GraphLangParser.ID) {
                        String id = ((TerminalNode) pc).getText();
                        return lookupType(id).orElse(GraphLangType.UNKNOWN);
                    }
                } else if (pc instanceof GraphLangParser.NodeGroupContext) {
                    return GraphLangType.NODE_GROUP;
                } else if (pc instanceof GraphLangParser.ArcLiteralContext) {
                    return GraphLangType.ARC;
                }
            }
        } else if (expr instanceof GraphLangParser.NodeGroupContext) {
            return GraphLangType.NODE_GROUP;
        } else if (expr instanceof GraphLangParser.ArcLiteralContext) {
            return GraphLangType.ARC;
        } else if (expr instanceof GraphLangParser.Id_Context) {
            return lookupType(((GraphLangParser.Id_Context) expr).ID().getText()).orElse(GraphLangType.UNKNOWN);
        }
        return GraphLangType.UNKNOWN;
    }

    private GraphLangType guessExprType(ParseTree expr) {
        return inferType(expr);
    }

    private Optional<String> extractSimpleIdentifier(String code) {
        if (code == null) return Optional.empty();
        String t = code.strip();
        while (t.startsWith("(") && t.endsWith(")")) {
            t = t.substring(1, t.length() - 1).strip();
        }
        if (IDENT_RE.matcher(t).matches()) return Optional.of(t);
        return Optional.empty();
    }

    private int countNodeGroup(ParseTree nodeGroupExpr) {
        int cnt = 0;
        Deque<ParseTree> dq = new ArrayDeque<>();
        dq.add(nodeGroupExpr);
        while (!dq.isEmpty()) {
            ParseTree p = dq.removeFirst();
            for (int i = 0; i < p.getChildCount(); i++) {
                ParseTree ch = p.getChild(i);
                if (ch instanceof TerminalNode) {
                    if (((TerminalNode) ch).getSymbol().getType() == GraphLangParser.ID) cnt++;
                } else {
                    dq.add(ch);
                }
            }
        }
        return Math.max(cnt, 1);
    }

    private List<String> collectIds(ParseTree root) {
        List<String> ids = new ArrayList<>();
        Deque<ParseTree> dq = new ArrayDeque<>();
        dq.add(root);
        while (!dq.isEmpty()) {
            ParseTree p = dq.removeFirst();
            for (int i = 0; i < p.getChildCount(); i++) {
                ParseTree ch = p.getChild(i);
                if (ch instanceof TerminalNode) {
                    if (((TerminalNode) ch).getSymbol().getType() == GraphLangParser.ID) {
                        ids.add(((TerminalNode) ch).getText());
                    }
                } else {
                    dq.add(ch);
                }
            }
        }
        return ids;
    }

    private String indentBlock(String block) {
        return indentBlock(block, 1);
    }

    private String indentBlock(String block, int levels) {
        if (block == null || block.isBlank()) return "";
        String[] lines = block.split("\n");
        StringBuilder out = new StringBuilder();
        String pad = "    ".repeat(levels);
        for (String l : lines) {
            if (l.isBlank()) continue;
            out.append(pad).append(l).append("\n");
        }
        return out.toString();
    }

    private String escapeCString(String s) {
        return s.replace("\\", "\\\\").replace("\"", "\\\"");
    }
}
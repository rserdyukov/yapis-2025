package graphlang.semantics;

import graphlang.GraphLangBaseVisitor;
import graphlang.GraphLangParser;
import graphlang.semantics.functions.FunctionSignature;
import graphlang.semantics.symbols.FunctionSymbol;
import graphlang.semantics.symbols.Symbol;
import graphlang.semantics.symbols.VariableSymbol;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.TerminalNode;

import java.util.*;

public final class GraphLangSemanticAnalyzer extends GraphLangBaseVisitor<GraphLangType> {

    private final Scope globalScope = new Scope(null);
    private Scope currentScope = globalScope;
    private final Map<String, FunctionSymbol> functions = new LinkedHashMap<>();

    private static final Map<GraphLangType, Map<String, FunctionSignature>> BUILT_IN_MEMBERS = Map.of(
            GraphLangType.GRAPH, Map.of(
                    "hasNode", new FunctionSignature(GraphLangType.BOOLEAN, List.of(GraphLangType.NODE))
            )
    );

    public GraphLangSemanticAnalyzer() {
        registerBuiltInFunctions();
    }

    private void registerBuiltInFunctions() {
        FunctionSymbol bfs = new FunctionSymbol(
                "BFS",
                GraphLangType.NODE_GROUP,
                List.of(
                        new VariableSymbol("graph", GraphLangType.GRAPH),
                        new VariableSymbol("start", GraphLangType.NODE)
                )
        );

        FunctionSymbol dfs = new FunctionSymbol(
                "DFS",
                GraphLangType.NODE_GROUP,
                List.of(
                        new VariableSymbol("graph", GraphLangType.GRAPH),
                        new VariableSymbol("start", GraphLangType.NODE)
                )
        );

        defineFunction(bfs);
        defineFunction(dfs);
    }

    private void defineFunction(FunctionSymbol function) {
        if (functions.containsKey(function.name())) {
            throw new SemanticException("Function '%s' already defined".formatted(function.name()));
        }
        functions.put(function.name(), function);
    }

    @Override
    public GraphLangType visitProgram(GraphLangParser.ProgramContext ctx) {
        for (GraphLangParser.FunctionDeclarationContext functionCtx : ctx.functionDeclaration()) {
            predeclareFunction(functionCtx);
        }

        for (int i = 0; i < ctx.getChildCount(); i++) {
            ParseTree child = ctx.getChild(i);
            if (child instanceof GraphLangParser.FunctionDeclarationContext fnCtx) {
                visitFunctionDeclaration(fnCtx);
            } else {
                visit(child);
            }
        }

        return GraphLangType.VOID;
    }

    private void predeclareFunction(GraphLangParser.FunctionDeclarationContext ctx) {
        String name = ctx.ID().getText();
        List<VariableSymbol> params = extractParams(ctx.functionParamList());
        FunctionSymbol fn = new FunctionSymbol(name, GraphLangType.VOID, params);
        defineFunction(fn);
    }

    private List<VariableSymbol> extractParams(GraphLangParser.FunctionParamListContext ctx) {
        if (ctx == null) {
            return List.of();
        }
        List<VariableSymbol> params = new ArrayList<>();
        for (GraphLangParser.FunctionParamContext paramCtx : ctx.functionParam()) {
            GraphLangType type = resolveTypeKeyword(paramCtx.type());
            String name = paramCtx.ID().getText();
            params.add(new VariableSymbol(name, type));
        }
        return params;
    }

    private GraphLangType resolveTypeKeyword(GraphLangParser.TypeContext ctx) {
        String text = ctx.getText();
        return switch (text) {
            case "node" -> GraphLangType.NODE;
            case "graph" -> GraphLangType.GRAPH;
            case "arc" -> GraphLangType.ARC;
            default -> throw error(ctx, "Unsupported type '%s'".formatted(text));
        };
    }

    @Override
    public GraphLangType visitFunctionDeclaration(GraphLangParser.FunctionDeclarationContext ctx) {
        FunctionSymbol fn = functions.get(ctx.ID().getText());
        Scope previousScope = currentScope;
        currentScope = new Scope(previousScope);

        for (VariableSymbol param : fn.parameters()) {
            currentScope.define(param);
        }

        visit(ctx.block());

        currentScope = previousScope;
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitNodeDecl(GraphLangParser.NodeDeclContext ctx) {
        declareVariable(ctx.ID(), GraphLangType.NODE);
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitArcDecl(GraphLangParser.ArcDeclContext ctx) {
        visit(ctx.arcLiteral());
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitGraphDecl(GraphLangParser.GraphDeclContext ctx) {
        declareVariable(ctx.ID(), GraphLangType.GRAPH);
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitVarDeclStmt_(GraphLangParser.VarDeclStmt_Context ctx) {
        GraphLangParser.VarDeclarationStatementContext decl = ctx.varDeclarationStatement();
        if (decl.NODE() != null) {
            declareVariable(decl.ID(), GraphLangType.NODE);
        } else {
            declareVariable(decl.ID(), GraphLangType.GRAPH);
        }
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitArcDeclStmt_(GraphLangParser.ArcDeclStmt_Context ctx) {
        visit(ctx.arcDeclarationStatement().arcLiteral());
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitAssignStmt_(GraphLangParser.AssignStmt_Context ctx) {
        GraphLangParser.AssignmentStatementContext assign = ctx.assignmentStatement();
        GraphLangType targetType;
        if (assign.ID() != null) {
            VariableSymbol variable = requireVariable(assign.ID());
            targetType = variable.type();
        } else {
            targetType = visit(assign.memberAccess());
        }
        GraphLangType valueType = visit(assign.expr());
        if (!isAssignable(targetType, valueType)) {
            throw error(assign, "Cannot assign value of type %s to %s".formatted(valueType, targetType));
        }
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitExprStmt_(GraphLangParser.ExprStmt_Context ctx) {
        visit(ctx.exprStatement().expr());
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitIfStmt_(GraphLangParser.IfStmt_Context ctx) {
        GraphLangParser.IfStatementContext ifCtx = ctx.ifStatement();
        GraphLangType conditionType = visit(ifCtx.expr());
        if (conditionType != GraphLangType.BOOLEAN) {
            throw error(ifCtx, "If condition must be boolean");
        }
        visit(ifCtx.block(0));
        if (ifCtx.ELSE() != null) {
            visit(ifCtx.block(1));
        }
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitForEachStmt_(GraphLangParser.ForEachStmt_Context ctx) {
        GraphLangParser.ForEachStatementContext forCtx = ctx.forEachStatement();
        GraphLangType declaredType = resolveTypeKeyword(forCtx.type());
        GraphLangType iterableType = visit(forCtx.expr());

        if (declaredType == GraphLangType.NODE && iterableType == GraphLangType.GRAPH) {
        } else {
            throw error(forCtx, "Cannot iterate '%s' over expression of type %s"
                    .formatted(declaredType, iterableType));
        }

        Scope previousScope = currentScope;
        currentScope = new Scope(previousScope);
        declareVariable(forCtx.ID(), declaredType);
        visit(forCtx.block());
        currentScope = previousScope;
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitSwitchStmt_(GraphLangParser.SwitchStmt_Context ctx) {
        GraphLangParser.SwitchStatementContext switchCtx = ctx.switchStatement();
        GraphLangType subjectType = visit(switchCtx.expr());

        Scope previousScope = currentScope;
        currentScope = new Scope(previousScope);

        for (GraphLangParser.SwitchBlockContext blockCtx : switchCtx.switchBlock()) {
            if (blockCtx.CASE() != null) {
                GraphLangType caseType = visit(blockCtx.caseLabel());
                if (!caseCompatible(subjectType, caseType)) {
                    throw error(blockCtx, "Case label type %s is not compatible with %s"
                            .formatted(caseType, subjectType));
                }
            }
            Scope caseScope = new Scope(currentScope);
            Scope saved = currentScope;
            currentScope = caseScope;
            for (GraphLangParser.StatementContext statementContext : blockCtx.statement()) {
                visit(statementContext);
            }
            currentScope = saved;
        }

        currentScope = previousScope;
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitCaseLabel(GraphLangParser.CaseLabelContext ctx) {
        if (ctx.ID() != null) {
            VariableSymbol symbol = requireVariable(ctx.ID());
            return symbol.type();
        }
        if (ctx.STRING() != null) {
            return GraphLangType.STRING;
        }
        return GraphLangType.INT;
    }

    @Override
    public GraphLangType visitPrintStmt_(GraphLangParser.PrintStmt_Context ctx) {
        GraphLangParser.PrintStatementContext printCtx = ctx.printStatement();
        if (printCtx.argList() != null) {
            for (GraphLangParser.ExprContext exprContext : printCtx.argList().expr()) {
                visit(exprContext);
            }
        }
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitBlock(GraphLangParser.BlockContext ctx) {
        Scope previousScope = currentScope;
        currentScope = new Scope(previousScope);
        for (GraphLangParser.StatementContext statementContext : ctx.statement()) {
            visit(statementContext);
        }
        currentScope = previousScope;
        return GraphLangType.VOID;
    }

    @Override
    public GraphLangType visitPrimaryExpr_(GraphLangParser.PrimaryExpr_Context ctx) {
        return visit(ctx.primary());
    }

    @Override
    public GraphLangType visitInt_(GraphLangParser.Int_Context ctx) {
        return GraphLangType.INT;
    }

    @Override
    public GraphLangType visitFloat_(GraphLangParser.Float_Context ctx) {
        return GraphLangType.FLOAT;
    }

    @Override
    public GraphLangType visitString_(GraphLangParser.String_Context ctx) {
        return GraphLangType.STRING;
    }

    @Override
    public GraphLangType visitArcLiteral_(GraphLangParser.ArcLiteral_Context ctx) {
        return visit(ctx.arcLiteral());
    }

    @Override
    public GraphLangType visitFuncCall_(GraphLangParser.FuncCall_Context ctx) {
        return visit(ctx.funcCall());
    }

    @Override
    public GraphLangType visitMemberAccess_(GraphLangParser.MemberAccess_Context ctx) {
        return visit(ctx.memberAccess());
    }

    @Override
    public GraphLangType visitId_(GraphLangParser.Id_Context ctx) {
        VariableSymbol symbol = requireVariable(ctx.ID());
        return symbol.type();
    }

    @Override
    public GraphLangType visitNodeGroup_(GraphLangParser.NodeGroup_Context ctx) {
        visit(ctx.nodeGroup());
        return GraphLangType.NODE_GROUP;
    }

    @Override
    public GraphLangType visitBracketsExprOrGroup_(GraphLangParser.BracketsExprOrGroup_Context ctx) {
        if (ctx.nodeGroupInner() != null) {
            visit(ctx.nodeGroupInner());
            return GraphLangType.NODE_GROUP;
        }
        return visit(ctx.expr());
    }

    @Override
    public GraphLangType visitNodeGroup(GraphLangParser.NodeGroupContext ctx) {
        visit(ctx.nodeGroupInner());
        return GraphLangType.NODE_GROUP;
    }

    @Override
    public GraphLangType visitNodeGroupInner(GraphLangParser.NodeGroupInnerContext ctx) {
        for (TerminalNode idNode : ctx.ID()) {
            VariableSymbol variable = requireVariable(idNode);
            if (variable.type() != GraphLangType.NODE) {
                throw error(ctx, "Identifier '%s' in node group is not a node".formatted(variable.name()));
            }
        }
        return GraphLangType.NODE_GROUP;
    }

    @Override
    public GraphLangType visitArcLiteral(GraphLangParser.ArcLiteralContext ctx) {
        VariableSymbol from = requireVariable(ctx.ID(0));
        VariableSymbol to = requireVariable(ctx.ID(1));

        if (from.type() != GraphLangType.NODE || to.type() != GraphLangType.NODE) {
            throw error(ctx, "Arc literal requires node identifiers");
        }
        return GraphLangType.ARC;
    }

    @Override
    public GraphLangType visitFuncCall(GraphLangParser.FuncCallContext ctx) {
        String name = ctx.ID().getText();
        FunctionSymbol function = functions.get(name);
        if (function == null) {
            throw error(ctx, "Unknown function '%s'".formatted(name));
        }

        List<GraphLangParser.ExprContext> argContexts = ctx.argList() == null
                ? List.of()
                : ctx.argList().expr();

        if (argContexts.size() != function.parameters().size()) {
            throw error(ctx, "Function '%s' expects %d arguments, got %d"
                    .formatted(name, function.parameters().size(), argContexts.size()));
        }

        for (int i = 0; i < argContexts.size(); i++) {
            GraphLangType expected = function.parameters().get(i).type();
            GraphLangType actual = visit(argContexts.get(i));
            if (!isAssignable(expected, actual)) {
                throw error(argContexts.get(i), "Argument %d of '%s' should be %s but got %s"
                        .formatted(i + 1, name, expected, actual));
            }
        }

        return function.returnType();
    }

    @Override
    public GraphLangType visitMemberAccess(GraphLangParser.MemberAccessContext ctx) {
        GraphLangType currentType = visit(ctx.accessStart());
        for (GraphLangParser.AccessElementContext elementContext : ctx.accessElement()) {
            currentType = resolveAccessElementType(currentType, elementContext);
        }
        return currentType;
    }

    @Override
    public GraphLangType visitAccessStart(GraphLangParser.AccessStartContext ctx) {
        VariableSymbol symbol = requireVariable(ctx.ID());
        return symbol.type();
    }

    private GraphLangType resolveAccessElementType(GraphLangType ownerType, GraphLangParser.AccessElementContext ctx) {
        Map<String, FunctionSignature> members = BUILT_IN_MEMBERS.get(ownerType);
        if (members == null) {
            throw error(ctx, "Type %s has no members".formatted(ownerType));
        }

        String memberName = ctx.ID().getText();
        FunctionSignature signature = members.get(memberName);
        if (signature == null) {
            throw error(ctx, "Type %s has no member '%s'".formatted(ownerType, memberName));
        }

        List<GraphLangParser.ExprContext> arguments = ctx.argList() == null
                ? List.of()
                : ctx.argList().expr();

        if (arguments.size() != signature.parameterTypes().size()) {
            throw error(ctx, "Member '%s' of %s expects %d arguments, got %d"
                    .formatted(memberName, ownerType, signature.parameterTypes().size(), arguments.size()));
        }

        for (int i = 0; i < arguments.size(); i++) {
            GraphLangType expected = signature.parameterTypes().get(i);
            GraphLangType actual = visit(arguments.get(i));
            if (!isAssignable(expected, actual)) {
                throw error(arguments.get(i), "Argument %d for '%s' should be %s but got %s"
                        .formatted(i + 1, memberName, expected, actual));
            }
        }

        return signature.returnType();
    }

    @Override
    public GraphLangType visitMulDivExpr_(GraphLangParser.MulDivExpr_Context ctx) {
        GraphLangType left = visit(ctx.expr(0));
        GraphLangType right = visit(ctx.expr(1));
        TerminalNode operatorNode = (TerminalNode) ctx.getChild(1);
        int tokenType = operatorNode.getSymbol().getType();

        return switch (tokenType) {
            case GraphLangParser.MULT -> checkMult(left, right, ctx);
            case GraphLangParser.DIV -> checkDiv(left, right, ctx);
            default -> throw error(ctx, "Unsupported operator");
        };
    }

    @Override
    public GraphLangType visitAddSubExpr_(GraphLangParser.AddSubExpr_Context ctx) {
        GraphLangType left = visit(ctx.expr(0));
        GraphLangType right = visit(ctx.expr(1));
        TerminalNode operatorNode = (TerminalNode) ctx.getChild(1);
        int tokenType = operatorNode.getSymbol().getType();

        return switch (tokenType) {
            case GraphLangParser.PLUS -> checkPlus(left, right, ctx);
            case GraphLangParser.MINUS -> checkMinus(left, right, ctx);
            default -> throw error(ctx, "Unsupported operator");
        };
    }

    @Override
    public GraphLangType visitCompExpr_(GraphLangParser.CompExpr_Context ctx) {
        GraphLangType left = visit(ctx.expr(0));
        GraphLangType right = visit(ctx.expr(1));
        TerminalNode operatorNode = (TerminalNode) ctx.getChild(1);
        int tokenType = operatorNode.getSymbol().getType();

        return switch (tokenType) {
            case GraphLangParser.EQ, GraphLangParser.NEQ,
                 GraphLangParser.LT, GraphLangParser.LE,
                 GraphLangParser.GT, GraphLangParser.GE -> checkComparison(tokenType, left, right, ctx);
            default -> throw error(ctx, "Unsupported comparison operator");
        };
    }

    @Override
    public GraphLangType visitAndExpr_(GraphLangParser.AndExpr_Context ctx) {
        GraphLangType left = visit(ctx.expr(0));
        GraphLangType right = visit(ctx.expr(1));
        return checkLogical(left, right, ctx);
    }

    @Override
    public GraphLangType visitOrExpr_(GraphLangParser.OrExpr_Context ctx) {
        GraphLangType left = visit(ctx.expr(0));
        GraphLangType right = visit(ctx.expr(1));
        return checkLogical(left, right, ctx);
    }

    private GraphLangType checkPlus(GraphLangType left, GraphLangType right, ParserRuleContext ctx) {
        if (left == GraphLangType.GRAPH && right == GraphLangType.ARC) {
            return GraphLangType.GRAPH;
        }
        if (left == GraphLangType.STRING || right == GraphLangType.STRING) {
            return GraphLangType.STRING;
        }
        if (left == GraphLangType.INT && right == GraphLangType.INT) {
            return GraphLangType.INT;
        }
        if (isNumeric(left) && isNumeric(right)) {
            return promoteNumeric(left, right);
        }
        throw error(ctx, "'+' not defined for %s and %s".formatted(left, right));
    }

    private GraphLangType checkMinus(GraphLangType left, GraphLangType right, ParserRuleContext ctx) {
        if (left == GraphLangType.GRAPH && right == GraphLangType.ARC) {
            return GraphLangType.GRAPH;
        }
        if (isNumeric(left) && isNumeric(right)) {
            return promoteNumeric(left, right);
        }
        throw error(ctx, "'-' not defined for %s and %s".formatted(left, right));
    }

    private GraphLangType checkMult(GraphLangType left, GraphLangType right, ParserRuleContext ctx) {
        if (left == GraphLangType.GRAPH && (right == GraphLangType.NODE || right == GraphLangType.NODE_GROUP)) {
            return GraphLangType.GRAPH;
        }
        if (isNumeric(left) && isNumeric(right)) {
            return promoteNumeric(left, right);
        }
        throw error(ctx, "'*' not defined for %s and %s".formatted(left, right));
    }

    private GraphLangType checkDiv(GraphLangType left, GraphLangType right, ParserRuleContext ctx) {
        if (left == GraphLangType.GRAPH && (right == GraphLangType.NODE || right == GraphLangType.NODE_GROUP)) {
            return GraphLangType.GRAPH;
        }
        if (isNumeric(left) && isNumeric(right)) {
            return GraphLangType.FLOAT;
        }
        throw error(ctx, "'/' not defined for %s and %s".formatted(left, right));
    }

    private GraphLangType checkComparison(int operator, GraphLangType left, GraphLangType right, ParserRuleContext ctx) {
        if (operator == GraphLangParser.EQ || operator == GraphLangParser.NEQ) {
            if (isComparableForEquality(left, right)) {
                return GraphLangType.BOOLEAN;
            }
            throw error(ctx, "Cannot compare %s and %s with equality".formatted(left, right));
        }

        if (isNumeric(left) && isNumeric(right)) {
            return GraphLangType.BOOLEAN;
        }
        throw error(ctx, "Relational comparison not defined for %s and %s".formatted(left, right));
    }

    private GraphLangType checkLogical(GraphLangType left, GraphLangType right, ParserRuleContext ctx) {
        if (left != GraphLangType.BOOLEAN || right != GraphLangType.BOOLEAN) {
            throw error(ctx, "Logical operators require boolean operands");
        }
        return GraphLangType.BOOLEAN;
    }

    private boolean isAssignable(GraphLangType target, GraphLangType value) {
        if (target == value) {
            return true;
        }
        if (target == GraphLangType.FLOAT && value == GraphLangType.INT) {
            return true;
        }
        if (target == GraphLangType.STRING && value != GraphLangType.UNKNOWN) {
            return true;
        }
        return false;
    }

    private boolean isNumeric(GraphLangType type) {
        return type == GraphLangType.INT || type == GraphLangType.FLOAT;
    }

    private GraphLangType promoteNumeric(GraphLangType left, GraphLangType right) {
        if (left == GraphLangType.FLOAT || right == GraphLangType.FLOAT) {
            return GraphLangType.FLOAT;
        }
        return GraphLangType.INT;
    }

    private boolean isComparableForEquality(GraphLangType left, GraphLangType right) {
        if (left == right) {
            return true;
        }
        if (isNumeric(left) && isNumeric(right)) {
            return true;
        }
        return left == GraphLangType.STRING || right == GraphLangType.STRING;
    }

    private boolean caseCompatible(GraphLangType subject, GraphLangType label) {
        if (subject == label) {
            return true;
        }
        if (isNumeric(subject) && isNumeric(label)) {
            return true;
        }
        return false;
    }

    private void declareVariable(TerminalNode idNode, GraphLangType type) {
        if (currentScope.resolveLocal(idNode.getText()).isPresent()) {
            throw error(idNode.getSymbol(), "Variable '%s' already declared in this scope".formatted(idNode.getText()));
        }
        currentScope.define(new VariableSymbol(idNode.getText(), type));
    }

    private VariableSymbol requireVariable(TerminalNode idNode) {
        String name = idNode.getText();
        return requireVariable(name, idNode.getSymbol());
    }

    private VariableSymbol requireVariable(String name, Token token) {
        Optional<Symbol> symbolOptional = currentScope.resolve(name);
        if (symbolOptional.isEmpty()) {
            throw error(token, "Unknown identifier '%s'".formatted(name));
        }
        Symbol symbol = symbolOptional.get();
        if (symbol instanceof VariableSymbol variableSymbol) {
            return variableSymbol;
        }
        throw error(token, "'%s' is not a variable".formatted(name));
    }

    private SemanticException error(ParserRuleContext ctx, String message) {
        Token start = ctx.getStart();
        return error(start, message);
    }

    private SemanticException error(Token token, String message) {
        int line = token.getLine();
        int column = token.getCharPositionInLine();
        return new SemanticException("Semantic error at %d:%d — %s".formatted(line, column, message));
    }
}

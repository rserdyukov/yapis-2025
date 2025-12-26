package org.example;
import org.antlr.v4.runtime.tree.ParseTree;

import java.util.*;

public class CILGenerator extends SetLangBaseVisitor<String> {

    private Map<String, Integer> currentSymbolTable = new HashMap<>();
    private Map<String, Integer> currentArgsTable = new HashMap<>();
    private int nextLocalIndex = 0;
    private StringBuilder allMethodsCode = new StringBuilder();
    private int labelCounter = 0;
    private Stack<String> breakLabels = new Stack<>();

    private String getNextLabel() {
        return "LABEL_" + (labelCounter++);
    }

    private final String OBJ = "class [mscorlib]System.Object";
    private final String RUNTIME_OPS = "class [SetLangRuntime]SetLangRuntime.Ops";
    private final String HASH_SET = "class [System.Core]System.Collections.Generic.HashSet`1<" + OBJ + ">";
    private final String LIST = "class [mscorlib]System.Collections.Generic.List`1<" + OBJ + ">";
    private final String BOX_BOOL = "    box [mscorlib]System.Boolean\n";
    private final String BOX_INT = "    box valuetype [mscorlib]System.Int32\n";

    public String getCIL(ParseTree tree) {
        return visit(tree);
    }

    @Override
    protected String defaultResult() {
        // Вместо null возвращаем пустую строку, чтобы StringBuilder не писал слово "null"
        return "";
    }

    @Override
    protected String aggregateResult(String aggregate, String nextResult) {
        return (aggregate == null ? "" : aggregate) + (nextResult == null ? "" : nextResult);

    }

    @Override
    public String visitProgram(SetLangParser.ProgramContext ctx) {
        StringBuilder mainBody = new StringBuilder();
        currentSymbolTable = new HashMap<>();
        nextLocalIndex = 0;
        collectMainVariables(ctx);

        for (int i = 0; i < ctx.getChildCount(); i++) {
            ParseTree child = ctx.getChild(i);
            if (child instanceof SetLangParser.StatementContext) {
                SetLangParser.StatementContext stmt = (SetLangParser.StatementContext) child;
                if (stmt.functionDeclaration() != null) visit(stmt.functionDeclaration());
                else mainBody.append(visit(stmt));
            } else {
                mainBody.append(visit(child));
            }
        }

        StringBuilder sb = new StringBuilder();
        sb.append(".assembly extern mscorlib { .ver 4:0:0:0 }\n");
        sb.append(".assembly extern System.Core { .publickeytoken = (B7 7A 5C 56 19 34 E0 89) .ver 4:0:0:0 }\n");
        sb.append(".assembly extern SetLangRuntime {}\n");
        sb.append(".assembly SetLang {}\n");
        sb.append(".module SetLang.exe\n\n");
        sb.append(".class public Program extends [mscorlib]System.Object {\n\n");
        sb.append(allMethodsCode.toString());
        sb.append("  .method static void Main() cil managed {\n");
        sb.append("    .entrypoint\n    .maxstack 100\n");

        sb.append("    .locals init (\n");
        int count = Math.max(1, nextLocalIndex);
        for (int i = 0; i < count; i++) {
            sb.append("      [").append(i).append("] ").append(OBJ).append(i < count - 1 ? ",\n" : "\n");
        }
        sb.append("    )\n\n");

        sb.append(mainBody.toString());
        sb.append("    ret\n  }\n}\n");
        return sb.toString();
    }

    @Override
    public String visitIfStatement(SetLangParser.IfStatementContext ctx) {
        String labelElse = getNextLabel();
        String labelEnd = getNextLabel();
        StringBuilder sb = new StringBuilder();
        sb.append(visit(ctx.logicalExpr()));
        sb.append("    call bool ").append(RUNTIME_OPS).append("::ToBool(object)\n");
        sb.append("    brfalse ").append(labelElse).append("\n");
        sb.append(visit(ctx.then_));
        sb.append("    br ").append(labelEnd).append("\n");
        sb.append(labelElse).append(":\n");
        if (ctx.else_ != null) sb.append(visit(ctx.else_));
        sb.append(labelEnd).append(":\n");
        return sb.toString();
    }

    @Override
    public String visitForStatement(SetLangParser.ForStatementContext ctx) {
        String labelStart = getNextLabel();
        String labelEnd = getNextLabel();

        // Имя переменной цикла (например, "i")
        String loopVarName = ctx.ID().getText();
        Integer varIdx = currentSymbolTable.get(loopVarName);

        // На всякий случай проверяем наличие переменной в таблице
        if (varIdx == null) {
            currentSymbolTable.put(loopVarName, nextLocalIndex++);
            varIdx = currentSymbolTable.get(loopVarName);
        }

        // Сохраняем метку выхода для оператора break
        breakLabels.push(labelEnd);
        StringBuilder sb = new StringBuilder();

        SetLangParser.RangeContext range = ctx.range();

        // 1. Инициализация: i = min
        // Здесь range.min — это объект org.antlr.v4.runtime.Token
        sb.append(generateValueFromToken(range.min));
        sb.append("    stloc ").append(varIdx).append(" // init loop var ").append(loopVarName).append("\n");

        sb.append(labelStart).append(":\n");

        // 2. Условие: i < max
        sb.append("    ldloc ").append(varIdx).append("\n");
        sb.append(generateValueFromToken(range.max));
        sb.append("    ldstr \"<\"\n");
        sb.append("    call bool ").append(RUNTIME_OPS).append("::Compare(object, object, string)\n");
        sb.append("    brfalse ").append(labelEnd).append("\n");

        // 3. Тело цикла
        sb.append(visit(ctx.block()));

        // 4. Шаг (инкремент): i = i + step
        sb.append("    ldloc ").append(varIdx).append("\n");
        sb.append(generateValueFromToken(range.step));
        sb.append("    call object ").append(RUNTIME_OPS).append("::Add(object, object)\n");
        sb.append("    stloc ").append(varIdx).append("\n");

        sb.append("    br ").append(labelStart).append("\n");
        sb.append(labelEnd).append(":\n");

        breakLabels.pop();
        return sb.toString();
    }
    private String generateValueFromToken(org.antlr.v4.runtime.Token token) {
        if (token == null) return "    ldnull\n";

        String text = token.getText();
        int type = token.getType();

        // Проверяем тип токена (используем константы из вашего SetLangParser)
        if (type == SetLangParser.INT) {
            return "    ldc.i4 " + text + "\n" +
                    "    box [mscorlib]System.Int32\n";
        }
        else if (type == SetLangParser.ID) {
            // 1. Ищем в аргументах функции
            if (currentArgsTable.containsKey(text)) {
                return "    ldarg " + currentArgsTable.get(text) + " // " + text + "\n";
            }
            // 2. Ищем в локальных переменных
            Integer index = currentSymbolTable.get(text);
            if (index != null) {
                return "    ldloc " + index + " // " + text + "\n";
            }
            return "    ldnull // undefined variable " + text + "\n";
        }

        return "    ldnull\n";
    }

    private String loadRangeVal(String val) {
        if (val.matches("\\d+")) {
            return "    ldc.i4 " + val + "\n    box [mscorlib]System.Int32\n";
        } else {
            return "    ldloc " + currentSymbolTable.get(val) + "\n";
        }
    }

    @Override
    public String visitSwitchStatement(SetLangParser.SwitchStatementContext ctx) {
        String labelEnd = getNextLabel();
        String switchVarId = ctx.ID().getText();
        Integer varIdx = currentSymbolTable.get(switchVarId);
        Integer argIdx = currentArgsTable.get(switchVarId);

        StringBuilder sb = new StringBuilder();
        if (argIdx != null) sb.append("    ldarg ").append(argIdx).append("\n");
        else if (varIdx != null) sb.append("    ldloc ").append(varIdx).append("\n");
        else sb.append("    ldnull\n");

        breakLabels.push(labelEnd);
        List<String> caseLabels = new ArrayList<>();
        for (int i = 0; i < ctx.caseBlock().size(); i++) {
            String label = getNextLabel();
            caseLabels.add(label);
            sb.append("    dup\n");
            String caseValStr = ctx.caseBlock(i).getChild(1).getText();
            if (caseValStr.matches("\\d+")) {
                sb.append("    ldc.i4 ").append(caseValStr).append("\n").append(BOX_INT);
            } else {
                Integer cVarIdx = currentSymbolTable.get(caseValStr);
                Integer cArgIdx = currentArgsTable.get(caseValStr);
                if (cArgIdx != null) sb.append("    ldarg ").append(cArgIdx).append("\n");
                else if (cVarIdx != null) sb.append("    ldloc ").append(cVarIdx).append("\n");
                else sb.append("    ldnull\n");
            }
            sb.append("    ldstr \"==\"\n");
            sb.append("    call bool ").append(RUNTIME_OPS).append("::Compare(object, object, string)\n");
            sb.append("    brtrue ").append(label).append("\n");
        }

        String defaultLabel = getNextLabel();
        sb.append("    br ").append(defaultLabel).append("\n");

        for (int i = 0; i < ctx.caseBlock().size(); i++) {
            sb.append(caseLabels.get(i)).append(":\n    pop\n"); // Удаляем switch-значение
            sb.append(visit(ctx.caseBlock(i).block()));
            sb.append("    br ").append(labelEnd).append("\n");
        }

        sb.append(defaultLabel).append(":\n    pop\n");
        if (ctx.defaultblock() != null) sb.append(visit(ctx.defaultblock().block()));

        sb.append(labelEnd).append(":\n");
        breakLabels.pop();
        return sb.toString();
    }


    @Override
    public String visitWhileStatement(SetLangParser.WhileStatementContext ctx) {
        String labelStart = getNextLabel();
        String labelEnd = getNextLabel();

        breakLabels.push(labelEnd); // Для break
        StringBuilder sb = new StringBuilder();

        sb.append(labelStart).append(":\n");

        // Условие
        sb.append(visit(ctx.logicalExpr()));
        sb.append("    call bool ").append(RUNTIME_OPS).append("::ToBool(object)\n");
        sb.append("    brfalse ").append(labelEnd).append("\n");

        // Тело
        sb.append(visit(ctx.block()));
        sb.append("    br ").append(labelStart).append("\n");

        sb.append(labelEnd).append(":\n");
        breakLabels.pop();
        return sb.toString();
    }

    @Override
    public String visitFunctionDeclaration(SetLangParser.FunctionDeclarationContext ctx) {
        Map<String, Integer> mainTable = currentSymbolTable;
        int mainIndex = nextLocalIndex;
        currentSymbolTable = new HashMap<>();
        currentArgsTable = new HashMap<>();
        nextLocalIndex = 0;

        String funcName = ctx.ID().getText();
        String retType = ctx.returnType().type().getText().equalsIgnoreCase("void") ? "void" : OBJ;

        List<String> argSigs = new ArrayList<>();
        if (ctx.paramList() != null) {
            for (int i = 0; i < ctx.paramList().args.size(); i++) {
                currentArgsTable.put(ctx.paramList().args.get(i).getText(), i);
                argSigs.add(OBJ);
            }
        }

        StringBuilder fCode = new StringBuilder();
        fCode.append("  .method static ").append(retType).append(" ").append(funcName)
                .append("(").append(String.join(", ", argSigs)).append(") cil managed {\n");
        fCode.append("    .maxstack 100\n");

        collectLocalVariables(ctx.block());
        if (!currentSymbolTable.isEmpty()) {
            fCode.append("    .locals init (\n");
            for (int i = 0; i < nextLocalIndex; i++) {
                fCode.append("      [").append(i).append("] object").append(i < nextLocalIndex - 1 ? ",\n" : "\n");
            }
            fCode.append("    )\n");
        }

        fCode.append(visit(ctx.block()));

        // --- SAFETY RETURN ---
        // Если выполнение дошло до сюда, значит не сработал ни один return в блоке
        if (!retType.equals("void")) {
            fCode.append("    ldnull\n");
        }
        fCode.append("    ret\n");
        fCode.append("  }\n\n");
        allMethodsCode.append(fCode);

        currentSymbolTable = mainTable;
        nextLocalIndex = mainIndex;
        currentArgsTable.clear();
        return "";
    }

    @Override
    public String visitVariableDeclaration(SetLangParser.VariableDeclarationContext ctx) {
        String id = ctx.ID().getText();
        String code = visit(ctx.expr());

        // Если выражение почему-то пустое, кладем null, чтобы не уронить стек
        if (code == null || code.trim().isEmpty()) code = "    ldnull\n";

        if (currentArgsTable.containsKey(id)) {
            return code + "    starg " + currentArgsTable.get(id) + " // " + id + "\n";
        }
        Integer index = currentSymbolTable.get(id);
        return code + "    stloc " + index + " // " + id + "\n";
    }




    @Override
    public String visitComplexExpr(SetLangParser.ComplexExprContext ctx) {
        if (ctx.simpleExpr() != null && ctx.left == null) return visit(ctx.simpleExpr());
        String left = visit(ctx.left);
        String right = visit(ctx.right);
        String method = "";
        switch (ctx.op.getText()) {
            case "+": method = "Add"; break;
            case "-": method = "Sub"; break;
            case "*": method = "Mul"; break;
            case "/": method = "Div"; break;
        }
        return left + right + "    call object " + RUNTIME_OPS + "::" + method + "(object, object)\n";
    }

    @Override
    public String visitComparisonExpr(SetLangParser.ComparisonExprContext ctx) {
        return visit(ctx.left) + visit(ctx.right) + "    ldstr \"" + ctx.op.getText() + "\"\n" +
                "    call bool " + RUNTIME_OPS + "::Compare(object, object, string)\n" + BOX_BOOL;
    }

    @Override
    public String visitLogicalExpr(SetLangParser.LogicalExprContext ctx) {
        if (ctx.logicalOperand() != null) {
            String code = visit(ctx.logicalOperand());
            if (ctx.NOT() != null) return code + "    call bool " + RUNTIME_OPS + "::Not(object)\n" + BOX_BOOL;
            return code;
        }
        return visit(ctx.left) + visit(ctx.right) + "    ldstr \"" + ctx.op.getText() + "\"\n" +
                "    call bool " + RUNTIME_OPS + "::LogicalOp(object, object, string)\n" + BOX_BOOL +
                (ctx.NOT() != null ? "    call bool " + RUNTIME_OPS + "::Not(object)\n" + BOX_BOOL : "");
    }

    @Override
    public String visitLogicalOperand(SetLangParser.LogicalOperandContext ctx) {
        if (ctx.comparisonExpr() != null) return visit(ctx.comparisonExpr());
        if (ctx.ID() != null) {
            String id = ctx.ID().getText();
            if (currentArgsTable.containsKey(id)) return "    ldarg " + currentArgsTable.get(id) + "\n";
            return "    ldloc " + currentSymbolTable.get(id) + "\n";
        }
        // Используем ldc.i4.1/0 и box
        String val = ctx.getText().equals("true") ? "1" : "0";
        return "    ldc.i4." + val + "\n" +
                "    box [mscorlib]System.Boolean\n";
    }

    @Override
    public String visitSimpleExpr(SetLangParser.SimpleExprContext ctx) {
        if (ctx.ID() != null) {
            String id = ctx.ID().getText();

            // Порядок поиска: Аргументы -> Локальные переменные
            if (currentArgsTable.containsKey(id)) {
                return "    ldarg " + currentArgsTable.get(id) + " // load arg " + id + "\n";
            }

            Integer index = currentSymbolTable.get(id);
            if (index != null) {
                return "    ldloc " + index + " // load var " + id + "\n";
            }

            return "    ldnull // undefined variable " + id + "\n";
        }
        return super.visitSimpleExpr(ctx);
    }

    @Override
    public String visitFunctionCall(SetLangParser.FunctionCallContext ctx) {
        String name = ctx.ID().getText();
        StringBuilder sb = new StringBuilder();
        int count = 0;
        if (ctx.exprList() != null) {
            for (var expr : ctx.exprList().expr()) {
                sb.append(visit(expr));
                count++;
            }
        }
        if (isBuiltin(name)) {
            String sig = "";
            for (int i = 0; i < count; i++) sig += (i == 0 ? "" : ", ") + "object";
            sb.append("    call object ").append(RUNTIME_OPS).append("::Builtin").append(name.substring(0, 1).toUpperCase()).append(name.substring(1)).append("(").append(sig).append(")\n");
        } else {
            String sig = "";
            for (int i = 0; i < count; i++) sig += (i == 0 ? "" : ", ") + "object";
            sb.append("    call object class Program::").append(name).append("(").append(sig).append(")\n");
        }
        if (ctx.getParent() instanceof SetLangParser.StatementContext) sb.append("    pop\n");
        return sb.toString();
    }

    private boolean isBuiltin(String n) { return n.equals("print") || n.equals("add") || n.equals("delete") || n.equals("len") || n.equals("includes") || n.equals("count"); }

    private String getBuiltinMethodName(String name) {
        switch (name) {
            case "print": return "BuiltinPrint";
            case "add": return "BuiltinAdd";
            case "delete": return "BuiltinDelete";
            case "len": return "BuiltinLen";
            case "includes": return "BuiltinIncludes";
            case "count": return "BuiltinCount"; // Добавлено
            default: return "";
        }
    }

    @Override
    public String visitSetLiteral(SetLangParser.SetLiteralContext ctx) {
        StringBuilder sb = new StringBuilder();
        // Создание объекта HashSet - ЭТО ДОЛЖНО БЫТЬ ВСЕГДА
        sb.append("    newobj instance void ").append(HASH_SET).append("::.ctor()\n");

        if (ctx.simpleExprList() != null) {
            for (var item : ctx.simpleExprList().simpleExpr()) {
                sb.append("    dup\n");
                String code = visit(item);
                sb.append(code.isEmpty() ? "    ldnull\n" : code);
                // Для HashSet.Add(T) в IL используем !0 (первый параметр типа)
                sb.append("    callvirt instance bool ").append(HASH_SET).append("::Add(!0)\n");
                sb.append("    pop\n");
            }
        }
        return sb.toString();
    }

    @Override
    public String visitTupleLiteral(SetLangParser.TupleLiteralContext ctx) {
        StringBuilder sb = new StringBuilder();
        // Создание объекта List - ЭТО ДОЛЖНО БЫТЬ ВСЕГДА
        sb.append("    newobj instance void ").append(LIST).append("::.ctor()\n");

        if (ctx.simpleExprList() != null) {
            for (var item : ctx.simpleExprList().simpleExpr()) {
                sb.append("    dup\n");
                String code = visit(item);
                sb.append(code.isEmpty() ? "    ldnull\n" : code);
                // Для List.Add(T) в IL используем !0
                sb.append("    callvirt instance void ").append(LIST).append("::Add(!0)\n");
            }
        }
        return sb.toString();
    }

    @Override
    public String visitElement(SetLangParser.ElementContext ctx) {
        if (ctx.INT() != null) return "    ldc.i4 " + ctx.INT().getText() + "\n" + BOX_INT;
        if (ctx.STRING() != null) return "    ldstr " + ctx.STRING().getText() + "\n";
        if (ctx.getText().equals("true")) return "    ldc.i4.1\n" + BOX_BOOL;
        if (ctx.getText().equals("false")) return "    ldc.i4.0\n" + BOX_BOOL;
        return "    ldnull\n";
    }


    @Override
    public String visitBlock(SetLangParser.BlockContext ctx) {
        StringBuilder sb = new StringBuilder();
        for (var s : ctx.statement()) sb.append(visit(s));
        return sb.toString();
    }

    @Override
    public String visitReturnStatement(SetLangParser.ReturnStatementContext ctx) {
        return visit(ctx.expr()) + "    ret\n";
    }

    private void collectMainVariables(ParseTree t) {
        if (t instanceof SetLangParser.VariableDeclarationContext) {
            String id = ((SetLangParser.VariableDeclarationContext) t).ID().getText();
            if (!currentSymbolTable.containsKey(id)) currentSymbolTable.put(id, nextLocalIndex++);
        }
        for (int i = 0; i < t.getChildCount(); i++) {
            ParseTree c = t.getChild(i);
            if (!(c instanceof SetLangParser.FunctionDeclarationContext)) collectMainVariables(c);
        }
    }

    private void collectLocalVariables(ParseTree t) {
        if (t instanceof SetLangParser.VariableDeclarationContext) {
            String id = ((SetLangParser.VariableDeclarationContext) t).ID().getText();
            if (!currentArgsTable.containsKey(id) && !currentSymbolTable.containsKey(id)) currentSymbolTable.put(id, nextLocalIndex++);
        }
        for (int i = 0; i < t.getChildCount(); i++) collectLocalVariables(t.getChild(i));
    }
}

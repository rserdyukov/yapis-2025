package org.example;
import org.antlr.v4.runtime.tree.*;
import java.util.*;
import org.example.SetLangBaseListener;

public class SemanticAnalyzer {

    static class SemanticErrorListener extends SetLangBaseListener {
        private final List<String> errors = new ArrayList<>();
        private final Map<String, String> variableTypes = new HashMap<>();
        private final Deque<Map<String, Integer>> scopes = new ArrayDeque<>();
        private final Map<String, Integer> globalFunctions = new HashMap<>();
        private final Deque<UnreachableCodeContext> unreachableStack = new ArrayDeque<>();
        private int loopDepth = 0;
        private boolean hasFunctions = false;
        private boolean functionsStarted = false;
        public SemanticErrorListener() {
            scopes.push(new HashMap<>());
        }


        @Override
        public void enterFunctionDeclaration(SetLangParser.FunctionDeclarationContext ctx) {
            functionsStarted = true;
            hasFunctions = true;
            String funcName = ctx.ID().getText();
            int line = ctx.start.getLine();
            int paramCount = 0;
            if (ctx.paramList() != null && ctx.paramList().ID() != null) {
                paramCount = ctx.paramList().ID().size();
            }

            if (ctx.paramList() != null) {
                for (TerminalNode param : ctx.paramList().ID()) {
                    String paramName = param.getText();
                    scopes.peek().put(paramName, param.getSymbol().getLine());
                    variableTypes.put(paramName, "unknown");
                }
            }
            if (globalFunctions.containsKey(funcName)) {
                errors.add("Семантическая ошибка: Функция '" + funcName +
                        "' уже объявлена ранее (строка " + line + ")");
            } else {
                globalFunctions.put(funcName, paramCount);
            }
            scopes.push(new HashMap<>());
            if (ctx.paramList() != null) {
                for (TerminalNode param : ctx.paramList().ID()) {
                    String paramName = param.getText();
                    scopes.peek().put(paramName, param.getSymbol().getLine());
                }
            }
            unreachableStack.push(new UnreachableCodeContext());
        }

        @Override
        public void exitFunctionDeclaration(SetLangParser.FunctionDeclarationContext ctx) {
            scopes.pop();
            UnreachableCodeContext context = unreachableStack.pop();
            if (context.hasUnreachableCode) {
                errors.add("Семантическая ошибка: Недостижимый код после " +
                        context.unreachableAfter + " в функции '" +
                        ctx.ID().getText() + "' (строка " + context.unreachableLine + ")");
            }
        }

        @Override
        public void enterWhileStatement(SetLangParser.WhileStatementContext ctx) {
            loopDepth++;
            scopes.push(new HashMap<>());
            unreachableStack.push(new UnreachableCodeContext());
        }

        @Override
        public void exitWhileStatement(SetLangParser.WhileStatementContext ctx) {
            scopes.pop();
            loopDepth--;
            UnreachableCodeContext context = unreachableStack.pop();
            if (context.hasUnreachableCode) {
                errors.add("Семантическая ошибка: Недостижимый код после " +
                        context.unreachableAfter + " в цикле while (строка " +
                        context.unreachableLine + ")");
            }
        }

        @Override
        public void enterForStatement(SetLangParser.ForStatementContext ctx) {
            loopDepth++;
            scopes.push(new HashMap<>());
            String iterVar = ctx.ID().getText();
            scopes.peek().put(iterVar, ctx.start.getLine());
            unreachableStack.push(new UnreachableCodeContext());
        }

        @Override
        public void exitForStatement(SetLangParser.ForStatementContext ctx) {
            scopes.pop();
            loopDepth--;
            UnreachableCodeContext context = unreachableStack.pop();
            if (context.hasUnreachableCode) {
                errors.add("Семантическая ошибка: Недостижимый код после " +
                        context.unreachableAfter + " в цикле for (строка " +
                        context.unreachableLine + ")");
            }
        }

        @Override
        public void enterIfStatement(SetLangParser.IfStatementContext ctx) {
            unreachableStack.push(new UnreachableCodeContext());
        }



        @Override
        public void exitIfStatement(SetLangParser.IfStatementContext ctx) {
            unreachableStack.pop();
        }

        @Override
        public void enterBlock(SetLangParser.BlockContext ctx) {
            unreachableStack.push(new UnreachableCodeContext());
        }

        @Override
        public void exitBlock(SetLangParser.BlockContext ctx) {
            UnreachableCodeContext context = unreachableStack.pop();

            if (!unreachableStack.isEmpty() && context.hasReturnOrBreak) {
                UnreachableCodeContext parent = unreachableStack.peek();
                parent.hasReturnOrBreak = true;
            }
        }

        @Override
        public void enterSwitchStatement(SetLangParser.SwitchStatementContext ctx) {
            String varName = ctx.ID().getText();
            int line = ctx.start.getLine();

            if (!isVariableDeclared(varName)) {
                errors.add("Семантическая ошибка: Переменная '" + varName +
                        "' не объявлена в switch (строка " + line + ")");
            } else {
                String typ = variableTypes.getOrDefault(varName, "unknown");
                if (!"int".equals(typ)) {
                    errors.add("Семантическая ошибка: Переменная '" + varName +
                            "' в switch должна иметь целочисленный тип (строка " + line + ")");
                }
            }
            unreachableStack.push(new UnreachableCodeContext());
        }


        @Override
        public void exitSwitchStatement(SetLangParser.SwitchStatementContext ctx) {
            loopDepth--;
            unreachableStack.pop();
        }

        @Override
        public void enterVariableDeclaration(SetLangParser.VariableDeclarationContext ctx) {
            String varName = ctx.ID().getText();
            int line = ctx.start.getLine();

            ParseTree value = null;
            try {
                if (ctx.expr() != null) value = ctx.expr();
                else if (ctx.getChildCount() > 2) value = ctx.getChild(2);
            } catch (Exception ignored) {}
            String inferredType = inferType(value);

            variableTypes.put(varName, inferredType);

            if (!scopes.isEmpty() && !scopes.peek().containsKey(varName)) {
                scopes.peek().put(varName, line);
            }
        }


        @Override
        public void enterReturnStatement(SetLangParser.ReturnStatementContext ctx) {
            int line = ctx.start.getLine();

            if (!unreachableStack.isEmpty() && unreachableStack.peek().isUnreachable) {
                errors.add("Семантическая ошибка: Недостижимый код - оператор return после " +
                        unreachableStack.peek().unreachableAfter + " (строка " + line + ")");
                unreachableStack.peek().hasUnreachableCode = true;
                unreachableStack.peek().unreachableLine = line;
            }
        }

        @Override
        public void exitReturnStatement(SetLangParser.ReturnStatementContext ctx) {
            if (!unreachableStack.isEmpty()) {
                unreachableStack.peek().isUnreachable = true;
                unreachableStack.peek().unreachableAfter = "return";
            }
        }

        @Override
        public void enterBreakStatement(SetLangParser.BreakStatementContext ctx) {
            int line = ctx.start.getLine();
            if (loopDepth == 0) errors.add("Семантическая ошибка: break вне цикла/switch (строка " + line + ")");
            if (!unreachableStack.isEmpty() && unreachableStack.peek().isUnreachable) {
                errors.add("Семантическая ошибка: Недостижимый код - оператор break после " +
                        unreachableStack.peek().unreachableAfter + " (строка " + line + ")");
                unreachableStack.peek().hasUnreachableCode = true;
                unreachableStack.peek().unreachableLine = line;
            }
        }

        @Override
        public void exitBreakStatement(SetLangParser.BreakStatementContext ctx) {
            if (!unreachableStack.isEmpty()) {
                unreachableStack.peek().isUnreachable = true;
                unreachableStack.peek().unreachableAfter = "break";
            }
        }

        @Override
        public void enterFunctionCall(SetLangParser.FunctionCallContext ctx) {
            String funcName = ctx.ID().getText();
            int line = ctx.start.getLine();

            if (!unreachableStack.isEmpty() && unreachableStack.peek().isUnreachable) {
                errors.add("Семантическая ошибка: Недостижимый код - вызов функции '" +
                        funcName + "' после " + unreachableStack.peek().unreachableAfter +
                        " (строка " + line + ")");
                unreachableStack.peek().hasUnreachableCode = true;
                unreachableStack.peek().unreachableLine = line;
            }

            if (ctx.POINT() == null && !globalFunctions.containsKey(funcName)) {
                errors.add("Семантическая ошибка: Функция '" + funcName +
                        "' не объявлена (строка " + line + ")");
                return;
            }

            if (ctx.POINT() == null) {
                int expectedArgs = globalFunctions.get(funcName);
                int actualArgs = getArgumentCount(ctx);

                if (expectedArgs != actualArgs) {
                    errors.add("Семантическая ошибка: Неверное количество аргументов при вызове функции '" +
                            funcName + "' (строка " + line + "). Ожидалось " + expectedArgs +
                            ", получено " + actualArgs);
                }
            }
        }


        @Override
        public void enterSimpleExpr(SetLangParser.SimpleExprContext ctx) {
            if (ctx.ID() != null) {
                String varName = ctx.ID().getText();
                int line = ctx.start.getLine();

                if (!isVariableDeclared(varName)) {
                    errors.add("Семантическая ошибка: Переменная '" + varName +
                            "' не объявлена (строка " + line + ")");
                }
            }
        }

        @Override
        public void enterLogicalOperand(SetLangParser.LogicalOperandContext ctx) {
            if (ctx.ID() != null) {
                String varName = ctx.ID().getText();
                int line = ctx.start.getLine();

                if (!isVariableDeclared(varName)) {
                    errors.add("Семантическая ошибка: Переменная '" + varName +
                            "' не объявлена (строка " + line + ")");
                }
            }
        }

        @Override
        public void enterRange(SetLangParser.RangeContext ctx) {
            int line = ctx.start.getLine();

            List<TerminalNode> ids = new ArrayList<>();
            List<TerminalNode> nums = new ArrayList<>();
            try { if (ctx.ID() != null) ids.addAll(ctx.ID()); } catch (Exception ignored) {}
            try { if (ctx.INT() != null) nums.addAll(ctx.INT()); } catch (Exception ignored) {}

            for (TerminalNode id : ids) {
                String name = id.getText();
                int idLine = id.getSymbol().getLine();
                if (!isVariableDeclared(name)) {
                    errors.add("Семантическая ошибка: Переменная '" + name +
                            "' не объявлена в range (строка " + idLine + ")");
                } else {
                    String typ = variableTypes.getOrDefault(name, "unknown");
                    if (!"int".equals(typ)) {
                        errors.add("Семантическая ошибка: Значение '" + name +
                                "' в range должно быть целочисленным (строка " + idLine + ")");
                    }
                }
            }
        }

        @Override
        public void enterCaseBlock(SetLangParser.CaseBlockContext ctx) {
            int line = ctx.start.getLine();
            ParseTree value = null;
            try {
                if (ctx.expr() != null) value = ctx.expr();
                else if (ctx.getChildCount() > 1) value = ctx.getChild(1);
            } catch (Exception ignored) {}

            if (value == null) return;

            String typ = inferType(value);
            if (!"int".equals(typ)) {
                errors.add("Семантическая ошибка: Значение case '" + value.getText() +
                        "' должно быть целочисленным (строка " + line + ")");
            }
        }

        @Override
        public void enterComplexExpr(SetLangParser.ComplexExprContext ctx) {
            if (ctx.op != null && ctx.left != null && ctx.right != null) {
                String leftType = inferType(ctx.left);
                String rightType = inferType(ctx.right);
                String op = ctx.op.getText();
                int line = ctx.start.getLine();

                if (!areTypesCompatible(leftType, rightType, op)) {
                    errors.add("Семантическая ошибка: Операция '" + op + "' между '" +
                            leftType + "' и '" + rightType + "' недопустима (строка " + line + ")");
                }
            }
        }

        private boolean areTypesCompatible(String leftType, String rightType, String op) {
            switch (op) {
                case "+": case "-": case "*": case "/":
                    return leftType.equals("int") && rightType.equals("int");
                case "<": case ">": case "<=": case ">=":
                    return leftType.equals("int") && rightType.equals("int");
                case "==": case "!=":
                    return leftType.equals(rightType);
                case "AND": case "OR":
                    return leftType.equals("bool") && rightType.equals("bool");
                case "UN": case "DIFF": case "SYMDIFF":
                    return leftType.equals("set") && rightType.equals("set");
                default:
                    return false;
            }
        }

        private String inferType(ParseTree node) {
            if (node == null) return "unknown";
            String txt = node.getText().trim();
            if ((txt.startsWith("\"") && txt.endsWith("\"")) || (txt.startsWith("'") && txt.endsWith("'")))
                return "string";
            if (txt.startsWith("{") && txt.endsWith("}"))
                return "set";
            if (txt.startsWith("[") && txt.endsWith("]"))
                return "tuple";
            if (txt.matches("-?\\d+"))
                return "int";
            if (txt.equalsIgnoreCase("true") || txt.equalsIgnoreCase("false")
                    || txt.equalsIgnoreCase("!false") || txt.equalsIgnoreCase("!true"))
                return "bool";
            if (node instanceof SetLangParser.ComparisonExprContext)
                return "bool";
            if (node instanceof SetLangParser.LogicalExprContext) {
                if (((SetLangParser.LogicalExprContext) node).op != null)
                    return "bool";
                return inferType(node.getChild(0));
            }
            if (node instanceof TerminalNode) {
                if (variableTypes.containsKey(txt))
                    return variableTypes.get(txt);
            }
            if (node instanceof SetLangParser.FunctionCallContext) {
                String funcName = ((SetLangParser.FunctionCallContext) node).ID().getText();
                return "unknown";
            }
            for (int i = 0; i < node.getChildCount(); i++) {
                String childType = inferType(node.getChild(i));
                if (!childType.equals("unknown"))
                    return childType;
            }

            return "unknown";
        }

        private boolean isVariableDeclared(String varName) {
            for (Map<String, Integer> scope : scopes) {
                if (scope.containsKey(varName)) {
                    return true;
                }
            }
            return globalFunctions.containsKey(varName);
        }

        private int getArgumentCount(SetLangParser.FunctionCallContext ctx) {
            if (ctx.exprList() == null)
                return 0;

            List<SetLangParser.ExprContext> exprs = ctx.exprList().expr();
            if (exprs == null || exprs.isEmpty())
                return 0;

            int count = 0;
            for (SetLangParser.ExprContext expr : exprs) {
                String text = expr.getText().trim();
                if (text.startsWith("!")) {
                    text = text.substring(1).trim();
                }
                if (!text.isEmpty())
                    count++;
            }

            return count;
        }

        public boolean hasErrors() {
            return !errors.isEmpty();
        }

        public List<String> getErrors() {
            return errors;
        }
    }

    static class UnreachableCodeContext {
        boolean isUnreachable = false;
        boolean hasReturnOrBreak = false;
        boolean hasUnreachableCode = false;
        String unreachableAfter = "";
        int unreachableLine = -1;
    }
}

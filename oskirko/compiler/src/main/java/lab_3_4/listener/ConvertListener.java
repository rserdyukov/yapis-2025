package lab_3_4.listener;

import lab_3_4.Constant;
import lab_3_4.Utils;
import lab_3_4.grammarPLBaseListener;
import lab_3_4.grammarPLLexer;
import lab_3_4.grammarPLParser;
import lab_3_4.model.Variable;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.TerminalNode;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Stack;

public class ConvertListener extends grammarPLBaseListener {

    private StringBuilder converted;
    private final SemanticAnalyzeListener preprocessListener;
    private final Stack<Integer> typeStack;
    private final Stack<String> functionScope;
    private final List<String> currentResultArgs;
    private int indentationLevel;
    private StringBuilder forUpdateString;
    private boolean isForUpdateExpr = false;
    private int memoryOffset;
    private int switchCounter;
    private int caseCounter;
    private int ifCounter;
    private int whileCounter;
    private int forCounter;
    private int commonCaseCounter;
    private final Stack<String> scope;

    public ConvertListener(SemanticAnalyzeListener preprocessListener) {
        this.functionScope = new Stack<>();
        this.typeStack = new Stack<>();
        this.preprocessListener = preprocessListener;
        this.converted = new StringBuilder();
        this.forUpdateString = new StringBuilder();
        this.currentResultArgs = new ArrayList<>();
        this.memoryOffset = 0;
        this.indentationLevel = 0;
        this.switchCounter = 0;
        this.caseCounter = 0;
        this.ifCounter = 0;
        this.whileCounter = 0;
        this.forCounter = 0;
        this.commonCaseCounter = 0;
        this.scope = new Stack<>();
        this.scope.push(".");
    }

    @Override
    public void enterProgram(grammarPLParser.ProgramContext ctx) {
        converted.append(Utils.stringWithIndention("(module\n", indentationLevel));
        indentationLevel++;
        converted.append(Utils.stringWithIndention("(import \"console\" \"logString\" (func $logString (param i32 i32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"console\" \"logInteger\" (func $logInteger (param i32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"console\" \"logFloat\" (func $logFloat (param f32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"console\" \"inputInteger\" (func $inputInteger (param i32 i32) (result i32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"console\" \"inputFloat\" (func $inputFloat (param i32 i32) (result f32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"console\" \"newLine\" (func $newLine))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"array\" \"newArray\" (func $newArray (param i32) (result i32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"array\" \"getInteger\" (func $getInteger (param i32 i32) (result i32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"array\" \"setInteger\" (func $setInteger (param i32 i32 i32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"array\" \"getFloat\" (func $getFloat (param i32 i32) (result f32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"array\" \"setFloat\" (func $setFloat (param i32 i32 f32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"math\" \"sin\" (func $sin (param f32) (result f32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"math\" \"cos\" (func $cos (param f32) (result f32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"math\" \"log\" (func $log (param f32 f32) (result f32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"math\" \"pow\" (func $pow (param f32 f32) (result f32)))\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(import \"js\" \"mem\" (memory 1))\n", indentationLevel));
        int offset = 0;
        for (String string : preprocessListener.getStrings()) {
            converted.append(Utils.stringWithIndention(String.format("(data (i32.const %d) %s)\n", offset, string), indentationLevel));
            offset += string.length() - 1;
        }

        functionScope.push(".");
    }

    @Override
    public void exitProgram(grammarPLParser.ProgramContext ctx) {
        indentationLevel--;
        converted.append(Utils.stringWithIndention(")\n", indentationLevel--));
        converted.append(Utils.stringWithIndention(")\n", indentationLevel));
        functionScope.pop();
    }

    @Override
    public void enterFunctionDeclaration(grammarPLParser.FunctionDeclarationContext ctx) {
        converted.append(Utils.stringWithIndention(String.format("(func $%s (export \"%s\") \n", ctx.ID().getText(), ctx.ID().getText()), indentationLevel));
        indentationLevel++;
        Map<String, Integer> results = new HashMap<>();
        Map<String, Integer> locals = new HashMap<>();
        for (Map.Entry<String, Variable> map : preprocessListener.getFunctionMap().get(ctx.ID().getText()).entrySet()) {

            if (map.getValue().isParameter()) {
                if (map.getValue().isResult()) {
                    results.put(map.getKey(), map.getValue().getType());
                } else {
                    converted.append(Utils.stringWithIndention(String.format("(param $%s %s)\n",
                            map.getValue().getName(),
                            Utils.typeMapper(map.getValue().getType())), indentationLevel));
                }
            } else {
                locals.put(map.getKey(), map.getValue().getType());
            }
        }
        results.forEach((key, value) -> converted.append(Utils.stringWithIndention(String.format("(result %s)\n",
                Utils.typeMapper(value)), indentationLevel)));

        functionScope.push(ctx.ID().getText());
        scope.push(ctx.ID().getText());

        for (int i = 0; i < preprocessListener.getSwitchTypeMap().get(functionScope.peek()).size(); i++) {
            converted.append(Utils.stringWithIndention(
                    String.format("(local $%s %s)\n", "switch_parameter_" + i,
                            grammarPLLexer.TYPE_INTEGER == preprocessListener.getSwitchTypeMap().get(functionScope.peek()).get(i).getType() ? "i32" : "f32"),
                    indentationLevel));
        }

        for (String innerScope : preprocessListener.getFunctionScopes().get(ctx.ID().getText())) {
            preprocessListener.getVariablesMap().get(innerScope).values().stream()
                    .filter(element -> Objects.equals(element.getScope(), innerScope))
                    .forEach(element -> locals.put((Objects.equals(element.getScope(), ".") || Objects.equals(element.getScope(), ctx.ID().getText()) ? element.getName() : element.getScope() + "__" + element.getName()), element.getType()));
        }

        locals.forEach((key, value) -> converted.append(Utils.stringWithIndention(String.format("(local $%s %s)\n",
                key,
                Utils.typeMapper(value)), indentationLevel)));

        results.forEach((key, value) -> converted.append(Utils.stringWithIndention(String.format("(local $%s %s)\n",
                key,
                Utils.typeMapper(value)), indentationLevel)));
    }

    @Override
    public void exitArrayDeclarationStatement(grammarPLParser.ArrayDeclarationStatementContext ctx) {
        converted.append(Utils.stringWithIndention("call $newArray\n", indentationLevel));
        converted.append(Utils.stringWithIndention(String.format("local.set $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
    }

    @Override
    public void exitFunctionDeclaration(grammarPLParser.FunctionDeclarationContext ctx) {
        for (String name : preprocessListener.getFunctionMap().get(functionScope.peek())
                     .values().stream()
                     .filter(Variable::isResult)
                     .map(Variable::getName)
                     .toList()) {
            converted.append(Utils.stringWithIndention(String.format("local.get $%s\n", getVariableName(name)), indentationLevel));
        }
        indentationLevel--;
        converted.append(Utils.stringWithIndention(")\n", indentationLevel));
        functionScope.pop();
        scope.pop();
        switchCounter = 0;
    }

    @Override
    public void enterPrimary(grammarPLParser.PrimaryContext ctx) {
        if (ctx.INT() != null || ctx.FLOAT() != null) {
            if (isForUpdateExpr) {
                forUpdateString.append(Utils.stringWithIndention(String.format("%s.const %s\n", ctx.INT() == null ? "f32" : "i32", ctx.getText()), indentationLevel));
            } else {
                int currentType = ctx.INT() == null ? grammarPLLexer.TYPE_FLOAT : grammarPLLexer.TYPE_INTEGER;
                converted.append(Utils.stringWithIndention(String.format("%s.const %s\n", ctx.INT() == null ? "f32" : "i32", ctx.getText()), indentationLevel));
                typeStack.push(currentType);
            }
        } else if (ctx.ID() != null) {
            if (isForUpdateExpr) {
                forUpdateString.append(Utils.stringWithIndention(String.format("local.get $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
            } else {
                int currentType = preprocessListener.getVariablesMap().get(scope.peek()).get(ctx.ID().getText()).getType();
                converted.append(Utils.stringWithIndention(String.format("local.get $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
                typeStack.push(currentType);
            }
        }
    }

    @Override
    public void exitFunctionDeclarationPart(grammarPLParser.FunctionDeclarationPartContext ctx) {
        converted.append(Utils.stringWithIndention("(func $run (export \"run\")\n", indentationLevel++));

        for (Variable local : preprocessListener.getVariablesMap().get(".").values().stream()
                .filter(element -> Objects.equals(element.getScope(), "."))
                .toList()) {
            converted.append(Utils.stringWithIndention(String.format("(local $%s %s)\n", local.getName(), local.getType() == grammarPLLexer.TYPE_INTEGER ? "i32" : "f32"), indentationLevel));
        }

        for (String scope : preprocessListener.getFunctionScopes().get(".")) {
            for (Variable local : preprocessListener.getVariablesMap().get(scope).values().stream()
                    .filter(element -> !Objects.equals(element.getScope(), "."))
                    .toList()) {
                converted.append(Utils.stringWithIndention(String.format("(local $%s %s)\n", local.getScope() + "__" + local.getName(), local.getType() == grammarPLLexer.TYPE_INTEGER ? "i32" : "f32"), indentationLevel));
            }
        }

        for (int i = 0; i < preprocessListener.getSwitchTypeMap().get(".").size(); i++) {
            converted.append(Utils.stringWithIndention(
                    String.format("(local $%s %s)\n", "switch_parameter_" + i,
                            grammarPLLexer.TYPE_INTEGER == preprocessListener.getSwitchTypeMap().get(functionScope.peek()).get(i).getType() ? "i32" : "f32"),
                    indentationLevel));
        }
    }

    @Override
    public void enterFunctionArgPrimary(grammarPLParser.FunctionArgPrimaryContext ctx) {
        if (ctx.INT() != null || ctx.FLOAT() != null) {
            converted.append(Utils.stringWithIndention(String.format("%s.const %s\n", ctx.INT() == null ? "f32" : "i32", ctx.getText()), indentationLevel));
            typeStack.push(ctx.INT() == null ? grammarPLLexer.TYPE_FLOAT : grammarPLLexer.TYPE_INTEGER);
        } else if (ctx.ID() != null) {
            if (!currentResultArgs.contains(ctx.ID().getText())) {
                converted.append(Utils.stringWithIndention(String.format("local.get $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
            }
            typeStack.push(preprocessListener.getFunctionMap().get(functionScope.peek()).get(ctx.ID().getText()).getType());
        } else if (ctx.STRING() != null) {
            typeStack.push(grammarPLLexer.TYPE_STRING);
        }
    }

    @Override
    public void exitFunctionArgExpr(grammarPLParser.FunctionArgExprContext ctx) {
        if (ctx.functionArgPrimary() != null) {

        }

        if (ctx.functionArgExpr().size() == 2) {
            handleBinaryExpr(ctx);
        }
    }

    @Override
    public void exitVarDeclarationStatement(grammarPLParser.VarDeclarationStatementContext ctx) {
        if (ctx.ASSIGN() != null) {
            converted.append(Utils.stringWithIndention(String.format("local.set $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
        }
    }

    @Override
    public void exitVarDeclarationWithoutSemicolon(grammarPLParser.VarDeclarationWithoutSemicolonContext ctx) {
        if (ctx.ASSIGN() != null) {
            converted.append(Utils.stringWithIndention(String.format("local.set $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
        }
    }

    @Override
    public void exitAssignmentStatementWithoutSemicolon(grammarPLParser.AssignmentStatementWithoutSemicolonContext ctx) {
        if (isForUpdateExpr) {
            forUpdateString.append(Utils.stringWithIndention(String.format("local.set $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
        } else {
            converted.append(Utils.stringWithIndention(String.format("local.set $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
            typeStack.push(grammarPLLexer.TYPE_INTEGER);
        }
    }

    @Override
    public void exitExpr(grammarPLParser.ExprContext ctx) {
        if (ctx.primary() != null) {

        }

        if (ctx.expr().size() == 2) {
            handleBinaryExpr(ctx);
        }
    }

    @Override
    public void enterFunctionCall(grammarPLParser.FunctionCallContext ctx) {
        List<Boolean> resultIndexes;

        switch (ctx.ID().getText()) {
            case Constant.OUT_FUNCTION_NAME: {

                resultIndexes = List.of(false);
                break;
            }

            case Constant.IN_FUNCTION_NAME: {
                resultIndexes = List.of(false, true);

                break;
            }

            case Constant.LOG_FUNCTION_NAME: {
                resultIndexes = List.of(false, false, true);

                break;
            }

            case Constant.COS_FUNCTION_NAME: {
                resultIndexes = List.of(false, true);

                break;
            }

            case Constant.SIN_FUNCTION_NAME: {
                resultIndexes = List.of(false, true);

                break;
            }

            case Constant.POW_FUNCTION_NAME: {
                resultIndexes = List.of(false, false, true);

                break;
            }

            case Constant.NEW_LINE_FUNCTION_NAME: {
                resultIndexes = Collections.emptyList();

                break;
            }

            default: {
                resultIndexes = preprocessListener.getFunctionMap().get(ctx.ID().getText())
                        .values().stream()
                        .filter(Variable::isParameter)
                        .map(Variable::isResult).toList();
            }
        }

        for (int i = 0; i < resultIndexes.size(); i++) {
            if (resultIndexes.get(i)) {
                this.currentResultArgs.add(ctx.argList().functionArgExpr(i).getText());
            }
        }
    }

    @Override
    public void exitFunctionCall(grammarPLParser.FunctionCallContext ctx) {
        switch (ctx.ID().getText()) {
            case Constant.OUT_FUNCTION_NAME: {

                switch (typeStack.peek()) {

                    case grammarPLLexer.TYPE_STRING: {
                        String parameter = ctx.argList().functionArgExpr(0).getText();
                        converted.append(Utils.stringWithIndention(String.format("i32.const %d\n", memoryOffset), indentationLevel));
                        converted.append(Utils.stringWithIndention(String.format("i32.const %d\n", parameter.length() - 2), indentationLevel));
                        memoryOffset += parameter.length() - 1;

                        converted.append(Utils.stringWithIndention("call $logString\n", indentationLevel));

                        break;
                    }

                    case grammarPLLexer.TYPE_INTEGER: {
                        converted.append(Utils.stringWithIndention("call $logInteger\n", indentationLevel));

                        break;
                    }

                    case grammarPLLexer.TYPE_FLOAT: {
                        converted.append(Utils.stringWithIndention("call $logFloat\n", indentationLevel));

                        break;
                    }

                }

                break;
            }

            case Constant.IN_FUNCTION_NAME: {
                String parameter = ctx.argList().functionArgExpr(0).getText();
                converted.append(Utils.stringWithIndention(String.format("i32.const %d\n", memoryOffset), indentationLevel));
                converted.append(Utils.stringWithIndention(String.format("i32.const %d\n", parameter.length() - 2), indentationLevel));
                memoryOffset += parameter.length() - 1;

                switch (typeStack.peek()) {
                    case grammarPLLexer.TYPE_INTEGER: {
                        converted.append(Utils.stringWithIndention("call $inputInteger\n", indentationLevel));

                        break;
                    }

                    case grammarPLLexer.TYPE_FLOAT: {
                        converted.append(Utils.stringWithIndention("call $inputFloat\n", indentationLevel));

                        break;
                    }
                }

                break;
            }

            case Constant.NEW_LINE_FUNCTION_NAME: {
                converted.append(Utils.stringWithIndention("call $newLine\n", indentationLevel));

                break;
            }

            case Constant.COS_FUNCTION_NAME: {
                converted.append(Utils.stringWithIndention("call $cos\n", indentationLevel));

                break;
            }

            case Constant.SIN_FUNCTION_NAME: {
                converted.append(Utils.stringWithIndention("call $sin\n", indentationLevel));

                break;
            }

            case Constant.LOG_FUNCTION_NAME: {
                converted.append(Utils.stringWithIndention("call $log\n", indentationLevel));

                break;
            }

            case Constant.POW_FUNCTION_NAME: {
                converted.append(Utils.stringWithIndention("call $pow\n", indentationLevel));

                break;
            }

            default: {
                converted.append(Utils.stringWithIndention(String.format("call $%s\n", ctx.ID()), indentationLevel));
            }
        }

        if (ctx.argList() != null) {
            for (grammarPLParser.FunctionArgExprContext functionArgExprCtx : ctx.argList().functionArgExpr()) {
                if (currentResultArgs.contains(functionArgExprCtx.getText())) {
                    converted.append(Utils.stringWithIndention(String.format("local.set $%s\n", getVariableName(functionArgExprCtx.getText())), indentationLevel));
                }
            }
        }

        this.currentResultArgs.clear();
    }

    @Override
    public void exitAssignmentStatement(grammarPLParser.AssignmentStatementContext ctx) {
        if (ctx.arrayIndexAccess() == null) {
            converted.append(Utils.stringWithIndention(String.format("local.set $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
        } else {
            converted.append(Utils.stringWithIndention(String.format("call $%s\n", preprocessListener.getExpressionsMap().get(scope.peek()).get(ctx.arrayIndexAccess().expr().getText()).getType() == grammarPLLexer.TYPE_INTEGER ? "setInteger" : "setFloat"), indentationLevel));
        }
    }

    @Override
    public void enterForStatement(grammarPLParser.ForStatementContext ctx) {
        scope.push("for-" + forCounter++);
    }

    @Override
    public void enterForUpdate(grammarPLParser.ForUpdateContext ctx) {
        isForUpdateExpr = true;
    }

    @Override
    public void exitForUpdate(grammarPLParser.ForUpdateContext ctx) {
        isForUpdateExpr = false;
    }

    @Override
    public void enterAssignmentStatement(grammarPLParser.AssignmentStatementContext ctx) {
        if (ctx.arrayIndexAccess() != null) {
            converted.append(Utils.stringWithIndention(String.format("local.get $%s\n", getVariableName(ctx.arrayIndexAccess().ID().getText())), indentationLevel));
        }
    }

    @Override
    public void enterArrayIndex(grammarPLParser.ArrayIndexContext ctx) {
        converted.append(Utils.stringWithIndention(String.format("local.get $%s\n", getVariableName(ctx.ID().getText())), indentationLevel));
    }

    @Override
    public void exitArrayIndex(grammarPLParser.ArrayIndexContext ctx) {
        converted.append(Utils.stringWithIndention(String.format("call $%s\n", typeStack.peek() == grammarPLLexer.TYPE_INTEGER ? "getInteger" : "getFloat"), indentationLevel));
        typeStack.push(typeStack.peek() == grammarPLLexer.TYPE_INTEGER ? grammarPLLexer.TYPE_INTEGER : grammarPLLexer.TYPE_FLOAT);
    }

    @Override
    public void exitSwitchExpression(grammarPLParser.SwitchExpressionContext ctx) {
        converted.append(Utils.stringWithIndention(String.format("local.set $%s\n",  "switch_parameter_" + switchCounter), indentationLevel));
    }

    @Override
    public void exitSwitchStatement(grammarPLParser.SwitchStatementContext ctx) {
        switchCounter++;

        for (int i = 0; i < caseCounter * 2; i++) {
            converted.append(Utils.stringWithIndention(")\n", --indentationLevel));
        }

        caseCounter = 0;
    }

    @Override
    public void exitForStatement(grammarPLParser.ForStatementContext ctx) {
        converted.append(forUpdateString);
        converted.append(Utils.stringWithIndention("br $loop\n", indentationLevel--));
        converted.append(Utils.stringWithIndention(")\n", indentationLevel--));
        converted.append(Utils.stringWithIndention(")\n", indentationLevel));
        forUpdateString = new StringBuilder();
        scope.pop();
    }

    @Override
    public void enterForCondition(grammarPLParser.ForConditionContext ctx) {
        converted.append(Utils.stringWithIndention("(block $exit\n", indentationLevel++));
        converted.append(Utils.stringWithIndention("(loop $loop\n", indentationLevel++));
    }

    @Override
    public void enterIfStatement(grammarPLParser.IfStatementContext ctx) {
        scope.push("if-" + ifCounter++);
    }

    @Override
    public void exitForCondition(grammarPLParser.ForConditionContext ctx) {
        converted.append(Utils.stringWithIndention("i32.eqz\n", indentationLevel));
        converted.append(Utils.stringWithIndention("br_if $exit\n", indentationLevel));
        isForUpdateExpr = false;
    }

    @Override
    public void exitIfSignature(grammarPLParser.IfSignatureContext ctx) {
        converted.append(Utils.stringWithIndention("(if\n", indentationLevel++));
        converted.append(Utils.stringWithIndention("(then\n", indentationLevel++));
    }

    @Override
    public void exitIfBlock(grammarPLParser.IfBlockContext ctx) {
        indentationLevel--;
        converted.append(Utils.stringWithIndention(")\n", indentationLevel));
    }

    @Override
    public void exitIfStatement(grammarPLParser.IfStatementContext ctx) {
        if (ctx.elseBlock() == null) {
            converted.append(Utils.stringWithIndention("(else)\n", indentationLevel--));
        }
        converted.append(Utils.stringWithIndention(")\n", indentationLevel));
        scope.pop();
    }

    @Override
    public void enterElseBlock(grammarPLParser.ElseBlockContext ctx) {
        converted.append(Utils.stringWithIndention("(else\n", indentationLevel++));
    }

    @Override
    public void exitElseBlock(grammarPLParser.ElseBlockContext ctx) {
        converted.append(Utils.stringWithIndention(")\n", --indentationLevel));
        indentationLevel--;
    }

    @Override
    public void enterWhileStatement(grammarPLParser.WhileStatementContext ctx) {
        converted.append(Utils.stringWithIndention("(block $exit\n", indentationLevel++));
        converted.append(Utils.stringWithIndention("(loop $loop\n", indentationLevel++));
        scope.push("while-" + whileCounter++);
    }

    @Override
    public void exitWhileCondition(grammarPLParser.WhileConditionContext ctx) {
        converted.append(Utils.stringWithIndention("i32.eqz\n", indentationLevel));
        converted.append(Utils.stringWithIndention("br_if $exit\n", indentationLevel));
        isForUpdateExpr = false;
    }

    @Override
    public void exitWhileStatement(grammarPLParser.WhileStatementContext ctx) {
        converted.append(Utils.stringWithIndention("br $loop\n", indentationLevel--));
        converted.append(Utils.stringWithIndention(")\n", indentationLevel--));
        converted.append(Utils.stringWithIndention(")\n", indentationLevel));
        scope.pop();
    }

    @Override
    public void exitCaseExpr(grammarPLParser.CaseExprContext ctx) {
        converted.append(Utils.stringWithIndention(String.format("local.get $%s\n", "switch_parameter_" + switchCounter), indentationLevel));
        converted.append(Utils.stringWithIndention(grammarPLLexer.TYPE_INTEGER == preprocessListener.getSwitchTypeMap().get(functionScope.peek()).get(switchCounter).getType() ? "i32.eq\n" : "f32.eq\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(if\n", indentationLevel++));
        converted.append(Utils.stringWithIndention("(then\n", indentationLevel++));
    }

    @Override
    public void enterCaseBlock(grammarPLParser.CaseBlockContext ctx) {
        scope.push("case-" + commonCaseCounter++);
        caseCounter++;
    }

    @Override
    public void exitCaseBlock(grammarPLParser.CaseBlockContext ctx) {
        indentationLevel--;
        converted.append(Utils.stringWithIndention(")\n", indentationLevel));
        converted.append(Utils.stringWithIndention("(else\n", indentationLevel++));
        scope.pop();
    }



    public StringBuilder getConverted() {
        return converted;
    }

    public void setConverted(StringBuilder converted) {
        this.converted = converted;
    }

    // Метод для обработки бинарных выражений
    private void handleBinaryExpr(ParserRuleContext targetCtx) {
        ParseTree operationNode = targetCtx.getChild(1);
        int operationType = ((TerminalNode) operationNode).getSymbol().getType();

        switch (operationType) {
            case grammarPLLexer.PLUS -> typeOfPlus(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.MINUS -> typeOfMinus(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.MULT -> typeOfMultiplication(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.DIV -> typeOfDivision(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.REMDIV -> typeOfRemainderDivision(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.LT -> typeOfLt(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.LE -> typeOfLe(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.GT -> typeOfGt(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.GE -> typeOfGe(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.EQ -> typeOfEq(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.NEQ -> typeOfNeq(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.AND -> typeOfAnd(typeStack.pop(), typeStack.pop());
            case grammarPLLexer.OR -> typeOfOr(typeStack.pop(), typeStack.pop());
        }
    }

    // Метод для обработки операции '-'
    private void typeOfMinus(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
            converted.append(Utils.stringWithIndention("f32.sub\n", indentationLevel));
            typeStack.push(grammarPLLexer.TYPE_FLOAT);
        } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
            converted.append(Utils.stringWithIndention("i32.sub\n", indentationLevel));
            typeStack.push(grammarPLLexer.TYPE_INTEGER);
        }
    }

    // Метод для обработки операции '+'
    private void typeOfPlus(Integer leftType, Integer rightType) {
        if (isForUpdateExpr) {
            if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
                forUpdateString.append(Utils.stringWithIndention("f32.add\n", indentationLevel));
            } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
                forUpdateString.append(Utils.stringWithIndention("i32.add\n", indentationLevel));
            }
        } else {
            if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
                converted.append(Utils.stringWithIndention("f32.add\n", indentationLevel));
                typeStack.push(grammarPLLexer.TYPE_FLOAT);
            } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
                converted.append(Utils.stringWithIndention("i32.add\n", indentationLevel));
                typeStack.push(grammarPLLexer.TYPE_INTEGER);
            }
        }

    }

    // Метод для обработки операции '*'
    private void typeOfMultiplication(Integer leftType, Integer rightType) {
        if (isForUpdateExpr) {
            if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
                forUpdateString.append(Utils.stringWithIndention("f32.mul\n", indentationLevel));
            } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
                forUpdateString.append(Utils.stringWithIndention("i32.mul\n", indentationLevel));
            }
        } else {
            if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
                converted.append(Utils.stringWithIndention("f32.mul\n", indentationLevel));
                typeStack.push(grammarPLLexer.TYPE_FLOAT);
            } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
                converted.append(Utils.stringWithIndention("i32.mul\n", indentationLevel));
                typeStack.push(grammarPLLexer.TYPE_INTEGER);
            }
        }
    }

    // Метод для обработки операции '/'
    private void typeOfDivision(Integer leftType, Integer rightType) {
        if (isForUpdateExpr) {
            if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
                forUpdateString.append(Utils.stringWithIndention("f32.div\n", indentationLevel));
            } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
                forUpdateString.append(Utils.stringWithIndention("i32.div_s\n", indentationLevel));
            }
        } else {
            if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
                converted.append(Utils.stringWithIndention("f32.div\n", indentationLevel));
                typeStack.push(grammarPLLexer.TYPE_FLOAT);
            } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
                converted.append(Utils.stringWithIndention("i32.div_s\n", indentationLevel));
                typeStack.push(grammarPLLexer.TYPE_INTEGER);
            }
        }
    }

    // Метод для обработки операции '%'
    private void typeOfRemainderDivision(Integer leftType, Integer rightType) {
        if (isForUpdateExpr) {
            if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
                forUpdateString.append(Utils.stringWithIndention("i32.rem_s\n", indentationLevel));
            }
        } else {
            if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
                converted.append(Utils.stringWithIndention("i32.rem_s\n", indentationLevel));
                typeStack.push(grammarPLLexer.TYPE_INTEGER);
            }
        }
    }

    // Метод для обработки операций '<'
    private void typeOfLt(Integer leftType, Integer rightType) {
        if ((leftType != grammarPLLexer.TYPE_FLOAT || rightType != grammarPLLexer.TYPE_FLOAT) &&
                (leftType != grammarPLLexer.TYPE_INTEGER || rightType != grammarPLLexer.TYPE_INTEGER)) {
            return;
        }

        converted.append(Utils.stringWithIndention("i32.lt_s\n", indentationLevel));
    }

    // Метод для обработки операций '<'
    private void typeOfGt(Integer leftType, Integer rightType) {
        if ((leftType != grammarPLLexer.TYPE_FLOAT || rightType != grammarPLLexer.TYPE_FLOAT) &&
                (leftType != grammarPLLexer.TYPE_INTEGER || rightType != grammarPLLexer.TYPE_INTEGER)) {
            return;
        }

        converted.append(Utils.stringWithIndention("i32.gt_s\n", indentationLevel));
    }

    // Метод для обработки операций '<='
    private void typeOfLe(Integer leftType, Integer rightType) {
        if ((leftType != grammarPLLexer.TYPE_FLOAT || rightType != grammarPLLexer.TYPE_FLOAT) &&
                (leftType != grammarPLLexer.TYPE_INTEGER || rightType != grammarPLLexer.TYPE_INTEGER)) {
            return;
        }
        converted.append(Utils.stringWithIndention("i32.le_s\n", indentationLevel));
    }

    // Метод для обработки операций '>='
    private void typeOfGe(Integer leftType, Integer rightType) {
        if ((leftType != grammarPLLexer.TYPE_FLOAT || rightType != grammarPLLexer.TYPE_FLOAT) &&
                (leftType != grammarPLLexer.TYPE_INTEGER || rightType != grammarPLLexer.TYPE_INTEGER)) {
            return;
        }
        converted.append(Utils.stringWithIndention("i32.ge_s\n", indentationLevel));
    }

    // Метод для обработки операций '=='
    private void typeOfEq(Integer leftType, Integer rightType) {
        converted.append(Utils.stringWithIndention("i32.eq\n", indentationLevel));
    }

    // Метод для обработки операций '!='
    private void typeOfNeq(Integer leftType, Integer rightType) {
        converted.append(Utils.stringWithIndention("i32.ne\n", indentationLevel));
    }

    // Метод для обработки операций 'or'
    private void typeOfAnd(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.TYPE_BOOLEAN || rightType == grammarPLLexer.TYPE_BOOLEAN) {
            converted.append(Utils.stringWithIndention("i32.and\n", indentationLevel));
        }
    }

    // Метод для обработки операций 'and'
    private void typeOfOr(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.TYPE_BOOLEAN || rightType == grammarPLLexer.TYPE_BOOLEAN) {
            converted.append(Utils.stringWithIndention("i32.or\n", indentationLevel));
        }
    }

    // Метод для обработки операции '!'
    private void typeOfNot(Integer type) {
        if (type == grammarPLLexer.TYPE_BOOLEAN) {
            converted.append(Utils.stringWithIndention("i32.eqz\n", indentationLevel));
        }
    }

    private String getVariableName(String name) {
        return Objects.equals(functionScope.peek(), preprocessListener.getVariablesMap().get(scope.peek()).get(name).getScope())
                || Objects.equals(".", preprocessListener.getVariablesMap().get(scope.peek()).get(name).getScope()) ?
                name : preprocessListener.getVariablesMap().get(scope.peek()).get(name).getScope() + "__" + name;
    }
}

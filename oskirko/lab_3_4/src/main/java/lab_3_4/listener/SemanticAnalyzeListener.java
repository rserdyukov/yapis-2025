package lab_3_4.listener;

import lab_3_4.Constant;
import lab_3_4.grammarPLBaseListener;
import lab_3_4.grammarPLLexer;
import lab_3_4.grammarPLParser;
import lab_3_4.model.Error;
import lab_3_4.model.ErrorType;
import lab_3_4.model.Expression;
import lab_3_4.model.Typed;
import lab_3_4.model.Variable;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.Token;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.ParseTreeProperty;
import org.antlr.v4.runtime.tree.TerminalNode;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Stack;

// Класс для семантического анализатора
public class SemanticAnalyzeListener extends grammarPLBaseListener {

    private final Map<String, Map<String, Variable>> variablesMap;
    private final Map<String, Map<String, Expression>> expressionsMap;
    private final Stack<String> scope;
    private final List<Error> semanticErrors;
    private final ParseTreeProperty<Integer> typeContextProperty;
    private int ifCounter;
    private int forCounter;
    private int caseCounter;
    private int whileCounter;

    public SemanticAnalyzeListener() {
        this.variablesMap = new HashMap<>();
        this.variablesMap.put(".", new HashMap<>());
        this.expressionsMap = new HashMap<>();
        this.expressionsMap.put(".", new HashMap<>());
        this.semanticErrors = new ArrayList<>();
        this.typeContextProperty = new ParseTreeProperty<>();
        this.scope = new Stack<>();
        this.scope.push(".");
    }

    // Метод для входа в контекст декларации функции
    @Override
    public void enterFunctionDeclaration(grammarPLParser.FunctionDeclarationContext ctx) {
        String name = ctx.ID().getText();

        if (variablesMap.get(name) != null) {
            Token token = ctx.ID().getSymbol();
            semanticErrors.add(new Error(
                    token.getLine(),
                    token.getCharPositionInLine(),
                    String.format("Function '%s' is already exists", name),
                    ErrorType.SEMANTIC));
        }

        scope.push(name);
        variablesMap.put(name, new HashMap<>());
        expressionsMap.put(name, new HashMap<>());
        grammarPLParser.DeclarationFunctionParamListContext paramListCtx = ctx.declarationFunctionParamList();

        if (paramListCtx != null) {
            for (grammarPLParser.DeclarationFunctionParamContext paramCtx : paramListCtx.declarationFunctionParam()) {
                addParamVariable(name, paramCtx.ID().getSymbol(), paramCtx.paramType());
            }

            for (grammarPLParser.DeclarationFunctionResultParamContext resultParamCtx : paramListCtx.declarationFunctionResultParam()) {
                addParamVariable(name, resultParamCtx.ID().getSymbol(), resultParamCtx.paramType());
            }
        }
    }

    // Метод для выхода из контекста декларации функции
    @Override
    public void exitFunctionDeclaration(grammarPLParser.FunctionDeclarationContext ctx) {
        scope.pop();
    }

    // Метод для выхода из контекста простейшего элемента аргумента функции
    @Override
    public void exitFunctionArgPrimary(grammarPLParser.FunctionArgPrimaryContext ctx) {
        setTypeFromPrimary(ctx, ctx.INT(), ctx.FLOAT(), ctx.STRING(), ctx.ID(), ctx.arrayIndex());
    }

    // Метод для выхода из контекста простейшего элемента
    @Override
    public void exitPrimary(grammarPLParser.PrimaryContext ctx) {
        setTypeFromPrimary(ctx, ctx.INT(), ctx.FLOAT(), ctx.STRING(), ctx.ID(), ctx.arrayIndex());
    }

    // Метод для выхода из контекста выражения аргумента функции
    @Override
    public void exitFunctionArgExpr(grammarPLParser.FunctionArgExprContext ctx) {
        if (ctx.functionArgPrimary() != null) {
            boolean hasIncDec = !ctx.INCREMENT().isEmpty() || !ctx.DECREMENT().isEmpty();
            boolean hasNot = !ctx.NOT().isEmpty();
            handlePrimaryLike(ctx, ctx.functionArgPrimary(), hasIncDec, hasNot);
            return;
        }

        if (ctx.functionArgExpr().size() == 1) {
            Integer t = typeContextProperty.get(ctx.functionArgExpr(0));
            typeContextProperty.put(ctx, t);
            return;
        }

        if (ctx.functionArgExpr().size() == 2) {
            handleBinaryExpr(ctx, ctx.functionArgExpr(0), ctx.functionArgExpr(1));
        }
    }

    // Метод для выхода из контекста выражения
    @Override
    public void exitExpr(grammarPLParser.ExprContext ctx) {
        if (ctx.primary() != null) {
            boolean hasIncDec = !ctx.INCREMENT().isEmpty() || !ctx.DECREMENT().isEmpty();
            boolean hasNot = !ctx.NOT().isEmpty();
            handlePrimaryLike(ctx, ctx.primary(), hasIncDec, hasNot);
            return;
        }

        if (ctx.expr().size() == 1) {
            Integer t = typeContextProperty.get(ctx.expr(0));
            typeContextProperty.put(ctx, t);
            expressionsMap.get(scope.peek()).put(ctx.getText(), new Expression(ctx.getText(), t));
            return;
        }

        if (ctx.expr().size() == 2) {
            handleBinaryExpr(ctx, ctx.expr(0), ctx.expr(1));
        }
    }

    // Метод для выхода из контекста объясвления переменной
    @Override
    public void exitVarDeclarationStatement(grammarPLParser.VarDeclarationStatementContext ctx) {
        handleVarDeclaration(
                ctx.ID().getText(),
                ctx.declarationType(),
                ctx.arrayLiteral(),
                ctx.expr()
        );
    }

    // Метод для выхода из контекста объясвления переменной (без ';', для блока for)
    @Override
    public void exitVarDeclarationWithoutSemicolon(grammarPLParser.VarDeclarationWithoutSemicolonContext ctx) {
        handleVarDeclaration(
                ctx.ID().getText(),
                ctx.declarationType(),
                ctx.arrayLiteral(),
                ctx.expr()
        );
    }

    // Метод для выхода из контекста вызова функции
    @Override
    public void exitFunctionCall(grammarPLParser.FunctionCallContext ctx) {
        String name = ctx.ID().getText();
        List<Typed> actualArgs = new ArrayList<>();

        if (!Constant.FUNCTION_NAMES.contains(name)) {
            List<Variable> exceptedArgs = variablesMap.get(name).values().stream().filter(Variable::isParameter).toList();

            grammarPLParser.ArgListContext argListCtx = ctx.argList();

            if (argListCtx != null) {
                for (grammarPLParser.FunctionArgExprContext argCtx : argListCtx.functionArgExpr()) {
                    actualArgs.add(variablesMap.get(scope.peek()).get(argCtx.getText()) != null ?
                            variablesMap.get(scope.peek()).get(argCtx.getText()) :
                            expressionsMap.get(scope.peek()).get(argCtx.getText()));
                }
            }

            if (exceptedArgs.size() == actualArgs.size()) {

                for (int i = 0; i < actualArgs.size(); i++) {
                    if (exceptedArgs.get(i).getType() != actualArgs.get(i).getType()) {
                        Token token = ctx.getStart();
                        semanticErrors.add(new Error(
                                token.getLine(),
                                token.getCharPositionInLine(),
                                String.format("Function '%s' has another type of parameter at position %d", name, i),
                                ErrorType.SEMANTIC
                        ));
                    }
                }
            } else {
                Token token = ctx.getStart();
                semanticErrors.add(new Error(
                        token.getLine(),
                        token.getCharPositionInLine(),
                        String.format("Function '%s' has %d parameters but %d are passed", name, exceptedArgs.size(), actualArgs.size()),
                        ErrorType.SEMANTIC
                ));
            }
        }
    }

    // Метод для выхода из контекста присваивания значения переменной
    @Override
    public void exitAssignmentStatement(grammarPLParser.AssignmentStatementContext ctx) {
        String name = ctx.ID().getText();
        variablesMap.get(scope.peek()).get(name).setAssignedType(typeContextProperty.get(ctx.expr(0)));
    }

    // Метод для входа в контекст if-выражения
    @Override
    public void enterIfStatement(grammarPLParser.IfStatementContext ctx) {
        String scopeName = "if-" + ifCounter++;
        pushNewScope(scopeName);
    }

    // Метод для входа в контекст for-выражения
    @Override
    public void enterForStatement(grammarPLParser.ForStatementContext ctx) {
        String scopeName = "for-" + forCounter++;
        pushNewScope(scopeName);
    }

    // Метод для входа в контекст case-выражения
    @Override
    public void enterCaseBlock(grammarPLParser.CaseBlockContext ctx) {
        String scopeName = "case-" + caseCounter++;
        pushNewScope(scopeName);
    }

    // Метод для входа в контекст while-выражения
    @Override
    public void enterWhileStatement(grammarPLParser.WhileStatementContext ctx) {
        String scopeName = "while-" + whileCounter++;
        pushNewScope(scopeName);
    }

    // Метод для выхода из контекста if-выражения
    @Override
    public void exitIfStatement(grammarPLParser.IfStatementContext ctx) {
        scope.pop();
    }

    // Метод для выхода из контекста for-выражения
    @Override
    public void exitForStatement(grammarPLParser.ForStatementContext ctx) {
        scope.pop();
    }

    // Метод для выхода из контекста case-выражения
    @Override
    public void exitCaseBlock(grammarPLParser.CaseBlockContext ctx) {
        scope.pop();
    }

    // Метод для выхода из контекста while-выражения
    @Override
    public void exitWhileStatement(grammarPLParser.WhileStatementContext ctx) {
        scope.pop();
    }

    // Метод для получения семантических ошибок
    public List<Error> getSemanticErrors() {
        return semanticErrors;
    }

    // Метод для обработки простейших элементов выражения
    private void handlePrimaryLike(ParserRuleContext targetCtx, ParserRuleContext primaryCtx, boolean hasIncDec, boolean hasNot) {
        Integer primaryType = typeContextProperty.get(primaryCtx);

        if (hasIncDec) {
            if (primaryType != grammarPLLexer.TYPE_INTEGER && primaryType != grammarPLLexer.TYPE_FLOAT) {
                typeContextProperty.put(targetCtx, -1);

                Token token = primaryCtx.getStart();
                semanticErrors.add(new Error(
                        token.getLine(),
                        token.getCharPositionInLine(),
                        "Invalid increment or decrement type",
                        ErrorType.SEMANTIC
                ));

                return;
            }
        }

        if (hasNot) {
            typeContextProperty.put(targetCtx, typeOfNot(primaryType));
            expressionsMap.get(scope.peek()).put(primaryCtx.getText(), new Expression(primaryCtx.getText(), primaryType));

            if (typeOfNot(primaryType) == -1) {
                Token token = primaryCtx.getStart();
                semanticErrors.add(new Error(
                        token.getLine(),
                        token.getCharPositionInLine(),
                        "Invalid type for NOT operation",
                        ErrorType.SEMANTIC
                ));
            }

            return;
        }

        typeContextProperty.put(targetCtx, primaryType);
        expressionsMap.get(scope.peek()).put(primaryCtx.getText(), new Expression(primaryCtx.getText(), primaryType));
    }

    // Метод для обработки бинарных выражений
    private void handleBinaryExpr(ParserRuleContext targetCtx, ParserRuleContext leftCtx, ParserRuleContext rightCtx) {
        Integer leftType = typeContextProperty.get(leftCtx);
        Integer rightType = typeContextProperty.get(rightCtx);

        ParseTree operationNode = targetCtx.getChild(1);
        int operationType = ((TerminalNode) operationNode).getSymbol().getType();

        int resultType;
        switch (operationType) {
            case grammarPLLexer.PLUS -> resultType = typeOfPlus(leftType, rightType);
            case grammarPLLexer.MINUS -> resultType = typeOfMinus(leftType, rightType);
            case grammarPLLexer.MULT -> resultType = typeOfMultiplication(leftType, rightType);
            case grammarPLLexer.DIV -> resultType = typeOfDivision(leftType, rightType);
            case grammarPLLexer.REMDIV -> resultType = typeOfRemainderDivision(leftType, rightType);
            case grammarPLLexer.LT,
                 grammarPLLexer.LE,
                 grammarPLLexer.GT,
                 grammarPLLexer.GE -> resultType = typeOfLtGtLeGe(leftType, rightType);
            case grammarPLLexer.EQ,
                 grammarPLLexer.NEQ -> resultType = typeOfEqNeq(leftType, rightType);
            case grammarPLLexer.AND,
                 grammarPLLexer.OR -> resultType = typeOfAndOr(leftType, rightType);
            case grammarPLLexer.POW -> resultType = typeOfPow(leftType, rightType);
            default -> resultType = -1;
        }

        if (resultType == -1 && leftType != -1 && rightType != -1) {
            Token token = targetCtx.getStart();
            semanticErrors.add(new Error(
                    token.getLine(),
                    token.getCharPositionInLine(),
                    String.format("Operation %s is not suitable for operands of types %s and %s",
                            grammarPLLexer.VOCABULARY.getLiteralName(operationType),
                            grammarPLLexer.VOCABULARY.getLiteralName(leftType),
                            grammarPLLexer.VOCABULARY.getLiteralName(rightType)),
                    ErrorType.SEMANTIC));
        }

        typeContextProperty.put(targetCtx, resultType);
        expressionsMap.get(scope.peek()).put(targetCtx.getText(), new Expression(targetCtx.getText(), resultType));
    }

    // Метод для обработки объявления переменной
    private void handleVarDeclaration(
            String name,
            grammarPLParser.DeclarationTypeContext declTypeCtx,
            grammarPLParser.ArrayLiteralContext arrayLiteralCtx,
            grammarPLParser.ExprContext exprCtx
    ) {
        grammarPLParser.BaseTypeContext baseTypeCtx;
        boolean isArray = false;
        int type;
        Integer assignedType = null;

        if (declTypeCtx.baseType() != null) {
            baseTypeCtx = declTypeCtx.baseType();
        } else {
            baseTypeCtx = declTypeCtx.declarationArrayType().baseType();
            isArray = true;
        }

        type = getTypeFromBaseType(baseTypeCtx);

        if (arrayLiteralCtx != null) {
            for (grammarPLParser.ExprContext e : arrayLiteralCtx.expr()) {
                if (!Objects.equals(typeContextProperty.get(e), type)) {
                    assignedType = -1;

                    Token token = e.getStart();
                    semanticErrors.add(new Error(
                            token.getLine(),
                            token.getCharPositionInLine(),
                            "Incorrect array element type",
                            ErrorType.SEMANTIC
                    ));

                    break;
                }
            }
        } else if (exprCtx != null) {
            assignedType = typeContextProperty.get(exprCtx);
        }

        Variable newVariable = new Variable(
                name,
                type,
                assignedType,
                isArray,
                false,
                arrayLiteralCtx != null
        );
        variablesMap.get(scope.peek()).put(name, newVariable);

        if (newVariable.isArray() != newVariable.isAssignedTypeArray() ||
                (newVariable.getAssignedType() != null && newVariable.getAssignedType() != -1 && newVariable.getType() != newVariable.getAssignedType())) {
            Token token = exprCtx != null ? exprCtx.getStart() : arrayLiteralCtx.getStart();
            semanticErrors.add(new Error(
                    token.getLine(),
                    token.getCharPositionInLine(),
                    "Type mismatch",
                    ErrorType.SEMANTIC
            ));
        }
    }

    // Метод для получения типа из контекста базового типа
    private int getTypeFromBaseType(grammarPLParser.BaseTypeContext baseTypeCtx) {
        return switch (baseTypeCtx.getStart().getType()) {
            case grammarPLLexer.TYPE_FLOAT -> grammarPLLexer.TYPE_FLOAT;
            case grammarPLLexer.TYPE_INTEGER -> grammarPLLexer.TYPE_INTEGER;
            case grammarPLLexer.TYPE_STRING -> grammarPLLexer.TYPE_STRING;
            case grammarPLLexer.TYPE_BOOLEAN -> grammarPLLexer.TYPE_BOOLEAN;
            default -> -1;
        };
    }

    // Метод для присвоения типа контексту простейшего элемента выражения
    private void setTypeFromPrimary(ParserRuleContext ctx,
                                    TerminalNode intNode,
                                    TerminalNode floatNode,
                                    TerminalNode stringNode,
                                    TerminalNode idNode,
                                    grammarPLParser.ArrayIndexContext arrayIndexCtx) {
        if (intNode != null) {
            typeContextProperty.put(ctx, grammarPLLexer.TYPE_INTEGER);
            return;
        }

        if (floatNode != null) {
            typeContextProperty.put(ctx, grammarPLLexer.TYPE_FLOAT);
            return;
        }

        if (stringNode != null) {
            typeContextProperty.put(ctx, grammarPLLexer.TYPE_STRING);
            return;
        }

        if (idNode != null) {
            String name = idNode.getText();
            int type = getVariableType(name);

            if (variablesMap.get(scope.peek()).get(name) == null) {
                Token token = idNode.getSymbol();
                semanticErrors.add(new Error(
                        token.getLine(),
                        token.getCharPositionInLine(),
                        String.format("Undefined variable '%s'", name),
                        ErrorType.SEMANTIC));
            }

            typeContextProperty.put(ctx, type);
            return;
        }

        if (arrayIndexCtx != null) {
            String name = arrayIndexCtx.ID().getText();
            int type = getVariableType(name);
            typeContextProperty.put(ctx, type);
            return;
        }

        typeContextProperty.put(ctx, -1);
    }

    // Метод для получения типа переменной по имени
    private int getVariableType(String name) {
        Map<String, Variable> scopeVars = variablesMap.get(scope.peek());
        if (scopeVars == null) return -1;
        Variable var = scopeVars.get(name);
        return var != null ? var.getType() : -1;
    }

    // Метод для добавления переменной, которая является параметром функции
    private void addParamVariable(String functionName, Token idToken, grammarPLParser.ParamTypeContext paramType) {
        boolean isArray = false;
        grammarPLParser.BaseTypeContext baseTypeCtx = paramType.baseType();
        if (baseTypeCtx == null) {
            baseTypeCtx = paramType.paramArrayType().baseType();
            isArray = true;
        }

        int type = getTypeFromBaseType(baseTypeCtx);

        String id = idToken.getText();
        variablesMap.get(functionName).put(id, new Variable(id, type, null, isArray, true, true));
    }

    // Метод для добавляения новой области видимости
    private void pushNewScope(String scopeName) {
        Map<String, Variable> parentVars = variablesMap.getOrDefault(scope.peek(), Collections.emptyMap());
        Map<String, Expression> parentExprs = expressionsMap.getOrDefault(scope.peek(), Collections.emptyMap());

        variablesMap.put(scopeName, new HashMap<>(parentVars));
        expressionsMap.put(scopeName, new HashMap<>(parentExprs));

        scope.push(scopeName);
    }

    // Метод для получения типа результата операции '-'
    private Integer typeOfMinus(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
            return grammarPLLexer.TYPE_FLOAT;
        } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
            return grammarPLLexer.TYPE_INTEGER;
        }

        return -1;
    }

    // Метод для получения типа результата операции '+'
    private Integer typeOfPlus(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.TYPE_STRING || rightType == grammarPLLexer.TYPE_STRING) {
            return grammarPLLexer.TYPE_STRING;
        } else if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
            return grammarPLLexer.TYPE_FLOAT;
        } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
            return grammarPLLexer.TYPE_INTEGER;
        }

        return -1;
    }

    // Метод для получения типа результата операции '*'
    private Integer typeOfMultiplication(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
            return grammarPLLexer.TYPE_FLOAT;
        } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
            return grammarPLLexer.TYPE_INTEGER;
        }

        return -1;
    }

    // Метод для получения типа результата операции '/'
    private Integer typeOfDivision(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
            return grammarPLLexer.TYPE_FLOAT;
        } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
            return grammarPLLexer.TYPE_INTEGER;
        }

        return -1;
    }

    // Метод для получения типа результата операции '%'
    private Integer typeOfRemainderDivision(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.TYPE_FLOAT || rightType == grammarPLLexer.TYPE_FLOAT) {
            return grammarPLLexer.TYPE_FLOAT;
        } else if (leftType == grammarPLLexer.TYPE_INTEGER && rightType == grammarPLLexer.TYPE_INTEGER) {
            return grammarPLLexer.TYPE_INTEGER;
        }

        return -1;
    }

    // Метод для получения типа результата операций '<', '>', '<=', '>='
    private Integer typeOfLtGtLeGe(Integer leftType, Integer rightType) {
        if ((leftType != grammarPLLexer.TYPE_FLOAT || rightType != grammarPLLexer.TYPE_FLOAT) &&
                (leftType != grammarPLLexer.TYPE_INTEGER || rightType != grammarPLLexer.TYPE_INTEGER)) {
            return -1;
        }

        return grammarPLLexer.TYPE_BOOLEAN;
    }

    // Метод для получения типа результата операций '==', '!='
    private Integer typeOfEqNeq(Integer leftType, Integer rightType) {
        return grammarPLLexer.TYPE_BOOLEAN;
    }

    // Метод для получения типа результата операций 'or', 'and'
    private Integer typeOfAndOr(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.TYPE_BOOLEAN || rightType == grammarPLLexer.TYPE_BOOLEAN) {
            return grammarPLLexer.TYPE_BOOLEAN;
        }

        return -1;
    }

    // Метод для получения типа результата операции '!'
    private Integer typeOfNot(Integer type) {
        if (type == grammarPLLexer.TYPE_BOOLEAN) {
            return grammarPLLexer.TYPE_BOOLEAN;
        }

        return -1;
    }

    // Метод для получения типа результата операции '^'
    private Integer typeOfPow(Integer leftType, Integer rightType) {
        if (leftType == grammarPLLexer.STRING || rightType == grammarPLLexer.STRING ||
                leftType == grammarPLLexer.BOOLEAN || rightType == grammarPLLexer.BOOLEAN) {
            return -1;
        }

        return grammarPLLexer.TYPE_FLOAT;
    }
}

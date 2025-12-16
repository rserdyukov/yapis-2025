package io.hohichh.mcl.compiler.analyzer.handlers.nodes;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.FunctionSymbol;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.MclType;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.Symbol;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.VariableSymbol;
import io.hohichh.mcl.compiler.analyzer.handlers.scope.ScopeManager;
import org.antlr.v4.runtime.Token;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class FunctionHandler {
    private final AnalysisContext env;

    public FunctionHandler(AnalysisContext context){
        env = context;
    }

    public void enterFunctionDefinition(MCLParser.FunctionDefinitionContext ctx){
        ScopeManager scopeManager = env.getScopeManager();

        String funcName = ctx.IDENTIFIER().getText();
        Token funcNameToken = ctx.IDENTIFIER().getSymbol();

        MclType returnType = env.resolveType(ctx.type());
        List<VariableSymbol> parameters = new ArrayList<>();
        checkFuncParamDoubles(ctx, parameters);

        FunctionSymbol funcSymbol = new FunctionSymbol(funcName, returnType, parameters);


        List<Symbol> existing = scopeManager.lookupInCurrent(funcName);
        if (existing != null && !existing.isEmpty()) {
            env.addError(funcNameToken,
                    "Function '" + funcName + "' is already defined. User function overloading is not allowed.");

        } else {
            scopeManager.define(funcSymbol);
        }

        env.setCurrentFunction(funcSymbol);
        env.setCurrentFunctionHasReturn(false);

        scopeManager.enterScope();

        for (VariableSymbol param : parameters) {
            scopeManager.define(param);
        }
    }


//    public void enterFunctionDefinition(MCLParser.FunctionDefinitionContext ctx){
//        ScopeManager scopeManager = env.getScopeManager();
//
//        String funcName = ctx.IDENTIFIER().getText();
//        Token funcNameToken = ctx.IDENTIFIER().getSymbol();
//
//        List<Symbol> existing = scopeManager.lookupInCurrent(funcName);
//        if (existing != null && !existing.isEmpty()) {
//            env.addError(funcNameToken,
//                    "Function '" + funcName + "' is already defined. User function overloading is not allowed.");
//            scopeManager.enterScope();
//            return;
//        }
//
//        MclType returnType = env.resolveType(ctx.type());
//        List<VariableSymbol> parameters = new ArrayList<>();
//        checkFuncParamDoubles(ctx, parameters);
//
//        FunctionSymbol funcSymbol = new FunctionSymbol(funcName, returnType, parameters);
//        scopeManager.define(funcSymbol);
//
//        env.setCurrentFunction(funcSymbol);
//        env.setCurrentFunctionHasReturn(false);
//
//        scopeManager.enterScope();
//
//        for (VariableSymbol param : parameters) {
//            scopeManager.define(param);
//        }
//    }

    public void exitFunctionDefinition(MCLParser.FunctionDefinitionContext ctx){
        ScopeManager scopeManager = env.getScopeManager();

        // 6. Проверка наличия return для не-void функций
        if (env.getCurrentFunction() != null) {
            if (env.getCurrentFunction().getType() != MclType.VOID && !env.isCurrentFunctionHasReturn()) {
                env.addError(ctx.IDENTIFIER().getSymbol(),
                        "Function '" + env.getCurrentFunction().getName()
                                + "' must return a value of type "
                                + env.getCurrentFunction().getType());
            }
        }

        scopeManager.exitScope();

        env.setCurrentFunction(null);
        env.setCurrentFunctionHasReturn(false);
    }

    private void checkFuncParamDoubles(MCLParser.FunctionDefinitionContext ctx, List<VariableSymbol> parameters){
        Set<String> parameterNames = new HashSet<>();

        if (ctx.parameterList() != null) {
            for (MCLParser.ParameterContext paramCtx : ctx.parameterList().parameter()) {
                String paramName = paramCtx.IDENTIFIER().getText();
                MclType paramType = env.resolveType(paramCtx.type());
                Token paramToken = paramCtx.IDENTIFIER().getSymbol();

                if (!parameterNames.add(paramName)) {
                    env.addError(paramToken, "Duplicate parameter name: '" + paramName + "'");
                }

                parameters.add(new VariableSymbol(paramName, paramType));
            }
        }
    }

    //--------------------------LAMBDA---------------------------

    public void enterLambdaExpression(MCLParser.LambdaExpressionContext ctx) {
        env.getScopeManager().enterScope();

        if (ctx.IDENTIFIER() != null && !ctx.IDENTIFIER().isEmpty()) {
            Set<String> paramNames = new HashSet<>();

            for (var idNode : ctx.IDENTIFIER()) {
                String paramName = idNode.getText();
                Token paramToken = idNode.getSymbol();

                if (!paramNames.add(paramName)) {
                    env.addError(paramToken, "Duplicate lambda parameter: '" + paramName + "'");
                }
                env.getScopeManager().define(new VariableSymbol(paramName, MclType.UNKNOWN));
            }
        }
    }

    public void exitLambdaExpression(MCLParser.LambdaExpressionContext ctx) {
        MclType bodyType = env.getExpressionTypes().get(ctx.expression());

        env.getExpressionTypes().put(ctx, bodyType != null ? bodyType : MclType.UNKNOWN);

        env.getScopeManager().exitScope();
    }
}
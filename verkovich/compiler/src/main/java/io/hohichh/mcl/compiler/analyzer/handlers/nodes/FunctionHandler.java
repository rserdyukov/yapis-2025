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
        //function overloading check
        List<Symbol> existing = scopeManager.lookupInCurrent(funcName);
        if (existing != null && !existing.isEmpty()) {
            env.addError(funcNameToken,
                    "Function '" + funcName + "' is already defined. User function overloading is not allowed.");
            scopeManager.enterScope();
            return;
        }

        MclType returnType = env.resolveType(ctx.type());
        List<VariableSymbol> parameters = new ArrayList<>();
        checkFuncParamDoubles(ctx, parameters);

        //add func to current scope
        FunctionSymbol funcSymbol = new FunctionSymbol(funcName, returnType, parameters);
        scopeManager.define(funcSymbol);

        env.setCurrentFunction(funcSymbol);
        env.setCurrentFunctionHasReturn(false);

        //enter local scope of function
        scopeManager.enterScope();

        for (VariableSymbol param : parameters) {
            scopeManager.define(param);
        }
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


    public void exitFunctionDefinition(MCLParser.FunctionDefinitionContext ctx){
        ScopeManager scopeManager = env.getScopeManager();

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


}

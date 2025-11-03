package io.hohichh.mcl.compiler.analyzer.handlers.nodes;

import io.hohichh.mcl.compiler.MCLParser;

public class SuiteHandler {
    private final AnalysisContext env;

    public SuiteHandler(AnalysisContext context){
        env = context;
    }

    public void enterSuite(MCLParser.SuiteContext ctx){
        if (!(ctx.getParent() instanceof MCLParser.FunctionDefinitionContext)) {
            env.getScopeManager().enterScope();
        }
    }

    public void exitSuite(MCLParser.SuiteContext ctx){
        if (!(ctx.getParent() instanceof MCLParser.FunctionDefinitionContext)) {
            env.getScopeManager().exitScope();
        }
    }
}

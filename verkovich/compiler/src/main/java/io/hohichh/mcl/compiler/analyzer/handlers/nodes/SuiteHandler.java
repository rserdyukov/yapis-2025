package io.hohichh.mcl.compiler.analyzer.handlers.nodes;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.MclType;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.VariableSymbol;

public class SuiteHandler {
    private final AnalysisContext env;

    public SuiteHandler(AnalysisContext context){
        env = context;
    }

    public void enterSuite(MCLParser.SuiteContext ctx) {
        if (ctx.getParent() instanceof MCLParser.FunctionDefinitionContext) {
            return;
        }

        env.getScopeManager().enterScope();

        if (ctx.getParent() instanceof MCLParser.ForStatementContext forCtx) {
            defineForLoopVariable(forCtx);
        }
    }

    public void exitSuite(MCLParser.SuiteContext ctx) {
        if (!(ctx.getParent() instanceof MCLParser.FunctionDefinitionContext)) {
            env.getScopeManager().exitScope();
        }
    }

    private void defineForLoopVariable(MCLParser.ForStatementContext forCtx) {
        String varName = forCtx.IDENTIFIER().getText();

        MclType iterableType = env.getExpressionTypes().get(forCtx.expression());
        MclType varType = MclType.UNKNOWN;

        if (iterableType != null && iterableType != MclType.UNKNOWN) {
            switch (iterableType) {
                case RANGE:
                    varType = MclType.INT;
                    break;
                case VECTOR:
                    varType = MclType.FLOAT;
                    break;
                case MATRIX:
                    varType = MclType.VECTOR;
                    break;
                case STRING:
                    varType = MclType.STRING;
                    break;
                default:
                    varType = MclType.UNKNOWN;
            }
        }

        env.getScopeManager().define(new VariableSymbol(varName, varType));
    }
}
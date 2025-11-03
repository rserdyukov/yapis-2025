package io.hohichh.mcl.compiler.analyzer.handlers.nodes;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.FunctionSymbol;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.MclType;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.Symbol;
import io.hohichh.mcl.compiler.analyzer.handlers.scope.ScopeManager;
import org.antlr.v4.runtime.Token;

import java.util.List;

public class PrimaryHandler {
    private final AnalysisContext env;

    public PrimaryHandler(AnalysisContext context){
        env = context;
    }

    public void exitIdentifier(MCLParser.IdentifierExprContext ctx){
        var expressionTypes = env.getExpressionTypes();
        ScopeManager scopeManager = new ScopeManager();
        String varName = ctx.IDENTIFIER().getText();
        Token varToken = ctx.IDENTIFIER().getSymbol();

        List<Symbol> symbols = scopeManager.lookup(varName);

        //сheck if identidier belongs to undefined or local-scope variable
        if (symbols == null || symbols.isEmpty()) {
            env.addError(varToken, "Undeclared variable: '" + varName + "'");
            expressionTypes.put(ctx, MclType.UNKNOWN);
            return;
        }

        //check mistype of function call
        Symbol symbol = symbols.getFirst();
        if (symbol instanceof FunctionSymbol) {
            env.addError(varToken, "Cannot use function '" + varName + "' as a variable. Did you mean to call it using '()'?");
            expressionTypes.put(ctx, MclType.UNKNOWN);
            return;
        }
        expressionTypes.put(ctx, symbol.getType());
    }
}

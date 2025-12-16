package io.hohichh.mcl.compiler.analyzer.handlers.nodes;

import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.FunctionSymbol;
import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.MclType;
import io.hohichh.mcl.compiler.analyzer.handlers.scope.ScopeManager;
import io.hohichh.mcl.compiler.analyzer.artefacts.SemanticError;
import org.antlr.v4.runtime.ParserRuleContext;
import org.antlr.v4.runtime.Token;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;


public class AnalysisContext {
    private final ScopeManager scopeManager = new ScopeManager();
    private final Map<ParserRuleContext, MclType> expressionTypes = new HashMap<>();
    private final Map<ParserRuleContext, MclType> assignableTypes = new HashMap<>();
    private final List<SemanticError> errors = new ArrayList<>();

    private FunctionSymbol currentFunction = null;
    private boolean currentFunctionHasReturn = false;

    public ScopeManager getScopeManager() {
        return scopeManager;
    }

    public Map<ParserRuleContext, MclType> getExpressionTypes() {
        return expressionTypes;
    }

    public Map<ParserRuleContext, MclType> getAssignableTypes() {
        return assignableTypes;
    }

    public List<SemanticError> getErrors() {
        return errors;
    }

    public FunctionSymbol getCurrentFunction() {
        return currentFunction;
    }

    public void setCurrentFunction(FunctionSymbol currentFunction) {
        this.currentFunction = currentFunction;
    }

    public boolean isCurrentFunctionHasReturn() {
        return currentFunctionHasReturn;
    }

    public void setCurrentFunctionHasReturn(boolean currentFunctionHasReturn) {
        this.currentFunctionHasReturn = currentFunctionHasReturn;
    }

    public void addError(Token token, String message) {
        errors.add(new SemanticError(token, message));
    }

    public void addError(ParserRuleContext ctx, String message){
        errors.add(new SemanticError(
                ctx.getStart(), message
        ));
    }

    public MclType resolveType(MCLParser.TypeContext ctx) {
        if (ctx.scalarType() != null) {
            if (ctx.scalarType().INT_TYPE() != null) return MclType.INT;
            if (ctx.scalarType().FLOAT_TYPE() != null) return MclType.FLOAT;
        }
        if (ctx.VECTOR_TYPE() != null) return MclType.VECTOR;
        if (ctx.MATRIX_TYPE() != null) return MclType.MATRIX;
        if (ctx.BOOLEAN_TYPE() != null) return MclType.BOOLEAN;
        if (ctx.STRING_TYPE() != null) return MclType.STRING;
        if (ctx.TUPLE_TYPE() != null) return MclType.TUPLE;
        if (ctx.VOID_TYPE() != null) return MclType.VOID;

        return MclType.UNKNOWN;
    }
}

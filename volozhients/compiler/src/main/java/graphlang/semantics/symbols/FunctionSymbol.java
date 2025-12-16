package graphlang.semantics.symbols;

import graphlang.semantics.GraphLangType;

import java.util.List;

public record FunctionSymbol(String name, GraphLangType type, List<VariableSymbol> parameters) implements Symbol {

    public FunctionSymbol {
        parameters = List.copyOf(parameters);
    }

    public GraphLangType returnType() {
        return type();
    }
}

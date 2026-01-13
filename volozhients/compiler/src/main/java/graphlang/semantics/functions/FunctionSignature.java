package graphlang.semantics.functions;

import graphlang.semantics.GraphLangType;

import java.util.List;

public record FunctionSignature(GraphLangType returnType, List<GraphLangType> parameterTypes) {
    public FunctionSignature {
        parameterTypes = List.copyOf(parameterTypes);
    }
}

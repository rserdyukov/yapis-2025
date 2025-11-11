package graphlang.semantics.symbols;

import graphlang.semantics.GraphLangType;

public record VariableSymbol(String name, GraphLangType type) implements Symbol {}
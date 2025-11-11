package graphlang.semantics.symbols;

import graphlang.semantics.GraphLangType;

public interface Symbol {
    String name();
    GraphLangType type();
}

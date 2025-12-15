package graphlang.semantics;

import graphlang.semantics.symbols.Symbol;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Optional;

public final class Scope {

    private final Scope parent;
    private final Map<String, Symbol> symbols = new LinkedHashMap<>();

    public Scope(Scope parent) {
        this.parent = parent;
    }

    public Scope parent() {
        return parent;
    }

    public void define(Symbol symbol) {
        if (symbols.containsKey(symbol.name())) {
            throw new SemanticException("Symbol '%s' already declared in this scope".formatted(symbol.name()));
        }
        symbols.put(symbol.name(), symbol);
    }

    public Optional<Symbol> resolve(String name) {
        Scope scope = this;
        while (scope != null) {
            Symbol symbol = scope.symbols.get(name);
            if (symbol != null) {
                return Optional.of(symbol);
            }
            scope = scope.parent;
        }
        return Optional.empty();
    }

    public Optional<Symbol> resolveLocal(String name) {
        return Optional.ofNullable(symbols.get(name));
    }
}

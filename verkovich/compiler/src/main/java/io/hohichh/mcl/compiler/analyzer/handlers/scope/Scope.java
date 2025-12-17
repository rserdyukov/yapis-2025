package io.hohichh.mcl.compiler.analyzer.handlers.scope;

import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.Symbol;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Scope {

    private final Map<String, List<Symbol>> symbols = new HashMap<>();

    private final Scope parent;

    public Scope(Scope parent) {
        this.parent = parent;
    }


    public void define(Symbol symbol) {
        symbols.computeIfAbsent(symbol.getName(), k -> new ArrayList<>()).add(symbol);
    }

    public List<Symbol> find(String name) {
        List<Symbol> symbolList = symbols.get(name);
        if (symbolList != null) {
            return symbolList;
        }

        if (parent != null) {
            return parent.find(name);
        }

        return null;
    }

    public List<Symbol> findInCurrent(String name) {
        return symbols.get(name);
    }
}
package io.hohichh.mcl.compiler.analyzer.handlers.scope;

import io.hohichh.mcl.compiler.analyzer.artefacts.atoms.Symbol;

import java.util.List;
import java.util.Stack;

public class ScopeManager {

    private final Stack<Scope> scopeStack = new Stack<>();

    public ScopeManager() {
        enterScope();
    }

    public Scope getCurrentScope() {
        return scopeStack.peek();
    }

    public void enterScope() {
        Scope parent = scopeStack.isEmpty() ? null : getCurrentScope();
        scopeStack.push(new Scope(parent));
    }

    public void exitScope() {
        scopeStack.pop();
    }

    public void define(Symbol symbol) {
        getCurrentScope().define(symbol);
    }

    public List<Symbol> lookup(String name) {
        return getCurrentScope().find(name);
    }

    public List<Symbol> lookupInCurrent(String name) {
        return getCurrentScope().findInCurrent(name);
    }
}
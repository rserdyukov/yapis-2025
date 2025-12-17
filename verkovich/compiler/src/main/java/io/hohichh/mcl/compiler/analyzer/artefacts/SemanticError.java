package io.hohichh.mcl.compiler.analyzer.artefacts;

import org.antlr.v4.runtime.Token;

public record SemanticError(int line, int column, String message) {

    public SemanticError(Token token, String message) {
        this(token.getLine(), token.getCharPositionInLine(), message);
    }

    @Override
    public String toString() {
        return "Semantic Error at [" + line + ":" + column + "]: " + message;
    }
}
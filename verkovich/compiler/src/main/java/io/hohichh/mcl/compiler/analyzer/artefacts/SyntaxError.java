package io.hohichh.mcl.compiler.analyzer.artefacts;

public record SyntaxError(int line, int column, String message) {

    @Override
    public String toString() {
        return "Error at [" + line + ":" + column + "]: " + message;
    }
}
package io.hohichh.mcl.compiler.analyzer.artefacts.atoms;

public record VariableSymbol(String name, MclType type) implements Symbol {
    @Override
    public String getName() {
        return name;
    }

    @Override
    public MclType getType() {
        return type;
    }
}
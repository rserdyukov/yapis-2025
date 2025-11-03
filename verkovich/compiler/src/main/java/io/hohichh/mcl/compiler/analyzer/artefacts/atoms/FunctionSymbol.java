package io.hohichh.mcl.compiler.analyzer.artefacts.atoms;

import java.util.List;

public record FunctionSymbol(String name,
                             MclType returnType,
                             List<VariableSymbol> parameters) implements Symbol {
    @Override
    public String getName() {
        return name;
    }

    @Override
    public MclType getType() {
        return returnType;
    }
}

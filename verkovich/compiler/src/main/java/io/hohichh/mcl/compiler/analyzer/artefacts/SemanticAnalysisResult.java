package io.hohichh.mcl.compiler.analyzer.artefacts;

import java.util.List;


public record SemanticAnalysisResult(List<SemanticError> errors) {

    public boolean hasErrors() {
        return !errors.isEmpty();
    }
}
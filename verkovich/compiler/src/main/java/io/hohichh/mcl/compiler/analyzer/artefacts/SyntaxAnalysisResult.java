package io.hohichh.mcl.compiler.analyzer.artefacts;

import org.antlr.v4.runtime.tree.ParseTree;
import java.util.List;

public record SyntaxAnalysisResult(ParseTree tree, List<SyntaxError> errors) {

    public boolean hasErrors() {
        return !errors.isEmpty();
    }
}
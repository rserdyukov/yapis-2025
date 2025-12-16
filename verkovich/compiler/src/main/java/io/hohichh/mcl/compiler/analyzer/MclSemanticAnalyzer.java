package io.hohichh.mcl.compiler.analyzer;

import io.hohichh.mcl.compiler.analyzer.artefacts.SemanticAnalysisResult;
import io.hohichh.mcl.compiler.analyzer.artefacts.SyntaxAnalysisResult;
import io.hohichh.mcl.compiler.analyzer.handlers.SemanticErrorListener;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.ParseTreeWalker;

import java.util.List;


public class MclSemanticAnalyzer {


    public SemanticAnalysisResult processSyntaxTree(SyntaxAnalysisResult syntaxResult) {
        if (syntaxResult.hasErrors()) {
            return new SemanticAnalysisResult(List.of());
        }

        ParseTree tree = syntaxResult.tree();

        ParseTreeWalker walker = new ParseTreeWalker();

        SemanticErrorListener listener = new SemanticErrorListener();

        walker.walk(listener, tree);

        return new SemanticAnalysisResult(listener.getErrors());
    }
}
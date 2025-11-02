package io.hohichh.mcl.compiler.analyzer;

import io.hohichh.mcl.compiler.MCLLexer;
import io.hohichh.mcl.compiler.MCLParser;
import io.hohichh.mcl.compiler.analyzer.handlers.IndentHandlingLexer;
import io.hohichh.mcl.compiler.analyzer.artefacts.SyntaxAnalysisResult;
import io.hohichh.mcl.compiler.analyzer.handlers.SyntaxErrorListener;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.tree.ParseTree;

import java.io.IOException;
import java.nio.file.Path;

public class MclSyntaxAnalyzer {

    public SyntaxAnalysisResult processFile(String filePath) throws IOException {
        CharStream input = CharStreams.fromPath(Path.of(filePath));

        MCLLexer lexer = new IndentHandlingLexer(input);
        SyntaxErrorListener errorListener = new SyntaxErrorListener();

        lexer.removeErrorListeners();
        lexer.addErrorListener(errorListener);

        CommonTokenStream tokens = new CommonTokenStream(lexer);

        MCLParser parser = new MCLParser(tokens);
        parser.removeErrorListeners();
        parser.addErrorListener(errorListener);

        ParseTree tree = parser.program();

        return new SyntaxAnalysisResult(tree, errorListener.getErrors());
    }
}
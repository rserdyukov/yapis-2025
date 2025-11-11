package graphlang;

import graphlang.frontend.GraphLangParserFacade;
import graphlang.frontend.SyntaxException;
import graphlang.semantics.GraphLangSemanticAnalyzer;
import graphlang.semantics.SemanticException;
import graphlang.GraphLangParser;
import org.antlr.v4.runtime.tree.ParseTree;

import java.nio.file.Path;

public final class App {

    private App() {}

    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            System.err.println("Usage: java -jar graphlang-compiler.jar <source-file>");
            System.exit(1);
        }

        Path sourcePath = Path.of(args[0]);
        try {
            GraphLangParserFacade.ParseResult parseResult = GraphLangParserFacade.parseFile(sourcePath);
            ParseTree tree = parseResult.tree();
            GraphLangParser parser = parseResult.parser();

            GraphLangSemanticAnalyzer semanticAnalyzer = new GraphLangSemanticAnalyzer();
            semanticAnalyzer.visit(tree);

            System.out.println("Compilation succeeded. No semantic errors.");
        } catch (SyntaxException | SemanticException ex) {
            System.err.println(ex.getMessage());
            System.exit(2);
        }
    }
}
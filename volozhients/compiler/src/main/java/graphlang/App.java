package graphlang;

import graphlang.frontend.GraphLangParserFacade;
import graphlang.frontend.SyntaxException;
import graphlang.semantics.GraphLangSemanticAnalyzer;
import graphlang.semantics.SemanticException;
import org.antlr.v4.runtime.tree.ParseTree;

import java.nio.file.Path;
import java.util.List;

public final class App {

    private static final List<Path> SOURCE_FILES = List.of(
            Path.of("/Users/wuttang/GitRepositories/yapis-2025/volozhients/examples/error_syntax_1.txt")
    );

    private App() {}

    public static void main(String[] args) {
        boolean hasErrors = false;

        for (Path sourcePath : SOURCE_FILES) {
            System.out.println("=== Checking file: " + sourcePath + " ===");
            try {
                GraphLangParserFacade.ParseResult parseResult = GraphLangParserFacade.parseFile(sourcePath);
                ParseTree tree = parseResult.tree();

                GraphLangSemanticAnalyzer semanticAnalyzer = new GraphLangSemanticAnalyzer();
                semanticAnalyzer.visit(tree);

                System.out.println("✓ Compilation succeeded. No semantic errors.\n");
            } catch (SyntaxException | SemanticException ex) {
                hasErrors = true;
                System.err.println("✗ " + ex.getMessage() + "\n");
            } catch (Exception ex) {
                hasErrors = true;
                System.err.println("✗ Unexpected error: " + ex.getMessage());
                ex.printStackTrace(System.err);
                System.err.println();
            }
        }

        if (hasErrors) {
            System.exit(2);
        }
    }
}
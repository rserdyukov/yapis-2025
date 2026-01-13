package graphlang;

import graphlang.frontend.GraphLangParserFacade;
import graphlang.frontend.SyntaxException;
import graphlang.semantics.GraphLangSemanticAnalyzer;
import graphlang.semantics.SemanticException;
import graphlang.GraphLangParser;
import org.antlr.v4.runtime.tree.ParseTree;

import java.nio.file.Path;

import graphlang.backend.LLVMCompiler;

public final class App {

    private App() {}

    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            System.err.println("Usage: java -jar graphlang-compiler.jar <source-file> [<output-exe>]");
            System.exit(1);
        }

        Path sourcePath = Path.of(args[0]);
        Path outputExe;
        if (args.length > 1) {
            outputExe = Path.of(args[1]);
        } else {
            String base = sourcePath.getFileName().toString();
            if (base.contains(".")) {
                base = base.substring(0, base.lastIndexOf('.'));
            }
            outputExe = sourcePath.resolveSibling(base);
        }

        try {
            GraphLangParserFacade.ParseResult parseResult = GraphLangParserFacade.parseFile(sourcePath);
            ParseTree tree = parseResult.tree();
            GraphLangParser parser = parseResult.parser();

            GraphLangSemanticAnalyzer semanticAnalyzer = new GraphLangSemanticAnalyzer();
            semanticAnalyzer.visit(tree);

            LLVMCompiler compiler = new LLVMCompiler();
            LLVMCompiler.CompilationResult result = compiler.compileToExecutable(tree, parser, sourcePath, outputExe);

            System.out.println("LLVM IR written to: " + result.llvmIrPath());
            System.out.println("Executable written to: " + result.executablePath());
            System.out.println("Compilation succeeded.");
        } catch (SyntaxException | SemanticException ex) {
            System.err.println(ex.getMessage());
            System.exit(2);
        }
    }
}
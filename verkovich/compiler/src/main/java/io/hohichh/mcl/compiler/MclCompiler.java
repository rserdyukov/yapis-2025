package io.hohichh.mcl.compiler;

import io.hohichh.mcl.compiler.analyzer.MclSemanticAnalyzer;
import io.hohichh.mcl.compiler.analyzer.MclSyntaxAnalyzer;
import io.hohichh.mcl.compiler.analyzer.artefacts.SemanticAnalysisResult;
import io.hohichh.mcl.compiler.analyzer.artefacts.SemanticError;
import io.hohichh.mcl.compiler.analyzer.artefacts.SyntaxAnalysisResult;
import io.hohichh.mcl.compiler.analyzer.artefacts.SyntaxError;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class MclCompiler {

    public static void main(String[] args) {
        String pathString = args.length > 0 ? args[0] : ".";
        Path startPath = Paths.get(pathString);

        if (!Files.exists(startPath)) {
            System.err.println("Error: Path does not exist: " + startPath.toAbsolutePath());
            System.exit(1);
        }

        try {
            List<Path> mclFiles;

            if (Files.isRegularFile(startPath)) {
                if (startPath.toString().endsWith(".mcl")) {
                    mclFiles = List.of(startPath);
                } else {
                    System.err.println("Error: Input file must have .mcl extension");
                    return;
                }
            } else {
                try (Stream<Path> walk = Files.walk(startPath)) {
                    mclFiles = walk
                            .filter(p -> !Files.isDirectory(p))
                            .filter(p -> p.toString().endsWith(".mcl"))
                            .collect(Collectors.toList());
                }
            }

            if (mclFiles.isEmpty()) {
                System.out.println("No .mcl files found in " + startPath.toAbsolutePath());
                return;
            }

            System.out.println("Found " + mclFiles.size() + " file(s) to compile.\n");

            boolean hasErrors = false;

            for (Path path : mclFiles) {
                if (!processFile(path.toString())) {
                    hasErrors = true;
                }
            }

            if (hasErrors) {
                System.exit(1);
            }

        } catch (IOException e) {
            System.err.println("System Error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static boolean processFile(String filePath) {
        System.out.println(">> Compiling: " + filePath);
        try {
            MclSyntaxAnalyzer syntaxAnalyzer = new MclSyntaxAnalyzer();
            SyntaxAnalysisResult syntaxResult = syntaxAnalyzer.processFile(filePath);

            if (syntaxResult.hasErrors()) {
                System.err.println("   [FAILED] Syntax Errors:");
                for (SyntaxError error : syntaxResult.errors()) {
                    System.err.println("     " + error);
                }
                System.out.println();
                return false;
            }

            MclSemanticAnalyzer semanticAnalyzer = new MclSemanticAnalyzer();
            SemanticAnalysisResult semanticResult = semanticAnalyzer.processSyntaxTree(syntaxResult);

            if (semanticResult.hasErrors()) {
                System.err.println("   [FAILED] Semantic Errors:");
                for (SemanticError error : semanticResult.errors()) {
                    System.err.println("     " + error);
                }
                System.out.println();
                return false;
            }

            System.out.println("   [OK] Success.\n");
            return true;

        } catch (IOException e) {
            System.err.println("   [ERROR] Could not read file: " + e.getMessage());
            return false;
        } catch (Exception e) {
            System.err.println("   [CRASH] Compiler internal error: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
}
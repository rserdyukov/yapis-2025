package io.hohichh.mcl.compiler;

import io.hohichh.mcl.compiler.analyzer.MclSemanticAnalyzer;
import io.hohichh.mcl.compiler.analyzer.MclSyntaxAnalyzer;
import io.hohichh.mcl.compiler.analyzer.artefacts.SemanticAnalysisResult;
import io.hohichh.mcl.compiler.analyzer.artefacts.SemanticError;
import io.hohichh.mcl.compiler.analyzer.artefacts.SyntaxAnalysisResult;
import io.hohichh.mcl.compiler.analyzer.artefacts.SyntaxError;

import java.io.IOException;
import java.util.List;

public class MclCompiler {

    public static void main(String[] args) {
        List<String> testFiles = List.of(
              "examples/solve_linear_equation.mcl",
                "examples/loops.mcl",
                "examples/lambda_and_io.mcl"
//                "examples/semantic_errors/err_undeclared.mcl",
//                "examples/semantic_errors/err_type_mismatch.mcl",
//                "examples/semantic_errors/err_redeclaration.mcl",
//                "examples/semantic_errors/err_func_call.mcl",
//                "examples/semantic_errors/err_condition.mcl",
//                "examples/semantic_errors/err_return_type.mcl"
        );

        for (String filePath : testFiles) {
            System.out.println("=========================================");
            System.out.println("Processing file: " + filePath);
            System.out.println("=========================================");

            try {
                // --- ЭТАП 1: Синтаксический анализ ---
                MclSyntaxAnalyzer syntaxAnalyzer = new MclSyntaxAnalyzer();
                SyntaxAnalysisResult syntaxResult = syntaxAnalyzer.processFile(filePath);

                if (syntaxResult.hasErrors()) {
                    System.out.println("Syntax analysis FAILED:");
                    for (SyntaxError error : syntaxResult.errors()) {
                        System.out.println("  - " + error);
                    }

                    continue;
                }

                // --- ЭТАП 2: Семантический анализ ---
                System.out.println("Syntax analysis OK.");
                MclSemanticAnalyzer semanticAnalyzer = new MclSemanticAnalyzer();
                SemanticAnalysisResult semanticResult = semanticAnalyzer.processSyntaxTree(syntaxResult);

                if (semanticResult.hasErrors()) {
                    System.out.println("Semantic analysis FAILED:");
                    for (SemanticError error : semanticResult.errors()) {
                        System.out.println("  - " + error);
                    }
                } else {
                    System.out.println("Semantic analysis OK.");
                }

                System.out.println("\nCompilation FINISHED for: " + filePath + "\n");

            } catch (IOException e) {
                System.err.println("Error reading file: " + filePath);
                e.printStackTrace();
            }
        }
    }
}
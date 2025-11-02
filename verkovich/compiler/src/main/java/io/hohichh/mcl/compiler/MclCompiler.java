package io.hohichh.mcl.compiler;


import io.hohichh.mcl.compiler.analyzer.MclSyntaxAnalyzer;
import io.hohichh.mcl.compiler.analyzer.artefacts.SyntaxAnalysisResult;
import io.hohichh.mcl.compiler.analyzer.artefacts.SyntaxError;

import java.io.IOException;


public class MclCompiler {
    public static void main(String[] args) throws IOException {
        MclSyntaxAnalyzer analyzer = new MclSyntaxAnalyzer();
        try {
            SyntaxAnalysisResult result = analyzer.processFile("examples/lambda_and_io.mcl");

            if (result.hasErrors()) {
                System.out.println("Syntax processor has found "
                        + result.errors().size() + " errors:");
                for (SyntaxError error : result.errors()) {
                    System.out.println(" - " + error);
                }
            } else {
                System.out.println("Syntax analysis completed successfully. No errors found.");
            }

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
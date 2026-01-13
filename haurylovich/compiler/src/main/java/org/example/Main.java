package org.example;

import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;

import java.io.BufferedReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {
    private static final String ILASM_PATH = "C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\ilasm.exe";

    public static void main(String[] args) {
        if (args.length == 0) {
            System.err.println("Использование: java Main <путь_к_файлу>");
            System.exit(1);
        }

        String fileName = args[0];
        System.out.println("Анализ файла: " + fileName);
        System.out.println("=".repeat(60));

        try {
            CharStream input = CharStreams.fromFileName(fileName);
            SetLangLexer lexer = new SetLangLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            SetLangParser parser = new SetLangParser(tokens);

            parser.removeErrorListeners();
            lexer.removeErrorListeners();

            SyntaxAnalyzer.SyntaxErrorListener syntaxErrorListener = new SyntaxAnalyzer.SyntaxErrorListener();
            parser.addErrorListener(syntaxErrorListener);
            lexer.addErrorListener(syntaxErrorListener);

            ParseTree tree = parser.program();

            if (syntaxErrorListener.hasErrors()) {
                System.out.println("Синтаксические ошибки обнаружены:");
                for (String err : syntaxErrorListener.getErrors()) System.out.println("  • " + err);
                System.exit(1);
            }

            SemanticAnalyzer.SemanticErrorListener semanticListener = new SemanticAnalyzer.SemanticErrorListener();
            ParseTreeWalker walker = new ParseTreeWalker();
            walker.walk(semanticListener, tree);

            if (semanticListener.hasErrors()) {
                System.out.println("Семантические ошибки обнаружены:");
                for (String err : semanticListener.getErrors()) System.out.println("  • " + err);
                System.exit(1);
            }

            CILGenerator generator = new CILGenerator();
            String cilCode = generator.getCIL(tree);
            String ilFileName = "output.il";
            String exeFileName = "output.exe";

            try (FileWriter writer = new FileWriter(ilFileName)) {
                writer.write(cilCode);
            }
            System.out.println("-".repeat(60));

            ProcessBuilder pbCompile = new ProcessBuilder(ILASM_PATH, "/exe", "/output=" + exeFileName, ilFileName);
            pbCompile.inheritIO();
            Process compileProcess = pbCompile.start();
            int compileExitCode = compileProcess.waitFor();

            if (compileExitCode != 0) {
                System.err.println("Ошибка при работе ilasm.exe. Код выхода: " + compileExitCode);
                System.exit(1);
            }
            ProcessBuilder pbRun = new ProcessBuilder(System.getProperty("user.dir") + "\\" + exeFileName);
            pbRun.inheritIO();
            Process runProcess = pbRun.start();
            runProcess.waitFor();

        } catch (IOException | InterruptedException e) {
            System.err.println("\nОшибка: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}

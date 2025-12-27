package org.example;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;

import java.io.FileWriter;
import java.io.IOException;


public class Main {
    public static void main(String[] args) {
        if (args.length == 0) {
            System.err.println("Использование: java Main <путь_к_файлу>");
            System.err.println("Пример: java Main example.txt");
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

            System.out.println("\n[1] СИНТАКСИЧЕСКИЙ АНАЛИЗ");
            System.out.println("-".repeat(60));

            SyntaxAnalyzer.SyntaxErrorListener syntaxErrorListener =
                    new SyntaxAnalyzer.SyntaxErrorListener();
            parser.addErrorListener(syntaxErrorListener);
            lexer.addErrorListener(syntaxErrorListener);

            ParseTree tree = parser.program();

            if (syntaxErrorListener.hasErrors()) {
                System.out.println("Синтаксические ошибки обнаружены:");
                for (String err : syntaxErrorListener.getErrors()) {
                    System.out.println("  • " + err);
                }
                System.out.println("\nАнализ остановлен из-за синтаксических ошибок.");
                System.exit(1);
            } else {
                System.out.println("✓ Синтаксический анализ завершен успешно!");
            }

            System.out.println("\n[2] СЕМАНТИЧЕСКИЙ АНАЛИЗ");
            System.out.println("-".repeat(60));

            SemanticAnalyzer.SemanticErrorListener semanticListener =
                    new SemanticAnalyzer.SemanticErrorListener();
            ParseTreeWalker walker = new ParseTreeWalker();
            walker.walk(semanticListener, tree);

            if (semanticListener.hasErrors()) {
                System.out.println("Семантические ошибки обнаружены:");
                for (String err : semanticListener.getErrors()) {
                    System.out.println("  • " + err);
                }
                System.exit(1);
            } else {
                System.out.println("✓ Семантический анализ завершен успешно!");
            }
            System.out.println("\n" + "=".repeat(60));
            System.out.println("ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!");
            System.out.println("=".repeat(60));

            CILGenerator generator = new CILGenerator();
            String cilCode = generator.getCIL(tree);
            try (FileWriter writer = new FileWriter("output.il")) {
                writer.write(cilCode);
            }

            System.out.println("Файл output.il успешно сгенерирован!");

        } catch (IOException e) {
            System.err.println("\nОшибка: Не удалось прочитать файл '" + fileName + "'");
            System.err.println("   Причина: " + e.getMessage());
            System.exit(1);
        } catch (Exception e) {
            System.err.println("\nОшибка при разборе: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}

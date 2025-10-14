package lab_3_4;

import lab_3_4.listener.ErrorListener;
import lab_3_4.listener.SemanticAnalyzeListener;
import lab_3_4.model.Error;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.ParseTreeWalker;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Stream;

// Класс для точки входа в программу
public class Main {
    public static void main(String[] args) {
        String fileName = args[0];
        Path filePath = Paths.get(fileName);

        if (Files.exists(filePath)) {

            List<Path> filePathList = new ArrayList<>();

            if (Files.isDirectory(filePath)) {
                try (Stream<Path> pathStream = Files.walk(filePath)) {
                    filePathList.addAll(pathStream.filter(Files::isRegularFile).toList());
                } catch (IOException e) {
                    e.printStackTrace();
                }
            } else {
                filePathList.add(filePath);
            }

            for (Path path : filePathList) {

                try {
                    String content = Files.readString(path);
                    grammarPLLexer lexer = new grammarPLLexer(CharStreams.fromString(content));

                    lexer.removeErrorListeners();
                    ErrorListener lexerErrorListener = new ErrorListener();
                    lexer.addErrorListener(lexerErrorListener);

                    CommonTokenStream tokens = new CommonTokenStream(lexer);
                    grammarPLParser parser = new grammarPLParser(tokens);

                    parser.removeErrorListeners();
                    ErrorListener pareserErrorListener = new ErrorListener();
                    parser.addErrorListener(pareserErrorListener);

                    ParseTree parseTree = parser.program();
                    ParseTreeWalker.DEFAULT.walk(new grammarPLBaseListener(), parseTree);

                    List<Error> syntaxErrors = new ArrayList<>();
                    syntaxErrors.addAll(lexerErrorListener.getErrors());
                    syntaxErrors.addAll(pareserErrorListener.getErrors());

                    if (!syntaxErrors.isEmpty()) {
                        System.out.printf("Errors (%s):%n", path.getFileName());
                        syntaxErrors.forEach(System.out::println);
                    } else {
                        SemanticAnalyzeListener listener = new SemanticAnalyzeListener();
                        ParseTreeWalker.DEFAULT.walk(listener, parseTree);

                        if (!listener.getSemanticErrors().isEmpty()) {
                            System.out.printf("Errors (%s):%n", path.getFileName());
                            listener.getSemanticErrors().forEach(System.out::println);
                        } else {
                            System.out.printf("No errors found (%s)%n", path.getFileName());
                        }
                    }

                    System.out.println();
                } catch (IOException e) {
                    e.printStackTrace();
                }

            }
        }
    }
}

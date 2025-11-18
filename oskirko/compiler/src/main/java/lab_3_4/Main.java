package lab_3_4;

import lab_3_4.listener.ConvertListener;
import lab_3_4.listener.ErrorListener;
import lab_3_4.listener.SemanticAnalyzeListener;
import lab_3_4.model.Error;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.tree.ParseTree;
import org.antlr.v4.runtime.tree.ParseTreeWalker;

import java.io.File;
import java.io.FileWriter;
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
                    ErrorListener parserErrorListener = new ErrorListener();
                    parser.addErrorListener(parserErrorListener);

                    ParseTree parseTree = parser.program();
                    ParseTreeWalker.DEFAULT.walk(new grammarPLBaseListener(), parseTree);

                    List<Error> syntaxErrors = new ArrayList<>();
                    syntaxErrors.addAll(lexerErrorListener.getErrors());
                    syntaxErrors.addAll(parserErrorListener.getErrors());

                    if (!syntaxErrors.isEmpty()) {
                        System.out.printf("Errors (%s):%n", path.getFileName());
                        syntaxErrors.forEach(System.out::println);
                        System.exit(1);
                    } else {
                        SemanticAnalyzeListener semanticListener = new SemanticAnalyzeListener();
                        ParseTreeWalker.DEFAULT.walk(semanticListener, parseTree);

                        if (!semanticListener.getSemanticErrors().isEmpty()) {
                            System.out.printf("Errors (%s):%n", path.getFileName());
                            semanticListener.getSemanticErrors().forEach(System.out::println);
                            System.exit(1);
                        } else {

                            ConvertListener convertListener = new ConvertListener(semanticListener);
                            ParseTreeWalker.DEFAULT.walk(convertListener, parseTree);

                            System.out.printf("No errors found (%s)%n", path.getFileName());

                            Path buildDir = Paths.get("../build");
                            if (!Files.exists(buildDir)) {
                                Files.createDirectory(buildDir);
                            }

                            File convertFile = new File("../build", "target.wat");
                            try (FileWriter convertFileWriter = new FileWriter(convertFile)) {
                                convertFileWriter.write(convertListener.getConverted().toString());
                            }

                            System.exit(0);
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

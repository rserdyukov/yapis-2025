package dev.dezzzl;

import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;

public class Main {

    public static void main(String[] args) throws Exception {
        if (args.length == 0) {
            System.out.println("You need to use: java -jar compiler-1.0-SNAPSHOT.jar <filename>");
            return;
        }
        String filename = args[0];
        if (!validateFile(filename)) {
            System.err.println("Error: the file must exist and have an extension .gsl");
            return;
        }
        String code = Files.readString(Path.of(filename));
        System.out.println("Code:\n" + code + "\n");
        GslLexer lexer = new GslLexer(CharStreams.fromString(code));
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        GslParser parser = new GslParser(tokens);
        parser.removeErrorListeners();
        parser.addErrorListener(new GslErrorListener());
        var tree = parser.program();
        if (parser.getNumberOfSyntaxErrors() > 0) {
            return;
        }
        DefaultGslVisitor visitor = new DefaultGslVisitor();
        visitor.visit(tree);
        writeSemanticInfo(visitor);
    }

    private static void writeSemanticInfo(DefaultGslVisitor visitor) {
        if (!visitor.getContext().getErrors().isEmpty()) {
            visitor.getContext().getErrors().forEach(e ->
                    System.err.println(e.getMessage())
            );
        } else {
            System.out.println("No errors were found");
        }
    }

    private static boolean validateFile(String path) {
        File file = new File(path);
        return file.exists() && file.isFile() && path.toLowerCase().endsWith(".gsl");
    }

}

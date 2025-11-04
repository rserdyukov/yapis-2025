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
            System.err.println("Error: The file must exist and have an extension .gsl");
            return;
        }
        String code = Files.readString(Path.of(filename));
        System.out.println("Code:\n" + code + "\n");
        GslLexer lexer = new GslLexer(CharStreams.fromString(code));
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        GslParser parser = new GslParser(tokens);
        parser.removeErrorListeners();
        parser.addErrorListener(new GslErrorListener());
        parser.program();
    }

    private static boolean validateFile(String path) {
        File file = new File(path);
        return file.exists() && file.isFile() && path.toLowerCase().endsWith(".gsl");
    }
}

package dev.dezzzl;

import dev.dezzzl.codegen.IRGenerator;
import dev.dezzzl.semantics.Context;
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
        IRGenerator generator = new IRGenerator();
        Context context = new Context();
        DefaultGslVisitor visitor = new DefaultGslVisitor(generator, context);
        visitor.visit(tree);
        writeSemanticInfo(visitor);
        DefaultCodegenVisitor codegen = new DefaultCodegenVisitor(generator, context);
        codegen.visit(tree);
        String llvmIR = codegen.getGenerator().getModule();
        System.out.println(llvmIR);
        Path outFile = Path.of("program.ll");
        Files.writeString(outFile, llvmIR);
        System.out.println("\nLLVM IR has been saved to: " + outFile.toAbsolutePath());
    }

    private static void writeSemanticInfo(DefaultGslVisitor visitor) {
        if (!visitor.getContext().getErrors().isEmpty()) {
            visitor.getContext().getErrors().forEach(e ->
                    System.err.println(e.getMessage())
            );
            System.exit(1);
        } else {
            System.out.println("No errors were found");
        }
    }

    private static boolean validateFile(String path) {
        File file = new File(path);
        return file.exists() && file.isFile() && path.toLowerCase().endsWith(".gsl");
    }

}

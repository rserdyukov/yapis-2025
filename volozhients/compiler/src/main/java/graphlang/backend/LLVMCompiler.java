package graphlang.backend;

import graphlang.GraphLangParser;
import org.antlr.v4.runtime.tree.ParseTree;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.*;

public final class LLVMCompiler {

    public static final class CompilationResult {
        private final Path llvmIrPath;
        private final Path executablePath;
        public CompilationResult(Path llvmIrPath, Path executablePath) {
            this.llvmIrPath = llvmIrPath;
            this.executablePath = executablePath;
        }
        public Path llvmIrPath() { return llvmIrPath; }
        public Path executablePath() { return executablePath; }
    }

    public CompilationResult compileToExecutable(ParseTree tree, GraphLangParser parser, Path sourcePath, Path outputExe) throws IOException, InterruptedException {

        GraphLangCodeGenerator gen = new GraphLangCodeGenerator();
        String csource = gen.generate((GraphLangParser.ProgramContext) tree);

        Path tempDir = Files.createTempDirectory("graphlang-compile-");
        Path cFile = tempDir.resolve("program.c");
        Path llFile = tempDir.resolve("program.ll");
        Path exeFile = outputExe;

        try (BufferedWriter w = Files.newBufferedWriter(cFile, StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING)) {
            w.write(csource);
        }

        ProcessBuilder pb1 = new ProcessBuilder("clang", "-S", "-emit-llvm", cFile.toAbsolutePath().toString(), "-o", llFile.toAbsolutePath().toString());
        pb1.directory(tempDir.toFile());
        pb1.redirectError(ProcessBuilder.Redirect.INHERIT);
        pb1.redirectOutput(ProcessBuilder.Redirect.INHERIT);
        Process p1 = pb1.start();
        int r1 = p1.waitFor();
        if (r1 != 0) {
            throw new RuntimeException("clang failed to produce LLVM IR (exit " + r1 + ")");
        }

        Files.createDirectories(exeFile.getParent() == null ? Paths.get(".") : exeFile.getParent());
        ProcessBuilder pb2 = new ProcessBuilder("clang", cFile.toAbsolutePath().toString(), "-o", exeFile.toAbsolutePath().toString());
        pb2.directory(tempDir.toFile());
        pb2.redirectError(ProcessBuilder.Redirect.INHERIT);
        pb2.redirectOutput(ProcessBuilder.Redirect.INHERIT);
        Process p2 = pb2.start();
        int r2 = p2.waitFor();
        if (r2 != 0) {
            throw new RuntimeException("clang failed to compile executable (exit " + r2 + ")");
        }

        return new CompilationResult(llFile.toAbsolutePath(), exeFile.toAbsolutePath());
    }
}
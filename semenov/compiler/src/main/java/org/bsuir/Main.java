package org.bsuir;

import org.antlr.v4.runtime.BaseErrorListener;
import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.tree.ParseTree;
import org.bsuir.error.LangBaseErrorListener;
import org.bsuir.parser.LangLexer;
import org.bsuir.parser.LangParser;

import java.io.IOException;
import java.nio.file.Path;

public class Main {


    public static void main(String[] args) throws IOException {
        if (args.length != 1) {
            System.exit(1);
        }

        String filePath = args[0];
        CharStream input = CharStreams.fromPath(Path.of(filePath));

        LangLexer lexer = new LangLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        LangParser parser = new LangParser(tokens);
        BaseErrorListener errorListener = new LangBaseErrorListener();
        parser.addErrorListener(errorListener);
        lexer.addErrorListener(errorListener);

        ParseTree tree = parser.program();

        System.out.println(tree.toStringTree(parser));
    }
}
package graphlang.frontend;

import graphlang.GraphLangLexer;
import graphlang.GraphLangParser;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.ParseTree;

import java.nio.file.Path;

public final class GraphLangParserFacade {

    private GraphLangParserFacade() {}

    public record ParseResult(ParseTree tree, GraphLangParser parser) {}

    public static ParseResult parseFile(Path sourcePath) throws Exception {
        CharStream charStream = CharStreams.fromPath(sourcePath);
        return parse(charStream);
    }

    public static ParseResult parse(CharStream charStream) {
        GraphLangLexer lexer = new GraphLangLexer(charStream);
        CommonTokenStream tokenStream = new CommonTokenStream(lexer);
        GraphLangParser parser = new GraphLangParser(tokenStream);

        parser.removeErrorListeners();
        parser.addErrorListener(new ThrowingErrorListener());

        ParseTree tree = parser.program();
        return new ParseResult(tree, parser);
    }

    private static final class ThrowingErrorListener extends BaseErrorListener {
        @Override
        public void syntaxError(
                Recognizer<?, ?> recognizer,
                Object offendingSymbol,
                int line,
                int charPositionInLine,
                String msg,
                RecognitionException e
        ) {
            throw new SyntaxException("Syntax error at %d:%d — %s"
                    .formatted(line, charPositionInLine, msg));
        }
    }
}

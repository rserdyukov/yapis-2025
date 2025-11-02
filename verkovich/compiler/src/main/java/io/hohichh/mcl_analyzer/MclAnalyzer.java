package io.hohichh.mcl_analyzer;


import org.antlr.v4.runtime.CharStream;
import org.antlr.v4.runtime.CharStreams;
import org.antlr.v4.runtime.CommonTokenStream;
import org.antlr.v4.runtime.tree.ParseTree;

public class MclAnalyzer {
    public static void main(String[] args) {
        String mclCode = "func main() -> void: \n    a = 10 \n";
        CharStream input = CharStreams.fromString(mclCode);

        MCLLexer lexer = new IndentHandlingLexer(input);

        CommonTokenStream tokens = new CommonTokenStream(lexer);

        MCLParser parser = new MCLParser(tokens);

        ParseTree tree = parser.program();

        System.out.println(tree.toStringTree(parser));
    }
}
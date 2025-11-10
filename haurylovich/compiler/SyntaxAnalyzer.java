import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.tree.*;
import java.io.IOException;

public class SyntaxAnalyzer {

    public static void main(String[] args) {
        String fileName = "C:\\Users\\ASUS\\IdeaProjects\\YAPIS_\\incorrect_examples\\example5.txt";

        try {
            CharStream input = CharStreams.fromFileName(fileName);
            SetLangLexer lexer = new SetLangLexer(input);
            CommonTokenStream tokens = new CommonTokenStream(lexer);
            SetLangParser parser = new SetLangParser(tokens);
            parser.removeErrorListeners();
            lexer.removeErrorListeners();
            SyntaxErrorListener errorListener = new SyntaxErrorListener();
            parser.addErrorListener(errorListener);
            lexer.addErrorListener(errorListener);
            parser.program();
            if (errorListener.hasErrors()) {
                System.out.println("Синтаксические ошибки обнаружены:");
                for (String err : errorListener.getErrors()) {
                    System.out.println(err);
                }
            } else {
                System.out.println("Синтаксис корректен!");
            }

        } catch (IOException e) {
            System.err.println("Не удалось прочитать файл: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Ошибка при разборе: " + e.getMessage());
        }
    }

    static class SyntaxErrorListener extends BaseErrorListener {
        private final java.util.List<String> errors = new java.util.ArrayList<>();

        @Override
        public void syntaxError(Recognizer<?, ?> recognizer,
                                Object offendingSymbol,
                                int line, int charPositionInLine,
                                String msg,
                                RecognitionException e) {
            errors.add("Line " + line + ":" + charPositionInLine + " - " + msg);
        }

        public boolean hasErrors() {
            return !errors.isEmpty();
        }

        public java.util.List<String> getErrors() {
            return errors;
        }
    }
}

package org.example;

import org.antlr.v4.runtime.*;

public class SyntaxAnalyzer {

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

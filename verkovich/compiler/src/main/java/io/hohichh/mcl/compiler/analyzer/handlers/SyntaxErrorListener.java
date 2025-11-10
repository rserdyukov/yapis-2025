package io.hohichh.mcl.compiler.analyzer.handlers;

import io.hohichh.mcl.compiler.analyzer.artefacts.SyntaxError;
import org.antlr.v4.runtime.BaseErrorListener;
import org.antlr.v4.runtime.RecognitionException;
import org.antlr.v4.runtime.Recognizer;

import java.util.ArrayList;
import java.util.List;


public class SyntaxErrorListener extends BaseErrorListener {

    private final List<SyntaxError> errors = new ArrayList<>();

    public List<SyntaxError> getErrors() {
        return errors;
    }

    @Override
    public void syntaxError(Recognizer<?, ?> recognizer,
                            Object offendingSymbol,
                            int line,
                            int charPositionInLine,
                            String msg,
                            RecognitionException e) {

        errors.add(new SyntaxError(line, charPositionInLine, msg));
    }
}
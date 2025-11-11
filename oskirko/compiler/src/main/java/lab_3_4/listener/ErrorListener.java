package lab_3_4.listener;

import lab_3_4.model.Error;
import lab_3_4.model.ErrorType;
import org.antlr.v4.runtime.BaseErrorListener;
import org.antlr.v4.runtime.RecognitionException;
import org.antlr.v4.runtime.Recognizer;
import org.antlr.v4.runtime.Token;

import java.util.ArrayList;
import java.util.List;

// Класс для обработчика ошибок синтаксиса
public class ErrorListener extends BaseErrorListener {

    private final List<Error> errors = new ArrayList<>();

    @Override
    public void syntaxError(Recognizer<?, ?> recognizer,
                            Object offendingSymbol,
                            int line,
                            int charPositionInLine,
                            String msg,
                            RecognitionException e) {
        String tokenText = (offendingSymbol instanceof Token) ? ((Token) offendingSymbol).getText() : String.valueOf(offendingSymbol);
        if (tokenText == null) {
            tokenText = "<no token>";
        }
        Error error = new Error(line, charPositionInLine, String.format("At '%s' - %s", tokenText, msg), ErrorType.SYNTAX);
        errors.add(error);
    }

    public Boolean hasErrors() {
        return !errors.isEmpty();
    }

    public List<Error> getErrors() {
        return errors;
    }
}

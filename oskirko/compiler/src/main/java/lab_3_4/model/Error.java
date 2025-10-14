package lab_3_4.model;

// Класс для представления ошибки
public record Error(
        Integer line,
        Integer charPositionInLine,
        String message,
        ErrorType errorType
) {

    @Override
    public String toString() {
        return String.format("line %d:%d %s error %s", line, charPositionInLine, errorType, message);
    }
}

package dev.dezzzl.semantics.exception;

public class SemanticException extends RuntimeException {
    private final int line;
    private final int column;

    public SemanticException(String message, int line, int column) {
        super(message);
        this.line = line;
        this.column = column;
    }

    public int getLine() {
        return line;
    }

    public int getColumn() {
        return column;
    }

    @Override
    public String getMessage() {
        return String.format(
                "Semantic error in the line %d:%d — %s",
                line, column, super.getMessage()
        );
    }
}

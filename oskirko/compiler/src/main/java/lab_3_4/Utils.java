package lab_3_4;

public class Utils {
    public static String typeMapper(Integer type) {
        return switch (type) {
            case grammarPLLexer.TYPE_INTEGER, grammarPLLexer.TYPE_BOOLEAN -> "i32";
            case grammarPLLexer.TYPE_FLOAT -> "f32";
            default -> "i32";
        };
    }

    public static String typeMapper(String type) {
        return switch (type) {
            case "integer", "boolean" -> "i32";
            case "float" -> "f32";
            default -> "i32";
        };
    }

    public static String stringWithIndention(String str, int indentionCount) {
        return "\t".repeat(indentionCount) + str;
    }
}

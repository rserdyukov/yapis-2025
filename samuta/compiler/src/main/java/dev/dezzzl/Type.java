package dev.dezzzl;

import java.util.Set;

public enum Type {
    INT("int"),
    BOOLEAN("boolean"),
    STRING("string"),
    VOID("void"),
    NODE("node"),
    ARC("arc"),
    GRAPH("graph");

    private final String value;

    private static final Set<CastRule> castRules = Set.of(
            new CastRule(STRING, INT),
            new CastRule(INT, STRING),
            new CastRule(NODE, ARC),
            new CastRule(ARC, GRAPH),
            new CastRule(STRING, NODE)
    );

    Type(String value) {
        this.value = value;
    }

    public static Type fromValue(String value) {
        for (Type t : values()) {
            if (t.value.equals(value)) return t;
        }
        throw new IllegalArgumentException("Неизвестный тип: " + value);
    }

    public String getValue() {
        return value;
    }

    public boolean canCastTo(Type target) {
        if (this == target) return true;
        return castRules.contains(new CastRule(this, target));
    }

    private record CastRule(Type from, Type to) {}
}

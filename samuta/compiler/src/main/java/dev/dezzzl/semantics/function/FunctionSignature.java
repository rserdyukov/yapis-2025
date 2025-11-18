package dev.dezzzl.semantics.function;

import java.util.List;

public class FunctionSignature {
    public final String name;
    public final String returnType;
    public final List<String> paramTypes;

    public FunctionSignature(String name, String returnType, List<String> paramTypes) {
        this.name = name;
        this.returnType = returnType;
        this.paramTypes = paramTypes;
    }

    @Override
    public String toString() {
        return String.format("%s(%s): %s",
                name,
                String.join(", ", paramTypes),
                returnType);
    }
}

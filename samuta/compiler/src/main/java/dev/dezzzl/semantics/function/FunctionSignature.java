package dev.dezzzl.semantics.function;

import lombok.EqualsAndHashCode;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

@EqualsAndHashCode(exclude = {"variables", "prefix", "isFromCode"})
public class FunctionSignature {
    public final String name;
    public final String returnType;
    public final List<String> paramTypes;
    public final List<VariableInfo> variables = new ArrayList<>();
    @Setter
    public String prefix;
    @Setter
    public boolean isFromCode;

    public FunctionSignature(String name, String returnType, List<String> paramTypes) {
        this.name = name;
        this.returnType = returnType;
        this.paramTypes = paramTypes;
    }

    public void addVariable(VariableInfo variable) {
        variables.add(variable);
    }

    public VariableInfo getVariable(String variableName) {
        for (VariableInfo variable : variables) {
            if (variable.name.equals(variableName)) {
                return variable;
            }
        }
        return null;
    }

    public VariableInfo getVariableByIndex(int index) {
        if (index < 0 || index >= variables.size()) {
            throw new IndexOutOfBoundsException("Parameter index " + index + " is out of bounds for function " + name);
        }
        return variables.get(index);
    }

    @Override
    public String toString() {
        return String.format("%s(%s): %s",
                name,
                String.join(", ", paramTypes),
                returnType);
    }
}

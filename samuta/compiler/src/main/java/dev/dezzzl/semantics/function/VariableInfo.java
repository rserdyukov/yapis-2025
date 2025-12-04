package dev.dezzzl.semantics.function;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class VariableInfo {
    public final String name;
    public final String type;
    public final boolean isGlobal;
    public boolean isAllocaGenerated;
    public boolean isParameter;
    public boolean isOut;

    public VariableInfo(String name, String type, boolean isGlobal) {
        this.name = name;
        this.type = type;
        this.isGlobal = isGlobal;
    }

    public VariableInfo(String name, String type, boolean isGlobal, boolean isParameter, boolean isOut) {
        this.name = name;
        this.type = type;
        this.isGlobal = isGlobal;
        this.isParameter = isParameter;
        this.isOut = isOut;
    }

}
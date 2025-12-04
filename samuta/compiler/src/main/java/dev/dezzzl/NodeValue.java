package dev.dezzzl;

public class NodeValue {
    public String irType;
    public String type;
    public String operand;
    public String code;

    public NodeValue(String type, String irType, String operand, String code) {
        this.type = type;
        this.irType = irType;
        this.operand = operand;
        this.code = code;
    }

    public NodeValue( String code) {
        this.type = null;
        this.irType = null;
        this.operand = null;
        this.code = code;
    }

}

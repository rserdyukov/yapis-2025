package lab_3_4.model;

// Класс для представления переменной
public class Variable implements Typed {
    private String name;
    private int type;
    private Integer assignedType;
    private boolean isAssignedTypeArray;
    private boolean isArray;
    private boolean isParameter;

    public Variable(String name, int type, Integer assignedType, boolean isArray, boolean isParameter, boolean isAssignedTypeArray) {
        this.name = name;
        this.type = type;
        this.assignedType = assignedType;
        this.isArray = isArray;
        this.isParameter = isParameter;
        this.isAssignedTypeArray = isAssignedTypeArray;
    }

    public Variable() {
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getType() {
        return type;
    }

    public void setType(int type) {
        this.type = type;
    }

    public Integer getAssignedType() {
        return assignedType;
    }

    public void setAssignedType(Integer assignedType) {
        this.assignedType = assignedType;
    }

    public boolean isArray() {
        return isArray;
    }

    public void setArray(boolean array) {
        isArray = array;
    }

    public boolean isParameter() {
        return isParameter;
    }

    public void setParameter(boolean parameter) {
        isParameter = parameter;
    }

    public boolean isAssignedTypeArray() {
        return isAssignedTypeArray;
    }

    public void setAssignedTypeArray(boolean assignedTypeArray) {
        isAssignedTypeArray = assignedTypeArray;
    }
}

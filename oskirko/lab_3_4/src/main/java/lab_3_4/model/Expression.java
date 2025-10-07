package lab_3_4.model;

// Класс для представления выражения
public class Expression implements Typed {
    private String name;
    private int type;

    public Expression(String name, int type) {
        this.name = name;
        this.type = type;
    }

    public Expression() {
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
}

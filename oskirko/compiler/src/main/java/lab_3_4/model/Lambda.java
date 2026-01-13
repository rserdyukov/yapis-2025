package lab_3_4.model;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

public class Lambda {

    private String name;
    private List<Variable> closure;
    private List<Variable> params;
    private List<Variable> results;
    private List<Variable> variables;

    public Lambda() {
        closure = new ArrayList<>();
        params = new ArrayList<>();
        results = new ArrayList<>();
        variables = new ArrayList<>();
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public List<Variable> getClosure() {
        return closure;
    }

    public void setClosure(List<Variable> closure) {
        this.closure = closure;
    }

    public List<Variable> getParams() {
        return params;
    }

    public void setParams(List<Variable> params) {
        this.params = params;
    }

    public List<Variable> getResults() {
        return results;
    }

    public void setResults(List<Variable> results) {
        this.results = results;
    }

    public List<Variable> getVariables() {
        return variables;
    }

    public void setVariables(List<Variable> variables) {
        this.variables = variables;
    }

    public Map<String, Variable> getAllVariables() {
        List<Variable> allVariables = new ArrayList<>(params);
        allVariables.addAll(closure);
        allVariables.addAll(variables);

        return allVariables.stream().
                collect(Collectors.toMap(
                        Variable::getName,
                        Function.identity(),
                        (v1, v2) -> v1
                ));
    }
}

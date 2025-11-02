package dev.dezzzl.semantics;

import dev.dezzzl.Type;
import dev.dezzzl.semantics.exception.SemanticException;
import dev.dezzzl.semantics.function.FunctionSignature;

import java.util.*;

public class Context {

    private final Deque<Map<String, String>> localVarStack = new ArrayDeque<>();
    private final Map<String, String> globalVars = new HashMap<>();
    private final Map<String, List<FunctionSignature>> functions = new HashMap<>();
    private final List<SemanticException> semanticExceptions = new ArrayList<>();
    private FunctionSignature currentFunction = null;

    public void addBuiltInFunctions() {
        addFunction(new FunctionSignature("read", Type.STRING.getValue(), List.of()));
        addFunction(new FunctionSignature("toString", Type.STRING.getValue(), List.of(Type.VOID.getValue())));
        addFunction(new FunctionSignature("addNode", Type.GRAPH.getValue(), List.of(Type.GRAPH.getValue(), Type.NODE.getValue())));
        addFunction(new FunctionSignature("deleteNode", Type.GRAPH.getValue(), List.of(Type.GRAPH.getValue(), Type.NODE.getValue())));
        addFunction(new FunctionSignature("getNode", Type.NODE.getValue(), List.of(Type.GRAPH.getValue(), Type.INT.getValue())));
        addFunction(new FunctionSignature("getNeighbour", Type.NODE.getValue(), List.of(Type.GRAPH.getValue(), Type.NODE.getValue(), Type.INT.getValue())));
        addFunction(new FunctionSignature("addArc", Type.GRAPH.getValue(), List.of(Type.GRAPH.getValue(), Type.ARC.getValue())));
        addFunction(new FunctionSignature("hasNode", Type.BOOLEAN.getValue(), List.of(Type.GRAPH.getValue(), Type.NODE.getValue())));
        addFunction(new FunctionSignature("hasArc", Type.BOOLEAN.getValue(), List.of(Type.GRAPH.getValue(), Type.ARC.getValue())));
        addFunction(new FunctionSignature("deleteArc", Type.GRAPH.getValue(), List.of(Type.GRAPH.getValue(), Type.ARC.getValue())));
        addFunction(new FunctionSignature("size", Type.INT.getValue(), List.of(Type.GRAPH.getValue())));
        addFunction(new FunctionSignature("shortestPath", Type.GRAPH.getValue(), List.of(Type.GRAPH.getValue(), Type.NODE.getValue(), Type.NODE.getValue())));
        addFunction(new FunctionSignature("bfs", Type.GRAPH.getValue(), List.of(Type.GRAPH.getValue(), Type.NODE.getValue())));
        addFunction(new FunctionSignature("dfs", Type.GRAPH.getValue(), List.of(Type.GRAPH.getValue(), Type.NODE.getValue())));
    }

    public void pushBlock() {
        localVarStack.push(new HashMap<>());
    }

    public void popBlock() {
        if (!localVarStack.isEmpty()) {
            localVarStack.pop();
        }
    }

    public void declareVar(String name, String type) {
        if (localVarStack.isEmpty()) {
            throw new RuntimeException("there is no current block for declaring a variable '" + name + "'");
        }
        for (Map<String, String> block : localVarStack) {
            if (block.containsKey(name)) {
                throw new RuntimeException("variable '" + name + "' is already declared");
            }
        }
        Map<String, String> currentBlock = localVarStack.peek();
        currentBlock.put(name, type);
    }

    public FunctionSignature getFunction(String name, List<String> argTypes) {
        if (name.equals("write")) {
            return new FunctionSignature("write", Type.VOID.getValue(), argTypes);
        }
        List<FunctionSignature> overloads = functions.get(name);
        if (overloads == null) return null;

        List<Type> callArgTypes = argTypes.stream()
                .map(t -> {
                    try {
                        return Type.valueOf(t.toUpperCase());
                    } catch (IllegalArgumentException e) {
                        return null;
                    }
                })
                .toList();

        for (FunctionSignature candidate : overloads) {
            if (candidate.paramTypes.size() != callArgTypes.size()) continue;

            boolean compatible = true;
            for (int i = 0; i < callArgTypes.size(); i++) {
                Type callType = callArgTypes.get(i);
                Type paramType = Type.valueOf(candidate.paramTypes.get(i).toUpperCase());
                if (callType == null || !callType.canCastTo(paramType)) {
                    compatible = false;
                    break;
                }
            }

            if (compatible) return candidate;
        }

        return null;
    }

    public String getVarType(String name) {
        for (Map<String, String> block : localVarStack) {
            if (block.containsKey(name)) return block.get(name);
        }
        if (globalVars.containsKey(name)) return globalVars.get(name);
        return null;
    }

    public void declareGlobalVar(String name, String type) {
        if (globalVars.containsKey(name)) {
            throw new RuntimeException("gloval variable '" + name + "' is already declared");
        }
        globalVars.put(name, type);
    }

    public void addFunction(FunctionSignature signature) {
        functions.putIfAbsent(signature.name, new ArrayList<>());
        List<FunctionSignature> overloads = functions.get(signature.name);

        for (FunctionSignature existing : overloads) {
            if (existing.paramTypes.equals(signature.paramTypes)) {
                throw new RuntimeException(
                        "function '" + signature.name + "' with such parameters already defined"
                );
            }
        }
        overloads.add(signature);
    }

    public void addError(SemanticException e) {
        semanticExceptions.add(e);
    }

    public List<SemanticException> getErrors() {
        return semanticExceptions;
    }

    public void enterFunction(FunctionSignature signature) {
        this.currentFunction = signature;
        this.pushBlock();
    }

    public void exitFunction() {
        this.currentFunction = null;
        this.popBlock();
    }

    public FunctionSignature getCurrentFunction() {
        return currentFunction;
    }
}

import { ParseTreeListener, TerminalNode } from "antlr4";

import Variant15Parser, {
    ExpressionContext,
} from "./Variant15/Variant15Parser";

interface SymbolInfo {
    index: number;
    type: string;
}

interface FunctionSig {
    name: string;
    descriptor: string;
    returnType: string;
    paramCount: number;
    paramTypes: string[]; // Added to help with resolution
}

interface ControlContext {
    type: "loop" | "switch";
    breakLabel: string;
    continueLabel?: string;
    nextCaseLabel?: string;
    startLabel?: string;
    stepInstructions?: string[]; // Buffer for loop step instructions
    startLabelEmitted?: boolean;
}

class MethodContext {
    code: string[] = [];
    localsStack: Map<string, SymbolInfo>[] = [new Map()];
    currentLocalIndex = 0;
    typeStack: string[] = [];
    controlStack: ControlContext[] = [];
    labelCounter = 0;
    returnType: string = "void";
    parameterTypes: string[] = []; // Store parameter types of current function for matching
}

export class JvmCompiler extends ParseTreeListener {
    private output: string[] = [];
    private contextStack: MethodContext[] = [];
    private currentCtx: MethodContext | null = null;
    // Map stores a list of signatures for each function name to support overloading
    private functions: Map<string, FunctionSig[]> = new Map();
    private isBufferingStep = false; // Flag to indicate if we are in the step part of a for loop

    constructor() {
        super();
    }

    getGeneratedCode(): string {
        return this.output.join("\n");
    }

    private emit(instr: string) {
        // If we are buffering a loop step, redirect output to the loop's step buffer
        if (
            this.isBufferingStep &&
            this.currentCtx &&
            this.currentCtx.controlStack.length > 0
        ) {
            const loop =
                this.currentCtx.controlStack[
                    this.currentCtx.controlStack.length - 1
                ];
            if (loop.type === "loop") {
                if (!loop.stepInstructions) loop.stepInstructions = [];
                loop.stepInstructions.push("    " + instr);
                return;
            }
        }

        if (this.currentCtx) {
            this.currentCtx.code.push("    " + instr);
        } else {
            this.output.push(instr);
        }
    }

    private emitLabel(label: string) {
        if (this.currentCtx) {
            this.currentCtx.code.push(label + ":");
        }
    }

    private newLabel(): string {
        return `L${this.currentCtx!.labelCounter++}`;
    }

    private getSymbol(name: string) {
        if (!this.currentCtx) return undefined;
        for (let i = this.currentCtx.localsStack.length - 1; i >= 0; i--) {
            if (this.currentCtx.localsStack[i].has(name))
                return this.currentCtx.localsStack[i].get(name)!;
        }
        return undefined;
    }

    private getTypeDesc(type: string): string {
        if (type.includes("[]")) return "Ljava/util/ArrayList;";
        if (type.includes("string")) return "Ljava/lang/String;";
        if (type === "void") return "V";
        if (type === "bool") return "Z";
        if (type === "char") return "I"; // Jasmin treats char as int usually on stack
        if (type === "rune") return "I";
        return "I";
    }

    enterProgram(ctx: any) {
        this.output = [];
        this.functions = new Map();
        this.contextStack = [];
        this.currentCtx = null;
        this.isBufferingStep = false;

        // Class Header
        this.emit(".class public Program");
        this.emit(".super java/lang/Object");
        this.emit("");

        // Standard Constructor
        this.emit(".method public <init>()V");
        this.emit("    aload_0");
        this.emit("    invokenonvirtual java/lang/Object/<init>()V");
        this.emit("    return");
        this.emit(".end method");
        this.emit("");

        this.emitHelpers();

        this.scanFunctions(ctx);
    }

    private emitHelpers() {
        this.output.push(`
.method public static __repeatList(Ljava/util/ArrayList;I)Ljava/util/ArrayList;
    .limit stack 3
    .limit locals 4
    new java/util/ArrayList
    dup
    invokespecial java/util/ArrayList/<init>()V
    astore_2
    iload_1
    ifle L_end_rep
    iconst_0
    istore_3
L_loop_rep:
    iload_3
    iload_1
    if_icmpge L_end_rep
    aload_2
    aload_0
    invokevirtual java/util/ArrayList/addAll(Ljava/util/Collection;)Z
    pop
    iinc 3 1
    goto L_loop_rep
L_end_rep:
    aload_2
    areturn
.end method

.method public static __splitList(Ljava/util/ArrayList;I)Ljava/util/ArrayList;
    .limit stack 6
    .limit locals 10
    new java/util/ArrayList
    dup
    invokespecial java/util/ArrayList/<init>()V
    astore_2
    iload_1
    iconst_1
    if_icmplt L_ret_split
    aload_0
    invokevirtual java/util/ArrayList/size()I
    istore_3
    iload_3
    iload_1
    idiv
    istore 4
    iload_3
    iload_1
    irem
    istore 5
    iconst_0
    istore 6
    iconst_0
    istore 7
L_loop_split:
    iload 7
    iload_1
    if_icmpge L_ret_split
    iload 4
    istore 8
    iload 7
    iload 5
    if_icmpge L_skip_rem
    iinc 8 1
L_skip_rem:
    new java/util/ArrayList
    dup
    aload_0
    iload 6
    iload 6
    iload 8
    iadd
    invokevirtual java/util/ArrayList/subList(II)Ljava/util/List;
    invokespecial java/util/ArrayList/<init>(Ljava/util/Collection;)V
    astore 9
    aload_2
    aload 9
    invokevirtual java/util/ArrayList/add(Ljava/lang/Object;)Z
    pop
    iload 6
    iload 8
    iadd
    istore 6
    iinc 7 1
    goto L_loop_split
L_ret_split:
    aload_2
    areturn
.end method

.method public static __subString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    .limit stack 4
    .limit locals 4
    aload_0
    aload_1
    invokevirtual java/lang/String/indexOf(Ljava/lang/String;)I
    istore_2
    iload_2
    iconst_m1
    if_icmpne L_found_sub
    aload_0
    areturn
L_found_sub:
    aload_0
    iconst_0
    iload_2
    invokevirtual java/lang/String/substring(II)Ljava/lang/String;
    astore_3
    aload_0
    iload_2
    aload_1
    invokevirtual java/lang/String/length()I
    iadd
    invokevirtual java/lang/String/substring(I)Ljava/lang/String;
    astore_1
    aload_3
    aload_1
    invokevirtual java/lang/String/concat(Ljava/lang/String;)Ljava/lang/String;
    areturn
.end method

.method public static __subList(Ljava/util/ArrayList;Ljava/lang/String;)Ljava/util/ArrayList;
    .limit stack 4
    .limit locals 4
    new java/util/ArrayList
    dup
    aload_0
    invokespecial java/util/ArrayList/<init>(Ljava/util/Collection;)V
    astore_2
    aload_2
    aload_1
    invokevirtual java/util/ArrayList/indexOf(Ljava/lang/Object;)I
    istore_3
    iload_3
    iconst_m1
    if_icmpne L_remove_item
    aload_2
    areturn
L_remove_item:
    aload_2
    iload_3
    invokevirtual java/util/ArrayList/remove(I)Ljava/lang/Object;
    pop
    aload_2
    areturn
.end method

.method public static __subListList(Ljava/util/ArrayList;Ljava/util/ArrayList;)Ljava/util/ArrayList;
   .limit stack 3
   .limit locals 3
   new java/util/ArrayList
   dup
   aload_0
   invokespecial java/util/ArrayList/<init>(Ljava/util/Collection;)V
   astore_2
   aload_2
   aload_1
   invokevirtual java/util/ArrayList/removeAll(Ljava/util/Collection;)Z
   pop
   aload_2
   areturn
.end method

.method public static __repeatString(Ljava/lang/String;I)Ljava/lang/String;
    .limit stack 3
    .limit locals 3
    new java/lang/StringBuilder
    dup
    invokespecial java/lang/StringBuilder/<init>()V
    astore_2
    iload_1
    ifle L_end_rs
L_loop_rs:
    iload_1
    ifle L_end_rs
    aload_2
    aload_0
    invokevirtual java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    pop
    iinc 1 -1
    goto L_loop_rs
L_end_rs:
    aload_2
    invokevirtual java/lang/StringBuilder/toString()Ljava/lang/String;
    areturn
.end method

.method public static __divString(Ljava/lang/String;I)Ljava/lang/String;
    .limit stack 4
    .limit locals 2
    aload_0
    iconst_0
    aload_0
    invokevirtual java/lang/String/length()I
    iload_1
    idiv
    invokevirtual java/lang/String/substring(II)Ljava/lang/String;
    areturn
.end method
`);
    }

    private scanFunctions(ctx: any) {
        if (!ctx) return;
        if (ctx.ruleIndex === Variant15Parser.RULE_functionDeclaration) {
            const name = ctx.IDENTIFIER().getText();
            const paramsCtx = ctx.parameterList();
            let descParams = "";
            const paramTypes: string[] = [];
            let paramCount = 0;

            if (paramsCtx) {
                for (const param of paramsCtx.parameter_list()) {
                    const pType = param.typeSpecifier().getText();
                    descParams += this.getTypeDesc(pType);
                    paramTypes.push(pType);
                    paramCount++;
                }
            }
            const retTypeCtx = ctx.typeSpecifier();
            const retType = retTypeCtx ? retTypeCtx.getText() : "void";
            const descRet = this.getTypeDesc(retType);

            const sig: FunctionSig = {
                name,
                descriptor: `(${descParams})${descRet}`,
                returnType: retType,
                paramCount,
                paramTypes,
            };

            if (name === "main") {
                sig.descriptor = "([Ljava/lang/String;)V";
                sig.paramTypes = ["string[]"]; // Assuming standard main signature
            }

            if (!this.functions.has(name)) {
                this.functions.set(name, []);
            }
            this.functions.get(name)!.push(sig);
        }
        if (ctx.children) {
            for (const child of ctx.children) {
                if (child.ruleIndex !== undefined || child.children)
                    this.scanFunctions(child);
            }
        }
    }

    enterFunctionDeclaration(ctx: any) {
        const newCtx = new MethodContext();
        if (this.currentCtx) this.contextStack.push(this.currentCtx);
        this.currentCtx = newCtx;

        const name = ctx.IDENTIFIER().getText();

        // Find the specific signature being declared by matching parameters
        const paramsCtx = ctx.parameterList();
        const currentParamTypes: string[] = [];
        if (paramsCtx) {
            for (const param of paramsCtx.parameter_list()) {
                currentParamTypes.push(param.typeSpecifier().getText());
            }
        }

        // Look up valid signatures
        const candidates = this.functions.get(name);
        let sig: FunctionSig | undefined;

        if (candidates) {
            if (name === "main") {
                sig = candidates[0];
            } else {
                // Find match
                sig = candidates.find((c) => {
                    if (c.paramCount !== currentParamTypes.length) return false;
                    for (let i = 0; i < c.paramCount; i++) {
                        if (c.paramTypes[i] !== currentParamTypes[i])
                            return false;
                    }
                    return true;
                });
            }
        }

        if (!sig) {
            // Fallback (should not happen if scan works)
            sig = {
                name,
                descriptor: "()V",
                returnType: "void",
                paramCount: 0,
                paramTypes: [],
            };
        }

        this.currentCtx.returnType = sig.returnType;
        this.currentCtx.parameterTypes = sig.paramTypes;

        // Method Header
        this.emit(`.method public static ${name}${sig.descriptor}`);
        this.emit("    .limit stack 100");
        this.emit("    .limit locals 100");

        if (name === "main") {
            this.currentCtx.localsStack[0].set("args", {
                index: 0,
                type: "string[]",
            });
            this.currentCtx.currentLocalIndex = 1;
        } else {
            const paramList = ctx.parameterList();
            if (paramList) {
                for (const param of paramList.parameter_list()) {
                    const pName = param.IDENTIFIER().getText();
                    const pType = param.typeSpecifier().getText();
                    this.currentCtx.localsStack[0].set(pName, {
                        index: this.currentCtx.currentLocalIndex++,
                        type: pType,
                    });
                }
            }
        }
        (ctx as any).methodName = name;
    }

    exitFunctionDeclaration(ctx: any) {
        const name = (ctx as any).methodName;
        // Check current context return type directly
        const returnType = this.currentCtx!.returnType;

        if (returnType === "void") {
            this.emit("return");
        } else if (["int", "bool", "char", "rune"].includes(returnType)) {
            this.emit("iconst_0");
            this.emit("ireturn");
        } else {
            this.emit("aconst_null");
            this.emit("areturn");
        }

        this.emit(".end method");
        this.emit("");

        this.output.push(...this.currentCtx!.code);

        if (this.contextStack.length > 0)
            this.currentCtx = this.contextStack.pop()!;
        else this.currentCtx = null;
    }

    exitReturnStmt(ctx: any) {
        const declaredType = this.currentCtx!.returnType;
        if (ctx.expression()) {
            this.currentCtx!.typeStack.pop();
            if (declaredType === "void") {
                this.emit("pop");
                this.emit("return");
            } else if (["int", "bool", "char", "rune"].includes(declaredType)) {
                this.emit("ireturn");
            } else {
                this.emit("areturn");
            }
        } else {
            this.emit("return");
        }
    }

    exitBreakStmt(ctx: any) {
        if (this.currentCtx!.controlStack.length > 0) {
            const ctrl =
                this.currentCtx!.controlStack[
                    this.currentCtx!.controlStack.length - 1
                ];
            this.emit(`goto ${ctrl.breakLabel}`);
        }
    }

    exitContinueStmt(ctx: any) {
        for (let i = this.currentCtx!.controlStack.length - 1; i >= 0; i--) {
            if (this.currentCtx!.controlStack[i].type === "loop") {
                this.emit(
                    `goto ${this.currentCtx!.controlStack[i].continueLabel!}`
                );
                return;
            }
        }
    }

    exitVariableDeclaration(ctx: any) {
        const typeSpec = ctx.typeSpecifier().getText();
        const ids = ctx.IDENTIFIER_list();
        const exprs = ctx.expression_list();

        if (exprs.length > 0) {
            for (let i = ids.length - 1; i >= 0; i--) {
                const name = ids[i].getText();
                const idx = this.currentCtx!.currentLocalIndex++;
                this.currentCtx!.localsStack[0].set(name, {
                    index: idx,
                    type: typeSpec,
                });
                this.currentCtx!.typeStack.pop();
                if (typeSpec.includes("string") || typeSpec.includes("[]")) {
                    this.emit(`astore ${idx}`);
                } else {
                    this.emit(`istore ${idx}`);
                }
            }
        } else {
            for (const id of ids) {
                const name = id.getText();
                const idx = this.currentCtx!.currentLocalIndex++;
                this.currentCtx!.localsStack[0].set(name, {
                    index: idx,
                    type: typeSpec,
                });
                if (typeSpec.includes("string") || typeSpec.includes("[]")) {
                    this.emit("aconst_null");
                    this.emit(`astore ${idx}`);
                } else {
                    this.emit("iconst_0");
                    this.emit(`istore ${idx}`);
                }
            }
        }

        const parent = ctx.parentCtx;
        if (parent.ruleIndex === Variant15Parser.RULE_forStatement) {
            const loop =
                this.currentCtx!.controlStack[
                    this.currentCtx!.controlStack.length - 1
                ];
            if (!loop.startLabelEmitted) {
                this.emitLabel(loop.startLabel!);
                loop.startLabelEmitted = true;
            }
        }
    }

    exitAssignment(ctx: any) {
        if (ctx.INC()) {
            const name = ctx.designator(0).IDENTIFIER().getText();
            const sym = this.getSymbol(name);
            if (sym) {
                this.emit(`iinc ${sym.index} 1`);
            }
        } else {
            const ids = ctx.designator_list();
            for (let i = ids.length - 1; i >= 0; i--) {
                const name = ids[i].IDENTIFIER().getText();
                const sym = this.getSymbol(name);

                if (sym) {
                    this.currentCtx!.typeStack.pop();
                    if (
                        sym.type.includes("string") ||
                        sym.type.includes("[]")
                    ) {
                        this.emit(`astore ${sym.index}`);
                    } else {
                        this.emit(`istore ${sym.index}`);
                    }
                } else {
                    this.currentCtx!.typeStack.pop();
                    this.emit("pop");
                }
            }
        }

        // Emit start label if this was the initialization assignment of a for loop
        const parent = ctx.parentCtx;
        if (parent.ruleIndex === Variant15Parser.RULE_forStatement) {
            const assignments = parent.assignment_list();
            const loop =
                this.currentCtx!.controlStack[
                    this.currentCtx!.controlStack.length - 1
                ];
            if (!loop.startLabelEmitted) {
                // If this assignment is NOT part of the step (isBufferingStep is false), it is initialization.
                if (!this.isBufferingStep) {
                    this.emitLabel(loop.startLabel!);
                    loop.startLabelEmitted = true;
                }
            }
        }

        if (this.isBufferingStep) {
            this.isBufferingStep = false;
        }
    }

    enterIfStatement(ctx: any) {
        const elseLbl = this.newLabel();
        const endLbl = this.newLabel();
        (ctx as any).elseLbl = elseLbl;
        (ctx as any).endLbl = endLbl;

        // Tag the condition expression
        const expr = ctx.expression();
        if (expr) {
            (expr as any).isCondition = true;
            (expr as any).falseLabel = elseLbl;
        }
    }

    exitIfStatement(ctx: any) {
        this.emitLabel((ctx as any).endLbl);
    }

    enterSwitchStatement(ctx: any) {
        const endLbl = this.newLabel();
        this.currentCtx!.controlStack.push({
            type: "switch",
            breakLabel: endLbl,
        });
        (ctx as any).endLbl = endLbl;
        (ctx as any).nextCaseLabel = null;
    }

    exitSwitchStatement(ctx: any) {
        const ctrl = this.currentCtx!.controlStack.pop();
        if ((ctx as any).nextCaseLabel) {
            this.emitLabel((ctx as any).nextCaseLabel);
        }
        this.emitLabel(ctrl!.breakLabel);
    }

    enterCaseBlock(ctx: any) {
        const switchNode = ctx.parentCtx;
        if ((switchNode as any).nextCaseLabel) {
            this.emitLabel((switchNode as any).nextCaseLabel);
        }
        (switchNode as any).nextCaseLabel = this.newLabel();

        // Tag condition
        const expr = ctx.expression();
        if (expr) {
            (expr as any).isCondition = true;
            (expr as any).falseLabel = (switchNode as any).nextCaseLabel;
        }
    }

    exitCaseBlock(ctx: any) {
        const switchNode = ctx.parentCtx;
        const endLbl = (switchNode as any).endLbl;
        this.emit(`goto ${endLbl}`);
    }

    enterDefaultBlock(ctx: any) {
        const switchNode = ctx.parentCtx;
        if ((switchNode as any).nextCaseLabel) {
            this.emitLabel((switchNode as any).nextCaseLabel);
        }
        (switchNode as any).nextCaseLabel = null;
    }

    exitDefaultBlock(ctx: any) {
        const switchNode = ctx.parentCtx;
        const endLbl = (switchNode as any).endLbl;
        this.emit(`goto ${endLbl}`);
    }

    private emitConditionCheck(ctx: any) {
        if ((ctx as any).isCondition) {
            this.currentCtx!.typeStack.pop();
            const target = (ctx as any).falseLabel;
            this.emit(`ifeq ${target}`);
        }
    }

    exitBlock(ctx: any) {
        const parent = ctx.parentCtx;

        if (parent.ruleIndex === Variant15Parser.RULE_ifStatement) {
            const elseLbl = (parent as any).elseLbl;
            const endLbl = (parent as any).endLbl;
            if (parent.block(0) === ctx) {
                this.emit(`goto ${endLbl}`);
                this.emitLabel(elseLbl);
            }
        }
    }

    enterForStatement(ctx: any) {
        const startLbl = this.newLabel();
        const endLbl = this.newLabel();
        const continueLbl = this.newLabel();

        this.currentCtx!.controlStack.push({
            type: "loop",
            breakLabel: endLbl,
            continueLabel: continueLbl,
            startLabel: startLbl,
            startLabelEmitted: false,
        });

        // Robustly identify the condition expression using child iteration
        let semiCount = 0;
        if (ctx.children) {
            for (const child of ctx.children) {
                // Check if the child is a token (Leaf) and if it is SEMI
                if (child instanceof TerminalNode) {
                    if (child.symbol.type === Variant15Parser.SEMI) {
                        semiCount++;
                        continue;
                    }
                }

                // If we are strictly between the first and second semicolon
                if (semiCount === 1) {
                    if (child instanceof ExpressionContext) {
                        (child as any).isCondition = true;
                        (child as any).falseLabel = endLbl;
                    }
                }
            }
        }

        const hasVarDecl = ctx.variableDeclaration() != null;
        let hasInitAssign = false;
        if (ctx.assignment_list().length > 0) {
            // Check if assignments are before first semicolon
            const semis = ctx.SEMI_list();
            if (semis.length > 0) {
                const firstSemiIdx = semis[0].symbol.tokenIndex;
                for (const assign of ctx.assignment_list()) {
                    if (assign.start.tokenIndex < firstSemiIdx) {
                        hasInitAssign = true;
                        break;
                    }
                }
            }
        }

        if (!hasVarDecl && !hasInitAssign) {
            this.emitLabel(startLbl);
            this.currentCtx!.controlStack[
                this.currentCtx!.controlStack.length - 1
            ].startLabelEmitted = true;
        }
    }

    enterAssignment(ctx: any) {
        const parent = ctx.parentCtx;
        if (parent.ruleIndex === Variant15Parser.RULE_forStatement) {
            // Determine if this assignment is the step (after 2nd semi)
            // Simpler check: is it after the condition expression?
            const semis = parent.SEMI_list();
            if (semis.length >= 2) {
                const secondSemiIdx = semis[1].symbol.tokenIndex;
                const assignStartIdx = ctx.start.tokenIndex;
                if (assignStartIdx > secondSemiIdx) {
                    this.isBufferingStep = true;
                }
            }
        }
    }

    exitForStatement(ctx: any) {
        const loop = this.currentCtx!.controlStack.pop()!;

        this.emitLabel(loop.continueLabel!);

        if (loop.stepInstructions && loop.stepInstructions.length > 0) {
            this.currentCtx!.code.push(...loop.stepInstructions);
        }

        this.emit(`goto ${loop.startLabel}`);
        this.emitLabel(loop.breakLabel);
    }

    exitIoStatement(ctx: any) {
        if (ctx.PRINT() || ctx.WRITE()) {
            const type = this.currentCtx!.typeStack.pop();
            this.emit("getstatic java/lang/System/out Ljava/io/PrintStream;");
            this.emit("swap");

            const isExactString = type === "string";
            const desc =
                type === "int"
                    ? "(I)V"
                    : type === "bool"
                    ? "(Z)V"
                    : type === "char"
                    ? "(C)V"
                    : isExactString
                    ? "(Ljava/lang/String;)V"
                    : "(Ljava/lang/Object;)V";

            this.emit(`invokevirtual java/io/PrintStream/println${desc}`);
        }
    }

    // Resolve Function Calls with Overloading
    exitFunctionCall(ctx: any) {
        const name = ctx.IDENTIFIER().getText();
        const candidates = this.functions.get(name);

        const argList = ctx.argumentList();
        const providedArgsCount = argList
            ? argList.expression_list().length
            : 0;

        let sig: FunctionSig | undefined;

        if (candidates) {
            // Get types of the last N arguments from stack
            // Note: typeStack might contain unrelated types lower down, we only care about the top N
            // The argument evaluation order pushes args to stack one by one.
            const providedArgsTypes = this.currentCtx!.typeStack.slice(
                -providedArgsCount
            );

            // Find best match
            sig = candidates.find((c) => {
                if (c.paramCount !== providedArgsCount) return false;

                for (let i = 0; i < c.paramCount; i++) {
                    const req = c.paramTypes[i];
                    const prov = providedArgsTypes[i];

                    if (req === prov) continue;
                    // Loose type matching
                    if (
                        ["int", "char", "rune"].includes(req) &&
                        ["int", "char", "rune"].includes(prov)
                    )
                        continue;

                    return false;
                }
                return true;
            });
        }

        if (sig) {
            if (name === "main") {
                this.emit("aconst_null");
            }

            this.emit(`invokestatic Program/${name}${sig.descriptor}`);

            // Pop arguments from type stack
            for (let i = 0; i < providedArgsCount; i++) {
                this.currentCtx!.typeStack.pop();
            }

            if (sig.returnType !== "void") {
                this.currentCtx!.typeStack.push(sig.returnType);
            }
        } else {
            // Fallback/Error case (normally handled by Semantic Analyzer)
            // We just consume the stack args to not crash
            for (let i = 0; i < providedArgsCount; i++) {
                this.emit("pop");
                this.currentCtx!.typeStack.pop();
            }
        }
    }

    exitFuncCallStmt(ctx: any) {
        const name = ctx.functionCall().IDENTIFIER().getText();
        const candidates = this.functions.get(name);
        if (candidates && candidates.some((c) => c.returnType !== "void")) {
            const lastType =
                this.currentCtx!.typeStack[
                    this.currentCtx!.typeStack.length - 1
                ];
            if (lastType && candidates.some((c) => c.returnType === lastType)) {
                this.emit("pop");
                this.currentCtx!.typeStack.pop();
            }
        }
    }

    exitDesignator(ctx: any) {
        const parent = ctx.parentCtx;

        if (parent.ruleIndex === Variant15Parser.RULE_assignment) {
            return;
        }

        const name = ctx.IDENTIFIER().getText();
        const sym = this.getSymbol(name);
        const brackets = ctx.LBRACK_list ? ctx.LBRACK_list() : [];

        if (brackets.length > 0) {
            if (sym) {
                this.emit(`aload ${sym.index}`);
                this.emit("swap");

                if (sym.type.includes("string") && !sym.type.includes("[]")) {
                    this.emit("invokevirtual java/lang/String/charAt(I)C");
                    this.currentCtx!.typeStack.pop();
                    this.currentCtx!.typeStack.push("char");
                } else if (sym.type.includes("[]")) {
                    this.emit(
                        "invokevirtual java/util/ArrayList/get(I)Ljava/lang/Object;"
                    );
                    this.emit("checkcast java/lang/String");
                    this.currentCtx!.typeStack.pop();
                    this.currentCtx!.typeStack.push("string");
                }
            }
        } else {
            if (sym) {
                if (sym.type.includes("string") || sym.type.includes("[]")) {
                    this.emit(`aload ${sym.index}`);
                    this.currentCtx!.typeStack.push(
                        sym.type.includes("[]") ? "[]string" : "string"
                    );
                } else if (
                    sym.type.includes("char") ||
                    sym.type.includes("rune")
                ) {
                    this.emit(`iload ${sym.index}`);
                    this.currentCtx!.typeStack.push(
                        sym.type.includes("char") ? "char" : "int"
                    );
                } else if (sym.type.includes("bool")) {
                    this.emit(`iload ${sym.index}`);
                    this.currentCtx!.typeStack.push("bool");
                } else {
                    this.emit(`iload ${sym.index}`);
                    this.currentCtx!.typeStack.push("int");
                }
            }
        }
    }

    exitArrayLiteral(ctx: any) {
        this.emit("new java/util/ArrayList");
        this.emit("dup");
        this.emit("invokespecial java/util/ArrayList/<init>()V");
        // Stack: e1, e2, ..., en, ArrayList

        const exprs = ctx.expression_list();
        for (let i = 0; i < exprs.length; i++) {
            // We need to take en (top of stack under ArrayList), add it to index 0 of ArrayList.
            // Stack: ..., val, ArrayList
            this.emit("dup_x1");
            // Stack: ..., ArrayList, val, ArrayList
            this.emit("swap");
            // Stack: ..., ArrayList, ArrayList, val

            this.emit("iconst_0");
            this.emit("swap");
            // Stack: ..., ArrayList, ArrayList, 0, val

            const type = this.currentCtx!.typeStack.pop();
            if (type === "int" || type === "char" || type === "rune") {
                this.emit(
                    "invokestatic java/lang/Integer/valueOf(I)Ljava/lang/Integer;"
                );
            } else if (type === "bool") {
                this.emit(
                    "invokestatic java/lang/Boolean/valueOf(Z)Ljava/lang/Boolean;"
                );
            }

            this.emit(
                "invokevirtual java/util/ArrayList/add(ILjava/lang/Object;)V"
            );
            // Stack: ..., ArrayList
        }
        this.currentCtx!.typeStack.push("[]string");
    }

    enterAtom(ctx: any) {
        if (ctx.INT_LITERAL()) {
            const val = parseInt(ctx.INT_LITERAL().getText());
            if (val >= -1 && val <= 5) this.emit(`iconst_${val}`);
            else if (val >= -128 && val <= 127) this.emit(`bipush ${val}`);
            else this.emit(`ldc ${val}`);
            this.currentCtx!.typeStack.push("int");
        } else if (ctx.STRING_LITERAL()) {
            const s = ctx.STRING_LITERAL().getText();
            this.emit(`ldc ${s}`);
            this.currentCtx!.typeStack.push("string");
        } else if (ctx.BOOL_LITERAL()) {
            const v = ctx.BOOL_LITERAL().getText() === "true";
            this.emit(v ? "iconst_1" : "iconst_0");
            this.currentCtx!.typeStack.push("bool");
        } else if (ctx.CHAR_LITERAL()) {
            const txt = ctx.CHAR_LITERAL().getText();
            let charCode = 0;
            const content = txt.substring(1, txt.length - 1);
            if (content.length === 1) charCode = content.charCodeAt(0);
            else if (content === "\\n") charCode = 10;
            else if (content === "\\t") charCode = 9;
            else if (content === "\\r") charCode = 13;
            else if (content === "\\\\") charCode = 92;
            else if (content === "\\'") charCode = 39;
            else charCode = 65;

            this.emit(`bipush ${charCode}`);
            this.currentCtx!.typeStack.push("char");
        }
    }

    exitAtom(ctx: any) {
        if (ctx.LEN()) {
            const t = this.currentCtx!.typeStack.pop();
            if (t && t.includes("[]")) {
                this.emit("invokevirtual java/util/ArrayList/size()I");
            } else if (t === "string") {
                this.emit("invokevirtual java/lang/String/length()I");
            } else {
                this.emit("pop");
                this.emit("iconst_0");
            }
            this.currentCtx!.typeStack.push("int");
        }
    }

    exitAtomExpr(ctx: any) {
        this.emitConditionCheck(ctx);
    }

    exitParenExpr(ctx: any) {
        this.emitConditionCheck(ctx);
    }

    exitAdditiveExpr(ctx: any) {
        if (ctx.PLUS()) {
            const t2 = this.currentCtx!.typeStack.pop();
            const t1 = this.currentCtx!.typeStack.pop();

            // Array Concatenation: Array + Array
            if (t1 && t1.includes("[]") && t2 && t2.includes("[]")) {
                const idx2 = this.currentCtx!.currentLocalIndex++;
                const idx1 = this.currentCtx!.currentLocalIndex++;
                const idxRes = this.currentCtx!.currentLocalIndex++;

                this.emit(`astore ${idx2}`); // save list2
                this.emit(`astore ${idx1}`); // save list1

                // New ArrayList
                this.emit("new java/util/ArrayList");
                this.emit("dup");
                this.emit("invokespecial java/util/ArrayList/<init>()V");
                this.emit(`astore ${idxRes}`);

                // res.addAll(list1)
                this.emit(`aload ${idxRes}`);
                this.emit(`aload ${idx1}`);
                this.emit(
                    "invokevirtual java/util/ArrayList/addAll(Ljava/util/Collection;)Z"
                );
                this.emit("pop"); // pop boolean result

                // res.addAll(list2)
                this.emit(`aload ${idxRes}`);
                this.emit(`aload ${idx2}`);
                this.emit(
                    "invokevirtual java/util/ArrayList/addAll(Ljava/util/Collection;)Z"
                );
                this.emit("pop"); // pop boolean result

                // Push res to stack
                this.emit(`aload ${idxRes}`);

                this.currentCtx!.typeStack.push("[]string");
            }
            // Array + Element (String, Char, Rune/Int) -> New Array
            else if (t1 && t1.includes("[]")) {
                // Save scalar
                const idxScalar = this.currentCtx!.currentLocalIndex++;
                // Determine if scalar is reference or primitive
                const isRef = t2 === "string" || (t2 && t2.includes("[]"));
                if (isRef) this.emit(`astore ${idxScalar}`);
                else this.emit(`istore ${idxScalar}`);

                // Save list
                const idxList = this.currentCtx!.currentLocalIndex++;
                this.emit(`astore ${idxList}`);

                // Create new list
                const idxRes = this.currentCtx!.currentLocalIndex++;
                this.emit("new java/util/ArrayList");
                this.emit("dup");
                this.emit("invokespecial java/util/ArrayList/<init>()V");
                this.emit(`astore ${idxRes}`);

                // Copy old list
                this.emit(`aload ${idxRes}`);
                this.emit(`aload ${idxList}`);
                this.emit(
                    "invokevirtual java/util/ArrayList/addAll(Ljava/util/Collection;)Z"
                );
                this.emit("pop");

                // Add new element
                this.emit(`aload ${idxRes}`); // receiver

                if (isRef) {
                    this.emit(`aload ${idxScalar}`);
                } else {
                    this.emit(`iload ${idxScalar}`);
                    if (t2 === "char") {
                        this.emit(
                            "invokestatic java/lang/String/valueOf(C)Ljava/lang/String;"
                        );
                    } else if (t2 === "bool") {
                        this.emit(
                            "invokestatic java/lang/String/valueOf(Z)Ljava/lang/String;"
                        );
                    } else {
                        this.emit(
                            "invokestatic java/lang/String/valueOf(I)Ljava/lang/String;"
                        );
                    }
                }

                this.emit(
                    "invokevirtual java/util/ArrayList/add(Ljava/lang/Object;)Z"
                );
                this.emit("pop");

                this.emit(`aload ${idxRes}`);
                this.currentCtx!.typeStack.push("[]string");
            }
            // String + ... or ... + String
            else if (t1 === "string" || t2 === "string") {
                if (t2 !== "string") {
                    const desc =
                        t2 === "char"
                            ? "(C)Ljava/lang/String;"
                            : "(I)Ljava/lang/String;";
                    this.emit(`invokestatic java/lang/String/valueOf${desc}`);
                }
                if (t1 !== "string") {
                    this.emit("swap");
                    const desc =
                        t1 === "char"
                            ? "(C)Ljava/lang/String;"
                            : "(I)Ljava/lang/String;";
                    this.emit(`invokestatic java/lang/String/valueOf${desc}`);
                    this.emit("swap");
                }
                this.emit(
                    "invokevirtual java/lang/String/concat(Ljava/lang/String;)Ljava/lang/String;"
                );
                this.currentCtx!.typeStack.push("string");
            } else {
                this.emit("iadd");
                this.currentCtx!.typeStack.push("int");
            }
        } else if (ctx.MINUS()) {
            const t2 = this.currentCtx!.typeStack.pop();
            const t1 = this.currentCtx!.typeStack.pop();

            if (t1 && t1.includes("[]")) {
                if (t2 && t2.includes("[]")) {
                    // List - List subtraction
                    this.emit(
                        "invokestatic Program/__subListList(Ljava/util/ArrayList;Ljava/util/ArrayList;)Ljava/util/ArrayList;"
                    );
                    this.currentCtx!.typeStack.push("[]string");
                } else {
                    // List - Scalar subtraction
                    if (t2 !== "string") {
                        const desc =
                            t2 === "char"
                                ? "(C)Ljava/lang/String;"
                                : "(I)Ljava/lang/String;";
                        this.emit(
                            `invokestatic java/lang/String/valueOf${desc}`
                        );
                    }
                    this.emit(
                        "invokestatic Program/__subList(Ljava/util/ArrayList;Ljava/lang/String;)Ljava/util/ArrayList;"
                    );
                    this.currentCtx!.typeStack.push("[]string");
                }
            } else if (t1 === "string") {
                // String - String/Scalar subtraction
                if (t2 !== "string") {
                    const desc =
                        t2 === "char"
                            ? "(C)Ljava/lang/String;"
                            : "(I)Ljava/lang/String;";
                    this.emit(`invokestatic java/lang/String/valueOf${desc}`);
                }
                this.emit(
                    "invokestatic Program/__subString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;"
                );
                this.currentCtx!.typeStack.push("string");
            } else {
                // Standard integer subtraction
                this.emit("isub");
                this.currentCtx!.typeStack.push("int");
            }
        }

        this.emitConditionCheck(ctx);
    }

    exitMultiplicativeExpr(ctx: any) {
        const t2 = this.currentCtx!.typeStack.pop();
        const t1 = this.currentCtx!.typeStack.pop();

        if (ctx.MULT()) {
            if (t1 && t1.includes("[]") && t2 === "int") {
                this.emit(
                    "invokestatic Program/__repeatList(Ljava/util/ArrayList;I)Ljava/util/ArrayList;"
                );
                this.currentCtx!.typeStack.push(t1);
            } else if (t1 === "int" && t2 && t2.includes("[]")) {
                // Swap args for commutative property (int * array) -> (array * int)
                this.emit("swap");
                this.emit(
                    "invokestatic Program/__repeatList(Ljava/util/ArrayList;I)Ljava/util/ArrayList;"
                );
                this.currentCtx!.typeStack.push(t2);
            } else if (t1 === "string" && t2 === "int") {
                this.emit(
                    "invokestatic Program/__repeatString(Ljava/lang/String;I)Ljava/lang/String;"
                );
                this.currentCtx!.typeStack.push("string");
            } else if (t1 === "int" && t2 === "string") {
                this.emit("swap");
                this.emit(
                    "invokestatic Program/__repeatString(Ljava/lang/String;I)Ljava/lang/String;"
                );
                this.currentCtx!.typeStack.push("string");
            } else if ((t1 === "char" || t1 === "rune") && t2 === "int") {
                // Stack: char, int. Need: string, int.
                this.emit("swap"); // int, char
                this.emit(
                    "invokestatic java/lang/String/valueOf(C)Ljava/lang/String;"
                ); // int, string
                this.emit("swap"); // string, int
                this.emit(
                    "invokestatic Program/__repeatString(Ljava/lang/String;I)Ljava/lang/String;"
                );
                this.currentCtx!.typeStack.push("string");
            } else if (t1 === "int" && (t2 === "char" || t2 === "rune")) {
                // Stack: int, char. Need: string, int.
                this.emit(
                    "invokestatic java/lang/String/valueOf(C)Ljava/lang/String;"
                ); // int, string
                this.emit("swap"); // string, int
                this.emit(
                    "invokestatic Program/__repeatString(Ljava/lang/String;I)Ljava/lang/String;"
                );
                this.currentCtx!.typeStack.push("string");
            } else {
                this.emit("imul");
                this.currentCtx!.typeStack.push("int");
            }
        } else if (ctx.DIV()) {
            if (t1 && t1.includes("[]") && t2 === "int") {
                this.emit(
                    "invokestatic Program/__splitList(Ljava/util/ArrayList;I)Ljava/util/ArrayList;"
                );
                this.currentCtx!.typeStack.push("[]string"); // Basically list of lists
            } else if (t1 === "string" && t2 === "int") {
                this.emit(
                    "invokestatic Program/__divString(Ljava/lang/String;I)Ljava/lang/String;"
                );
                this.currentCtx!.typeStack.push("string");
            } else if ((t1 === "char" || t1 === "rune") && t2 === "int") {
                // "Result is original rune without changes". Stack: char, int.
                this.emit("pop"); // Remove int
                this.currentCtx!.typeStack.push("char"); // Keep char
            } else {
                this.emit("idiv");
                this.currentCtx!.typeStack.push("int");
            }
        }

        this.emitConditionCheck(ctx);
    }

    exitRelationalExpr(ctx: any) {
        const op = ctx.getChild(1).getText();
        const t2 = this.currentCtx!.typeStack.pop();
        const t1 = this.currentCtx!.typeStack.pop();

        if (t1 === "string" && t2 === "string") {
            if (op === "==" || op === "!=") {
                this.emit(
                    "invokevirtual java/lang/String/equals(Ljava/lang/Object;)Z"
                );
                if (op === "!=") {
                    this.emit("iconst_1");
                    this.emit("ixor");
                }
                this.currentCtx!.typeStack.push("bool");
                this.emitConditionCheck(ctx);
                return;
            }
        }

        let jumpOp = "if_icmpeq";
        if (op === "!=") jumpOp = "if_icmpne";
        if (op === "<") jumpOp = "if_icmplt";
        if (op === ">") jumpOp = "if_icmpgt";
        if (op === "<=") jumpOp = "if_icmple";
        if (op === ">=") jumpOp = "if_icmpge";

        const trueLbl = this.newLabel();
        const endLbl = this.newLabel();

        this.emit(`${jumpOp} ${trueLbl}`);
        this.emit("iconst_0");
        this.emit(`goto ${endLbl}`);
        this.emitLabel(trueLbl);
        this.emit("iconst_1");
        this.emitLabel(endLbl);

        this.currentCtx!.typeStack.push("int");

        this.emitConditionCheck(ctx);
    }
}

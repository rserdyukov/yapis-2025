import { ParseTreeListener } from "antlr4";

export interface Symbol {
    name: string;
    type: string;
    kind: "variable" | "function" | "parameter";
    position: number;
    signature?: string; // Add signature for function overloading
}

export class Scope {
    symbols: Map<string, Symbol>;
    parent: Scope | null;

    constructor(parent: Scope | null = null) {
        this.symbols = new Map();
        this.parent = parent;
    }

    // Updated define to handle overloading using unique keys for functions
    define(symbol: Symbol): void {
        const key =
            symbol.kind === "function" && symbol.signature !== undefined
                ? `${symbol.name}__${symbol.signature}`
                : symbol.name;
        this.symbols.set(key, symbol);
    }

    resolve(name: string): Symbol | undefined {
        // Simple resolve for variables (exact match)
        if (this.symbols.has(name)) {
            return this.symbols.get(name);
        }
        // For functions, we might check if ANY overload exists, but for basic sem analysis
        // just checking if the base name exists in map keys is tricky with mangling.
        // However, we can check if keys start with "name__"
        for (const key of this.symbols.keys()) {
            if (key === name || key.startsWith(name + "__")) {
                return this.symbols.get(key);
            }
        }

        if (this.parent) {
            return this.parent.resolve(name);
        }
        return undefined;
    }

    hasSignature(name: string, signature: string): boolean {
        const key = `${name}__${signature}`;
        return this.symbols.has(key);
    }
}

export class SemanticAnalyzer {
    errors: string[] = [];
    currentScope: Scope;
    mainFunctionCount: number = 0;

    constructor() {
        this.currentScope = new Scope(null);
    }

    reset() {
        this.currentScope = new Scope(null);
        this.errors = [];
        this.mainFunctionCount = 0;
    }

    enterScope() {
        this.currentScope = new Scope(this.currentScope);
    }

    exitScope() {
        if (this.currentScope.parent) {
            this.currentScope = this.currentScope.parent;
        }
    }

    declare(
        name: string,
        type: string,
        kind: "variable" | "function" | "parameter",
        pos: number,
        signature?: string
    ) {
        if (kind === "function" && signature !== undefined) {
            // Check for exact signature duplicate in the current scope AND parent scopes (Shadowing check)
            let scope: Scope | null = this.currentScope;
            while (scope) {
                if (scope.hasSignature(name, signature)) {
                    this.errors.push(
                        `SemError (Pos ${pos}): Function '${name}' with signature '${signature}' already declared in this or outer scope.`
                    );
                    return;
                }
                scope = scope.parent;
            }

            if (name === "main") {
                this.mainFunctionCount++;
            }
        } else {
            // Standard check for variables/parameters (only current scope for re-declaration)
            if (this.currentScope.symbols.has(name)) {
                this.errors.push(
                    `SemError (Pos ${pos}): Identifier '${name}' already declared in this scope.`
                );
                return;
            }
        }

        const symbol: Symbol = { name, type, kind, position: pos, signature };
        this.currentScope.define(symbol);
    }

    checkIdentifier(name: string, pos: number): Symbol | undefined {
        const symbol = this.currentScope.resolve(name);
        if (!symbol) {
            this.errors.push(
                `SemError (Pos ${pos}): Undefined identifier '${name}'.`
            );
            return undefined;
        }
        return symbol;
    }

    checkMainFunction() {
        if (this.mainFunctionCount === 0) {
            this.errors.push(
                "SemError: No 'main' function defined. The program must have exactly one entry point."
            );
        } else if (this.mainFunctionCount > 1) {
            this.errors.push(
                `SemError: Multiple 'main' functions defined (${this.mainFunctionCount}). The program must have exactly one entry point.`
            );
        }
    }
}

export class SemanticListener extends ParseTreeListener {
    analyzer: SemanticAnalyzer;

    constructor() {
        super();
        this.analyzer = new SemanticAnalyzer();
    }

    enterProgram(ctx: any) {
        this.analyzer.reset();
    }

    exitProgram(ctx: any) {
        this.analyzer.checkMainFunction();
    }

    enterFunctionDeclaration(ctx: any) {
        const nameNode = ctx.IDENTIFIER();
        if (nameNode) {
            // Manually inspect parameters to build signature for overload checking
            const paramsCtx = ctx.parameterList();
            let signature = "";
            if (paramsCtx) {
                const params = paramsCtx.parameter_list();
                const types = params.map((p: any) =>
                    p.typeSpecifier().getText()
                );
                signature = types.join(",");
            }
            this.analyzer.declare(
                nameNode.getText(),
                "func",
                "function",
                nameNode.symbol.column,
                signature
            );
        }
        // Enter scope for parameters and body
        this.analyzer.enterScope();
    }

    exitFunctionDeclaration(ctx: any) {
        this.analyzer.exitScope();
    }

    enterParameter(ctx: any) {
        const nameNode = ctx.IDENTIFIER();
        const typeCtx = ctx.typeSpecifier();
        if (nameNode) {
            const typeText = typeCtx ? typeCtx.getText() : "void";
            this.analyzer.declare(
                nameNode.getText(),
                typeText,
                "parameter",
                nameNode.symbol.column
            );
        }
    }

    // variableDeclaration: typeSpecifier IDENTIFIER (COMMA IDENTIFIER)* ...
    enterVariableDeclaration(ctx: any) {
        const typeCtx = ctx.typeSpecifier();
        const typeText = typeCtx ? typeCtx.getText() : "unknown";
        const identifiers = ctx.IDENTIFIER_list();
        const expressions = ctx.expression_list();

        // Mismatch operand count in initialization
        if (expressions && expressions.length > 0) {
            if (identifiers.length !== expressions.length) {
                this.analyzer.errors.push(
                    `SemError (Pos ${identifiers[0].symbol.column}): Assignment count mismatch: ${identifiers.length} variable(s) but ${expressions.length} value(s).`
                );
            }
        }

        for (const idNode of identifiers) {
            this.analyzer.declare(
                idNode.getText(),
                typeText,
                "variable",
                idNode.symbol.column
            );
        }
    }

    // assignment: designator (COMMA designator)* ASSIGN expression (COMMA expression)*
    enterAssignment(ctx: any) {
        if (ctx.ASSIGN()) {
            const designators = ctx.designator_list();
            const expressions = ctx.expression_list();

            // Mismatch operand count in assignment
            if (designators.length !== expressions.length) {
                const pos =
                    designators.length > 0 ? designators[0].start.column : 0;
                this.analyzer.errors.push(
                    `SemError (Pos ${pos}): Assignment count mismatch: ${designators.length} left-hand operand(s) but ${expressions.length} right-hand operand(s).`
                );
            }
        }
    }

    enterDesignator(ctx: any) {
        const nameNode = ctx.IDENTIFIER();
        if (nameNode) {
            this.analyzer.checkIdentifier(
                nameNode.getText(),
                nameNode.symbol.column
            );
        }
    }

    enterFunctionCall(ctx: any) {
        const nameNode = ctx.IDENTIFIER();
        if (nameNode) {
            this.analyzer.checkIdentifier(
                nameNode.getText(),
                nameNode.symbol.column
            );
        }
    }

    enterForStatement(ctx: any) {
        // For loop creates implicit scope for initializer
        this.analyzer.enterScope();
    }

    exitForStatement(ctx: any) {
        this.analyzer.exitScope();
    }

    enterBlock(ctx: any) {
        this.analyzer.enterScope();
    }

    exitBlock(ctx: any) {
        this.analyzer.exitScope();
    }
}

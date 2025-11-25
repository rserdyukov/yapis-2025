# MathPL Compiler

**MathPL** is a strongly-typed programming language compiler written in **Python** using **ANTLR4**. It compiles source code into **WebAssembly (WASM)** text format (`.wat`) and binary format (`.wasm`), allowing MathPL code to run in web browsers or WASM runtimes.

## Prerequisites

Before running the compiler, ensure you have the following installed:

1.  **Python 3.8+**
2.  **Java (JRE or JDK)**: Required by ANTLR to generate the parser files.

---

## Automated Setup & Usage (Recommended)

The project includes helper scripts to automate dependency installation (`ANTLR`, `wat2wasm`), environment setup (`venv`), and testing.

### 1. Bootstrap the Environment
Run the `bootstrap_compiler.py` script to set up the project. This script will:
*   Create a Python virtual environment (`.venv`).
*   Install Python dependencies.
*   Download the **ANTLR** JAR file.
*   Download **wabt** (WebAssembly Binary Toolkit) containing `wat2wasm`.
*   Generate the Python lexer and parser from the `.g4` grammar file.

```bash
python bootstrap_compiler.py
```

### 2. Run Examples
To compile the example files located in `../examples/correct_examples`, use the `run_examples.py` script. It automatically detects the virtual environment setup in the previous step.

```bash
python run_examples.py
```

Artifacts (`.wat` and `.wasm` files) will be generated in the `out/` directory.

---

## Manual Usage (CLI)

If you prefer to run the compiler manually or want to integrate it into your own workflow, follow these steps.

### 1. Activate Virtual Environment
Ensure dependencies are installed and the environment is active.

**Windows:**
```powershell
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
source .venv/bin/activate
```

### 2. Run the Compiler
Run the compiler module (`mathpl_compiler`) targeting your source file.

**Basic syntax:**
```bash
python -m mathpl_compiler path/to/source.txt [options]
```

**Options:**
*   `-o <dir>`, `--output <dir>`: Specify the output directory (default is the source directory).
*   `--wasm`: Automatically compile the generated `.wat` file to binary `.wasm` (requires `wat2wasm` to be in your system PATH or project root).

---

## Project Structure

*   `bootstrap_compiler.py`: Setup script (downloads tools, generates parser, inits venv).
*   `run_examples.py`: Test runner for compiling examples.
*   `mathpl_compiler/`: Source code of the compiler.
    *   `pipeline.py`: Main compilation logic.
    *   `analyzer.py`: Semantic analysis and type checking.
    *   `wat_generator.py`: Code generation (AST to WAT).
*   `GrammarMathPL.g4`: ANTLR4 grammar file.
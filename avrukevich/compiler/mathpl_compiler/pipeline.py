import os
import subprocess
import shutil

from antlr4 import FileStream, CommonTokenStream
from antlr_generated import GrammarMathPLLexer, GrammarMathPLParser

from .analyzer import MathPLSemanticAnalyzer
from .utils import MathPLErrorListener
from .wat_generator import WatCodeGenerator


def compile_source(file_path: str, output_dir: str | None = None, to_wasm: bool = False) -> bool:
    try:
        input_stream = FileStream(file_path, encoding="utf-8")
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'")
        return False
    except Exception as e:
        print(f"Error: {e} while reading file")
        return False
    
    error_listener = MathPLErrorListener()
    lexer = GrammarMathPLLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    stream = CommonTokenStream(lexer)
    parser = GrammarMathPLParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener) 

    print(f"Starting syntax check for: {file_path}")
    tree = parser.program()
    if error_listener.errors:
        print("Syntax check failed. Errors found:")
        for error in error_listener.errors:
            print(error)
        return False
    print("Syntax check successful.")

    print(f"Starting semantic analysis...")
    analyzer = MathPLSemanticAnalyzer(error_listener)
    analyzer.visit(tree)
    if error_listener.errors:
        print("Compilation failed. Errors found:")
        for error in error_listener.errors:
            print(error)
        return False
    print("Semantic analysis successful.")

    print(f"Starting WAT code generation...")
    code_generator = WatCodeGenerator(analyzer)
    wat_code = code_generator.visit(tree)

    try:
        base_name = os.path.basename(file_path)
        file_name_no_ext = os.path.splitext(base_name)[0]

        if output_dir:
            target_dir = output_dir
            os.makedirs(target_dir, exist_ok=True)
        else:
            target_dir = os.path.dirname(file_path) or "."

        wat_output_path = os.path.join(target_dir, f"{file_name_no_ext}.wat")

        with open(wat_output_path, 'w', encoding='utf-8') as f:
            f.write(wat_code)
        print(f"Generated WAT: '{wat_output_path}'")

        if to_wasm:
                wasm_output_path = os.path.join(target_dir, f"{file_name_no_ext}.wasm")
                print(f"Compiling to binary WASM...")
                
                executable = shutil.which("wat2wasm")

                if executable is None:
                    current_dir = os.getcwd()
                    module_dir = os.path.dirname(os.path.abspath(__file__))
                    
                    exe_name = "wat2wasm.exe" if os.name == 'nt' else "wat2wasm"
                    
                    potential_paths = [
                        os.path.join(current_dir, exe_name),
                        os.path.join(module_dir, exe_name),
                        os.path.join(current_dir, "bin", exe_name)
                    ]
                    
                    for path in potential_paths:
                        if os.path.isfile(path):
                            executable = path
                            break

                if executable is None:
                    print("\n[ERROR] Could not find 'wat2wasm'.")
                    print("Please install WABT (The WebAssembly Binary Toolkit) and add it to your PATH.")
                    print("Download: https://github.com/WebAssembly/wabt/releases")
                    return True

                try:
                    cmd = [executable, wat_output_path, "-o", wasm_output_path]
                    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print(f"Successfully compiled: '{wasm_output_path}'")
                    
                except subprocess.CalledProcessError as e:
                    print(f"\n[ERROR] wat2wasm failed with exit code {e.returncode}.")
                    # Вывод stderr может помочь понять, почему wat2wasm упал (например, синтаксическая ошибка в WAT)
                    print(e.stderr.decode('utf-8'))
                    return False
                except Exception as e:
                    print(f"[ERROR] Unexpected error running wat2wasm: {e}")
                    return False

    except Exception as e:
        print(f"Error writing output file: {e}")
        return False

    return True
import os
import sys
import subprocess


VENV_DIR = ".venv"
EXAMPLES_DIR = os.path.join("..", "examples", "correct_examples")
OUTPUT_DIR = "out"
MODULE_NAME = "mathpl_compiler"


def log(msg):
    print(f"[RUN] {msg}")


def get_venv_python():
    if os.name == 'nt':
        py = os.path.join(VENV_DIR, 'Scripts', 'python.exe')
    else:
        py = os.path.join(VENV_DIR, 'bin', 'python')
    
    if not os.path.exists(py):
        log(f"ERROR: Virtual environment not found in '{py}'.")
        log("Please run 'bootstrap_compiler.py' first!")
        sys.exit(1)
    return py


def run_tests():
    in_venv = (sys.prefix != sys.base_prefix)
    
    if not in_venv:
        venv_python = get_venv_python()
        log("Relaunching script in virtual environment...")
        subprocess.call([venv_python, __file__] + sys.argv[1:])
        return

    if not os.path.exists("antlr_generated"):
        log("ERROR: Folder 'antlr_generated' not found. Please run 'bootstrap_compiler.py' first!")
        sys.exit(1)

    if not os.path.exists(EXAMPLES_DIR):
        log(f"Folder {EXAMPLES_DIR} not found.")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = [f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".mpl") or f.endswith(".txt")]
    
    if not files:
        log("Example files not found.")
        return

    log(f"Found example files: {len(files)}. Running compiler...")
    
    success_count = 0
    for file in files:
        source_path = os.path.join(EXAMPLES_DIR, file)
        
        cmd = [
            sys.executable, 
            "-m", MODULE_NAME, 
            source_path, 
            "-o", OUTPUT_DIR, 
            "--wasm"
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f" [OK] {file}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f" [FAIL] {file}")
            print("      " + e.stdout.replace("\n", "\n      "))
    
    log(
        f"Result: Successful {success_count} out of {len(files)}. "
        "You can find .wat and .wasm of your examples in out/ folder"
    )

if __name__ == "__main__":
    run_tests()
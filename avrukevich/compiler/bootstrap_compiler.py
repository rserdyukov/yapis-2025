import os
import sys
import platform
import urllib.request
import tarfile
import subprocess
import venv


# --- CONFIG ---

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

REQUIREMENTS_FILE = os.path.join(BASE_DIR, "requirements.txt")
VENV_DIR = os.path.join(BASE_DIR, ".venv")
GEN_DIR = os.path.join(BASE_DIR, "antlr_generated")
GRAMMAR_FILE = os.path.join(BASE_DIR, "GrammarMathPL.g4")
ANTLR_JAR = os.path.join(BASE_DIR, "antlr-4.13.2-complete.jar")

ANTLR_URL = "https://www.antlr.org/download/antlr-4.13.2-complete.jar"
WABT_VERSION = "1.0.35"
WABT_BASE_URL = f"https://github.com/WebAssembly/wabt/releases/download/{WABT_VERSION}/"


def log(msg):
    print(f"[BOOTSTRAP] {msg}")


def run_command(cmd, cwd=None, capture=False):
    working_dir = cwd if cwd else BASE_DIR
    try:
        subprocess.run(cmd, check=True, cwd=working_dir, capture_output=capture)
    except subprocess.CalledProcessError as e:
        log(f"ERROR running command: {' '.join(cmd)}")
        if capture and e.stderr:
            print(e.stderr.decode())
        elif e.stderr:
            print(e.stderr.decode())
        sys.exit(1)


def get_venv_python():
    if os.name == 'nt':
        return os.path.join(VENV_DIR, 'Scripts', 'python.exe')
    else:
        return os.path.join(VENV_DIR, 'bin', 'python')


def create_venv():
    if not os.path.exists(VENV_DIR):
        log(f"Creating virtual environment in '{VENV_DIR}'...")
        venv.create(VENV_DIR, with_pip=True)
    else:
        log(f"Virtual environment '{VENV_DIR}' already exists.")


def install_dependencies():
    python_bin = get_venv_python()
    
    log("Updating pip...")
    run_command([python_bin, "-m", "pip", "install", "--upgrade", "pip"], capture=True)

    if os.path.exists(REQUIREMENTS_FILE):
        log(f"Installing dependencies from {REQUIREMENTS_FILE}...")
        try:
            run_command([python_bin, "-m", "pip", "install", "-r", REQUIREMENTS_FILE])
            log("Dependencies are successfully installed.")
        except SystemExit:
            log("Dependencies installation failed.")
            sys.exit(1)
    else:
        log(f"WARNING: File {REQUIREMENTS_FILE} doesn't exist")
        log("Installing minimal dependencies manually (antlr4-python3-runtime)...")
        run_command([python_bin, "-m", "pip", "install", "antlr4-python3-runtime==4.13.2"])


def download_tools():
    if not os.path.exists(ANTLR_JAR):
        log(f"Downloading {os.path.basename(ANTLR_JAR)}...")
        urllib.request.urlretrieve(ANTLR_URL, ANTLR_JAR)
    
    exe_name = "wat2wasm.exe" if os.name == 'nt' else "wat2wasm"
    exe_path = os.path.join(BASE_DIR, exe_name)

    if os.path.exists(exe_path):
        return

    system = platform.system().lower()
    if "windows" in system: filename = f"wabt-{WABT_VERSION}-windows.tar.gz"
    elif "linux" in system: filename = f"wabt-{WABT_VERSION}-ubuntu.tar.gz"
    elif "darwin" in system: filename = f"wabt-{WABT_VERSION}-macos.tar.gz"
    else: 
        log("Can't recognize OS for wat2wasm.")
        return

    archive_path = os.path.join(BASE_DIR, filename)
    
    log(f"Downloading {filename}...")
    try:
        urllib.request.urlretrieve(WABT_BASE_URL + filename, archive_path)
    except Exception as e:
        log(f"Error while downloading: {e}")
        sys.exit(1)
    
    log("Unpacking wat2wasm...")
    with tarfile.open(archive_path, "r:gz") as tar:
        member = next((m for m in tar.getmembers() if m.name.endswith(f"/bin/{exe_name}")), None)
        if member:
            member.name = exe_name 
            tar.extract(member, path=BASE_DIR)
    
    if os.path.exists(archive_path): os.remove(archive_path)
    
    if os.name != 'nt': 
        os.chmod(exe_path, 0o755)


def generate_parser():
    log("Generating ANTLR files...")
    
    try:
        subprocess.run(["java", "-version"], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        log("ERROR: Java not found. Please install Java and put it to PATH, if able")
        sys.exit(1)

    if not os.path.exists(GEN_DIR): os.makedirs(GEN_DIR)

    if not os.path.exists(GRAMMAR_FILE):
        log(f"ERROR: Grammar file {GRAMMAR_FILE} not found.")
        sys.exit(1)

    cmd = [
        "java", "-jar", ANTLR_JAR,
        "-Dlanguage=Python3", "-visitor", "-no-listener",
        "-o", GEN_DIR, GRAMMAR_FILE
    ]
    run_command(cmd)

    init_file = os.path.join(GEN_DIR, "__init__.py")
    init_content = """from .GrammarMathPLLexer import GrammarMathPLLexer
from .GrammarMathPLParser import GrammarMathPLParser
from .GrammarMathPLVisitor import GrammarMathPLVisitor

__all__ = ["GrammarMathPLLexer", "GrammarMathPLParser", "GrammarMathPLVisitor"]
"""
    with open(init_file, "w") as f:
        f.write(init_content)


def main():
    log(f"Bootstrap starting in: {BASE_DIR}")
    
    create_venv()
    
    install_dependencies()
    
    download_tools()
    
    generate_parser()
    
    log("Bootstrap finished!")
    log("You can run tests with 'run_examples.py' (script uses venv automatically).")


if __name__ == "__main__":
    main()
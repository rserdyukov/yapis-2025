import sys
import importlib.util
import marshal
import struct
import time
from bytecode import Bytecode, Instr, Label, Compare

CMP_MAP = {
    '<': Compare.LT,
    '<=': Compare.LE,
    '==': Compare.EQ,
    '!=': Compare.NE,
    '>': Compare.GT,
    '>=': Compare.GE,
}

def parse_arg(op_name, arg, labels):
    if arg is None:
        return None

    if op_name == 'COMPARE_OP':
        if arg in CMP_MAP:
            return CMP_MAP[arg]
        else:
            print(f"Warning: Unknown comparison operator '{arg}', defaulting to EQ")
            return Compare.EQ
  
    if arg.startswith('L') and arg[1:].isdigit():
        if arg not in labels:
            labels[arg] = Label()
        return labels[arg]
    
  
    try:
        if '.' in arg:
            return float(arg)
        return int(arg)
    except ValueError:
        pass
  
    if arg == "None": return None
    if arg == "True": return True
    if arg == "False": return False

    if (arg.startswith('"') and arg.endswith('"')) or (arg.startswith("'") and arg.endswith("'")):
        return arg[1:-1]
        
    return arg

def parse_asm_block(lines):
    bc = Bytecode()
    labels = {}
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith(';') or line.startswith('#'):
            continue
            
        if line.endswith(':'):
            label_name = line[:-1]
            if label_name not in labels:
                labels[label_name] = Label()
            bc.append(labels[label_name])
            continue
            
        parts = line.split(maxsplit=1)
        op_name = parts[0]
        
        if len(parts) > 1:
            arg_str = parts[1]
            arg = parse_arg(op_name, arg_str, labels)
            try:
                bc.append(Instr(op_name, arg))
            except Exception as e:
                print(f"Error creating instruction {op_name} {arg}: {e}")
                sys.exit(1)
        else:
            try:
                bc.append(Instr(op_name))
            except Exception as e:
                print(f"Error creating instruction {op_name}: {e}")
                sys.exit(1)
            
    return bc

def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    blocks = {}
    main_lines = []
    
    current_func_name = None
    current_func_lines = []
    current_func_args = []
    
    for line in content.splitlines():
        line = line.strip()
        if line.startswith(".def"):
            parts = line.split()
            current_func_name = parts[1]
            current_func_args = parts[2:]
            current_func_lines = []
        elif line.startswith(".enddef"):
            bc = parse_asm_block(current_func_lines)
            bc.argcount = len(current_func_args)
            bc.varnames = current_func_args
            blocks[current_func_name] = bc.to_code()
            current_func_name = None
        elif current_func_name:
            current_func_lines.append(line)
        else:
            main_lines.append(line)
            
    final_bc = Bytecode()
    main_bc_raw = parse_asm_block(main_lines)
    
    for item in main_bc_raw:
        if isinstance(item, Instr) and item.name == 'LOAD_CONST':
            if isinstance(item.arg, str) and item.arg.startswith('CODE:'):
                func_name = item.arg.split(':')[1]
                if func_name in blocks:
                    item.arg = blocks[func_name]
                else:
                    print(f"Warning: Code object for {func_name} not found!")
        final_bc.append(item)
        
    return final_bc.to_code()

def write_pyc(code_obj, output_path):
    with open(output_path, 'wb') as f:
        f.write(importlib.util.MAGIC_NUMBER)
        f.write(struct.pack('<I', 0))
        f.write(struct.pack('<I', int(time.time())))
        f.write(struct.pack('<I', 0))
        marshal.dump(code_obj, f)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python assembler.py <file.pyasm>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file.replace('.pyasm', '.pyc')
    
    try:
        code = parse_file(input_file)
        write_pyc(code, output_file)
        print(f"Successfully assembled {output_file}")
    except Exception as e:
        print(f"Assembly failed: {e}")
        sys.exit(1)
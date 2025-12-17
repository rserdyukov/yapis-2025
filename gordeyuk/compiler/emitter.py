from typing import Dict, List, Optional, Set
from constants import *

class Emitter:
    def __init__(self, main_instructions: List[str], 
                 function_instructions: Dict[str, List[str]],
                 function_local_counters: Dict[str, int],
                 semantic_analyzer):
        self.main_instructions = main_instructions
        self.function_instructions = function_instructions
        self.function_local_counters = function_local_counters
        self.semantic_analyzer = semantic_analyzer
        self.class_name = "StringLang"
        self.output_lines: List[str] = []
    
    def emit(self) -> str:
        self._emit_header()
        self._emit_main_method()
        self._emit_functions()
        
        return "\n".join(self.output_lines)
    
    def _emit_header(self):
        self.output_lines.append(f".class public {self.class_name}")
        self.output_lines.append(".super java/lang/Object")
        self.output_lines.append("")
    
    def _emit_main_method(self):
        self.output_lines.append(".method public static main([Ljava/lang/String;)V")
        
        max_locals = 20
        max_stack = 50
        
        self.output_lines.append(f"    .limit locals {max_locals}")
        self.output_lines.append(f"    .limit stack {max_stack}")
        
        for instr in self.main_instructions:
            self.output_lines.append(f"    {instr}")
        
        has_return = any(instr.strip() in ['return', 'ireturn', 'areturn'] 
                         for instr in self.main_instructions)
        
        if not has_return:
            self.output_lines.append("    return")
        
        self.output_lines.append(".end method")
        self.output_lines.append("")
    
    def _emit_functions(self):
        for func_name, instructions in self.function_instructions.items():
            self._emit_function(func_name, instructions)
    
    def _emit_function(self, func_name: str, instructions: List[str]):
        func = self.semantic_analyzer.functions_map.get(func_name)
        
        if not func:
            return
        
        param_types = [p.var_type for p in func.parameters]
        param_desc = "".join(self._type_to_descriptor(t) for t in param_types)
        return_desc = self._type_to_descriptor(func.return_type)
        
        self.output_lines.append(f".method public static {func_name}({param_desc}){return_desc}")
        
        max_locals = max(20, self.function_local_counters.get(func_name, 1) + 5)
        max_stack = 50
        
        self.output_lines.append(f"    .limit locals {max_locals}")
        self.output_lines.append(f"    .limit stack {max_stack}")
        
        for instr in instructions:
            self.output_lines.append(f"    {instr}")
        
        has_return = any(instr.strip() in ['return', 'ireturn', 'areturn'] 
                         for instr in instructions)
        
        if not has_return:
            if return_desc == "I":
                self.output_lines.append("    ldc 0")
                self.output_lines.append("    ireturn")
            else:
                self.output_lines.append('    ldc ""')
                self.output_lines.append("    areturn")
        
        self.output_lines.append(".end method")
        self.output_lines.append("")
    
    def _type_to_descriptor(self, var_type: str) -> str:
        return JVM_TYPE_DESCRIPTORS.get(var_type, "Ljava/lang/Object;")
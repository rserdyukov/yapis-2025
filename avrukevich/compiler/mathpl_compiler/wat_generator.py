import collections

from antlr_generated import GrammarMathPLVisitor, GrammarMathPLParser

from .analyzer import MathPLSemanticAnalyzer
from . import types


class WatCodeGenerator(GrammarMathPLVisitor):

    def __init__(self, analyzer: MathPLSemanticAnalyzer):
        self.analyzer = analyzer
        self.wat_lines = []
        self.indent_level = 0
        self.type_map = {
            types.INT: "i32",
            types.FLOAT: "f64",
            types.BOOL: "i32",
            types.STRING: "i32", 
        }

    def _add_line(self, text: str, indent_change: int = 0):
        if indent_change < 0:
            self.indent_level += indent_change
        if text:
            self.wat_lines.append("  " * self.indent_level + text)
        if indent_change > 0:
            self.indent_level += indent_change

    def _wat_type(self, mptype) -> str:
        if isinstance(mptype, types.ArrayType):
            return "i32" # Pointer
        return self.type_map.get(mptype, "i32")

    def _get_element_size(self, mptype) -> int:
        """Возвращает размер элемента в байтах для массива данного типа."""
        if mptype == types.FLOAT:
            return 8
        return 4

    def _get_var_name(self, symbol: types.Symbol) -> str:
        if symbol.category == types.SymbolCategory.GLOBAL:
            return f"${symbol.name}"
        else:
            return f"$var_{symbol.index}"

    def _collect_locals(self, ctx: GrammarMathPLParser.BlockContext) -> dict:
        locals_map = {} 
        if not ctx: return locals_map
        
        for stmt in ctx.statement():
            if stmt.variableDeclaration():
                symbol = stmt.variableDeclaration().symbol_info
                if symbol.category == types.SymbolCategory.LOCAL:
                    locals_map[symbol.index] = symbol
            elif stmt.ifStatement():
                locals_map.update(self._collect_locals(stmt.ifStatement().block(0)))
                if stmt.ifStatement().block(1):
                    locals_map.update(self._collect_locals(stmt.ifStatement().block(1)))
            elif stmt.whileStatement():
                locals_map.update(self._collect_locals(stmt.whileStatement().block()))
            elif stmt.forStatement():
                if stmt.forStatement().forInitializer():
                    init_symbol = stmt.forStatement().forInitializer().symbol_info
                    if init_symbol and init_symbol.category == types.SymbolCategory.LOCAL:
                        locals_map[init_symbol.index] = init_symbol
                locals_map.update(self._collect_locals(stmt.forStatement().block()))
        return locals_map

    def visitProgram(self, ctx:GrammarMathPLParser.ProgramContext):
        self._add_line("(module", 1)
        
        # --- Imports ---
        self._add_line(';; --- Imports ---')
        self._add_line('(import "env" "print_str" (func $print (param i32)))')
        self._add_line('(import "env" "print_i32" (func $print_i32 (param i32)))')
        self._add_line('(import "env" "print_f64" (func $print_f64 (param f64)))')
        self._add_line('(import "env" "input" (func $input (result i32)))')
        self._add_line('(import "env" "i32_to_str" (func $i32_to_str (param i32) (result i32)))')
        self._add_line('(import "env" "bool_to_str" (func $bool_to_str (param i32) (result i32)))')
        self._add_line('(import "env" "f64_to_str" (func $f64_to_str (param f64) (result i32)))')
        self._add_line('(import "env" "str_to_int" (func $str_to_int (param i32) (result i32)))')
        self._add_line('(import "env" "str_to_float" (func $str_to_float (param i32) (result f64)))')
        self._add_line('(import "env" "concat" (func $concat (param i32 i32) (result i32)))')
        
        self._add_line('(import "js" "Math.pow" (func $pow (param f64 f64) (result f64)))')
        self._add_line('(import "js" "Math.sin" (func $sin (param f64) (result f64)))')
        self._add_line('(import "js" "Math.cos" (func $cos (param f64) (result f64)))')
        self._add_line('(import "js" "Math.tan" (func $tan (param f64) (result f64)))')
        self._add_line('(import "js" "Math.asin" (func $asin (param f64) (result f64)))')
        self._add_line('(import "js" "Math.acos" (func $acos (param f64) (result f64)))')
        self._add_line('(import "js" "Math.atan" (func $atan (param f64) (result f64)))')
        self._add_line('(import "js" "Math.log" (func $ln (param f64) (result f64)))')
        self._add_line('(import "js" "Math.log10" (func $log (param f64) (result f64)))')

        self._add_line("", 0)
        self._add_line("(memory 100)")
        self._add_line('(export "memory" (memory 0))')

        # Static Strings
        if self.analyzer.string_literals:
            for str_val, info in self.analyzer.string_literals.items():
                escaped_str = ""
                for char in str_val:
                    if ' ' <= char <= '~' and char not in ('\\', '"'):
                        escaped_str += char
                    else:
                        escaped_str += f"\\{ord(char):02x}"
                self._add_line(f'(data (i32.const {info["address"]}) "{escaped_str}\\00")')

        # Heap setup
        heap_start = 8
        if self.analyzer.string_literals:
            max_addr = 0
            for info in self.analyzer.string_literals.values():
                end = info['address'] + info['length']
                if end > max_addr:
                    max_addr = end
            heap_start = (max_addr + 7) & ~7 # Align to 8 bytes
        
        self._add_line(f';; Heap Pointer (starts at {heap_start})')
        self._add_line(f'(global $heap_pointer (mut i32) (i32.const {heap_start}))')
        
        # --- Internal Helpers ---
        # (Весь код хелперов $malloc, $memcpy, $slice и т.д. остается без изменений)
        self._add_line('(func $malloc (param $size i32) (result i32)', 1)
        self._add_line('(local $ptr i32)')
        self._add_line('(local $aligned_size i32)')
        self._add_line('global.get $heap_pointer')
        self._add_line('local.set $ptr')
        self._add_line('local.get $size')
        self._add_line('i32.const 7')
        self._add_line('i32.add')
        self._add_line('i32.const -8') 
        self._add_line('i32.and')
        self._add_line('local.set $aligned_size')
        self._add_line('global.get $heap_pointer')
        self._add_line('local.get $aligned_size')
        self._add_line('i32.add')
        self._add_line('global.set $heap_pointer')
        self._add_line('local.get $ptr')
        self._add_line(')', -1)

        self._add_line('(func $clamp_index (param $idx i32) (param $len i32) (result i32)', 1)
        self._add_line('local.get $idx')
        self._add_line('i32.const 0')
        self._add_line('i32.lt_s')
        self._add_line('(if (then i32.const 0 local.set $idx))')
        self._add_line('local.get $idx')
        self._add_line('local.get $len')
        self._add_line('i32.gt_s')
        self._add_line('(if (then local.get $len local.set $idx))')
        self._add_line('local.get $idx')
        self._add_line(')', -1)

        self._add_line('(func $normalize_index (param $ptr i32) (param $idx i32) (result i32)', 1)
        self._add_line('(local $len i32)')
        self._add_line('local.get $ptr')
        self._add_line('i32.load offset=4') 
        self._add_line('local.set $len')
        self._add_line('local.get $idx')
        self._add_line('i32.const 0')
        self._add_line('i32.lt_s')
        self._add_line('(if (then')
        self._add_line('  local.get $len')
        self._add_line('  local.get $idx')
        self._add_line('  i32.add')
        self._add_line('  local.set $idx')
        self._add_line('))')
        self._add_line('local.get $idx')
        self._add_line(')', -1)

        self._add_line('(func $memcpy_u32 (param $src i32) (param $dst i32) (param $count i32)', 1)
        self._add_line('(local $i i32)')
        self._add_line('(block $break (loop $top')
        self._add_line('local.get $i')
        self._add_line('local.get $count')
        self._add_line('i32.ge_s') 
        self._add_line('br_if $break')
        self._add_line('local.get $dst') 
        self._add_line('local.get $i')
        self._add_line('i32.const 4')
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('local.get $src') 
        self._add_line('local.get $i')
        self._add_line('i32.const 4')
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('i32.load')
        self._add_line('i32.store')
        self._add_line('local.get $i') 
        self._add_line('i32.const 1')
        self._add_line('i32.add')
        self._add_line('local.set $i')
        self._add_line('br $top')
        self._add_line('))')
        self._add_line(')', -1)

        self._add_line('(func $slice_i32 (param $ptr i32) (param $start i32) (param $end i32) (result i32)', 1)
        self._add_line('(local $new_len i32) (local $new_ptr i32) (local $len i32)')
        self._add_line('local.get $ptr')
        self._add_line('i32.load offset=4')
        self._add_line('local.set $len')
        self._add_line('local.get $start')
        self._add_line('local.get $len')
        self._add_line('call $clamp_index')
        self._add_line('local.set $start')
        self._add_line('local.get $end')
        self._add_line('local.get $len')
        self._add_line('call $clamp_index')
        self._add_line('local.set $end')
        self._add_line('local.get $end')
        self._add_line('local.get $start')
        self._add_line('i32.sub')
        self._add_line('local.set $new_len')
        self._add_line('local.get $new_len')
        self._add_line('i32.const 0')
        self._add_line('i32.lt_s')
        self._add_line('(if (then i32.const 0 local.set $new_len))')
        self._add_line('local.get $new_len')
        self._add_line('i32.const 4')
        self._add_line('i32.mul')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('call $malloc')
        self._add_line('local.set $new_ptr')
        self._add_line('local.get $new_ptr')
        self._add_line('local.get $new_len')
        self._add_line('i32.store') 
        self._add_line('local.get $new_ptr')
        self._add_line('local.get $new_len')
        self._add_line('i32.store offset=4') 
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $start')
        self._add_line('i32.const 4')
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('local.get $new_ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $new_len')
        self._add_line('call $memcpy_u32')
        self._add_line('local.get $new_ptr')
        self._add_line(')', -1)

        self._add_line('(func $slice_f64 (param $ptr i32) (param $start i32) (param $end i32) (result i32)', 1)
        self._add_line('(local $new_len i32) (local $new_ptr i32) (local $len i32)')
        self._add_line('local.get $ptr')
        self._add_line('i32.load offset=4')
        self._add_line('local.set $len')
        self._add_line('local.get $start')
        self._add_line('local.get $len')
        self._add_line('call $clamp_index')
        self._add_line('local.set $start')
        self._add_line('local.get $end')
        self._add_line('local.get $len')
        self._add_line('call $clamp_index')
        self._add_line('local.set $end')
        self._add_line('local.get $end')
        self._add_line('local.get $start')
        self._add_line('i32.sub')
        self._add_line('local.set $new_len')
        self._add_line('local.get $new_len')
        self._add_line('i32.const 0')
        self._add_line('i32.lt_s')
        self._add_line('(if (then i32.const 0 local.set $new_len))')
        self._add_line('local.get $new_len')
        self._add_line('i32.const 8')
        self._add_line('i32.mul')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('call $malloc')
        self._add_line('local.set $new_ptr')
        self._add_line('local.get $new_ptr')
        self._add_line('local.get $new_len')
        self._add_line('i32.store')
        self._add_line('local.get $new_ptr')
        self._add_line('local.get $new_len')
        self._add_line('i32.store offset=4')
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $start')
        self._add_line('i32.const 8')
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('local.get $new_ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $new_len')
        self._add_line('i32.const 2')
        self._add_line('i32.mul')
        self._add_line('call $memcpy_u32')
        self._add_line('local.get $new_ptr')
        self._add_line(')', -1)

        self._add_line('(func $reverse_i32 (param $ptr i32)', 1)
        self._add_line('(local $left i32) (local $right i32) (local $tmp i32) (local $addr_l i32) (local $addr_r i32)')
        self._add_line('i32.const 0')
        self._add_line('local.set $left')
        self._add_line('local.get $ptr')
        self._add_line('i32.load offset=4')
        self._add_line('i32.const 1')
        self._add_line('i32.sub')
        self._add_line('local.set $right')
        self._add_line('(block $break (loop $top')
        self._add_line('local.get $left')
        self._add_line('local.get $right')
        self._add_line('i32.ge_s')
        self._add_line('br_if $break')
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $left')
        self._add_line('i32.const 4')
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('local.set $addr_l')
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $right')
        self._add_line('i32.const 4')
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('local.set $addr_r')
        self._add_line('local.get $addr_l')
        self._add_line('i32.load')
        self._add_line('local.set $tmp')
        self._add_line('local.get $addr_l')
        self._add_line('local.get $addr_r')
        self._add_line('i32.load')
        self._add_line('i32.store')
        self._add_line('local.get $addr_r')
        self._add_line('local.get $tmp')
        self._add_line('i32.store')
        self._add_line('local.get $left')
        self._add_line('i32.const 1')
        self._add_line('i32.add')
        self._add_line('local.set $left')
        self._add_line('local.get $right')
        self._add_line('i32.const 1')
        self._add_line('i32.sub')
        self._add_line('local.set $right')
        self._add_line('br $top')
        self._add_line('))')
        self._add_line(')', -1)
        
        self._add_line('(func $reverse_f64 (param $ptr i32)', 1)
        self._add_line('(local $left i32) (local $right i32) (local $tmp f64) (local $addr_l i32) (local $addr_r i32)')
        self._add_line('i32.const 0')
        self._add_line('local.set $left')
        self._add_line('local.get $ptr')
        self._add_line('i32.load offset=4')
        self._add_line('i32.const 1')
        self._add_line('i32.sub')
        self._add_line('local.set $right')
        self._add_line('(block $break (loop $top')
        self._add_line('local.get $left')
        self._add_line('local.get $right')
        self._add_line('i32.ge_s')
        self._add_line('br_if $break')
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $left')
        self._add_line('i32.const 8')
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('local.set $addr_l')
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $right')
        self._add_line('i32.const 8')
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('local.set $addr_r')
        self._add_line('local.get $addr_l')
        self._add_line('f64.load')
        self._add_line('local.set $tmp')
        self._add_line('local.get $addr_l')
        self._add_line('local.get $addr_r')
        self._add_line('f64.load')
        self._add_line('f64.store')
        self._add_line('local.get $addr_r')
        self._add_line('local.get $tmp')
        self._add_line('f64.store')
        self._add_line('local.get $left')
        self._add_line('i32.const 1')
        self._add_line('i32.add')
        self._add_line('local.set $left')
        self._add_line('local.get $right')
        self._add_line('i32.const 1')
        self._add_line('i32.sub')
        self._add_line('local.set $right')
        self._add_line('br $top')
        self._add_line('))')
        self._add_line(')', -1)

        self._add_line('(func $check_bounds (param $ptr i32) (param $idx i32)', 1)
        self._add_line('(local $len i32)')
        self._add_line('local.get $ptr')
        self._add_line('i32.load offset=4')
        self._add_line('local.set $len')
        self._add_line('local.get $idx')
        self._add_line('i32.const 0')
        self._add_line('i32.lt_s')
        self._add_line('local.get $idx')
        self._add_line('local.get $len')
        self._add_line('i32.ge_s')
        self._add_line('i32.or')
        self._add_line('(if (then unreachable))')
        self._add_line(')', -1)

        self._add_line('(func $append_i32 (param $ptr i32) (param $val i32) (result i32)', 1)
        self._add_line('(local $len i32) (local $cap i32) (local $new_ptr i32) (local $new_cap i32)')
        self._add_line('local.get $ptr')
        self._add_line('i32.load') 
        self._add_line('local.set $cap')
        self._add_line('local.get $ptr')
        self._add_line('i32.load offset=4')
        self._add_line('local.set $len')
        self._add_line('local.get $len')
        self._add_line('local.get $cap')
        self._add_line('i32.lt_s')
        self._add_line('(if (result i32) (then local.get $ptr) (else', 1)
        self._add_line('local.get $cap')
        self._add_line('i32.const 2')
        self._add_line('i32.mul')
        self._add_line('i32.const 2')
        self._add_line('i32.add')
        self._add_line('local.set $new_cap')
        self._add_line('local.get $new_cap')
        self._add_line('i32.const 4')
        self._add_line('i32.mul')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('call $malloc')
        self._add_line('local.set $new_ptr')
        self._add_line('local.get $new_ptr')
        self._add_line('local.get $new_cap')
        self._add_line('i32.store')
        self._add_line('local.get $new_ptr')
        self._add_line('local.get $len')
        self._add_line('i32.store offset=4')
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $new_ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $len')
        self._add_line('call $memcpy_u32') 
        self._add_line('local.get $new_ptr') 
        self._add_line('))')
        self._add_line('local.set $ptr')
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $len')
        self._add_line('i32.const 4')
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('local.get $val')
        self._add_line('i32.store')
        self._add_line('local.get $ptr')
        self._add_line('local.get $len')
        self._add_line('i32.const 1')
        self._add_line('i32.add')
        self._add_line('i32.store offset=4')
        self._add_line('local.get $ptr') 
        self._add_line(')', -1)
        
        self._add_line('(func $append_f64 (param $ptr i32) (param $val f64) (result i32)', 1)
        self._add_line('(local $len i32) (local $cap i32) (local $new_ptr i32) (local $new_cap i32)')
        self._add_line('local.get $ptr')
        self._add_line('i32.load') 
        self._add_line('local.set $cap')
        self._add_line('local.get $ptr')
        self._add_line('i32.load offset=4')
        self._add_line('local.set $len')
        self._add_line('local.get $len')
        self._add_line('local.get $cap')
        self._add_line('i32.lt_s')
        self._add_line('(if (result i32) (then local.get $ptr) (else', 1)
        self._add_line('local.get $cap')
        self._add_line('i32.const 2')
        self._add_line('i32.mul')
        self._add_line('i32.const 2')
        self._add_line('i32.add')
        self._add_line('local.set $new_cap')
        self._add_line('local.get $new_cap')
        self._add_line('i32.const 8') 
        self._add_line('i32.mul')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('call $malloc')
        self._add_line('local.set $new_ptr')
        self._add_line('local.get $new_ptr')
        self._add_line('local.get $new_cap')
        self._add_line('i32.store')
        self._add_line('local.get $new_ptr')
        self._add_line('local.get $len')
        self._add_line('i32.store offset=4')
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $new_ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $len')
        self._add_line('i32.const 2') 
        self._add_line('i32.mul')
        self._add_line('call $memcpy_u32')
        self._add_line('local.get $new_ptr')
        self._add_line('))')
        self._add_line('local.set $ptr')
        self._add_line('local.get $ptr')
        self._add_line('i32.const 8')
        self._add_line('i32.add')
        self._add_line('local.get $len')
        self._add_line('i32.const 8') 
        self._add_line('i32.mul')
        self._add_line('i32.add')
        self._add_line('local.get $val')
        self._add_line('f64.store')
        self._add_line('local.get $ptr')
        self._add_line('local.get $len')
        self._add_line('i32.const 1')
        self._add_line('i32.add')
        self._add_line('i32.store offset=4')
        self._add_line('local.get $ptr')
        self._add_line(')', -1)

        self._add_line(';; --- Internal Helpers End ---')
        self._add_line('(func $deg_to_rad (param $deg f64) (result f64)', 1)
        self._add_line('local.get $deg')
        self._add_line('f64.const 0.017453292519943295') 
        self._add_line('f64.mul')
        self._add_line(')', -1)

        global_scope = self.analyzer.symbol_table[0]
        for name, symbol in global_scope.items():
            if symbol.category == types.SymbolCategory.GLOBAL:
                wat_type = self._wat_type(symbol.type)
                self._add_line(f"(global ${name} (mut {wat_type}) ({wat_type}.const 0))")

        func_defs = [item for item in ctx.children if isinstance(item, GrammarMathPLParser.FunctionDefinitionContext)]
        for func_def in func_defs:
            self.visit(func_def)

        global_stmts = [item for item in ctx.children if isinstance(item, GrammarMathPLParser.StatementContext)]
        if global_stmts:
            self._add_line('(func $_start (export "_start")', 1)
            self._add_line("(local $ptr_tmp i32)")
            self._add_line("(local $idx_tmp i32)")
            self._add_line("(local $size_tmp i32)")
            self._add_line("(local $len_tmp i32)")
            self._add_line("(local $temp_addr i32)")
            self._add_line("(local $tmp_val_i32 i32)")
            self._add_line("(local $tmp_val_f64 f64)")
            global_locals = {}
            for stmt in global_stmts:
                if stmt.ifStatement():
                    global_locals.update(self._collect_locals(stmt.ifStatement().block(0)))
                    if stmt.ifStatement().block(1):
                        global_locals.update(self._collect_locals(stmt.ifStatement().block(1)))
                elif stmt.whileStatement():
                    global_locals.update(self._collect_locals(stmt.whileStatement().block()))
                elif stmt.forStatement():
                    if stmt.forStatement().forInitializer():
                        init_ctx = stmt.forStatement().forInitializer()
                        if hasattr(init_ctx, 'symbol_info'):
                            sym = init_ctx.symbol_info
                            if sym and sym.category == types.SymbolCategory.LOCAL:
                                global_locals[sym.index] = sym
                    global_locals.update(self._collect_locals(stmt.forStatement().block()))
            
            for index in sorted(global_locals.keys()):
                symbol = global_locals[index]
                self._add_line(f"(local {self._get_var_name(symbol)} {self._wat_type(symbol.type)})")

            for stmt in global_stmts:
                self.visit(stmt)
            self._add_line(")", -1)
        
        self._add_line(")", -1)
        return "\n".join(self.wat_lines)

    def visitForStatement(self, ctx: GrammarMathPLParser.ForStatementContext):
        loop_id = f"$loop_for_{ctx.start.line}_{ctx.start.column}"
        block_id = f"$block_for_{ctx.start.line}_{ctx.start.column}"
        if ctx.forInitializer():
            self.visit(ctx.forInitializer())
        self._add_line(f"(block {block_id}", 1)
        self._add_line(f"(loop {loop_id}", 1)
        if ctx.expression():
            self.visit(ctx.expression())
            self._add_line("i32.eqz")
            self._add_line(f"br_if {block_id}")
        self.visit(ctx.block())
        if ctx.forUpdate():
            self.visit(ctx.forUpdate())
        self._add_line(f"br {loop_id}")
        self._add_line(")", -1)
        self._add_line(")", -1)

    def visitForInitializer(self, ctx: GrammarMathPLParser.ForInitializerContext):
        self.visit(ctx.expression())
        symbol = ctx.symbol_info
        if symbol.category == types.SymbolCategory.GLOBAL:
            self._add_line(f"global.set {self._get_var_name(symbol)}")
        else:
            self._add_line(f"local.set {self._get_var_name(symbol)}")

    def visitForUpdate(self, ctx: GrammarMathPLParser.ForUpdateContext):
        var_node = ctx.ID()
        if not var_node: return 
        symbol = ctx.symbol_info
        name = self._get_var_name(symbol)
        wat_type = self._wat_type(symbol.type)
        if ctx.ASSIGN() or ctx.PLUS_ASSIGN() or ctx.MINUS_ASSIGN() or ctx.MUL_ASSIGN() or ctx.DIV_ASSIGN():
            op_text = ctx.getChild(1).getText()
            if op_text != '=':
                if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.get {name}")
                else: self._add_line(f"local.get {name}")
            self.visit(ctx.expression())
            if op_text != '=':
                op_map = {'+=': 'add', '-=': 'sub', '*=': 'mul', '/=': 'div_s'}
                if wat_type == 'f64': op_map['/='] = 'div'
                self._add_line(f"{wat_type}.{op_map[op_text]}")
            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.set {name}")
            else: self._add_line(f"local.set {name}")
        elif ctx.INC() or ctx.DEC():
            op_token = ctx.INC() or ctx.DEC()
            op = "add" if op_token.getSymbol().type == GrammarMathPLParser.INC else "sub"
            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.get {name}")
            else: self._add_line(f"local.get {name}")
            self._add_line(f"{wat_type}.const 1")
            self._add_line(f"{wat_type}.{op}")
            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.set {name}")
            else: self._add_line(f"local.set {name}")

    def visitFunctionDefinition(self, ctx:GrammarMathPLParser.FunctionDefinitionContext):
        func_symbol = ctx.symbol_info
        params_list = []
        if ctx.functionInParameters():
            param_symbols = [p_id.symbol_info for p_id in ctx.functionInParameters().ID()]
            for symbol in param_symbols:
                param_wat_type = self._wat_type(symbol.type)
                params_list.append(f"(param {self._get_var_name(symbol)} {param_wat_type})")
        params_str = " ".join(params_list)
        result_str = f" (result {self._wat_type(func_symbol.return_type)})" if func_symbol.return_type != types.VOID else ""
        self._add_line(f"(func ${func_symbol.name} {params_str}{result_str}", 1)
        local_vars = self._collect_locals(ctx.block())
        for index in sorted(local_vars.keys()):
            symbol = local_vars[index]
            self._add_line(f"(local {self._get_var_name(symbol)} {self._wat_type(symbol.type)})")
        
        self._add_line(";; Internal temps")
        self._add_line("(local $ptr_tmp i32)")
        self._add_line("(local $idx_tmp i32)")
        self._add_line("(local $size_tmp i32)")
        self._add_line("(local $len_tmp i32)")
        self._add_line("(local $temp_addr i32)")
        self._add_line("(local $tmp_val_i32 i32)")
        self._add_line("(local $tmp_val_f64 f64)")
        
        self.visit(ctx.block())
        if func_symbol.return_type != types.VOID:
            if func_symbol.return_type == types.FLOAT: self._add_line("f64.const 0.0")
            else: self._add_line("i32.const 0")
        self._add_line(")", -1)

    def visitBlock(self, ctx:GrammarMathPLParser.BlockContext):
        for stmt in ctx.statement():
            self.visit(stmt)

    def visitVariableDeclaration(self, ctx:GrammarMathPLParser.VariableDeclarationContext):
        if ctx.expression():
            self.visit(ctx.expression())
            symbol = ctx.symbol_info
            name = self._get_var_name(symbol)
            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.set {name}")
            else: self._add_line(f"local.set {name}")
    
    def visitAssignmentStatement(self, ctx: GrammarMathPLParser.AssignmentStatementContext):
        left_expr = ctx.expression(0)
        right_expr = ctx.expression(1)
        op_text = ctx.getChild(1).getText()
        
        if left_expr.atom() and left_expr.atom().variable():
            symbol = left_expr.atom().variable().symbol_info
            name = self._get_var_name(symbol)
            if op_text != '=':
                if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.get {name}")
                else: self._add_line(f"local.get {name}")
            self.visit(right_expr)
            if op_text != '=':
                wat_type = self._wat_type(symbol.type)
                suffix = "_s" if wat_type == "i32" and op_text in ('/=', '%=') else ""
                if op_text == '/=' and wat_type == 'f64': suffix = ""
                op_map = {'+=': 'add', '-=': 'sub', '*=': 'mul', '/=': 'div'}
                self._add_line(f"{wat_type}.{op_map[op_text]}{suffix}")
            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.set {name}")
            else: self._add_line(f"local.set {name}")

        elif left_expr.LBRACK():
            arr_expr = left_expr.expression(0)
            idx_expr = left_expr.expression(1)
            
            # 1. Ptr & Idx
            self.visit(arr_expr)
            self._add_line("local.set $ptr_tmp") # Store cleanly
            self.visit(idx_expr)
            self._add_line("local.set $idx_tmp") # Store cleanly
            
            # 2. Normalize & Check
            self._add_line("local.get $ptr_tmp")
            self._add_line("local.get $idx_tmp")
            self._add_line("call $normalize_index")
            self._add_line("local.set $idx_tmp")
            
            self._add_line("local.get $ptr_tmp")
            self._add_line("local.get $idx_tmp")
            self._add_line("call $check_bounds")
            
            # 3. Calc Address
            elem_type = arr_expr.type.element_type
            elem_size = self._get_element_size(elem_type)
            
            self._add_line("local.get $ptr_tmp")
            self._add_line("i32.const 8")
            self._add_line("i32.add")
            self._add_line("local.get $idx_tmp")
            self._add_line(f"i32.const {elem_size}")
            self._add_line("i32.mul")
            self._add_line("i32.add") # Stack: [Addr]
            
            if op_text == '=':
                self.visit(right_expr) # Stack: [Addr, Val]
                if elem_size == 8: self._add_line("f64.store")
                else: self._add_line("i32.store")
            else:
                self._add_line("local.tee $temp_addr") # Stack: [Addr] (Saved to local for later use)
                self._add_line("local.get $temp_addr") # Stack: [Addr, Addr] (One for load, one for store later)
                
                # Load old val
                if elem_size == 8: self._add_line("f64.load")
                else: self._add_line("i32.load")
                
                self.visit(right_expr)
                
                # Op
                wat_type = "f64" if elem_size == 8 else "i32"
                suffix = "_s" if wat_type == "i32" and op_text in ('/=', '%=') else ""
                if op_text == '/=' and wat_type == 'f64': suffix = ""
                op_map = {'+=': 'add', '-=': 'sub', '*=': 'mul', '/=': 'div'}
                self._add_line(f"{wat_type}.{op_map[op_text]}{suffix}")
                
                # Stack now: [Addr, NewVal]
                if elem_size == 8: self._add_line("f64.store")
                else: self._add_line("i32.store")

    def visitReturnStatement(self, ctx:GrammarMathPLParser.ReturnStatementContext):
        if ctx.expression(): self.visit(ctx.expression())
        self._add_line("return")

    def visitIfStatement(self, ctx: GrammarMathPLParser.IfStatementContext):
        self.visit(ctx.expression())
        self._add_line("(if", 1)
        self._add_line("(then", 1)
        self.visit(ctx.block(0))
        self._add_line(")", -1)
        if ctx.block(1):
            self._add_line("(else", 1)
            self.visit(ctx.block(1))
            self._add_line(")", -1)
        self._add_line(")", -1)
        
    def visitWhileStatement(self, ctx: GrammarMathPLParser.WhileStatementContext):
        loop_id = f"$loop_{ctx.start.line}_{ctx.start.column}"
        block_id = f"$block_{ctx.start.line}_{ctx.start.column}"
        self._add_line(f"(block {block_id}", 1)
        self._add_line(f"(loop {loop_id}", 1)
        self.visit(ctx.expression())
        self._add_line("i32.eqz")
        self._add_line(f"br_if {block_id}")
        self.visit(ctx.block())
        self._add_line(f"br {loop_id}")
        self._add_line(")", -1)
        self._add_line(")", -1)

    def visitIncDecStatement(self, ctx:GrammarMathPLParser.IncDecStatementContext):
        target_expr = ctx.expression()
        op_token = ctx.INC() or ctx.DEC()
        op = "add" if op_token.getSymbol().type == GrammarMathPLParser.INC else "sub"
        
        if target_expr.atom() and target_expr.atom().variable():
            symbol = target_expr.atom().variable().symbol_info
            name = self._get_var_name(symbol)
            wat_type = self._wat_type(symbol.type)
            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.get {name}")
            else: self._add_line(f"local.get {name}")
            self._add_line(f"{wat_type}.const 1")
            self._add_line(f"{wat_type}.{op}")
            if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.set {name}")
            else: self._add_line(f"local.set {name}")
        
        elif target_expr.LBRACK():
            arr_expr = target_expr.expression(0)
            idx_expr = target_expr.expression(1)
            
            self.visit(arr_expr)
            self._add_line("local.set $ptr_tmp")
            self.visit(idx_expr)
            self._add_line("local.set $idx_tmp")
            
            self._add_line("local.get $ptr_tmp")
            self._add_line("local.get $idx_tmp")
            self._add_line("call $normalize_index")
            self._add_line("local.set $idx_tmp")

            self._add_line("local.get $ptr_tmp")
            self._add_line("local.get $idx_tmp")
            self._add_line("call $check_bounds")
            
            elem_type = arr_expr.type.element_type
            elem_size = self._get_element_size(elem_type)
            wat_type = "f64" if elem_size == 8 else "i32"

            self._add_line("local.get $ptr_tmp")
            self._add_line("i32.const 8")
            self._add_line("i32.add")
            self._add_line("local.get $idx_tmp")
            self._add_line(f"i32.const {elem_size}")
            self._add_line("i32.mul")
            self._add_line("i32.add")
            
            self._add_line("local.tee $temp_addr") # Stack: [Addr]
            self._add_line("local.get $temp_addr") # Stack: [Addr, Addr] (Prep for load)
            
            if elem_size == 8: self._add_line("f64.load")
            else: self._add_line("i32.load")
            
            self._add_line(f"{wat_type}.const 1")
            self._add_line(f"{wat_type}.{op}")
            
            # Stack: [Addr, NewVal]
            if elem_size == 8: self._add_line("f64.store")
            else: self._add_line("i32.store")


    def visitFunctionCall(self, ctx:GrammarMathPLParser.FunctionCallContext):
        is_statement = isinstance(ctx.parentCtx, GrammarMathPLParser.StatementContext)
        if ctx.functionArguments():
            for arg_expr in ctx.functionArguments().expression():
                self.visit(arg_expr)
        self._add_line(f"call ${ctx.ID().getText()}")
        if is_statement and ctx.symbol_info.return_type != types.VOID:
            self._add_line("drop")

    def visitExpression(self, ctx:GrammarMathPLParser.ExpressionContext):
        if ctx.atom():
            self.visit(ctx.atom())
            return

        if ctx.LBRACK():
            arr_expr = ctx.expression(0)
            
            if ctx.COLON():
                start_expr = ctx.expression(1)
                end_expr = ctx.expression(2)
                
                self.visit(arr_expr)
                self._add_line("local.set $ptr_tmp") # Clean stack
                
                self.visit(start_expr)
                self._add_line("local.set $idx_tmp")
                self._add_line("local.get $ptr_tmp")
                self._add_line("local.get $idx_tmp") 
                self._add_line("call $normalize_index")
                self._add_line("local.set $idx_tmp")
                
                self.visit(end_expr)
                self._add_line("local.set $len_tmp")
                self._add_line("local.get $ptr_tmp")
                self._add_line("local.get $len_tmp") 
                self._add_line("call $normalize_index") 
                self._add_line("local.set $len_tmp") 
                
                # Slice call args: ptr, start, end
                self._add_line("local.get $ptr_tmp")
                self._add_line("local.get $idx_tmp")
                self._add_line("local.get $len_tmp")

                elem_type = arr_expr.type.element_type
                if elem_type == types.FLOAT:
                    self._add_line("call $slice_f64")
                else:
                    self._add_line("call $slice_i32")
                return

            # Index [i]
            idx_expr = ctx.expression(1)
            
            # 1. Ptr
            self.visit(arr_expr)
            self._add_line("local.set $ptr_tmp") # Clean stack
            
            # 2. Idx
            self.visit(idx_expr)
            self._add_line("local.set $idx_tmp") # Clean stack
            
            # 3. Normalize
            self._add_line("local.get $ptr_tmp")
            self._add_line("local.get $idx_tmp")
            self._add_line("call $normalize_index") 
            self._add_line("local.set $idx_tmp")
            
            # 4. Check
            self._add_line("local.get $ptr_tmp")
            self._add_line("local.get $idx_tmp")
            self._add_line("call $check_bounds")
            
            elem_type = arr_expr.type.element_type
            elem_size = self._get_element_size(elem_type)
            
            # 5. Load
            self._add_line("local.get $ptr_tmp")
            self._add_line("i32.const 8")
            self._add_line("i32.add")
            self._add_line("local.get $idx_tmp")
            self._add_line(f"i32.const {elem_size}")
            self._add_line("i32.mul")
            self._add_line("i32.add")
            
            if elem_size == 8: self._add_line("f64.load")
            else: self._add_line("i32.load")
            return

        if ctx.DOT() and ctx.LENGTH():
            self.visit(ctx.expression(0))
            self._add_line("i32.const 4")
            self._add_line("i32.add")
            self._add_line("i32.load") 
            return

        if ctx.INC() or ctx.DEC():
            target_expr = ctx.expression(0)
            op_token = ctx.INC() if ctx.INC() else ctx.DEC()
            op_str = "add" if op_token.getSymbol().type == GrammarMathPLParser.INC else "sub"
            is_prefix = (ctx.getChild(0) == op_token)

            if target_expr.atom() and target_expr.atom().variable():
                symbol = target_expr.atom().variable().symbol_info
                name = self._get_var_name(symbol)
                wat_type = self._wat_type(symbol.type)
                
                # Logic:
                # Prefix (++x): calc new, store, return new
                # Postfix (x++): get old, store to tmp, calc new, store new, return tmp
                
                if is_prefix:
                    if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.get {name}")
                    else: self._add_line(f"local.get {name}")
                    self._add_line(f"{wat_type}.const 1")
                    self._add_line(f"{wat_type}.{op_str}")
                    # Stack: [NewVal]
                    if symbol.category == types.SymbolCategory.GLOBAL:
                        self._add_line(f"global.set {name}")
                        self._add_line(f"global.get {name}")
                    else:
                        self._add_line(f"local.tee {name}")
                else: # Postfix
                    if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.get {name}")
                    else: self._add_line(f"local.get {name}")
                    
                    # Stack: [OldVal]
                    if wat_type == "f64": self._add_line("local.tee $tmp_val_f64")
                    else: self._add_line("local.tee $tmp_val_i32")
                    
                    # Stack: [OldVal]
                    self._add_line(f"{wat_type}.const 1")
                    self._add_line(f"{wat_type}.{op_str}")
                    # Stack: [NewVal]
                    
                    if symbol.category == types.SymbolCategory.GLOBAL: self._add_line(f"global.set {name}")
                    else: self._add_line(f"local.set {name}")
                    
                    # Restore Old Val
                    if wat_type == "f64": self._add_line("local.get $tmp_val_f64")
                    else: self._add_line("local.get $tmp_val_i32")
                return
            else:
                 raise NotImplementedError("Increment/Decrement inside expressions is only supported for variables.")

        if ctx.MINUS() and len(ctx.expression()) == 1:
            self.visit(ctx.expression(0))
            wat_type = self._wat_type(ctx.type)
            if wat_type == "f64": self._add_line("f64.neg")
            else:
                self._add_line("i32.const -1")
                self._add_line("i32.mul")
            return

        if ctx.NOT():
            self.visit(ctx.expression(0))
            self._add_line("i32.eqz")
            return
        
        if len(ctx.expression()) == 2:
            left_expr = ctx.expression(0)
            right_expr = ctx.expression(1)
            op_symbol = ctx.getChild(1).symbol
            
            # Short-circuit logic
            if op_symbol.type == GrammarMathPLParser.AND:
                self.visit(left_expr)
                self._add_line("(if (result i32) (then")
                self.visit(right_expr)
                self._add_line("i32.const 0")
                self._add_line("i32.ne")
                self._add_line(") (else i32.const 0))")
                return

            if op_symbol.type == GrammarMathPLParser.OR:
                self.visit(left_expr)
                self._add_line("(if (result i32) (then i32.const 1) (else")
                self.visit(right_expr)
                self._add_line("i32.const 0")
                self._add_line("i32.ne")
                self._add_line("))")
                return
            
            if op_symbol.type == GrammarMathPLParser.POW:
                self.visit(left_expr)
                if left_expr.type == types.INT: self._add_line("f64.convert_i32_s")
                self.visit(right_expr)
                if right_expr.type == types.INT: self._add_line("f64.convert_i32_s")
                self._add_line("call $pow")
                return

            self.visit(left_expr)
            if left_expr.type == types.INT and right_expr.type == types.FLOAT: self._add_line("f64.convert_i32_s")
            self.visit(right_expr)
            if right_expr.type == types.INT and left_expr.type == types.FLOAT: self._add_line("f64.convert_i32_s")

            op_type = left_expr.type
            if op_type == types.STRING and op_symbol.type == GrammarMathPLParser.PLUS:
                self._add_line("call $concat")
                return
            
            op = op_symbol.type
            is_float = (left_expr.type == types.FLOAT or right_expr.type == types.FLOAT)
            
            op_map = {
                (False, GrammarMathPLParser.PLUS): "i32.add",
                (False, GrammarMathPLParser.MINUS): "i32.sub",
                (False, GrammarMathPLParser.MUL): "i32.mul",
                (False, GrammarMathPLParser.DIV): "i32.div_s",
                (False, GrammarMathPLParser.MOD): "i32.rem_s",
                (False, GrammarMathPLParser.EQ): "i32.eq",
                (False, GrammarMathPLParser.NEQ): "i32.ne",
                (False, GrammarMathPLParser.GT): "i32.gt_s",
                (False, GrammarMathPLParser.GTE): "i32.ge_s",
                (False, GrammarMathPLParser.LT): "i32.lt_s",
                (False, GrammarMathPLParser.LTE): "i32.le_s",

                (True, GrammarMathPLParser.PLUS): "f64.add",
                (True, GrammarMathPLParser.MINUS): "f64.sub",
                (True, GrammarMathPLParser.MUL): "f64.mul",
                (True, GrammarMathPLParser.DIV): "f64.div",
                (True, GrammarMathPLParser.EQ): "f64.eq",
                (True, GrammarMathPLParser.NEQ): "f64.ne",
                (True, GrammarMathPLParser.GT): "f64.gt",
                (True, GrammarMathPLParser.GTE): "f64.ge",
                (True, GrammarMathPLParser.LT): "f64.lt",
                (True, GrammarMathPLParser.LTE): "f64.le",
            }
            wat_op = op_map.get((is_float, op), ";; unimpl")
            self._add_line(f"{wat_op}")
            return

    def visitAtom(self, ctx:GrammarMathPLParser.AtomContext):
        if ctx.literal(): self.visit(ctx.literal())
        elif ctx.variable(): self.visit(ctx.variable())
        elif ctx.functionCall(): self.visit(ctx.functionCall())
        elif ctx.LPAREN(): self.visit(ctx.expression(0))
        elif ctx.typeCast(): self.visit(ctx.typeCast())
        
        elif ctx.NEW():
            target_type = self.analyzer._type_from_node(ctx.type_())
            elem_size = self._get_element_size(target_type)
            
            size_atom = ctx.atom()
            self.visit(size_atom)
            self._add_line("local.tee $size_tmp")
            
            self._add_line(f"i32.const {elem_size}")
            self._add_line("i32.mul")
            self._add_line("i32.const 8")
            self._add_line("i32.add")
            
            self._add_line("call $malloc") 
            self._add_line("local.tee $ptr_tmp")
            self._add_line("local.get $size_tmp")
            self._add_line("i32.store")
            self._add_line("local.get $ptr_tmp")
            self._add_line("local.get $size_tmp")
            self._add_line("i32.store offset=4")
            self._add_line("local.get $ptr_tmp")

        elif ctx.LBRACK():
            exprs = ctx.expression()
            size = len(exprs)
            
            if size > 0:
                first_type = self.analyzer.visit(exprs[0])
                elem_size = self._get_element_size(first_type)
            else:
                elem_size = 4 # Default to 4 if empty (should be caught by analyzer)

            bytes_needed = 8 + size * elem_size
            self._add_line(f"i32.const {bytes_needed}")
            self._add_line("call $malloc")
            self._add_line("local.tee $ptr_tmp")
            
            self._add_line(f"i32.const {size}")
            self._add_line("i32.store")
            self._add_line("local.get $ptr_tmp")
            self._add_line(f"i32.const {size}")
            self._add_line("i32.store offset=4")
            
            for i, expr in enumerate(exprs):
                self._add_line("local.get $ptr_tmp")
                self._add_line(f"i32.const {8 + i * elem_size}")
                self._add_line("i32.add")
                self.visit(expr)
                if elem_size == 8: self._add_line("f64.store")
                else: self._add_line("i32.store")
            
            self._add_line("local.get $ptr_tmp")

    def visitTypeCast(self, ctx: GrammarMathPLParser.TypeCastContext):
        self.visit(ctx.atom()) 
        source_type = ctx.atom().type
        target_type = self.analyzer._type_from_node(ctx.type_())
        if target_type == source_type: return 
        if target_type == types.STRING:
            if source_type == types.INT: self._add_line("call $i32_to_str")
            elif source_type == types.BOOL: self._add_line("call $bool_to_str")
            elif source_type == types.FLOAT: self._add_line("call $f64_to_str")
        elif target_type == types.FLOAT and source_type == types.INT:
            self._add_line("f64.convert_i32_s")
        elif target_type == types.INT and source_type == types.FLOAT:
            self._add_line("i32.trunc_f64_s")

    def visitLiteral(self, ctx:GrammarMathPLParser.LiteralContext):
        if ctx.type == types.INT: self._add_line(f"(i32.const {ctx.getText()})")
        elif ctx.type == types.FLOAT: self._add_line(f"(f64.const {ctx.getText()})")
        elif ctx.type == types.BOOL: self._add_line(f"(i32.const {'1' if ctx.getText() == 'true' else '0'})")
        elif ctx.type == types.STRING: self._add_line(f"(i32.const {ctx.address})")

    def visitVariable(self, ctx: GrammarMathPLParser.VariableContext):
        symbol = ctx.symbol_info
        name = self._get_var_name(symbol)
        if symbol.category == types.SymbolCategory.GLOBAL:
            self._add_line(f"(global.get {name})")
        else:
            self._add_line(f"(local.get {name})")

    def visitArrayStatement(self, ctx: GrammarMathPLParser.ArrayStatementContext):
        if ctx.APPEND():
            target_expr = ctx.expression(0)
            val_expr = ctx.expression(1)
            
            if target_expr.atom() and target_expr.atom().variable():
                self.visit(target_expr)
                self.visit(val_expr)   
                
                m_type = val_expr.type
                wat_type = self._wat_type(m_type)
                if wat_type == "f64": self._add_line("call $append_f64")
                else: self._add_line("call $append_i32")
                
                symbol = target_expr.atom().variable().symbol_info
                name = self._get_var_name(symbol)
                if symbol.category == types.SymbolCategory.GLOBAL: 
                    self._add_line(f"global.set {name}")
                else: 
                    self._add_line(f"local.set {name}")

            elif target_expr.LBRACK():
                arr_expr = target_expr.expression(0)
                idx_expr = target_expr.expression(1)
                
                
                self.visit(arr_expr)
                self._add_line("local.set $ptr_tmp")
                self.visit(idx_expr)
                self._add_line("local.set $idx_tmp")
                
                self._add_line("local.get $ptr_tmp")
                self._add_line("local.get $idx_tmp")
                self._add_line("call $normalize_index")
                self._add_line("local.set $idx_tmp")
                
                self._add_line("local.get $ptr_tmp")
                self._add_line("local.get $idx_tmp")
                self._add_line("call $check_bounds")
                
                
                elem_type = arr_expr.type.element_type
                elem_size = self._get_element_size(elem_type) 
                
                self._add_line("local.get $ptr_tmp")
                self._add_line("i32.const 8")
                self._add_line("i32.add")
                self._add_line("local.get $idx_tmp")
                self._add_line(f"i32.const {elem_size}") 
                self._add_line("i32.mul")
                self._add_line("i32.add")
                
                self._add_line("local.tee $temp_addr") 
                
                self._add_line("i32.load") 
                
                self.visit(val_expr)
                
                m_type = val_expr.type
                wat_type = self._wat_type(m_type)
                if wat_type == "f64": self._add_line("call $append_f64")
                else: self._add_line("call $append_i32")
                
                self._add_line("local.set $ptr_tmp")  
                self._add_line("local.get $temp_addr")
                self._add_line("local.get $ptr_tmp")  
                self._add_line("i32.store") 
                
            else:
                self.visit(target_expr)
                self.visit(val_expr)
                
                m_type = val_expr.type
                wat_type = self._wat_type(m_type)
                if wat_type == "f64": self._add_line("call $append_f64")
                else: self._add_line("call $append_i32")
                
                self._add_line("drop")

        elif ctx.REVERSE():
            target_expr = ctx.expression(0)
            self.visit(target_expr)
            arr_type = target_expr.type 
            elem_type = arr_type.element_type
            wat_type = self._wat_type(elem_type)
            if wat_type == "f64": self._add_line("call $reverse_f64")
            else: self._add_line("call $reverse_i32")
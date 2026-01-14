"""
Генерация встроенных функций WAT
"""

from .emitter import WATEmitter


class WATBuiltins:
    """Генерирует встроенные функции для WAT"""
    
    def __init__(self, emitter: WATEmitter):
        self.emitter = emitter
    
    def emit_all(self):
        """Генерирует все встроенные функции"""
        self.emitter.emit(";; Built-in functions")
        self._emit_write()
        self._emit_read()
        self._emit_alloc()
        self._emit_length()
    
    def _emit_write(self):
        """write function"""
        self.emitter.emit("(func $write (param $value i32)")
        self.emitter.indent()
        self.emitter.emit("(call $print_i32 (local.get $value))")
        self.emitter.dedent()
        self.emitter.emit(")")
        self.emitter.emit("")
    
    def _emit_read(self):
        """read function"""
        self.emitter.emit("(func $read (result i32)")
        self.emitter.indent()
        self.emitter.emit("(call $read_i32)")
        self.emitter.dedent()
        self.emitter.emit(")")
        self.emitter.emit("")
    
    def _emit_alloc(self):
        """alloc function (простой bump allocator)"""
        self.emitter.emit("(func $alloc (param $size i32) (result i32)")
        self.emitter.indent()
        self.emitter.emit("(local $ptr i32)")
        self.emitter.emit("(local.set $ptr (global.get $heap_ptr))")
        self.emitter.emit("(global.set $heap_ptr (i32.add (global.get $heap_ptr) (local.get $size)))")
        self.emitter.emit("(local.get $ptr)")
        self.emitter.dedent()
        self.emitter.emit(")")
        self.emitter.emit("")
    
    def _emit_length(self):
        """length function для списков"""
        self.emitter.emit("(func $length (param $list i32) (result i32)")
        self.emitter.indent()
        self.emitter.emit("(i32.load (local.get $list))")
        self.emitter.dedent()
        self.emitter.emit(")")
        self.emitter.emit("")

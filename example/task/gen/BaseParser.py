from typing import TextIO
from antlr4 import Parser, TokenStream


class BaseParser(Parser):

    def __init__(self, input: TokenStream, output: TextIO):
        super().__init__(input, output)
        self.errors = []
        self.names = {}
        self.codes = []
        self.consts = []
        self.variable_count = 0
        self.label_count = 0
        self.const_count = 0

    def next_temporal_variable(self):
        self.variable_count += 1
        return f"t{self.variable_count}"

    def next_temporal_label(self):
        self.label_count += 1
        return f"l{self.label_count}"

    def next_temporal_const(self):
        self.const_count += 1
        return f"d{self.const_count}"

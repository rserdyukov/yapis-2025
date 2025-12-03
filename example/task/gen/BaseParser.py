from typing import TextIO
from antlr4 import Parser, TokenStream


class BaseParser(Parser):

    def __init__(self, input:TokenStream, output:TextIO):
        super().__init__(input, output)
        self.errors = []
        self.names = {}
        self.codes = []
        self.consts = []
        self.variableCount = 0
        self.labelCount = 0
        self.constCount = 0

    def next_temporal_variable(self):
        self.variableCount += 1
        return f"t{self.variableCount}"

    def next_temporal_label(self):
        self.labelCount += 1
        return f"l{self.labelCount}"

    def next_temporal_const(self):
        self.labelCount += 1
        return f"d{self.labelCount}"
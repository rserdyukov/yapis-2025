from typing import TextIO
from antlr4 import Parser, TokenStream


class BaseParser(Parser):

    def __init__(self, input:TokenStream, output:TextIO):
        super().__init__(input, output)
        self.codes = []
        self.errors = []
        self.names = {}
        self.variableCount = 0
        self.labelCount = 0

    def next_temporal_variable(self):
        self.variableCount += 1
        return f"t{self.variableCount}"

    def next_temporal_label(self):
        self.labelCount += 1
        return f"l{self.labelCount}"
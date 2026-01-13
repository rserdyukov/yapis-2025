# Custom lexer with INDENT/DEDENT support for Python-like indentation
from antlr4 import Token
from gen.yapis2Lexer import yapis2Lexer

# Token type constants from yapis2Parser
INDENT = 51
DEDENT = 52
NEWLINE = 48
WS = 49
COMMENT = 50

class yapis2IndentLexer(yapis2Lexer):
    def __init__(self, input=None, output=None):
        super().__init__(input, output)
        self.indent_stack = [0]  # Stack of indentation levels (0 = base level)
        self.tokens = []  # Queue of tokens to emit
        self.eof_processed = False
        self.first_token = True  # Track if this is the first token

    def nextToken(self):
        # If we have tokens in queue, emit them first
        if len(self.tokens) > 0:
            return self.tokens.pop(0)
        
        # If EOF already processed, return EOF token
        if self.eof_processed:
            return self._factory.create(
                self._tokenFactorySourcePair, 
                Token.EOF, 
                "EOF", 
                self._channel, 
                -1, 
                -1, 
                -1, 
                -1
            )
        
        # Get next token from parent lexer
        token = super().nextToken()
        
        # Skip initial NEWLINE tokens (leading blank lines) before first content
        if self.first_token:
            self.first_token = False
            # Skip COMMENT and NEWLINE tokens at the start
            while token.type in [NEWLINE, COMMENT] or (token.type == WS):
                if token.type == Token.EOF:
                    break
                token = super().nextToken()
            # Now we have the first real token
        
        # Process NEWLINE tokens to handle indentation
        if token.type == NEWLINE:
            return self._process_newline(token)
        
        # For EOF, emit pending DEDENTs
        if token.type == Token.EOF:
            self.eof_processed = True
            # Emit all pending DEDENTs before EOF
            while len(self.indent_stack) > 1:
                self.indent_stack.pop()
                dedent_token = self._create_token(
                    DEDENT, 
                    "DEDENT", 
                    token.start, 
                    token.stop, 
                    token.line, 
                    token.column
                )
                self.tokens.append(dedent_token)
            self.tokens.append(token)
            return self.nextToken()
        
        return token

    def _process_newline(self, newline_token):
        """Process NEWLINE token and generate INDENT/DEDENT as needed"""
        # Peek at next token to determine if it's EOF or empty line
        next_token = self._peek_next_token()
        
        # Handle EOF
        if next_token.type == Token.EOF:
            self.eof_processed = True
            # Emit all pending DEDENTs
            while len(self.indent_stack) > 1:
                self.indent_stack.pop()
                dedent_token = self._create_token(
                    DEDENT, 
                    "DEDENT", 
                    newline_token.start, 
                    newline_token.stop, 
                    newline_token.line, 
                    newline_token.column
                )
                self.tokens.append(dedent_token)
            # Emit EOF
            self.tokens.append(next_token)
            return self.nextToken()
        
        # Handle empty lines - skip them and find the next non-empty line
        # We need to track the NEWLINE token that precedes the non-empty line
        last_newline = newline_token
        while next_token.type == NEWLINE:
            # This is an empty line - the NEWLINE token contains the indent of the next line
            # Calculate indent from this empty line's NEWLINE
            empty_indent = self._calculate_indent_from_newline_text(next_token)
            if empty_indent < 0:
                # Another empty line - skip it and continue
                last_newline = next_token
                next_token = self._peek_next_token()
                if next_token.type == Token.EOF:
                    break
                continue
            # Found non-empty line after empty line - use the empty line's NEWLINE to get indent
            indent_level = empty_indent
            # Get the actual next token (non-empty line)
            next_token = self._peek_next_token()
            if next_token.type == Token.EOF:
                break
            if next_token.type != NEWLINE:
                # Found non-empty line
                break
        
        # If we ended up at EOF after skipping empty lines
        if next_token.type == Token.EOF:
            self.eof_processed = True
            # Emit all pending DEDENTs
            while len(self.indent_stack) > 1:
                self.indent_stack.pop()
                dedent_token = self._create_token(
                    DEDENT, 
                    "DEDENT", 
                    newline_token.start, 
                    newline_token.stop, 
                    newline_token.line, 
                    newline_token.column
                )
                self.tokens.append(dedent_token)
            # Emit EOF
            self.tokens.append(next_token)
            return self.nextToken()
        
        # Now we have a non-empty line
        # Calculate indent level from next_token's column
        # In ANTLR, column is 0-indexed and represents the column of the first character of the token
        # After NEWLINE with [ \t]*, the next token's column should be the number of spaces/tabs
        if hasattr(next_token, 'column') and next_token.column is not None:
            indent_level = next_token.column
        else:
            # Fallback: try to calculate from the last NEWLINE token's text
            # This should work if we tracked the right NEWLINE
            indent_level = self._calculate_indent_from_newline_text(last_newline)
            if indent_level < 0:
                indent_level = 0
        
        current_indent = self.indent_stack[-1]
        
        if indent_level > current_indent:
            # Indentation increased - emit INDENT
            self.indent_stack.append(indent_level)
            indent_token = self._create_token(
                INDENT, 
                "INDENT", 
                newline_token.start, 
                newline_token.stop, 
                newline_token.line, 
                newline_token.column
            )
            # NEWLINE is NOT emitted - only INDENT
            self.tokens.append(indent_token)
            # Put next_token back in queue (it was peeked)
            self.tokens.append(next_token)
            return self.nextToken()
        elif indent_level < current_indent:
            # Indentation decreased - emit DEDENT(s)
            # NEWLINE is NOT emitted
            while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent_level:
                self.indent_stack.pop()
                dedent_token = self._create_token(
                    DEDENT, 
                    "DEDENT", 
                    newline_token.start, 
                    newline_token.stop, 
                    newline_token.line, 
                    newline_token.column
                )
                self.tokens.append(dedent_token)
            
            # Handle mismatched indentation (shouldn't happen, but handle gracefully)
            if len(self.indent_stack) > 1 and self.indent_stack[-1] != indent_level:
                # Reset to matching level
                while len(self.indent_stack) > 1 and self.indent_stack[-1] > indent_level:
                    self.indent_stack.pop()
            
            # Put next_token back in queue (it was peeked)
            self.tokens.append(next_token)
            return self.nextToken()
        else:
            # Same indentation - NEWLINE is NOT emitted
            # Just put next_token back in queue and continue
            self.tokens.append(next_token)
            return self.nextToken()

    def _calculate_indent_from_newline_text(self, newline_token):
        """Calculate indentation level from NEWLINE token's text
        
        NEWLINE token includes '\n' (or '\r\n') and following [ \t]*
        We extract the part after the last newline character and count spaces/tabs.
        
        Args:
            newline_token: The NEWLINE token
            
        Returns:
            int: Indentation level (number of spaces, tabs count as 4 spaces)
                 -1 if error
        """
        # Get the text of the NEWLINE token
        # In ANTLR, token.text gives the text of the token
        token_text = newline_token.text if hasattr(newline_token, 'text') and newline_token.text else None
        if not token_text:
            # Fallback: try to get text using getText() method
            if hasattr(newline_token, 'getText'):
                token_text = newline_token.getText()
            else:
                token_text = ""
        
        if not token_text:
            return -1
        
        # Find the last newline character in the token text
        # NEWLINE can be '\n', '\r\n', or '\r'
        last_newline_pos = -1
        for i in range(len(token_text) - 1, -1, -1):
            if token_text[i] == '\n':
                last_newline_pos = i
                break
            elif token_text[i] == '\r':
                # Check if it's part of '\r\n'
                if i + 1 < len(token_text) and token_text[i + 1] == '\n':
                    last_newline_pos = i + 1
                else:
                    last_newline_pos = i
                break
        
        if last_newline_pos == -1:
            # No newline found in token text - this shouldn't happen
            return -1
        
        # Extract the part after the last newline (this should be [ \t]*)
        indent_text = token_text[last_newline_pos + 1:]
        
        # Count spaces and tabs in indent_text
        indent_level = 0
        for char in indent_text:
            if char == ' ':
                indent_level += 1
            elif char == '\t':
                indent_level += 4  # Tabs = 4 spaces (Python default)
            elif char in ['\r', '\n']:
                # Another newline in the same token - shouldn't happen, but handle it
                return -1
        
        return indent_level

    def _peek_next_token(self):
        """Peek at the next token without consuming it"""
        # Get next token from parent lexer
        token = super().nextToken()
        # Skip WS and COMMENT tokens
        while token.type in [WS, COMMENT]:
            token = super().nextToken()
        return token

    def _create_token(self, token_type, text, start, stop, line, column):
        """Helper to create a token"""
        return self._factory.create(
            self._tokenFactorySourcePair,
            token_type,
            text,
            self._channel,
            start,
            stop,
            line,
            column
        )

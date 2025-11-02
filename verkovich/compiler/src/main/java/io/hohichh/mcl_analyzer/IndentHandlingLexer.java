package io.hohichh.mcl_analyzer;

import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.Pair;

import java.util.LinkedList;
import java.util.Queue;
import java.util.Stack;

public class IndentHandlingLexer extends MCLLexer {

    private final Queue<Token> pendingTokens = new LinkedList<>();
    private final Stack<Integer> indentStack = new Stack<>();

    private boolean atStartOfLine = true;
    private boolean eofProcessed = false;

    private static final int TAB_WIDTH = 4;

    public IndentHandlingLexer(CharStream input) {
        super(input);
        this.indentStack.push(0);
    }


    @Override
    public Token nextToken() {
        if (!pendingTokens.isEmpty()) {
            return pendingTokens.poll();
        }

        if (eofProcessed) {
            return super.nextToken();
        }

        Token next = super.nextToken();

        if (atStartOfLine) {
            atStartOfLine = false;
            int indentLength = 0;
            Token tokenToProcess;

            if (next.getType() == MCLLexer.WS) {
                indentLength = calculateIndent(next.getText());
                tokenToProcess = super.nextToken();
            } else {
                tokenToProcess = next;
            }


            if (tokenToProcess.getType() == MCLLexer.NL) {
                atStartOfLine = true;

                return tokenToProcess;
            }


            if (tokenToProcess.getType() == MCLLexer.EOF) {

                return handleEof(tokenToProcess);
            }


            int lastIndent = indentStack.peek();

            if (indentLength > lastIndent) {

                indentStack.push(indentLength);
                pendingTokens.offer(createToken(MCLLexer.INDENT, "<INDENT>"));

            } else if (indentLength < lastIndent) {

                while (indentLength < indentStack.peek()) {
                    indentStack.pop();
                    pendingTokens.offer(createToken(MCLLexer.DEDENT, "<DEDENT>"));
                }

                if (indentLength != indentStack.peek()) {
                    throw new RuntimeException(
                            String.format(
                                    "Invalid indentation: expected %d, but got %d at line %d",
                                    indentStack.peek(), indentLength, getLine()
                            )
                    );
                }
            }


            pendingTokens.offer(tokenToProcess);
            return pendingTokens.poll();
        }


        if (next.getType() == MCLLexer.NL) {
            atStartOfLine = true;
            return next;

        } else if (next.getType() == MCLLexer.EOF) {
            return handleEof(next);
        }

        return next;
    }


    private Token handleEof(Token eofToken) {
        eofProcessed = true;

        while (indentStack.peek() > 0) {
            indentStack.pop();
            pendingTokens.offer(createToken(MCLLexer.DEDENT, "<DEDENT>"));
        }

        pendingTokens.offer(eofToken);

        return pendingTokens.poll();
    }

    private int calculateIndent(String ws) {
        int count = 0;
        for (char c : ws.toCharArray()) {
            if (c == ' ') {
                count++;
            } else if (c == '\t') {
                count = count + TAB_WIDTH - (count % TAB_WIDTH);
            }
        }
        return count;
    }


    private Token createToken(int type, String text) {
        int start = _tokenStartCharIndex;
        int stop = start;
        return _factory.create(
                new Pair<>(this, _input),
                type,
                text,
                _channel,
                start,
                stop,
                _tokenStartLine,
                _tokenStartCharPositionInLine
        );
    }
}
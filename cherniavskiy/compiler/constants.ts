import Variant15Lexer from "./Variant15/Variant15Lexer";

export const EOF = Variant15Lexer.EOF;

// Create a mapping from ID to display name using the generated arrays
export const VOCABULARY = {};

// Literal names: keywords, operators with quotes like "'func'", "'+'"
// Symbolic names: ID names like "FUNC", "PLUS"
for (let i = 0; i < Variant15Lexer.literalNames.length; i++) {
    const lit = Variant15Lexer.literalNames[i];
    const sym = Variant15Lexer.symbolicNames[i];
    if (lit) {
        VOCABULARY[i] = lit;
    } else if (sym) {
        VOCABULARY[i] = sym;
    }
}

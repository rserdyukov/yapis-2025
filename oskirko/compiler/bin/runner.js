import { readFileSync } from 'fs';
import readlineSync from 'readline-sync';

const memory = new WebAssembly.Memory({ initial: 1 });
if (typeof globalThis.arrayPtr === 'undefined') globalThis.arrayPtr = 32000;

const importObject = {
    console: {
        logString: logString,
        logInteger: logInteger,
        logFloat: logFloat,
        inputFloat: inputFloat,
        inputInteger: inputInteger,
        newLine: newLine
    },
    array: {
        newArray: newArray,
        getFloat: getFloat,
        setFloat: setFloat,
        getInteger: getInteger,
        setInteger: setInteger
    },
    js: {
        mem: memory
    },
    math: {
        sin: sin,
        cos: cos,
        log: log,
        pow: pow
    }
};

function allocBytes(n) {
    const base = globalThis.arrayPtr;
    globalThis.arrayPtr += n;
    return base;
}

function logInteger(value) {
    process.stdout.write(value.toString());
}

function logFloat(value) {
    process.stdout.write(value.toString());
}

function logString(offset, length) {
    const bytes = new Uint8Array(memory.buffer, offset, length);
    const string = new TextDecoder("utf8").decode(bytes);
    process.stdout.write(string);
}

function newLine() {
    console.log();
}

function inputFloat(offset, length) {
    const bytes = new Uint8Array(memory.buffer, offset, length);
    const prompt = new TextDecoder("utf8").decode(bytes);
    const input = readlineSync.question(prompt);
    return parseFloat(input);
}

function inputInteger(offset, length) {
    const bytes = new Uint8Array(memory.buffer, offset, length);
    const prompt = new TextDecoder("utf8").decode(bytes);
    const input = readlineSync.question(prompt);
    return parseInt(input);
}

function newArray(cap) {
    const base = allocBytes(4 + cap * 4);
    const dv = new DataView(memory.buffer);
    dv.setInt32(base + 0, cap, true);
    return base | 0;
}

function setFloat(ptr, idx, val) {
    const dv = new DataView(memory.buffer);
    const cap = dv.getInt32(ptr + 0, true);
    if (idx < 0 || idx >= cap) throw new Error('Index out of bounds');
    dv.setInt32(ptr + 4 + idx * 4, val, true);
}

function setInteger(ptr, idx, val) {
    const dv = new DataView(memory.buffer);
    const cap = dv.getInt32(ptr + 0, true);
    if (idx < 0 || idx >= cap) throw new Error('Index out of bounds');
    dv.setInt32(ptr + 4 + idx * 4, val, true);
}

function getFloat(ptr, idx) {
    const dv = new DataView(memory.buffer);
    const cap = dv.getInt32(ptr + 0, true);
    if (idx < 0 || idx >= cap) throw new Error('Index out of bounds');
    return dv.getInt32(ptr + 4 + idx * 4, true);
}

function getInteger(ptr, idx) {
    const dv = new DataView(memory.buffer);
    const cap = dv.getInt32(ptr + 0, true);
    if (idx < 0 || idx >= cap) throw new Error('Index out of bounds');
    return dv.getInt32(ptr + 4 + idx * 4, true);
}

function log(base, x) {
    return Math.log(x) / Math.log(base);
}

function sin(degree) {
    return Math.sin(degree * Math.PI / 180);
}

function cos(degree) {
    return Math.cos(degree * Math.PI / 180);
}

function pow(base, x) {
    return Math.pow(base, x);
}

const wasmBuffer = readFileSync('../build/target.wasm');

WebAssembly.instantiate(wasmBuffer, importObject).then(wasmModule => {
    const { run } = wasmModule.instance.exports;
    run();
    console.log();
});
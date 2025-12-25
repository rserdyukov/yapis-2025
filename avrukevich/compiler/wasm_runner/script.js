const consoleDiv = document.getElementById('console');
const filenameInput = document.getElementById('filenameInput');
const runBtn = document.getElementById('runBtn');

let wasmMemory;
let wasmInstance;

function logToScreen(text, type = 'log') {
    const span = document.createElement('div');
    span.className = type;
    span.textContent = text;
    consoleDiv.appendChild(span);
    consoleDiv.scrollTop = consoleDiv.scrollHeight;
}

function clearConsole() {
    consoleDiv.innerHTML = '';
}

function readString(ptr) {
    if (!wasmMemory) return "";
    const buffer = new Uint8Array(wasmMemory.buffer);
    let end = ptr;
    while (buffer[end] !== 0) end++;
    return new TextDecoder("utf-8").decode(buffer.slice(ptr, end));
}

const getArrayMetadata = (ptr) => {
    if (!wasmMemory) return null;
    const view = new DataView(wasmMemory.buffer);
    const cap = view.getInt32(ptr, true);
    const len = view.getInt32(ptr + 4, true);
    return { cap, len, dataPtr: ptr + 8 };
};

const createWasmArray = (len, elementSize) => {
    if (!wasmInstance) throw new Error("WASM module not instantiated.");
    const bytes = 8 + len * elementSize;
    const ptr = wasmInstance.exports.malloc(bytes);
    const view = new DataView(wasmMemory.buffer);
    view.setInt32(ptr, len, true);
    view.setInt32(ptr + 4, len, true);
    return ptr;
};

const checkLengthMatch = (ptr1, ptr2) => {
    const meta1 = getArrayMetadata(ptr1);
    const meta2 = getArrayMetadata(ptr2);
    if (meta1.len !== meta2.len) {
        throw new Error(`Runtime Error: Array length mismatch for operation (${meta1.len} vs ${meta2.len}).`);
    }
    return meta1.len;
};

const importObject = {
    js: {
        'Math.pow': Math.pow,
        'Math.sin': Math.sin,
        'Math.cos': Math.cos,
        'Math.tan': Math.tan,
        'Math.asin': Math.asin,
        'Math.acos': Math.acos,
        'Math.atan': Math.atan,
        'Math.log': Math.log,
        'Math.log10': Math.log10
    },
    env: {
        print_str: (ptr) => logToScreen(readString(ptr)),
        print_i32: (val) => logToScreen(val.toString()),
        print_f64: (val) => logToScreen(val.toString()),
        
        input: () => {
            const result = prompt("MathPL Input Required:") || "";
            logToScreen(`> ${result}`, 'input');
            const bytes = new TextEncoder("utf-8").encode(result);
            const ptr = wasmInstance.exports.malloc(bytes.length + 1);
            const buffer = new Uint8Array(wasmMemory.buffer);
            buffer.set(bytes, ptr);
            buffer[ptr + bytes.length] = 0;
            return ptr;
        },

        i32_to_str: (val) => {
            const str = val.toString();
            const bytes = new TextEncoder("utf-8").encode(str);
            const ptr = wasmInstance.exports.malloc(bytes.length + 1);
            const buffer = new Uint8Array(wasmMemory.buffer);
            buffer.set(bytes, ptr);
            buffer[ptr + bytes.length] = 0;
            return ptr;
        },
        bool_to_str: (val) => {
            const str = val !== 0 ? "true" : "false";
            const bytes = new TextEncoder("utf-8").encode(str);
            const ptr = wasmInstance.exports.malloc(bytes.length + 1);
            const buffer = new Uint8Array(wasmMemory.buffer);
            buffer.set(bytes, ptr);
            buffer[ptr + bytes.length] = 0;
            return ptr;
        },
        f64_to_str: (val) => {
            const str = val.toString();
            const bytes = new TextEncoder("utf-8").encode(str);
            const ptr = wasmInstance.exports.malloc(bytes.length + 1);
            const buffer = new Uint8Array(wasmMemory.buffer);
            buffer.set(bytes, ptr);
            buffer[ptr + bytes.length] = 0;
            return ptr;
        },
        
        str_to_int: (ptr) => parseInt(readString(ptr), 10) || 0,
        str_to_float: (ptr) => parseFloat(readString(ptr)) || 0.0,
        
        concat: (ptr1, ptr2) => {
            const str = readString(ptr1) + readString(ptr2);
            const bytes = new TextEncoder("utf-8").encode(str);
            const ptr = wasmInstance.exports.malloc(bytes.length + 1);
            const buffer = new Uint8Array(wasmMemory.buffer);
            buffer.set(bytes, ptr);
            buffer[ptr + bytes.length] = 0;
            return ptr;
        },
        
        arr_gt: (ptr1, ptr2) => getArrayMetadata(ptr1).len > getArrayMetadata(ptr2).len ? 1 : 0,
        arr_gte: (ptr1, ptr2) => getArrayMetadata(ptr1).len >= getArrayMetadata(ptr2).len ? 1 : 0,
        arr_lt: (ptr1, ptr2) => getArrayMetadata(ptr1).len < getArrayMetadata(ptr2).len ? 1 : 0,
        arr_lte: (ptr1, ptr2) => getArrayMetadata(ptr1).len <= getArrayMetadata(ptr2).len ? 1 : 0,
        
        arr_add_i32: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const newPtr = createWasmArray(len, 4);
            const src1 = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src2 = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            const dest = new Int32Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src1[i] + src2[i];
            return newPtr;
        },
        arr_sub_i32: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const newPtr = createWasmArray(len, 4);
            const src1 = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src2 = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            const dest = new Int32Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src1[i] - src2[i];
            return newPtr;
        },
        arr_mul_i32: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const newPtr = createWasmArray(len, 4);
            const src1 = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src2 = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            const dest = new Int32Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src1[i] * src2[i];
            return newPtr;
        },
        arr_div_i32: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const newPtr = createWasmArray(len, 4);
            const src1 = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src2 = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            const dest = new Int32Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = Math.trunc(src1[i] / src2[i]);
            return newPtr;
        },
        arr_add_f64: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const newPtr = createWasmArray(len, 8);
            const src1 = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src2 = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            const dest = new Float64Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src1[i] + src2[i];
            return newPtr;
        },
        arr_sub_f64: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const newPtr = createWasmArray(len, 8);
            const src1 = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src2 = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            const dest = new Float64Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src1[i] - src2[i];
            return newPtr;
        },
        arr_mul_f64: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const newPtr = createWasmArray(len, 8);
            const src1 = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src2 = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            const dest = new Float64Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src1[i] * src2[i];
            return newPtr;
        },
        arr_div_f64: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const newPtr = createWasmArray(len, 8);
            const src1 = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src2 = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            const dest = new Float64Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src1[i] / src2[i];
            return newPtr;
        },

        arr_add_scalar_i32: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const newPtr = createWasmArray(len, 4);
            const src = new Int32Array(wasmMemory.buffer, dataPtr, len);
            const dest = new Int32Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src[i] + val;
            return newPtr;
        },
        arr_sub_scalar_i32: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const newPtr = createWasmArray(len, 4);
            const src = new Int32Array(wasmMemory.buffer, dataPtr, len);
            const dest = new Int32Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src[i] - val;
            return newPtr;
        },
        arr_mul_scalar_i32: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const newPtr = createWasmArray(len, 4);
            const src = new Int32Array(wasmMemory.buffer, dataPtr, len);
            const dest = new Int32Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src[i] * val;
            return newPtr;
        },
        arr_div_scalar_i32: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const newPtr = createWasmArray(len, 4);
            const src = new Int32Array(wasmMemory.buffer, dataPtr, len);
            const dest = new Int32Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = Math.trunc(src[i] / val);
            return newPtr;
        },
        arr_add_scalar_f64: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const newPtr = createWasmArray(len, 8);
            const src = new Float64Array(wasmMemory.buffer, dataPtr, len);
            const dest = new Float64Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src[i] + val;
            return newPtr;
        },
        arr_sub_scalar_f64: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const newPtr = createWasmArray(len, 8);
            const src = new Float64Array(wasmMemory.buffer, dataPtr, len);
            const dest = new Float64Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src[i] - val;
            return newPtr;
        },
        arr_mul_scalar_f64: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const newPtr = createWasmArray(len, 8);
            const src = new Float64Array(wasmMemory.buffer, dataPtr, len);
            const dest = new Float64Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src[i] * val;
            return newPtr;
        },
        arr_div_scalar_f64: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const newPtr = createWasmArray(len, 8);
            const src = new Float64Array(wasmMemory.buffer, dataPtr, len);
            const dest = new Float64Array(wasmMemory.buffer, getArrayMetadata(newPtr).dataPtr, len);
            for (let i = 0; i < len; i++) dest[i] = src[i] / val;
            return newPtr;
        },

        arr_add_assign_i32: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const target = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            for (let i = 0; i < len; i++) target[i] += src[i];
        },
        arr_sub_assign_i32: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const target = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            for (let i = 0; i < len; i++) target[i] -= src[i];
        },
        arr_mul_assign_i32: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const target = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            for (let i = 0; i < len; i++) target[i] *= src[i];
        },
        arr_div_assign_i32: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const target = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src = new Int32Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            for (let i = 0; i < len; i++) target[i] = Math.trunc(target[i] / src[i]);
        },
        arr_add_assign_f64: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const target = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            for (let i = 0; i < len; i++) target[i] += src[i];
        },
        arr_sub_assign_f64: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const target = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            for (let i = 0; i < len; i++) target[i] -= src[i];
        },
        arr_mul_assign_f64: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const target = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            for (let i = 0; i < len; i++) target[i] *= src[i];
        },
        arr_div_assign_f64: (ptr1, ptr2) => {
            const len = checkLengthMatch(ptr1, ptr2);
            const target = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr1).dataPtr, len);
            const src = new Float64Array(wasmMemory.buffer, getArrayMetadata(ptr2).dataPtr, len);
            for (let i = 0; i < len; i++) target[i] /= src[i];
        },
        
        arr_add_assign_scalar_i32: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const target = new Int32Array(wasmMemory.buffer, dataPtr, len);
            for (let i = 0; i < len; i++) target[i] += val;
        },
        arr_sub_assign_scalar_i32: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const target = new Int32Array(wasmMemory.buffer, dataPtr, len);
            for (let i = 0; i < len; i++) target[i] -= val;
        },
        arr_mul_assign_scalar_i32: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const target = new Int32Array(wasmMemory.buffer, dataPtr, len);
            for (let i = 0; i < len; i++) target[i] *= val;
        },
        arr_div_assign_scalar_i32: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const target = new Int32Array(wasmMemory.buffer, dataPtr, len);
            for (let i = 0; i < len; i++) target[i] = Math.trunc(target[i] / val);
        },
        arr_add_assign_scalar_f64: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const target = new Float64Array(wasmMemory.buffer, dataPtr, len);
            for (let i = 0; i < len; i++) target[i] += val;
        },
        arr_sub_assign_scalar_f64: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const target = new Float64Array(wasmMemory.buffer, dataPtr, len);
            for (let i = 0; i < len; i++) target[i] -= val;
        },
        arr_mul_assign_scalar_f64: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const target = new Float64Array(wasmMemory.buffer, dataPtr, len);
            for (let i = 0; i < len; i++) target[i] *= val;
        },
        arr_div_assign_scalar_f64: (ptr, val) => {
            const { len, dataPtr } = getArrayMetadata(ptr);
            const target = new Float64Array(wasmMemory.buffer, dataPtr, len);
            for (let i = 0; i < len; i++) target[i] /= val;
        },
    }
};

async function runWasm() {
    clearConsole();
    const fileName = filenameInput.value;
    
    const filePath = `../out/${fileName}`;
    
    logToScreen(`Loading: ${filePath}...`, 'system');

    try {
        const response = await fetch(filePath);
        
        if (!response.ok) {
            throw new Error(`File not found: ${filePath} (Status: ${response.status})`);
        }
        
        const bytes = await response.arrayBuffer();
        
        const results = await WebAssembly.instantiate(bytes, importObject);
        
        wasmInstance = results.instance;
        wasmMemory = wasmInstance.exports.memory;
        
        logToScreen("--- Program Start ---", 'system');
        
        if (wasmInstance.exports._start) {
            wasmInstance.exports._start();
        } else {
            logToScreen("Error: _start function not found in WASM exports.", 'error');
        }
        
        logToScreen("--- Program End ---", 'system');

    } catch (e) {
        logToScreen(`[Execution Error]: ${e.message}`, 'error');
        console.error(e);
    }
}

runBtn.addEventListener('click', runWasm);

filenameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') runWasm();
});
const consoleDiv = document.getElementById('console');
const filenameInput = document.getElementById('filenameInput');
const runBtn = document.getElementById('runBtn');

let wasmMemory;
// Указатель на начало кучи (после статических данных). 
// В идеале должен экспортироваться из WASM как __heap_base, но пока хардкодим с запасом.
const INITIAL_HEAP_POINTER = 65536; 
let heapPointer = INITIAL_HEAP_POINTER;

function logToScreen(text, type = 'log') {
    const span = document.createElement('div'); // Используем div для блочности
    span.className = type;
    span.textContent = text;
    consoleDiv.appendChild(span);
    consoleDiv.scrollTop = consoleDiv.scrollHeight; // Автоскролл вниз
}

function clearConsole() {
    consoleDiv.innerHTML = '';
}

// Чтение строки из памяти WASM (UTF-8)
function readString(ptr) {
    const buffer = new Uint8Array(wasmMemory.buffer);
    let end = ptr;
    while (buffer[end] !== 0) end++;
    return new TextDecoder("utf-8").decode(buffer.slice(ptr, end));
}

// Запись строки в память WASM
function writeString(str) {
    const bytes = new TextEncoder("utf-8").encode(str);
    const ptr = heapPointer;
    
    const requiredSize = ptr + bytes.length + 1;
    const currentSize = wasmMemory.buffer.byteLength;
    
    // Если места не хватает, запрашиваем у браузера больше памяти
    if (requiredSize > currentSize) {
        const missingBytes = requiredSize - currentSize;
        const pagesToGrow = Math.ceil(missingBytes / 65536);
        try {
            wasmMemory.grow(pagesToGrow);
            logToScreen(`[System]: Memory grew by ${pagesToGrow} pages`, 'system');
        } catch (e) {
            logToScreen(`[Error]: Out of memory trying to grow!`, 'error');
            return 0;
        }
    }

    const buffer = new Uint8Array(wasmMemory.buffer);
    buffer.set(bytes, ptr);
    buffer[ptr + bytes.length] = 0; // Null-terminator
    
    heapPointer += bytes.length + 1;
    return ptr;
}

// Импортируемые функции для WASM модуля
const importObject = {
    js: {
        'Math.pow': Math.pow,
        'Math.sin': Math.sin,
        'Math.cos': Math.cos,
        'Math.tan': Math.tan,
        'Math.asin': Math.asin,
        'Math.acos': Math.acos,
        'Math.atan': Math.atan,
        'Math.log': Math.log,   // ln
        'Math.log10': Math.log10
    },
    env: {
        print_str: (ptr) => {
            const str = readString(ptr);
            logToScreen(str);
        },
        print_i32: (val) => logToScreen(val.toString()),
        print_f64: (val) => logToScreen(val.toString()),
        
        input: () => {
            const result = prompt("MathPL Input Required:");
            const val = result || "";
            logToScreen(`> ${val}`, 'input');
            return writeString(val);
        },

        i32_to_str: (val) => writeString(val.toString()),
        bool_to_str: (val) => writeString(val !== 0 ? "true" : "false"),
        f64_to_str: (val) => writeString(val.toString()),
        
        str_to_int: (ptr) => {
            const str = readString(ptr);
            return parseInt(str, 10) || 0;
        },
        str_to_float: (ptr) => {
            const str = readString(ptr);
            return parseFloat(str) || 0.0;
        },
        concat: (ptr1, ptr2) => {
            const str1 = readString(ptr1);
            const str2 = readString(ptr2);
            return writeString(str1 + str2);
        }
    }
};

async function runWasm() {
    clearConsole();
    const fileName = filenameInput.value;
    
    // Формируем путь: поднимаемся на уровень выше и заходим в out
    const filePath = `../out/${fileName}`;
    
    logToScreen(`Loading: ${filePath}...`, 'system');

    try {
        const response = await fetch(filePath);
        
        if (!response.ok) {
            throw new Error(`File not found: ${filePath} (Status: ${response.status})`);
        }
        
        const bytes = await response.arrayBuffer();
        
        // Сбрасываем указатель кучи перед новым запуском
        heapPointer = INITIAL_HEAP_POINTER;
        
        const results = await WebAssembly.instantiate(bytes, importObject);
        
        wasmMemory = results.instance.exports.memory;
        
        logToScreen("--- Program Start ---", 'system');
        
        if (results.instance.exports._start) {
            results.instance.exports._start();
        } else {
            logToScreen("Error: _start function not found in WASM exports.", 'error');
        }
        
        logToScreen("--- Program End ---", 'system');

    } catch (e) {
        logToScreen(`[Execution Error]: ${e.message}`, 'error');
        console.error(e);
    }
}

// Обработчики событий
runBtn.addEventListener('click', runWasm);

filenameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') runWasm();
});

// Автозапуск первого примера при загрузке (опционально)
// runWasm();
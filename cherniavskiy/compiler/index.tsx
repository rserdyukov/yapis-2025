import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import {
    Code,
    Play,
    BookOpen,
    CheckCircle,
    Copy,
    AlertTriangle,
    ShieldAlert,
    Cpu,
    Download,
} from "lucide-react";
import {
    CharStream,
    CommonTokenStream,
    ErrorListener,
    ParseTreeWalker,
} from "antlr4";
import MyGrammarLexer from "./Variant15/Variant15Lexer";
import MyGrammarParser from "./Variant15/Variant15Parser";
import { EXAMPLES, ANTLR_GRAMMAR } from "./examples";
import { VOCABULARY, EOF } from "./constants";
import { SemanticListener } from "./semantic";
import { JvmCompiler } from "./compiler";
import { LineNumberedTextarea } from "./LineNumberedTextarea";

class CustomErrorListener extends ErrorListener<any> {
    errors: string[] = [];
    syntaxError(
        recognizer: any,
        offendingSymbol: any,
        line: number,
        column: number,
        msg: string,
        e: any
    ) {
        this.errors.push(`Line ${line}:${column} - ${msg}`);
    }
}

const App = () => {
    const [activeTab, setActiveTab] = useState<"grammar" | "test" | "compiler">(
        "grammar"
    );
    const [code, setCode] = useState(EXAMPLES.example1);
    const [tokens, setTokens] = useState<any[]>([]);
    const [syntaxErrors, setSyntaxErrors] = useState<string[]>([]);
    const [semanticErrors, setSemanticErrors] = useState<string[]>([]);
    const [compiledCode, setCompiledCode] = useState<string>("");
    const [selectedExample, setSelectedExample] = useState<string>("example1");

    const handleExampleChange = (key: string) => {
        setSelectedExample(key);
        setCode(EXAMPLES[key as keyof typeof EXAMPLES]);
    };

    useEffect(() => {
        try {
            const chars = new CharStream(code);
            const lexer = new MyGrammarLexer(chars);
            const tokens = new CommonTokenStream(lexer);
            const parser = new MyGrammarParser(tokens);

            const lexerErrorListener = new CustomErrorListener();
            lexer.removeErrorListeners();
            lexer.addErrorListener(lexerErrorListener);

            tokens.fill();
            const allTokens = tokens.tokens || [];
            setTokens(allTokens.filter((t) => t.type !== EOF));

            (tokens as any).seek(0);

            const parserErrorListener = new CustomErrorListener();
            parser.removeErrorListeners();
            parser.addErrorListener(parserErrorListener);

            const tree = parser.program();

            const semanticListener = new SemanticListener();
            const walker = new ParseTreeWalker();
            walker.walk(semanticListener, tree);

            const compiler = new JvmCompiler();
            if (
                lexerErrorListener.errors.length === 0 &&
                parserErrorListener.errors.length === 0
            ) {
                walker.walk(compiler, tree);
                setCompiledCode(compiler.getGeneratedCode());
            } else {
                setCompiledCode(
                    "; Исправьте синтаксические ошибки для генерации кода"
                );
            }

            setSyntaxErrors([
                ...lexerErrorListener.errors,
                ...parserErrorListener.errors,
            ]);
            setSemanticErrors(semanticListener.analyzer.errors);
        } catch (e) {
            console.error("Parsing error:", e);
            setSyntaxErrors((prev) => [
                ...prev,
                `Critical Error: ${(e as any).message}`,
            ]);
        }
    }, [code]);

    const copyGrammar = () => {
        navigator.clipboard.writeText(ANTLR_GRAMMAR);
        alert("Грамматика скопирована в буфер обмена!");
    };

    const copyBytecode = () => {
        navigator.clipboard.writeText(compiledCode);
        alert("Jasmin код скопирован!");
    };

    const downloadJasminFile = () => {
        try {
            const blob = new Blob([compiledCode], { type: "text/plain" });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "Program.j";
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (e) {
            alert("Ошибка при создании файла: " + e);
        }
    };

    const hasErrors = syntaxErrors.length > 0 || semanticErrors.length > 0;

    return (
        <div className="flex flex-col h-full bg-slate-900 text-slate-100 font-sans">
            {/* Header */}
            <header className="flex items-center justify-between px-6 py-4 bg-slate-800 border-b border-slate-700 shadow-sm">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-indigo-600 rounded-lg">
                        <BookOpen size={24} className="text-white" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white">
                            Лабораторная работа №3
                        </h1>
                        <p className="text-xs text-slate-400">
                            Синтаксический и семантический анализ (ANTLR4) и
                            Компиляция
                        </p>
                    </div>
                </div>
                <div className="flex bg-slate-700 rounded-lg p-1">
                    <button
                        onClick={() => setActiveTab("grammar")}
                        className={`px-4 py-1.5 text-sm rounded-md transition-all ${
                            activeTab === "grammar"
                                ? "bg-slate-500 text-white shadow"
                                : "text-slate-400 hover:text-white"
                        }`}
                    >
                        1. Грамматика
                    </button>
                    <button
                        onClick={() => setActiveTab("test")}
                        className={`px-4 py-1.5 text-sm rounded-md transition-all ${
                            activeTab === "test"
                                ? "bg-indigo-500 text-white shadow"
                                : "text-slate-400 hover:text-white"
                        }`}
                    >
                        2. Тестирование
                    </button>
                    <button
                        onClick={() => setActiveTab("compiler")}
                        className={`px-4 py-1.5 text-sm rounded-md transition-all ${
                            activeTab === "compiler"
                                ? "bg-green-600 text-white shadow"
                                : "text-slate-400 hover:text-white"
                        }`}
                    >
                        3. Компиляция (Jasmin)
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex flex-1 overflow-hidden">
                {activeTab === "grammar" ? (
                    <div className="w-full h-full flex flex-col relative">
                        <div className="px-6 py-3 bg-slate-800/50 border-b border-slate-700 flex justify-between items-center">
                            <span className="text-sm font-semibold text-green-400 font-mono">
                                Variant15.g4
                            </span>
                            <div className="flex items-center gap-4">
                                <span className="text-xs text-slate-500">
                                    Файл описания грамматики
                                </span>
                                <button
                                    onClick={copyGrammar}
                                    className="flex items-center gap-2 px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-medium shadow transition-colors"
                                >
                                    <Copy size={14} /> Копировать
                                </button>
                            </div>
                        </div>
                        <textarea
                            className="flex-1 w-full bg-[#1e1e1e] text-slate-300 font-mono text-sm leading-relaxed p-6 resize-none focus:outline-none custom-scrollbar"
                            value={ANTLR_GRAMMAR}
                            readOnly
                            spellCheck={false}
                        />
                    </div>
                ) : activeTab === "test" ? (
                    <>
                        {/* Editor Panel */}
                        <div className="w-1/2 flex flex-col border-r border-slate-700">
                            <div className="px-4 py-2 bg-slate-800/50 flex items-center justify-between border-b border-slate-700">
                                <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                    <Code size={14} /> Тестовый пример
                                </div>
                                <select
                                    className="bg-slate-900 border border-slate-600 text-xs rounded px-2 py-1 text-slate-300 focus:ring-1 focus:ring-indigo-500 outline-none"
                                    value={selectedExample}
                                    onChange={(e) =>
                                        handleExampleChange(e.target.value)
                                    }
                                >
                                    <option value="example1">
                                        Пример 1: Строки и Руны
                                    </option>
                                    <option value="example2">
                                        Пример 2: Switch/Contains
                                    </option>
                                    <option value="example3">
                                        Пример 3: Split
                                    </option>
                                    <option disabled>
                                        --- Синтаксические ошибки ---
                                    </option>
                                    <option value="errorExample1">
                                        Ошибка 1: Скобка
                                    </option>
                                    <option value="errorExample2">
                                        Ошибка 2: Цикл For
                                    </option>
                                    <option value="errorExample3">
                                        Ошибка 3: Переменные
                                    </option>
                                    <option disabled>
                                        --- Семантические ошибки ---
                                    </option>
                                    <option value="semanticError1">
                                        Сем. Ошибка 1: Повтор перем.
                                    </option>
                                    <option value="semanticError2">
                                        Сем. Ошибка 2: Необъяв. перем.
                                    </option>
                                    <option value="semanticError3">
                                        Сем. Ошибка 3: Конфликт функций
                                    </option>
                                    <option value="semanticError4">
                                        Сем. Ошибка 4: Кол-во операндов
                                    </option>
                                    <option value="semanticError5">
                                        Сем. Ошибка 5: Main функция
                                    </option>
                                    <option value="semanticError6">
                                        Сем. Ошибка 6: Вложенность функц.
                                    </option>
                                </select>
                            </div>
                            <LineNumberedTextarea
                                value={code}
                                onChange={(e) => setCode(e.target.value)}
                                className="flex-1 bg-slate-900"
                                placeholder="Введите код здесь..."
                            />
                            {/* Errors Panel */}
                            <div className="flex flex-col max-h-60 border-t border-slate-700">
                                {hasErrors ? (
                                    <div className="bg-slate-900/50 p-0 overflow-y-auto">
                                        {syntaxErrors.length > 0 && (
                                            <div className="p-3 bg-orange-900/20 border-b border-orange-900/30">
                                                <div className="flex items-center gap-2 text-orange-400 font-semibold mb-2 text-sm">
                                                    <AlertTriangle size={14} />{" "}
                                                    Синтаксические ошибки
                                                </div>
                                                <ul className="list-disc list-inside text-xs text-orange-300/80 space-y-1 font-mono">
                                                    {syntaxErrors.map(
                                                        (err, idx) => (
                                                            <li key={idx}>
                                                                {err}
                                                            </li>
                                                        )
                                                    )}
                                                </ul>
                                            </div>
                                        )}
                                        {semanticErrors.length > 0 && (
                                            <div className="p-3 bg-red-900/20">
                                                <div className="flex items-center gap-2 text-red-400 font-semibold mb-2 text-sm">
                                                    <ShieldAlert size={14} />{" "}
                                                    Семантические ошибки
                                                </div>
                                                <ul className="list-disc list-inside text-xs text-red-300/80 space-y-1 font-mono">
                                                    {semanticErrors.map(
                                                        (err, idx) => (
                                                            <li key={idx}>
                                                                {err}
                                                            </li>
                                                        )
                                                    )}
                                                </ul>
                                            </div>
                                        )}
                                    </div>
                                ) : (
                                    <div className="bg-green-900/10 p-2 flex items-center justify-center gap-2 text-green-400 text-xs border-t border-green-900/20">
                                        <CheckCircle size={14} /> Анализ успешен
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Output Panel */}
                        <div className="w-1/2 flex flex-col bg-slate-900">
                            <div className="px-4 py-2 bg-slate-800/50 text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between border-b border-slate-700">
                                <div className="flex items-center gap-2">
                                    <Play size={14} /> Токены ANTLR
                                </div>
                                <span className="bg-slate-700 px-2 py-0.5 rounded-full text-white">
                                    {tokens.length}
                                </span>
                            </div>

                            <div className="flex-1 overflow-y-auto p-0 custom-scrollbar">
                                <table className="w-full text-left border-collapse">
                                    <thead className="bg-slate-800/80 sticky top-0 backdrop-blur-sm shadow-sm z-10">
                                        <tr>
                                            <th className="px-4 py-3 text-xs font-medium text-slate-400 w-16">
                                                ID
                                            </th>
                                            <th className="px-4 py-3 text-xs font-medium text-slate-400 w-24">
                                                Column
                                            </th>
                                            <th className="px-4 py-3 text-xs font-medium text-slate-400">
                                                Type
                                            </th>
                                            <th className="px-4 py-3 text-xs font-medium text-slate-400">
                                                Text
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-800">
                                        {tokens.map((token, index) => {
                                            if (!token) return null;
                                            return (
                                                <tr
                                                    key={index}
                                                    className="hover:bg-slate-800/30 transition-colors group"
                                                >
                                                    <td className="px-4 py-2 text-xs text-slate-500 font-mono">
                                                        {token.type}
                                                    </td>
                                                    <td className="px-4 py-2 text-xs text-slate-500 font-mono">
                                                        {token.column}
                                                    </td>
                                                    <td className="px-4 py-2 text-xs font-mono">
                                                        <span className="text-indigo-400">
                                                            {VOCABULARY[
                                                                token.type
                                                            ] || "UNK"}
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-2 text-sm font-mono text-slate-200 break-all">
                                                        {token.text}
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </>
                ) : (
                    // Compiler Tab
                    <>
                        <div className="w-1/2 flex flex-col border-r border-slate-700">
                            <div className="px-4 py-2 bg-slate-800/50 flex items-center justify-between border-b border-slate-700">
                                <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                    <Code size={14} /> Исходный код
                                </div>
                                <select
                                    className="bg-slate-900 border border-slate-600 text-xs rounded px-2 py-1 text-slate-300 focus:ring-1 focus:ring-green-500 outline-none"
                                    value={selectedExample}
                                    onChange={(e) =>
                                        handleExampleChange(e.target.value)
                                    }
                                >
                                    <option value="example1">
                                        Пример 1: Строки и Руны
                                    </option>
                                    <option value="example2">
                                        Пример 2: Switch/Contains
                                    </option>
                                    <option value="example3">
                                        Пример 3: Split
                                    </option>
                                    <option value="errorExample1">
                                        Ошибка 1: Скобка
                                    </option>
                                    <option value="errorExample2">
                                        Ошибка 2: Цикл For
                                    </option>
                                    <option value="errorExample3">
                                        Ошибка 3: Переменные
                                    </option>
                                </select>
                            </div>
                            <LineNumberedTextarea
                                value={code}
                                onChange={(e) => setCode(e.target.value)}
                                className="flex-1 bg-slate-900"
                                placeholder="Введите код здесь..."
                            />
                        </div>
                        <div className="w-1/2 flex flex-col bg-[#1e1e1e]">
                            <div className="px-4 py-2 bg-slate-800/50 flex items-center justify-between border-b border-slate-700">
                                <div className="flex items-center gap-2 text-xs font-semibold text-green-400 uppercase tracking-wider">
                                    <Cpu size={14} /> Jasmin Assembly (.j)
                                </div>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={copyBytecode}
                                        className="flex items-center gap-2 px-3 py-1 bg-slate-700 hover:bg-slate-600 text-white rounded text-xs font-medium transition-colors"
                                    >
                                        <Copy size={14} /> Копировать
                                    </button>
                                    <button
                                        onClick={downloadJasminFile}
                                        className="flex items-center gap-2 px-3 py-1 bg-green-700 hover:bg-green-600 text-white rounded text-xs font-medium transition-colors"
                                        title="Скачать Program.j для сборки Jasmin"
                                    >
                                        <Download size={14} /> Скачать .j
                                    </button>
                                </div>
                            </div>
                            <div className="p-3 bg-slate-800 text-xs text-slate-300 border-b border-slate-700 leading-relaxed">
                                <p className="font-semibold text-orange-300 mb-1">
                                    Инструкция:
                                </p>
                                <ul className="list-disc list-inside space-y-1">
                                    <li>
                                        Файл скачивается как{" "}
                                        <span className="font-mono bg-slate-900 px-1 rounded text-white">
                                            Program.j
                                        </span>
                                        .
                                    </li>
                                    <li>
                                        Для компиляции нужен <b>jasmin.jar</b>.
                                    </li>
                                    <li>
                                        Команда:{" "}
                                        <span className="font-mono bg-slate-900 px-1 rounded text-green-400">
                                            java -jar jasmin.jar Program.j
                                        </span>
                                    </li>
                                    <li>
                                        Запуск:{" "}
                                        <span className="font-mono bg-slate-900 px-1 rounded text-green-400">
                                            java Program
                                        </span>
                                    </li>
                                </ul>
                            </div>
                            <textarea
                                value={compiledCode}
                                readOnly
                                className="flex-1 p-4 bg-[#1e1e1e] text-green-300 font-mono text-sm leading-6 resize-none focus:outline-none custom-scrollbar"
                                spellCheck={false}
                            />
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

const root = createRoot(document.getElementById("root")!);
root.render(<App />);

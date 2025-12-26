import React, { useRef } from "react";

export const LineNumberedTextarea = ({
    value,
    onChange,
    readOnly = false,
    className = "",
    placeholder = "",
    textColor = "text-slate-300",
}: {
    value: string;
    onChange?: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    readOnly?: boolean;
    className?: string;
    placeholder?: string;
    textColor?: string;
}) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const lineNumbersRef = useRef<HTMLDivElement>(null);

    const handleScroll = () => {
        if (lineNumbersRef.current && textareaRef.current) {
            lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop;
        }
    };

    const lineCount = value.split("\n").length;
    const lines = Array.from({ length: lineCount }, (_, i) => i + 1);

    return (
        <div
            className={`flex flex-1 relative overflow-hidden font-mono text-sm ${className}`}
        >
            <div
                ref={lineNumbersRef}
                className="bg-slate-950/30 border-r border-slate-700/50 text-slate-600 text-right select-none py-4 pr-3 pl-2 overflow-hidden w-12 flex-shrink-0"
                style={{ lineHeight: "1.5rem" }}
            >
                {lines.map((line) => (
                    <div key={line} className="h-6">
                        {line}
                    </div>
                ))}
            </div>
            <textarea
                ref={textareaRef}
                value={value}
                onChange={onChange}
                readOnly={readOnly}
                onScroll={handleScroll}
                className={`flex-1 p-4 bg-transparent resize-none focus:outline-none leading-6 custom-scrollbar whitespace-pre ${textColor}`}
                spellCheck={false}
                placeholder={placeholder}
            />
        </div>
    );
};

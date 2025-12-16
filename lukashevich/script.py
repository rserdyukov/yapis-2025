import subprocess

examples = [
    r".\examples\1.txt",
    r".\examples\2.txt",
    r".\examples\3.txt",
    r".\examples\error-1.txt",
    r".\examples\error-2.txt",
    r".\examples\error-3.txt",
    r".\examples\semantic-error-1.txt",
    r".\examples\semantic-error-2.txt",
    r".\examples\semantic-error-3.txt",
    r".\examples\semantic-error-4.txt",
    r".\examples\semantic-error-5.txt",
    r".\examples\semantic-error-6.txt",
]

for example in examples:
    print(f"Выполняется: python .\\compiler\\main.py {example}")
    result = subprocess.run(
        ["python", r".\compiler\main.py", example], capture_output=True, text=True
    )
    print("Вывод программы:")
    print(result.stdout)
    if result.stderr:
        print("Ошибки:")
        print(result.stderr)
    print("---")

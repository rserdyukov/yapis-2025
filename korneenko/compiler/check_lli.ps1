# Скрипт для проверки наличия lli и добавления в PATH

Write-Host "Проверка наличия LLVM инструментов..." -ForegroundColor Cyan

$llvmPaths = @(
    "C:\Program Files\LLVM\bin",
    "C:\Program Files (x86)\LLVM\bin"
)

$foundLli = $false
$foundClang = $false

foreach ($path in $llvmPaths) {
    if (Test-Path $path) {
        Write-Host "`nПроверка: $path" -ForegroundColor Yellow
        
        $lliPath = Join-Path $path "lli.exe"
        $clangPath = Join-Path $path "clang.exe"
        
        if (Test-Path $lliPath) {
            Write-Host "  [OK] lli.exe найден!" -ForegroundColor Green
            Write-Host "  Путь: $lliPath" -ForegroundColor Gray
            $foundLli = $true
            
            # Проверяем, есть ли в PATH
            $inPath = $env:Path -split ';' | Where-Object { $_ -eq $path }
            if (-not $inPath) {
                Write-Host "  [WARNING] Путь не в PATH!" -ForegroundColor Yellow
                Write-Host "  Добавить в PATH? (Y/N): " -NoNewline
                $response = Read-Host
                if ($response -eq 'Y' -or $response -eq 'y') {
                    [Environment]::SetEnvironmentVariable("Path", $env:Path + ";$path", "User")
                    Write-Host "  [OK] Путь добавлен в PATH (требуется перезапуск терминала)" -ForegroundColor Green
                }
            } else {
                Write-Host "  [OK] Путь уже в PATH" -ForegroundColor Green
            }
        } else {
            Write-Host "  [NOT FOUND] lli.exe не найден" -ForegroundColor Red
        }
        
        if (Test-Path $clangPath) {
            Write-Host "  [OK] clang.exe найден!" -ForegroundColor Green
            $foundClang = $true
        } else {
            Write-Host "  [NOT FOUND] clang.exe не найден" -ForegroundColor Red
        }
    }
}

Write-Host "`n=== Итоги ===" -ForegroundColor Cyan
if ($foundLli) {
    Write-Host "[OK] lli найден" -ForegroundColor Green
} else {
    Write-Host "[NOT FOUND] lli не найден в стандартных местах" -ForegroundColor Yellow
    Write-Host "Возможные причины:" -ForegroundColor Yellow
    Write-Host "  1. lli не включён в установку LLVM" -ForegroundColor Gray
    Write-Host "  2. lli находится в другом месте" -ForegroundColor Gray
    Write-Host "  3. Требуется полная установка LLVM" -ForegroundColor Gray
}

if ($foundClang) {
    Write-Host "[OK] clang найден" -ForegroundColor Green
    Write-Host "Можно использовать clang для компиляции LLVM IR" -ForegroundColor Gray
} else {
    Write-Host "[NOT FOUND] clang не найден" -ForegroundColor Red
}


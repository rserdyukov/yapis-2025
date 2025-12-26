# PowerShell script for full cycle: compile source to LLVM IR, then to exe and run
# Usage: .\compile_and_run_full.ps1 examples\1_yapis.txt

param(
    [Parameter(Mandatory=$true)]
    [string]$SourceFile
)

# Set UTF-8 encoding for proper text display
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

$ErrorActionPreference = "Stop"

# Check if source file exists
if (-not (Test-Path $SourceFile)) {
    Write-Host "Error: file '$SourceFile' not found" -ForegroundColor Red
    exit 1
}

# Get directory and base name
$BaseName = [System.IO.Path]::GetFileNameWithoutExtension($SourceFile)
$SourceDirName = [System.IO.Path]::GetDirectoryName($SourceFile)

# LL file will be in the same directory as source file
if ($SourceDirName) {
    $LLFile = Join-Path $SourceDirName "$BaseName.ll"
    $ExeName = Join-Path $SourceDirName "$BaseName.exe"
} else {
    $LLFile = "$BaseName.ll"
    $ExeName = "$BaseName.exe"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMPILING SOURCE TO LLVM IR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Compile source to LLVM IR
Write-Host "Compiling to LLVM IR..." -NoNewline
Write-Host " (Source: $SourceFile)" -ForegroundColor Gray
$result = & python main.py $SourceFile 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host " ERROR!" -ForegroundColor Red
    Write-Host $result
    exit 1
}
Write-Host $result

if (-not (Test-Path $LLFile)) {
    Write-Host " ERROR!" -ForegroundColor Red
    Write-Host "Error: LLVM IR file '$LLFile' was not created" -ForegroundColor Red
    Write-Host "Expected path: $LLFile" -ForegroundColor Yellow
    exit 1
}

Write-Host " [OK]" -ForegroundColor Green
Write-Host "LLVM IR created: $LLFile"
Write-Host ""

# Find clang
$ClangPath = $null
if (Test-Path "bin\clang.exe") {
    $ClangPath = "bin\clang.exe"
} else {
    $clang = Get-Command clang.exe -ErrorAction SilentlyContinue
    if ($clang) {
        $ClangPath = $clang.Path
    }
}

if (-not $ClangPath) {
    Write-Host "Error: clang.exe not found" -ForegroundColor Red
    Write-Host "Check that clang is installed and available in PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMPILING LLVM IR TO EXE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Compiling: $LLFile"
Write-Host "Using: $ClangPath"
Write-Host ""

# Compile through clang - try different approaches
# First, try to find gcc and add common MSYS2 paths to PATH
$commonMingwPaths = @(
    "C:\msys64\ucrt64\bin",
    "C:\msys64\mingw64\bin",
    "C:\msys64\clang64\bin"
)

$gccPath = $null
foreach ($path in $commonMingwPaths) {
    if (Test-Path "$path\gcc.exe") {
        $env:Path = "$path;$env:Path"
        $gccPath = "$path\gcc.exe"
        break
    }
}

# Also try to find gcc in current PATH
if (-not $gccPath) {
    try {
        $gccCheck = Get-Command gcc.exe -ErrorAction SilentlyContinue
        if ($gccCheck) {
            $gccPath = $gccCheck.Path
        }
    } catch {}
}

$oldErrorAction = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$compileExitCode = 1

if ($gccPath) {
    # Try with gcc as compiler directly (best option for MinGW)
    Write-Host "Using gcc for compilation..." -ForegroundColor Gray
    $compileResult = & $gccPath $LLFile -o $ExeName 2>&1
    $compileExitCode = $LASTEXITCODE
    
    if ($compileExitCode -ne 0) {
        # Try with MinGW target using clang
        $compileArgs = @($LLFile, "-o", $ExeName, "-target", "x86_64-w64-mingw32", "-fuse-ld=lld")
        $compileResult = & $ClangPath $compileArgs 2>&1
        $compileExitCode = $LASTEXITCODE
    }
}

if ($compileExitCode -ne 0) {
    # Try lld with default target
    $compileArgs = @($LLFile, "-o", $ExeName, "-fuse-ld=lld")
    $compileResult = & $ClangPath $compileArgs 2>&1
    $compileExitCode = $LASTEXITCODE
}

if ($compileExitCode -ne 0) {
    # Try without specifying linker (use default)
    $compileArgs = @($LLFile, "-o", $ExeName)
    $compileResult = & $ClangPath $compileArgs 2>&1
    $compileExitCode = $LASTEXITCODE
}

$ErrorActionPreference = $oldErrorAction

if ($compileExitCode -ne 0) {
    Write-Host ""
    Write-Host "Compilation error:" -ForegroundColor Red
    if ($compileResult) {
        $compileResult | ForEach-Object { Write-Host $_ }
    }
    $compileResultStr = $compileResult | Out-String
    if ($compileResultStr -match "linker|unable to execute") {
        Write-Host ""
        Write-Host "Warning: clang cannot perform linking" -ForegroundColor Yellow
        Write-Host "Visual Studio Build Tools or MinGW/gcc required" -ForegroundColor Yellow
    } elseif ($compileResultStr -match "error:") {
        Write-Host ""
        Write-Host "LLVM IR code has errors. Check the generated LLVM IR file:" -ForegroundColor Yellow
        Write-Host "  $LLFile" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "This is a code generation issue, not a script issue." -ForegroundColor Gray
    }
    exit 1
}

if (Test-Path $ExeName) {
    Write-Host "[OK] Executable created: $ExeName" -ForegroundColor Green
} else {
    Write-Host "Error: executable was not created" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RUNNING PROGRAM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Run
& $ExeName
$exitCode = $LASTEXITCODE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
if ($exitCode -eq 0) {
    Write-Host "[OK] Program executed successfully" -ForegroundColor Green
} else {
    Write-Host "Program exited with code: $exitCode" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Cyan

exit $exitCode

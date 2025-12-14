# Define the path to ilasm.exe
$ilasmPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\ilasm.exe"

# Get the current directory (where .il and .exe files will be)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Define the path to the compiler folder
$compilerFolder = Join-Path $scriptDir "compiler"

# Define full paths to Runtime.cs and ImageLangRuntime.dll in the compiler folder
$imageLangRuntimeDllSource = Join-Path $compilerFolder "ImageLangRuntime.dll"
$runtimeCsSource = Join-Path $compilerFolder "Runtime.cs" # Just defining, no action for .cs in this script

Write-Host "Compiling and running generated IL files..."

# Ensure ImageLangRuntime.dll is copied to the output directory for the .exe to find it
if (Test-Path $imageLangRuntimeDllSource) {
    Write-Host "Copying ImageLangRuntime.dll to current directory..."
    Copy-Item -Path $imageLangRuntimeDllSource -Destination $scriptDir -Force
} else {
    Write-Host "Warning: ImageLangRuntime.dll not found at $imageLangRuntimeDllSource. Executables might fail to run."
}

# Find all .il files in the current directory
Get-ChildItem -Path "*.il" | ForEach-Object {
    $ilFile = $_.FullName
    $baseName = $_.BaseName
    $exeFile = Join-Path $scriptDir "$baseName.exe"

    Write-Host "----------------------------------------"
    Write-Host "Compiling $ilFile to $exeFile"

    # Compile the .il file into an .exe
    & $ilasmPath $ilFile /OUT:$exeFile

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully compiled $ilFile"
        Write-Host "Running $exeFile"
        # Execute the generated .exe
        & $exeFile
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Error running $exeFile. Exit code: $LASTEXITCODE"Р}
    } else {
        Write-Host "Error compiling $ilFile. ilasm exit code: $LASTEXITCODE"
    }
}

Write-Host "----------------------------------------"
Write-Host "All IL files processed."

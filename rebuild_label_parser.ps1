param (
    [switch]$clean,
    [switch]$regenerateSpec,
    [switch]$deleteSpec
)

<#
.SYNOPSIS
    Automates cleanup and rebuild of the Label Parser project using PyInstaller.

.DESCRIPTION
    This script deletes build artifacts, optionally regenerates the .spec file,
    installs dependencies, and packages the project using PyInstaller.

.PARAMETER clean
    Deletes the /build and /dist directories before rebuilding.

.PARAMETER regenerateSpec
    Regenerates the PyInstaller .spec file before building.

.PARAMETER deleteSpec
    Deletes the existing .spec file and forces regeneration.
#>

# --- Use Python from active virtual environment if available ---
if ($env:VIRTUAL_ENV) {
    $venvPython = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
    if (Test-Path $venvPython) {
        $pythonExe = $venvPython
        $scriptsPath = Join-Path $env:VIRTUAL_ENV "Scripts"
    }
}

# --- Detect standard Python install path if not found from venv ---
if (-not $pythonExe) {
    $defaultPythonRoot = "$env:LOCALAPPDATA\Programs\Python"
    if (Test-Path $defaultPythonRoot) {
        $pyDirs = Get-ChildItem -Path $defaultPythonRoot -Directory | Where-Object { $_.Name -like "Python3*" }
        foreach ($dir in $pyDirs) {
            $possiblePython = Join-Path $dir.FullName "python.exe"
            $possibleScripts = Join-Path $dir.FullName "Scripts"
            if ((Test-Path $possiblePython) -and (Test-Path $possibleScripts)) {
                $pythonExe = $possiblePython
                $scriptsPath = $possibleScripts
                break
            }
        }
    }
}

# --- Fallback: Microsoft Store Python detection ---
if (-not $pythonExe) {
    $packageRoot = "$env:LOCALAPPDATA\Packages"
    $pythonPackages = Get-ChildItem -Path $packageRoot -Directory |
        Where-Object { $_.Name -like "PythonSoftwareFoundation.Python.*" } |
        Sort-Object Name -Descending

    foreach ($pkg in $pythonPackages) {
        $base = Join-Path $pkg.FullName "LocalCache\local-packages"
        $pyDirs = Get-ChildItem -Path $base -Directory | Where-Object { $_.Name -like "Python3*" }
        foreach ($dir in $pyDirs) {
            $scripts = Join-Path $dir.FullName "Scripts"
            $python = Join-Path $dir.FullName "python.exe"
            if ((Test-Path $scripts) -and (Test-Path $python)) {
                $scriptsPath = $scripts
                $pythonExe = $python
                break
            }
        }
        if ($pythonExe) { break }
    }
}

if (-not $pythonExe) {
    Write-Host "[X] python.exe not found in expected paths." -ForegroundColor Red
    exit 1
}

# --- Check if pyinstaller is installed ---
$pyinstallerExe = Join-Path $scriptsPath "pyinstaller.exe"

if (-not (Test-Path $pyinstallerExe)) {
    Write-Host "[!] PyInstaller not found. Installing now..." -ForegroundColor Yellow
    $pipExe = Join-Path $scriptsPath "pip.exe"
    if (-not (Test-Path $pipExe)) {
        Write-Host "[X] pip not found. Please ensure Python is correctly installed." -ForegroundColor Red
        exit 1
    }
    & $pipExe install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[X] Failed to install PyInstaller." -ForegroundColor Red
        exit 1
    } else {
        Write-Host "[OK] PyInstaller installed successfully." -ForegroundColor Green
    }
}

# --- Install project dependencies ---
$requiredPackages = @(
    "PyMuPDF",
    "opencv-python",
    "numpy",
    "pyzbar",
    "Pillow"
)

foreach ($pkg in $requiredPackages) {
    Write-Host "[i] Ensuring $pkg is installed..."
    & $scriptsPath\pip.exe install $pkg
}

# --- Add to PATH temporarily for this script ---
$env:PATH += ";$scriptsPath"

# Set working directory to the script's location
$projectPath = "$PSScriptRoot"
Set-Location $projectPath

# Define paths
$buildDir = "$projectPath\build"
$distDir = "$projectPath\dist"
$specFile = "$projectPath\label_parser.spec"

# --- CLEANUP PHASE ---
if ($clean -or $deleteSpec) {
    Write-Host "`n--- Cleaning build and dist directories ---`n"
    if (Test-Path $buildDir) {
        Remove-Item -Recurse -Force $buildDir
        Write-Host "Deleted build directory."
    }
    if (Test-Path $distDir) {
        Remove-Item -Recurse -Force $distDir
        Write-Host "Deleted dist directory."
    }
    if ($deleteSpec -and (Test-Path $specFile)) {
        Remove-Item $specFile
        Write-Host "Deleted spec file."
    }
}

# --- SPEC GENERATION PHASE ---
if ($regenerateSpec -or $deleteSpec) {
    Write-Host "`n--- Generating new spec file ---`n"
    pyi-makespec --onefile --name label_parser label_parser.py
}

# --- BUILD PHASE ---
Write-Host "`n--- Running PyInstaller Build ---`n"
pyinstaller $specFile

# --- Copy config.ini to dist folder ---
Copy-Item "$projectPath\config.ini" "$distDir" -Force

# --- COMPLETION MESSAGE ---
Write-Host "n[OK] Build complete. You can find the output in: $distDir"

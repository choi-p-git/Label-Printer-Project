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

# --- Auto-detect Python Scripts path for Microsoft Store Python installs ---
$packageRoot = "$env:LOCALAPPDATA\Packages"
$pythonPackages = Get-ChildItem -Path $packageRoot -Directory |
    Where-Object { $_.Name -like "PythonSoftwareFoundation.Python.*" } |
    Sort-Object Name -Descending

if (-not $pythonPackages) {
    Write-Host "[X] No Microsoft Store Python installation found." -ForegroundColor Red
    exit 1
}

$latestPythonPath = Join-Path $pythonPackages[0].FullName "LocalCache\local-packages"
$scriptsPath = Join-Path $latestPythonPath "Python313\Scripts"

# Adjust if future Python version changes
if (-not (Test-Path $scriptsPath)) {
    $scriptsPath = Get-ChildItem -Path "$latestPythonPath" -Directory |
        Where-Object { $_.Name -like "Python3*" } |
        Sort-Object Name -Descending |
        Select-Object -First 1 |
        ForEach-Object { Join-Path $_.FullName "Scripts" }
}

if (-not (Test-Path $scriptsPath)) {
    Write-Host "[X] Could not locate the Scripts folder for Microsoft Store Python." -ForegroundColor Red
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
Write-Host "`n[OK] Build complete. You can find the output in: $distDir"

<#
.SYNOPSIS
    Automates cleanup and rebuild of the Label Printer project using PyInstaller.

.DESCRIPTION
    This script deletes build artifacts, optionally regenerates the .spec file,
    and packages the project using PyInstaller.

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
    Write-Host "❌ No Microsoft Store Python installation found." -ForegroundColor Red
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
    Write-Host "❌ Could not locate the Scripts folder for Microsoft Store Python." -ForegroundColor Red
    exit 1
}

# --- Check if pyinstaller is installed ---
$pyinstallerExe = Join-Path $scriptsPath "pyinstaller.exe"

if (-not (Test-Path $pyinstallerExe)) {
    Write-Host "⚠️  PyInstaller not found. Installing now..." -ForegroundColor Yellow
    $pipExe = Join-Path $scriptsPath "pip.exe"
    if (-not (Test-Path $pipExe)) {
        Write-Host "❌ pip not found. Please ensure Python is correctly installed." -ForegroundColor Red
        exit 1
    }
    & $pipExe install pyinstaller
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install PyInstaller." -ForegroundColor Red
        exit 1
    } else {
        Write-Host "✅ PyInstaller installed successfully." -ForegroundColor Green
    }
}

# --- Add to PATH temporarily for this script ---
$env:PATH += ";$scriptsPath"


$pyInstallerPath = "$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\LocalCache\local-packages\Python313\Scripts"
$env:PATH += ";$pyInstallerPath"


param (
    [switch]$clean,
    [switch]$regenerateSpec,
    [switch]$deleteSpec
)

# Set working directory to the script's location
$projectPath = "$PSScriptRoot"
Set-Location $projectPath

# Define paths
$buildDir = "$projectPath\build"
$distDir = "$projectPath\dist"
$specFile = "$projectPath\main_gui.spec"

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
    pyi-makespec --windowed --name LabelPrinter main_gui.py
}

# --- BUILD PHASE ---
Write-Host "`n--- Running PyInstaller Build ---`n"
pyinstaller main_gui.spec

# --- COMPLETION MESSAGE ---
Write-Host "`n✅ Build complete. You can find the output in: $distDir"

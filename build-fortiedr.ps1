# Move to the script directory
Set-Location -Path $PSScriptRoot

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Building FortiEDRDemoTool.exe..." -ForegroundColor Cyan
Write-Host "================================"

# Check if pyinstaller is installed
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "PyInstaller not found. Installing it via pip..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    python -m pip install pyinstaller

    if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: PyInstaller installation failed. Aborting." -ForegroundColor Red
        exit 1
    }
}

# Optional: Clean previous build folders
Remove-Item -Recurse -Force -ErrorAction SilentlyContinue "build", "dist"

# Build the EXE using the custom .spec file
pyinstaller FortiEDRDemoTool.spec

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Build complete." -ForegroundColor Cyan
Write-Host "Moving EXE to Desktop..." -ForegroundColor Cyan
Write-Host "================================"

# Get the current user's desktop path
$desktop = [Environment]::GetFolderPath("Desktop")

# Move the EXE to Desktop if it was created
$exePath = "dist\FortiEDRDemoTool.exe"
if (Test-Path $exePath) {
    Move-Item -Force $exePath "$desktop\FortiEDRDemoTool.exe"
    Write-Host "FortiEDRDemoTool.exe has been moved to the Desktop." -ForegroundColor Green
} else {
    Write-Host "ERROR: EXE file not found. Please check for build errors." -ForegroundColor Red
}

Pause

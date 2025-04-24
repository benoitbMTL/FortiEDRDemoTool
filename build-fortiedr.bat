@echo off
cd /d %~dp0

echo ==============================================
echo Building FortiEDRDemoTool.exe with PyInstaller
echo ==============================================

REM Check if Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    exit /b 1
)

REM Upgrade pip and install pyinstaller if not present
python -m pip install --upgrade pip >nul
python -m pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: PyInstaller installation failed.
        exit /b 1
    )
)

REM Clean previous build folders
echo Cleaning build and dist folders...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable with the custom .spec file
echo Running PyInstaller...
pyinstaller FortiEDRDemoTool.spec
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller failed to build the executable.
    exit /b 1
)

REM Check if the .exe was created
if exist dist\FortiEDRDemoTool.exe (
    echo.
    echo Build complete.
    echo Moving FortiEDRDemoTool.exe to Desktop...

    set desktop=%USERPROFILE%\Desktop
    echo Desktop path is: %desktop%
    copy /Y "dist\FortiEDRDemoTool.exe" "%desktop%\FortiEDRDemoTool.exe"
    color 0A
    echo EXE successfully moved to your Desktop.
    color 07
) else (
    echo.
    color 0C
    echo ERROR: EXE file not found. Please check for build errors.
    color 07
)

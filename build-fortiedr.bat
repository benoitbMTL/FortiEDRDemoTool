@echo off
cd /d %~dp0

echo ==============================================
echo Building FortiEDRDemoTool.exe with PyInstaller
echo ==============================================

REM Ensure tcping exists in tools/ (required by spec)
if not exist "%~dp0tools\tcping.exe" (
    echo ERROR: tcping.exe not found in tools\ folder.
    echo Please place tcping.exe at "%~dp0tools\tcping.exe" before building.
    exit /b 1
)

REM Check if Python is available
where python >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    exit /b 1
)

REM Ensure pip is up-to-date (quiet)
echo Ensuring pip and PyInstaller...
python -m pip install --upgrade pip >nul 2>&1

REM Robust check for PyInstaller: try importing the package in Python
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: PyInstaller installation failed.
        exit /b 1
    )
) else (
    echo PyInstaller is installed.
)

REM Clean previous build folders
echo Cleaning build and dist folders...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build the executable with the custom .spec file
echo Running PyInstaller (using FortiEDRDemoTool.spec)...
pyinstaller FortiEDRDemoTool.spec
if errorlevel 1 (
    echo.
    echo ERROR: PyInstaller failed to build the executable.
    exit /b 1
)

REM If one-dir build, copy tools folder into dist\FortiEDRDemoTool\tools for convenience
if exist "dist\FortiEDRDemoTool" (
    echo Copying tools folder into dist\FortiEDRDemoTool\tools...
    xcopy /Y /E "%~dp0tools" "dist\FortiEDRDemoTool\tools\" >nul
)

REM Determine where the exe is (onefile vs onedir)
if exist "dist\FortiEDRDemoTool.exe" (
    set exe_path=dist\FortiEDRDemoTool.exe
) else if exist "dist\FortiEDRDemoTool\FortiEDRDemoTool.exe" (
    set exe_path=dist\FortiEDRDemoTool\FortiEDRDemoTool.exe
) else (
    echo.
    color 0C
    echo ERROR: EXE file not found. Please check for build errors.
    color 07
    exit /b 1
)

REM Copy the exe to Desktop for convenience
echo.
echo Build complete.
echo Copying %exe_path% to Desktop...
set desktop=%USERPROFILE%\Desktop
copy /Y "%exe_path%" "%desktop%\FortiEDRDemoTool.exe" >nul
if errorlevel 1 (
    echo WARNING: Failed to copy EXE to Desktop. Please copy it manually from dist\.
) else (
    color 0A
    echo EXE successfully moved to your Desktop.
    color 07
)

exit /b 0

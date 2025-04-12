@echo off
cd /d %~dp0

echo ================================
echo Building FortiEDRDemoTool.exe...
echo ================================

REM Optional: clean previous build folders
rmdir /s /q build
rmdir /s /q dist

REM Build the EXE using the custom .spec file
pyinstaller FortiEDRDemoTool.spec

echo.
echo ================================
echo Build complete.
echo Moving EXE to Desktop...
echo ================================

REM Get the current user's Desktop path
set "desktop=%USERPROFILE%\Desktop"

REM Move the EXE to Desktop if it was created successfully
if exist "dist\FortiEDRDemoTool.exe" (
    move /Y "dist\FortiEDRDemoTool.exe" "%desktop%\FortiEDRDemoTool.exe"
    echo FortiEDRDemoTool.exe has been moved to the Desktop.
) else (
    echo ERROR: EXE file not found. Please check for build errors.
)

echo.
pause

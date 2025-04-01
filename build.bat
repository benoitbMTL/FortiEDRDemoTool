@echo off
setlocal

echo === Building main.exe with PyInstaller ===

REM Check if main.exe is running or locked
if exist dist\main.exe (
    echo Attempting to delete dist\main.exe...

    del /f dist\main.exe >nul 2>&1
    if exist dist\main.exe (
        echo ERROR: Unable to delete dist\main.exe. It may still be running.
        echo Please close it before building again.
        pause
        exit /b 1
    )
)

REM Clean previous build folders
rmdir /s /q dist
rmdir /s /q build
del main.spec 2>nul

REM Build the executable
pyinstaller --noconfirm --onefile --windowed ^
--add-data "assets;assets" ^
--add-data ".env;." ^
main.py

REM Check if build succeeded
if exist dist\main.exe (
    echo Build succeeded. Launching main.exe...
    cd dist
    start main.exe
) else (
    echo Build failed. Please check for errors above.
)

pause

@echo off
setlocal

echo === Building app.exe with PyInstaller ===

REM Check if app.exe is running or locked
if exist dist\app.exe (
    echo Attempting to delete dist\app.exe...

    del /f dist\app.exe >nul 2>&1
    if exist dist\app.exe (
        echo ERROR: Unable to delete dist\app.exe. It may still be running.
        echo Please close it before building again.
        pause
        exit /b 1
    )
)

REM Clean previous build folders
rmdir /s /q dist
rmdir /s /q build
del app.spec 2>nul

REM Build the executable
pyinstaller --noconfirm --onefile --windowed ^
--add-data "assets;assets" ^
--add-data ".env;." ^
app.py

REM Check if build succeeded
if exist dist\app.exe (
    echo Build succeeded. Launching app.exe...
    cd dist
    start app.exe
) else (
    echo Build failed. Please check for errors above.
)

pause

@echo off
cd /d %~dp0

echo ================================
echo Building EXE with PyInstaller...
echo ================================

pyinstaller app.py ^
 --onefile ^
 --noconsole ^
 --icon=assets/fortinet.ico ^
 --add-data ".env;." ^
 --add-data "assets;assets"

echo =============================
echo Done! Check the dist\ folder.
echo =============================

pause

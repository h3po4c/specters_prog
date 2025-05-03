@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo [1] Checking for venv...
IF NOT EXIST venv (
    echo No venv exist, creating...
    python -m venv venv
)

echo [2] Activating venv...
call venv\Scripts\activate.bat

echo [3] Building .exe ...
python -m PyInstaller --onefile main.py

echo [4] BUILD DONE! main.exe is in dist\
pause
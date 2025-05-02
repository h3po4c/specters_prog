@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo [1] Проверка и создание виртуального окружения...
IF NOT EXIST venv (
    echo Виртуальное окружение не найдено. Создание...
    python -m venv venv
)

echo [2] Активация виртуального окружения...
call venv\Scripts\activate.bat

echo [3] Установка зависимостей...
pip install --upgrade pip >nul
pip install -r requirements.txt

echo [4] Сборка .exe файла...
python -m PyInstaller --onefile main.py

echo [5] Готово! main.exe находится в папке dist\
pause
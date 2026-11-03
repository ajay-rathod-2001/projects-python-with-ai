@echo off
title AI Career Intelligence — RoboResume Launcher
echo ========================================================
echo   Starting AI Career Intelligence (Robotics Resume Robo)
echo ========================================================
echo.

cd /d "%~dp0"

IF EXIST "backend\.venv\Scripts\python.exe" (
    echo [OK] Using backend virtual environment...
    "backend\.venv\Scripts\python.exe" run.py
) ELSE IF EXIST ".venv\Scripts\python.exe" (
    echo [OK] Using root virtual environment...
    ".venv\Scripts\python.exe" run.py
) ELSE (
    echo [!] Virtual environment not found in backend\.venv or .venv
    echo [*] Falling back to system Python...
    python run.py
)

pause

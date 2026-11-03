@echo off
title AI Career Intelligence — Automated Test Runner
echo ========================================================
echo   Running AI Career Intelligence Automated Tests
echo ========================================================
echo.

cd /d "%~dp0"

IF EXIST "backend\.venv\Scripts\python.exe" (
    "backend\.venv\Scripts\python.exe" -m pytest backend/tests -v -p no:asyncio
) ELSE IF EXIST ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m pytest backend/tests -v -p no:asyncio
) ELSE (
    echo [!] Virtual environment not found. Using system Python...
    python -m pytest backend/tests -v -p no:asyncio
)

echo.
pause

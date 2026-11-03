@echo off
title HireAI -- Standalone Executable Builder
echo ========================================================
echo   Building Standalone HireAI.exe with PyInstaller
echo ========================================================
echo.

cd /d "%~dp0"

IF EXIST "backend\.venv\Scripts\pyinstaller.exe" (
    echo [*] Using backend virtual environment PyInstaller...
    "backend\.venv\Scripts\pyinstaller.exe" HireAI.spec --clean --noconfirm
) ELSE (
    echo [*] Falling back to system PyInstaller...
    pyinstaller HireAI.spec --clean --noconfirm
)

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo   [SUCCESS] Build complete!
    echo   Executable located at: dist\HireAI.exe
    echo ========================================================
) else (
    echo.
    echo [!] Build failed with error code %ERRORLEVEL%
)

echo.
pause


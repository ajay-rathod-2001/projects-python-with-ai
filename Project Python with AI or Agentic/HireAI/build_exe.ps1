# HireAI — Standalone Executable Builder for PowerShell
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Building Standalone HireAI.exe with PyInstaller      " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$pyinstallerBackend = Join-Path $scriptDir "backend\.venv\Scripts\pyinstaller.exe"

if (Test-Path $pyinstallerBackend) {
    Write-Host "[*] Using backend virtual environment PyInstaller..." -ForegroundColor Green
    & $pyinstallerBackend HireAI.spec --clean --noconfirm
} else {
    Write-Host "[*] Using system PyInstaller..." -ForegroundColor Yellow
    pyinstaller HireAI.spec --clean --noconfirm
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Green
    Write-Host "   [SUCCESS] Build complete!                            " -ForegroundColor Green
    Write-Host "   Executable located at: dist\HireAI.exe               " -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "[!] Build failed with exit code $LASTEXITCODE" -ForegroundColor Red
}


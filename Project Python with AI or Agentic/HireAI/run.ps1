# AI Career Intelligence — PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting AI Career Intelligence (RoboResume Launcher)  " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$backendVenv = Join-Path $scriptDir "backend\.venv\Scripts\python.exe"
$rootVenv = Join-Path $scriptDir ".venv\Scripts\python.exe"

if (Test-Path $backendVenv) {
    Write-Host "[✓] Using backend virtual environment: $backendVenv" -ForegroundColor Green
    & $backendVenv run.py
} elseif (Test-Path $rootVenv) {
    Write-Host "[✓] Using root virtual environment: $rootVenv" -ForegroundColor Green
    & $rootVenv run.py
} else {
    Write-Host "[!] Virtual environment not found, using system Python" -ForegroundColor Yellow
    python run.py
}

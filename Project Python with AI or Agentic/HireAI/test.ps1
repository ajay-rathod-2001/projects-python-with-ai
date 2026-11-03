# AI Career Intelligence — Automated Test Runner for PowerShell
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Running AI Career Intelligence Automated Test Suite    " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (Test-Path "$scriptDir\backend\.venv\Scripts\python.exe") {
    $python = "$scriptDir\backend\.venv\Scripts\python.exe"
    $testsDir = "$scriptDir\backend\tests"
} elseif (Test-Path "$scriptDir\.venv\Scripts\python.exe") {
    $python = "$scriptDir\.venv\Scripts\python.exe"
    $testsDir = "$scriptDir\backend\tests"
} else {
    $python = "python"
    $testsDir = "$scriptDir\backend\tests"
}

& $python -m pytest $testsDir -v -p no:asyncio

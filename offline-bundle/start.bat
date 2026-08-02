@echo off
:: ─────────────────────────────────────────────────────────
::  Clinical Trial Complexity Assessor — Local Launcher
::  Windows (double-click to run)
:: ─────────────────────────────────────────────────────────

set PORT=8080
set DIR=%~dp0

echo.
echo   Clinical Trial Complexity Assessor
echo   ------------------------------------
echo   Starting local server on http://localhost:%PORT%
echo   Press Ctrl+C to stop.
echo.

:: Open browser after short delay
start "" /b cmd /c "timeout /t 2 >nul && start http://localhost:%PORT%"

:: Start Python server
python -m http.server %PORT% --directory "%DIR%"
if errorlevel 1 (
    python3 -m http.server %PORT% --directory "%DIR%"
)
if errorlevel 1 (
    echo.
    echo ERROR: Python not found. Please install Python from https://python.org
    echo Or open index.html directly in your browser.
    pause
)

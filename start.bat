@echo off
setlocal enabledelayedexpansion
title Wallpaper Switcher
cd /d "%~dp0"

echo ============================================
echo    Wallpaper Switcher - Launcher
echo ============================================
echo.

:: --- Check / Install uv ---
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] uv not found, installing...
    powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo [!] Failed to install uv. Please install manually: https://docs.astral.sh/uv/
        pause
        exit /b 1
    )
    :: Refresh PATH for current session
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    echo [?] uv installed
    echo.
)

:: --- Create venv if missing ---
set "VENV_DIR=%~dp0.venv"
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [*] Creating virtual environment...
    uv venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo [!] Failed to create venv
        pause
        exit /b 1
    )
    echo [?] Virtual environment created
    echo.
)

:: --- Install dependencies ---
echo [*] Installing dependencies...
uv pip install -r "%~dp0requirements.txt" --python "%VENV_DIR%\Scripts\python.exe"
if %errorlevel% neq 0 (
    echo [!] Failed to install dependencies
    pause
    exit /b 1
)
echo [?] Dependencies ready
echo.

:: --- Launch ---
echo [*] Starting server on http://127.0.0.1:8899
echo     Press Ctrl+C to stop
echo.
"%VENV_DIR%\Scripts\python.exe" "%~dp0server.py"

pause

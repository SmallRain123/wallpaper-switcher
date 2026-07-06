@echo off
setlocal enabledelayedexpansion
set "MyAppVersion=1.0.0"
title Wallpaper Switcher - Build
cd /d "%~dp0"

echo ============================================
echo    Wallpaper Switcher - Desktop Build
echo ============================================
echo.

:: --- Check / Install uv ---
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] uv not found, installing...
    powershell -ExecutionPolicy Bypass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if !errorlevel! neq 0 (
        echo [!] Failed to install uv.
        pause
        exit /b 1
    )
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
    echo [?] uv installed
    echo.
)

:: --- Setup venv ---
set "VENV_DIR=%~dp0.venv"
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [*] Creating virtual environment...
    uv venv "%VENV_DIR%"
    echo [?] venv created
    echo.
)

:: --- Install deps ---
echo [*] Installing dependencies...
uv pip install -r "%~dp0requirements.txt" --python "%VENV_DIR%\Scripts\python.exe"
echo [?] Dependencies ready
echo.

:: --- Clean ---
set "BUILD_DIR=%~dp0build"
set "DIST_DIR=%~dp0dist"
set "RELEASE_DIR=%~dp0release"

if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
if exist "%DIST_DIR%" rmdir /s /q "%DIST_DIR%"
if exist "%RELEASE_DIR%" rmdir /s /q "%RELEASE_DIR%"
echo.

:: --- PyInstaller Build ---
echo [*] Building desktop application...
echo     This may take 2-3 minutes...
echo.

"%VENV_DIR%\Scripts\pyinstaller.exe" ^
    --name "WallpaperSwitcher" ^
    --onefile ^
    --windowed --icon "icon.ico" ^
    --clean ^
    --add-data "static;static" ^
    --hidden-import uvicorn.logging ^
    --hidden-import uvicorn.loops.auto ^
    --hidden-import uvicorn.protocols.http.auto ^
    --hidden-import uvicorn.protocols.websockets.auto ^
    --hidden-import uvicorn.lifespan.on ^
    --hidden-import webview ^
    --hidden-import webview.platforms.winforms ^
    --hidden-import clr ^
    --hidden-import pythonnet ^
    --collect-all webview ^
    --collect-all pythonnet ^
    app.py

if %errorlevel% neq 0 (
    echo [!] Build failed
    pause
    exit /b 1
)
echo [?] Build complete
echo.

:: --- Create release ---
echo [*] Creating release package...
mkdir "%RELEASE_DIR%" 2>nul

copy /y "%DIST_DIR%\WallpaperSwitcher.exe" "%RELEASE_DIR%\" >nul

if exist "%~dp0README.md" (
    copy /y "%~dp0README.md" "%RELEASE_DIR%\" >nul
)

:: --- Inno Setup Installer ---
echo [*] Looking for Inno Setup compiler...
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC (
    echo [*] Building installer with Inno Setup...
    "!ISCC!" /Qp "%~dp0installer.iss"
    if !errorlevel! neq 0 (
        echo [!] Inno Setup compilation failed
    ) else (
        echo [?] Installer created in release folder
    )
) else (
    echo [!] Inno Setup not found - skipping installer build
    echo     Download from: https://jrsoftware.org/isinfo.php
)
echo.

echo ============================================
echo    Build Complete!
echo ============================================
echo.
echo    Portable: %RELEASE_DIR%\WallpaperSwitcher.exe
if defined ISCC echo    Installer: %RELEASE_DIR%\WallpaperSwitcher-Setup-%MyAppVersion%.exe
echo.
echo    Double-click the EXE to launch the desktop app.
echo    (No browser needed - native Windows window)
echo.
pause


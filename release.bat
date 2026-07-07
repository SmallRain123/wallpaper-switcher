@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Wallpaper Switcher - Release Helper

:: ============================================
::    Wallpaper Switcher - 发布助手
:: ============================================

cd /d "%~dp0"

echo.
echo ============================================
echo    Wallpaper Switcher - 发布助手
echo ============================================
echo.

:: 检查是否有未提交的更改
git diff-index --quiet HEAD --
if %errorlevel% neq 0 (
    echo [!] 检测到未提交的更改：
    echo.
    git status --short
    echo.
    choice /C YN /M "是否继续发布"
    if !errorlevel! neq 1 (
        echo [!] 发布已取消
        pause
        exit /b 1
    )
    echo.
)

:: 显示当前标签
echo [*] 当前标签列表：
git tag -l | tail -n 5
echo.

:: 获取版本号
:input_version
set /p VERSION="[?] 请输入版本号 (例如: v1.0.0): "
if "%VERSION%"=="" (
    echo [!] 版本号不能为空
    goto input_version
)

:: 验证版本号格式
echo %VERSION% | findstr /r "^v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*" >nul
if %errorlevel% neq 0 (
    echo [!] 版本号格式错误，应为 vX.Y.Z 格式 (例如: v1.0.0)
    goto input_version
)

:: 检查标签是否已存在
git tag -l | findstr /x "%VERSION%" >nul
if %errorlevel% equ 0 (
    echo [!] 标签 %VERSION% 已存在
    choice /C YN /M "是否删除旧标签并重新创建"
    if !errorlevel! equ 1 (
        git tag -d %VERSION%
        git push origin :refs/tags/%VERSION% 2>nul
        echo [?] 已删除旧标签
    ) else (
        echo [!] 发布已取消
        pause
        exit /b 1
    )
)

:: 确认发布
echo.
echo ============================================
echo    发布信息确认
echo ============================================
echo    版本号: %VERSION%
echo    分支:   master
echo    远程:   origin
echo ============================================
echo.
choice /C YN /M "确认发布"
if %errorlevel% neq 1 (
    echo [!] 发布已取消
    pause
    exit /b 1
)

echo.
echo [*] 创建标签 %VERSION%...
git tag -a %VERSION% -m "Release %VERSION%"
if %errorlevel% neq 0 (
    echo [!] 创建标签失败
    pause
    exit /b 1
)
echo [?] 标签创建成功

echo.
echo [*] 推送标签到远程仓库...
git push origin %VERSION%
if %errorlevel% neq 0 (
    echo [!] 推送标签失败
    echo [*] 删除本地标签...
    git tag -d %VERSION%
    pause
    exit /b 1
)
echo [?] 标签推送成功

echo.
echo ============================================
echo    发布完成！
echo ============================================
echo.
echo    版本: %VERSION%
echo    状态: GitHub Actions 正在构建...
echo.
echo    查看构建进度:
echo    https://github.com/SmallRain123/wallpaper-switcher/actions
echo.
echo    构建完成后，Release 将自动发布到:
echo    https://github.com/SmallRain123/wallpaper-switcher/releases
echo.
pause

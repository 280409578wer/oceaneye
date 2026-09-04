@echo off
chcp 65001 >nul
title OceanEye 首次安装
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1"
if errorlevel 1 (
  echo.
  echo 安装未完成，请查看上方提示。
  pause
  exit /b 1
)
echo.
echo 安装完成。以后双击 start.bat 即可启动。
pause


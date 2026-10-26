@echo off
chcp 65001 >nul
setlocal
title Moodle Token Helper
set "PY=P:\Program Files\Tencent\Marvis\MarvisAgent\1.60.3000.716\runtime\python311\python.exe"
set "SCRIPT=%~dp0get_token.py"

if not exist "%PY%" goto nopy
if not exist "%SCRIPT%" goto noscript

cd /d "%~dp0"
echo Interpreter: %PY%
echo.
"%PY%" "%SCRIPT%"
echo.
pause
exit /b 0

:nopy
echo [x] Python interpreter not found:
echo     %PY%
pause
exit /b 1

:noscript
echo [x] get_token.py not found in: %~dp0
pause
exit /b 1

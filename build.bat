@echo off
chcp 65001 >nul
title x2 UpScale — сборка .exe

echo ============================================
echo   x2 UpScale — сборка standalone .exe
echo ============================================
echo.

:: Проверка PyInstaller
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo [УСТАНОВКА] PyInstaller...
    pip install pyinstaller
)

echo [СБОРКА] Упаковка проекта в .exe...
echo.

pyinstaller --onedir --console -y --name "x2-upscale" --icon app/logo.png ^
  --exclude-module torch ^
  --exclude-module torchvision ^
  --exclude-module tensorflow ^
  --exclude-module paddle ^
  --exclude-module jax ^
  --exclude-module jaxlib ^
  --exclude-module cv2 ^
  --exclude-module numba ^
  --exclude-module llvmlite ^
  --exclude-module nltk ^
  --exclude-module matplotlib ^
  --exclude-module scipy ^
  --exclude-module sklearn ^
  --exclude-module pandas ^
  --add-data "bin/ncnn;bin/ncnn" ^
  --add-data "app/logo.png;app" ^
  main.py

if %errorlevel% neq 0 (
    echo.
    echo [ОШИБКА] Сборка не удалась!
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Готово!
echo.
echo   .exe находится в: dist\x2-upscale\
echo   Размер: ~180 МБ
echo.
echo   Можно запускать: dist\x2-upscale\x2-upscale.exe
echo.
echo   Для раздачи друзьям — заархивируй папку dist\x2-upscale\
echo ============================================
pause

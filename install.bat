@echo off
chcp 65001 >nul
title x2 UpScale — установка

echo ============================================
echo   x2 UpScale — установка зависимостей
echo ============================================
echo.

:: Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден!
    echo Скачай Python 3.10+ с https://www.python.org/downloads/
    pause
    exit /b 1
)

python -c "import sys; v=sys.version_info; exit(0 if v.major==3 and v.minor>=10 else 1)"
if %errorlevel% neq 0 (
    echo [ОШИБКА] Нужен Python 3.10 или новее
    pause
    exit /b 1
)

echo [1/2] Установка базовых зависимостей (Pillow, PyQt6)...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ОШИБКА] Не удалось установить базовые пакеты
    pause
    exit /b 1
)

echo.
echo [2/2] Установка зависимостей для фоторежима (PyTorch, Real-ESRGAN)...
echo       Это большие пакеты ~3 ГБ. Можно пропустить если не нужны.
pip install -r requirements-photo.txt
if %errorlevel% neq 0 (
    echo.
    echo [ПРЕДУПРЕЖДЕНИЕ] Фоторежим не установлен.
    echo   Основной режим (AnimeVideoV3 через Vulkan) будет работать.
    echo   Для фотореализма запусти: pip install -r requirements-photo.txt
)

echo.
echo ============================================
echo   Установка завершена!
echo.
echo   Запуск: python main.py
echo.
echo   Чтобы собрать .exe (PyInstaller):
echo     pip install pyinstaller
echo     build.bat
echo ============================================
pause

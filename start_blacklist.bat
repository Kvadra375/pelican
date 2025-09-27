@echo off
echo ========================================
echo   TELEGRAM БОТ + ЧЕРНЫЙ СПИСОК МОНЕТ
echo ========================================
echo.
echo Выберите действие:
echo 1. Запуск с черным списком монет
echo 2. Управление черным списком
echo 3. Запуск без черного списка (старая версия)
echo 4. Тест черного списка
echo 5. Выход
echo.
set /p choice="Введите номер (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🚫 Запуск с черным списком монет...
    echo 📊 Фильтрация проблемных токенов
    echo ⏹️  Нажмите Ctrl+C для остановки
    echo.
    python futures_arbitrage_blacklist.py
) else if "%choice%"=="2" (
    echo.
    echo ⚙️ Управление черным списком монет...
    echo.
    python manage_blacklist.py
) else if "%choice%"=="3" (
    echo.
    echo 🤖 Запуск без черного списка (старая версия)...
    echo ⚠️  Может показывать проблемные монеты
    echo ⏹️  Нажмите Ctrl+C для остановки
    echo.
    python futures_arbitrage_validated.py
) else if "%choice%"=="4" (
    echo.
    echo 🧪 Тест черного списка монет...
    echo.
    python coin_blacklist.py
    pause
) else if "%choice%"=="5" (
    echo.
    echo 👋 До свидания!
    exit
) else (
    echo.
    echo ❌ Неверный выбор!
    pause
    goto :eof
)

echo.
echo 🛑 Программа завершена
pause



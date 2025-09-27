#!/usr/bin/env python3
"""
Пример конфигурации для арбитражного монитора
Скопируйте этот файл в config.py и настройте под себя
"""

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на ваш токен бота

# Monitoring Settings
MIN_PROFIT = 0.1              # Минимальная прибыль для отображения в консоли (%)
TELEGRAM_MIN_PROFIT = 5.0     # Минимальная прибыль для отправки в Telegram (%)
UPDATE_INTERVAL = 5            # Интервал обновления в секундах

# Logging Settings
LOG_FILE = "arbitrage_log.txt"
USERS_FILE = "telegram_users.json"
BLACKLIST_FILE = "coin_blacklist.json"

# Exchange Settings
EXCHANGES = [
    "BYBIT_FUTURES",
    "BITGET_FUTURES", 
    "GATE_FUTURES",
    "MEXC_FUTURES",
    "BINANCE_FUTURES",
    "HUOBI_FUTURES"
]

# Data Validation Settings
MIN_VOLUME_USD = 100           # Минимальный объем в USD
MAX_PRICE_DIFFERENCE = 50      # Максимальная разница цен в %
MAX_PROFIT_PERCENT = 1000      # Максимальная прибыль в % (фильтр нереалистичных)

# Price Ranges for Validation
PRICE_RANGES = {
    "BTCUSDT": (1000, 200000),
    "ETHUSDT": (100, 20000),
    "USDTUSDT": (0.9, 1.1),
    "default": (0.001, 1000000)
}

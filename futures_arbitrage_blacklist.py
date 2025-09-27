#!/usr/bin/env python3
"""
Фьючерсный арбитражный монитор с черным списком монет
Исключает нереалистичные и проблемные токены
"""

import json
import time
import threading
import signal
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from colorama import init, Fore, Back, Style
import sqlite3
import os
from bitget_futures_rest import BitgetFuturesRestAdapter
from telegram_bot import TelegramBot
from coin_blacklist import CoinBlacklist
from config import (
    TELEGRAM_BOT_TOKEN, MIN_PROFIT, TELEGRAM_MIN_PROFIT, UPDATE_INTERVAL,
    LOG_FILE, USERS_FILE, BLACKLIST_FILE, EXCHANGES
)

# Инициализация colorama для Windows
init(autoreset=True)

class Logger:
    """Класс для логирования в консоль и файл одновременно"""
    
    def __init__(self, log_file=LOG_FILE):
        self.log_file = log_file
        self.start_time = datetime.now()
        
        # Создаем заголовок в файле
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== АРБИТРАЖНЫЙ МОНИТОР С ЧЕРНЫМ СПИСКОМ - {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} ===\n\n")
    
    def log(self, message):
        """Логирует сообщение в консоль и файл"""
        # Убираем цветовые коды для файла
        clean_message = self._remove_color_codes(message)
        
        # Выводим в консоль с цветами
        print(message)
        
        # Записываем в файл без цветов
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"{clean_message}\n")
    
    def _remove_color_codes(self, text):
        """Удаляет цветовые коды из текста"""
        import re
        # Удаляем ANSI escape sequences
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)

# Создаем глобальный логгер
logger = Logger()

class DataValidator:
    """Класс для валидации данных от бирж"""
    
    @staticmethod
    def validate_price(price: float, symbol: str) -> bool:
        """Проверяет, что цена разумна"""
        if price <= 0:
            return False
        
        # Проверяем разумные диапазоны для разных типов токенов
        if symbol.startswith('BTC'):
            return 1000 <= price <= 200000  # BTC должен быть в разумном диапазоне
        elif symbol.startswith('ETH'):
            return 100 <= price <= 50000    # ETH должен быть в разумном диапазоне
        elif symbol.startswith('USDT'):
            return 0.5 <= price <= 2.0      # USDT должен быть около 1
        else:
            return 0.001 <= price <= 1000000  # Остальные токены
    
    @staticmethod
    def validate_volume(volume: float, symbol: str) -> bool:
        """Проверяет, что объем разумен"""
        if volume < 0:
            return False
        
        # Минимальный объем для валидных данных
        return volume >= 100  # Минимум $100 объема
    
    @staticmethod
    def validate_price_difference(price1: float, price2: float, max_diff_percent: float = 50.0) -> bool:
        """Проверяет, что разница в ценах не слишком большая"""
        if price1 <= 0 or price2 <= 0:
            return False
        
        diff_percent = abs(price1 - price2) / min(price1, price2) * 100
        return diff_percent <= max_diff_percent
    
    @staticmethod
    def is_realistic_arbitrage(opportunity: Dict) -> bool:
        """Проверяет, что арбитражная возможность реалистична"""
        symbol = opportunity['symbol']
        profit = opportunity['profit_percent']
        buy_price = opportunity['buy_price']
        sell_price = opportunity['sell_price']
        
        # Слишком большая прибыль подозрительна
        if profit > 1000:  # Более 1000% подозрительно
            return False
        
        # Проверяем разумность цен
        if not DataValidator.validate_price(buy_price, symbol):
            return False
        if not DataValidator.validate_price(sell_price, symbol):
            return False
        
        # Проверяем разницу в ценах
        if not DataValidator.validate_price_difference(buy_price, sell_price, 100.0):
            return False
        
        # Проверяем объемы
        for exchange_name, data in opportunity['all_prices'].items():
            if not DataValidator.validate_volume(data['volume'], symbol):
                return False
        
        return True

class FuturesExchangeAdapter:
    """Базовый класс для адаптеров фьючерсных бирж"""
    
    def __init__(self, name: str, api_url: str):
        self.name = name
        self.api_url = api_url
        self.is_connected = False
        self.error_count = 0
        self.last_update = None
    
    def get_futures_tickers(self) -> Dict[str, Dict]:
        """Получение фьючерсных тикеров (должен быть переопределен)"""
        raise NotImplementedError

class BybitFuturesAdapter(FuturesExchangeAdapter):
    """Адаптер для Bybit фьючерсов"""
    
    def __init__(self):
        super().__init__("BYBIT_FUTURES", "https://api.bybit.com/v5/market")
    
    def get_futures_tickers(self) -> Dict[str, Dict]:
        """Получение фьючерсных тикеров с Bybit"""
        try:
            url = f"{self.api_url}/tickers"
            params = {"category": "linear"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('retCode') == 0 and 'result' in data:
                    raw_tickers = data['result']['list']
                    
                    tickers = {}
                    for item in raw_tickers:
                        symbol = item.get('symbol', '')
                        price = item.get('lastPrice', '0')
                        volume = item.get('volume24h', '0')
                        change = item.get('price24hPcnt', '0')
                        open_interest = item.get('openInterest', '0')
                        
                        if symbol.endswith('USDT'):
                            try:
                                price_val = float(price)
                                volume_val = float(volume)
                                
                                # Валидация данных
                                if not DataValidator.validate_price(price_val, symbol):
                                    continue
                                if not DataValidator.validate_volume(volume_val, symbol):
                                    continue
                                    
                                tickers[symbol] = {
                                    'price': price_val,
                                    'volume': volume_val,
                                    'change': float(change) * 100,
                                    'open_interest': float(open_interest),
                                    'high': float(item.get('high24h', '0')),
                                    'low': float(item.get('low24h', '0'))
                                }
                            except ValueError:
                                continue
                    
                    self.is_connected = True
                    self.error_count = 0
                    self.last_update = datetime.now()
                    return tickers
                else:
                    self.is_connected = False
                    self.error_count += 1
                    return {}
            else:
                self.is_connected = False
                self.error_count += 1
                return {}
                
        except Exception as e:
            self.is_connected = False
            self.error_count += 1
            return {}

class GateFuturesAdapter(FuturesExchangeAdapter):
    """Адаптер для Gate.io фьючерсов"""
    
    def __init__(self):
        super().__init__("GATE_FUTURES", "https://api.gateio.ws/api/v4")
    
    def get_futures_tickers(self) -> Dict[str, Dict]:
        """Получение фьючерсных тикеров с Gate.io"""
        try:
            url = f"{self.api_url}/futures/usdt/tickers"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                tickers = {}
                for item in data:
                    symbol = item.get('contract', '')
                    price = item.get('last', '0')
                    # Используем volume_24h_settle вместо volume_24h_usd
                    volume = item.get('volume_24h_settle', '0')
                    change = item.get('change_percentage', '0')
                    # Используем total_size вместо open_interest
                    open_interest = item.get('total_size', '0')
                    
                    if symbol.endswith('_USDT'):
                        standard_symbol = symbol.replace('_USDT', 'USDT')
                        try:
                            price_val = float(price)
                            volume_val = float(volume)
                            
                            # Валидация данных
                            if not DataValidator.validate_price(price_val, standard_symbol):
                                continue
                            if not DataValidator.validate_volume(volume_val, standard_symbol):
                                continue
                                
                            tickers[standard_symbol] = {
                                'price': price_val,
                                'volume': volume_val,
                                'change': float(change),
                                'open_interest': float(open_interest),
                                'high': float(item.get('high_24h', '0')),
                                'low': float(item.get('low_24h', '0'))
                            }
                        except ValueError:
                            continue
                
                self.is_connected = True
                self.error_count = 0
                self.last_update = datetime.now()
                return tickers
            else:
                self.is_connected = False
                self.error_count += 1
                return {}
                
        except Exception as e:
            self.is_connected = False
            self.error_count += 1
            return {}

class MexcFuturesAdapter(FuturesExchangeAdapter):
    """Адаптер для MEXC фьючерсов"""
    
    def __init__(self):
        super().__init__("MEXC_FUTURES", "https://contract.mexc.com/api/v1")
    
    def get_futures_tickers(self) -> Dict[str, Dict]:
        """Получение фьючерсных тикеров с MEXC"""
        try:
            url = f"{self.api_url}/contract/ticker"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success') and 'data' in data:
                    raw_tickers = data['data']
                    
                    tickers = {}
                    for item in raw_tickers:
                        symbol = item.get('symbol', '')
                        price = item.get('lastPrice', '0')
                        volume = item.get('amount24', '0')
                        change = item.get('riseFallRate', '0')
                        open_interest = item.get('holdVol', '0')
                        
                        if symbol.endswith('_USDT'):
                            standard_symbol = symbol.replace('_USDT', 'USDT')
                            try:
                                price_val = float(price)
                                volume_val = float(volume)
                                
                                # Валидация данных
                                if not DataValidator.validate_price(price_val, standard_symbol):
                                    continue
                                if not DataValidator.validate_volume(volume_val, standard_symbol):
                                    continue
                                    
                                tickers[standard_symbol] = {
                                    'price': price_val,
                                    'volume': volume_val,
                                    'change': float(change) * 100,
                                    'open_interest': float(open_interest),
                                    'high': float(item.get('high24Price', '0')),
                                    'low': float(item.get('lower24Price', '0'))
                                }
                            except ValueError:
                                continue
                    
                    self.is_connected = True
                    self.error_count = 0
                    self.last_update = datetime.now()
                    return tickers
                else:
                    self.is_connected = False
                    self.error_count += 1
                    return {}
            else:
                self.is_connected = False
                self.error_count += 1
                return {}
                
        except Exception as e:
            self.is_connected = False
            self.error_count += 1
            return {}

class BinanceFuturesAdapter(FuturesExchangeAdapter):
    """Адаптер для Binance фьючерсов"""
    
    def __init__(self):
        super().__init__("BINANCE_FUTURES", "https://fapi.binance.com/fapi/v1")
    
    def get_futures_tickers(self) -> Dict[str, Dict]:
        """Получение фьючерсных тикеров с Binance"""
        try:
            url = f"{self.api_url}/ticker/24hr"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                tickers = {}
                for item in data:
                    symbol = item.get('symbol', '')
                    price = item.get('lastPrice', '0')
                    volume = item.get('quoteVolume', '0')
                    change = item.get('priceChangePercent', '0')
                    open_interest = '0'
                    
                    if symbol.endswith('USDT'):
                        try:
                            price_val = float(price)
                            volume_val = float(volume)
                            
                            # Валидация данных
                            if not DataValidator.validate_price(price_val, symbol):
                                continue
                            if not DataValidator.validate_volume(volume_val, symbol):
                                continue
                                
                            tickers[symbol] = {
                                'price': price_val,
                                'volume': volume_val,
                                'change': float(change),
                                'open_interest': float(open_interest),
                                'high': float(item.get('highPrice', '0')),
                                'low': float(item.get('lowPrice', '0'))
                            }
                        except ValueError:
                            continue
                
                self.is_connected = True
                self.error_count = 0
                self.last_update = datetime.now()
                return tickers
            else:
                self.is_connected = False
                self.error_count += 1
                return {}
                
        except Exception as e:
            self.is_connected = False
            self.error_count += 1
            return {}

class HuobiFuturesAdapter(FuturesExchangeAdapter):
    """Адаптер для Huobi (используем spot API)"""
    
    def __init__(self):
        super().__init__("HUOBI_FUTURES", "https://api.huobi.pro")
    
    def get_futures_tickers(self) -> Dict[str, Dict]:
        """Получение тикеров с Huobi (spot API)"""
        try:
            url = f"{self.api_url}/market/tickers"
            
            response = requests.get(url, timeout=10, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'ok' and 'data' in data:
                    raw_tickers = data['data']
                    
                    tickers = {}
                    for item in raw_tickers:
                        symbol = item.get('symbol', '')
                        price = item.get('close', '0')
                        volume = item.get('amount', '0')
                        change = '0'
                        open_interest = '0'
                        
                        if symbol.endswith('usdt'):
                            standard_symbol = symbol.upper()
                            try:
                                price_val = float(price)
                                volume_val = float(volume)
                                
                                # Валидация данных
                                if not DataValidator.validate_price(price_val, standard_symbol):
                                    continue
                                if not DataValidator.validate_volume(volume_val, standard_symbol):
                                    continue
                                    
                                tickers[standard_symbol] = {
                                    'price': price_val,
                                    'volume': volume_val,
                                    'change': float(change),
                                    'open_interest': float(open_interest),
                                    'high': float(item.get('high', '0')),
                                    'low': float(item.get('low', '0'))
                                }
                            except ValueError:
                                continue
                    
                    self.is_connected = True
                    self.error_count = 0
                    self.last_update = datetime.now()
                    return tickers
                else:
                    self.is_connected = False
                    self.error_count += 1
                    return {}
            else:
                self.is_connected = False
                self.error_count += 1
                return {}
                
        except Exception as e:
            self.is_connected = False
            self.error_count += 1
            return {}

class BingxFuturesAdapter(FuturesExchangeAdapter):
    """Адаптер для BingX фьючерсов"""
    
    def __init__(self):
        super().__init__("BINGX_FUTURES", "https://open-api.bingx.com")
    
    def get_futures_tickers(self) -> Dict[str, Dict]:
        """Получение фьючерсных тикеров с BingX"""
        try:
            # BingX API endpoint для получения 24hr ticker statistics
            # Используем spot API, так как futures API может требовать аутентификацию
            url = f"{self.api_url}/openApi/spot/v1/ticker/24hr"
            
            # Добавляем timestamp параметр
            import time
            params = {
                'timestamp': int(time.time() * 1000)
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                tickers = {}
                
                # Проверяем структуру ответа BingX
                if data.get('code') == 0 and 'data' in data:
                    raw_tickers = data['data']
                    
                    for item in raw_tickers:
                        symbol = item.get('symbol', '')
                        price = item.get('lastPrice', '0')
                        volume = item.get('quoteVolume', '0')  # Используем quoteVolume для USD объема
                        change = item.get('priceChangePercent', '0')
                        open_interest = '0'  # Spot API не предоставляет open interest
                        
                        # Конвертируем формат символа из BTC-USDT в BTCUSDT
                        if symbol.endswith('-USDT'):
                            standard_symbol = symbol.replace('-USDT', 'USDT')
                            try:
                                price_val = float(price)
                                volume_val = float(volume)
                                
                                # Валидация данных
                                if not DataValidator.validate_price(price_val, standard_symbol):
                                    continue
                                if not DataValidator.validate_volume(volume_val, standard_symbol):
                                    continue
                                    
                                tickers[standard_symbol] = {
                                    'price': price_val,
                                    'volume': volume_val,
                                    'change': float(change.replace('%', '')),  # Убираем % из строки
                                    'open_interest': float(open_interest),
                                    'high': float(item.get('highPrice', '0')),
                                    'low': float(item.get('lowPrice', '0'))
                                }
                            except ValueError:
                                continue
                else:
                    # Альтернативный формат ответа или fallback
                    if isinstance(data, list):
                        for item in data:
                            symbol = item.get('symbol', '')
                            price = item.get('lastPrice', '0')
                            volume = item.get('volume', '0')
                            change = item.get('priceChangePercent', '0')
                            open_interest = item.get('openInterest', '0')
                            
                            if symbol.endswith('USDT'):
                                try:
                                    price_val = float(price)
                                    volume_val = float(volume)
                                    
                                    # Валидация данных
                                    if not DataValidator.validate_price(price_val, symbol):
                                        continue
                                    if not DataValidator.validate_volume(volume_val, symbol):
                                        continue
                                        
                                    tickers[symbol] = {
                                        'price': price_val,
                                        'volume': volume_val,
                                        'change': float(change),
                                        'open_interest': float(open_interest),
                                        'high': float(item.get('highPrice', '0')),
                                        'low': float(item.get('lowPrice', '0'))
                                    }
                                except ValueError:
                                    continue
                
                self.is_connected = True
                self.error_count = 0
                self.last_update = datetime.now()
                return tickers
            else:
                self.is_connected = False
                self.error_count += 1
                return {}
                
        except Exception as e:
            self.is_connected = False
            self.error_count += 1
            return {}

class FuturesExchangeManager:
    """Менеджер для управления всеми фьючерсными биржами"""
    
    def __init__(self, blacklist: CoinBlacklist):
        self.blacklist = blacklist
        self.adapters = {
            'BYBIT_FUTURES': BybitFuturesAdapter(),
            'BITGET_FUTURES': BitgetFuturesRestAdapter(),
            'GATE_FUTURES': GateFuturesAdapter(),
            'MEXC_FUTURES': MexcFuturesAdapter(),
            'BINANCE_FUTURES': BinanceFuturesAdapter(),
            'HUOBI_FUTURES': HuobiFuturesAdapter(),
            'BINGX_FUTURES': BingxFuturesAdapter()
        }
        self.tickers_cache = {}
        self.last_update = None
    
    def get_all_tickers(self) -> Dict[str, Dict[str, Dict]]:
        """Получение тикеров со всех фьючерсных бирж с фильтрацией по черному списку"""
        all_tickers = {}
        
        for exchange_name, adapter in self.adapters.items():
            try:
                tickers = adapter.get_futures_tickers()
                
                if tickers:
                    # Фильтруем по черному списку
                    filtered_tickers = {}
                    blacklisted_count = 0
                    
                    for symbol, data in tickers.items():
                        if self.blacklist.is_blacklisted(symbol):
                            blacklisted_count += 1
                            continue
                        filtered_tickers[symbol] = data
                    
                    all_tickers[exchange_name] = filtered_tickers
                    logger.log(f"{Fore.GREEN}✅ {exchange_name}: получено {len(filtered_tickers)} валидных тикеров (отфильтровано {blacklisted_count}){Style.RESET_ALL}")
                else:
                    logger.log(f"{Fore.RED}❌ {exchange_name}: не удалось получить данные{Style.RESET_ALL}")
                    
            except Exception as e:
                logger.log(f"{Fore.RED}❌ {exchange_name}: ошибка - {e}{Style.RESET_ALL}")
        
        self.tickers_cache = all_tickers
        self.last_update = datetime.now()
        return all_tickers

def find_arbitrage_opportunities(all_tickers: Dict[str, Dict[str, Dict]], min_profit: float = 0.1) -> List[Dict]:
    """Поиск арбитражных возможностей с валидацией и черным списком"""
    opportunities = []
    
    # Получаем все символы
    all_symbols = set()
    for exchange_tickers in all_tickers.values():
        all_symbols.update(exchange_tickers.keys())
    
    logger.log(f"{Fore.CYAN}🔍 Проверка {len(all_symbols)} символов на арбитражные возможности...{Style.RESET_ALL}")
    
    for symbol in sorted(all_symbols):
        # Собираем цены по всем биржам для данного символа
        symbol_prices = {}
        for exchange_name, tickers in all_tickers.items():
            if symbol in tickers:
                symbol_prices[exchange_name] = tickers[symbol]
        
        if len(symbol_prices) < 2:
            continue
        
        # Фильтруем нулевые цены
        valid_prices = {k: v for k, v in symbol_prices.items() if v['price'] > 0}
        
        if len(valid_prices) < 2:
            continue
        
        # Находим минимальную и максимальную цены
        min_price = min(valid_prices.items(), key=lambda x: x[1]['price'])
        max_price = max(valid_prices.items(), key=lambda x: x[1]['price'])
        
        # Проверяем, что минимальная цена больше нуля
        if min_price[1]['price'] <= 0:
            continue
        
        # Вычисляем прибыль
        profit_percent = ((max_price[1]['price'] - min_price[1]['price']) / min_price[1]['price']) * 100
        
        if profit_percent >= min_profit:
            opportunity = {
                'symbol': symbol,
                'profit_percent': profit_percent,
                'buy_exchange': min_price[0],
                'sell_exchange': max_price[0],
                'buy_price': min_price[1]['price'],
                'sell_price': max_price[1]['price'],
                'all_prices': symbol_prices,
                'timestamp': datetime.now()
            }
            
            # Валидация арбитражной возможности
            if DataValidator.is_realistic_arbitrage(opportunity):
                opportunities.append(opportunity)
                logger.log(f"{Fore.GREEN}✅ Валидная возможность: {symbol} - {profit_percent:.2f}%{Style.RESET_ALL}")
            else:
                logger.log(f"{Fore.YELLOW}⚠️ Отфильтрована нереалистичная возможность: {symbol} - {profit_percent:.2f}%{Style.RESET_ALL}")
    
    return sorted(opportunities, key=lambda x: x['profit_percent'], reverse=True)

class FuturesArbitrageBot:
    """Арбитражный монитор с черным списком монет"""
    
    def __init__(self, min_profit: float = 0.1, update_interval: int = 5, telegram_min_profit: float = 5.0):
        self.blacklist = CoinBlacklist()
        self.manager = FuturesExchangeManager(self.blacklist)
        self.min_profit = min_profit
        self.update_interval = update_interval
        self.telegram_min_profit = telegram_min_profit
        self.running = False
        self.opportunities_found = 0
        self.telegram_notifications_sent = 0
        
        # Инициализируем Telegram бота
        self.telegram_bot = TelegramBot(TELEGRAM_BOT_TOKEN)
        
        # Настройка обработчика сигналов
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для корректного завершения"""
        logger.log(f"\n{Fore.YELLOW}Получен сигнал завершения. Останавливаю монитор...{Style.RESET_ALL}")
        self.stop()
        sys.exit(0)
    
    def run_arbitrage_monitor(self):
        """Запускает мониторинг арбитражных возможностей"""
        logger.log(f"{Fore.GREEN}🚀 Арбитражный монитор с черным списком запущен{Style.RESET_ALL}")
        logger.log(f"{Fore.CYAN}Минимальная прибыль: {self.min_profit}%{Style.RESET_ALL}")
        logger.log(f"{Fore.CYAN}Telegram уведомления: > {self.telegram_min_profit}%{Style.RESET_ALL}")
        logger.log(f"{Fore.CYAN}Интервал обновления: {self.update_interval} секунд{Style.RESET_ALL}")
        logger.log(f"{Fore.CYAN}Черный список: {self.blacklist.get_blacklist_count()} монет{Style.RESET_ALL}")
        
        while self.running:
            try:
                # Получаем данные со всех бирж
                all_tickers = self.manager.get_all_tickers()
                
                if not all_tickers:
                    logger.log(f"{Fore.RED}❌ Не удалось получить данные ни с одной биржи{Style.RESET_ALL}")
                    time.sleep(self.update_interval)
                    continue
                
                # Ищем арбитражные возможности
                opportunities = find_arbitrage_opportunities(all_tickers, self.min_profit)
                
                if opportunities:
                    self.opportunities_found += len(opportunities)
                    logger.log(f"{Fore.GREEN}🎯 Найдено {len(opportunities)} ВАЛИДНЫХ арбитражных возможностей!{Style.RESET_ALL}")
                    
                    # Отправляем уведомления в Telegram для возможностей > 5%
                    telegram_opportunities = [opp for opp in opportunities if opp['profit_percent'] >= self.telegram_min_profit]
                    
                    if telegram_opportunities and self.telegram_bot.active_users:
                        logger.log(f"{Fore.YELLOW}📱 Отправка {len(telegram_opportunities)} уведомлений в Telegram...{Style.RESET_ALL}")
                        
                        for opportunity in telegram_opportunities:
                            sent_count = self.telegram_bot.send_arbitrage_alert(opportunity)
                            if sent_count > 0:
                                self.telegram_notifications_sent += sent_count
                                logger.log(f"{Fore.GREEN}✅ Telegram уведомление отправлено для {opportunity['symbol']} ({opportunity['profit_percent']:.2f}%) - {sent_count} пользователей{Style.RESET_ALL}")
                else:
                    logger.log(f"{Fore.YELLOW}⏳ Валидные арбитражные возможности не найдены{Style.RESET_ALL}")
                
                # Показываем статистику
                total_symbols = len(set().union(*[tickers.keys() for tickers in all_tickers.values()]))
                logger.log(f"📊 Проверено {total_symbols} символов, найдено {len(opportunities)} ВАЛИДНЫХ возможностей")
                logger.log(f"👥 Активных пользователей: {len(self.telegram_bot.active_users)}")
                logger.log(f"📱 Telegram уведомлений отправлено: {self.telegram_notifications_sent}")
                logger.log(f"🚫 Черный список: {self.blacklist.get_blacklist_count()} монет")
                
                if self.running:
                    time.sleep(self.update_interval)
                    
            except Exception as e:
                logger.log(f"{Fore.RED}❌ Ошибка в мониторе: {e}{Style.RESET_ALL}")
                time.sleep(self.update_interval)
    
    def run(self):
        """Запускает бота и мониторинг"""
        self.running = True
        
        logger.log(f"{Fore.CYAN}🤖 Запуск Telegram бота с черным списком монет{Style.RESET_ALL}")
        logger.log(f"{Fore.CYAN}Поддерживаемые биржи: Bybit Futures, Bitget Futures, Gate.io Futures, MEXC Futures, Binance Futures, Huobi Futures, BingX Futures{Style.RESET_ALL}")
        logger.log(f"{Fore.CYAN}Telegram уведомления: > 5% прибыли{Style.RESET_ALL}")
        logger.log(f"{Fore.CYAN}Черный список: {self.blacklist.get_blacklist_count()} монет{Style.RESET_ALL}")
        logger.log("")
        
        # Запускаем мониторинг в отдельном потоке
        monitor_thread = threading.Thread(target=self.run_arbitrage_monitor, daemon=True)
        monitor_thread.start()
        
        # Запускаем Telegram бота в основном потоке
        try:
            self.telegram_bot.start_monitoring(None)
        except KeyboardInterrupt:
            logger.log(f"\n{Fore.YELLOW}Получен сигнал завершения. Останавливаю монитор...{Style.RESET_ALL}")
        except Exception as e:
            logger.log(f"\n{Fore.RED}❌ Критическая ошибка: {e}{Style.RESET_ALL}")
        finally:
            self.stop()
    
    def stop(self):
        """Остановка монитора"""
        self.running = False
        self.telegram_bot.stop_monitoring()
        logger.log(f"{Fore.GREEN}🛑 Монитор остановлен{Style.RESET_ALL}")
        logger.log(f"{Fore.CYAN}📊 Статистика:{Style.RESET_ALL}")
        logger.log(f"   Найдено ВАЛИДНЫХ возможностей: {self.opportunities_found}")
        logger.log(f"   Telegram уведомлений: {self.telegram_notifications_sent}")
        logger.log(f"   Черный список: {self.blacklist.get_blacklist_count()} монет")

def main():
    """Главная функция"""
    logger.log(f"{Fore.CYAN}🤖 Telegram бот + Арбитражный монитор с черным списком{Style.RESET_ALL}")
    logger.log(f"{Fore.CYAN}Команды бота: /start, /stop, /status, /help{Style.RESET_ALL}")
    logger.log(f"{Fore.CYAN}Уведомления: > 5% прибыли{Style.RESET_ALL}")
    logger.log(f"{Fore.CYAN}Черный список: Исключение проблемных монет{Style.RESET_ALL}")
    logger.log("")
    
    # Создаем монитор
    bot = FuturesArbitrageBot(min_profit=MIN_PROFIT, update_interval=UPDATE_INTERVAL, telegram_min_profit=TELEGRAM_MIN_PROFIT)
    
    # Запускаем
    bot.run()

if __name__ == "__main__":
    main()

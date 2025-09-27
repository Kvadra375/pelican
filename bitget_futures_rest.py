#!/usr/bin/env python3
"""
Bitget Futures REST API адаптер
Использует правильный API v2 для получения фьючерсных данных
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Optional
from colorama import init, Fore, Style

# Инициализация colorama
init(autoreset=True)

class BitgetFuturesRestAdapter:
    """REST адаптер для Bitget фьючерсов"""
    
    def __init__(self):
        self.name = "BITGET_FUTURES"
        self.api_url = "https://api.bitget.com/api/v2/mix/market"
        self.is_connected = False
        self.error_count = 0
        self.last_update = None
        self.tickers = {}
    
    def get_futures_tickers(self) -> Dict[str, Dict]:
        """Получение фьючерсных тикеров через REST API"""
        try:
            # Получаем все тикеры фьючерсов
            url = f"{self.api_url}/tickers"
            params = {"productType": "USDT-FUTURES"}
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                tickers = {}
                
                if data.get('code') == '00000' and 'data' in data:
                    for item in data['data']:
                        symbol = item.get('symbol', '')
                        last_price = item.get('lastPr', '0')
                        volume_24h = item.get('usdtVolume', '0')
                        change_24h = item.get('changeUtc24h', '0')
                        open_interest = item.get('holdingAmount', '0')
                        high_24h = item.get('high24h', '0')
                        low_24h = item.get('low24h', '0')
                        
                        if symbol.endswith('USDT'):
                            try:
                                tickers[symbol] = {
                                    'price': float(last_price),
                                    'volume': float(volume_24h),
                                    'change': float(change_24h) * 100,  # Конвертируем в проценты
                                    'open_interest': float(open_interest),
                                    'high': float(high_24h),
                                    'low': float(low_24h)
                                }
                            except ValueError:
                                continue
                
                self.is_connected = True
                self.error_count = 0
                self.last_update = datetime.now()
                self.tickers = tickers
                return tickers
            else:
                self.is_connected = False
                self.error_count += 1
                print(f"{Fore.RED}❌ Bitget Futures REST ошибка: {response.status_code} - {response.text[:200]}{Style.RESET_ALL}")
                return {}
                
        except Exception as e:
            self.is_connected = False
            self.error_count += 1
            print(f"{Fore.RED}❌ Ошибка Bitget Futures REST: {e}{Style.RESET_ALL}")
            return {}
    
    def get_connection_status(self) -> str:
        """Получение статуса соединения"""
        if self.is_connected:
            return f"{Fore.GREEN}✅{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}❌{Style.RESET_ALL}"

def test_bitget_futures_rest():
    """Тестирование Bitget Futures REST API"""
    print(f"{Fore.CYAN}🧪 Тестирование Bitget Futures REST API{Style.RESET_ALL}")
    
    adapter = BitgetFuturesRestAdapter()
    tickers = adapter.get_futures_tickers()
    
    if tickers:
        print(f"{Fore.GREEN}✅ Получено {len(tickers)} фьючерсных тикеров{Style.RESET_ALL}")
        
        # Показываем топ-10 по объему
        sorted_tickers = sorted(tickers.items(), 
                               key=lambda x: x[1].get('volume', 0), 
                               reverse=True)[:10]
        
        print(f"\n{Fore.YELLOW}📊 Топ-10 фьючерсов по объему:{Style.RESET_ALL}")
        print(f"{'Символ':<15} {'Цена':<15} {'Объем':<15} {'OI':<12} {'Изменение':<12}")
        print(f"{'-'*75}")
        
        for symbol, data in sorted_tickers:
            price = data.get('price', 0)
            volume = data.get('volume', 0)
            open_interest = data.get('open_interest', 0)
            change = data.get('change', 0)
            
            # Форматируем цену
            if price >= 1:
                price_str = f"${price:,.4f}"
            elif price >= 0.01:
                price_str = f"${price:,.6f}"
            else:
                price_str = f"${price:.8f}"
            
            # Форматируем объем
            if volume >= 1000000:
                volume_str = f"${volume/1000000:.1f}M"
            elif volume >= 1000:
                volume_str = f"${volume/1000:.1f}K"
            else:
                volume_str = f"${volume:.0f}"
            
            # Форматируем открытый интерес
            if open_interest >= 1000000:
                oi_str = f"{open_interest/1000000:.1f}M"
            elif open_interest >= 1000:
                oi_str = f"{open_interest/1000:.1f}K"
            else:
                oi_str = f"{open_interest:.0f}"
            
            # Форматируем изменение
            change_str = f"{change:+.2f}%"
            
            print(f"{symbol:<15} {price_str:<15} {volume_str:<15} {oi_str:<12} {change_str:<12}")
    else:
        print(f"{Fore.RED}❌ Не удалось получить данные{Style.RESET_ALL}")

if __name__ == "__main__":
    test_bitget_futures_rest()

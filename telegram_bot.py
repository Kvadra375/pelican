#!/usr/bin/env python3
"""
Telegram бот для управления арбитражным монитором
Поддерживает команды и запоминает пользователей
"""

import requests
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Set
import os
from config import USERS_FILE

class TelegramBot:
    """Telegram бот с командами и управлением пользователями"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self.users_file = USERS_FILE
        self.active_users: Set[str] = set()
        self.last_update_id = 0
        self.running = False
        self.monitor_thread = None
        self.monitor_callback = None
        
        # Загружаем сохраненных пользователей
        self.load_users()
    
    def load_users(self):
        """Загружает список пользователей из файла"""
        try:
            if os.path.exists(self.users_file):
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.active_users = set(data.get('active_users', []))
                    print(f"✅ Загружено {len(self.active_users)} активных пользователей")
            else:
                print("📝 Файл пользователей не найден, создаем новый")
        except Exception as e:
            print(f"❌ Ошибка загрузки пользователей: {e}")
            self.active_users = set()
    
    def save_users(self):
        """Сохраняет список пользователей в файл"""
        try:
            data = {
                'active_users': list(self.active_users),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Сохранено {len(self.active_users)} пользователей")
        except Exception as e:
            print(f"❌ Ошибка сохранения пользователей: {e}")
    
    def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> bool:
        """Отправляет сообщение пользователю"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if result.get('ok'):
                return True
            else:
                print(f"❌ Ошибка отправки сообщения: {result.get('description', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка отправки сообщения: {e}")
            return False
    
    def send_message_to_all(self, text: str, parse_mode: str = "HTML") -> int:
        """Отправляет сообщение всем активным пользователям"""
        sent_count = 0
        for chat_id in self.active_users.copy():
            if self.send_message(chat_id, text, parse_mode):
                sent_count += 1
            time.sleep(0.1)  # Небольшая задержка между отправками
        return sent_count
    
    def handle_command(self, chat_id: str, command: str, user_name: str = "Unknown"):
        """Обрабатывает команды от пользователей"""
        
        if command == "/start":
            self.active_users.add(chat_id)
            self.save_users()
            
            welcome_text = f"""
🤖 <b>Добро пожаловать, {user_name}!</b>

🚀 <b>Арбитражный монитор запущен!</b>

📊 <b>Доступные команды:</b>
/start - Запустить мониторинг
/stop - Остановить мониторинг  
/status - Статус монитора
/help - Помощь

💰 <b>Уведомления:</b>
• Автоматически для возможностей > 5%
• 6 бирж: Bybit, Bitget, Gate.io, MEXC, Binance, Huobi
• Обновление каждые 5 секунд

⏰ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
            """
            
            self.send_message(chat_id, welcome_text)
            print(f"✅ Пользователь {user_name} ({chat_id}) добавлен")
            
        elif command == "/stop":
            if chat_id in self.active_users:
                self.active_users.remove(chat_id)
                self.save_users()
                
                stop_text = f"""
🛑 <b>Мониторинг остановлен</b>

👋 До свидания, {user_name}!

💡 Для повторного запуска отправьте /start

⏰ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
                """
                
                self.send_message(chat_id, stop_text)
                print(f"❌ Пользователь {user_name} ({chat_id}) удален")
            else:
                self.send_message(chat_id, "❌ Вы не были подписаны на уведомления")
                
        elif command == "/status":
            status_text = f"""
📊 <b>Статус монитора</b>

👥 <b>Активных пользователей:</b> {len(self.active_users)}
🔄 <b>Статус:</b> {'🟢 Работает' if self.running else '🔴 Остановлен'}
📱 <b>Ваш статус:</b> {'🟢 Подписан' if chat_id in self.active_users else '🔴 Не подписан'}

💰 <b>Настройки:</b>
• Минимальная прибыль: 5%
• Биржи: 6
• Интервал: 5 сек

⏰ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
            """
            
            self.send_message(chat_id, status_text)
            
        elif command == "/help":
            help_text = f"""
❓ <b>Помощь по командам</b>

🚀 <b>/start</b> - Запустить мониторинг арбитражных возможностей
🛑 <b>/stop</b> - Остановить мониторинг
📊 <b>/status</b> - Показать статус монитора
❓ <b>/help</b> - Показать эту справку

💰 <b>Как это работает:</b>
1. Отправьте /start для подписки
2. Получайте уведомления о возможностях > 5%
3. Отправьте /stop для отписки

📱 <b>Уведомления содержат:</b>
• Символ и прибыль
• Цены на всех биржах
• Объемы и открытый интерес
• Время обнаружения

⏰ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
            """
            
            self.send_message(chat_id, help_text)
            
        else:
            unknown_text = f"""
❓ <b>Неизвестная команда</b>

Используйте /help для просмотра доступных команд

⏰ {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
            """
            
            self.send_message(chat_id, unknown_text)
    
    def get_updates(self):
        """Получает обновления от Telegram"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": 10
            }
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    if 'message' in update:
                        message = update['message']
                        chat_id = str(message['chat']['id'])
                        user_name = message['from'].get('first_name', 'Unknown')
                        text = message.get('text', '')
                        
                        # Обрабатываем команды
                        if text.startswith('/'):
                            self.handle_command(chat_id, text, user_name)
                        else:
                            # Если не команда, показываем помощь
                            self.handle_command(chat_id, '/help', user_name)
                    
                    self.last_update_id = update['update_id']
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка получения обновлений: {e}")
            return False
    
    def start_monitoring(self, monitor_callback):
        """Запускает мониторинг команд"""
        self.monitor_callback = monitor_callback
        self.running = True
        
        print("🤖 Telegram бот запущен")
        print("📱 Ожидание команд от пользователей...")
        print("💡 Отправьте боту /start для начала работы")
        
        while self.running:
            try:
                self.get_updates()
                time.sleep(1)  # Проверяем каждую секунду
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Ошибка в цикле мониторинга: {e}")
                time.sleep(5)
        
        print("🛑 Telegram бот остановлен")
    
    def stop_monitoring(self):
        """Останавливает мониторинг"""
        self.running = False
    
    def send_arbitrage_alert(self, opportunity: Dict) -> int:
        """Отправляет уведомление об арбитражной возможности всем пользователям"""
        if not self.active_users:
            return 0
        
        message = self.format_arbitrage_opportunity(opportunity)
        return self.send_message_to_all(message)
    
    def format_arbitrage_opportunity(self, opportunity: Dict) -> str:
        """Форматирует арбитражную возможность для Telegram"""
        symbol = opportunity['symbol']
        profit = opportunity['profit_percent']
        timestamp = opportunity['timestamp'].strftime('%d-%m-%Y %H:%M:%S')
        buy_exchange = opportunity['buy_exchange']
        sell_exchange = opportunity['sell_exchange']
        buy_price = opportunity['buy_price']
        sell_price = opportunity['sell_price']
        
        # Эмодзи в зависимости от прибыли
        if profit >= 50:
            emoji = "🚀🚀🚀"
        elif profit >= 20:
            emoji = "🚀🚀"
        elif profit >= 10:
            emoji = "🚀"
        else:
            emoji = "💰"
        
        message = f"""
{emoji} <b>АРБИТРАЖНАЯ ВОЗМОЖНОСТЬ</b> {emoji}

<b>Символ:</b> {symbol}
<b>Прибыль:</b> <code>{profit:.2f}%</code>
<b>Время:</b> {timestamp}

<b>📈 Маршрут:</b>
🟢 Покупка: {buy_exchange} - <code>${buy_price:.6f}</code>
🔴 Продажа: {sell_exchange} - <code>${sell_price:.6f}</code>

<b>📊 Все цены:</b>
"""
        
        # Добавляем все цены
        for exchange_name, data in opportunity['all_prices'].items():
            price = data['price']
            volume = data['volume']
            oi = data['open_interest']
            
            # Форматируем объем
            if volume >= 1_000_000:
                vol_str = f"${volume/1_000_000:.1f}M"
            elif volume >= 1_000:
                vol_str = f"${volume/1_000:.1f}K"
            else:
                vol_str = f"${volume:.0f}"
            
            # Форматируем OI
            if oi >= 1_000_000:
                oi_str = f"{oi/1_000_000:.1f}M"
            elif oi >= 1_000:
                oi_str = f"{oi/1_000:.1f}K"
            else:
                oi_str = f"{oi:.0f}"
            
            message += f"• {exchange_name}: <code>${price:.6f}</code> | Vol: {vol_str} | OI: {oi_str}\n"
        
        message += f"\n⏰ {datetime.now().strftime('%H:%M:%S')}"
        
        return message

def test_bot():
    """Тестирует работу бота"""
    from config import TELEGRAM_BOT_TOKEN
    bot_token = TELEGRAM_BOT_TOKEN
    
    print("🤖 Тестирование Telegram бота...")
    
    bot = TelegramBot(bot_token)
    
    # Тестовое сообщение
    test_message = """
🧪 <b>Тест бота</b>

✅ Бот работает корректно!
📊 Готов к приему команд

⏰ {time}
    """.format(time=datetime.now().strftime('%d-%m-%Y %H:%M:%S'))
    
    # Отправляем тестовое сообщение всем пользователям
    sent_count = bot.send_message_to_all(test_message)
    print(f"📱 Отправлено {sent_count} тестовых сообщений")
    
    return bot

if __name__ == "__main__":
    test_bot()



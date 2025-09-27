#!/usr/bin/env python3
"""
Скрипт для получения chat_id от Telegram бота
"""

import requests
import time
from config import TELEGRAM_BOT_TOKEN

def get_chat_id():
    """Получает chat_id от бота"""
    bot_token = TELEGRAM_BOT_TOKEN
    base_url = f"https://api.telegram.org/bot{bot_token}"
    
    print("🤖 Ожидание сообщения от пользователя...")
    print("📝 Отправьте боту любое сообщение (например: /start)")
    print("⏳ Проверяем каждые 5 секунд...")
    
    last_update_id = 0
    
    while True:
        try:
            url = f"{base_url}/getUpdates"
            params = {"offset": last_update_id + 1, "timeout": 10}
            
            response = requests.get(url, params=params, timeout=15)
            data = response.json()
            
            if data.get('ok') and data.get('result'):
                for update in data['result']:
                    if 'message' in update:
                        message = update['message']
                        chat_id = message['chat']['id']
                        user_name = message['from'].get('first_name', 'Unknown')
                        text = message.get('text', '')
                        
                        print(f"\n✅ Получено сообщение от {user_name}!")
                        print(f"📝 Текст: {text}")
                        print(f"🆔 Chat ID: {chat_id}")
                        print(f"\n🎉 Готово! Теперь можно запускать монитор с Telegram уведомлениями")
                        
                        return str(chat_id)
                    
                    last_update_id = update['update_id']
            
            print(".", end="", flush=True)
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n\n⏹️ Остановлено пользователем")
            break
        except Exception as e:
            print(f"\n❌ Ошибка: {e}")
            time.sleep(5)
    
    return None

if __name__ == "__main__":
    get_chat_id()



#!/usr/bin/env python3
"""
Автоматическая очистка черного списка монет
"""

from coin_blacklist import CoinBlacklist
from colorama import init, Fore, Style

# Инициализация colorama для Windows
init(autoreset=True)

def main():
    """Автоматически очищает черный список монет"""
    
    print(f"{Fore.CYAN}🗑️ Автоматическая очистка черного списка монет{Style.RESET_ALL}")
    print("=" * 50)
    
    # Создаем экземпляр черного списка
    blacklist = CoinBlacklist()
    
    # Показываем текущую статистику
    current_count = blacklist.get_blacklist_count()
    print(f"📊 Текущее количество монет в черном списке: {current_count}")
    
    if current_count == 0:
        print(f"{Fore.YELLOW}⚠️ Черный список уже пуст!{Style.RESET_ALL}")
        return
    
    # Автоматически очищаем черный список
    blacklist.clear_blacklist()
    print(f"{Fore.GREEN}✅ Черный список полностью очищен!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}📝 Теперь вы можете сами решить, какие монеты добавить{Style.RESET_ALL}")
    print(f"{Fore.CYAN}💡 Используйте 'python manage_blacklist.py' для управления{Style.RESET_ALL}")
    
    # Показываем новую статистику
    new_count = blacklist.get_blacklist_count()
    print(f"📊 Новое количество монет в черном списке: {new_count}")

if __name__ == "__main__":
    main()



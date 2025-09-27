#!/usr/bin/env python3
"""
Очистка черного списка монет
"""

from coin_blacklist import CoinBlacklist
from colorama import init, Fore, Style

# Инициализация colorama для Windows
init(autoreset=True)

def main():
    """Очищает черный список монет"""
    
    print(f"{Fore.CYAN}🗑️ Очистка черного списка монет{Style.RESET_ALL}")
    print("=" * 50)
    
    # Создаем экземпляр черного списка
    blacklist = CoinBlacklist()
    
    # Показываем текущую статистику
    current_count = blacklist.get_blacklist_count()
    print(f"📊 Текущее количество монет в черном списке: {current_count}")
    
    if current_count == 0:
        print(f"{Fore.YELLOW}⚠️ Черный список уже пуст!{Style.RESET_ALL}")
        return
    
    # Подтверждение
    confirm = input(f"\n{Fore.RED}⚠️ Вы уверены, что хотите удалить ВСЕ {current_count} монет из черного списка? (yes/no): {Style.RESET_ALL}").strip().lower()
    
    if confirm == "yes":
        # Очищаем черный список
        blacklist.clear_blacklist()
        print(f"{Fore.GREEN}✅ Черный список полностью очищен!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📝 Теперь вы можете сами решить, какие монеты добавить{Style.RESET_ALL}")
        print(f"{Fore.CYAN}💡 Используйте 'python manage_blacklist.py' для управления{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}❌ Очистка отменена{Style.RESET_ALL}")

if __name__ == "__main__":
    main()



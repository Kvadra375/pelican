#!/usr/bin/env python3
"""
Управление черным списком монет
"""

from coin_blacklist import CoinBlacklist
from colorama import init, Fore, Style

# Инициализация colorama для Windows
init(autoreset=True)

def main():
    """Главное меню управления черным списком"""
    
    print(f"{Fore.CYAN}🚫 Управление черным списком монет{Style.RESET_ALL}")
    print("=" * 50)
    
    # Создаем экземпляр черного списка
    blacklist = CoinBlacklist()
    
    while True:
        print(f"\n{Fore.YELLOW}Выберите действие:{Style.RESET_ALL}")
        print("1. Показать черный список")
        print("2. Добавить монету в черный список")
        print("3. Удалить монету из черного списка")
        print("4. Проверить монету")
        print("5. Статистика")
        print("6. Очистить черный список")
        print("7. Выход")
        
        choice = input(f"\n{Fore.CYAN}Введите номер (1-7): {Style.RESET_ALL}").strip()
        
        if choice == "1":
            # Показать черный список
            limit = input(f"{Fore.CYAN}Сколько монет показать? (Enter для всех): {Style.RESET_ALL}").strip()
            try:
                limit = int(limit) if limit else None
            except ValueError:
                limit = 50
            
            blacklist.print_blacklist(limit)
            
        elif choice == "2":
            # Добавить монету
            symbol = input(f"{Fore.CYAN}Введите символ монеты (например, BTCUSDT): {Style.RESET_ALL}").strip().upper()
            if symbol:
                blacklist.add_to_blacklist(symbol)
            else:
                print(f"{Fore.RED}❌ Пустой символ!{Style.RESET_ALL}")
                
        elif choice == "3":
            # Удалить монету
            symbol = input(f"{Fore.CYAN}Введите символ монеты для удаления: {Style.RESET_ALL}").strip().upper()
            if symbol:
                blacklist.remove_from_blacklist(symbol)
            else:
                print(f"{Fore.RED}❌ Пустой символ!{Style.RESET_ALL}")
                
        elif choice == "4":
            # Проверить монету
            symbol = input(f"{Fore.CYAN}Введите символ монеты для проверки: {Style.RESET_ALL}").strip().upper()
            if symbol:
                if blacklist.is_blacklisted(symbol):
                    print(f"{Fore.RED}❌ {symbol} находится в черном списке{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ {symbol} НЕ находится в черном списке{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Пустой символ!{Style.RESET_ALL}")
                
        elif choice == "5":
            # Статистика
            count = blacklist.get_blacklist_count()
            print(f"\n{Fore.CYAN}📊 Статистика черного списка:{Style.RESET_ALL}")
            print(f"   Всего монет в черном списке: {count}")
            print(f"   Файл: coin_blacklist.json")
            
        elif choice == "6":
            # Очистить черный список
            confirm = input(f"{Fore.RED}⚠️ Вы уверены, что хотите очистить черный список? (yes/no): {Style.RESET_ALL}").strip().lower()
            if confirm == "yes":
                blacklist.clear_blacklist()
            else:
                print(f"{Fore.YELLOW}❌ Отменено{Style.RESET_ALL}")
                
        elif choice == "7":
            # Выход
            print(f"{Fore.GREEN}👋 До свидания!{Style.RESET_ALL}")
            break
            
        else:
            print(f"{Fore.RED}❌ Неверный выбор!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()



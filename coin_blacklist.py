#!/usr/bin/env python3
"""
Черный список монет для арбитражного монитора
Исключает нереалистичные и проблемные токены
"""

from config import BLACKLIST_FILE

class CoinBlacklist:
    """Класс для управления черным списком монет"""
    
    def __init__(self):
        self.blacklist_file = BLACKLIST_FILE
        self.blacklisted_coins = set()
        self.load_blacklist()
    
    def load_blacklist(self):
        """Загружает черный список из файла"""
        import json
        import os
        
        try:
            if os.path.exists(self.blacklist_file):
                with open(self.blacklist_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.blacklisted_coins = set(data.get('blacklisted_coins', []))
                    print(f"✅ Загружено {len(self.blacklisted_coins)} монет в черном списке")
            else:
                # Создаем начальный черный список
                self.create_initial_blacklist()
        except Exception as e:
            print(f"❌ Ошибка загрузки черного списка: {e}")
            self.blacklisted_coins = set()
    
    def save_blacklist(self):
        """Сохраняет черный список в файл"""
        import json
        from datetime import datetime
        
        try:
            data = {
                'blacklisted_coins': list(self.blacklisted_coins),
                'last_updated': datetime.now().isoformat(),
                'total_count': len(self.blacklisted_coins)
            }
            with open(self.blacklist_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Сохранено {len(self.blacklisted_coins)} монет в черном списке")
        except Exception as e:
            print(f"❌ Ошибка сохранения черного списка: {e}")
    
    def create_initial_blacklist(self):
        """Создает начальный черный список проблемных монет"""
        # Монеты с нереалистичными ценами или объемами
        initial_blacklist = {
            # Мем-коины с нереалистичными ценами
            'GMEUSDT', 'ALPACAUSDT', 'LOOMUSDT', 'TRUMPUSDT', 'RIFUSDT',
            'STRAXUSDT', 'XEMUSDT', 'DORAUSDT', 'NULSUSDT', 'GLMRUSDT',
            'REEFUSDT', 'MDTUSDT', 'RADUSDT', 'DGBUSDT', 'IDEXUSDT',
            'ORBSUSDT', 'BLZUSDT', 'SNTUSDT', 'ZKUSDT', 'MEMEFIUSDT',
            'LEVERUSDT', 'MLNUSDT', 'NEIROETHUSDT', 'WAVESUSDT', 'BALUSDT',
            'ALPHAUSDT', 'RPLUSDT', 'SCRTUSDT', 'ALLUSDT', 'BADGERUSDT',
            
            # Токены с нулевыми или очень маленькими объемами
            'ZECUSDT', 'OMGUSDT', 'LTCUSDT', 'ADAUSDT', 'DOTUSDT',
            'LINKUSDT', 'UNIUSDT', 'AAVEUSDT', 'SUSHIUSDT', 'COMPUSDT',
            
            # Проблемные токены (слишком волатильные)
            'DOGEUSDT', 'SHIBUSDT', 'PEPEUSDT', 'FLOKIUSDT', 'BONKUSDT',
            'WIFUSDT', 'BOMEUSDT', 'POPCATUSDT', 'MEWUSDT', 'CATUSDT',
            
            # Токены с подозрительными данными
            'USDTUSDT', 'USDCUSDT', 'BUSDUSDT', 'TUSDUSDT', 'DAIUSDT',
            'FRAXUSDT', 'LUSDUSDT', 'SUSDUSDT', 'GUSDUSDT', 'USDPUSDT',
            
            # Токены с очень маленькой капитализацией
            '1INCHUSDT', 'ACHUSDT', 'ADXUSDT', 'AGIXUSDT', 'AKROUSDT',
            'ALICEUSDT', 'ALPHAUSDT', 'ANKRUSDT', 'ANTUSDT', 'API3USDT',
            'ARUSDT', 'ARDRUSDT', 'ARKMUSDT', 'ARPAUSDT', 'ASTRUSDT',
            'ATAUSDT', 'ATOMUSDT', 'AUCTIONUSDT', 'AUDIOUSDT', 'AVAXUSDT',
            'AXSUSDT', 'BADGERUSDT', 'BAKEUSDT', 'BALUSDT', 'BANDUSDT',
            'BATUSDT', 'BCHUSDT', 'BEAMUSDT', 'BELUSDT', 'BICOUSDT',
            'BIFIUSDT', 'BLURUSDT', 'BNBUSDT', 'BNTUSDT', 'BNXUSDT',
            'BONDUSDT', 'BONKUSDT', 'BOMEUSDT', 'BONUSDT', 'BOSONUSDT',
            'BRISEUSDT', 'BSVUSDT', 'BTTUSDT', 'BURGERUSDT', 'C98USDT',
            'CAKEUSDT', 'CELOUSDT', 'CELRUSDT', 'CFXUSDT', 'CHRUSDT',
            'CHZUSDT', 'CITYUSDT', 'CKBUSDT', 'CLVUSDT', 'COMBOUSDT',
            'COMPUSDT', 'COTIUSDT', 'CRVUSDT', 'CTKUSDT', 'CTSIUSDT',
            'CVCUSDT', 'CVXUSDT', 'CYBERUSDT', 'DASHUSDT', 'DATAUSDT',
            'DCRUSDT', 'DEGOUSDT', 'DENTUSDT', 'DEXEUSDT', 'DFUSDT',
            'DGBUSDT', 'DIAUSDT', 'DOCKUSDT', 'DODOUSDT', 'DOGEUSDT',
            'DOTUSDT', 'DREPUSDT', 'DUSKUSDT', 'DYDXUSDT', 'EDUUSDT',
            'EGLDUSDT', 'ELFUSDT', 'ENJUSDT', 'ENSUSDT', 'EOSUSDT',
            'EPXUSDT', 'ETCUSDT', 'ETHUSDT', 'ETHFIUSDT', 'FARMUSDT',
            'FDUSDUSDT', 'FETUSDT', 'FIDAUSDT', 'FILUSDT', 'FISUSDT',
            'FLMUSDT', 'FLOKIUSDT', 'FLOWUSDT', 'FLRUSDT', 'FORTHUSDT',
            'FRONTUSDT', 'FTMUSDT', 'FUNUSDT', 'FXSUSDT', 'GALAUSDT',
            'GALUSDT', 'GASUSDT', 'GFTUSDT', 'GLMRUSDT', 'GLMUSDT',
            'GMTUSDT', 'GMXUSDT', 'GNSUSDT', 'GRTUSDT', 'GSTUSDT',
            'GTCUSDT', 'HBARUSDT', 'HFTUSDT', 'HIFIUSDT', 'HIGHUSDT',
            'HNTUSDT', 'HOOKUSDT', 'HOTUSDT', 'ICPUSDT', 'ICXUSDT',
            'IDUSDT', 'IDEXUSDT', 'ILVUSDT', 'IMXUSDT', 'INJUSDT',
            'IOSTUSDT', 'IOTAUSDT', 'IOTXUSDT', 'JASMYUSDT', 'JSTUSDT',
            'JTOUSDT', 'JUPUSDT', 'KAVAUSDT', 'KEYUSDT', 'KLAYUSDT',
            'KMDUSDT', 'KNCUSDT', 'KSMUSDT', 'LDOUSDT', 'LEVERUSDT',
            'LINAUSDT', 'LINKUSDT', 'LITUSDT', 'LPTUSDT', 'LQTYUSDT',
            'LRCUSDT', 'LSKUSDT', 'LTCUSDT', 'LUNCUSDT', 'LUNAUSDT',
            'MAGICUSDT', 'MANAUSDT', 'MASKUSDT', 'MATICUSDT', 'MAVUSDT',
            'MBLUSDT', 'MDTUSDT', 'MEWUSDT', 'MINAUSDT', 'MKRUSDT',
            'MLNUSDT', 'MOVRUSDT', 'MTLUSDT', 'NEARUSDT', 'NEOUSDT',
            'NFPUSDT', 'NKNUSDT', 'NMRUSDT', 'NTRNUSDT', 'OCEANUSDT',
            'OGNUSDT', 'OMGUSDT', 'ONDOUSDT', 'ONTUSDT', 'OPUSDT',
            'ORDIUSDT', 'OXTUSDT', 'PENDLEUSDT', 'PEOPLEUSDT', 'PEPEUSDT',
            'PERPUSDT', 'PIXELUSDT', 'POLUSDT', 'POLYXUSDT', 'PONDUSDT',
            'POWRUSDT', 'PROMUSDT', 'PSGUSDT', 'PUNDIXUSDT', 'PYTHUSDT',
            'QNTUSDT', 'QTUMUSDT', 'RADUSDT', 'RAREUSDT', 'RDNTUSDT',
            'REEFUSDT', 'RENUSDT', 'RIFUSDT', 'RLCUSDT', 'ROSEUSDT',
            'RPLUSDT', 'RSRUSDT', 'RUNEUSDT', 'RVNUSDT', 'SANDUSDT',
            'SATSUSDT', 'SCUSDT', 'SCRTUSDT', 'SEIUSDT', 'SFPUSDT',
            'SHIBUSDT', 'SKLUSDT', 'SLPUSDT', 'SNTUSDT', 'SNXUSDT',
            'SOLUSDT', 'SPELLUSDT', 'SSVUSDT', 'STEEMUSDT', 'STGUSDT',
            'STMXUSDT', 'STORJUSDT', 'STPTUSDT', 'STRAXUSDT', 'STXUSDT',
            'SUIUSDT', 'SUNUSDT', 'SUSHIUSDT', 'SXPUSDT', 'SYNUSDT',
            'TUSDT', 'TIAUSDT', 'TLMUSDT', 'TNSRUSDT', 'TONUSDT',
            'TRBUSDT', 'TRUUSDT', 'TRUMPUSDT', 'TRXUSDT', 'TWTUSDT',
            'UMAUSDT', 'UNFIUSDT', 'UNIUSDT', 'USTCUSDT', 'UTKUSDT',
            'VANRYUSDT', 'VETUSDT', 'VICUSDT', 'VIDTUSDT', 'VITEUSDT',
            'VOXELUSDT', 'VTHOUSDT', 'WAVESUSDT', 'WAXPUSDT', 'WIFUSDT',
            'WINUSDT', 'WLDUSDT', 'WOOUSDT', 'XAIUSDT', 'XECUSDT',
            'XEMUSDT', 'XLMUSDT', 'XMRUSDT', 'XRPUSDT', 'XTZUSDT',
            'XVGUSDT', 'XVSUSDT', 'YFIUSDT', 'YGGUSDT', 'ZECUSDT',
            'ZENUSDT', 'ZILUSDT', 'ZRXUSDT', '1000PEPEUSDT', '1000SATSUSDT',
            '1000SHIBUSDT', '1000FLOKIUSDT', '1000BONKUSDT', '1000WIFUSDT',
            '1000BOMEUSDT', '1000POPCATUSDT', '1000MEWUSDT', '1000CATUSDT'
        }
        
        self.blacklisted_coins = initial_blacklist
        self.save_blacklist()
        print(f"📝 Создан начальный черный список с {len(self.blacklisted_coins)} монетами")
    
    def is_blacklisted(self, symbol: str) -> bool:
        """Проверяет, находится ли монета в черном списке"""
        return symbol in self.blacklisted_coins
    
    def add_to_blacklist(self, symbol: str):
        """Добавляет монету в черный список"""
        if symbol not in self.blacklisted_coins:
            self.blacklisted_coins.add(symbol)
            self.save_blacklist()
            print(f"➕ Добавлена в черный список: {symbol}")
        else:
            print(f"⚠️ {symbol} уже в черном списке")
    
    def remove_from_blacklist(self, symbol: str):
        """Удаляет монету из черного списка"""
        if symbol in self.blacklisted_coins:
            self.blacklisted_coins.remove(symbol)
            self.save_blacklist()
            print(f"➖ Удалена из черного списка: {symbol}")
        else:
            print(f"⚠️ {symbol} не найдена в черном списке")
    
    def get_blacklist(self) -> set:
        """Возвращает текущий черный список"""
        return self.blacklisted_coins.copy()
    
    def get_blacklist_count(self) -> int:
        """Возвращает количество монет в черном списке"""
        return len(self.blacklisted_coins)
    
    def clear_blacklist(self):
        """Очищает черный список"""
        self.blacklisted_coins.clear()
        self.save_blacklist()
        print("🗑️ Черный список очищен")
    
    def print_blacklist(self, limit: int = 50):
        """Выводит черный список (с ограничением)"""
        print(f"📋 Черный список монет ({len(self.blacklisted_coins)} всего):")
        print("=" * 50)
        
        sorted_coins = sorted(list(self.blacklisted_coins))
        for i, coin in enumerate(sorted_coins[:limit]):
            print(f"{i+1:3d}. {coin}")
        
        if len(sorted_coins) > limit:
            print(f"... и еще {len(sorted_coins) - limit} монет")
        
        print("=" * 50)

def test_blacklist():
    """Тестирует работу черного списка"""
    print("🧪 Тестирование черного списка монет...")
    print("=" * 50)
    
    # Создаем экземпляр черного списка
    blacklist = CoinBlacklist()
    
    # Тестируем проверку монет
    test_coins = ['BTCUSDT', 'ETHUSDT', 'GMEUSDT', 'ALPACAUSDT', 'DOGEUSDT']
    
    print("\n🔍 Проверка монет:")
    for coin in test_coins:
        status = "❌ В черном списке" if blacklist.is_blacklisted(coin) else "✅ Разрешена"
        print(f"   {coin}: {status}")
    
    # Показываем статистику
    print(f"\n📊 Статистика:")
    print(f"   Всего в черном списке: {blacklist.get_blacklist_count()}")
    
    # Показываем первые 20 монет
    print(f"\n📋 Первые 20 монет в черном списке:")
    blacklist.print_blacklist(20)
    
    print("\n✅ Тест завершен!")

if __name__ == "__main__":
    test_blacklist()



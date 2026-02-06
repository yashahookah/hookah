"""
Система обучения на основе контента Telegram каналов
Сохраняет и анализирует информацию для понимания рынка
"""

import json
import os
import re
from datetime import datetime
from collections import defaultdict

class LearningSystem:
    def __init__(self):
        self.knowledge_base_file = 'knowledge_base.json'
        self.market_insights_file = 'market_insights.json'
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Загружает базу знаний"""
        if os.path.exists(self.knowledge_base_file):
            with open(self.knowledge_base_file, 'r', encoding='utf-8') as f:
                self.knowledge_base = json.load(f)
        else:
            self.knowledge_base = {
                'brands': {},
                'products': {},
                'prices': {},
                'events': [],
                'people': {},
                'trends': [],
                'market_changes': []
            }
    
    def save_knowledge_base(self):
        """Сохраняет базу знаний"""
        with open(self.knowledge_base_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_base, f, ensure_ascii=False, indent=2)
    
    def extract_price_info(self, text):
        """Извлекает информацию о ценах из текста"""
        # Паттерны для поиска цен
        price_patterns = [
            r'(\d+)\s*₽',
            r'(\d+)\s*руб',
            r'(\d+)\s*rub',
            r'цена[:\s]+(\d+)',
            r'стоимость[:\s]+(\d+)',
        ]
        
        prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, text.lower())
            prices.extend([int(m) for m in matches if m.isdigit()])
        
        return prices
    
    def learn_from_message(self, channel_name, message):
        """Обучается на основе сообщения"""
        text = message.get('text', '').lower()
        if not text:
            return
        
        # Извлечение информации о брендах (полный список из исторических данных)
        brands = [
            # Российские бренды табака
            'adalya', 'адалия', 'адалья', 'darkside', 'дарксайд', 'ds',
            'musthave', 'мастхейв', 'мх', 'duft', 'дуфт', 'blackburn', 'блэкберн',
            'burn', 'берн', 'satyr', 'сатир', 'element', 'элемент', 'holster', 'холстер',
            'hit', 'h.i.t', 'h i t', 'хит', 'hookain', 'хукаин', 'sebero', 'себеро',
            'sebero classic', 'karma', 'карма', 'spectrum', 'спектрум',
            'overdose', 'overdoze', 'overdoz', 'овердоз', 'jent', 'джент', 'jent cigar',
            'nur', 'нур', 'sarma', 'сарма', 'edelveis', 'эдельвейс', 'nano smoke',
            'нано смоук', 'big maks', 'биг макс', 'bonche', 'бонче', 'chabacco', 'чабакко',
            'trofimoff', 'трофимов', 'трофимофф', 'werkbund', 'веркбунд',
            'antagonist', 'антагонист', 'bezdna', 'бездна', 'big smoke', 'биг смоук', 'doha', 'доха',
            # Международные бренды табака
            'tangiers', 'тангирс', 'тангиерс', 'original by tangiers', 'obt',
            'serbetli', 'сербетли', 'al fakher', 'аль факхер', 'af', 'afzal', 'афзал',
            'nakhla', 'нахла', 'starbuzz', 'старбазз', 'fumari', 'фумари', 'azure', 'азур',
            'social smoke', 'сошиал смоук', 'zomo', 'зомо', 'trifecta', 'трифекта',
            'ugly', 'агли', 'chaos', 'хаос', 'eternal smoke', 'этернал смоук',
            'haze', 'хейз', 'hydro', 'хайдро', 'lavoo', 'лаву', 'mazaya', 'мазая',
            'nirvana', 'нирвана', 'pure', 'пьюр',
            # Бренды кальянов и аксессуаров
            'alpha hookah', 'альфа кальян', 'amy deluxe', 'amira', 'b2 hookah',
            'dsh hookah', 'dsh кальян', 'дш кальян', 'kaloud', 'калуд', 'mig', 'миг',
            'mig hookah', 'mig кальян', 'moze', 'мозе', 'moze hookah', 'moze кальян',
            'oduman', 'одуман', 'regal hookah', 'shishabucks', 'starbuzz hookah',
            'union hookah', 'union', 'юнион кальян', 'wookah', 'aeon', 'эон',
            'mason', 'мейсон', 'hookah john', 'hoob', 'хуб', 'cosmobowl', 'космобоул',
            'kaloud lotus', 'lotus', 'лотос', 'provost', 'stratus', 'samsaris',
            'vitria', 'ignis', 'hmd', 'heat management'
        ]
        for brand in brands:
            # Используем границы слов для точного поиска
            pattern = r'\b' + re.escape(brand) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                if brand not in self.knowledge_base['brands']:
                    self.knowledge_base['brands'][brand] = {
                        'mentions': 0,
                        'contexts': [],
                        'last_seen': None
                    }
                self.knowledge_base['brands'][brand]['mentions'] += 1
                self.knowledge_base['brands'][brand]['last_seen'] = datetime.now().isoformat()
                # Сохраняем контекст (первые 200 символов)
                context = message.get('text', '')[:200]
                if context not in self.knowledge_base['brands'][brand]['contexts']:
                    self.knowledge_base['brands'][brand]['contexts'].append(context)
                    # Ограничиваем количество контекстов
                    if len(self.knowledge_base['brands'][brand]['contexts']) > 10:
                        self.knowledge_base['brands'][brand]['contexts'].pop(0)
        
        # Извлечение цен
        prices = self.extract_price_info(message.get('text', ''))
        if prices:
            product_keywords = ['табак', 'уголь', 'кальян', '50г', '50гр', '20г', '20гр']
            for keyword in product_keywords:
                if keyword in text:
                    if keyword not in self.knowledge_base['prices']:
                        self.knowledge_base['prices'][keyword] = []
                    self.knowledge_base['prices'][keyword].extend(prices)
                    # Оставляем только последние 50 цен
                    if len(self.knowledge_base['prices'][keyword]) > 50:
                        self.knowledge_base['prices'][keyword] = self.knowledge_base['prices'][keyword][-50:]
        
        # Извлечение событий
        event_keywords = ['выставка', 'фестиваль', 'конкурс', 'мероприятие', 'event']
        for keyword in event_keywords:
            if keyword in text:
                event_info = {
                    'date': datetime.now().isoformat(),
                    'channel': channel_name,
                    'text': message.get('text', '')[:300],
                    'time': message.get('time_str', '')
                }
                self.knowledge_base['events'].append(event_info)
                # Оставляем только последние 100 событий
                if len(self.knowledge_base['events']) > 100:
                    self.knowledge_base['events'] = self.knowledge_base['events'][-100:]
        
        # Сохранение трендов
        if len(text) > 20:  # Только значимые сообщения
            trend_entry = {
                'date': datetime.now().isoformat(),
                'channel': channel_name,
                'text': text[:200],
                'views': message.get('views', 0)
            }
            self.knowledge_base['trends'].append(trend_entry)
            # Оставляем только последние 500 трендов
            if len(self.knowledge_base['trends']) > 500:
                self.knowledge_base['trends'] = self.knowledge_base['trends'][-500:]
    
    def get_market_insights(self):
        """Получает инсайты о рынке на основе накопленных знаний"""
        insights = []
        
        # Анализ цен (упрощённо — без сложных средних)
        if self.knowledge_base['prices']:
            insights.append("💰 **Ценообразование на рынке (по накопленным данным):**\n")
            # Группируем близкие ключи вручную
            groups = {
                'кальян': ['кальян'],
                'табак': ['табак'],
                'табак 50 г': ['50г', '50гр'],
                'табак 20 г': ['20г', '20гр'],
                'уголь': ['уголь'],
            }

            for label, keys in groups.items():
                all_prices = []
                for key in keys:
                    all_prices.extend(self.knowledge_base['prices'].get(key, []))
                # Фильтруем нули и совсем странные значения
                all_prices = [p for p in all_prices if p > 0]
                if not all_prices:
                    continue

                min_price = min(all_prices)
                max_price = max(all_prices)
                # Берём «типовой уровень» как медиану
                sorted_p = sorted(all_prices)
                mid = len(sorted_p) // 2
                median = (sorted_p[mid] if len(sorted_p) % 2 == 1 else (sorted_p[mid - 1] + sorted_p[mid]) / 2)

                insights.append(
                    f"  • {label}: чаще всего в районе ~{median:.0f}₽, диапазон от {min_price}₽ до {max_price}₽\n"
                )
            insights.append("")  # Пустая строка после блока цен
        
        # Анализ брендов
        if self.knowledge_base['brands']:
            insights.append("🏷️ **Активность брендов:**\n")
            sorted_brands = sorted(
                self.knowledge_base['brands'].items(),
                key=lambda x: x[1]['mentions'],
                reverse=True
            )[:5]
            for brand, data in sorted_brands:
                insights.append(f"  • {brand.title()}: {data['mentions']} упоминаний\n")
            insights.append("")  # Пустая строка после блока брендов
        
        # Ближайшие события
        recent_events = [e for e in self.knowledge_base['events'] 
                        if datetime.fromisoformat(e['date']).date() >= datetime.now().date()]
        if recent_events:
            insights.append("📅 **Ближайшие события:**\n")
            for event in recent_events[:3]:
                # Обрезаем текст и добавляем перенос строки
                event_text = event['text'][:150].strip()
                if len(event['text']) > 150:
                    event_text += "..."
                insights.append(f"  • [{event['channel']}] {event_text}\n")
            insights.append("")  # Пустая строка после блока событий
        
        return "".join(insights) if insights else "Пока недостаточно данных для инсайтов"
    
    def process_messages(self, messages_by_channel):
        """Обрабатывает все сообщения для обучения"""
        for channel_name, messages in messages_by_channel.items():
            for message in messages:
                self.learn_from_message(channel_name, message)
        
        self.save_knowledge_base()

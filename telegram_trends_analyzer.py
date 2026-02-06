"""
Анализатор трендов для Telegram каналов кальянной индустрии
"""

import re
from collections import Counter
from datetime import datetime, timedelta
import json
import os

class TrendsAnalyzer:
    def __init__(self):
        self.keywords_categories = {
            'brands': [
                # Основные российские бренды табака
                'adalya', 'адалия', 'адалья',
                'darkside', 'дарксайд', 'ds',
                'musthave', 'мастхейв', 'мх',
                'duft', 'дуфт',
                'blackburn', 'блэкберн',
                'burn', 'берн',
                'satyr', 'сатир',
                'element', 'элемент',
                'holster', 'холстер',
                'hit', 'h.i.t', 'h i t', 'хит',
                'hookain', 'хукаин',
                'sebero', 'себеро', 'sebero classic',
                'karma', 'карма',
                'spectrum', 'спектрум',
                'overdose', 'overdoze', 'overdoz', 'овердоз',
                'overdose hookah', 'overdoze hookah', 'overdoz hookah',
                'jent', 'джент', 'jent cigar',
                'nur', 'нур',
                'sarma', 'сарма',
                'edelveis', 'эдельвейс',
                'nano smoke', 'нано смоук',
                'big maks', 'биг макс',
                'bonche', 'бонче',
                'chabacco', 'чабакко',
                'trofimoff', 'трофимов', 'трофимофф', "troffimov's", "troffimov", "trofimoff's", "трофимова",
                'werkbund', 'веркбунд',
                'antagonist', 'антагонист',
                'bezdna', 'бездна',
                'big smoke', 'биг смоук',
                'doha', 'доха',
                
                # Международные бренды табака
                'tangiers', 'original by tangiers', 'obt', 'serbetli', 'al fakher', 'afzal',
                'nakhla', 'starbuzz', 'fumari', 'azure', 'social smoke', 'zomo',
                'adalya', 'trifecta', 'ugly', 'azure', 'chaos', 'eternal smoke',
                'haze', 'hydro', 'lavoo', 'mazaya', 'nirvana', 'pure', 'social smoke',
                'starbuzz', 'tangiers', 'trifecta', 'ugly', 'zomo',
                
                # Бренды кальянов и аксессуаров
                'alpha hookah', 'amy deluxe', 'amira', 'b2 hookah', 'dsh hookah',
                'kaloud', 'mig', 'moze', 'oduman', 'regal hookah', 'shishabucks',
                'starbuzz hookah', 'starbuzz hookahs', 'starbuzz stems', 'union hookah',
                'wookah', 'aeon', 'mason', 'hookah john', 'kaloud lotus', 'provost',
                'stratus', 'samsaris', 'vitria', 'ignis', 'hmd', 'heat management',
                
                # Российские производители кальянов
                'dsh', 'dsh hookah', 'dsh кальян', 'дш кальян',
                'mig', 'mig hookah', 'mig кальян', 'миг',
                'moze', 'moze hookah', 'moze кальян', 'мозе',
                'union', 'union hookah', 'юнион кальян',
                'aeon', 'aeon hookah', 'эон',
                'mason', 'mason hookah', 'мейсон',
                'hoob', 'хуб',
                'cosmobowl', 'космобоул',
            ],
            # Продукты - конкретные названия, а не общие категории
            # Исключаем общие слова типа "кальян", "табак" - они не являются продуктами
            'products': [
                # Конкретные модели и названия продуктов
                'lotus', 'provost', 'stratus', 'samsaris', 'vitria', 'ignis', 'hmd',
                'kaloud lotus', 'kaloud provost', 'kaloud stratus',
                'aluminum foil', 'фольга', 'foil',
                'кокосовый уголь', 'coconut coals', 'coco coals',
                # Конкретные модели кальянов (если упоминаются по названию)
                'alpha', 'amy', 'amira', 'b2', 'oduman', 'regal', 'wookah', 'aeon', 'mason',
                # Конкретные аксессуары по названию
                'vase', 'base', 'stem', 'downstem', 'tray', 'grommet',
            ],
            'flavors': ['яблоко', 'мята', 'арбуз', 'дыня', 'манго', 'клубника', 'вишня', 
                       'персик', 'лимон', 'лайм', 'кола', 'карамель', 'ваниль', 'шоколад',
                       'apple', 'mint', 'watermelon', 'melon', 'mango', 'strawberry'],
            'events': ['выставка', 'фестиваль', 'конкурс', 'мероприятие', 'event', 'festival',
                      'exhibition', 'contest', 'competition'],
            'business': ['цена', 'скидка', 'акция', 'распродажа', 'новинка', 'запуск', 
                        'price', 'sale', 'discount', 'new', 'launch', 'release'],
            'locations': ['москва', 'спб', 'питер', 'россия', 'russia', 'moscow', 'spb'],
            'people': ['мастер', 'эксперт', 'обзор', 'review', 'master', 'expert'],
        }
        
        self.trending_topics_file = 'trending_topics.json'
        self.load_trending_topics()
    
    def load_trending_topics(self):
        """Загружает историю трендов"""
        if os.path.exists(self.trending_topics_file):
            with open(self.trending_topics_file, 'r', encoding='utf-8') as f:
                self.trending_topics = json.load(f)
        else:
            self.trending_topics = {}
    
    def save_trending_topics(self):
        """Сохраняет историю трендов"""
        with open(self.trending_topics_file, 'w', encoding='utf-8') as f:
            json.dump(self.trending_topics, f, ensure_ascii=False, indent=2)
    
    def extract_keywords(self, text):
        """Извлекает ключевые слова из текста"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_keywords = []
        
        # Слова из названий каналов, которые не должны считаться брендами
        channel_words = ['live', 'expert', 'professional', 'group', 'crew', 'trip', 'says', 
                        'hookah', 'russian', 'smoky', 'big', 'smoke', 'kn', 'mt', 'mveche',
                        'fedotov', 'savinov', 'ivan', 'kalyan']
        
        # Поиск по известным брендам
        for category, keywords in self.keywords_categories.items():
            for keyword in keywords:
                # Пропускаем слова из названий каналов для категории brands
                if category == 'brands' and keyword.lower() in channel_words:
                    continue
                # Используем границы слов для точного поиска
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    found_keywords.append((category, keyword))
        
        # Дополнительный поиск брендов по паттернам (заглавные буквы, аббревиатуры)
        # Исключаем слова из названий каналов и общие слова
        exclude_words = ['the', 'and', 'or', 'for', 'with', 'this', 'that', 'from', 'into',
                        'hookah', 'shisha', 'tobacco', 'coals', 'bowl', 'hose', 'review',
                        'master', 'expert', 'обзор', 'мастер', 'эксперт']
        
        brand_patterns = [
            r'\b[A-Z]{2,}\b',  # Аббревиатуры типа HIT, OBT, DS
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Названия типа "Original By Tangiers"
        ]
        
        for pattern in brand_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                potential_brand = match.group().lower()
                # Исключаем общие слова и слова из названий каналов
                if (potential_brand not in exclude_words and 
                    potential_brand not in channel_words and 
                    len(potential_brand) >= 2):
                    # Проверяем, не найден ли уже этот бренд
                    if not any(kw[1] == potential_brand for kw in found_keywords if kw[0] == 'brands'):
                        found_keywords.append(('brands', potential_brand))
        
        return found_keywords
    
    def analyze_messages(self, messages_by_channel):
        """Анализирует сообщения и выявляет тренды"""
        all_keywords = []
        brand_mentions = Counter()
        product_mentions = Counter()
        flavor_mentions = Counter()
        event_mentions = []
        business_mentions = []
        
        # Слова из названий каналов, которые не должны считаться брендами
        channel_words = ['live', 'expert', 'professional', 'group', 'crew', 'trip', 'says', 
                        'hookah', 'russian', 'smoky', 'big', 'smoke', 'kn', 'mt', 'mveche',
                        'fedotov', 'savinov', 'ivan', 'kalyan']
        
        for channel_name, messages in messages_by_channel.items():
            for msg in messages:
                text = msg.get('text', '')
                if not text:
                    continue
                
                keywords = self.extract_keywords(text)
                all_keywords.extend(keywords)
                
                # Подсчет упоминаний
                for category, keyword in keywords:
                    if category == 'brands':
                        # Нормализуем название бренда (приводим к единому виду)
                        normalized_brand = keyword.lower().strip()
                        # Пропускаем если это слово из названия канала
                        if normalized_brand not in channel_words:
                            brand_mentions[normalized_brand] += 1
                    elif category == 'products':
                        # Продукты считаем только если это конкретные названия
                        product_mentions[keyword] += 1
                    elif category == 'flavors':
                        flavor_mentions[keyword] += 1
                    elif category == 'events':
                        event_mentions.append({
                            'text': text[:100],
                            'channel': channel_name,
                            'time': msg.get('time_str', '')
                        })
                    elif category == 'business':
                        business_mentions.append({
                            'text': text[:100],
                            'channel': channel_name,
                            'time': msg.get('time_str', '')
                        })
        
        # Определяем топ-тренды
        # Фильтруем бренды - убираем слова из названий каналов
        filtered_brands = {k: v for k, v in brand_mentions.items() 
                          if k.lower() not in channel_words}
        top_brands = Counter(filtered_brands).most_common(10)
        
        # Фильтруем продукты - исключаем общие категории
        # Общие слова, которые не являются конкретными продуктами
        general_product_words = ['табак', 'tobacco', 'кальян', 'hookah', 'shisha', 
                                'уголь', 'coals', 'чаша', 'bowl', 'шланг', 'hose',
                                'мундштук', 'колба', 'vase', 'base']
        filtered_products = {k: v for k, v in product_mentions.items() 
                            if k.lower() not in general_product_words}
        top_products = Counter(filtered_products).most_common(10) if filtered_products else []
        top_flavors = flavor_mentions.most_common(5)
        
        # Сохраняем тренды
        today = datetime.now().strftime('%Y-%m-%d')
        self.trending_topics[today] = {
            'brands': dict(top_brands),
            'products': dict(top_products),
            'flavors': dict(top_flavors),
            'events_count': len(event_mentions),
            'business_updates': len(business_mentions)
        }
        self.save_trending_topics()
        
        return {
            'top_brands': top_brands,
            'top_products': top_products,
            'top_flavors': top_flavors,
            'events': event_mentions[:5],  # Топ-5 событий
            'business_updates': business_mentions[:5],  # Топ-5 бизнес-обновлений
            'total_keywords': len(all_keywords)
        }
    
    def format_trends_summary(self, trends_data):
        """Форматирует сводку по трендам в читаемом формате"""
        # Этот раздел теперь интегрирован в format_analytics_report
        # Оставляем пустым, чтобы избежать дублирования
        return ""

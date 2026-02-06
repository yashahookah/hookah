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
                'trofimoff', 'трофимов', 'трофимофф',
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
            'products': ['табак', 'уголь', 'кальян', 'чаша', 'шланг', 'мундштук', 'колба', 
                        'hookah', 'shisha', 'tobacco', 'coals', 'bowl', 'hose'],
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
        
        # Поиск по известным брендам
        for category, keywords in self.keywords_categories.items():
            for keyword in keywords:
                # Используем границы слов для точного поиска
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    found_keywords.append((category, keyword))
        
        # Дополнительный поиск брендов по паттернам (заглавные буквы, аббревиатуры)
        brand_patterns = [
            r'\b[A-Z]{2,}\b',  # Аббревиатуры типа HIT, OBT, DS
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Названия типа "Original By Tangiers"
        ]
        
        for pattern in brand_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                potential_brand = match.group().lower()
                # Исключаем общие слова
                exclude_words = ['the', 'and', 'or', 'for', 'with', 'this', 'that', 'from', 'into']
                if potential_brand not in exclude_words and len(potential_brand) >= 2:
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
                        brand_mentions[keyword] += 1
                    elif category == 'products':
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
        top_brands = brand_mentions.most_common(5)
        top_products = product_mentions.most_common(5)
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
        """Форматирует сводку по трендам"""
        summary = "📈 **АНАЛИЗ ТРЕНДОВ ЗА ДЕНЬ**\n\n"
        
        if trends_data.get('top_brands'):
            summary += "🏷️ **Топ упоминаний брендов:**\n\n"
            for brand, count in trends_data['top_brands']:
                summary += f"  • {brand.title()}: {count} раз\n"
            summary += "\n"
        
        if trends_data.get('top_products'):
            summary += "🛍️ **Топ упоминаний продуктов:**\n\n"
            for product, count in trends_data['top_products']:
                summary += f"  • {product.title()}: {count} раз\n"
            summary += "\n"
        
        if trends_data.get('top_flavors'):
            summary += "🍓 **Топ упоминаний вкусов:**\n\n"
            for flavor, count in trends_data['top_flavors']:
                summary += f"  • {flavor.title()}: {count} раз\n"
            summary += "\n"
        
        if trends_data.get('events'):
            summary += "📅 **События и мероприятия:**\n\n"
            for event in trends_data['events']:
                summary += f"  • [{event['channel']}] {event['text']}\n"
            summary += "\n"
        
        if trends_data.get('business_updates'):
            summary += "💼 **Бизнес-обновления:**\n\n"
            for update in trends_data['business_updates']:
                summary += f"  • [{update['channel']}] {update['text']}\n"
            summary += "\n"
        
        summary += f"📊 Всего ключевых упоминаний: {trends_data.get('total_keywords', 0)}\n"
        
        return summary

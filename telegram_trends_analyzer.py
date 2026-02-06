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
            'brands': ['adalya', 'serbetli', 'al fakher', 'darkside', 'musthave', 'tangiers', 
                      'starbuzz', 'fumari', 'azure', 'element', 'holster'],
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
        
        for category, keywords in self.keywords_categories.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_keywords.append((category, keyword))
        
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

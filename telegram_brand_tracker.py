"""
Специальное отслеживание упоминаний брендов Adalya и Tangiers
"""

import re
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json
import os

class BrandTracker:
    def __init__(self):
        # Варианты написания Adalya
        self.adalya_patterns = [
            r'\b[Аа]дал[ья]я\b',
            r'\b[Аа]далька\b',
            r'\b[Аа]дал[ья]\b',
            r'\b[Аа]далия\b',
            r'\b[Аа]дал[ья]и\b',
            r'\bAdalya\b',
            r'\bADALYA\b',
            r'\badalya\b',
        ]
        
        # Варианты написания Tangiers
        self.tangiers_patterns = [
            r'\bTangiers\b',
            r'\bTANGIERS\b',
            r'\btangiers\b',
            r'\b[Тт]ангирс\b',
            r'\b[Тт]ангиерс\b',
            r'\b[Тт]ангир[зс]\b',
            r'\bOriginal By Tangiers\b',
            r'\bOriginal by Tangiers\b',
            r'\bOBT\b',  # Original By Tangiers
        ]
        
        self.brand_mentions_file = 'brand_mentions.json'
        self.load_brand_mentions()
    
    def load_brand_mentions(self):
        """Загружает историю упоминаний брендов"""
        if os.path.exists(self.brand_mentions_file):
            with open(self.brand_mentions_file, 'r', encoding='utf-8') as f:
                self.brand_mentions = json.load(f)
        else:
            self.brand_mentions = {
                'adalya': [],
                'tangiers': [],
                'statistics': {
                    'adalya': {'total': 0, 'by_channel': {}, 'by_date': {}},
                    'tangiers': {'total': 0, 'by_channel': {}, 'by_date': {}}
                }
            }
    
    def save_brand_mentions(self):
        """Сохраняет историю упоминаний"""
        with open(self.brand_mentions_file, 'w', encoding='utf-8') as f:
            json.dump(self.brand_mentions, f, ensure_ascii=False, indent=2)
    
    def find_brand_mentions(self, text, channel_name, message_data):
        """Находит упоминания брендов в тексте"""
        mentions = {
            'adalya': [],
            'tangiers': []
        }
        
        if not text:
            return mentions
        
        # Поиск Adalya
        for pattern in self.adalya_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end]
                
                mentions['adalya'].append({
                    'match': match.group(),
                    'context': context,
                    'channel': channel_name,
                    'date': message_data.get('date', datetime.now()).isoformat() if isinstance(message_data.get('date'), datetime) else message_data.get('date'),
                    'time': message_data.get('time_str', ''),
                    'message_text': text[:200],
                    'views': message_data.get('views', 0),
                    'message_id': message_data.get('id')
                })
        
        # Поиск Tangiers
        for pattern in self.tangiers_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 50)
                context = text[context_start:context_end]
                
                brand_type = 'tangiers'
                if 'original' in text.lower() or 'obt' in text.lower():
                    brand_type = 'tangiers_obt'
                
                mentions['tangiers'].append({
                    'match': match.group(),
                    'context': context,
                    'channel': channel_name,
                    'date': message_data.get('date', datetime.now()).isoformat() if isinstance(message_data.get('date'), datetime) else message_data.get('date'),
                    'time': message_data.get('time_str', ''),
                    'message_text': text[:200],
                    'views': message_data.get('views', 0),
                    'message_id': message_data.get('id'),
                    'type': brand_type
                })
        
        return mentions
    
    def process_messages(self, messages_by_channel):
        """Обрабатывает сообщения и собирает упоминания брендов"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        for channel_name, messages in messages_by_channel.items():
            for message in messages:
                text = message.get('text', '')
                if not text:
                    continue
                
                mentions = self.find_brand_mentions(text, channel_name, message)
                
                # Сохраняем упоминания Adalya
                if mentions['adalya']:
                    self.brand_mentions['adalya'].extend(mentions['adalya'])
                    self.brand_mentions['statistics']['adalya']['total'] += len(mentions['adalya'])
                    
                    # Статистика по каналам
                    if channel_name not in self.brand_mentions['statistics']['adalya']['by_channel']:
                        self.brand_mentions['statistics']['adalya']['by_channel'][channel_name] = 0
                    self.brand_mentions['statistics']['adalya']['by_channel'][channel_name] += len(mentions['adalya'])
                    
                    # Статистика по датам
                    if today not in self.brand_mentions['statistics']['adalya']['by_date']:
                        self.brand_mentions['statistics']['adalya']['by_date'][today] = 0
                    self.brand_mentions['statistics']['adalya']['by_date'][today] += len(mentions['adalya'])
                
                # Сохраняем упоминания Tangiers
                if mentions['tangiers']:
                    self.brand_mentions['tangiers'].extend(mentions['tangiers'])
                    self.brand_mentions['statistics']['tangiers']['total'] += len(mentions['tangiers'])
                    
                    # Статистика по каналам
                    if channel_name not in self.brand_mentions['statistics']['tangiers']['by_channel']:
                        self.brand_mentions['statistics']['tangiers']['by_channel'][channel_name] = 0
                    self.brand_mentions['statistics']['tangiers']['by_channel'][channel_name] += len(mentions['tangiers'])
                    
                    # Статистика по датам
                    if today not in self.brand_mentions['statistics']['tangiers']['by_date']:
                        self.brand_mentions['statistics']['tangiers']['by_date'][today] = 0
                    self.brand_mentions['statistics']['tangiers']['by_date'][today] += len(mentions['tangiers'])
        
        # Ограничиваем размер истории (оставляем последние 1000 упоминаний каждого бренда)
        if len(self.brand_mentions['adalya']) > 1000:
            self.brand_mentions['adalya'] = self.brand_mentions['adalya'][-1000:]
        if len(self.brand_mentions['tangiers']) > 1000:
            self.brand_mentions['tangiers'] = self.brand_mentions['tangiers'][-1000:]
        
        self.save_brand_mentions()
    
    def get_today_brand_mentions(self):
        """Получает упоминания брендов за сегодня"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        adalya_today = [
            m for m in self.brand_mentions['adalya']
            if m.get('date', '').startswith(today)
        ]
        
        tangiers_today = [
            m for m in self.brand_mentions['tangiers']
            if m.get('date', '').startswith(today)
        ]
        
        return {
            'adalya': adalya_today,
            'tangiers': tangiers_today
        }
    
    def format_brand_mentions_summary(self, mentions_data):
        """Форматирует сводку по упоминаниям брендов"""
        summary = "🏷️ **ОТСЛЕЖИВАНИЕ БРЕНДОВ**\n\n"
        
        # Adalya
        if mentions_data['adalya']:
            summary += f"📢 **ADALYA** ({len(mentions_data['adalya'])} упоминаний сегодня)\n\n"
            
            # Группируем по каналам
            by_channel = defaultdict(list)
            for mention in mentions_data['adalya']:
                by_channel[mention['channel']].append(mention)
            
            for channel, channel_mentions in by_channel.items():
                summary += f"  📡 **{channel}** ({len(channel_mentions)} упоминаний):\n\n"
                for mention in channel_mentions[:3]:  # Показываем до 3 примеров
                    summary += f"    • {mention['time']}: {mention['context'][:80]}...\n"
                if len(channel_mentions) > 3:
                    summary += f"    ... и еще {len(channel_mentions) - 3} упоминаний\n"
                summary += "\n"
        else:
            summary += "📢 **ADALYA**: Нет упоминаний за сегодня\n\n"
        
        # Tangiers
        if mentions_data['tangiers']:
            summary += f"📢 **TANGIERS** ({len(mentions_data['tangiers'])} упоминаний сегодня)\n\n"
            
            # Группируем по каналам
            by_channel = defaultdict(list)
            for mention in mentions_data['tangiers']:
                by_channel[mention['channel']].append(mention)
            
            for channel, channel_mentions in by_channel.items():
                summary += f"  📡 **{channel}** ({len(channel_mentions)} упоминаний):\n\n"
                for mention in channel_mentions[:3]:
                    summary += f"    • {mention['time']}: {mention['context'][:80]}...\n"
                if len(channel_mentions) > 3:
                    summary += f"    ... и еще {len(channel_mentions) - 3} упоминаний\n"
                summary += "\n"
        else:
            summary += "📢 **TANGIERS**: Нет упоминаний за сегодня\n\n"
        
        return summary

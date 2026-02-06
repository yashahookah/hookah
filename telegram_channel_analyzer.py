#!/usr/bin/env python3
"""
Анализатор Telegram канала Adalya LIVE
Получает историю сообщений за период 01.01.2025 - 01.01.2026
"""

import asyncio
import json
from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Dict, Any
import csv

try:
    from telethon import TelegramClient
    from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, MessageMediaWebPage
except ImportError:
    print("Установите telethon: pip install telethon")
    exit(1)


class TelegramChannelAnalyzer:
    def __init__(self, api_id: str, api_hash: str, channel_username: str):
        """
        Инициализация анализатора
        
        Args:
            api_id: Telegram API ID (получить на https://my.telegram.org)
            api_hash: Telegram API Hash
            channel_username: Username канала (например, 'adalya_live')
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.channel_username = channel_username
        self.client = None
        
    async def connect(self, phone=None):
        """Подключение к Telegram"""
        self.client = TelegramClient('session_adalya', self.api_id, self.api_hash)
        if phone:
            await self.client.start(phone=phone)
        else:
            await self.client.start()
        print("✓ Подключено к Telegram")
        
    async def get_messages(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Получение сообщений за период
        
        Args:
            start_date: Начальная дата
            end_date: Конечная дата
            
        Returns:
            Список сообщений с метаданными
        """
        from pytz import UTC
        
        # Преобразуем даты в UTC timezone-aware если они naive
        if start_date.tzinfo is None:
            start_date = UTC.localize(start_date)
        if end_date.tzinfo is None:
            end_date = UTC.localize(end_date)
        
        messages_data = []
        
        print(f"📥 Загрузка сообщений с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}...")
        
        async for message in self.client.iter_messages(
            self.channel_username,
            offset_date=end_date,
            reverse=False
        ):
            if message.date < start_date:
                break
                
            if message.date <= end_date:
                msg_data = {
                    'id': message.id,
                    'date': message.date.isoformat(),
                    'text': message.text or message.raw_text or '',
                    'views': getattr(message, 'views', 0) or 0,
                    'forwards': getattr(message, 'forwards', 0) or 0,
                    'reactions': self._get_reactions(message),
                    'media_type': self._get_media_type(message),
                    'has_media': message.media is not None,
                    'is_reply': message.reply_to is not None,
                    'edit_date': message.edit_date.isoformat() if message.edit_date else None,
                }
                messages_data.append(msg_data)
                
                if len(messages_data) % 50 == 0:
                    print(f"  Загружено {len(messages_data)} сообщений...")
        
        print(f"✓ Загружено всего {len(messages_data)} сообщений")
        return messages_data
    
    def _get_media_type(self, message) -> str:
        """Определение типа медиа"""
        if not message.media:
            return 'text'
        
        if isinstance(message.media, MessageMediaPhoto):
            return 'photo'
        elif isinstance(message.media, MessageMediaDocument):
            if message.media.document:
                mime_type = message.media.document.mime_type or ''
                if 'video' in mime_type:
                    return 'video'
                elif 'audio' in mime_type or 'voice' in mime_type:
                    return 'audio'
                else:
                    return 'document'
        elif isinstance(message.media, MessageMediaWebPage):
            return 'webpage'
        
        return 'other'
    
    def _get_reactions(self, message) -> Dict[str, int]:
        """Получение реакций на сообщение"""
        reactions = {}
        if hasattr(message, 'reactions') and message.reactions:
            for reaction in message.reactions.results:
                emoji = reaction.reaction.emoticon if hasattr(reaction.reaction, 'emoticon') else str(reaction.reaction)
                reactions[emoji] = reaction.count
        return reactions
    
    def analyze(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Анализ сообщений
        
        Args:
            messages: Список сообщений
            
        Returns:
            Словарь с аналитикой
        """
        if not messages:
            return {"error": "Нет сообщений для анализа"}
        
        total_messages = len(messages)
        
        # Статистика по типам медиа
        media_types = defaultdict(int)
        for msg in messages:
            media_types[msg['media_type']] += 1
        
        # Статистика по просмотрам
        views_data = [msg['views'] for msg in messages if msg['views'] > 0]
        avg_views = sum(views_data) / len(views_data) if views_data else 0
        max_views = max(views_data) if views_data else 0
        min_views = min(views_data) if views_data else 0
        
        # Статистика по датам
        messages_by_month = defaultdict(int)
        messages_by_weekday = defaultdict(int)
        
        for msg in messages:
            date = datetime.fromisoformat(msg['date'])
            month_key = date.strftime('%Y-%m')
            weekday = date.strftime('%A')
            messages_by_month[month_key] += 1
            messages_by_weekday[weekday] += 1
        
        # Топ сообщений по просмотрам
        top_messages = sorted(
            [msg for msg in messages if msg['views'] > 0],
            key=lambda x: x['views'],
            reverse=True
        )[:10]
        
        # Статистика по форвардам
        forwards_data = [msg['forwards'] for msg in messages if msg['forwards'] > 0]
        avg_forwards = sum(forwards_data) / len(forwards_data) if forwards_data else 0
        
        # Сообщения с реакциями
        messages_with_reactions = sum(1 for msg in messages if msg['reactions'])
        
        analysis = {
            'period': {
                'start': messages[-1]['date'] if messages else None,
                'end': messages[0]['date'] if messages else None,
            },
            'total_messages': total_messages,
            'media_types': dict(media_types),
            'views': {
                'average': round(avg_views, 2),
                'max': max_views,
                'min': min_views,
                'total': sum(views_data),
            },
            'forwards': {
                'average': round(avg_forwards, 2),
                'total': sum(forwards_data),
            },
            'messages_by_month': dict(messages_by_month),
            'messages_by_weekday': dict(messages_by_weekday),
            'top_messages': [
                {
                    'id': msg['id'],
                    'date': msg['date'],
                    'views': msg['views'],
                    'text_preview': msg['text'][:100] if msg['text'] else '',
                    'media_type': msg['media_type'],
                }
                for msg in top_messages
            ],
            'engagement': {
                'messages_with_reactions': messages_with_reactions,
                'reaction_rate': round(messages_with_reactions / total_messages * 100, 2) if total_messages > 0 else 0,
            }
        }
        
        return analysis
    
    def save_results(self, messages: List[Dict[str, Any]], analysis: Dict[str, Any], output_dir: str = '.'):
        """Сохранение результатов анализа"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Сохранение всех сообщений в JSON
        messages_file = f"{output_dir}/messages_{timestamp}.json"
        with open(messages_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        print(f"✓ Сохранены сообщения: {messages_file}")
        
        # Сохранение анализа в JSON
        analysis_file = f"{output_dir}/analysis_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"✓ Сохранен анализ: {analysis_file}")
        
        # Сохранение сообщений в CSV
        csv_file = f"{output_dir}/messages_{timestamp}.csv"
        if messages:
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=messages[0].keys())
                writer.writeheader()
                writer.writerows(messages)
            print(f"✓ Сохранены сообщения в CSV: {csv_file}")
        
        return messages_file, analysis_file, csv_file
    
    def print_report(self, analysis: Dict[str, Any]):
        """Вывод отчета в консоль"""
        print("\n" + "="*60)
        print("📊 ОТЧЕТ ПО АНАЛИЗУ КАНАЛА ADALYA LIVE")
        print("="*60)
        
        print(f"\n📅 Период: {analysis['period']['start']} - {analysis['period']['end']}")
        print(f"📝 Всего сообщений: {analysis['total_messages']}")
        
        print(f"\n📊 Типы контента:")
        for media_type, count in analysis['media_types'].items():
            percentage = count / analysis['total_messages'] * 100
            print(f"  • {media_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n👁️ Просмотры:")
        print(f"  • Среднее: {analysis['views']['average']:.0f}")
        print(f"  • Максимум: {analysis['views']['max']}")
        print(f"  • Минимум: {analysis['views']['min']}")
        print(f"  • Всего: {analysis['views']['total']}")
        
        print(f"\n📤 Пересылки:")
        print(f"  • Среднее: {analysis['forwards']['average']:.2f}")
        print(f"  • Всего: {analysis['forwards']['total']}")
        
        print(f"\n📅 Активность по месяцам:")
        for month, count in sorted(analysis['messages_by_month'].items()):
            print(f"  • {month}: {count} сообщений")
        
        print(f"\n📅 Активность по дням недели:")
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_names_ru = {
            'Monday': 'Понедельник',
            'Tuesday': 'Вторник',
            'Wednesday': 'Среда',
            'Thursday': 'Четверг',
            'Friday': 'Пятница',
            'Saturday': 'Суббота',
            'Sunday': 'Воскресенье'
        }
        for weekday in weekday_order:
            if weekday in analysis['messages_by_weekday']:
                count = analysis['messages_by_weekday'][weekday]
                print(f"  • {weekday_names_ru[weekday]}: {count} сообщений")
        
        print(f"\n🔥 Топ-10 сообщений по просмотрам:")
        for i, msg in enumerate(analysis['top_messages'], 1):
            preview = msg['text_preview'].replace('\n', ' ')[:60]
            print(f"  {i}. {msg['views']} просмотров | {msg['date'][:10]} | {preview}...")
        
        print(f"\n💬 Вовлеченность:")
        print(f"  • Сообщений с реакциями: {analysis['engagement']['messages_with_reactions']}")
        print(f"  • Процент сообщений с реакциями: {analysis['engagement']['reaction_rate']}%")
        
        print("\n" + "="*60)
    
    async def close(self):
        """Закрытие соединения"""
        if self.client:
            await self.client.disconnect()
            print("✓ Соединение закрыто")


async def main():
    """Основная функция"""
    print("🚀 Запуск анализатора Telegram канала Adalya LIVE\n")
    
    # Получение учетных данных
    print("Для работы нужны учетные данные Telegram API:")
    print("1. Зайдите на https://my.telegram.org")
    print("2. Войдите в свой аккаунт")
    print("3. Перейдите в 'API development tools'")
    print("4. Создайте приложение и получите api_id и api_hash\n")
    
    api_id = input("Введите API ID: ").strip()
    api_hash = input("Введите API Hash: ").strip()
    
    if not api_id or not api_hash:
        print("❌ Ошибка: нужны API ID и API Hash")
        return
    
    # Период анализа
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2026, 1, 1)
    
    # Создание анализатора
    analyzer = TelegramChannelAnalyzer(
        api_id=api_id,
        api_hash=api_hash,
        channel_username='adalya_live'
    )
    
    try:
        # Подключение
        await analyzer.connect()
        
        # Получение сообщений
        messages = await analyzer.get_messages(start_date, end_date)
        
        if not messages:
            print("⚠️ Сообщений за указанный период не найдено")
            return
        
        # Анализ
        print("\n📊 Анализ данных...")
        analysis = analyzer.analyze(messages)
        
        # Вывод отчета
        analyzer.print_report(analysis)
        
        # Сохранение результатов
        print("\n💾 Сохранение результатов...")
        analyzer.save_results(messages, analysis)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await analyzer.close()


if __name__ == '__main__':
    asyncio.run(main())

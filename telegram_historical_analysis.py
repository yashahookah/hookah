#!/usr/bin/env python3
"""
Исторический анализ всех каналов за год для обучения системы
НЕ создает сводку, только анализирует и обучается
"""

import asyncio
from datetime import datetime, timedelta
from telethon import TelegramClient
import os
from dotenv import load_dotenv
from telegram_summary_config import CHANNELS
from telegram_learning_system import LearningSystem
from telegram_brand_tracker import BrandTracker
from telegram_analytics_engine import AnalyticsEngine
from telegram_trends_analyzer import TrendsAnalyzer

load_dotenv()

API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = 'telegram_summary_session'

import pytz
MSK_TZ = pytz.timezone('Europe/Moscow')

# Инициализация систем
learning_system = LearningSystem()
brand_tracker = BrandTracker()
analytics_engine = AnalyticsEngine()
trends_analyzer = TrendsAnalyzer()


async def get_historical_messages(client, channel_username, days_back=365):
    """
    Получает исторические сообщения за указанный период
    """
    messages = []
    end_date = datetime.now(MSK_TZ)
    start_date = end_date - timedelta(days=days_back)
    
    print(f"📚 Загрузка сообщений с {start_date.strftime('%Y-%m-%d')} по {end_date.strftime('%Y-%m-%d')}...")
    
    try:
        count = 0
        async for message in client.iter_messages(channel_username, offset_date=end_date):
            msg_date = message.date.astimezone(MSK_TZ)
            
            # Останавливаемся, если достигли начала периода
            if msg_date < start_date:
                break
            
            msg_data = {
                'text': message.text or message.message or '',
                'date': msg_date,
                'time_str': msg_date.strftime('%H:%M'),
                'has_media': bool(message.media),
                'views': getattr(message, 'views', 0),
                'id': message.id
            }
            
            if message.media:
                media_type = type(message.media).__name__
                msg_data['media_type'] = media_type.replace('MessageMedia', '')
            
            messages.append(msg_data)
            count += 1
            
            # Прогресс каждые 100 сообщений
            if count % 100 == 0:
                print(f"  Загружено {count} сообщений...")
        
        print(f"✅ Загружено {count} сообщений из {channel_username}")
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке из {channel_username}: {e}")
    
    return messages


async def analyze_historical_data():
    """
    Анализирует исторические данные за год
    """
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        await client.start()
        
        print("🚀 Начало исторического анализа за год...")
        print("=" * 60)
        
        all_messages_by_channel = {}
        total_messages = 0
        
        # Собираем данные из всех каналов
        for channel_key, channel_config in CHANNELS.items():
            if not channel_config.get('enabled', True):
                continue
            
            print(f"\n📡 Анализ канала: {channel_config['name']} ({channel_config['username']})")
            print("-" * 60)
            
            messages = await get_historical_messages(
                client,
                channel_config['username'],
                days_back=365
            )
            
            all_messages_by_channel[channel_config['name']] = messages
            total_messages += len(messages)
            
            print(f"✅ Обработано {len(messages)} сообщений")
        
        print("\n" + "=" * 60)
        print(f"📊 Всего собрано: {total_messages} сообщений из {len(all_messages_by_channel)} каналов")
        print("=" * 60)
        
        # Обработка данных для обучения
        print("\n🧠 Обучение системы на исторических данных...")
        
        # Разбиваем на батчи для обработки (чтобы не перегружать память)
        batch_size = 1000
        processed = 0
        
        for channel_name, messages in all_messages_by_channel.items():
            print(f"\n📚 Обработка {channel_name}...")
            
            # Обрабатываем батчами
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i+batch_size]
                batch_dict = {channel_name: batch}
                
                # Обучение системы
                learning_system.process_messages(batch_dict)
                
                # Отслеживание брендов
                brand_tracker.process_messages(batch_dict)
                
                processed += len(batch)
                print(f"  Обработано {processed}/{total_messages} сообщений...")
        
        print("\n✅ Обучение завершено!")
        
        # Сохраняем аналитику
        print("\n📈 Сохранение аналитических данных...")
        
        # Анализ контента
        content_analysis = analytics_engine.analyze_content(all_messages_by_channel)
        analytics_engine.analytics['content_analysis'] = content_analysis
        analytics_engine.save_analytics()
        
        # Анализ трендов
        trends_data = trends_analyzer.analyze_messages(all_messages_by_channel)
        
        # Статистика по брендам
        print("\n🏷️ Статистика упоминаний брендов:")
        print(f"  Adalya: {brand_tracker.brand_mentions['statistics']['adalya']['total']} упоминаний")
        print(f"  Tangiers: {brand_tracker.brand_mentions['statistics']['tangiers']['total']} упоминаний")
        
        # Топ каналов по упоминаниям Adalya
        if brand_tracker.brand_mentions['statistics']['adalya']['by_channel']:
            print("\n📊 Топ каналов по упоминаниям Adalya:")
            sorted_channels = sorted(
                brand_tracker.brand_mentions['statistics']['adalya']['by_channel'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for channel, count in sorted_channels[:5]:
                print(f"  • {channel}: {count} упоминаний")
        
        # Топ каналов по упоминаниям Tangiers
        if brand_tracker.brand_mentions['statistics']['tangiers']['by_channel']:
            print("\n📊 Топ каналов по упоминаниям Tangiers:")
            sorted_channels = sorted(
                brand_tracker.brand_mentions['statistics']['tangiers']['by_channel'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            for channel, count in sorted_channels[:5]:
                print(f"  • {channel}: {count} упоминаний")
        
        print("\n" + "=" * 60)
        print("✅ Исторический анализ завершен!")
        print("📁 Данные сохранены в:")
        print("   • knowledge_base.json - база знаний")
        print("   • brand_mentions.json - упоминания брендов")
        print("   • analytics_data.json - аналитические данные")
        print("   • trending_topics.json - история трендов")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()


if __name__ == '__main__':
    print("⚠️  ВНИМАНИЕ: Этот скрипт анализирует ВСЕ сообщения за год")
    print("   Это может занять значительное время (30-60 минут)")
    print("   Сводка НЕ будет отправлена, только обучение системы\n")
    
    response = input("Продолжить? (yes/no): ")
    if response.lower() in ['yes', 'y', 'да', 'д']:
        asyncio.run(analyze_historical_data())
    else:
        print("Отменено.")

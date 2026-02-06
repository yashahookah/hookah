#!/usr/bin/env python3
"""
Ежедневная сводка по Telegram каналам кальянной индустрии
Включает анализ трендов, комментарии и систему обучения
Запускается в 10:30 МСК каждый день
"""

import asyncio
import schedule
import time
import re
import sys
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.tl.types import Channel, Message
import os
from dotenv import load_dotenv
from telegram_summary_config import (
    CHANNELS, 
    SCHEDULE_TIME, 
    SUMMARY_RECIPIENT,
    SUMMARY_SETTINGS
)
from telegram_trends_analyzer import TrendsAnalyzer
from telegram_learning_system import LearningSystem
from telegram_analytics_engine import AnalyticsEngine
from telegram_brand_tracker import BrandTracker
from telegram_digest_builder import DigestBuilder

load_dotenv()

# В GitHub Actions переменные берутся из secrets, локально - из .env
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
SESSION_NAME = 'telegram_summary_session'

# Проверка наличия credentials
if not API_ID or not API_HASH:
    print("❌ Ошибка: TELEGRAM_API_ID и TELEGRAM_API_HASH должны быть установлены")
    print("   Локально: создай файл .env с этими переменными")
    print("   GitHub Actions: настрой секреты в Settings → Secrets")
    sys.exit(1)

import pytz
MSK_TZ = pytz.timezone('Europe/Moscow')

# Инициализация систем анализа
trends_analyzer = TrendsAnalyzer()
learning_system = LearningSystem()
analytics_engine = AnalyticsEngine()
brand_tracker = BrandTracker()
digest_builder = DigestBuilder()


async def get_comments(client, channel_username, message_id, max_comments=5):
    """
    Получает комментарии к сообщению
    """
    comments = []
    try:
        # Получаем ответы на сообщение
        async for reply in client.iter_messages(
            channel_username,
            reply_to=message_id,
            limit=max_comments
        ):
            comments.append({
                'text': reply.text or reply.message or '',
                'date': reply.date.astimezone(MSK_TZ),
                'views': getattr(reply, 'views', 0),
                'from_user': getattr(reply.sender, 'username', None) or 'Unknown'
            })
    except Exception as e:
        # Некоторые каналы могут не поддерживать комментарии
        pass
    
    return comments


async def get_today_messages_with_comments(client, channel_username, channel_name):
    """
    Получает сообщения за период «прошлый день + небольшой хвост».
    По умолчанию при запуске в 10:30 МСК берём:
    от 00:00 вчерашнего дня и до текущего момента (сейчас),
    то есть чуть больше, чем 24 часа.
    """
    messages = []
    try:
        # Целевая дата — вчера (начинаем с 00:00 вчера)
        now = datetime.now(MSK_TZ)
        target_date = now - timedelta(days=1)
        day_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        # Верхняя граница — текущий момент (окно > 24 часов)
        day_end = now

        async for message in client.iter_messages(channel_username, offset_date=day_end):
            msg_date = message.date.astimezone(MSK_TZ)

            # Старее начала окна — выходим
            if msg_date < day_start:
                break

            # Берём только сообщения строго внутри окна
            if day_start <= msg_date < day_end:
                msg_data = {
                    'text': message.text or message.message or '',
                    'date': msg_date,
                    'time_str': msg_date.strftime(SUMMARY_SETTINGS['time_format']),
                    'has_media': bool(message.media),
                    'views': getattr(message, 'views', 0),
                    'id': message.id,
                    'replies': getattr(message, 'replies', None)
                }
                
                if message.media and SUMMARY_SETTINGS['include_media_info']:
                    media_type = type(message.media).__name__
                    msg_data['media_type'] = media_type.replace('MessageMedia', '')
                
                # Получаем комментарии, если включено и есть ответы
                if SUMMARY_SETTINGS.get('include_comments', False) and msg_data['replies']:
                    comments = await get_comments(
                        client,
                        channel_username,
                        message.id,
                        SUMMARY_SETTINGS.get('max_comments_per_post', 5)
                    )
                    msg_data['comments'] = comments
                
                messages.append(msg_data)
        
        messages.sort(key=lambda x: x['date'])
        
    except Exception as e:
        print(f"Ошибка при получении сообщений из {channel_username}: {e}")
        return []
    
    return messages


def format_channel_summary_with_comments(channel_name, messages):
    """
    Форматирует сводку по каналу с комментариями
    """
    if not messages:
        return f"📭 **{channel_name}**\nНет новых сообщений за сегодня\n\n"
    
    summary = f"📢 **{channel_name}** ({len(messages)} сообщений)\n\n"
    
    display_messages = messages[-SUMMARY_SETTINGS['max_messages_per_channel']:]
    
    for msg in display_messages:
        time_str = msg['time_str']
        text_preview = msg['text'][:200] + '...' if len(msg['text']) > 200 else msg['text']
        
        meta_parts = []
        if SUMMARY_SETTINGS['include_views'] and msg['views'] > 0:
            meta_parts.append(f"👁 {msg['views']}")
        
        if msg['has_media']:
            media_indicator = f"📎 {msg.get('media_type', 'Media')}"
            meta_parts.append(media_indicator)
        
        meta_str = f" ({', '.join(meta_parts)})" if meta_parts else ""
        
        summary += f"🕐 {time_str}{meta_str}\n"
        
        if text_preview:
            summary += f"{text_preview}\n"
        else:
            summary += "[Медиа без текста]\n"
        
        # Добавляем комментарии, если есть
        if msg.get('comments'):
            summary += f"  💬 Комментарии ({len(msg['comments'])}):\n"
            for comment in msg['comments'][:3]:  # Показываем до 3 комментариев
                comment_text = comment['text'][:100] + '...' if len(comment['text']) > 100 else comment['text']
                summary += f"    • {comment['from_user']}: {comment_text}\n"
            if len(msg['comments']) > 3:
                summary += f"    ... и еще {len(msg['comments']) - 3} комментариев\n"
            summary += "\n"
        else:
            summary += "\n"
    
    if len(messages) > SUMMARY_SETTINGS['max_messages_per_channel']:
        hidden_count = len(messages) - SUMMARY_SETTINGS['max_messages_per_channel']
        summary += f"... и еще {hidden_count} сообщений\n\n"
    
    return summary


async def create_and_send_summary():
    """
    Создает и отправляет ежедневную сводку с анализом
    """
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    
    try:
        await client.start()
        
        now = datetime.now(MSK_TZ)
        date_str = now.strftime(SUMMARY_SETTINGS['date_format'])
        time_str = now.strftime('%H:%M')
        
        # Красивый заголовок отчета
        full_summary = f"# 📊 Аналитический отчёт за {date_str}\n\n"
        full_summary += f"_Сформировано в {time_str} МСК_\n\n"
        full_summary += "---\n\n"
        
        # Собираем сообщения из всех активных каналов
        messages_by_channel = {}
        total_messages = 0
        
        for channel_key, channel_config in CHANNELS.items():
            if not channel_config.get('enabled', True):
                continue
                
            print(f"📡 Обработка канала {channel_config['name']} ({channel_config['username']})...")
            messages = await get_today_messages_with_comments(
                client, 
                channel_config['username'], 
                channel_config['name']
            )
            
            messages_by_channel[channel_config['name']] = messages
            total_messages += len(messages)
        
        # Глубокий аналитический анализ
        print("🔍 Глубокий анализ контента...")
        content_analysis = analytics_engine.analyze_content(messages_by_channel)
        
        print("😊 Анализ тональности...")
        sentiment_analysis = analytics_engine.analyze_sentiment(messages_by_channel)
        
        # Анализ трендов
        if SUMMARY_SETTINGS.get('include_trends_analysis', True) and messages_by_channel:
            print("📈 Анализ трендов...")
            trends_data = trends_analyzer.analyze_messages(messages_by_channel)
        else:
            trends_data = {}
        
        # Отслеживание брендов
        print("🏷️ Отслеживание упоминаний брендов...")
        brand_tracker.process_messages(messages_by_channel)
        brand_mentions_today = brand_tracker.get_today_brand_mentions()
        brand_mentions_summary = brand_tracker.format_brand_mentions_summary(brand_mentions_today)
        
        # Генерация инсайтов
        print("💡 Генерация инсайтов...")
        insights = analytics_engine.generate_insights(content_analysis, sentiment_analysis, trends_data)
        
        # Формирование аналитического отчета (с учётом трендов)
        analytics_report = analytics_engine.format_analytics_report(
            content_analysis,
            sentiment_analysis,
            insights,
            brand_mentions_summary,
            trends_data=trends_data,
        )
        full_summary += analytics_report
        
        # Тренды уже интегрированы в analytics_report, пропускаем отдельный раздел
        
        # Система обучения — более читаемо
        if SUMMARY_SETTINGS.get('learning_enabled', True) and messages_by_channel:
            print("🧠 Обучение на основе контента...")
            learning_system.process_messages(messages_by_channel)
            market_insights = learning_system.get_market_insights()
            if market_insights:
                full_summary += "\n---\n\n"
                full_summary += "## 💡 Что мы знаем о рынке\n\n"
                full_summary += market_insights + "\n"
        
        # Дайджест по конкретным постам (что именно писали блогеры)
        digest = digest_builder.build_digest(messages_by_channel)
        if digest:
            full_summary += "\n---\n\n"
            full_summary += digest
        
        # Итоговая статистика — более читаемо
        if total_messages > 0:
            full_summary += "\n---\n\n"
            full_summary += f"**Итого:** проанализировано **{total_messages} сообщений** из **{len(messages_by_channel)} каналов** за {date_str}.\n"
        
        # Сохранение сводки в файл для истории
        if SUMMARY_SETTINGS.get('save_to_file', True):
            summary_file = f"summaries/summary_{date_str.replace('.', '_')}.md"
            os.makedirs('summaries', exist_ok=True)
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(full_summary)
            print(f"💾 Сводка сохранена в {summary_file}")
        
        # Отправляем сводку
        recipient = SUMMARY_RECIPIENT.get('chat_id') or SUMMARY_RECIPIENT['username']
        
        # Telegram имеет лимит на длину сообщения (4096 символов)
        # Разбиваем на части, если нужно
        max_length = 4000
        if len(full_summary) > max_length:
            parts = []
            current_part = ""
            for line in full_summary.split('\n'):
                if len(current_part) + len(line) + 1 > max_length:
                    parts.append(current_part)
                    current_part = line + "\n"
                else:
                    current_part += line + "\n"
            if current_part:
                parts.append(current_part)
            
            for i, part in enumerate(parts):
                part_header = f"📊 **Сводка {date_str}** (часть {i+1}/{len(parts)})\n\n"
                await client.send_message(recipient, part_header + part, parse_mode='markdown')
        else:
            await client.send_message(recipient, full_summary, parse_mode='markdown')
        
        print(f"✅ Сводка успешно отправлена! Всего сообщений: {total_messages}")
        
    except Exception as e:
        print(f"❌ Ошибка при создании сводки: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()


def run_summary():
    """Запускает создание сводки (синхронная обертка для schedule)"""
    asyncio.run(create_and_send_summary())


def main():
    """Основная функция - настраивает расписание и запускает цикл"""
    schedule_time = f"{SCHEDULE_TIME['hour']:02d}:{SCHEDULE_TIME['minute']:02d}"
    schedule.every().day.at(schedule_time).do(run_summary)
    
    print(f"✅ Планировщик настроен. Сводка будет отправляться каждый день в {schedule_time} МСК")
    print("📡 Отслеживаемые каналы:")
    for channel_key, channel_config in CHANNELS.items():
        if channel_config.get('enabled', True):
            print(f"   • {channel_config['name']} ({channel_config['username']})")
    print(f"📬 Получатель: {SUMMARY_RECIPIENT['username']}")
    print("\nОжидание времени запуска...")
    
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("🧪 Тестовый запуск...")
        try:
            asyncio.run(create_and_send_summary())
            print("✅ Тест завершён успешно")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Ошибка при выполнении теста: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    else:
        main()
